#!/usr/bin/env python3
"""Build the PNAS 2017 SPECIES-level reduction / pooling map (Phase 6b).

This is the species complement of `scripts/build_pnas2017_reduction_map.py`.
The two maps answer different questions and are NOT interchangeable:

  reaction map  "can this reaction be represented differently / lumped /
                 treated as a candidate fast or degradation step?"
  species map   "what conserved / resource / machinery moieties does this
                 state carry, and what candidate coarse variable would retain
                 that information?"

SCOPE: classification + composition (moiety) analysis + audit ONLY.
  * Does NOT build a reduced CRN or ODEs; no QSSA; no parameter fitting.
  * Does NOT claim any lumping is mathematically valid: every pool is a
    candidate for later mathematical validation.
  * Does NOT modify the SBML (read-only; SHA-256 verified unchanged).

Inputs are the TRACKED audit artefacts only:
  models/pnas2017_full_reference/audit/species.csv
  models/pnas2017_full_reference/audit/reactions.csv
  models/pnas2017_full_reference/audit/inventory_summary.json
  models/pnas2017_full_reference/original/fMGG_synthesis.xml   (hash only)

so the pipeline is reproducible from a clean checkout with no `scratch/`
directory present. The naming/moiety classifiers below are the single source
of truth for species-level component inference; `build_pnas2017_ledger.py`
answers a different question (molecule_class for the resource ledger) and is
not re-used here to avoid mixing the two vocabularies.

Outputs:
  models/pnas2017_full_reference/audit/species_reduction_map.csv
  models/pnas2017_full_reference/audit/species_reduction_map.json
  docs/reduction/species_reduction_map.md
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")
SBML_REL = "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
SBML = os.path.join(ROOT, *SBML_REL.split("/"))
RAW_SBML_REL = "references/PNAS2017_Matsuura/raw/fMGG_synthesis.xml"
RAW_SBML = os.path.join(ROOT, *RAW_SBML_REL.split("/"))
DOCS = os.path.join(ROOT, "docs", "reduction")

# The digest is NOT duplicated here: data/provenance.csv is the single
# registered source of truth for the immutable reference model.
PROVENANCE_REL = "data/provenance.csv"
PROVENANCE_ITEM = "Matsuura_2017_combined_SBML"

MAP_VERSION = "v3"
GENERATOR = "scripts/analyze_pnas2017_species_reduction.py"
PROVENANCE = ("species-level audit promoted from branch "
              "audit/pnas2017-reduction-map (commit 3cdd80e); the scientific "
              "classification is unchanged from that independent audit")

# --- moiety vocabulary ----------------------------------------------------- #
RESOURCES = ["ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr"]
RESOURCE_SET = set(RESOURCES)
PROTEIN_FAMILIES = ["CK", "NDK", "MK", "PPiase", "GlyRS", "MetRS", "MTF",
                    "IF1", "IF2", "IF3", "EFTu", "EFTs", "EFG", "RF1", "RF2",
                    "RF3", "RRF"]
IF_FACTORS = {"IF1", "IF2", "IF3"}
ELONG_FAC = {"EFTu", "EFTs", "EFG"}
REL_FACTORS = {"RF1", "RF2", "RF3", "RRF"}
TL_FACTORS = IF_FACTORS | ELONG_FAC | REL_FACTORS
ENERGY_ENZYMES = {"CK", "NDK", "MK", "PPiase"}
AARS = {"GlyRS", "MetRS"}
AMINO_ACIDS = {"Gly", "Met", "fMet", "Ala", "Phe"}
# The name vocabulary this model actually uses for moiety decomposition.
AMINO_ACID_TOKENS = {"Gly", "Met", "fMet"}
COFACTORS = {"FD", "THF"}
DEGRADED_SUFFIX = "_degraded"

AMINOACYL_AMP = re.compile(r"^([A-Z][a-z]{2})(ATP|ADP|AMP)$")   # GlyAMP -> Gly + AMP
PEPTIDYL_TRNA = re.compile(r"^(Pept\d+)(tRNA.*)$")              # peptide + tRNA moieties
BARE_PEPTIDE = re.compile(r"^Pept\d+$")
PEPTIDE_ANYWHERE = re.compile(r"Pept\d+")     # peptide token inside a complex name
NUMERIC = re.compile(r"^\d+$")
RIBO_STATE = re.compile(r"^(el)?(term)?RS(30S|50S|70S)")
AARS_NAME = re.compile(r"^[A-Z][a-z]{2}RS")

CLASSES = ["KEEP_EXPLICIT", "LUMP_FUNCTIONAL_POOL", "ENZYME_INTERMEDIATE",
           "DEGRADED_SINK", "REVIEW"]
REVIEW_CLASSES = ["NONE", "SCIENTIFIC_DECISION_REQUIRED", "MODULE_LABEL_CONFLICT_ONLY"]
# Species whose explicit-vs-pooled treatment is a model-resolution decision.
SCIENTIFIC_SPECIES = {"FD", "THF", "MTF", "RS70S"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def registered_digest():
    """Look up the reference SBML digest in the tracked provenance manifest."""
    with open(os.path.join(ROOT, *PROVENANCE_REL.split("/")),
              newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["item"] == PROVENANCE_ITEM:
                return row["sha256"]
    raise SystemExit(f"{PROVENANCE_ITEM} is not registered in {PROVENANCE_REL}")


# --------------------------------------------------------------------------- #
# tracked audit inputs
# --------------------------------------------------------------------------- #
def parse_side(field):
    """`A:1|B:2|A:1` -> [("A","1"),("B","2"),("A","1")] (duplicates kept)."""
    out = []
    for item in filter(None, field.split("|")):
        sid, _, stoich = item.partition(":")
        out.append((sid, stoich or "1"))
    return out


def load_audit_tables():
    with open(os.path.join(AUDIT, "inventory_summary.json"), encoding="utf-8") as fh:
        summary = json.load(fh)
    species = []
    with open(os.path.join(AUDIT, "species.csv"), newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            species.append({
                "id": r["id"],
                "sbml_initial_concentration": r["sbml_initial_concentration"],
                "author_export_initial_value": r["author_export_initial_value"],
            })
    reactions = []
    with open(os.path.join(AUDIT, "reactions.csv"), newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            reactions.append({
                "id": r["id"],
                "subsystem_files": r["subsystem_files"],
                "reactants": parse_side(r["reactants"]),
                "products": parse_side(r["products"]),
            })
    return summary, species, reactions


# --------------------------------------------------------------------------- #
# naming classifiers (source of truth for species-level module inference)
# --------------------------------------------------------------------------- #
def toks(sp):
    return sp.split("_")


def has_any(sp, names):
    return any(t in names for t in toks(sp))


def classify_species(sp):
    """(category, subcategory) from the CellDesigner-style species name.

    `RS` is deliberately ambiguous in this model (ribosomal subunit vs
    aminoacyl-tRNA synthetase) and disambiguated by position, not by token.
    """
    if sp in RESOURCE_SET:
        return "energy_nucleotide", sp
    if sp in ENERGY_ENZYMES:
        return "energy_regeneration_enzyme", sp
    if toks(sp)[0] in ENERGY_ENZYMES:
        return "energy_regeneration_enzyme", "enzyme_substrate_complex"
    if sp in COFACTORS or sp == "MTF" or toks(sp)[0] == "MTF":
        return "formylation_factor", sp
    if sp in IF_FACTORS:
        return "translation_factor", "initiation_factor"
    if sp in REL_FACTORS:
        return "translation_factor", "release_or_recycling_factor"
    if sp in ELONG_FAC:
        return "translation_factor", "elongation_factor"
    if sp == "mRNA":
        return "mRNA", "mRNA"
    if sp in AMINO_ACIDS:
        return "amino_acid", sp
    if re.match(r"^[A-Z][a-z]{2}AMP$", sp):
        return "aminoacylation_complex", sp
    if sp in {"RS30S", "RS50S", "RS70S"}:
        return "ribosome", {"RS30S": "30S", "RS50S": "50S", "RS70S": "70S"}[sp]
    if AARS_NAME.match(sp) and "_" not in sp:
        return "aminoacyl_tRNA_synthetase", sp
    if sp.endswith(DEGRADED_SUFFIX):
        return "degraded_species", sp[: -len(DEGRADED_SUFFIX)]
    if RIBO_STATE.match(sp):
        if sp.startswith("elRS70S"):
            return "translation_complex", "elongating_ribosome"
        if sp.startswith("termRS70S"):
            return "translation_complex", "terminating_ribosome"
        return "translation_complex", "initiation_or_assembly_ribosome"
    if has_any(sp, REL_FACTORS):
        return "translation_factor_complex", "release_or_recycling_factor_complex"
    if has_any(sp, IF_FACTORS):
        return "translation_factor_complex", "initiation_factor_complex"
    if has_any(sp, ELONG_FAC):
        return "translation_factor_complex", "elongation_factor_complex"
    if AARS_NAME.match(sp):
        return "aminoacylation_complex", toks(sp)[0]
    if PEPTIDE_ANYWHERE.search(sp):
        return "peptide", "peptide_intermediate"
    if "tRNA" in sp:
        core = toks(sp)[0]
        charged = bool(re.match(r"^[A-Za-z]{1,4}tRNA", core)) and not core.startswith("tRNA")
        return ("charged_tRNA" if charged else "tRNA"), sp
    return "other", sp


def classify_reaction(rxn, all_species):
    """Module inference from the SET of participating species (ordered rules).

    Explicit ribosome-state prefixes win over the looser factor/tRNA
    heuristics. This is a naming-derived label; the authors' own subsystem
    grouping is carried separately as `sbml_subsystems`.
    """
    ss = ({s for s, _ in rxn["reactants"]}
          | {s for s, _ in rxn["products"]})
    anytok = lambda names: any(has_any(s, names) or (s in names) for s in ss)
    ribo_present = any(RIBO_STATE.match(s) for s in ss)

    if any(s.endswith(DEGRADED_SUFFIX) for s, _ in rxn["products"]):
        return "degradation"
    if any(AARS_NAME.match(s) for s in ss):
        return "aminoacylation"
    if anytok(ENERGY_ENZYMES):
        return "energy_regeneration"
    if any(s.startswith("termRS70S") for s in ss):
        return "translation_termination"
    if any(s.startswith("elRS70S") for s in ss):
        return "translation_elongation"
    if any(has_any(s, {"RRF"}) for s in ss):
        return "ribosome_recycling"
    if ribo_present and anytok({"RF1", "RF2", "RF3"}):
        return "translation_termination"
    if anytok(IF_FACTORS) or anytok({"MTF"}) or (
            any(s.startswith("RS30S") for s in ss)
            and ("mRNA" in ss or any("fMettRNAfMetCAU" == t for s in ss for t in toks(s)))):
        return "translation_initiation"
    if any(PEPTIDE_ANYWHERE.search(s) for s in ss) or (
            ribo_present and anytok(ELONG_FAC)):
        return "translation_elongation"
    if anytok({"EFTu"}):
        return "EF_Tu_nucleotide_cycle"
    if anytok({"EFG"}):
        return "EF_G_nucleotide_cycle"
    if ribo_present:
        return "translation_initiation"
    if ss & RESOURCE_SET:
        return "energy_regeneration"
    return "uncertain"


RXN_MODULE_MAP = {"EF_Tu_nucleotide_cycle": "translation_elongation",
                  "EF_G_nucleotide_cycle": "ribosome_recycling"}

NAME_MODULE_PRIOR = {
    "energy_nucleotide": "energy_regeneration",
    "energy_regeneration_enzyme": "energy_regeneration",
    "formylation_factor": "aminoacylation",
    "aminoacyl_tRNA_synthetase": "aminoacylation",
    "aminoacylation_complex": "aminoacylation",
    "amino_acid": "amino_acid",
    "tRNA": "tRNA",
    "charged_tRNA": "tRNA",
    "mRNA": "mRNA",
    "peptide": "peptide_product",
}


def prior_module(sp):
    cat, sub = classify_species(sp)
    stripped = sp[: -len(DEGRADED_SUFFIX)] if sp.endswith(DEGRADED_SUFFIX) else sp
    if cat in ("translation_complex", "translation_factor_complex"):
        if stripped.startswith("elRS"):
            return "translation_elongation"
        if stripped.startswith("termRS"):
            return "translation_termination"
        if has_any(stripped, {"RRF"}) or (has_any(stripped, {"EFG"}) and RIBO_STATE.match(stripped)):
            return "ribosome_recycling"
        if has_any(stripped, {"RF1", "RF2", "RF3"}):
            return "translation_termination"
        if has_any(stripped, ELONG_FAC):
            return "translation_elongation"
        return "translation_initiation"
    if cat == "ribosome":
        return "translation_initiation"
    if cat == "translation_factor":
        return {"initiation_factor": "translation_initiation",
                "elongation_factor": "translation_elongation"}.get(sub, "translation_termination")
    if cat == "degraded_species":
        return "degradation"
    return NAME_MODULE_PRIOR.get(cat, "other")


# --------------------------------------------------------------------------- #
# moiety decomposition
# --------------------------------------------------------------------------- #
def ribo_canonical(token):
    for canon in ("RS30S", "RS50S", "RS70S"):
        if canon in token:
            return canon
    return None


def split_components(sp):
    """Decompose a species name into moiety components.

    Returns (comps, numeric_tokens, unknown_tokens)."""
    degraded = sp.endswith(DEGRADED_SUFFIX)
    core = sp[: -len(DEGRADED_SUFFIX)] if degraded else sp
    if "_" in core:
        parts = core.split("_")
    else:
        m = AMINOACYL_AMP.match(core)
        p = PEPTIDYL_TRNA.match(core)
        if m and core not in RESOURCE_SET:
            parts = [m.group(1), m.group(2)]
        elif p:
            parts = [p.group(1), p.group(2)]
        elif ribo_canonical(core) and core != ribo_canonical(core):
            parts = [ribo_canonical(core)]
        else:
            parts = [core]
    comps, numeric, unknown = [], [], []
    for tok in parts:
        if tok in RESOURCE_SET or tok in PROTEIN_FAMILIES:
            comps.append(tok)
            continue
        m = AMINOACYL_AMP.match(tok)
        if m:
            comps.extend([m.group(1), m.group(2)])
            continue
        p = PEPTIDYL_TRNA.match(tok)
        if p:
            comps.extend([p.group(1), p.group(2)])
            continue
        can = ribo_canonical(tok)
        if can:
            comps.append(can)
            continue
        if (tok in {"mRNA", "FD", "THF"} | AMINO_ACID_TOKENS
                or BARE_PEPTIDE.match(tok) or "tRNA" in tok):
            comps.append(tok)
            continue
        if NUMERIC.match(tok):
            numeric.append(tok)
            continue
        unknown.append(tok)
    if degraded:
        comps.append("degraded")
    return comps, numeric, unknown


def moiety_bag(comps):
    """Multiset used for the reaction moiety balance.

    RS70S contributes one RS30S and one RS50S moiety; `degraded` is an inert
    state flag and contributes nothing."""
    bag = collections.Counter()
    for c in comps:
        if c == "degraded":
            continue
        if c == "RS70S":
            bag["RS30S"] += 1
            bag["RS50S"] += 1
            continue
        bag[c] += 1
    return bag


def families_of(comps, degraded):
    """Per-species three-layer pool membership, from MOIETY membership:

      <F>_active_pool   = all non-degraded free/bound states carrying moiety F
      <F>_degraded_pool = degraded state(s) carrying moiety F
      <F>_family_total  = active + degraded (built in build_pools; the ONLY
                          layer called a conservation candidate)
    """
    suffix = "_degraded_pool" if degraded else "_active_pool"
    fams = [f"{p}{suffix}" for p in PROTEIN_FAMILIES if p in comps]
    if "RS30S" in comps or "RS70S" in comps:
        fams.append(f"RS30S{suffix}")
    if "RS50S" in comps or "RS70S" in comps:
        fams.append(f"RS50S{suffix}")
    return fams


def primary_protein_family(comps):
    for p in PROTEIN_FAMILIES:
        if p in comps:
            return f"{p}_active_pool"
    return ""


# --------------------------------------------------------------------------- #
# reduction classes
# --------------------------------------------------------------------------- #
def classify_ribosome(core, comps):
    has = lambda r: r in comps
    if core == "RS30S":
        return ("LUMP_FUNCTIONAL_POOL", "R30_free", "high",
                "free 30S subunit; kept separate from 50S to preserve subunit-limiting information",
                "R21_free_30S")
    if core == "RS50S":
        return ("LUMP_FUNCTIONAL_POOL", "R50_free", "high",
                "free 50S subunit; kept separate from 30S", "R21_free_50S")
    if core == "RS70S":
        return ("LUMP_FUNCTIONAL_POOL", "R70_active", "medium",
                "free 70S: explicit vs pooled vs transitional is an open resolution decision",
                "R21_free_70S")
    if core.startswith("elRS"):
        return ("LUMP_FUNCTIONAL_POOL", "R_elong", "high",
                "elongating ribosome micro-state", "R21_elong")
    if core.startswith("termRS"):
        return ("LUMP_FUNCTIONAL_POOL", "R_term", "high",
                "post-termination ribosome micro-state", "R21_term")
    if has("RRF") or has("EFG"):
        return ("LUMP_FUNCTIONAL_POOL", "R_recycle", "medium",
                "subunit/70S state carrying RRF or EF-G; recycling pool candidate",
                "R21_recycle")
    return ("LUMP_FUNCTIONAL_POOL", "R_init", "high",
            "30S/70S initiation-complex micro-state", "R21_init")


def classify_reduction(sp, comps, numeric, unknown, numeric_evidence=None):
    """Return (class, coarse_variable, confidence, reason, rule)."""
    degraded = sp.endswith(DEGRADED_SUFFIX)
    core = sp[: -len(DEGRADED_SUFFIX)] if degraded else sp
    has = lambda r: r in comps

    if degraded:
        return ("DEGRADED_SINK", "", "high",
                "explicit _degraded terminal state; tracked in *_degraded_pool, excluded from "
                "*_active_pool; conservation candidate is *_family_total", "R01_degraded_suffix")
    if core in RESOURCE_SET:
        return ("KEEP_EXPLICIT", "", "high", "free small-molecule energy resource",
                "R02_free_resource")
    if core in AMINO_ACIDS:
        return ("KEEP_EXPLICIT", "", "high", "free amino acid", "R03_free_aminoacid")
    if core in {"tRNAGlyGCC", "tRNAfMetCAU"}:
        return ("KEEP_EXPLICIT", "", "high", "free (uncharged) tRNA", "R04_free_trna")
    if core in {"GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU"}:
        return ("KEEP_EXPLICIT", "", "high",
                "aminoacyl/charged tRNA (distinct from peptidyl-tRNA); charging ledger entity",
                "R05_charged_trna")
    if BARE_PEPTIDE.match(core):
        return ("KEEP_EXPLICIT", "", "high", "free peptide product", "R06_peptide_product")
    if core == "mRNA":
        return ("KEEP_EXPLICIT", "", "high", "mRNA template", "R07_mrna")
    if core in COFACTORS:
        return ("KEEP_EXPLICIT", "", "medium",
                "formylation cofactor outside the canonical resource list; retention is a "
                "model-resolution decision", "R08_cofactor")
    if PEPTIDYL_TRNA.match(core):
        return ("LUMP_FUNCTIONAL_POOL", "peptidyl_tRNA", "medium",
                "peptidyl-tRNA (not aminoacyl-tRNA): carries one peptide moiety + one tRNA "
                "moiety; must be double-counted in peptide AND tRNA ledgers",
                "R22_peptidyl_trna")
    if unknown:
        return ("REVIEW", "", "low",
                f"unparseable name tokens {unknown}; component membership unreliable",
                "R10_unparsed_tokens")
    if numeric:
        if numeric_evidence and numeric_evidence["balanced"]:
            return ("ENZYME_INTERMEDIATE", "", "high",
                    f"numeric suffix = distinct binding-site/configuration (e.g. ADP site "
                    f"{numeric[0]}); moiety composition {comps} confirmed by moiety balance in "
                    f"{len(numeric_evidence['rxns'])} reactions incl. "
                    f"{', '.join(numeric_evidence['rxns'][:4])}",
                    "R10b_numeric_site_topology")
        return ("REVIEW", "", "low",
                f"numeric token(s) {numeric}; moiety balance could not confirm composition "
                f"(unbalanced: {', '.join(numeric_evidence['bad'] if numeric_evidence else [])})",
                "R10_unparsed_tokens")
    if AMINOACYL_AMP.match(core):
        return ("ENZYME_INTERMEDIATE", "", "medium",
                "free aminoacyl-adenylate (aaRS mechanism intermediate); AMP moiety recorded "
                "for the adenylate ledger", "R09_aminoacyl_amp")
    first = core.split("_")[0]
    if "_" in core and first in ENERGY_ENZYMES:
        return ("ENZYME_INTERMEDIATE", "", "high",
                "energy-enzyme substrate complex; bound resources + enzyme family recorded",
                "R11_energy_enzyme_complex")
    if "_" in core and first in AARS:
        return ("ENZYME_INTERMEDIATE", "", "high",
                "aminoacyl-tRNA synthetase intermediate complex", "R12_aars_complex")
    if "_" in core and first == "MTF":
        return ("ENZYME_INTERMEDIATE", "", "high", "transformylase intermediate complex",
                "R13_mtf_complex")
    if core in ENERGY_ENZYMES:
        return ("LUMP_FUNCTIONAL_POOL", f"{core}_active_pool", "high",
                "free energy enzyme; member of <F>_active_pool (enzymes are NOT interchangeable)",
                "R14_bare_energy_enzyme")
    if core in AARS:
        return ("LUMP_FUNCTIONAL_POOL", f"{core}_active_pool", "high",
                "free synthetase; member of <F>_active_pool (GlyRS and MetRS are not "
                "interchangeable)", "R15_bare_aars")
    if core == "MTF":
        return ("LUMP_FUNCTIONAL_POOL", "MTF_active_pool", "medium",
                "formylation-module granularity (explicit vs pooled) is an open resolution "
                "decision", "R16_bare_mtf")
    if RIBO_STATE.match(core):
        return classify_ribosome(core, comps)
    if core in TL_FACTORS:
        return ("LUMP_FUNCTIONAL_POOL", f"{core}_active_pool", "high",
                "free translation factor; member of <F>_active_pool (per-protein; factors are "
                "not interchangeable)", "R17_bare_factor")
    factor_toks = [c for c in comps if c in TL_FACTORS]
    if factor_toks and ribo_canonical(core) is None:
        if all(c in TL_FACTORS or c in RESOURCE_SET or "tRNA" in c
               or BARE_PEPTIDE.match(c) or c in AMINO_ACID_TOKENS | {"mRNA"}
               for c in comps):
            fam = primary_protein_family(comps)
            extra = [c for c in comps if c in TL_FACTORS][1:]
            note = (f"; also counted in {', '.join(f'{e}_active_pool' for e in extra)}"
                    if extra else "")
            kind = ("soluble factor complexed with aa-tRNA (spans factor + tRNA ledgers)"
                    if any("tRNA" in c for c in comps)
                    else ("EF-Tu.EF-Ts exchange complex (tracked in BOTH per-protein totals)"
                          if "EFTs" in factor_toks else
                          "soluble translation-factor nucleotide state"))
            return ("LUMP_FUNCTIONAL_POOL", fam, "medium", f"{kind}{note}", "R18_factor_complex")
    return ("REVIEW", "", "low", "no reliable rule matched", "R23_no_rule")


def validate_numeric(sp, comps, reactions, comps_of):
    """Check every reaction containing `sp` for moiety balance under the assumed
    composition (numeric site tokens contribute no moieties).

    Stoichiometry coefficients are intentionally not applied here: the balance
    tests species identity/moiety membership, and every coefficient in this
    model is 1 or 2 of an already-counted species."""
    rxns, bad = [], []
    for r in reactions:
        rset = {s for s, _ in r["reactants"]} | {s for s, _ in r["products"]}
        if sp not in rset:
            continue
        lhs = collections.Counter()
        rhs = collections.Counter()
        for bag, lst in ((lhs, r["reactants"]), (rhs, r["products"])):
            for s, _ in lst:
                bag.update(moiety_bag(comps_of.get(s, [])))
        rxns.append(r["id"])
        if lhs != rhs:
            bad.append(r["id"])
    return {"balanced": bool(rxns) and not bad, "rxns": rxns, "bad": bad}


def build_pools(rows):
    pools = collections.defaultdict(list)
    for r in rows:
        for f in filter(None, r["conservation_family"].split(";")):
            pools[f].append(r["species_id"])
    for f in [k for k in list(pools)
              if k.endswith("_active_pool") or k.endswith("_degraded_pool")]:
        base = (f[: -len("_active_pool")] if f.endswith("_active_pool")
                else f[: -len("_degraded_pool")])
        merged = (pools.get(f"{base}_active_pool", [])
                  + pools.get(f"{base}_degraded_pool", []))
        pools[f"{base}_family_total"] = sorted(set(merged))
    for r in rows:
        if r["candidate_coarse_variable"]:
            pools["coarse:" + r["candidate_coarse_variable"]].append(r["species_id"])
    return {k: sorted(v) for k, v in sorted(pools.items())}


# --------------------------------------------------------------------------- #
# analysis
# --------------------------------------------------------------------------- #
def analyse(species, reactions):
    species_ids = [s["id"] for s in species]
    parsed = {s["id"]: split_components(s["id"]) for s in species}
    comps_of = {sp: parsed[sp][0] for sp in species_ids}

    rxn_module = {r["id"]: classify_reaction(r, species_ids) for r in reactions}
    as_reactant, as_product = collections.Counter(), collections.Counter()
    module_votes = collections.defaultdict(collections.Counter)
    subsystems = collections.defaultdict(set)
    for r in reactions:
        rset = {s for s, _ in r["reactants"]} | {s for s, _ in r["products"]}
        for s, _ in r["reactants"]:
            as_reactant[s] += 1
        for s, _ in r["products"]:
            as_product[s] += 1
        mod = RXN_MODULE_MAP.get(rxn_module[r["id"]], rxn_module[r["id"]])
        for a in rset:
            if mod not in ("uncertain", "degradation"):
                module_votes[a][mod] += 1
            subsystems[a] |= set(filter(None, r["subsystem_files"].split("|")))

    rows = []
    for s in species:
        sp = s["id"]
        comps, numeric, unknown = parsed[sp]
        evidence = (validate_numeric(sp, comps, reactions, comps_of)
                    if numeric and not unknown else None)
        prior = prior_module(sp)
        degraded = sp.endswith(DEGRADED_SUFFIX)
        if degraded:
            module, conflict = "degradation", False
        else:
            topo = module_votes[sp].most_common()
            module = topo[0][0] if topo else prior
            conflict = bool(topo) and prior != "other" and prior != module and topo[0][1] >= 2
        cls, coarse, conf, reason, rule = classify_reduction(
            sp, comps, numeric, unknown, evidence)
        core = sp[: -len(DEGRADED_SUFFIX)] if degraded else sp
        if conflict:
            reason += ("; module-label only: name-prior=%s vs topology=%s "
                       "(species legitimately acts in several modules)" % (prior, module))

        if cls != "DEGRADED_SINK" and (
                cls == "REVIEW" or core in SCIENTIFIC_SPECIES
                or core.split("_")[0] == "MTF" or PEPTIDYL_TRNA.match(core)):
            sci = "SCIENTIFIC_DECISION_REQUIRED"
        elif conflict:
            sci = "MODULE_LABEL_CONFLICT_ONLY"
        else:
            sci = "NONE"

        nres = {r: comps.count(r) for r in RESOURCES}
        row = OrderedDict([
            ("species_id", sp),
            ("sbml_initial_concentration", s["sbml_initial_concentration"]),
            ("author_export_initial_value", s["author_export_initial_value"]),
            ("functional_module", module),
            ("sbml_subsystems", "|".join(sorted(subsystems.get(sp, ())))),
            ("primary_reduction_class", cls),
            ("candidate_coarse_variable", coarse),
            ("conservation_family", ";".join(families_of(comps, degraded))),
            ("scientific_review_class", sci),
            ("detected_components", " + ".join(comps)),
            ("n_peptide", sum(1 for c in comps if BARE_PEPTIDE.match(c))),
            ("n_tRNA", sum(1 for c in comps if "tRNA" in c)),
            ("n_RS30S", 1 if ("RS30S" in comps or "RS70S" in comps) else 0),
            ("n_RS50S", 1 if ("RS50S" in comps or "RS70S" in comps) else 0),
        ])
        for r in RESOURCES:
            row["n_%s" % r] = nres[r]
        for r in RESOURCES:
            row["contains_%s" % r] = str(nres[r] > 0).lower()
        row.update([
            ("reaction_as_reactant_count", as_reactant[sp]),
            ("reaction_as_product_count", as_product[sp]),
            ("confidence", conf),
            ("needs_human_review", str(sci == "SCIENTIFIC_DECISION_REQUIRED").lower()),
            ("reason", reason),
            ("rule_used", rule),
        ])
        row["_numeric_evidence"] = evidence
        rows.append(row)
    return rows, parsed


# --------------------------------------------------------------------------- #
# structural assertions (fail loudly rather than ship a broken map)
# --------------------------------------------------------------------------- #
def run_checks(rows, parsed, species_ids, reactions):
    errs = []
    rows_by_id = {r["species_id"]: r for r in rows}
    if sorted(r["species_id"] for r in rows) != sorted(species_ids):
        errs.append("QC-base: map does not cover each species exactly once")
    cc = collections.Counter(r["primary_reduction_class"] for r in rows)
    if set(cc) - set(CLASSES) or sum(cc.values()) != len(species_ids) or not all(cc.values()):
        errs.append("QC15: class enum/coverage failure")
    if any(r["scientific_review_class"] not in REVIEW_CLASSES for r in rows):
        errs.append("QC: bad scientific_review_class")
    for r in rows:
        core = r["species_id"][: -len(DEGRADED_SUFFIX)]
        if core in RESOURCE_SET and r["primary_reduction_class"] != "KEEP_EXPLICIT":
            errs.append(f"QC-free: {core} not KEEP_EXPLICIT")
        if r["species_id"].endswith(DEGRADED_SUFFIX) and \
                r["primary_reduction_class"] != "DEGRADED_SINK":
            errs.append(f"QC-degraded: {r['species_id']}")

    # family purity: a member of X_active_pool / X_degraded_pool must really carry
    # the X moiety; degraded states never enter an active pool; and
    # X_family_total == active_pool + degraded_pool (the conservation candidate).
    pools = build_pools(rows)
    for fname, members in pools.items():
        if fname.startswith("coarse:"):
            continue
        if fname.endswith("_family_total"):
            base = fname[: -len("_family_total")]
            union = sorted(set(pools.get(f"{base}_active_pool", [])
                               + pools.get(f"{base}_degraded_pool", [])))
            if members != union:
                errs.append(f"QC-layer: {fname} != active_pool + degraded_pool")
            continue
        if fname.endswith("_degraded_pool"):
            base = fname[: -len("_degraded_pool")]
            for sp in members:
                if base not in rows_by_id[sp]["detected_components"].split(" + "):
                    errs.append(f"QC8: {sp} in {fname} without moiety {base}")
                if not sp.endswith(DEGRADED_SUFFIX):
                    errs.append(f"QC8: non-degraded {sp} in {fname}")
            continue
        base = fname[: -len("_active_pool")]
        for sp in members:
            comps = parsed[sp][0]
            ok = (base in comps or "RS70S" in comps) if base in ("RS30S", "RS50S") \
                else base in comps
            if not ok:
                errs.append(f"QC5-7: {sp} in {fname} without moiety {base}")
            if sp.endswith(DEGRADED_SUFFIX):
                errs.append(f"QC8: degraded {sp} leaked into active {fname}")
            if base in ENERGY_ENZYMES or base in AARS:
                others = [e for e in list(ENERGY_ENZYMES) + list(AARS)
                          if e != base and e in comps]
                if others:
                    errs.append(f"QC1-4: {sp} cross-family {base} vs {others}")

    # RS70S must feed BOTH subunit ledgers; peptidyl-tRNA must feed BOTH
    # the peptide and the tRNA ledger, and never the charged-tRNA pool.
    for sp in ("RS70S", "RS70S_EFG_GTP"):
        r = rows_by_id.get(sp)
        if r and not (int(r["n_RS30S"]) == 1 and int(r["n_RS50S"]) == 1):
            errs.append(f"QC-ribo: {sp} does not contribute to both subunit moieties")
    for sp, r in rows_by_id.items():
        core = sp[: -len(DEGRADED_SUFFIX)]
        if PEPTIDYL_TRNA.match(core) and not (int(r["n_peptide"]) >= 1 and int(r["n_tRNA"]) >= 1):
            errs.append(f"QC-pept: {sp} not double-counted in peptide + tRNA ledgers")
    if any(r["candidate_coarse_variable"] == "charged_tRNA" and PEPTIDYL_TRNA.match(r["species_id"])
           for r in rows):
        errs.append("QC9: peptidyl-tRNA in charged_tRNA pool")
    for sp, expect in (("MK_ADP_1", 1), ("MK_ADP_2", 1), ("MK_ADP_ADP", 2)):
        r = rows_by_id.get(sp)
        if r and int(r["n_ADP"]) != expect:
            errs.append(f"QC10: {sp} n_ADP={r['n_ADP']} expected {expect}")
        if r and r["primary_reduction_class"] == "REVIEW":
            errs.append(f"QC10: {sp} still REVIEW")

    # resource identities stay distinct (no NTP/NXP collapse)
    for r in rows:
        if r["species_id"] in RESOURCE_SET:
            flags = [x for x in RESOURCES if int(r[f"n_{x}"]) > 0]
            if flags != [r["species_id"]]:
                errs.append(f"QC11-14: free {r['species_id']} flags {flags}")
    for a, b in (("ATP", "GTP"), ("AMP", "ADP"), ("PO4", "PPi"), ("CP", "Cr")):
        merged = [r["species_id"] for r in rows
                  if r["species_id"] in RESOURCE_SET and r[f"n_{a}"] and r[f"n_{b}"]]
        if merged:
            errs.append(f"QC: {a}/{b} merged on {merged}")
    for r in rows:
        for tok in r["species_id"].split("_"):
            if tok in RESOURCE_SET and int(r[f"n_{tok}"]) < 1:
                errs.append(f"QC-bound: resource {tok} in {r['species_id']} missing multiplicity")
    if errs:
        print("\n".join(errs))
        raise SystemExit(f"ASSERTION FAILURES: {len(errs)}")


# --------------------------------------------------------------------------- #
# reporting
# --------------------------------------------------------------------------- #
DECISION_GROUP_ORDER = ["D1_formylation_resolution", "D2_peptidyl_tRNA_resolution",
                        "D3_RS70S_resolution"]


def decision_groups(sci_rows):
    groups = collections.defaultdict(list)
    for r in sci_rows:
        sp = r["species_id"]
        core = sp[: -len(DEGRADED_SUFFIX)] if sp.endswith(DEGRADED_SUFFIX) else sp
        if PEPTIDYL_TRNA.match(core):
            groups["D2_peptidyl_tRNA_resolution"].append(sp)
        elif core == "RS70S":
            groups["D3_RS70S_resolution"].append(sp)
        else:
            groups["D1_formylation_resolution"].append(sp)
    return groups


def fmt_reaction(rid, reactions):
    r = next((x for x in reactions if x["id"] == rid), None)
    if not r:
        return None

    def side(lst):
        return " + ".join(s if st == "1" else f"{s}*{st}" for s, st in lst)
    return f"`{rid}`: {side(r['reactants'])} -> {side(r['products'])}"


MK_EVIDENCE_RXNS = ("re0000000390", "re0000000391", "re0000000392", "re0000000394",
                    "re0000000395", "re0000000396", "re0000000397", "re0000000388")


def build_markdown(rows, pools, reactions, digest, summary):
    cc = collections.Counter(r["primary_reduction_class"] for r in rows)
    rc = collections.Counter(r["scientific_review_class"] for r in rows)
    mc = collections.Counter(r["functional_module"] for r in rows)
    sci = [r for r in rows if r["scientific_review_class"] == "SCIENTIFIC_DECISION_REQUIRED"]
    mlo = [r for r in rows if r["scientific_review_class"] == "MODULE_LABEL_CONFLICT_ONLY"]
    groups = decision_groups(sci)
    L = []
    A = L.append

    A("# PNAS 2017 — species / moiety-level reduction map")
    A("")
    A(f"> **This document performs NO reduction.** It classifies the "
      f"{len(rows)} species of the reference network by the moieties they carry "
      "and proposes *candidate* coarse variables. Every pool below is a "
      "**candidate for later mathematical validation**; no conservation law is "
      "claimed to be proven, and no QSSA or lumping is asserted.")
    A("")
    A("Machine-readable companion: "
      "`models/pnas2017_full_reference/audit/species_reduction_map.csv` "
      "(`.json` for the pool layer), generated by "
      f"`{GENERATOR}`.")
    A("")
    A("## 0. Scope, source and provenance")
    A("")
    A(f"- source SBML (read-only): `{SBML_REL}`")
    A(f"- source SHA-256: `{digest}` — looked up from the registered digest in "
      f"`{PROVENANCE_REL}` (`{PROVENANCE_ITEM}`), verified unchanged before and after "
      f"the run, and matching the immutable drop `{RAW_SBML_REL}`")
    A(f"- model id `{summary['model_id']}`; "
      f"**{len(rows)} species**; **{len(reactions)} reactions**")
    A(f"- map version: `{MAP_VERSION}`")
    A(f"- provenance: {PROVENANCE}.")
    A("- inputs are the tracked audit artefacts `species.csv`, `reactions.csv` and "
      "`inventory_summary.json`; the pipeline has **no dependency on `scratch/`** "
      "and reproduces from a clean checkout.")
    A("")
    A("## 1. How this map relates to the reaction-level map")
    A("")
    A("| | reaction map | species map (this document) |")
    A("| --- | --- | --- |")
    A("| artefacts | `docs/reduction/reduction_map.md`, "
      "`docs/reduction/reduction_decisions.csv` | this file, "
      "`species_reduction_map.csv` / `.json` |")
    A("| unit | 968 reactions | 241 species |")
    A("| question | can this reaction be re-represented, lumped, or treated as a "
      "candidate fast / degradation step? | what conserved / resource / machinery "
      "moieties does this state carry, and what candidate coarse variable retains "
      "that information? |")
    A("| generator | `scripts/build_pnas2017_reduction_map.py` | "
      f"`{GENERATOR}` |")
    A("")
    A("The two layers are **complementary, not interchangeable**, and neither one "
      "licenses the other:")
    A("")
    A("- a reaction `LUMP_CANDIDATE` in the reaction map does **not** imply that "
      "the species taking part in it may be deleted;")
    A("- a species `LUMP_FUNCTIONAL_POOL` here does **not** prove that the "
      "reactions connecting the micro-states inside the pool are at QSSA or fast "
      "equilibrium — that is a timescale claim and needs SI evidence.")
    A("")
    A("Join key between the two: `sbml_subsystems` here and `level_B_subsystems` "
      "in `reduction_decisions.csv` (both are the authors' own subsystem labels). "
      "`functional_module` in this map is a *naming-derived* label and is "
      "deliberately kept separate from the subsystem provenance.")
    A("")
    A("Position in the scientific hierarchy:")
    A("")
    A("```")
    A("PNAS 2017 full reference (immutable SBML)")
    A("  ->  inventory                    models/pnas2017_full_reference/audit/")
    A("  ->  chemical / resource ledger   species_properties.csv, "
      "reaction_balance_audit.csv")
    A("  ->  reaction-level reduction map docs/reduction/reduction_map.md + "
      "reduction_decisions.csv")
    A("      +")
    A("      species/moiety-level map    THIS FILE + species_reduction_map.csv/.json")
    A("  ->  human decisions              docs/reduction/human_reduction_review.md")
    A("  ->  candidate reduced CRN        docs/reduction/candidate_core_v0.md")
    A("  ->  mathematical + numerical validation   (not started)")
    A("```")
    A("")
    A("## 2. Tally")
    A("")
    A("| reduction class | species |")
    A("| --- | --- |")
    for c in CLASSES:
        A(f"| `{c}` | {cc.get(c, 0)} |")
    A("")
    A("| scientific review class | species |")
    A("| --- | --- |")
    for c in REVIEW_CLASSES:
        A(f"| `{c}` | {rc.get(c, 0)} |")
    A("")
    A("| naming-derived functional module | species |")
    A("| --- | --- |")
    for m, n in mc.most_common():
        A(f"| `{m}` | {n} |")
    A("")
    A(f"low-confidence rows: {sum(r['confidence'] == 'low' for r in rows)}.")
    A("")
    A("## 3. Decision groups")
    A("")
    A(f"`SCIENTIFIC_DECISION_REQUIRED` flags **{len(sci)} species**. Those are "
      "species-level markers, **not independent scientific decisions**: they "
      f"collapse into **{len(groups)} decision groups**.")
    A("")
    A("- **D1_formylation_resolution** — is the formylation layer (MTF, FD, THF "
      "and their complexes) kept explicit, pooled, or reduced to pure "
      "accounting?")
    for sp in sorted(groups.get("D1_formylation_resolution", [])):
        A(f"  - `{sp}`")
    A("- **D2_peptidyl_tRNA_resolution** — which coarse variable represents free "
      "peptidyl-tRNA, given it is counted in both the peptide and the tRNA "
      "ledger?")
    for sp in sorted(groups.get("D2_peptidyl_tRNA_resolution", [])):
        A(f"  - `{sp}`")
    A("- **D3_RS70S_resolution** — is free `RS70S` an independent state, a member "
      "of the active ribosome pool, or a transitional state?")
    for sp in sorted(groups.get("D3_RS70S_resolution", [])):
        A(f"  - `{sp}`")
    A("")
    A("## 4. Per-family three-layer pools")
    A("")
    A("Membership is derived **programmatically from moiety membership, not from "
      "name prefixes**. Three layers per family `F`:")
    A("")
    A("1. `F_active_pool` — every **non-degraded** free or bound state carrying "
      "moiety `F`;")
    A("2. `F_degraded_pool` — the degraded state(s) carrying moiety `F`;")
    A("3. `F_family_total` — `active_pool + degraded_pool`.")
    A("")
    A("**Only layer 3 may be described as a CONSERVATION CANDIDATE.** Grouping "
      "species is not a proof of a conservation law; the proof/validation belongs "
      "to the later mathematical reduction stage. Species classification, "
      "component membership and multiplicities are unaffected by the layering.")
    A("")
    bases = sorted({f[: -len(suf)] for f in pools if not f.startswith("coarse:")
                    for suf in ("_active_pool", "_degraded_pool") if f.endswith(suf)})
    for base in bases:
        a = pools.get(f"{base}_active_pool", [])
        d = pools.get(f"{base}_degraded_pool", [])
        t = pools.get(f"{base}_family_total", [])
        A(f"- **{base}** — `active_pool` ({len(a)}): " + ", ".join(f"`{m}`" for m in a))
        if d:
            A(f"  `degraded_pool` ({len(d)}): " + ", ".join(f"`{m}`" for m in d))
        A(f"  **{base}_family_total** = {base}_active_pool + {base}_degraded_pool "
          f"({len(t)} species) — conservation candidate")
    A("")
    A("Ribosomes: `RS30S_family_total` and `RS50S_family_total` track the 30S and "
      "50S subunit moieties **separately**; an `RS70S` complex contributes one "
      "unit to *each*. They are **not** merged into a single `R_total`.")
    A("")
    A("## 5. Candidate coarse variables (functional pools)")
    A("")
    A("| coarse variable | members | representative states |")
    A("| --- | --- | --- |")
    for cname in sorted(f for f in pools if f.startswith("coarse:")):
        members = pools[cname]
        rep = ", ".join(f"`{m}`" for m in sorted(members, key=len)[:3])
        A(f"| `{cname[7:]}` | {len(members)} | {rep} |")
    A("")
    A("## 6. `KEEP_EXPLICIT` — states retained as named variables")
    A("")
    A("| species | moiety count | why |")
    A("| --- | --- | --- |")
    for r in sorted((r for r in rows if r["primary_reduction_class"] == "KEEP_EXPLICIT"),
                    key=lambda x: x["species_id"]):
        nstr = ", ".join(f"n_{x}={r[f'n_{x}']}" for x in RESOURCES if r[f"n_{x}"]) \
            or "structural"
        reason = r["reason"].split("; module-label only")[0]
        A(f"| `{r['species_id']}` | {nstr} | {reason} |")
    A("")
    A("ATP/ADP/AMP, GTP/GDP/GMP, PO4/Pi, PPi, CP and Cr keep **independent** "
      "resource identities. They are **not** collapsed into NTP/NXP; such a "
      "quantity may only ever be a derived reporting figure.")
    A("")
    A("## 7. Peptidyl-tRNA double bookkeeping")
    A("")
    A("| species | peptide moiety | tRNA moiety | class / pool |")
    A("| --- | --- | --- | --- |")
    for r in sorted(rows, key=lambda x: x["species_id"]):
        core = r["species_id"][: -len(DEGRADED_SUFFIX)] \
            if r["species_id"].endswith(DEGRADED_SUFFIX) else r["species_id"]
        if not PEPTIDYL_TRNA.match(core):
            continue
        cs = r["detected_components"].split(" + ")
        pep = next((c for c in cs if BARE_PEPTIDE.match(c)), "?")
        tr = next((c for c in cs if "tRNA" in c), "?")
        A(f"| `{r['species_id']}` | {pep} | {tr} | "
          f"{r['primary_reduction_class']}/{r['candidate_coarse_variable'] or '-'} |")
    A("")
    A("Each of these states carries **one peptide moiety and one tRNA moiety**, so "
      "any later conservation statement must count them **twice** — once in the "
      "peptide ledger, once in the tRNA ledger. They must **not** be merged with "
      "ordinary aminoacyl/charged tRNA (`GlytRNAGlyGCC`, `MettRNAfMetCAU`, "
      "`fMettRNAfMetCAU`), which stay `KEEP_EXPLICIT` as charging-ledger "
      "entities.")
    A("")
    A("## 8. Enzyme intermediates")
    A("")
    A("| enzyme / family | intermediate states |")
    A("| --- | --- |")
    fam = collections.Counter()
    for r in rows:
        if r["primary_reduction_class"] == "ENZYME_INTERMEDIATE":
            fam[r["species_id"].split("_")[0]] += 1
    for f, n in fam.most_common():
        A(f"| `{f}` | {n} |")
    A("")
    A("If an intermediate is later eliminated, the resource moieties it carries "
      "**stay in the ledger** through the `n_*` columns and its "
      "`*_family_total`.")
    A("")
    A("## 9. `MK_ADP_1` / `MK_ADP_2` / `MK_ADP_ADP`")
    A("")
    A("The `_1` / `_2` suffixes are **not** unknown tokens. The composition is "
      "resolved from the reaction topology, verified by an automatic moiety "
      "balance over the SBML reactions:")
    A("")
    for rid in MK_EVIDENCE_RXNS:
        line = fmt_reaction(rid, reactions)
        if line:
            A(f"- {line}")
    A("")
    A("So `MK_ADP_1` and `MK_ADP_2` are each **MK + 1 ADP** in two distinct "
      "binding-site / configuration states (each formed directly from MK + ADP, "
      "each dissociating back to MK + ADP, each one ADP away from `MK_ADP_ADP`), "
      "and `MK_ADP_ADP` is **MK + 2 ADP** (`n_ADP=2`, consistent with the "
      "myokinase step `2 ADP <=> ATP + AMP` via `MK_ATP_AMP`). All three are "
      "`ENZYME_INTERMEDIATE` in `MK_active_pool`; the conservation candidate is "
      "`MK_family_total`.")
    A("")
    A("## 10. Degraded terminal states")
    A("")
    deg = sorted((r for r in rows if r["primary_reduction_class"] == "DEGRADED_SINK"),
                 key=lambda x: x["species_id"])
    A(f"{len(deg)} `*_degraded` terminal states are **all retained** (none "
      "deleted) and enter only their `*_degraded_pool`; the conservation "
      "candidate is `*_family_total`.")
    A("")
    A("| species | components | degraded pool |")
    A("| --- | --- | --- |")
    for r in deg:
        A(f"| `{r['species_id']}` | {r['detected_components']} | "
          f"{r['conservation_family'] or '-'} |")
    A("")
    A("## 11. Bound-resource ledger risk")
    A("")
    A("These resources exist inside complexes. Deleting such a species **without** "
      "transferring its moieties into the reduced-variable definitions would drop "
      "the bound resource (including multiply-bound copies, see the `n_*` "
      "columns) from the conservation ledger.")
    A("")
    A("| resource | carrier complexes | total moiety copies | by reduction class |")
    A("| --- | --- | --- | --- |")
    for res in RESOURCES:
        holders = [r for r in rows if r[f"n_{res}"] > 0 and "_" in r["species_id"]]
        if holders:
            tot = sum(r[f"n_{res}"] for r in holders)
            byc = collections.Counter(r["primary_reduction_class"] for r in holders)
            A(f"| `{res}` | {len(holders)} | {tot} | "
              + ", ".join(f"{k}: {v}" for k, v in sorted(byc.items())) + " |")
    A("")
    A("## 12. Open scientific decisions")
    A("")
    A(f"The {len(sci)} flagged species below belong to the "
      f"{len(groups)} decision groups of section 3.")
    A("")
    for r in sorted(sci, key=lambda x: x["species_id"]):
        reason = r["reason"].split("; module-label only")[0]
        A(f"- `{r['species_id']}` [{r['primary_reduction_class']}] — {reason} "
          f"(`{r['rule_used']}`)")
    A("")
    A("## 13. Module-label conflicts only")
    A("")
    A("These species merely disagree between their name-prior module and their "
      "reaction-topology module — they legitimately act in several modules. There "
      "is **no reduction ambiguity** here, and no decision is owed:")
    A("")
    for r in sorted(mlo, key=lambda x: x["species_id"]):
        A(f"- `{r['species_id']}` [{r['primary_reduction_class']}]")
    A("")
    A("## 14. Invariants preserved by construction")
    A("")
    A("Enforced by `run_checks()` on every run:")
    A("")
    A("- `RS70S` and its complexes contribute to **both** the RS30S and RS50S "
      "moieties; `RS30S` and `RS50S` stay distinct and are never merged into "
      "`R_total`;")
    A("- peptidyl-tRNA contributes to **both** the peptide and tRNA ledgers, and "
      "never lands in a charged-tRNA pool;")
    A("- `ATP`, `ADP`, `AMP`, `GTP`, `GDP`, `GMP`, `PO4`, `PPi`, `CP`, `Cr` stay "
      "mutually distinct;")
    A("- `MK_ADP_1` / `MK_ADP_2` carry one ADP each, `MK_ADP_ADP` carries two;")
    A("- degraded states never leak into an `*_active_pool`;")
    A("- every `*_family_total` equals its `*_active_pool` + `*_degraded_pool`;")
    A("- a free resource species is always `KEEP_EXPLICIT` and flags exactly "
      "itself;")
    A("- every resource token inside a complex has a recorded multiplicity.")
    A("")
    A("## 15. Status")
    A("")
    A("This is still a **candidate** species-level reduction map. The mathematical "
      "reduction stage must still verify conservation, protein output, ATP/GTP "
      "consumption, Pi/PPi, CP/Cr, tRNA charging, ribosome occupancy, positivity "
      "and full-versus-reduced trajectory error. See "
      "`docs/reduction/reduction_map.md`, "
      "`docs/reduction/human_reduction_review.md` and "
      "`docs/reduction/candidate_core_v0.md`.")
    A("")
    return "\n".join(L)


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv-out", default=os.path.join(AUDIT, "species_reduction_map.csv"))
    ap.add_argument("--json-out", default=os.path.join(AUDIT, "species_reduction_map.json"))
    ap.add_argument("--md-out", default=os.path.join(DOCS, "species_reduction_map.md"))
    args = ap.parse_args()

    summary, species, reactions = load_audit_tables()
    if len(species) != summary["species_count"] or len(reactions) != summary["reaction_count"]:
        raise SystemExit("audit tables disagree with inventory_summary.json counts")

    before = sha256(SBML)
    registered = registered_digest()
    if before != registered:
        raise SystemExit(f"reference SBML digest {before} != registered {registered}")
    if sha256(RAW_SBML) != registered:
        raise SystemExit("the immutable raw drop and the working reference copy differ")

    rows, parsed = analyse(species, reactions)
    run_checks(rows, parsed, [s["id"] for s in species], reactions)

    after = sha256(SBML)
    assert before == after, "reference SBML changed during run"

    rows_sorted = sorted(rows, key=lambda r: r["species_id"])
    pools = build_pools(rows)
    fieldnames = [k for k in rows_sorted[0] if not k.startswith("_")]

    for path in (args.csv_out, args.json_out, args.md_out):
        os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(args.csv_out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for row in rows_sorted:
            w.writerow(row)

    payload = OrderedDict([
        ("meta", OrderedDict([
            ("source_sbml", SBML_REL),
            ("sbml_sha256", before),
            ("sbml_sha256_registered_in", f"{PROVENANCE_REL}::{PROVENANCE_ITEM}"),
            ("sbml_immutable_drop", RAW_SBML_REL),
            ("model_id", summary["model_id"]),
            ("n_species", len(species)),
            ("n_reactions", len(reactions)),
            ("map_version", MAP_VERSION),
            ("map_level", "species / moiety (complements the reaction-level map in "
                          "docs/reduction/reduction_decisions.csv)"),
            ("generator", GENERATOR),
            ("inputs", ["models/pnas2017_full_reference/audit/species.csv",
                        "models/pnas2017_full_reference/audit/reactions.csv",
                        "models/pnas2017_full_reference/audit/inventory_summary.json"]),
            ("provenance", PROVENANCE),
            ("reduction_class_counts",
             {c: sum(1 for r in rows if r["primary_reduction_class"] == c) for c in CLASSES}),
            ("scientific_review_counts",
             {c: sum(1 for r in rows if r["scientific_review_class"] == c)
              for c in REVIEW_CLASSES}),
            ("decision_groups",
             {k: sorted(v) for k, v in sorted(decision_groups(
                 [r for r in rows
                  if r["scientific_review_class"] == "SCIENTIFIC_DECISION_REQUIRED"]).items())}),
            ("disclaimer", "candidate reduction map only; every pool is a candidate for "
                           "later mathematical validation; no lumping/QSSA is claimed"),
        ])),
        ("pools", pools),
        ("species", [OrderedDict((k, v) for k, v in r.items() if not k.startswith("_"))
                     for r in rows_sorted]),
    ])
    # .gitattributes pins *.json to eol=lf so a fresh checkout reproduces the
    # recorded bytes on every platform; write LF explicitly to match.
    with open(args.json_out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    with open(args.md_out, "w", encoding="utf-8") as fh:
        fh.write(build_markdown(rows, pools, reactions, before, summary))

    cc = collections.Counter(r["primary_reduction_class"] for r in rows)
    rc = collections.Counter(r["scientific_review_class"] for r in rows)
    print(f"OK: {len(rows)} species, {len(reactions)} reactions; SBML sha256 stable")
    print("classes:", {c: cc.get(c, 0) for c in CLASSES})
    print("review:", {c: rc.get(c, 0) for c in REVIEW_CLASSES})
    print("pools:", len(pools))


if __name__ == "__main__":
    main()

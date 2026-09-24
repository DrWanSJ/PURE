#!/usr/bin/env python3
"""Build the PNAS 2017 chemical / resource ledger (Phase 5).

Reads the SBML inventory produced by scripts/parse_pnas2017_sbml.py
(species.csv, reactions.csv) and derives, WITHOUT any scientific editing of
the model:

  species_properties.csv    per-species class / module / resource annotations
  reaction_balance_audit.csv per-reaction resource-moiety accounting

Resource/moiety detection uses underscore tokenisation of the SBML species
identifier (CellDesigner-style complex names, e.g. ``EFTu_GTP_GlytRNAGlyGCC``
-> tokens EFTu, GTP, GlytRNAGlyGCC). A resource is:
  * "free pool"   when the species id EQUALS the resource token (e.g. GTP);
  * "in a complex"when the token appears among the species' underscore tokens
                    but the id is not exactly the token.

Charge, molecular formula and protonation are NOT encoded anywhere in this
SBML (no <annotation>, no formula attribute). Those fields are therefore
recorded as null / "unknown" and MUST NOT be guessed. Quantitative ionic
strength cannot be computed from these data and is deliberately not produced.
"""
import csv
import json
import os
from collections import OrderedDict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")

# Energy / small-molecule carrier tokens tracked by the ledger.
RESOURCE_TOKENS = OrderedDict([
    ("ATP", "ATP"), ("ADP", "ADP"), ("AMP", "AMP"),
    ("GTP", "GTP"), ("GDP", "GDP"),
    ("PPi", "PPi"), ("Pi_PO4", "PO4"),
    ("CP_creatine_phosphate", "CP"),
    ("creatine", "Cr"),
])
AMINO_ACIDS = {"Met", "Gly", "fMet"}
COFACTORS = {"THF", "GMP", "CMP", "UMP"}  # small molecules w/ no charge data
MACRO_CLASSES = {
    "ribosomal": ("RS70S", "RS50S", "RS30S"),
    "tRNA": ("tRNA",),
    "translation_factor": ("EFTu", "EFG", "EFTs", "IF1", "IF2", "IF3",
                           "RF1", "RF2", "RF3", "RRF", "MTF"),
    "aminoacyl_tRNA_synthetase": ("MetRS", "GlyRS"),
    "energy_regeneration_enzyme": ("CK", "NDK", "MK", "PPiase", "FD"),
    "mRNA": ("mRNA",),
}


def tokens(sid):
    return [t for t in sid.split("_") if t]


def base_species(sid):
    """Species id with a trailing _degraded removed."""
    return sid[:-9] if sid.endswith("_degraded") else sid


def is_degraded(sid):
    return sid.endswith("_degraded")


def classify(sid):
    """Return (molecule_class,) — a heuristic CANDIDATE only, human-reviewable."""
    b = base_species(sid)
    if b in AMINO_ACIDS or b == "fMet":
        return ("small_molecule:amino_acid",)
    if b in ("CP",):
        return ("small_molecule:energy_regeneration",)
    if b == "Cr":
        return ("small_molecule:creatine",)
    if b in RESOURCE_TOKENS.values() and b not in ("CP", "Cr"):
        return ("small_molecule:energy_carrier",)
    if b in COFACTORS:
        return ("small_molecule:cofactor_nucleotide",)
    # aminoacyl-adenylate intermediate (amino acid + AMP), e.g. GlyAMP, MetAMP
    if b.endswith("AMP") and any(b.startswith(a) for a in ("Met", "Gly")):
        return ("complex:aminoacyl_adenylate",)
    if b.startswith("Pept") or b.startswith("pept"):
        return ("macromolecule:peptide_product",)
    for grp, prefixes in MACRO_CLASSES.items():
        if b in prefixes:
            return ("macromolecule:%s" % grp,)
    # tRNA charged with an amino acid  (e.g. GlytRNAGlyGCC, fMettRNAfMetCAU)
    if "tRNA" in b:
        charged = any(b.startswith(a) for a in ("Met", "Gly", "fMet")) \
            and b not in ("tRNAfMetCAU", "tRNAGlyGCC")
        return ("complex:aminoacyl_tRNA" if charged else "macromolecule:tRNA",)
    if "_" in b:
        return ("complex:bound_state",)
    return ("unknown",)


def resource_delta(side_counter, resource_name, token):
    free = 0
    bound = 0
    for sid, n in side_counter.items():
        if sid == token:
            free += n
        elif token in tokens(sid):
            bound += n
    return free, bound


def parse_species_field(field):
    out = {}
    for item in filter(None, field.split("|")):
        sid, _, stoich = item.partition(":")
        try:
            n = float(stoich)
        except ValueError:
            n = 1.0
        out[sid] = out.get(sid, 0.0) + n
    return out


def main():
    species_rows = list(csv.DictReader(
        open(os.path.join(AUDIT, "species.csv"), encoding="utf-8")))
    reaction_rows = list(csv.DictReader(
        open(os.path.join(AUDIT, "reactions.csv"), encoding="utf-8")))

    init_by_id = {r["id"]: r for r in species_rows}

    # ---- species_properties.csv ----
    prop_rows = []
    for r in species_rows:
        sid = r["id"]
        cls = classify(sid)[0]
        subs = sorted({m for rxn in reaction_rows
                       if sid in parse_species_field(rxn["reactants"])
                       or sid in parse_species_field(rxn["products"])
                       for m in filter(None, rxn["subsystem_files"].split("|"))})
        prop_rows.append(OrderedDict([
            ("sbml_id", sid),
            ("sbml_name", r["name"]),
            ("functional_modules", "|".join(subs)),
            ("molecule_class", cls),
            ("is_complex_with_underscore", str("_" in sid).lower()),
            ("is_degraded_species", str(is_degraded(sid)).lower()),
            ("initial_concentration_author_export",
             r["author_export_initial_value"]),
            ("sbml_initial_concentration_placeholder",
             r["sbml_initial_concentration"]),
            ("dynamic_or_boundary",
             "boundary" if r["boundary_condition"] == "true" else "dynamic"),
            ("small_molecule", str(cls.startswith("small_molecule")).lower()),
            ("ATP", str("ATP" in tokens(sid)).lower()),
            ("ADP", str("ADP" in tokens(sid)).lower()),
            ("AMP", str("AMP" in tokens(sid)).lower()),
            ("GTP", str("GTP" in tokens(sid)).lower()),
            ("GDP", str("GDP" in tokens(sid)).lower()),
            ("Pi_PO4", str("PO4" in tokens(sid)).lower()),
            ("PPi", str("PPi" in tokens(sid)).lower()),
            ("creatine_phosphate", str("CP" in tokens(sid)).lower()),
            ("creatine", str(base_species(sid) == "Cr").lower()),
            ("amino_acid", str(base_species(sid) in AMINO_ACIDS).lower()),
            ("tRNA", str("tRNA" in sid).lower()),
            ("aminoacyl_tRNA", str(cls == "complex:aminoacyl_tRNA").lower()),
            ("ribosomal_species", str("RS70S" in sid or "RS50S" in sid
                                      or "RS30S" in sid).lower()),
            ("translation_factor", str("EF" in tokens(sid) or "IF" in
                                       tokens(sid) or base_species(sid) in
                                       MACRO_CLASSES["translation_factor"]
                                       ).lower()),
            ("aminoacyl_tRNA_synthetase",
             str(base_species(sid) in MACRO_CLASSES["aminoacyl_tRNA_synthetase"]
                 ).lower()),
            ("energy_regeneration_enzyme",
             str(base_species(sid) in
                 MACRO_CLASSES["energy_regeneration_enzyme"]).lower()),
            ("peptide_product", str("Pept" in sid or "pept" in sid).lower()),
            ("molecular_formula", ""),
            ("formula_provenance", ""),
            ("formal_net_charge", ""),
            ("charge_provenance", ""),
            ("protonation_convention", "unknown"),
            ("unresolved_fields",
             "molecular_formula,formal_net_charge,charge_provenance,"
             "protonation_convention"),
        ]))
    write_csv(os.path.join(AUDIT, "species_properties.csv"), prop_rows)

    # ---- reaction_balance_audit.csv ----
    bal_rows = []
    for rxn in reaction_rows:
        react = parse_species_field(rxn["reactants"])
        prod = parse_species_field(rxn["products"])
        row = OrderedDict([
            ("reaction_id", rxn["id"]),
            ("subsystem_files", rxn["subsystem_files"]),
            ("n_reactant_species", rxn["n_reactants"]),
            ("n_product_species", rxn["n_products"]),
            ("net_particle_number_change",
             "%.0f" % (sum(prod.values()) - sum(react.values()))),
        ])
        for name, token in RESOURCE_TOKENS.items():
            rf, rb = resource_delta(react, name, token)
            pf, pb = resource_delta(prod, name, token)
            row["%s_free_net" % name] = "%.0f" % ((pf + pb) - (rf + rb))
            row["%s_consumed_free" % name] = "%.0f" % max(0.0, rf - pf)
            row["%s_produced_free" % name] = "%.0f" % max(0.0, pf - rf)
        bal_rows.append(row)
    write_csv(os.path.join(AUDIT, "reaction_balance_audit.csv"), bal_rows)

    # ---- summary ----
    from collections import Counter
    cls_counter = Counter(p["molecule_class"] for p in prop_rows)
    print(json.dumps(OrderedDict([
        ("species_count", len(prop_rows)),
        ("molecule_class_counts", dict(cls_counter)),
        ("reactions_count", len(bal_rows)),
        ("charge_formula_available", False),
        ("ionic_strength_computable", False),
    ]), indent=2))
    print("\nWrote species_properties.csv and reaction_balance_audit.csv")


def write_csv(path, rows):
    if not rows:
        open(path, "w").close()
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()

"""Exact, read-only source audit for the four-step CHAIN_01 local experiment.

Only newly generated audit files are written. Source data, historical evidence,
scientific decisions, and Git state are never mutated. Uses the standard library.
The canonical MathML, rather than a speciesReference accessor default, supplies
stoichiometry. All quantities tagged ``*_exact`` are rational strings.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SBML = "{http://www.sbml.org/sbml/level2/version4}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
CHAIN_IDS = tuple(f"re{i:010d}" for i in (14, 16, 17, 18))
SOURCE_DIR = Path("models/pnas2017_full_reference/original")
DAT_DIR = SOURCE_DIR / "simulate/Simulate_fMGG_synthesis/dat"
SOURCE_PATHS = (
    SOURCE_DIR / "fMGG_synthesis.xml",
    DAT_DIR / "fMGG_synthesis_parameters.csv",
    DAT_DIR / "fMGG_synthesis_initial_values.csv",
    DAT_DIR / "fMGG_synthesis_reactions.csv",
    Path("results/topology_audit/reactions_table.csv"),
    Path("results/topology_audit/case_study.json"),
    Path("docs/reduction/one_chain_reduction_case_study.md"),
    Path("docs/reduction/topology_first_audit.md"),
    Path("docs/reduction/reaction_inventory_and_effective_rate_review.md"),
    Path("docs/reduction/qssa_repositioning_note.md"),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csv_rows(path: Path) -> list[dict[str, str]]:
    # Keep raw hashes distinct; newline normalization is only a parsing operation.
    text = path.read_bytes().decode("utf-8-sig").replace("\r\r\n", "\n")
    return list(csv.DictReader(io.StringIO(text)))


def exact_constant(node: ET.Element) -> Fraction:
    """Evaluate constant MathML exactly; reject symbolic stoichiometry."""
    tag = node.tag.rsplit("}", 1)[-1]
    if tag == "math":
        if len(node) != 1:
            raise ValueError("Expected one constant MathML expression")
        return exact_constant(node[0])
    if tag == "cn":
        kind = node.get("type", "real")
        if kind in ("rational", "e-notation"):
            if len(node) != 1 or node[0].tag != MATH + "sep":
                raise ValueError("Malformed separated MathML number")
            left = Fraction((node.text or "").strip())
            right = Fraction((node[0].tail or "").strip())
            if kind == "rational":
                return left / right
            if right.denominator != 1:
                raise ValueError("Noninteger MathML decimal exponent")
            return left * Fraction(10) ** int(right)
        return Fraction((node.text or "").strip())
    if tag == "apply" and len(node) >= 2:
        op = node[0].tag.rsplit("}", 1)[-1]
        args = [exact_constant(n) for n in node[1:]]
        if op == "plus":
            return sum(args, Fraction(0))
        if op == "times":
            ans = Fraction(1)
            for arg in args:
                ans *= arg
            return ans
        if op == "minus" and len(args) == 1:
            return -args[0]
        if op == "minus" and len(args) == 2:
            return args[0] - args[1]
        if op == "divide" and len(args) == 2:
            return args[0] / args[1]
        if op == "power" and len(args) == 2 and args[1].denominator == 1:
            return args[0] ** int(args[1])
    raise ValueError(f"Unsupported constant MathML: {ET.tostring(node, encoding='unicode')}")


def refs(reaction: ET.Element, side: str) -> dict[str, Fraction]:
    result: dict[str, Fraction] = defaultdict(Fraction)
    for ref in reaction.findall(f"{SBML}listOf{side}/{SBML}speciesReference"):
        math = ref.find(f"{SBML}stoichiometryMath/{MATH}math")
        coefficient = exact_constant(math) if math is not None else Fraction(ref.get("stoichiometry", "1"))
        if coefficient < 0:
            raise ValueError("Negative source stoichiometric coefficient")
        result[ref.attrib["species"]] += coefficient
    return dict(result)


def kinetic_product(node: ET.Element) -> list[str]:
    """Audit this model's multiplicative kinetic shape without assuming it."""
    tag = node.tag.rsplit("}", 1)[-1]
    if tag == "math" and len(node) == 1:
        return kinetic_product(node[0])
    if tag == "ci":
        return [(node.text or "").strip()]
    if tag == "cn":
        return [str(exact_constant(node))]
    if tag == "apply" and node[0].tag == MATH + "times":
        return [factor for child in node[1:] for factor in kinetic_product(child)]
    raise ValueError("Unsupported kinetic shape; no activity conclusion made")


def stringify(mapping: dict[str, Fraction]) -> dict[str, str]:
    return {key: str(value) for key, value in sorted(mapping.items())}


def parse_sources(repo: Path) -> tuple[dict, dict, dict, dict]:
    model = ET.parse(repo / SOURCE_PATHS[0]).getroot().find(SBML + "model")
    if model is None:
        raise ValueError("Canonical SBML model missing")
    species = {s.attrib["id"]: dict(s.attrib) for s in model.findall(f"{SBML}listOfSpecies/{SBML}species")}
    parameter_rows = csv_rows(repo / SOURCE_PATHS[1])
    author = {r["Name"]: Fraction(r["Value"]) for r in parameter_rows}
    if len(author) != len(parameter_rows):
        raise ValueError("Duplicate author parameter names")
    initial_rows = csv_rows(repo / SOURCE_PATHS[2])
    initial = {r["Name"]: Fraction(r["Value"]) for r in initial_rows}
    if set(initial) != set(species) or len(initial) != len(initial_rows):
        raise ValueError("Author initial species set mismatch")
    global_parameters = {p.attrib["id"]: dict(p.attrib) for p in model.findall(f"{SBML}listOfParameters/{SBML}parameter")}
    reactions = {}
    for reaction in model.findall(f"{SBML}listOfReactions/{SBML}reaction"):
        rid = reaction.attrib["id"]
        kinetic = reaction.find(SBML + "kineticLaw")
        if kinetic is None:
            raise ValueError(f"Missing kinetic law for {rid}")
        math = kinetic.find(MATH + "math")
        if math is None:
            raise ValueError(f"Missing kinetic MathML for {rid}")
        factors = kinetic_product(math)
        local = [dict(p.attrib) for p in kinetic.findall(f"{SBML}listOfParameters/{SBML}parameter")]
        parameters = []
        for p in local:
            name = f"{rid}_{p['id']}"
            if name not in author:
                raise ValueError(f"Missing author parameter {name}")
            parameters.append({"parameter_id": p["id"], "source_attributes": p,
                               "author_csv_name": name, "author_value_exact": str(author[name]),
                               "author_value": float(author[name]),
                               "sbml_placeholder_exact": str(Fraction(p["value"]))})
        ids = [p["parameter_id"] for p in parameters]
        symbols = [(n.text or "").strip() for n in math.iter(MATH + "ci")]
        unknown = set(symbols) - set(species) - set(ids) - set(global_parameters)
        if unknown:
            raise ValueError(f"Unknown kinetic dependencies for {rid}: {unknown}")
        if any(p in global_parameters for p in symbols):
            raise ValueError("Global kinetic parameters require an explicit author overlay audit")
        reactants, products = refs(reaction, "Reactants"), refs(reaction, "Products")
        net = {s: products.get(s, Fraction(0)) - reactants.get(s, Fraction(0)) for s in reactants.keys() | products.keys()}
        net = {s: v for s, v in net.items() if v}
        modifiers = sorted(m.attrib["species"] for m in reaction.findall(f"{SBML}listOfModifiers/{SBML}modifierSpeciesReference"))
        zero = any(Fraction(p["author_value_exact"]) == 0 for p in parameters if p["parameter_id"] in factors)
        reactions[rid] = {"reaction_id": rid, "source_attributes": dict(reaction.attrib),
                          "reactants_exact": stringify(reactants), "products_exact": stringify(products),
                          "net_stoichiometry_exact": stringify(net), "modifiers": modifiers,
                          "kinetic_factors": factors, "kinetic_law_formula": " * ".join(factors),
                          "kinetic_mathml": ET.tostring(math, encoding="unicode"),
                          "kinetic_species": sorted(set(symbols) & set(species)),
                          "author_parameters": parameters,
                          "author_activity": "IDENTICALLY_ZERO_FIXED_AUTHOR_PARAMETERS" if zero else "NONZERO_K_POTENTIALLY_ENABLED"}
    expected = {f"{rid}_{p['parameter_id']}" for rid, r in reactions.items() for p in r["author_parameters"]}
    compartments = {c.attrib["id"]: dict(c.attrib) for c in model.findall(f"{SBML}listOfCompartments/{SBML}compartment")}
    if set(author) != expected | set(compartments):
        raise ValueError("Author parameter coverage does not equal source local parameters plus compartments")
    for cid, c in compartments.items():
        if author[cid] != Fraction(c["size"]):
            raise ValueError("Author compartment size differs from source; concentration scaling needs review")
    units = {"model_attributes": dict(model.attrib), "compartment_attributes": compartments,
             "unit_definitions": [ET.tostring(n, encoding="unicode") for n in model.findall(f"{SBML}listOfUnitDefinitions/{SBML}unitDefinition")],
             "source_kinetic_parameter_units": sorted({p["source_attributes"].get("units", "UNSPECIFIED") for r in reactions.values() for p in r["author_parameters"]}),
             "time_unit_label": "source model time unit",
             "interpretation": "The model has no explicit time-unit declaration or custom unitDefinitions. Local k1 carries the source label 'substance'; retain it as source metadata, not a dimensionally repaired unit. CSV values have no unit column. No conversion to seconds is made."}
    return reactions, species, initial, {"units": units, "counts": {"species": len(species), "reactions": len(reactions), "author_parameter_rows": len(parameter_rows)}}


def audit_sources(repo: Path = ROOT) -> dict:
    """Return an evidence-bound manifest; perform no writes and no simulations."""
    repo = repo.resolve()
    reactions, species, initial, source_info = parse_sources(repo)
    chain = [reactions[rid] for rid in CHAIN_IDS]
    for r in chain:
        if len(r["reactants_exact"]) != 1 or next(iter(r["reactants_exact"].values())) != "1":
            raise ValueError("Selected chain is not a unit-coefficient single-reactant path")
        if r["source_attributes"].get("reversible", "false") != "false" or r["modifiers"]:
            raise ValueError("Selected chain direction/modifiers do not match the local contract")
        expected_factors = ["k1", next(iter(r["reactants_exact"]))]
        if r["kinetic_factors"] != expected_factors or len(r["author_parameters"]) != 1:
            raise ValueError("Selected chain is not exactly k1 times its reactant")
    state_ids = [next(iter(r["reactants_exact"])) for r in chain]
    s4 = [s for s in chain[-1]["products_exact"] if s not in ("PO4", "EFTu_GDP")]
    if len(s4) != 1:
        raise ValueError("Cannot identify S4 uniquely")
    state_ids += s4
    if len(set(state_ids)) != 5:
        raise ValueError("Four-step state identities are not distinct")
    for i, r in enumerate(chain[:-1]):
        if r["products_exact"].get(state_ids[i + 1]) != "1":
            raise ValueError("Selected reactions do not join in requested order")
    aliases = {f"S{i}": sid for i, sid in enumerate(state_ids)}
    rates_exact = [Fraction(r["author_parameters"][0]["author_value_exact"]) for r in chain]
    if any(k <= 0 for k in rates_exact):
        raise ValueError("The four author rates must be positive")
    # This is a source-check assertion, not assignment of rates to the model.
    expected_author_rates = [Fraction(x) for x in (260, 1000, 7, 1000)]
    if rates_exact != expected_author_rates:
        raise ValueError("Author rates differ from task's expected source values")
    tau = sum((1 / k for k in rates_exact), Fraction(0))
    net = defaultdict(Fraction)
    for r in chain:
        for sid, coefficient in r["net_stoichiometry_exact"].items():
            net[sid] += Fraction(coefficient)
    candidate = {state_ids[0]: Fraction(-1), state_ids[-1]: Fraction(1), "PO4": Fraction(1), "EFTu_GDP": Fraction(1)}
    all_rows = [{"species_id": sid, "sum_of_four_columns_exact": str(net.get(sid, 0)),
                 "candidate_exact": str(candidate.get(sid, 0)),
                 "difference_exact": str(net.get(sid, 0) - candidate.get(sid, 0))} for sid in species]
    exact_pass = all(row["difference_exact"] == "0" for row in all_rows)
    if not exact_pass:
        raise ValueError("Four-column sum differs from the candidate net reaction")
    incidence = {}
    for alias, sid in aliases.items():
        entries = []
        for r in reactions.values():
            roles = [role for role, field in (("reactant", "reactants_exact"), ("product", "products_exact"),
                                              ("modifier", "modifiers"), ("kinetic_dependency", "kinetic_species")) if sid in r[field]]
            if roles:
                entry = dict(r)
                entry.update({"species_id": sid, "alias": alias, "roles": roles,
                              "chain_membership": "CHAIN" if r["reaction_id"] in CHAIN_IDS else "SURROUNDING_NETWORK",
                              "domain_role": "INTERNAL_SIDE_PATH" if alias in ("S1", "S2", "S3") and r["reaction_id"] not in CHAIN_IDS else ("BOUNDARY_NETWORK_INCIDENCE" if r["reaction_id"] not in CHAIN_IDS else "CHAIN")})
                entries.append(entry)
        incidence[alias] = {"species_id": sid, "canonical_attributes": species[sid],
                            "author_initial_exact": str(initial[sid]),
                            "all_incidence_count": len(entries), "incidences": entries,
                            "nonzero_author_reaction_ids": [r["reaction_id"] for r in entries if r["author_activity"] == "NONZERO_K_POTENTIALLY_ENABLED"],
                            "zero_author_reaction_ids": [r["reaction_id"] for r in entries if r["author_activity"] == "IDENTICALLY_ZERO_FIXED_AUTHOR_PARAMETERS"]}
    internal_active = sorted({r["reaction_id"] for alias in ("S1", "S2", "S3") for r in incidence[alias]["incidences"]
                             if r["chain_membership"] != "CHAIN" and r["author_activity"] == "NONZERO_K_POTENTIALLY_ENABLED"})
    if internal_active:
        raise ValueError(f"Internal chain states have author-active side incidences: {internal_active}")
    # Cross-check the entire existing reaction table, not just selected rows.
    table_rows = csv_rows(repo / SOURCE_PATHS[4])
    table = {r["reaction_id"]: r for r in table_rows}
    if len(table_rows) != len(reactions) or set(table) != set(reactions):
        raise ValueError("Topology reaction-table coverage mismatch")
    for rid, r in reactions.items():
        row = table[rid]
        for column, key in (("substrates_json", "reactants_exact"), ("products_json", "products_exact")):
            values = json.loads(row[column], parse_float=Fraction, parse_int=Fraction)
            if {s: Fraction(v) for s, v in values.items()} != {s: Fraction(v) for s, v in r[key].items()}:
                raise ValueError(f"Topology table stoichiometry mismatch for {rid}")
        if set(json.loads(row["modifiers_json"])) != set(r["modifiers"]) or set(json.loads(row["kinetic_species_json"])) != set(r["kinetic_species"]):
            raise ValueError(f"Topology modifier/kinetic dependencies mismatch for {rid}")
        if row["kinetic_law_formula"] != r["kinetic_law_formula"]:
            raise ValueError(f"Topology kinetic law mismatch for {rid}")
        if Fraction(row["author_rate_coefficient"]) != Fraction(r["author_parameters"][0]["author_value_exact"]):
            raise ValueError(f"Topology author parameter mismatch for {rid}")
    old_case = json.loads((repo / SOURCE_PATHS[5]).read_text(encoding="utf-8"))
    old_ids = old_case["serial_reaction_ids"]
    if old_ids != list(CHAIN_IDS[1:]):
        raise ValueError("Existing case study no longer refers to the expected three-step segment")
    inventory = (repo / SOURCE_PATHS[8]).read_text(encoding="utf-8").split("## 5.", 1)[1].split("## 6.", 1)[0]
    inventory_rows = re.findall(r"^\| `(re\d+)` \|.*?\| ([0-9.eE+-]+) \| (?:binding|release|transition) \|", inventory, re.MULTILINE)
    if len(inventory_rows) != len(reactions) or len({rid for rid, _ in inventory_rows}) != len(reactions):
        raise ValueError("Existing full reaction inventory must contain each of the 968 directions once")
    for rid, value in inventory_rows:
        if Fraction(value) != Fraction(reactions[rid]["author_parameters"][0]["author_value_exact"]):
            raise ValueError(f"Inventory author parameter mismatch for {rid}")
    sources = [{"path": path.as_posix(), "sha256": sha256(repo / path), "bytes": (repo / path).stat().st_size,
                "provenance": "EXTRACTED", "freshness": "CURRENT_WORKTREE_BYTES_AT_AUDIT",
                "git_blob_id": subprocess.check_output(["git", "rev-parse", f"HEAD:{path.as_posix()}"], cwd=repo, text=True).strip()} for path in SOURCE_PATHS]
    source_status = subprocess.check_output(["git", "status", "--porcelain", "--", *[p.as_posix() for p in SOURCE_PATHS]], cwd=repo, text=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=repo, text=True).strip()
    return {"schema_version": "chain01_source_manifest_v1", "audit_status": "PASSED_EXACT_SOURCE_AUDIT",
            "provenance_class": "EXTRACTED", "scientific_approval": "HUMAN_REVIEW_REQUIRED",
            "git_context": {"head": head, "branch": branch, "source_paths_status_porcelain": source_status,
                            "note": "Only source-path status is recorded for deterministic regeneration; the final task reports all workspace changes separately."},
            "sources": sources, "source_model": source_info, "species_aliases": aliases,
            "chain_reaction_ids": list(CHAIN_IDS), "chain_reactions": chain,
            "author_rates": [float(k) for k in rates_exact], "author_rates_exact": [str(k) for k in rates_exact],
            "tau": float(tau), "tau_exact": str(tau), "k_eff": float(1 / tau), "k_eff_exact": str(1 / tau),
            "candidate_class": "MEAN_DWELL_MATCHED_CANDIDATE",
            "stoichiometry_exact": {"status": "PASS", "method": "Fraction evaluation of canonical stoichiometryMath and sum of all four directed columns",
                                    "species_compared": len(species), "sum_nonzero_exact": stringify({s: v for s, v in net.items() if v}),
                                    "candidate_nonzero_exact": stringify(candidate), "per_species_comparison": all_rows,
                                    "limitation": "Source reaction-vector identity only; no atomic/ionic balance or instantaneous release equivalence claimed."},
            "species_incidence_audit": incidence,
            "domain_summary": {"internal_states": ["S1", "S2", "S3"], "internal_author_active_side_reactions": internal_active,
                               "internal_all_side_reactions": sorted({r["reaction_id"] for alias in ("S1", "S2", "S3") for r in incidence[alias]["incidences"] if r["chain_membership"] != "CHAIN"}),
                               "boundary_author_active_surrounding": {alias: [r["reaction_id"] for r in incidence[alias]["incidences"] if r["chain_membership"] != "CHAIN" and r["author_activity"] == "NONZERO_K_POTENTIALLY_ENABLED"] for alias in ("S0", "S4")},
                               "boundary_author_active_details": {alias: [{"reaction_id": r["reaction_id"], "roles": r["roles"],
                                                                           "kinetic_law_formula": r["kinetic_law_formula"],
                                                                           "author_parameters": r["author_parameters"],
                                                                           "reactants_exact": r["reactants_exact"], "products_exact": r["products_exact"]}
                                                                          for r in incidence[alias]["incidences"] if r["chain_membership"] != "CHAIN" and r["author_activity"] == "NONZERO_K_POTENTIALLY_ENABLED"] for alias in ("S0", "S4")},
                               "active_S0_competing_consuming_reactions": [r["reaction_id"] for r in incidence["S0"]["incidences"] if r["chain_membership"] != "CHAIN" and "reactant" in r["roles"] and r["author_activity"] == "NONZERO_K_POTENTIALLY_ENABLED"],
                               "local_boundary_intervention": "Replace source S0-producing surrounding-network kinetics with prescribed u(t); suppress the author-active competing S0 exit re0000000021 (k=0.23); omit S4 consumption re0000000019 (k=30) and surrounding return re0000000020 (k=25). These are local experiment assumptions, not source parameter changes. The canonical source and its overlay retain every direction.",
                               "interpretation": "Internal side incidences exist in the canonical network but are identically zero under the fixed author CSV. S0 and S4 have author-active surrounding reactions. The imposed local boundaries, including suppression of the active S0 exit, do not represent the full coupled network. Nonzero k indicates potential activity, not a certified trajectory."},
            "resource_semantics": {"PO4_free_release": "v16 / xi16", "EFTu_GDP_free_release": "v17 / xi17",
                                   "bound_phosphate_inventory": "x1", "ribosome_bound_EFTu_GDP_inventory": "x1+x2",
                                   "ribosome_bound_EFTu_GTP_inventory": "x0", "unfinished_ribosome_inventory": "x0+x1+x2+x3",
                                   "GTP_gamma_phosphate_precursor_inventory": "x0 (GTP-bound precursor, distinct from the PO4-bound x1)",
                                   "phosphate_fate_identity": "x0+x1+xi16 = x0(0)+x1(0)+integral(u)",
                                   "Tu_factor_fate_identity": "x0+x1+x2+xi17 = x0(0)+x1(0)+x2(0)+integral(u)",
                                   "endpoint_ribosome_inventory": "x4 (still a ribosome-bound peptide state; local completion is not free ribosome or final Pept0003 release)"},
            "existing_evidence_crosscheck": {"reactions_table_all_rows": len(table_rows), "inventory_all_rows": len(inventory_rows), "status": "PASS",
                                             "old_three_step_reactions": old_ids, "old_case_aliases_shift": "old A/X1/X2/B correspond to new S1/S2/S3/S4",
                                             "warning": "The old three-step k_eff is not the four-step rate. Historical scientific conclusions remain unchanged."}}


def write_audit(manifest: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    fields = ["alias", "species_id", "reaction_id", "roles", "domain_role", "author_activity", "author_parameters", "reactants_exact", "products_exact", "kinetic_law_formula"]
    with (output_dir / "source_incidence_audit.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        for state in manifest["species_incidence_audit"].values():
            for incidence in state["incidences"]:
                row = {key: incidence[key] for key in fields}
                for key, value in row.items():
                    if isinstance(value, (dict, list)):
                        row[key] = json.dumps(value, sort_keys=True, separators=(",", ":"))
                writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--verify", action="store_true", help="Regenerate in memory and compare the existing manifest without writing")
    args = parser.parse_args()
    manifest = audit_sources(args.repo)
    out = args.output_dir or args.repo / "results/reduction/chain01_four_step"
    if args.verify:
        saved = json.loads((out / "source_manifest.json").read_text(encoding="utf-8"))
        if saved != manifest:
            raise ValueError("Saved source manifest differs from current exact audit; preserve it and investigate drift")
    else:
        write_audit(manifest, out)
    print(json.dumps({"audit_status": manifest["audit_status"], "author_rates": manifest["author_rates"],
                      "tau": manifest["tau"], "k_eff": manifest["k_eff"],
                      "internal_author_active_side_reactions": manifest["domain_summary"]["internal_author_active_side_reactions"],
                      "boundary_author_active_surrounding": manifest["domain_summary"]["boundary_author_active_surrounding"],
                      "manifest": str(out / "source_manifest.json")}, indent=2))


if __name__ == "__main__":
    main()

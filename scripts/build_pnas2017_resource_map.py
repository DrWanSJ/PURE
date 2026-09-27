"""Build a reviewable resource/reduction navigation layer from frozen sources.

All classifications are candidates. SBML and the authors' simulator CSVs remain
the source; generated tables never become a second scientific model.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
MODULE_ZIP = ROOT / "references/PNAS2017_Matsuura/raw/SBML_files.zip"
SIM_ZIP = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
OUT = ROOT / "models/pnas2017_full_reference/audit"
RED = ROOT / "docs/reduction"
NS = "{http://www.sbml.org/sbml/level2/version4}"
CD = "{http://www.sbml.org/2001/ns/celldesigner}"
MATH = "{http://www.w3.org/1998/Math/MathML}"
DOI = "10.1073/pnas.1615351114"
CURRENCIES = ("ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr", "Gly", "Met", "fMet", "tRNAGlyGCC", "tRNAfMetCAU", "GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU")
FREE_SMALL = {"ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr", "Gly", "Met", "fMet", "FD", "THF"}
PEPTIDES = {"Pept0002", "Pept0003"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv_member(archive: zipfile.ZipFile, suffix: str) -> list[dict[str, str]]:
    members = [name for name in archive.namelist() if name.endswith(suffix)]
    if len(members) != 1:
        raise ValueError(f"Expected one {suffix}, got {members}")
    source_text = archive.read(members[0]).decode("utf-8-sig")
    # The official CSV members use CR-CR-LF; normalize only in memory.
    text = source_text.replace("\r\r\n", "\n").replace("\r\n", "\n")
    return list(csv.DictReader(io.StringIO(text)))


def references(reaction: ET.Element, side: str) -> dict[str, float]:
    found: dict[str, float] = defaultdict(float)
    parent = reaction.find(NS + "listOf" + side)
    if parent is None:
        return {}
    for item in parent:
        if item.tag != NS + "speciesReference":
            continue
        stoichiometry_math = item.find(NS + "stoichiometryMath")
        if stoichiometry_math is not None:
            numbers = stoichiometry_math.findall(".//" + MATH + "cn")
            if len(numbers) != 1 or len(list(stoichiometry_math.findall(".//" + MATH + "apply"))) != 0:
                raise ValueError("Nonconstant stoichiometryMath needs explicit handling")
            stoichiometry = float(numbers[0].text.strip())
        else:
            stoichiometry = float(item.get("stoichiometry", "1"))
        found[item.attrib["species"]] += stoichiometry
    return dict(found)


def signature(reaction: ET.Element) -> tuple:
    return (
        tuple(sorted(references(reaction, "Reactants").items())),
        tuple(sorted(references(reaction, "Products").items())),
    )


def module_level(name: str) -> str:
    if name.startswith("Initiation"):
        return "initiation"
    if name.startswith("Elongation"):
        return "elongation"
    if name.startswith("Aminoacylation") or name.startswith("FMet"):
        return "aminoacylation"
    if name.startswith("Termination"):
        return "termination / ribosome recycling"
    if name.startswith("EnergyRegeneration") or name == "SmallMolecules":
        return "energy regeneration"
    return "UNKNOWN"


def module_process(name: str) -> str:
    if name.startswith("Aminoacylation_A"):
        return "amino acid activation / aminoacyl-adenylate"
    if name.startswith("Aminoacylation_B"):
        return "tRNA aminoacylation"
    if name == "FMet_tRNASynthesis":
        return "initiator tRNA formylation"
    if name.startswith("EnergyRegeneration_A"):
        return "creatine kinase carrier regeneration"
    if name.startswith("EnergyRegeneration_B"):
        return "nucleotide diphosphate kinase carrier exchange"
    if name.startswith("EnergyRegeneration_C"):
        return "adenylate kinase carrier exchange"
    if name.startswith("EnergyRegeneration_D"):
        return "pyrophosphate hydrolysis"
    if name == "SmallMolecules":
        return "shared small-molecule reactions"
    if name.startswith("Initiation"):
        return "translation initiation"
    if name.startswith("Elongation"):
        return "elongation / translocation"
    if name.startswith("Termination"):
        return "termination / ribosome recycling"
    return "unknown biochemical process"


def species_class(identifier: str) -> tuple[str, str]:
    if identifier in FREE_SMALL:
        return "small molecule", "EXTRACTED_NAME_AND_INFERRED_CLASS"
    if identifier in PEPTIDES:
        return "peptide product/intermediate", "INFERRED_FROM_ID"
    if "_" in identifier and not identifier.endswith("_degraded"):
        return "complex", "INFERRED_FROM_ID"
    if identifier.endswith("_degraded"):
        return "degraded state", "INFERRED_FROM_ID"
    if "tRNA" in identifier or identifier == "mRNA":
        return "RNA", "INFERRED_FROM_ID"
    if identifier.startswith(("RS", "elRS", "termRS")):
        return "ribosomal species", "INFERRED_FROM_ID"
    if identifier.startswith(("EFT", "EFG", "IF", "RF", "RRF", "GlyRS", "MetRS", "CK", "NDK", "MK", "PPiase", "MTF")):
        return "protein/enzyme", "INFERRED_FROM_ID"
    return "unresolved", "AMBIGUOUS"


def resource_flags(identifier: str) -> dict[str, bool]:
    tokens = identifier.split("_")
    exact = lambda name: identifier == name  # free species, not bound moieties
    return {
        "ATP": exact("ATP"), "ADP": exact("ADP"), "AMP": exact("AMP"),
        "GTP": exact("GTP"), "GDP": exact("GDP"), "Pi": exact("PO4"),
        "PPi": exact("PPi"), "creatine_phosphate": exact("CP"),
        "creatine": exact("Cr"),
        "amino_acid": identifier in {"Gly", "Met", "fMet"},
        "tRNA": identifier in {"tRNAGlyGCC", "tRNAfMetCAU"},
        "aminoacyl_tRNA": identifier in {"GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU"},
        "ribosomal_species": any(x in identifier for x in ("RS30S", "RS50S", "RS70S")),
        "translation_factor": any(x in identifier for x in ("EFTu", "EFTs", "EFG", "IF1", "IF2", "IF3", "RF1", "RF2", "RF3", "RRF")),
        "aminoacyl_tRNA_synthetase": any(x in tokens for x in ("GlyRS", "MetRS")),
        "energy_regeneration_enzyme": any(x in tokens for x in ("CK", "NDK", "MK", "PPiase")),
        "peptide_product": identifier in PEPTIDES,
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError(f"Empty table: {path}")
    fields = list(rows[0])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def net_value(reactants: dict[str, float], products: dict[str, float], key: str) -> float:
    return products.get(key, 0.0) - reactants.get(key, 0.0)


def format_ids(ids: list[str]) -> str:
    return ", ".join(ids)


def main() -> None:
    source_hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in (MODEL, MODULE_ZIP, SIM_ZIP)}
    model = ET.parse(MODEL).getroot().find(NS + "model")
    if model is None:
        raise ValueError("No SBML model")
    species = model.findall("./" + NS + "listOfSpecies/" + NS + "species")
    reactions = model.findall("./" + NS + "listOfReactions/" + NS + "reaction")
    if (len(species), len(reactions)) != (241, 968):
        raise ValueError(f"Unexpected literal source counts: {len(species)}, {len(reactions)}")
    with zipfile.ZipFile(SIM_ZIP) as archive:
        initial_rows = read_csv_member(archive, "fMGG_synthesis_initial_values.csv")
        parameter_rows = read_csv_member(archive, "fMGG_synthesis_parameters.csv")
    initial = {row["Name"]: float(row["Value"]) for row in initial_rows}
    parameters = {row["Name"]: float(row["Value"]) for row in parameter_rows}
    species_ids = [item.attrib["id"] for item in species]
    if len(initial_rows) != 241 or len(initial) != 241 or set(initial) != set(species_ids):
        raise ValueError("Official initial CSV does not match combined SBML species IDs")
    if sum(value > 0 for value in initial.values()) != 27:
        raise ValueError("Expected 27 positive reference initial components")

    module_matches: dict[tuple, list[dict[str, str]]] = defaultdict(list)
    with zipfile.ZipFile(MODULE_ZIP) as archive:
        if len([n for n in archive.namelist() if n.endswith(".xml")]) != 26:
            raise ValueError("Expected 26 original subsystem XML files")
        for member in archive.namelist():
            if not member.endswith(".xml"):
                continue
            module = Path(member).stem
            root = ET.fromstring(archive.read(member))
            for reaction in root.findall("./" + NS + "model/" + NS + "listOfReactions/" + NS + "reaction"):
                local_type = reaction.find(".//" + CD + "reactionType")
                module_matches[signature(reaction)].append({
                    "module": module,
                    "local_id": reaction.attrib["id"],
                    "cell_designer_type": (local_type.text or "").strip() if local_type is not None else "UNKNOWN",
                })

    species_to_modules: dict[str, set[str]] = defaultdict(set)
    balance_rows: list[dict] = []
    decision_rows: list[dict] = []
    module_to_ids: dict[str, list[str]] = defaultdict(list)
    module_to_species: dict[str, set[str]] = defaultdict(set)
    level_to_ids: dict[str, set[str]] = defaultdict(set)
    mapping_counts = Counter()

    for reaction in reactions:
        rid = reaction.attrib["id"]
        reactants, products = references(reaction, "Reactants"), references(reaction, "Products")
        participants = set(reactants) | set(products)
        matches = module_matches.get(signature(reaction), [])
        match_status = "EXTRACTED_EXACT_STOICHIOMETRY" if len(matches) == 1 else ("AMBIGUOUS_MULTIPLE_SUBSYSTEMS" if matches else "UNMAPPED")
        mapping_counts[match_status] += 1
        modules = sorted({m["module"] for m in matches})
        levels = sorted({module_level(m) for m in modules})
        for module_name in modules:
            module_to_ids[module_name].append(rid)
            module_to_species[module_name].update(participants)
            for sid in participants:
                species_to_modules[sid].add(module_name)
        for level in levels:
            level_to_ids[level].add(rid)
        ctype_element = reaction.find(".//" + CD + "reactionType")
        local_types = {m["cell_designer_type"] for m in matches}
        ctype = (ctype_element.text or "").strip() if ctype_element is not None else (next(iter(local_types)) if len(local_types) == 1 else "UNKNOWN")
        if len(modules) == 1:
            process = module_process(modules[0])
        elif len(modules) > 1:
            process = "shared chemistry / ambiguous subsystem attribution"
        else:
            process = "unmapped original reaction"
        family = f"{process} / {ctype}"
        delta = {currency: net_value(reactants, products, currency) for currency in CURRENCIES}
        particle_delta = sum(products.values()) - sum(reactants.values())
        small_delta = sum(value for sid, value in products.items() if sid in FREE_SMALL) - sum(value for sid, value in reactants.items() if sid in FREE_SMALL)
        official_k = parameters.get(rid + "_k1")
        if official_k is None:
            raise ValueError(f"Missing official reaction parameter {rid}_k1")
        touches_resource = any(delta[c] for c in ("ATP", "ADP", "AMP", "GTP", "GDP", "GMP", "PO4", "PPi", "CP", "Cr", "Gly", "Met", "fMet"))
        touches_peptide = any("Pept" in x or x in {"fMet", "Gly"} for x in participants)
        degraded = any(x.endswith("_degraded") for x in participants)
        if official_k == 0 and degraded:
            label = "DROP_CANDIDATE"
            reason = "Official fMGG parameter CSV sets this degradation step to zero for the reference condition; applicability outside that condition is unresolved."
        elif touches_resource or (touches_peptide and "Elongation" in ";".join(modules)):
            label = "KEEP"
            reason = "Explicit resource or peptide-state accounting is directly relevant to the revised scope."
        elif ctype in {"HETERODIMER_ASSOCIATION", "DISSOCIATION", "STATE_TRANSITION"} and not degraded:
            label = "LUMP_CANDIDATE"
            reason = "May be representable by an effective transition if occupancy, bound resources, and timescales are preserved or separately reconstructed."
        else:
            label = "UNKNOWN"
            reason = "Insufficient chemical or timescale evidence for a responsible transformation proposal."
        is_nonkeep = label != "KEEP"
        affected = ", ".join(currency for currency, value in delta.items() if value)
        lost = "individual intermediate and machinery occupancy trajectories; microscopic forward/reverse fluxes" if label == "LUMP_CANDIDATE" else ("degradation-state trajectory and any nonreference-condition loss" if label == "DROP_CANDIDATE" else "not yet determined")
        assumption = ("effective rate law and reconstruction must reproduce resource/moiety balances and occupancy over the stated domain" if label == "LUMP_CANDIDATE" else "the original zero rate and its condition/domain remain fixed" if label == "DROP_CANDIDATE" else "none accepted")
        evidence = "none measured here; official single reaction k1 is not a timescale separation certificate"
        common = {
            "sbml_reaction_id": rid,
            "reaction_family": family,
            "level_a_module_candidates": ";".join(levels),
            "level_b_subsystem_candidates": ";".join(modules),
            "module_local_reaction_ids": ";".join(f"{m['module']}:{m['local_id']}" for m in matches),
            "module_mapping_status": match_status,
            "cell_designer_reaction_type": ctype,
            "reactants_json": json.dumps(reactants, sort_keys=True),
            "products_json": json.dumps(products, sort_keys=True),
            "official_parameter_id": rid + "_k1",
            "official_parameter_value": official_k,
        }
        balance_rows.append({
            **common,
            "net_tracked_particle_count_per_event": particle_delta,
            "net_explicit_free_small_solute_count_per_event": small_delta,
            **{f"net_free_{currency}": value for currency, value in delta.items()},
            "elemental_balance_status": "UNRESOLVED_FORMULAS_ABSENT",
            "moiety_balance_status": "UNRESOLVED_BOUND_MOIETIES_NOT_ANNOTATED",
            "osmotic_proxy_status": "STOICHIOMETRIC_PROXY_ONLY_NOT_VALIDATED_OSMOTIC_PRESSURE",
            "ionic_strength_status": "UNAVAILABLE_CHARGE_PROTONATION_MG_BINDING_ABSENT",
            "source_sbml_sha256": source_hashes[MODEL.relative_to(ROOT).as_posix()],
        })
        decision_rows.append({
            **common,
            "candidate_label": label,
            "biochemical_role": process,
            "reason_candidate": reason,
            "required_assumption": assumption,
            "timescale_evidence": evidence,
            "conservation_moiety_consequence": "Bound-carrier and enzyme/moiety conservation must be rederived; no atomic formula audit is available." if is_nonkeep else "explicit representation retained as candidate",
            "ATP_GTP_accounting_consequence": f"net free ATP={delta['ATP']}; ADP={delta['ADP']}; AMP={delta['AMP']}; GTP={delta['GTP']}; GDP={delta['GDP']}; complex-bound moieties unresolved",
            "PPi_Pi_consequence": f"net free PPi={delta['PPi']}; PO4={delta['PO4']}; bound phosphate unresolved",
            "tRNA_accounting_consequence": "; ".join(f"{s}={delta[s]}" for s in ("tRNAGlyGCC", "tRNAfMetCAU", "GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU")) + "; bound tRNA unresolved",
            "osmolarity_consequence": f"tracked-species particle delta={particle_delta:g} per event; free-small-solute delta={small_delta:g}; ideal proxy only",
            "ionic_strength_consequence": "UNKNOWN; no charge/protonation/Mg convention in SBML",
            "observables_unrecoverable_if_applied": lost,
            "data_needed_to_validate": "authoritative complex composition; concentration time courses; timescale/flux comparisons; conservation reconstruction; charge/protonation/Mg convention" if is_nonkeep else "reference reproduction and balances",
            "HUMAN_REVIEW_REQUIRED": True,
            "decision_status": "PENDING",
        })

    species_rows = []
    for item in species:
        sid = item.attrib["id"]
        kind, basis = species_class(sid)
        modules = sorted(species_to_modules[sid])
        flags = resource_flags(sid)
        species_rows.append({
            "sbml_id": sid,
            "sbml_name": item.get("name", ""),
            "compartment_id": item.get("compartment", ""),
            "sbml_initial_concentration": item.get("initialConcentration", ""),
            "reference_initial_concentration": initial[sid],
            "reference_initial_unit_status": "uM inferred from paper concentration examples; CSV omits unit metadata",
            "initial_source": "Simulate_fMGG_synthesis.zip:dat/fMGG_synthesis_initial_values.csv",
            "boundary_condition": item.get("boundaryCondition", "false"),
            "constant": item.get("constant", "false"),
            "dynamic_status": "dynamic" if item.get("boundaryCondition", "false") == "false" and item.get("constant", "false") == "false" else "boundary/constant",
            "level_a_module_candidates": ";".join(sorted({module_level(m) for m in modules})),
            "level_b_subsystem_candidates": ";".join(modules),
            "molecule_class": kind,
            "classification_basis": basis,
            "small_molecule": kind == "small molecule",
            "macromolecule": kind in {"RNA", "ribosomal species", "protein/enzyme"},
            "complex": kind == "complex",
            **flags,
            "formula": "",
            "net_charge": "",
            "charge_protonation_convention": "",
            "formula_charge_provenance": "UNRESOLVED",
            "HUMAN_REVIEW_REQUIRED": True,
        })

    write_csv(OUT / "species_properties.csv", species_rows)
    write_csv(OUT / "reaction_balance_audit.csv", balance_rows)
    write_csv(RED / "reduction_decisions.csv", decision_rows)
    output_hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in (OUT / "species_properties.csv", OUT / "reaction_balance_audit.csv", RED / "reduction_decisions.csv")}
    manifest = {
        "generated_by": "scripts/build_pnas2017_resource_map.py",
        "doi": DOI,
        "status": "DERIVED_NAVIGATION_NOT_SOURCE_AUTHORITY",
        "input_sha256": source_hashes,
        "output_sha256": output_hashes,
        "counts": {"species": len(species_rows), "reactions": len(balance_rows), "positive_reference_initial_components": sum(v > 0 for v in initial.values()), "module_mapping_status": dict(mapping_counts), "candidate_labels": dict(Counter(r["candidate_label"] for r in decision_rows))},
        "freshness_rule": "Regenerate if any input SHA-256 differs. Do not hand-edit derived CSVs.",
    }
    (OUT / "resource_map_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest["counts"], indent=2))


if __name__ == "__main__":
    main()

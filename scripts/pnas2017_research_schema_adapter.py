#!/usr/bin/env python3
"""Build branch-compatible *temporary* tables from main's PNAS audit.

The output is a compatibility input for historical analysis, never a replacement
for main's libSBML audit or the original SBML. No scientific annotations are
inferred here: IDs, effective stoichiometry, rate formulas, source-file links,
and author CSV values are copied from the identified sources.
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "models/pnas2017_full_reference/audit"
AUTHOR_ZIP = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
SBML = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def author_rows(archive, suffix):
    name = next(name for name in archive.namelist() if name.endswith(suffix))
    return list(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8-sig"))))


def number(value):
    value = str(value)
    try:
        scalar = float(value)
        return str(int(scalar)) if scalar.is_integer() else value
    except ValueError:
        return value


def side(encoded):
    return "|".join(
        f"{part['species_id']}:{number(part['stoichiometry'])}"
        for part in json.loads(encoded)
    )


def write_csv(path, fieldnames, data):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def build(output_dir):
    output_dir = Path(output_dir).resolve()
    if output_dir == AUDIT.resolve() or AUDIT.resolve() in output_dir.parents:
        raise ValueError("adapter output must not overwrite or sit inside main's audit")
    output_dir.mkdir(parents=True, exist_ok=True)

    source_files = [AUDIT / f"{name}.csv" for name in ("species", "reactions", "parameters")]
    main_species, main_reactions, main_parameters = map(rows, source_files)
    assert (len(main_species), len(main_reactions), len(main_parameters)) == (241, 968, 968)
    with zipfile.ZipFile(AUTHOR_ZIP) as archive:
        initials = author_rows(archive, "fMGG_synthesis_initial_values.csv")
        parameters = author_rows(archive, "fMGG_synthesis_parameters.csv")
    initial_by_id = {row["Name"]: row["Value"] for row in initials}
    parameter_by_name = {row["Name"]: row["Value"] for row in parameters}
    assert len(initial_by_id) == 241
    assert all(f"{r['owner_reaction_id']}_{r['parameter_id']}" in parameter_by_name
               for r in main_parameters)

    sbml_model = ET.parse(SBML).getroot().find("{http://www.sbml.org/sbml/level2/version4}model")
    assert sbml_model is not None
    model_id = sbml_model.attrib["id"]
    metaids = {reaction.attrib["id"]: reaction.attrib.get("metaid", "") for reaction in
               sbml_model.findall(".//{http://www.sbml.org/sbml/level2/version4}reaction")}

    species_fields = ["id", "name", "compartment", "sbml_initial_concentration",
                      "sbml_initial_amount", "boundary_condition", "constant",
                      "has_annotations", "author_export_initial_value"]
    species = [{"id": row["species_id"], "name": row["original_name"],
                "compartment": row["compartment_id"],
                "sbml_initial_concentration": number(row["initial_concentration"]),
                "sbml_initial_amount": row["initial_amount"],
                "boundary_condition": row["boundary_condition"],
                "constant": row["constant"], "has_annotations": "false",
                "author_export_initial_value": initial_by_id[row["species_id"]]}
               for row in main_species]
    write_csv(output_dir / "species.csv", species_fields, species)

    reaction_fields = ["id", "name", "reversible", "fast", "subsystem_files",
                       "n_reactants", "n_products", "reactants", "products",
                       "n_kinetic_params", "kinetic_param_ids", "rate_law", "metaid"]
    reactions = []
    for row in main_reactions:
        refs = json.loads(row["source_module_reaction_refs_json"])
        filenames = sorted({Path(ref["source_file"]).stem for ref in refs})
        reactants = json.loads(row["reactants_json"])
        products = json.loads(row["products_json"])
        reactions.append({"id": row["reaction_id"], "name": row["original_name"],
                          "reversible": row["reversible"], "fast": "false",
                          "subsystem_files": "|".join(filenames),
                          "n_reactants": len(reactants), "n_products": len(products),
                          "reactants": side(row["reactants_json"]),
                          "products": side(row["products_json"]),
                          "n_kinetic_params": len(row["local_parameter_ids"].split("|")),
                          "kinetic_param_ids": row["local_parameter_ids"],
                          "rate_law": row["kinetic_law_formula"],
                          "metaid": metaids[row["reaction_id"]]})
    assert all(row["subsystem_files"] for row in reactions), "main audit source mapping incomplete"
    write_csv(output_dir / "reactions.csv", reaction_fields, reactions)

    parameter_fields = ["reaction_id", "parameter_id", "parameter_name", "sbml_value",
                        "sbml_units", "sbml_constant", "author_export_value",
                        "value_is_placeholder"]
    adapted_parameters = [{"reaction_id": row["owner_reaction_id"],
                           "parameter_id": row["parameter_id"],
                           "parameter_name": row["original_name"],
                           "sbml_value": number(row["value"]),
                           "sbml_units": row["units_declared"],
                           "sbml_constant": row["constant"],
                           "author_export_value": parameter_by_name[
                               f"{row['owner_reaction_id']}_{row['parameter_id']}"],
                           "value_is_placeholder": "true" if number(row["value"]) !=
                           number(parameter_by_name[
                               f"{row['owner_reaction_id']}_{row['parameter_id']}"])
                           else "false"}
                          for row in main_parameters]
    write_csv(output_dir / "parameters.csv", parameter_fields, adapted_parameters)

    summary = {"source_file": str(SBML.relative_to(ROOT)).replace("\\", "/"),
               "model_id": model_id, "species_count": len(species),
               "reaction_count": len(reactions),
               "adapter_status": "MAIN_DERIVED_COMPATIBILITY_INPUT_NOT_SOURCE_AUTHORITY"}
    (output_dir / "inventory_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    by_id = {row["id"]: row for row in reactions}
    assert by_id["re0000000414"]["products"].split("|").count("PO4:2") == 1
    manifest = {"schema": "pnas2017_research_schema_adapter/v1",
                "status": "GENERATED_EVIDENCE_NOT_CANONICAL_AUDIT",
                "source_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): digest(path)
                                  for path in [SBML, AUTHOR_ZIP] + source_files},
                "output_sha256": {name: digest(output_dir / name) for name in
                                  ("species.csv", "reactions.csv", "parameters.csv",
                                   "inventory_summary.json")},
                "counts": {"species": len(species), "reactions": len(reactions),
                           "parameters": len(adapted_parameters),
                           "mapped_reactions": sum(bool(r["subsystem_files"]) for r in reactions)}}
    (output_dir / "adapter_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.output_dir)["counts"], sort_keys=True))

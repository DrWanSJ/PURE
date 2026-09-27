"""Run the author fMGG inputs with a provenance-checked SBML compatibility copy.

The original SBML and author ZIP are immutable inputs. All changes to species
initial concentrations and local k1 values occur only in an in-memory SBML
document. A separate, byte-tracked compatibility SBML replaces *literal*
stoichiometryMath constants by the identical numeric stoichiometry attribute,
because the tested SBML engines otherwise read re0000000414 -> PO4 as 1
instead of the source value 2. This is an import workaround, not a reduction.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import sys
import traceback
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_XML = ROOT / "references/PNAS2017_Matsuura/raw/fMGG_synthesis.xml"
MODEL_XML = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
AUTHOR_ZIP = ROOT / "references/PNAS2017_Matsuura/raw/Simulate_fMGG_synthesis.zip"
SOURCE_REGISTER = ROOT / "references/PNAS2017_Matsuura/provenance/sources.json"
NORMALIZED_DIR = ROOT / "models/pnas2017_full_reference/normalized"
NORMALIZED_XML = NORMALIZED_DIR / "fMGG_synthesis_constant_stoichiometry.xml"
NORMALIZED_MANIFEST = NORMALIZED_DIR / "fMGG_synthesis_constant_stoichiometry.provenance.json"
ZIP_PREFIX = "Simulate_fMGG_synthesis/"
INITIAL_MEMBER = ZIP_PREFIX + "dat/fMGG_synthesis_initial_values.csv"
PARAMETER_MEMBER = ZIP_PREFIX + "dat/fMGG_synthesis_parameters.csv"
SAMPLE_MEMBER = ZIP_PREFIX + "fMGG_synthesis_Sample.m"
PRODUCT_ID = "Pept0003"
GRID_START = 1e-4
GRID_END = 1e3
GRID_POINTS = 200


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse_csv(data: bytes) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def scalar(value: str, description: str) -> float:
    number = float(value)
    if not math.isfinite(number) or number < 0:
        raise ValueError(f"{description}: expected finite nonnegative value, got {value!r}")
    return number


def check_source_bytes() -> tuple[bytes, dict[str, str]]:
    register = json.loads(SOURCE_REGISTER.read_text(encoding="utf-8"))
    expected = {row["path"]: row["sha256"] for row in register["source_files"]}
    byte_hashes: dict[str, str] = {}
    for path in (SOURCE_XML, MODEL_XML, AUTHOR_ZIP):
        raw = path.read_bytes()
        digest = sha256(raw)
        byte_hashes[relative(path)] = digest
        if path != MODEL_XML and expected[relative(path)] != digest:
            raise ValueError(f"source hash mismatch: {relative(path)}")
    if byte_hashes[relative(SOURCE_XML)] != byte_hashes[relative(MODEL_XML)]:
        raise ValueError("model/original SBML is not a byte-identical source copy")
    return MODEL_XML.read_bytes(), byte_hashes


def read_sbml(data: bytes):
    import libsbml

    document = libsbml.readSBMLFromString(data.decode("utf-8"))
    model = document.getModel()
    if model is None:
        raise ValueError("SBML document has no model")
    if (document.getLevel(), document.getVersion()) != (2, 4):
        raise ValueError("unexpected SBML level/version")
    if (model.getNumSpecies(), model.getNumReactions()) != (241, 968):
        raise ValueError("unexpected source species/reaction count")
    return document, model


def literal_stoichiometry(species_reference) -> float:
    import libsbml

    if not species_reference.isSetStoichiometryMath():
        return float(species_reference.getStoichiometry())
    node = species_reference.getStoichiometryMath().getMath()
    if node is None or node.getNumChildren():
        raise ValueError("nonliteral stoichiometryMath cannot be normalized")
    if node.getType() == libsbml.AST_INTEGER:
        value = float(node.getInteger())
    elif node.getType() == libsbml.AST_REAL:
        value = float(node.getReal())
    elif node.getType() == libsbml.AST_RATIONAL:
        value = node.getNumerator() / node.getDenominator()
    else:
        raise ValueError(f"unsupported stoichiometryMath AST type {node.getType()}")
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"invalid stoichiometryMath literal {value}")
    return value


def stoichiometry_inventory(model) -> list[tuple[str, str, int, str, float]]:
    rows = []
    for reaction in model.getListOfReactions():
        for role, members in (
            ("reactant", reaction.getListOfReactants()),
            ("product", reaction.getListOfProducts()),
        ):
            for index, species_reference in enumerate(members):
                rows.append(
                    (
                        reaction.getId(),
                        role,
                        index,
                        species_reference.getSpecies(),
                        literal_stoichiometry(species_reference),
                    )
                )
    return rows


def normalize_stoichiometry(document, model) -> tuple[bytes, dict]:
    import libsbml

    before = stoichiometry_inventory(model)
    converted = 0
    nonunit = []
    for reaction in model.getListOfReactions():
        for role, members in (
            ("reactant", reaction.getListOfReactants()),
            ("product", reaction.getListOfProducts()),
        ):
            for species_reference in members:
                if not species_reference.isSetStoichiometryMath():
                    continue
                value = literal_stoichiometry(species_reference)
                if value != 1:
                    nonunit.append(
                        {
                            "reaction_id": reaction.getId(),
                            "role": role,
                            "species_id": species_reference.getSpecies(),
                            "source_math_literal": value,
                        }
                    )
                if species_reference.unsetStoichiometryMath() != libsbml.LIBSBML_OPERATION_SUCCESS:
                    raise RuntimeError("could not remove literal stoichiometryMath")
                if species_reference.setStoichiometry(value) != libsbml.LIBSBML_OPERATION_SUCCESS:
                    raise RuntimeError("could not set equivalent numeric stoichiometry")
                converted += 1
    output = libsbml.writeSBMLToString(document).encode("utf-8")
    _, reloaded = read_sbml(output)
    after = stoichiometry_inventory(reloaded)
    if before != after:
        raise AssertionError("normalized stoichiometric inventory differs from the source")
    if any(
        member.isSetStoichiometryMath()
        for reaction in reloaded.getListOfReactions()
        for member in list(reaction.getListOfReactants()) + list(reaction.getListOfProducts())
    ):
        raise AssertionError("normalization left stoichiometryMath elements")
    if converted != 3854 or len(before) != 3854:
        raise ValueError(f"unexpected species-reference count: {converted}/{len(before)}")
    if nonunit != [
        {
            "reaction_id": "re0000000414",
            "role": "product",
            "species_id": "PO4",
            "source_math_literal": 2.0,
        }
    ]:
        raise ValueError(f"unexpected nonunit source coefficients: {nonunit!r}")
    report = {
        "transformation": "Every literal stoichiometryMath constant replaced by the identical numeric stoichiometry attribute; no reaction or species deleted.",
        "source_species_reference_count": len(before),
        "converted_literal_count": converted,
        "nonunit_literals": nonunit,
        "stoichiometric_inventory_equal_after_roundtrip": True,
    }
    return output, report


def load_author_inputs(model, archive: zipfile.ZipFile) -> tuple[dict[str, float], dict[str, float], dict]:
    species_rows = parse_csv(archive.read(INITIAL_MEMBER))
    parameter_rows = parse_csv(archive.read(PARAMETER_MEMBER))
    species_ids = [species.getId() for species in model.getListOfSpecies()]
    if len(species_rows) != len(species_ids):
        raise ValueError("author initial CSV has wrong number of rows")
    initial_values: dict[str, float] = {}
    for index, (row, species_id) in enumerate(zip(species_rows, species_ids), start=1):
        if int(row["No."]) != index or row["Name"] != species_id:
            raise ValueError(f"author initial CSV differs from SBML at row {index}")
        initial_values[species_id] = scalar(row["Value"], species_id)
    reaction_ids = [reaction.getId() for reaction in model.getListOfReactions()]
    if len(parameter_rows) != len(reaction_ids) + 1:
        raise ValueError("author parameter CSV has wrong number of rows")
    parameters: dict[str, float] = {}
    for row, reaction_id in zip(parameter_rows[:-1], reaction_ids):
        expected = f"{reaction_id}_k1"
        if row["Name"] != expected:
            raise ValueError(f"author parameter CSV differs from SBML at {reaction_id}")
        local = model.getReaction(reaction_id).getKineticLaw().getParameter("k1")
        if local is None:
            raise ValueError(f"SBML reaction {reaction_id} has no local k1")
        parameters[reaction_id] = scalar(row["Value"], expected)
    if parameter_rows[-1]["Name"] != "default" or float(parameter_rows[-1]["Value"]) != 1:
        raise ValueError("unexpected extra author parameter CSV row")
    if PRODUCT_ID not in initial_values:
        raise ValueError(f"expected terminal product species {PRODUCT_ID} is absent")
    summary = {
        "species_count": len(initial_values),
        "positive_initial_species_count": sum(value > 0 for value in initial_values.values()),
        "reaction_local_k1_count": len(parameters),
        "nonzero_k1_count": sum(value > 0 for value in parameters.values()),
        "ignored_author_csv_sentinel": {"Name": "default", "Value": 1},
        "mapping": "Initial CSV No./Name equals original SBML species order/ID; parameter CSV reaction_id_k1 equals original reaction order and local kinetic-law k1.",
    }
    return initial_values, parameters, summary


def apply_author_inputs(model, initials: dict[str, float], parameters: dict[str, float]) -> None:
    import libsbml

    for species_id, value in initials.items():
        if model.getSpecies(species_id).setInitialConcentration(value) != libsbml.LIBSBML_OPERATION_SUCCESS:
            raise RuntimeError(f"could not set initial concentration {species_id}")
    for reaction_id, value in parameters.items():
        local = model.getReaction(reaction_id).getKineticLaw().getParameter("k1")
        if local.setValue(value) != libsbml.LIBSBML_OPERATION_SUCCESS:
            raise RuntimeError(f"could not set local k1 {reaction_id}")


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(run_id: str, prepare_only: bool) -> dict:
    import libsbml

    source_data, file_hashes = check_source_bytes()
    source_doc, source_model = read_sbml(source_data)
    normalized_data, normalization = normalize_stoichiometry(source_doc, source_model)
    NORMALIZED_DIR.mkdir(parents=True, exist_ok=True)
    if NORMALIZED_XML.exists() and NORMALIZED_XML.read_bytes() != normalized_data:
        raise ValueError("existing normalized SBML differs from deterministic regeneration")
    NORMALIZED_XML.write_bytes(normalized_data)
    normalized_hash = sha256(normalized_data)
    normalization_manifest = {
        "canonical_source_path": relative(MODEL_XML),
        "canonical_source_sha256": file_hashes[relative(MODEL_XML)],
        "normalized_path": relative(NORMALIZED_XML),
        "normalized_sha256": normalized_hash,
        "generator_path": relative(Path(__file__).resolve()),
        "libsbml_version": libsbml.getLibSBMLDottedVersion(),
        "status": "derived_compatibility_copy_not_scientific_authority",
        **normalization,
    }
    save_json(NORMALIZED_MANIFEST, normalization_manifest)

    with zipfile.ZipFile(AUTHOR_ZIP) as archive:
        members = {
            member: sha256(archive.read(member))
            for member in (INITIAL_MEMBER, PARAMETER_MEMBER, SAMPLE_MEMBER)
        }
        normalized_doc, normalized_model = read_sbml(normalized_data)
        initials, parameters, input_summary = load_author_inputs(normalized_model, archive)
    apply_author_inputs(normalized_model, initials, parameters)
    overlay_sbml = libsbml.writeSBMLToString(normalized_doc)
    effective_doc, effective_model = read_sbml(overlay_sbml.encode("utf-8"))
    if any(
        effective_model.getSpecies(species_id).getInitialConcentration() != value
        for species_id, value in initials.items()
    ) or any(
        effective_model.getReaction(reaction_id).getKineticLaw().getParameter("k1").getValue() != value
        for reaction_id, value in parameters.items()
    ):
        raise AssertionError("author CSV overlay did not survive SBML roundtrip")

    result_dir = ROOT / "results/pnas2017_reference" / run_id
    result_dir.mkdir(parents=True, exist_ok=True)
    effective_path = result_dir / "effective_author_conditions.xml"
    effective_bytes = overlay_sbml.encode("utf-8")
    if effective_path.exists() and effective_path.read_bytes() != effective_bytes:
        raise ValueError("existing author-condition SBML differs from deterministic regeneration")
    effective_path.write_bytes(effective_bytes)
    summary = {
        "benchmark": "PNAS2017_full_reference",
        "scientific_status": "reference_integrity_diagnostic_not_experimental_validation",
        "execution_status": "prepared",
        "source_sha256": file_hashes,
        "author_zip_members_sha256": members,
        "normalization_manifest": relative(NORMALIZED_MANIFEST),
        "normalized_sbml_sha256": normalized_hash,
        "effective_author_conditions_sbml": {
            "path": relative(effective_path),
            "sha256": sha256(effective_bytes),
            "status": "derived_numeric_execution_input_not_canonical_source",
        },
        "author_csv_overlay": input_summary,
        "time_grid": {
            "definition": "logspace(-4, 3, 200) from author fMGG_synthesis_Sample.m",
            "start_seconds": GRID_START,
            "end_seconds": GRID_END,
            "points": GRID_POINTS,
        },
        "solver": {
            "name": "libRoadRunner CVODE",
            "relative_tolerance": 1e-3,
            "absolute_tolerance": 1e-9,
            "stiff": True,
            "author_solver": "MATLAB ode15s with NonNegative; CVODE does not assert identical nonnegative handling",
        },
        "observed_product_sbml_id": PRODUCT_ID,
        "dataset_s28_comparison": "unavailable_original_publisher_dataset_not_acquired",
    }
    report_path = result_dir / "run_manifest.json"
    save_json(report_path, summary)
    if prepare_only:
        summary["execution_status"] = "prepared_only"
        save_json(report_path, summary)
        return summary

    import roadrunner

    summary["solver"]["roadrunner_version"] = roadrunner.__version__
    try:
        runner = roadrunner.RoadRunner(overlay_sbml)
        runner.setIntegrator("cvode")
        integrator = runner.getIntegrator()
        integrator.setValue("relative_tolerance", 1e-3)
        integrator.setValue("absolute_tolerance", 1e-9)
        integrator.setValue("stiff", True)
        summary["solver"]["maximum_num_steps"] = integrator.getValue("maximum_num_steps")
        species_ids = [species.getId() for species in effective_model.getListOfSpecies()]
        grid = [10 ** (-4 + 7 * index / (GRID_POINTS - 1)) for index in range(GRID_POINTS)]
        selections = ["time"] + [f"[{species_id}]" for species_id in species_ids]
        result = runner.simulate(times=grid, selections=selections)
        if len(result) != GRID_POINTS:
            raise RuntimeError(f"RoadRunner returned {len(result)} rows, expected {GRID_POINTS}")
        rows = [[float(value) for value in row] for row in result]
        if any(not math.isfinite(value) for row in rows for value in row):
            raise RuntimeError("simulation produced nonfinite values")
        product_index = species_ids.index(PRODUCT_ID) + 1
        trajectory_path = result_dir / "trajectory.csv"
        with trajectory_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["time_seconds"] + species_ids)
            writer.writerows(rows)
        summary["execution_status"] = "completed"
        summary["trajectory"] = {
            "path": relative(trajectory_path),
            "sha256": sha256(trajectory_path.read_bytes()),
            "rows": len(rows),
            "species_columns": len(species_ids),
            "minimum_species_concentration": min(min(row[1:]) for row in rows),
            "product_initial": rows[0][product_index],
            "product_final": rows[-1][product_index],
            "product_maximum": max(row[product_index] for row in rows),
        }
    except Exception as exc:
        summary["execution_status"] = "failed"
        summary["error_type"] = type(exc).__name__
        summary["error"] = str(exc)
        (result_dir / "error_traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
    save_json(report_path, summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="rr_cvode_author_csv_20260924")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    if not args.run_id or any(char not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for char in args.run_id):
        parser.error("run ID may contain only ASCII letters, digits, underscore and hyphen")
    try:
        summary = run(args.run_id, args.prepare_only)
    except Exception:
        traceback.print_exc()
        return 2
    print(json.dumps({"execution_status": summary["execution_status"], "run_id": args.run_id, "product_id": PRODUCT_ID}, indent=2))
    return 0 if summary["execution_status"] in ("completed", "prepared_only") else 1


if __name__ == "__main__":
    sys.exit(main())

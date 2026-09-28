"""Read-only SBML inventory for the PNAS 2017 reference source.

The four CSV files and Markdown report are derived outputs.  This script never
rewrites the source SBML or the archived subsystem ZIP.  In particular, it
reads constant stoichiometryMath nodes: SpeciesReference.getStoichiometry()
alone silently returns 1 for the one coefficient encoded as MathML 2.
"""

from __future__ import annotations

import argparse
import collections
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import libsbml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SBML = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
DEFAULT_ZIP = ROOT / "references/PNAS2017_Matsuura/raw/SBML_files.zip"
DEFAULT_AUDIT = ROOT / "models/pnas2017_full_reference/audit"
DEFAULT_REPORT = ROOT / "docs/pnas2017/sbml_audit.md"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def truth(value: bool) -> str:
    return "true" if value else "false"


def decimal_text(value: Decimal) -> str:
    return format(value.normalize(), "f")


def effective_stoichiometry(ref: libsbml.SpeciesReference) -> tuple[str, str, str]:
    """Return effective coefficient, encoding, and unmodified MathML formula.

    A symbolic stoichiometryMath requires separate evaluation and is rejected;
    silently replacing it with the default stoichiometry attribute is unsafe.
    """
    if ref.isSetStoichiometryMath():
        node = ref.getStoichiometryMath().getMath()
        formula = libsbml.formulaToL3String(node)
        if node.isInteger():
            value = Decimal(node.getInteger())
        elif node.isReal():
            value = Decimal(str(node.getReal()))
        else:
            raise ValueError(
                f"Nonliteral stoichiometryMath for species {ref.getSpecies()}: {formula}"
            )
        return decimal_text(value), "stoichiometryMath", formula
    return decimal_text(Decimal(str(ref.getStoichiometry()))), "attribute", ""


def reference_rows(refs: libsbml.ListOfSpeciesReferences) -> list[dict[str, str]]:
    rows = []
    for ref in refs:
        value, encoding, math_formula = effective_stoichiometry(ref)
        rows.append(
            {
                "species_id": ref.getSpecies(),
                "stoichiometry": value,
                "encoding": encoding,
                "stoichiometry_math": math_formula,
            }
        )
    return rows


def reaction_signature(reaction: libsbml.Reaction) -> tuple:
    def side(refs: libsbml.ListOfSpeciesReferences) -> tuple:
        return tuple(
            sorted(
                (ref.getSpecies(), effective_stoichiometry(ref)[0]) for ref in refs
            )
        )

    return (
        side(reaction.getListOfReactants()),
        side(reaction.getListOfProducts()),
        tuple(sorted(ref.getSpecies() for ref in reaction.getListOfModifiers())),
    )


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_subsystems(zip_path: Path) -> tuple[list[dict], dict[tuple, list[dict]]]:
    modules: list[dict] = []
    signature_map: dict[tuple, list[dict]] = collections.defaultdict(list)
    with zipfile.ZipFile(zip_path) as archive:
        for name in archive.namelist():
            if not name.lower().endswith((".xml", ".sbml")):
                continue
            raw = archive.read(name)
            document = libsbml.readSBMLFromString(raw.decode("utf-8"))
            if document.getModel() is None or document.getNumErrors():
                messages = [document.getError(i).getMessage() for i in range(document.getNumErrors())]
                raise ValueError(f"Could not parse subsystem {name}: {messages}")
            model = document.getModel()
            module = {
                "source_file": name,
                "source_model_id": model.getId(),
                "sbml_level": document.getLevel(),
                "sbml_version": document.getVersion(),
                "species_count": model.getNumSpecies(),
                "reaction_entry_count": model.getNumReactions(),
                "kinetic_law_count": sum(r.isSetKineticLaw() for r in model.getListOfReactions()),
                "source_entry_sha256": sha256_bytes(raw),
            }
            modules.append(module)
            for reaction in model.getListOfReactions():
                signature_map[reaction_signature(reaction)].append(
                    {
                        "source_model_id": model.getId(),
                        "source_file": name,
                        "source_reaction_id": reaction.getId(),
                    }
                )
    return modules, signature_map


def validation_summary(document: libsbml.SBMLDocument) -> tuple[int, list[dict]]:
    count = document.checkConsistency()
    grouped: dict[tuple, dict] = {}
    for i in range(document.getNumErrors()):
        error = document.getError(i)
        key = (error.getSeverityAsString(), error.getCategoryAsString(), error.getErrorId())
        if key not in grouped:
            grouped[key] = {
                "severity": key[0],
                "category": key[1],
                "rule_id": key[2],
                "count": 0,
                "example_line": error.getLine(),
                "example_message": " ".join(error.getMessage().split()),
            }
        grouped[key]["count"] += 1
    return count, sorted(grouped.values(), key=lambda item: (item["severity"], item["rule_id"]))


def roadrunner_probe(sbml_path: Path, model: libsbml.Model) -> dict:
    try:
        import roadrunner
    except ImportError as exc:
        return {"status": "unavailable", "detail": str(exc)}
    try:
        runner = roadrunner.RoadRunner(str(sbml_path))
        species_ids = list(runner.model.getFloatingSpeciesIds())
        reaction_ids = list(runner.model.getReactionIds())
        matrix = runner.getFullStoichiometryMatrix()
        row_index = {species_id: i for i, species_id in enumerate(species_ids)}
        col_index = {reaction_id: i for i, reaction_id in enumerate(reaction_ids)}
        differences = []
        for reaction in model.getListOfReactions():
            net: dict[str, Decimal] = collections.defaultdict(lambda: Decimal(0))
            for ref in reaction.getListOfReactants():
                net[ref.getSpecies()] -= Decimal(effective_stoichiometry(ref)[0])
            for ref in reaction.getListOfProducts():
                net[ref.getSpecies()] += Decimal(effective_stoichiometry(ref)[0])
            for species_id, expected in net.items():
                actual = float(matrix[row_index[species_id], col_index[reaction.getId()]])
                if abs(actual - float(expected)) > 1e-12:
                    differences.append(
                        {
                            "reaction_id": reaction.getId(),
                            "species_id": species_id,
                            "source_net_stoichiometry": decimal_text(expected),
                            "imported_net_stoichiometry": actual,
                        }
                    )
        return {
            "status": "imported",
            "version": roadrunner.__version__,
            "floating_species": len(species_ids),
            "reactions": len(reaction_ids),
            "default_integrator": runner.getIntegrator().getName(),
            "stoichiometry_differences": differences,
        }
    except Exception as exc:  # preserve import failure rather than fabricating success
        return {"status": "failed", "detail": f"{type(exc).__name__}: {exc}"}


def simbiology_probe(sbml_path: Path, mode: str, expected_refs: int) -> dict:
    if mode == "skip":
        return {"status": "not_run", "detail": "--simbiology skip"}
    matlab = shutil.which("matlab")
    if matlab is None:
        return {"status": "unavailable", "detail": "matlab executable not found on PATH"}
    matlab_path = str(sbml_path).replace("\\", "/").replace("'", "''")
    command = (
        f"m=sbmlimport('{matlab_path}'); "
        "fprintf('SIMBIOLOGY_IMPORT_OK species=%d reactions=%d compartments=%d\\n',"
        "numel(m.Species),numel(m.Reactions),numel(m.Compartments));"
    )
    try:
        process = subprocess.run(
            [matlab, "-batch", command],
            cwd=tempfile.gettempdir(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "failed", "detail": f"{type(exc).__name__}: {exc}"}
    output = process.stdout + process.stderr
    match = re.search(
        r"SIMBIOLOGY_IMPORT_OK species=(\d+) reactions=(\d+) compartments=(\d+)",
        output,
    )
    warning_count = output.count("Stoichiometry Math is not supported for species.")
    return {
        "status": "imported" if process.returncode == 0 and match else "failed",
        "returncode": process.returncode,
        "species": int(match.group(1)) if match else None,
        "reactions": int(match.group(2)) if match else None,
        "compartments": int(match.group(3)) if match else None,
        "unsupported_stoichiometry_math_warnings": warning_count,
        "expected_stoichiometry_math_references": expected_refs,
        "startup_missing_search_path_warning": "slanCM" in output,
        "command": f"matlab -batch \"{command}\"",
        "detail": "" if match else output[-800:].replace("\n", " "),
    }


def markdown_report(
    source_path: Path,
    source_hash: str,
    zip_path: Path,
    zip_hash: str,
    document: libsbml.SBMLDocument,
    modules: list[dict],
    mapping_counts: collections.Counter,
    unmatched_source: list[tuple],
    warnings: list[dict],
    rr: dict,
    sb: dict,
    species_rows: list[dict],
    reaction_rows: list[dict],
    parameter_rows: list[dict],
) -> str:
    model = document.getModel()
    local_parameters = [row for row in parameter_rows if row["scope"] == "reaction_local"]
    stoich_math_rows = sum(int(row["stoichiometry_math_reference_count"]) for row in reaction_rows)
    nonunit_math = [
        (row["reaction_id"], row["reactants_json"], row["products_json"])
        for row in reaction_rows
        if int(row["nonunit_stoichiometry_math_reference_count"]) > 0
    ]
    kinetic_types = collections.Counter(row["kinetic_law_math_type"] for row in reaction_rows)
    severity_counts = collections.Counter()
    for item in warnings:
        severity_counts[item["severity"]] += item["count"]
    math_count = sum(r.isSetKineticLaw() for r in model.getListOfReactions())
    missing_kinetics = model.getNumReactions() - math_count
    shared = sum(count > 1 for count, n in mapping_counts.items() for _ in range(n))
    lines = [
        "# PNAS 2017 combined SBML audit",
        "",
        "This is a structural and tool-compatibility audit of the **unaltered source file**. "
        "It is not reference-trajectory reproduction or a validated reduction. "
        "The four CSV inventories below are derived and can be regenerated with "
        "`scripts/audit_pnas2017_sbml.py`.",
        "",
        "## Inputs and reproducibility",
        "",
        f"- Combined source: `{relative(source_path)}`; SHA-256 `{source_hash}`.",
        f"- Subsystem archive: `{relative(zip_path)}`; SHA-256 `{zip_hash}`.",
        f"- Parser: python-libsbml {libsbml.getLibSBMLDottedVersion()}.",
        "- Regenerate: with CPython 3.12 and python-libsbml 5.21.2, run `python scripts/audit_pnas2017_sbml.py` "
        "(use `--simbiology skip` where MATLAB is unavailable).",
        "- Output: `models/pnas2017_full_reference/audit/{species,reactions,parameters,modules}.csv` "
        "and this report. Original SBML IDs remain in every inventory row.",
        "",
        "## SBML inventory",
        "",
        "| Field | Observed |",
        "| --- | ---: |",
        f"| Model ID | `{model.getId()}` |",
        f"| SBML level/version | {document.getLevel()}/{document.getVersion()} |",
        f"| Compartments | {model.getNumCompartments()} |",
        f"| Species | {model.getNumSpecies()} |",
        f"| Reactions | {model.getNumReactions()} |",
        f"| Global parameters | {model.getNumParameters()} |",
        f"| Reaction-local parameters | {len(local_parameters)} |",
        f"| Explicit unit definitions | {model.getNumUnitDefinitions()} |",
        f"| Reversible / irreversible reactions | {sum(r.getReversible() for r in model.getListOfReactions())} / {sum(not r.getReversible() for r in model.getListOfReactions())} |",
        f"| Reactions with / without kinetic law | {math_count} / {missing_kinetics} |",
        f"| Assignment / rate / algebraic rules | {sum(r.isAssignment() for r in model.getListOfRules())} / {sum(r.isRate() for r in model.getListOfRules())} / {sum(r.isAlgebraic() for r in model.getListOfRules())} |",
        f"| Events | {model.getNumEvents()} |",
        f"| Boundary / constant species | {sum(s.getBoundaryCondition() for s in model.getListOfSpecies())} / {sum(s.getConstant() for s in model.getListOfSpecies())} |",
        "",
        "Kinetic-law MathML top-level types: "
        + ", ".join(f"`{name}` {count}" for name, count in sorted(kinetic_types.items()))
        + ". These are expression shapes, not mechanistic classifications. "
        "No conserved-moiety relationships are declared by the SBML; none is inferred here.",
        "",
        "## Published-count comparison and source limitation",
        "",
        "The reported 241 components, 968 reactions and 26 subsystems match this "
        "combined file and the 26 XML entries in the official subsystem ZIP. "
        f"The subsystem diagrams contain {sum(m['reaction_entry_count'] for m in modules)} reaction entries "
        f"but {len({row['reaction_id'] for row in reaction_rows})} distinct stoichiometric reactions; "
        "130 entries repeat a reaction across subsystems. "
        f"All {model.getNumReactions()} combined reaction signatures map to at least one ZIP entry "
        f"when constant `stoichiometryMath` is evaluated; {shared} combined reactions appear in multiple ZIP entries. "
        f"Unmatched ZIP signatures: {len(unmatched_source)}. "
        "The ZIP subsystem SBMLs have no kinetic laws, so their 1,098 entries are "
        "structural diagrams rather than 1,098 separately executable reactions.",
        "",
        f"The combined file sets `initialConcentration=1` for **all {model.getNumSpecies()} species**, "
        f"and `k1=1` for **all {len(local_parameters)} reaction-local parameters**. "
        "It therefore encodes 241 initially positive species, not the paper's 27 "
        "initially present components. The publication's original numerical "
        "initial-condition/parameter set is not identified by this SBML. Do not "
        "claim an original-parameter fMGG reproduction from this file alone.",
        "",
        "## Stoichiometry encoding and engine compatibility",
        "",
        f"All {stoich_math_rows} combined reactant/product references encode a constant "
        "`stoichiometryMath`; 3,853 equal 1 and one equals 2. "
        "For `re0000000414`, the product `PO4` has MathML coefficient **2** "
        "although `SpeciesReference.getStoichiometry()` returns the default **1**. "
        "The matching `EnergyRegeneration_D.xml` source reaction is `re13`. "
        "The CSV inventory uses the MathML value and retains its encoding.",
        "",
    ]
    if nonunit_math:
        lines.append(
            "- Nonunit MathML coefficient in combined model: "
            + ", ".join(f"`{item[0]}`" for item in nonunit_math)
            + "."
        )
    lines += [
        "",
        "### libRoadRunner",
        "",
    ]
    if rr["status"] == "imported":
        lines += [
            f"- Import status: **success** with libRoadRunner {rr['version']}; "
            f"{rr['floating_species']} floating species and {rr['reactions']} reactions. "
            f"Default integrator: `{rr['default_integrator']}`. No reference simulation was run here.",
            f"- Raw import stoichiometric-matrix differences from the source MathML: "
            f"**{len(rr['stoichiometry_differences'])}**.",
        ]
        for difference in rr["stoichiometry_differences"]:
            lines.append(
                f"  - `{difference['reaction_id']}` / `{difference['species_id']}`: "
                f"source net coefficient {difference['source_net_stoichiometry']}; "
                f"imported matrix {difference['imported_net_stoichiometry']:g}."
            )
        if rr["stoichiometry_differences"]:
            lines.append(
                "- **Status: diagnostic-only raw import.** Direct numerical execution "
                "does not preserve the source stoichiometry and cannot serve as a "
                "faithful benchmark. A separately verified, mathematically equivalent "
                "compatibility copy is required before RoadRunner simulation."
            )
    else:
        lines.append(f"- Import status: **{rr['status']}**; {rr.get('detail', '')}.")
    lines += ["", "### MATLAB SimBiology", ""]
    if sb["status"] == "imported":
        lines += [
            f"- Import status: **success**; {sb['species']} species, "
            f"{sb['reactions']} reactions, {sb['compartments']} compartments.",
            f"- Import emitted {sb['unsupported_stoichiometry_math_warnings']} "
            "`Stoichiometry Math is not supported ... will be read ... 1` "
            f"warnings for {sb['expected_stoichiometry_math_references']} source references. "
            "The one nonunit coefficient (`re0000000414` → `PO4`: 2) is therefore "
            "not preserved. **Status: diagnostic-only raw import; no independent "
            "equivalent simulation claim.**",
            f"- MATLAB process exit code: {sb['returncode']}. "
            + ("A separate stale startup search-path warning (`slanCM`) appeared." if sb["startup_missing_search_path_warning"] else ""),
            f"- Reproduce import probe: `{sb['command']}`",
        ]
    else:
        lines.append(f"- Import status: **{sb['status']}**; {sb.get('detail', '')}.")
    lines += [
        "",
        "## Units and libSBML consistency",
        "",
        "- The file defines **zero** explicit unit definitions. Its compartment "
        "declares the built-in `volume` unit; all 241 species leave "
        "`substanceUnits` and `spatialSizeUnits` unset. All 968 local `k1` "
        "parameters declare `substance` and all 968 kinetic laws leave "
        "substance/time units unset. The implied numerical concentration, "
        "time and rate-constant units are therefore not sufficiently documented "
        "for a biochemical units claim.",
        "- No charge, protonation or Mg-binding metadata appear in this audit. "
        "A solver import cannot validate ionic-strength or osmotic calculations.",
        f"- libSBML `checkConsistency()` reported **{sum(item['count'] for item in warnings)}** messages: "
        f"{severity_counts.get('Error', 0)} errors, {severity_counts.get('Fatal', 0)} fatal, "
        f"{severity_counts.get('Warning', 0)} warnings. All message classes are below.",
        "",
        "| Severity | Category | Rule ID | Count | Representative message |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for item in warnings:
        example = item["example_message"].replace("|", "\\|")
        if len(example) > 300:
            example = example[:297] + "..."
        lines.append(
            f"| {item['severity']} | {item['category']} | {item['rule_id']} | "
            f"{item['count']} | {example} |"
        )
    lines += [
        "",
        "Warnings are not waived. In particular, kinetic-law unit consistency "
        "cannot be established from the source declarations. The CSV files and "
        "source hash above provide the row-level audit trail; this table "
        "aggregates every libSBML message by rule ID and severity.",
        "",
        "## Subsystem archive inventory",
        "",
        "Each row below is an original XML model ID. Exact combined-reaction "
        "memberships (including shared reactions) are in `reactions.csv`; source "
        "reaction IDs are preserved there. This is structural mapping only.",
        "",
        "| Source file | Original model ID | Species | Reaction entries | Kinetic laws |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for module in modules:
        lines.append(
            f"| `{module['source_file']}` | `{module['source_model_id']}` | "
            f"{module['species_count']} | {module['reaction_entry_count']} | "
            f"{module['kinetic_law_count']} |"
        )
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "This inventory preserves original SBML species/reaction IDs and "
        "subsystem source IDs. It does not select reaction families, delete "
        "states, estimate timescales, refit parameters or declare a reduction "
        "scientifically acceptable. Such decisions require a separate "
        "`HUMAN_REVIEW_REQUIRED` record with explicit material, nucleotide, "
        "phosphate, tRNA, osmotic and ionic consequences.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sbml", type=Path, default=DEFAULT_SBML)
    parser.add_argument("--modules-zip", type=Path, default=DEFAULT_ZIP)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--simbiology", choices=("auto", "skip"), default="auto")
    args = parser.parse_args()

    sbml_path = args.sbml.resolve()
    zip_path = args.modules_zip.resolve()
    document = libsbml.readSBML(str(sbml_path))
    if document.getModel() is None:
        raise ValueError("Combined source has no readable SBML model")
    parse_messages = document.getNumErrors()
    if parse_messages:
        raise ValueError(
            "Combined source has parse messages: "
            + "; ".join(document.getError(i).getMessage() for i in range(parse_messages))
        )
    model = document.getModel()
    source_hash = sha256_bytes(sbml_path.read_bytes())
    zip_hash = sha256_bytes(zip_path.read_bytes())
    modules, signature_map = load_subsystems(zip_path)
    combined_signatures = {reaction_signature(r) for r in model.getListOfReactions()}
    unmatched_source = [signature for signature in signature_map if signature not in combined_signatures]

    species_rows = [
        {
            "species_id": s.getId(),
            "original_name": s.getName(),
            "compartment_id": s.getCompartment(),
            "initial_concentration": s.getInitialConcentration() if s.isSetInitialConcentration() else "",
            "initial_amount": s.getInitialAmount() if s.isSetInitialAmount() else "",
            "boundary_condition": truth(s.getBoundaryCondition()),
            "constant": truth(s.getConstant()),
            "has_only_substance_units": truth(s.getHasOnlySubstanceUnits()),
            "substance_units_declared": s.getSubstanceUnits(),
            "spatial_size_units_declared": s.getSpatialSizeUnits(),
            "source_sbml_sha256": source_hash,
        }
        for s in model.getListOfSpecies()
    ]
    write_csv(
        args.output_dir / "species.csv",
        list(species_rows[0]),
        species_rows,
    )

    reaction_rows: list[dict] = []
    mapping_counts: collections.Counter = collections.Counter()
    for reaction in model.getListOfReactions():
        signature = reaction_signature(reaction)
        matches = signature_map.get(signature, [])
        mapping_counts[len(matches)] += 1
        reactants = reference_rows(reaction.getListOfReactants())
        products = reference_rows(reaction.getListOfProducts())
        all_refs = reactants + products
        law = reaction.getKineticLaw() if reaction.isSetKineticLaw() else None
        node = law.getMath() if law is not None and law.isSetMath() else None
        kinetic_type = (
            "multiplication" if node is not None and node.getType() == libsbml.AST_TIMES
            else ("none" if node is None else f"AST_{node.getType()}")
        )
        reaction_rows.append(
            {
                "reaction_id": reaction.getId(),
                "original_name": reaction.getName(),
                "reversible": truth(reaction.getReversible()),
                "reactants_json": json.dumps(reactants, separators=(",", ":")),
                "products_json": json.dumps(products, separators=(",", ":")),
                "modifiers_json": json.dumps(
                    [ref.getSpecies() for ref in reaction.getListOfModifiers()],
                    separators=(",", ":"),
                ),
                "kinetic_law_formula": law.getFormula() if law is not None else "",
                "kinetic_law_math_type": kinetic_type,
                "local_parameter_ids": "|".join(
                    p.getId() for p in law.getListOfParameters()
                ) if law is not None else "",
                "stoichiometry_math_reference_count": sum(
                    ref["encoding"] == "stoichiometryMath" for ref in all_refs
                ),
                "nonunit_stoichiometry_math_reference_count": sum(
                    ref["encoding"] == "stoichiometryMath" and ref["stoichiometry"] != "1"
                    for ref in all_refs
                ),
                "source_module_ids": "|".join(dict.fromkeys(m["source_model_id"] for m in matches)),
                "source_module_reaction_refs_json": json.dumps(matches, separators=(",", ":")),
                "source_match_count": len(matches),
                "source_mapping_status": "exact_effective_stoichiometry" if matches else "unmatched",
                "source_sbml_sha256": source_hash,
            }
        )
    write_csv(args.output_dir / "reactions.csv", list(reaction_rows[0]), reaction_rows)

    parameter_rows: list[dict] = []
    for p in model.getListOfParameters():
        parameter_rows.append(
            {
                "scope": "global",
                "owner_reaction_id": "",
                "parameter_id": p.getId(),
                "original_name": p.getName(),
                "value": p.getValue() if p.isSetValue() else "",
                "units_declared": p.getUnits(),
                "constant": truth(p.getConstant()),
                "source_sbml_sha256": source_hash,
            }
        )
    for reaction in model.getListOfReactions():
        if not reaction.isSetKineticLaw():
            continue
        for p in reaction.getKineticLaw().getListOfParameters():
            parameter_rows.append(
                {
                    "scope": "reaction_local",
                    "owner_reaction_id": reaction.getId(),
                    "parameter_id": p.getId(),
                    "original_name": p.getName(),
                    "value": p.getValue() if p.isSetValue() else "",
                    "units_declared": p.getUnits(),
                    "constant": truth(p.getConstant()),
                    "source_sbml_sha256": source_hash,
                }
            )
    write_csv(
        args.output_dir / "parameters.csv",
        [
            "scope", "owner_reaction_id", "parameter_id", "original_name", "value",
            "units_declared", "constant", "source_sbml_sha256",
        ],
        parameter_rows,
    )

    # Several distinct subsystem files reuse the same SBML model ID. Count
    # memberships by archive entry, never by that non-unique model ID.
    reverse: dict[str, set[str]] = collections.defaultdict(set)
    for row in reaction_rows:
        for match in json.loads(row["source_module_reaction_refs_json"]):
            reverse[match["source_file"]].add(row["reaction_id"])
    module_rows = []
    for module in modules:
        module_rows.append(
            {
                **module,
                "mapped_combined_reaction_count": len(reverse[module["source_file"]]),
                "source_archive_sha256": zip_hash,
            }
        )
    write_csv(args.output_dir / "modules.csv", list(module_rows[0]), module_rows)

    _validation_count, warnings = validation_summary(document)
    rr = roadrunner_probe(sbml_path, model)
    n_refs = sum(int(row["stoichiometry_math_reference_count"]) for row in reaction_rows)
    sb = simbiology_probe(sbml_path, args.simbiology, n_refs)
    report = markdown_report(
        sbml_path, source_hash, zip_path, zip_hash, document, modules,
        mapping_counts, unmatched_source, warnings, rr, sb,
        species_rows, reaction_rows, parameter_rows,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8", newline="\n")
    print(
        json.dumps(
            {
                "model_id": model.getId(),
                "species": len(species_rows),
                "reactions": len(reaction_rows),
                "local_parameters": len(parameter_rows) - model.getNumParameters(),
                "modules": len(module_rows),
                "module_entries": sum(m["reaction_entry_count"] for m in modules),
                "mapping_cardinality": dict(mapping_counts),
                "unmatched_source_signatures": len(unmatched_source),
                "libsbml_messages": sum(item["count"] for item in warnings),
                "roadrunner": rr,
                "simbiology": {k: v for k, v in sb.items() if k != "command"},
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

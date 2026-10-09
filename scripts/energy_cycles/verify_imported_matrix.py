"""Independent direct RoadRunner import matrix audit against source MathML.

Run in the existing RoadRunner environment; stdlib XML parsing does not import
the candidate or source inventory generator. No numerical integration is run.
"""
import hashlib
import json
import platform
import subprocess
import sys
import xml.etree.ElementTree as ET
from fractions import Fraction
from pathlib import Path

import numpy as np
import roadrunner

ROOT = Path(__file__).resolve().parents[2]
SB = "{http://www.sbml.org/sbml/level2/version4}"
MM = "{http://www.w3.org/1998/Math/MathML}"


def parse(path):
    model = ET.fromstring(path.read_bytes()).find(SB + "model")
    species = [s.get("id") for s in model.findall(SB + "listOfSpecies/" + SB + "species")]
    columns = {}
    for reaction in model.findall(SB + "listOfReactions/" + SB + "reaction"):
        column = {}
        for name, sign in [("listOfReactants", -1), ("listOfProducts", 1)]:
            for ref in reaction.findall(SB + name + "/" + SB + "speciesReference"):
                math = ref.find(SB + "stoichiometryMath/" + MM + "math")
                value = Fraction(ref.get("stoichiometry", "1"))
                if math is not None:
                    if len(math) != 1 or math[0].tag != MM + "cn":
                        raise ValueError("Unsupported source MathML coefficient")
                    value = Fraction(math[0].text.strip())
                s = ref.get("species")
                column[s] = column.get(s, Fraction(0)) + sign * value
        columns[reaction.get("id")] = column
    return species, columns


def import_check(path, expected_species, expected_columns):
    engine = roadrunner.RoadRunner(path.read_text(encoding="utf-8"))
    species = list(engine.model.getFloatingSpeciesIds())
    reactions = list(engine.model.getReactionIds())
    if set(species) != set(expected_species) or set(reactions) != set(expected_columns):
        raise ValueError("Engine source species/reaction identity mismatch")
    actual = np.asarray(engine.getFullStoichiometryMatrix())
    expected = np.array([[float(expected_columns[r].get(s, 0)) for r in reactions] for s in species])
    bad = np.argwhere(actual != expected)
    differences = [{"species": species[i], "reaction": reactions[j], "canonical_MathML_net_coefficient": float(expected[i, j]), "imported_coefficient": float(actual[i, j])} for i, j in bad]
    return {"input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "species": len(species), "reactions": len(reactions), "matrix_shape": list(actual.shape), "source_matrix_exact_equal": not len(bad), "differing_entries": differences, "PO4_re0000000414_imported_coefficient": float(actual[species.index("PO4"), reactions.index("re0000000414")])}


def main():
    canonical = ROOT / "models/pnas2017_full_reference/original/fMGG_synthesis.xml"
    normalized = ROOT / "models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml"
    full_overlay = ROOT / "results/energy_cycles_v1/full_reference_retry1/derived_full_author_conditions.xml"
    species, reactions = parse(canonical)
    results = {"raw_canonical_diagnostic": import_check(canonical, species, reactions)}
    for label, path in [("normalized_compatibility", normalized), ("full_author_overlay", full_overlay)]:
        results[label] = import_check(path, species, reactions)
        if not results[label]["source_matrix_exact_equal"]:
            raise ValueError(label + " import lost source stoichiometry")
    report = {"status": "INDEPENDENT_ENGINE_IMPORT_MATRIX_CHECK_PASS", "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
              "environment": {"python": sys.version, "executable": sys.executable, "platform": platform.platform(), "roadrunner": roadrunner.__version__, "numpy": np.__version__},
              "command": [sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]], "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "canonical_xml_sha256": hashlib.sha256(canonical.read_bytes()).hexdigest(), "imports": results,
              "scope": "Direct imported full241x968 matrices compared against independently parsed canonical MathML; raw import is diagnostic-only. No new trajectory or scientific reduction acceptance."}
    path = ROOT / "results/energy_cycles_v1/source_reference_import_verification.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "raw_import_differences": len(results["raw_canonical_diagnostic"]["differing_entries"]), "normalized_import_exact": results["normalized_compatibility"]["source_matrix_exact_equal"], "full_overlay_import_exact": results["full_author_overlay"]["source_matrix_exact_equal"]}))


if __name__ == "__main__":
    main()

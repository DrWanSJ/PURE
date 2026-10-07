"""Compare two independent SBML-engine runs without setting an acceptance gate."""

from __future__ import annotations

import csv
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from pnas2017_s28_status import dataset_s28_status


ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/pnas2017_reference/rr_cvode_author_csv_20260924"
RESOURCES = ("Pept0003", "ATP", "ADP", "AMP", "GTP", "GDP", "PO4", "PPi", "CP", "Cr", "Gly", "Met", "tRNAGlyGCC", "tRNAfMetCAU", "GlytRNAGlyGCC", "MettRNAfMetCAU", "fMettRNAfMetCAU")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(output: Path | None = None) -> None:
    output = output or RUN / "engine_comparison_current.json"
    if output.exists():
        raise FileExistsError("Choose a new comparison output; preserved evidence cannot be overwritten")
    rr_path = RUN / "trajectory.csv"
    sb_path = RUN / "simbiology_trajectory.csv"
    name_path = RUN / "simbiology_names.json"
    effective_path = RUN / "effective_author_conditions.xml"
    with rr_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.reader(stream)
        header = next(reader)
        rr = np.asarray([[float(value) for value in row] for row in reader])
    sb = np.loadtxt(sb_path, delimiter=",")
    names = json.loads(name_path.read_text(encoding="utf-8"))
    if header != ["time_seconds"] + names:
        raise ValueError("Engine species names/order differ; comparison requires explicit mapping")
    if rr.shape != (200, 242) or sb.shape[1] != 242 or not np.all(np.diff(rr[:, 0]) > 0) or not np.all(np.diff(sb[:, 0]) > 0):
        raise ValueError("Unexpected shape or nonmonotone time grid")
    if rr[0, 0] < sb[0, 0] or rr[-1, 0] > sb[-1, 0]:
        raise ValueError("SimBiology times do not bracket RoadRunner evaluation grid")
    sb_interpolated = np.column_stack([
        np.interp(rr[:, 0], sb[:, 0], sb[:, column])
        for column in range(1, sb.shape[1])
    ])
    absolute = np.abs(rr[:, 1:] - sb_interpolated)
    final_difference = np.abs(rr[-1, 1:] - sb[-1, 1:])
    by_resource = {}
    for name in RESOURCES:
        index = names.index(name)
        by_resource[name] = {
            "roadrunner_final": float(rr[-1, index + 1]),
            "simbiology_final": float(sb[-1, index + 1]),
            "absolute_final_difference": float(final_difference[index]),
            "maximum_interpolated_trajectory_absolute_difference": float(np.max(absolute[:, index])),
        }
    inputs = (effective_path, rr_path, sb_path, name_path, RUN / "run_manifest.json", RUN / "simbiology_run.json")
    report = {
        "status": "ENGINE_COMPARISON_DIAGNOSTIC_NO_PREREGISTERED_PASS_THRESHOLD",
        "comparison_method": "Linear interpolation of SimBiology ode15s output onto the 200 RoadRunner CVODE output times; direct final-time comparison at 1000 s.",
        "same_effective_execution_sbml": True,
        "source_files_sha256": {path.relative_to(ROOT).as_posix(): sha256(path) for path in inputs},
        "species_count": len(names),
        "road_runner_points": rr.shape[0],
        "simbiology_points": sb.shape[0],
        "largest_absolute_difference_any_species_any_sample": float(np.max(absolute)),
        "largest_absolute_final_difference_any_species": float(np.max(final_difference)),
        "resources": by_resource,
        **dataset_s28_status(ROOT),
        "limitations": [
            "SBML source lacks sufficient unit declarations; both engines made dimensional assumptions.",
            "The effective model is a stoichiometry-compatible derived copy plus author CSV initial/parameter overlay; the untouched source SBML has all-one placeholders.",
            "Linear interpolation adds its own error; solver tolerances and nonnegativity handling differ.",
            "Dataset S28 acquisition and readability are reported separately; its pointwise trajectory comparison has not been run.",
            "This is a numerical integrity comparison, not experimental validation or reduction acceptance.",
        ],
    }
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"product_final_difference": by_resource["Pept0003"]["absolute_final_difference"], "largest_absolute_final_difference_any_species": report["largest_absolute_final_difference_any_species"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    main(parser.parse_args().output)

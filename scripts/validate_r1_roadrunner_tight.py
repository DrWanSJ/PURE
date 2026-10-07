#!/usr/bin/env python3
"""Independent tight RoadRunner import and identical-state rate diagnostic."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from runtime_reconstruction_rhs import SourceCoordinateRuntime
from validate_source_coordinates_full_v1 import metric_rows, rate_vector, source_matrix, write_table


ROOT = Path(__file__).resolve().parents[1]
EFFECTIVE = ROOT / "results/pnas2017_reference/rr_cvode_author_csv_20260924/effective_author_conditions.xml"
EXPECTED_EFFECTIVE_SHA256 = "bd1029bcb876c052e5a28049ffe16050efbfb518d0fdeac4e57d91ee6fc8327b"
DEFAULT_REFERENCE = ROOT / "results/reduction/r1_full_coupled_v4r3/decisive_001/trajectories.npz"
SPECIES_LIMIT = 1e-6
IDENTICAL_STATE_RATE_LIMIT = 1e-10


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    args = parser.parse_args()
    import roadrunner

    assert digest(EFFECTIVE) == EXPECTED_EFFECTIVE_SHA256
    runtime = SourceCoordinateRuntime("source_coordinate_certificate_v4.json")
    reference = np.load(args.reference)
    times = reference["times"]
    full_state = reference["full_state"]
    assert times.shape == (201,) and times[0] == 0.0 and times[-1] == 1000.0
    assert full_state.shape == (201, 241)
    expected_ids = [reaction["id"] for reaction in runtime.reactions]
    runner = roadrunner.RoadRunner(str(EFFECTIVE))
    species_ids = list(runner.model.getFloatingSpeciesIds())
    reaction_ids = list(runner.model.getReactionIds())
    assert set(species_ids) == set(runtime.species) and len(species_ids) == 241
    assert set(reaction_ids) == set(expected_ids) and len(reaction_ids) == 968
    source_rows = [runtime.species.index(name) for name in species_ids]
    source_columns = [expected_ids.index(name) for name in reaction_ids]
    source_stoich = source_matrix(runtime).toarray()[np.ix_(source_rows, source_columns)]
    imported_stoich = np.asarray(runner.getFullStoichiometryMatrix(), dtype=float)
    assert imported_stoich.shape == (241, 968)
    stoich_error = float(np.max(np.abs(imported_stoich - source_stoich)))
    assert stoich_error <= 1e-12, "RoadRunner import changed source stoichiometry"
    x0 = np.array([float(runtime.author_initial[name]) for name in runtime.species])
    imported_initial = np.array([float(runner.getValue(f"[{name}]")) for name in runtime.species])
    initial_error = float(np.max(np.abs(imported_initial - x0)))
    assert initial_error <= 1e-12, "RoadRunner import changed author initial state"

    runner.setIntegrator("cvode")
    integrator = runner.getIntegrator()
    integrator.setValue("relative_tolerance", 1e-12)
    integrator.setValue("absolute_tolerance", 1e-14)
    integrator.setValue("stiff", True)
    selections = ["time"] + [f"[{name}]" for name in runtime.species]
    trajectory = np.asarray(runner.simulate(times=times.tolist(), selections=selections), dtype=float)
    assert trajectory.shape == (201, 242)
    assert np.max(np.abs(trajectory[:, 0] - times)) <= 1e-12
    assert np.isfinite(trajectory).all()
    species_rows = metric_rows(runtime.species, full_state, trajectory[:, 1:], x0, SPECIES_LIMIT)

    # Use a fresh independently imported model. At each solver state, set all
    # 241 concentrations and ask RoadRunner for the 968 original rate laws.
    rate_runner = roadrunner.RoadRunner(str(EFFECTIVE))
    assert list(rate_runner.model.getReactionIds()) == reaction_ids
    parser_rates = np.array([rate_vector(runtime, state) for state in full_state])
    road_rates = np.empty_like(parser_rates)
    reaction_order = [reaction_ids.index(name) for name in expected_ids]
    for k, state in enumerate(full_state):
        for name, value in zip(runtime.species, state):
            rate_runner.setValue(f"[{name}]", float(value))
        road_rates[k] = np.asarray(rate_runner.model.getReactionRates(), dtype=float)[reaction_order]
    assert np.isfinite(road_rates).all()
    rate_rows = metric_rows(expected_ids, parser_rates, road_rates, parser_rates[0],
                            IDENTICAL_STATE_RATE_LIMIT)
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    write_table(out.parent / "roadrunner_species_errors.csv", species_rows)
    write_table(out.parent / "identical_state_rate_errors.csv", rate_rows)
    result = {
        "schema_version": "1.0",
        "status": "R1_INDEPENDENT_ROADRUNNER_TIGHT",
        "roadrunner_version": roadrunner.__version__,
        "effective_sbml_sha256": digest(EFFECTIVE),
        "reference_trajectory_sha256": digest(args.reference),
        "imported_species": len(species_ids),
        "imported_reactions": len(reaction_ids),
        "source_stoichiometry_max_absolute_error": stoich_error,
        "author_initial_max_absolute_error": initial_error,
        "solver": {"name": "libRoadRunner CVODE", "rtol": 1e-12, "atol": 1e-14,
                   "stiff": True, "grid_points": len(times)},
        "maxima": {"species_E_inf": max(row["E_inf"] for row in species_rows),
                   "identical_state_rates_E_inf": max(row["E_inf"] for row in rate_rows)},
        "thresholds": {"species_E_inf": SPECIES_LIMIT,
                       "identical_state_rates_E_inf": IDENTICAL_STATE_RATE_LIMIT},
        "error_tables": ["roadrunner_species_errors.csv", "identical_state_rate_errors.csv"],
    }
    result["pass"] = (result["maxima"]["species_E_inf"] <= SPECIES_LIMIT and
                      result["maxima"]["identical_state_rates_E_inf"] <= IDENTICAL_STATE_RATE_LIMIT)
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pass": result["pass"], "maxima": result["maxima"]}, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

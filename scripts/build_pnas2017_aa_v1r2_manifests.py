#!/usr/bin/env python3
"""Build per-run manifests for the v1r2 formal runs (Phase-10 recording).

Reads logs/<RUNID>.log.txt written by scripts/drive_pnas2017_aa_v1_formal.m
(raw runner console text + one machine-readable RUNSTATS JSON line) plus the
hash-verified config JSON and input_hashes.json, and writes
manifests/<RUNID>.manifest.json recording, per the execution instruction:

  run id; active partition revision; source SHA (SBML + author inputs);
  runner SHA; config SHA; MATLAB version; solver; RelTol; AbsTol; output
  grid; wall time; success/failure; algebraic root statistics; maximum
  scaled algebraic residual; minimum reconstructed concentration;
  initial-layer adjustment; solver step count; failed-step count; RHS
  evaluation count; and for RED runs additionally block-solve count, Newton
  iteration total/median/maximum, line-search/fallback count, root failures.

The manifests builder never changes an outcome: it parses what the driver
recorded.  Re-running it is idempotent.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMAL = os.path.join(ROOT, "results", "pnas2017_reference", "2026-09-26_aa_v1r2_formal")
LOGS = os.path.join(FORMAL, "logs")
MANS = os.path.join(FORMAL, "manifests")
REG = os.path.join(ROOT, "docs", "audit",
                   "pnas2017_aminoacylation_reduction_v1")


def main():
    os.makedirs(MANS, exist_ok=True)
    reg = json.load(open(os.path.join(REG, "run_registry_v1r2.json"), encoding="utf-8"))
    hashes = json.load(open(os.path.join(REG, "input_hashes.json"), encoding="utf-8"))
    built = []
    for rid, rr in sorted(reg["runs"].items()):
        logpath = os.path.join(LOGS, "%s.log.txt" % rid)
        if not os.path.exists(logpath):
            print("no log for %s (not yet executed)" % rid)
            continue
        txt = open(logpath, encoding="utf-8", errors="replace").read()
        m = re.search(r"^RUNSTATS (\{.*\})\s*$", txt, re.M)
        if not m:
            print("log for %s has no RUNSTATS line - run incomplete, "
                  "manifest NOT written" % rid)
            continue
        rec = json.loads(m.group(1))
        cfg = json.load(open(os.path.join(ROOT, rr["config"].replace("/", os.sep)),
                             encoding="utf-8"))
        manifest = {
            "schema": "pnas2017_aa_v1_run_manifest/v1r1",
            "run_id": rid,
            "active_partition_revision": rec.get("active_partition_revision"),
            "config": rr["config"],
            "config_sha256": rec.get("config_sha256"),
            "source_sha256": {
                "sbml": hashes.get(
                    "models/pnas2017_full_reference/original/fMGG_synthesis.xml"),
                "author_parameters_csv": hashes.get(
                    "models/pnas2017_full_reference/original/simulate/"
                    "Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv"),
                "author_initial_values_csv": hashes.get(
                    "models/pnas2017_full_reference/original/simulate/"
                    "Simulate_fMGG_synthesis/dat/fMGG_synthesis_initial_values.csv"),
                "author_model_m": hashes.get(
                    "models/pnas2017_full_reference/original/simulate/"
                    "Simulate_fMGG_synthesis/fMGG_synthesis.m"),
            },
            "runner_sha256": hashes.get("scripts/run_pnas2017_aa_v1_formal.m"),
            "runner_file": "scripts/run_pnas2017_aa_v1_formal.m",
            "matlab_version": rec.get("matlab_version"),
            "solver": rec.get("solver"),
            "reltol": cfg.get("reltol"),
            "abstol": cfg.get("abstol"),
            "output_grid": cfg.get("grid"),
            "output_points_recorded": rec.get("output_points"),
            "x0_scale": cfg.get("x0_scale"),
            "mode": cfg.get("mode"),
            "wall_time_s": rec.get("wall_time_s"),
            "outcome": rec.get("outcome"),
            "error": rec.get("error"),
            "solver_stats": {
                "steps_successful": rec.get("solver_steps_successful"),
                "steps_failed": rec.get("solver_steps_failed"),
                "rhs_evaluations": rec.get("solver_rhs_evaluations"),
            },
            "initial_layer_adjustment": {
                "max_species": rec.get("initial_layer_max_species"),
                "max_from": rec.get("initial_layer_max_from"),
                "max_to": rec.get("initial_layer_max_to"),
                "max_abs": rec.get("initial_layer_max_abs"),
            },
            "consistent_start": {
                k.split("consistent_start_")[1]: v for k, v in rec.items()
                if k.startswith("consistent_start_")},
            "trajectory_sha256": rec.get("trajectory_sha256"),
        }
        if "algebraic" in rec:
            a = rec["algebraic"]
            manifest["algebraic_root_statistics"] = {
                "block_solve_count": a.get("block_solves"),
                "newton_iterations_total": a.get("newton_iters_total"),
                "newton_iterations_median": a.get("newton_iters_median"),
                "newton_iterations_max": a.get("newton_iters_max"),
                "line_search_rejections": a.get("line_search_rejections"),
                "jacobian_refreshes": a.get("jacobian_refreshes"),
                "plateau_accepts": a.get("plateau_accepts"),
                "max_abs_algebraic_residual": a.get("max_abs_residual"),
                "max_scaled_algebraic_residual": a.get("max_scaled_residual"),
                "min_reconstructed_concentration": a.get(
                    "min_reconstructed_concentration"),
                "root_failures": rec.get("root_failures"),
            }
        elif cfg.get("mode") == "reduced":
            manifest["algebraic_root_statistics"] = None
        out = os.path.join(MANS, "%s.manifest.json" % rid)
        with open(out, "w", newline="\n", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
            f.write("\n")
        built.append(rid)
        print("manifest: %-10s outcome=%-16s wall=%8.1f s" %
              (rid, rec.get("outcome"), rec.get("wall_time_s") or -1))
    print("%d manifests built" % len(built))
    return 0


if __name__ == "__main__":
    sys.exit(main())

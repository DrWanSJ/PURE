#!/usr/bin/env python3
"""Safe, additive reproduction entry point for the frozen Phase C V1 milestone.

Usage: python scripts/reduction/rapid_v1/release.py reproduce --run-id MY_UNIQUE_ID
       python scripts/reduction/rapid_v1/release.py verify --run-id MY_UNIQUE_ID

Both commands rebuild the exact mathematical objects and preserve original files.
verify re-scores saved evidence; reproduce additionally executes the original full
campaign and independent solver checks. Existing output directories are refused.
The historical individual entry points remain untouched; do not invoke their main
functions directly to verify this release, because their default paths are frozen.
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import functools
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HISTORY = ROOT / "results/reduction/rapid_v1"
DOC = ROOT / "docs/reduction/rapid_reduction"
BASE = ROOT / "results/reduction/phase_c_release_v1"
PREFLIGHT = DOC / "release_preflight_20261010.json"
MANIFEST = DOC / "release_manifest_v1.json"
MILESTONE = "PNAS2017_PHASE_C_REDUCTION_V1_20261010"
EXPECTED = {
    "models/pnas2017_full_reference/original/fMGG_synthesis.xml":
        "dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df",
    "models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_parameters.csv":
        "cfb24e2cb9f70168e30355d51dd4a4036686ceefab1a2b26bac122448c81b465",
    "docs/reduction/rapid_reduction/mathematical_certificate.json":
        "c698ca685bf1052f529c9b8b2bb3626c2a3176818e868469cf9b29e6f3e26df0",
}
MODELS = ["R0", "R1", "R2", "R3_CHAIN1", "R3_CHAIN12", "R3_RECYCLE", "R3_CHAIN12_RECYCLE"]
SCENARIOS = ["AUTHOR_BASELINE", "FLOW_CHALLENGE", "ENERGY_FACTOR_LIMITED", "COMPETITION_OCCUPANCY"]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True,
                                    allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def protected_inventory():
    """Protect original research and all prior scientific source/code/data.

    Current top-level navigation/dashboard files are a separate release concern.
    They are checked by the publication manifest after authorized editing ends.
    """
    preflight = load(PREFLIGHT)
    paths = {r["path"]: r["sha256"] for r in preflight["original_research_files"]}
    for row in preflight["tracked"]:
        p = row["path"]
        if p.startswith(("models/", "results/", "configs/", "scripts/", "docs/reduction/")):
            # The presentation generator is expressly authorized for upgrading.
            if p in {"scripts/build_reduction_reasoning_atlas.py",
                     "scripts/reduction_reasoning_atlas.template.html",
                     "scripts/test_reduction_reasoning_atlas.py"}:
                continue
            paths[p] = row["sha256"]
    require(len(preflight["original_research_files"]) == 277, "Original 277-file inventory missing")
    return paths


def check_protection(inventory):
    changed = [p for p, h in inventory.items() if not (ROOT / p).is_file() or sha(ROOT / p) != h]
    require(not changed, "PROTECTED_SCIENTIFIC_EVIDENCE_CHANGED: " + repr(changed))
    for p, h in EXPECTED.items():
        require(sha(ROOT / p) == h, "Pinned source/certificate hash mismatch: " + p)
    freeze = load(HISTORY / "freeze.json")
    require(sha(ROOT / "configs/reduction/rapid_v1.json") == freeze["config_sha256"], "Frozen config changed")
    require(sha(DOC / "protocol.md") == freeze["protocol_sha256"], "Frozen protocol changed")
    return {"status": "PASS", "protected_original_files": len(inventory),
            "original_research_files": 277, "changed": [], "pinned_sha256": EXPECTED}


def manifest_check(required=False):
    if not MANIFEST.is_file():
        require(not required, "Final publication manifest is required but absent")
        return {"status": "NOT_YET_PACKAGED", "publication_ready": False}
    manifest = load(MANIFEST)
    rows = manifest["files"]
    paths = [r["path"] for r in rows]
    require(len(paths) == len(set(paths)), "Duplicate manifest path")
    changed = [r["path"] for r in rows if not (ROOT / r["path"]).is_file()
               or sha(ROOT / r["path"]) != r["sha256"]
               or (ROOT / r["path"]).stat().st_size != r["bytes"]]
    require(not changed, "RELEASE_MANIFEST_MISMATCH: " + repr(changed))
    originals = {r["path"] for r in load(PREFLIGHT)["original_research_files"]}
    require(originals <= set(paths), "Release manifest omits original research evidence")
    return {"status": "PASS", "files_checked": len(rows), "sha256": sha(MANIFEST),
            "all_original_research_paths_included": True, "publication_ready": True}


class AccessAudit:
    """Record runtime inputs; forbid reference trajectories and escaped writes."""
    def __init__(self, output):
        self.output = output.resolve()
        self.runtime_phase = None
        self.reads = {}
        self.forbidden_attempts = []
        self.enabled = True

    def hook(self, event, args):
        if not self.enabled or event != "open":
            return
        path, mode, flags = args
        if isinstance(path, int):
            return
        path = Path(os.fsdecode(path)).resolve()
        writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing:
            require(path.is_relative_to(self.output), "Write outside fresh run directory refused: " + str(path))
        if self.runtime_phase and not writing:
            trajectory = path.suffix == ".npz" or "trajectories" in path.parts
            if trajectory:
                self.forbidden_attempts.append(str(path))
                raise RuntimeError("Reference/saved trajectory read during runtime is forbidden: " + str(path))
            if path.is_relative_to(ROOT):
                self.reads.setdefault(self.runtime_phase, set()).add(relative(path))

    @contextlib.contextmanager
    def phase(self, name):
        previous = self.runtime_phase
        self.runtime_phase = name
        try:
            yield
        finally:
            self.runtime_phase = previous

    def wrap_runtime(self, cls):
        for method in ("__init__", "simulate"):
            original = getattr(cls, method)

            def wrap(original, method):
                @functools.wraps(original)
                def traced(instance, *args, **kwargs):
                    name = args[0] if method == "__init__" else instance.model
                    with self.phase(str(name) + "." + method):
                        return original(instance, *args, **kwargs)
                return traced
            setattr(cls, method, wrap(original, method))

    def report(self):
        code = ROOT / "scripts/reduction/rapid_v1/runtime.py"
        tree = ast.parse(code.read_text(encoding="utf-8"))
        calls = sorted({ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)
                        and (isinstance(n.func, ast.Name) and n.func.id in ("load", "open")
                             or isinstance(n.func, ast.Attribute) and n.func.attr in ("load", "loadtxt", "read_csv", "read_bytes", "read_text"))})
        return {"status": "PASS" if not self.forbidden_attempts else "FAIL",
                "runtime_source_sha256": sha(code), "static_file_read_call_sites": calls,
                "runtime_repository_reads": {k: sorted(v) for k, v in sorted(self.reads.items())},
                "blocked_trajectory_read_attempts": self.forbidden_attempts,
                "scope": "Actual Runtime construction and simulation were audited. Saved arrays are read only by the separate comparison/scoring stage. Counters are integrated in each runtime.",
                "write_policy": "All Python open-for-write calls are confined to this fresh output directory."}


def configure_modules(output, protection):
    import common
    import mathematics
    import runtime
    import validate
    import score_saved
    import solver_crosschecks
    for module in (common, mathematics, runtime, validate, score_saved, solver_crosschecks):
        module.RESULT = output
        module.DOC = output / "mathematics"
        module.protection = protection
    return mathematics, runtime, validate, score_saved, solver_crosschecks


def independent_algebra(mathematics, output):
    """Evaluate identities/counterexamples from canonical source, not certificate flags."""
    import sympy as sp
    names, reactions, initial = mathematics.source_network()
    S = mathematics.matrix_source(names, reactions)
    require(len(names) == 241 and len(reactions) == 968, "Source dimensions changed")
    require(next(r for r in reactions if r["id"] == "re0000000414")["products"]["PO4"] == 2,
            "Canonical re0000000414 must release 2 PO4")
    cert = load(output / "mathematics/mathematical_certificate.json")
    charts = load(output / "charts.json")
    require(cert == load(DOC / "mathematical_certificate.json"), "Rebuilt certificate differs from frozen certificate")
    require(charts == load(HISTORY / "charts.json"), "Rebuilt coordinate charts differ from frozen charts")
    tail = charts["R3_RECYCLE"]["tail"]
    P = sp.Matrix(tail["source_projection_rows"])
    tail_indices = [names.index(s) for s in mathematics.TAIL]
    ids = charts["R3_RECYCLE"]["tail_rate_indices"]
    D = sp.zeros(len(ids), 7)
    for j, rid in enumerate(ids):
        r = reactions[rid]
        D[j, mathematics.TAIL.index(next(s for s in r["factors"] if s != "k1"))] = sp.Rational(str(r["k"]))
    A = S[tail_indices, ids] * D
    H = P.T * (P * P.T).inv()
    Q = P * A * H
    require(P * A == Q * P and P.rank() == 5, "Exact recycling quotient identity failed")
    counterexamples = []
    for chain in mathematics.CHAIN:
        _, projection, _, _ = mathematics.physical_projection(names, set(names), [chain["round"]])
        a = sp.zeros(241, 1)
        b = sp.zeros(241, 1)
        a[names.index(chain["slow"])] = 1
        b[names.index(chain["fast"])] = 1
        b[names.index("EFTu_GDP")] = 1
        require(projection * a == projection * b, "Counterexample projections do not match")

        def vector_field(x):
            v = []
            for r in reactions:
                rate = sp.Rational(str(r["k"]))
                for s in r["factors"]:
                    if s != "k1":
                        rate *= x[names.index(s)]
                v.append(rate)
            return S * sp.Matrix(v)
        delta = projection * (vector_field(a) - vector_field(b))
        require(delta != sp.zeros(projection.rows, 1), "Gly non-exactness counterexample disappeared")
        counterexamples.append({"round": chain["round"], "source_ids": chain["ids"],
                                "same_projected_state": True, "exact_lumpability": False,
                                "projected_derivative_max_difference": str(max(abs(v) for v in delta)),
                                "effective_rate": "7000/1007",
                                "source_waiting_variance": str(sp.Rational(1, 49) + sp.Rational(1, 1000000)),
                                "effective_waiting_variance": str(sp.Rational(1007, 7000) ** 2)})
    result = {"status": "PASS", "species": 241, "canonical_directed_reactions": 968,
              "re0000000414_PO4_coefficient": 2, "source_rank": cert["source_rank"],
              "source_left_nullity": cert["source_left_nullity"],
              "author_support_species": cert["author_support_species"], "author_zero_species": cert["zero_count"],
              "support_left_nullity": cert["author_support_species"] - cert["support_live_rank"],
              "support_rank": cert["support_live_rank"], "positive_parameter_directions": sum(r["k"] > 0 for r in reactions),
              "support_live_directions": len(charts["R2"]["live_reaction_indices"]),
              "rebuilt_certificate_semantically_identical": True, "rebuilt_charts_semantically_identical": True,
              "recycling": {"identity": "P A_tail = Q P", "exact_zero_residual": True,
                             "microstates": 7, "observables": P.rank(), "nonunique_inverse_dimension": 7 - P.rank(),
                             "P": [[str(v) for v in P.row(i)] for i in range(P.rows)],
                             "Q": [[str(v) for v in Q.row(i)] for i in range(Q.rows)]},
              "Gly_source_vector_field_counterexamples": counterexamples}
    save(output / "independent_algebra.json", result)
    return result


def read_run(folder, tag):
    import numpy as np
    with np.load(folder / "trajectories" / (tag + ".npz"), allow_pickle=False) as z:
        out = {k: z[k] for k in z.files}
    out["diagnostics"] = load(folder / "trajectories" / (tag + ".json"))
    return out


def numerical_summary(runtime, output, fresh):
    import numpy as np
    cfg = load(ROOT / "configs/reduction/rapid_v1.json")
    report = load(output / "validation_results.json")
    original = load(HISTORY / "validation_results.json")
    checks = []
    counters = None
    for scenario in cfg["scenarios"][:4]:
        sid = scenario["id"]
        require(report["scenarios"][sid]["reference_converged"], sid + " reference did not converge")
        for model in MODELS:
            row = report["scenarios"][sid]["models"][model]
            require(row["diagnostics"]["success"] and row["diagnostics"]["final_time"] == 1000,
                    sid + " " + model + " solver failure/partial execution")
            require(row["status"] == original["scenarios"][sid]["models"][model]["status"],
                    sid + " " + model + " gate status differs from frozen report")
            rt = runtime.Runtime(model, scenario)
            require(rt.nc == 20, "Missing integration counters")
            if counters is None:
                counters = rt.counter_names
            require(rt.counter_names == counters, "Inconsistent counter identity/order")
            old = read_run(HISTORY, sid + "__" + model)
            current = read_run(output if fresh else HISTORY, sid + "__" + model)
            require(np.array_equal(current["t"], np.array(cfg["observation_grid"])), "Observation grid differs")
            comp = runtime.compare_observables(rt, old, current)
            err = comp["source_reconstruction_numeric_error"]
            require(err <= cfg["gates"]["exact_numeric_error"], "Fresh/saved trajectory discrepancy exceeds frozen numerical accuracy")
            require(current["counters"].shape[0] == 20 and current["chemical"].shape[0] == rt.dim,
                    "Stored chemical/counter coordinates incorrect")
            checks.append({"scenario": sid, "model": model, "status": row["status"],
                           "chemical_dimensions": rt.dim, "total_integrated_coordinates": rt.dim + 20,
                           "evaluated_mass_action_expressions": len(rt.k),
                           "fresh_vs_frozen_source_numeric_error": err if fresh else None,
                           "new_solver_execution": fresh})
    domain = report["scenarios"]["ZERO_BRANCH_REACTIVATION"]["models"]
    require(all(domain[m]["status"] == "BLOCKED" for m in MODELS if m not in ("R0", "R1")),
            "Author-domain reactivation guard missing")
    for sid, entry in report["scenarios"].items():
        for m, row in entry["models"].items():
            if "diagnostics" in row:
                require(row["diagnostics"]["success"], "Solver failure cannot be scored as success")
    result = {"status": "PASS", "mode": "FRESH_FULL_CAMPAIGN" if fresh else "SAVED_EVIDENCE_RESCORED",
              "four_scenarios": SCENARIOS, "models_per_scenario": 7, "checks": checks,
              "counter_names": counters, "counter_count": 20,
              "gates_unchanged": cfg["gates"], "normalization_rules_unchanged": cfg["scale_rule"],
              "normalization_detail": "Per-scenario numeric observable and counter scales are in validation_results.json comparison.fixed_scales and comparison.counter_fixed_scales; the frozen runtime is authoritative.",
              "source_time_unit": cfg["time_unit"], "windows": cfg["windows"],
              "zero_branch_reactivation_R2_R3": "BLOCKED_AS_REQUIRED",
              "historical_solver_failures": "Retained in original failure_evidence.jsonl; none silently converted to a completed solve.",
              "inherited_MATLAB": "Historical 99 passed / 3 failed / 1 incomplete; not rerun or fixed by this Python campaign.",
              "formal_scientific_decision": "Separate dated acceptance records; numerical PASS does not extend their scope."}
    save(output / "numerical_reproducibility.json", result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("verify", "reproduce"))
    parser.add_argument("--run-id", required=True, help="New portable directory name; existing names are refused")
    parser.add_argument("--require-manifest", action="store_true", help="Require the final release manifest and verify every listed hash")
    args = parser.parse_args()
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", args.run_id) is not None, "Unsafe run-id")
    require(args.run_id.upper().split(".")[0] not in {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)], *[f"LPT{i}" for i in range(1, 10)]}, "Reserved run-id")
    output = BASE / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    audit = AccessAudit(output)
    sys.addaudithook(audit.hook)
    result = {"milestone": MILESTONE, "mode": args.mode, "run_id": args.run_id,
              "output_directory": relative(output), "status": "RUNNING"}
    try:
        inventory = protected_inventory()
        protection = lambda: check_protection(inventory)
        result["pre_run_protection"] = protection()
        result["publication_manifest"] = manifest_check(args.require_manifest)
        (output / "mathematics").mkdir()
        (output / "trajectories").mkdir()
        shutil.copyfile(DOC / "protocol.md", output / "mathematics/protocol.md")
        shutil.copyfile(Path(__file__), output / "executed_wrapper_snapshot.py")
        save(output / "run_inputs.json", {"source_and_evidence_sha256": inventory,
                                          "wrapper_sha256": sha(Path(__file__)),
                                          "python": platform.python_version(), "platform": platform.platform(),
                                          "argv": [args.mode, "--run-id", args.run_id]})
        mathematics, runtime, validate, score_saved, crosschecks = configure_modules(output, protection)
        import scipy
        import numpy
        import sympy
        import numba
        result["software_versions"] = {"python": platform.python_version(), "numpy": numpy.__version__,
                                       "scipy": scipy.__version__, "sympy": sympy.__version__, "numba": numba.__version__}
        audit.wrap_runtime(runtime.Runtime)
        print("Rebuilding exact mathematical objects in " + relative(output), flush=True)
        mathematics.main()
        result["independent_algebra"] = independent_algebra(mathematics, output)
        if args.mode == "reproduce":
            print("Executing frozen full campaign, local failures, and independent solver checks", flush=True)
            validate.main()
            crosschecks.main()
        else:
            print("Checking immutable saved trajectories; no fresh ODE execution is claimed", flush=True)
            shutil.copyfile(HISTORY / "validation_results.json", output / "validation_results.json")
            score_saved.read_run = lambda tag: read_run(HISTORY, tag)
            validate.pointwise_checks()
        score_saved.main()
        result["numerical_reproducibility"] = numerical_summary(runtime, output, args.mode == "reproduce")
        result["runtime_input_audit"] = audit.report()
        save(output / "runtime_input_audit.json", result["runtime_input_audit"])
        result["post_run_protection"] = protection()
        result["status"] = "PASS"
        result["publication_ready"] = result["publication_manifest"]["publication_ready"]
        result["limitations"] = ["Four frozen author-domain scenarios only", "Gly aggregation remains approximate",
                                 "Recycling microscopic inverse is nonunique", "No claim of speed improvement",
                                 "Fresh timing is not substituted for the original reported timing"]
        save(output / "verification_report.json", result)
        print(json.dumps({"status": "PASS", "mode": args.mode, "report": relative(output / "verification_report.json")}), flush=True)
    except Exception:
        result["status"] = "FAIL"
        result["error"] = traceback.format_exc()
        result["runtime_input_audit"] = audit.report()
        save(output / "verification_report.json", result)
        raise
    finally:
        audit.enabled = False


if __name__ == "__main__":
    main()

"""Independent symbolic and trajectory checks for the additive NDK coordinate run."""
from __future__ import annotations

import hashlib
import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import sympy as sy

from independent_tests import ROOT, active_reactions, enzyme_states, net, read_sources, require
from numerical_verify import verify_one


def symbolic_proof(module):
    a, b, q, kf, E, kA, kB, rAB = sy.symbols("a b q kf Efree kATP kGDP rAB", positive=True)
    states = enzyme_states(module)
    # Extract the exact source generator rows before substituting abstract
    # source association rates. No candidate module is imported.
    free = {"ATP": a / kA, "GDP": b / kB, "ADP": sy.Symbol("ADP", positive=True), "GTP": sy.Symbol("GTP", positive=True)}
    state_symbols = {s: sy.Symbol(s) for s in states}
    rhs = {s: sy.Integer(0) for s in states}
    row_constants = {r["id"]: r["k"] for r in module["reactions"].values()}
    kA_value = row_constants["re0000000355"]
    kB_value = row_constants["re0000000357"]
    for reaction in active_reactions(module):
        parameters = {sy.Symbol("k1"): sy.Rational(reaction["k"])}
        parameters.update({sy.Symbol(s): v for s, v in free.items()})
        flux = reaction["law"].subs(parameters).subs({kA: sy.Rational(kA_value), kB: sy.Rational(kB_value)})
        for state, coefficient in zip(states, net(reaction, states)):
            rhs[state] += coefficient * flux
    # Anchor symbolic dissociation and conversion constants to parsed values.
    q_value = sy.Rational(row_constants["re0000000356"])
    kf_value = sy.Rational(row_constants["re0000000363"])
    require(row_constants["re0000000364"] == 0, "NDK_COORDINATE_REVERSE_AUTHOR_ZERO", "re364")
    expected_binary_A = a * state_symbols["NDK"] + q * state_symbols["NDK_GDP_ATP"] - (q + b) * state_symbols["NDK_ATP"]
    expected_binary_B = b * state_symbols["NDK"] + q * state_symbols["NDK_GDP_ATP"] - (q + a) * state_symbols["NDK_GDP"]
    expected_loaded = b * state_symbols["NDK_ATP"] + a * state_symbols["NDK_GDP"] - (2 * q + kf) * state_symbols["NDK_GDP_ATP"]
    for state, expected in [("NDK_ATP", expected_binary_A), ("NDK_GDP", expected_binary_B), ("NDK_GDP_ATP", expected_loaded)]:
        require(sy.simplify(rhs[state] - expected.subs({q: q_value, kf: kf_value})) == 0, "NDK_SOURCE_SYMBOLIC_BALANCE_ROW", state)
    L = 1 / (q + b) + 1 / (q + a)
    beta = q ** 2 * L
    alpha = a * b * L
    stationary_binary_A = E * (a + q * rAB) / (q + b)
    stationary_binary_B = E * (b + q * rAB) / (q + a)
    loaded_rhs = expected_loaded.subs({state_symbols["NDK"]: E, state_symbols["NDK_ATP"]: stationary_binary_A,
                                      state_symbols["NDK_GDP"]: stationary_binary_B, state_symbols["NDK_GDP_ATP"]: E * rAB})
    require(sy.simplify(loaded_rhs - E * (alpha - (beta + kf) * rAB)) == 0, "NDK_LOADED_BALANCE_ELIMINATION", "residual")
    selected_rAB = alpha / (beta + kf)
    current = kf * E * selected_rAB
    proofs = {}
    for resource, substrate, microscopic_k, binary, other in [
            ("ATP", a, kA, stationary_binary_A, b),
            ("GDP", b, kB, stationary_binary_B, a)]:
        theta = other * L / (beta + kf)
        storage = (1 + q * theta) / (q + other) + theta
        total = substrate / microscopic_k + binary.subs(rAB, selected_rAB) + E * selected_rAB
        factored_total = substrate / microscopic_k * (1 + E * microscopic_k * storage)
        hazard = kf * E * microscopic_k * theta / (1 + E * microscopic_k * storage)
        ledger_residual = sy.simplify(total - factored_total)
        current_residual = sy.simplify(current - total * hazard)
        require(ledger_residual == current_residual == 0, "NDK_HAZARD_EXACT_SYMBOLIC_IDENTITY", resource)
        boundary_hazard = sy.simplify(hazard.subs(substrate, 0))
        require(not boundary_hazard.has(sy.zoo, sy.nan, sy.oo), "NDK_HAZARD_FINITE_AT_DEPLETION", resource)
        proofs[resource] = {"source_total_factorization_residual": str(ledger_residual), "source_current_equals_total_times_hazard_residual": str(current_residual), "depletion_boundary_hazard": str(boundary_hazard)}
    L0, qstate, hazard = sy.symbols("L0 qstate hazard", positive=True)
    remaining = L0 * sy.exp(-qstate)
    extent = L0 * (1 - sy.exp(-qstate))
    require(sy.simplify(sy.diff(remaining, qstate) * hazard + remaining * hazard) == 0, "NDK_LOG_COORDINATE_REMAINING_IDENTITY", "residual")
    require(sy.simplify(sy.diff(extent, qstate) * hazard - remaining * hazard) == 0, "NDK_LOG_COORDINATE_EXTENT_IDENTITY", "residual")
    return {"status": "INDEPENDENT_CANONICAL_SYMBOLIC_COORDINATE_PROOF_PASS", "resource_cases": proofs, "remaining_and_extent_coordinate_derivative_residuals": "0", "scope": "Exact coordinate and source-rate factorization at kr=0; finite algebraic root tolerances remain numerical approximations."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--numerical-dir", type=Path, default=ROOT / "results/energy_cycles_v1/numerical_ndk_coordinate")
    parser.add_argument("--output", type=Path, default=ROOT / "results/energy_cycles_v1/ndk_coordinate_verification.json")
    parser.add_argument("--addendum", type=Path, default=ROOT / "docs/reduction/energy_cycles/ndk_numerical_repair_preregistration.json")
    args = parser.parse_args()
    args.numerical_dir = args.numerical_dir.resolve()
    args.output = args.output.resolve()
    args.addendum = args.addendum.resolve()
    source, initial, parameters, index, modules = read_sources()
    registration_path = ROOT / "docs/reduction/energy_cycles/validation_preregistration.json"
    registration = json.loads(registration_path.read_text())
    report = {"symbolic": symbolic_proof(modules["NDK"]), "original_preregistration_sha256": hashlib.sha256(registration_path.read_bytes()).hexdigest(), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    paths = sorted(args.numerical_dir.glob("*/*/metrics.json"))
    addendum_hash = hashlib.sha256(args.addendum.read_bytes()).hexdigest() if args.addendum.exists() else None
    for path in paths:
        metadata = json.loads(path.read_text())
        require(metadata["engineering_addendum_sha256"] == addendum_hash, "NDK_ENGINEERING_ADDENDUM_PROVENANCE", str(path))
        require(metadata["preregistration_sha256"] == report["original_preregistration_sha256"], "NDK_ORIGINAL_PREREGISTRATION_PRESERVED", str(path))
    if addendum_hash:
        addendum_data = json.loads(args.addendum.read_text())
        for relative, expected in addendum_data["implementation_sha256"].items():
            require(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, "NDK_ENGINEERING_IMPLEMENTATION_PROVENANCE", relative)
    checks = [verify_one(path, modules, registration) for path in paths]
    report["completed_coordinate_trajectory_pairs_checked"] = len(checks)
    report["trajectory_checks"] = checks
    report["status"] = "INDEPENDENT_SYMBOLIC_AND_NUMERICAL_COORDINATE_CHECK_PASS" if checks else "INDEPENDENT_SYMBOLIC_PROOF_PASS_NUMERICAL_RESULTS_NOT_YET_AVAILABLE"
    report["scope"] = "Additive engineering coordinate verification, preserving original 84 trajectory checks and seven raw NDK failure paths; no scientific promotion or full-model acceptance."
    report["numerical_directory"] = args.numerical_dir.relative_to(ROOT).as_posix()
    report.update(source_commit=registration["source_commit"], source_hashes=registration["source_hashes"],
                  environment={"python": sys.version, "numpy": np.__version__, "sympy": sy.__version__, "platform": platform.platform()},
                  command=[sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                  independent_parser_sha256=hashlib.sha256((ROOT / "scripts/energy_cycles/independent_tests.py").read_bytes()).hexdigest())
    if addendum_hash:
        report["engineering_addendum_sha256"] = addendum_hash
        report["engineering_addendum_path"] = args.addendum.relative_to(ROOT).as_posix()
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "trajectory_pairs": len(checks)}))


if __name__ == "__main__":
    main()

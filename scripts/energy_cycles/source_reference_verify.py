"""Independent XML overlays, source-reference fluxes and embedding-domain audit."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import sympy as sy
from scipy.optimize import root

from independent_tests import (ROOT, SB, active_reactions, enzyme_states,
                               form_composition, parse_xml, read_sources,
                               require, signature)
from numerical_verify import source_rates


def overlay_check(path, source, initial, parameters, allowed_parameters=None):
    overlay = parse_xml(path.read_bytes())
    require(set(overlay["species"]) == set(source["species"]), "REFERENCE_OVERLAY_SPECIES", str(path))
    require(set(overlay["reactions"]) == set(source["reactions"]), "REFERENCE_OVERLAY_REACTIONS", str(path))
    model = ET.fromstring(path.read_bytes()).find(SB + "model")
    values = {}
    for element in model.findall(SB + "listOfReactions/" + SB + "reaction"):
        values[element.get("id")] = float(element.find(SB + "kineticLaw/" + SB + "listOfParameters/" + SB + "parameter").get("value"))
    for rid, reaction in source["reactions"].items():
        other = overlay["reactions"][rid]
        require(signature(reaction) == signature(other) and reaction["law"] == other["law"], "REFERENCE_OVERLAY_CHEMISTRY", rid)
        expected = float(parameters[rid]) if allowed_parameters is None or rid in allowed_parameters else 0.0
        require(values[rid] == expected, "REFERENCE_OVERLAY_AUTHOR_PARAMETER", rid)
    for s, attributes in overlay["species"].items():
        require(float(attributes["initialConcentration"]) == float(initial[s]), "REFERENCE_OVERLAY_AUTHOR_INITIAL", s)
        source_metadata = {k: v for k, v in source["species"][s].items() if k != "initialConcentration"}
        derived_metadata = {k: v for k, v in attributes.items() if k != "initialConcentration"}
        require(source_metadata == derived_metadata, "REFERENCE_OVERLAY_SPECIES_SEMANTICS", s)
    require(overlay["reactions"]["re0000000414"]["p"]["PO4"] == 2, "REFERENCE_OVERLAY_MATHML_TWO_PO4", str(path))
    return {"all968_original_stoichiometries_and_kinetic_laws_equal": True, "all241_initial_values_checked": True, "all968_author_or_declared_zero_parameters_checked": True, "species_metadata_except_initial_values_unchanged": True, "re0000000414_PO4_coefficient": 2, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def build_stationarity(module):
    boundary, composition = form_composition(module)
    states = enzyme_states(module)
    index = {s: i for i, s in enumerate(states)}
    C = np.array([[float(composition[s][r]) for s in states] for r in boundary])
    transitions = []
    for reaction in active_reactions(module):
        origin = next(s for s in reaction["r"] if s in index)
        target = next(s for s in reaction["p"] if s in index)
        factors = [boundary.index(str(s)) for s in (reaction["law"] / sy.Symbol("k1") / sy.Symbol(origin)).free_symbols]
        transitions.append((index[origin], index[target], float(reaction["k"]), factors))
    def stationary(free, enzyme_total):
        Q = np.zeros((len(states), len(states)))
        for origin, target, constant, factors in transitions:
            rate = constant * np.prod(free[factors])
            Q[target, origin] += rate
            Q[origin, origin] -= rate
        system = Q.copy()
        system[-1] = 1
        rhs = np.zeros(len(states))
        rhs[-1] = enzyme_total
        return np.linalg.solve(system, rhs)
    return boundary, states, C, stationary


def full_reference(source, initial, parameters, modules):
    folder = ROOT / "results/energy_cycles_v1/full_reference_retry1"
    if not (folder / "manifest.json").exists():
        return {"status": "NOT_AVAILABLE"}
    manifest = json.loads((folder / "manifest.json").read_text())
    result = {"overlay": overlay_check(folder / "derived_full_author_conditions.xml", source, initial, parameters), "runs": {}}
    combined = {"reactions": {rid: r for module in modules.values() for rid, r in module["reactions"].items()}}
    arrays = {}
    for label in ["base", "tight"]:
        path = folder / (label + ".npz")
        with np.load(path, allow_pickle=False) as data:
            species = list(data["species"])
            x = data["concentrations"]
            time = data["time"]
            rates = list(data["energy_reaction_ids"])
            require(set(species) == set(source["species"]), "REFERENCE_TRAJECTORY_SPECIES", label)
            require(np.array_equal(x[0], [float(initial[s]) for s in species]), "REFERENCE_TRAJECTORY_INITIAL", label)
            recomputed = source_rates(combined, species, x, rates)
            discrepancy = float(np.max(np.abs(recomputed - data["energy_rates"])))
            require(discrepancy <= 1e-9 * max(np.max(np.abs(recomputed)), 1), "REFERENCE_SOURCE_ENERGY_RATES", label)
            endpoint = float(x[-1, species.index("Pept0003")])
            require(endpoint == manifest["runs"][label]["Pept0003_endpoint"], "REFERENCE_PEPT_ENDPOINT", label)
            require(hashlib.sha256(path.read_bytes()).hexdigest() == manifest["runs"][label]["sha256"], "REFERENCE_TRAJECTORY_HASH", label)
            result["runs"][label] = {"Pept0003_endpoint": endpoint, "minimum_unclipped_inventory": float(x.min()), "maximum_canonical_energy_flux_discrepancy": discrepancy, "trajectory_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            arrays[label] = x.copy()
            if label == "tight":
                result["embedding_domain_check"] = verify_embedding_domain(modules, species, time, x)
    differences = np.abs(arrays["base"] - arrays["tight"])
    result["Pept0003_endpoint_base_tight_difference"] = float(differences[-1, species.index("Pept0003")])
    require(result["Pept0003_endpoint_base_tight_difference"] == manifest["convergence"]["Pept0003_endpoint_absolute_difference"], "REFERENCE_ENDPOINT_CONVERGENCE", "mismatch")
    result["status"] = "INDEPENDENT_SOURCE_REFERENCE_CHECK_PASS_NOT_CANDIDATE_VALIDATION"
    return result


def verify_embedding_domain(modules, species, time, x):
    path = ROOT / "results/energy_cycles_v1/embedding_domain_audit.json"
    if not path.exists():
        return {"status": "NOT_AVAILABLE"}
    reported = json.loads(path.read_text())
    checks = {}
    for name, module in modules.items():
        boundary, states, C, stationary = build_stationarity(module)
        free = x[:, [species.index(s) for s in boundary]]
        occupancies = x[:, [species.index(s) for s in states]]
        totals = free + occupancies @ C.T
        enzyme_total = occupancies.sum(axis=1)
        failures = []
        positive_count = 0
        worst_residual = 0.0
        # A fresh generic generator plus finite-difference root search provides
        # independent candidate-domain diagnostics; no explicit rate formula is
        # imported. Failure of a local solve is never a global no-root proof.
        for i, tt in enumerate(time):
            try:
                solve = root(lambda u: u + C @ stationary(u, enzyme_total[i]) - totals[i], totals[i], tol=1e-10)
                u = solve.x
                h = stationary(u, enzyme_total[i])
                residual = float(np.max(np.abs(u + C @ h - totals[i])))
                worst_residual = max(worst_residual, residual)
                physical = residual <= 1e-8 and min(u.min(), h.min()) >= -1e-8 and np.max(u - totals[i]) <= 1e-8
                if physical:
                    positive_count += 1
                else:
                    failures.append(float(tt))
            except Exception:
                failures.append(float(tt))
        reported_failures = [f["time"] for f in reported["units"][name]["failures"]]
        require(failures == reported_failures, "INDEPENDENT_EMBEDDING_DOMAIN_SAMPLES", {"unit": name, "independent_failed": failures, "reported_failed": reported_failures})
        for failure in reported["units"][name]["failures"]:
            i = list(time).index(failure["time"])
            for resource, value in failure["retained_totals"].items():
                require(abs(totals[i, boundary.index(resource)] - value) <= 1e-8, "INDEPENDENT_EMBEDDING_TOTALS", name)
        checks[name] = {"independent_physical_samples": positive_count, "independent_unphysical_or_uncertified_samples": len(failures), "same_failed_times_as_report": True, "worst_root_balance_residual": worst_residual}
    return {"status": "INDEPENDENT_SOURCE_GENERATOR_DOMAIN_AUDIT_AGREES", "units": checks, "scope": "Sampled local stationary-total inversion; no reduced embedding and no global root-exclusion proof for positive-product samples."}


def coupled_reference(source, initial, parameters, modules):
    output = {}
    energy = {rid for module in modules.values() for rid in module["reactions"]}
    combined = {"reactions": {rid: r for module in modules.values() for rid, r in module["reactions"].items()}}
    for folder in sorted((ROOT / "results/energy_cycles_v1/coupled_reference").glob("*")):
        if not (folder / "run_manifest.json").exists():
            continue
        manifest = json.loads((folder / "run_manifest.json").read_text())
        case_initial = manifest["initial_conditions"]
        check = {"overlay": overlay_check(folder / "derived_source_execution.xml", source, case_initial, parameters, energy)}
        with np.load(folder / "trajectories.npz", allow_pickle=False) as data:
            species = list(data["species_ids"])
            reactions = list(data["reaction_ids"])
            boundary = list(data["boundary_species"])
            require(set(reactions) == energy, "COUPLED_SOURCE_ALL87", folder.name)
            A = np.zeros((len(boundary), len(species)))
            for i, resource in enumerate(boundary):
                A[i, species.index(resource)] = 1
            enzyme_columns = set()
            for module in modules.values():
                local_boundary, composition = form_composition(module)
                states = enzyme_states(module)
                require(not enzyme_columns.intersection(states), "COUPLED_CATALYST_DUPLICATION", folder.name)
                enzyme_columns.update(states)
                for state in states:
                    for resource in local_boundary:
                        A[boundary.index(resource), species.index(state)] += float(composition[state][resource])
            require(np.array_equal(A, data["total_resource_map"]), "COUPLED_COMPLETE_SOURCE_RESOURCE_MAP", folder.name)
            x = data["microscopic"]
            require(np.array_equal(x[0], [case_initial[s] for s in species]), "COUPLED_INITIAL_VALUES", folder.name)
            rates = source_rates(combined, species, x, reactions)
            discrepancy = float(np.max(np.abs(rates - data["microscopic_source_flux"])))
            require(discrepancy <= 1e-9 * max(np.max(np.abs(rates)), 1), "COUPLED_SOURCE_ENERGY_RATES", folder.name)
            totals = x @ A.T
            require(np.max(np.abs(totals - data["retained_total_resource"])) <= 1e-8, "COUPLED_RETAINED_TOTALS", folder.name)
            bound = totals - x[:, [species.index(s) for s in boundary]]
            require(np.max(np.abs(bound - data["bound_resource"])) <= 1e-8, "COUPLED_BOUND_INVENTORIES", folder.name)
            net = data["net_matrix"]
            source_certificate = np.zeros_like(net)
            for j, (name, module) in enumerate(modules.items()):
                from independent_tests import certificate
                proof, pools = certificate(module)
                for resource, value in proof["oriented_net"].items():
                    source_certificate[boundary.index(resource), j] = float(value)
            require(np.array_equal(net, source_certificate), "COUPLED_SOURCE_NET_MATRIX", folder.name)
            extents = (np.linalg.pinv(net) @ (totals - totals[0]).T).T
            require(np.max(np.abs(extents - data["net_extent_from_pools"])) <= 1e-8, "COUPLED_SOURCE_NET_EXTENTS", folder.name)
            check.update(status="INDEPENDENT_COUPLED_SOURCE_REFERENCE_CHECK_PASS", max_canonical_energy_flux_discrepancy=discrepancy, no_shared_free_resource_or_catalyst_double_count=True)
        output[folder.name] = check
    return output


def main():
    source, initial, parameters, index, modules = read_sources()
    report = {"full_source_reference": full_reference(source, initial, parameters, modules), "coupled_source_reference": coupled_reference(source, initial, parameters, modules),
              "scope": "Source-reference chemistry/input/rate/ledger and stationary-graph domain audit only. Engine numerical import itself is checked by the execution manifest; independent XML and trajectory checks corroborate it without another engine run.",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    registration = json.loads((ROOT / "docs/reduction/energy_cycles/validation_preregistration.json").read_text())
    report.update(source_commit=registration["source_commit"], source_hashes=registration["source_hashes"],
                  environment={"python": sys.version, "numpy": np.__version__, "sympy": sy.__version__, "platform": platform.platform()},
                  command=[sys.executable, str(Path(__file__).resolve()), *sys.argv[1:]],
                  independent_parser_sha256=hashlib.sha256((ROOT / "scripts/energy_cycles/independent_tests.py").read_bytes()).hexdigest())
    path = ROOT / "results/energy_cycles_v1/source_reference_verification.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"full_source_status": report["full_source_reference"]["status"], "coupled_source_conditions": list(report["coupled_source_reference"])}))


if __name__ == "__main__":
    main()

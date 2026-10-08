"""Independent CHAIN_01 evidence verifier; never imports the trajectory runner.

Reconstructs exact stoichiometry and kinetics from canonical SBML/author CSV,
then compares saved trajectories to a sparse exponential-action solution.
Run after validate_chain01_four_step.py; writes independent_verification.json.
Scientific acceptance and numerical verification are deliberately separate.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply

IDS = ["re0000000014", "re0000000016", "re0000000017", "re0000000018"]
STATE_LABELS = ["x0", "x1", "x2", "x3", "x4", "xi14", "xi16", "xi17", "xi18"]
METRICS = ["product_trajectory", "product_flux", "pi_current", "pi_extent",
           "eftu_gdp_current", "eftu_gdp_extent", "occupancy"]
GROUPS = {"product_output": METRICS[:2], "resource_current": ["pi_current", "eftu_gdp_current"],
          "resource_extent": ["pi_extent", "eftu_gdp_extent"], "occupancy": ["occupancy"]}
THRESHOLD_KEYS = {"product_trajectory": ("product_output", "trajectory"),
                  "product_flux": ("product_output", "flux"),
                  "pi_current": ("resource_current", "pi"),
                  "eftu_gdp_current": ("resource_current", "eftu_gdp"),
                  "pi_extent": ("resource_extent", "pi"),
                  "eftu_gdp_extent": ("resource_extent", "eftu_gdp"),
                  "occupancy": ("occupancy", "uncompleted")}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def rational_math(node):
    tag = node.tag.rsplit("}", 1)[-1]
    if tag in ("math", "stoichiometryMath"):
        return rational_math(list(node)[0])
    if tag == "cn":
        return Fraction((node.text or "").strip())
    if tag == "apply":
        op = list(node)[0].tag.rsplit("}", 1)[-1]
        values = [rational_math(x) for x in list(node)[1:]]
        if op == "divide" and len(values) == 2:
            return values[0] / values[1]
        if op == "times":
            result = Fraction(1)
            for value in values:
                result *= value
            return result
        if op == "plus":
            return sum(values, Fraction(0))
    raise ValueError(f"Unrecognized exact stoichiometry expression: {tag}")


def source_model(root, config, manifest):
    tree = ET.parse(root / "models/pnas2017_full_reference/original/fMGG_synthesis.xml")
    reactions = {x.attrib["id"]: x for x in tree.findall(".//{*}reaction")}
    species = [x.attrib["id"] for x in tree.findall(".//{*}species")]
    with (root / config["parameter_source"]).open(encoding="utf-8-sig", newline="") as handle:
        overlay = {row["Name"]: Fraction(row["Value"]) for row in csv.DictReader(handle)}
    aliases = [manifest["species_aliases"][f"S{i}"] for i in range(5)]
    columns, rates = [], []
    for index, rid in enumerate(IDS):
        reaction = reactions[rid]
        column = {sid: Fraction(0) for sid in species}
        for role, sign in (("Reactants", -1), ("Products", 1)):
            for ref in reaction.findall(f"{{*}}listOf{role}/{{*}}speciesReference"):
                expression = ref.find("{*}stoichiometryMath")
                coefficient = rational_math(expression) if expression is not None else Fraction(ref.get("stoichiometry", "1"))
                column[ref.attrib["species"]] += sign * coefficient
        factors = [x.text.strip() for x in reaction.findall("{*}kineticLaw/{*}math/{*}apply/{*}ci")]
        assert sorted(factors) == sorted(["k1", aliases[index]]), (rid, factors)
        assert column[aliases[index]] == -1 and column[aliases[index + 1]] == 1
        rates.append(overlay[rid + "_k1"])
        columns.append(column)
    expected = {aliases[0]: -1, aliases[4]: 1, "PO4": 1, "EFTu_GDP": 1}
    assert all(sum(c[sid] for c in columns) == expected.get(sid, 0) for sid in species)
    assert len(species) == 241 and len(reactions) == 968
    assert rates == [Fraction(str(config["parameters"][key])) for key in ("k14", "k16", "k17", "k18")]
    internal = set(aliases[1:4])
    disabled_sides = []
    for rid, reaction in reactions.items():
        if rid in IDS:
            continue
        refs = {x.attrib["species"] for x in reaction.findall("{*}listOfReactants/{*}speciesReference") +
                reaction.findall("{*}listOfProducts/{*}speciesReference")}
        dependencies = {x.text.strip() for x in reaction.findall("{*}kineticLaw/{*}math/{*}apply/{*}ci")}
        if internal & (refs | dependencies):
            parameter_values = [overlay[rid + "_" + p.attrib["id"]]
                                for p in reaction.findall("{*}kineticLaw/{*}listOfParameters/{*}parameter")]
            assert parameter_values and any(value == 0 for value in parameter_values), rid
            disabled_sides.append(rid)
    matrix = np.zeros((11, 11))  # states, extents, cumulative input, constant
    for j, rate in enumerate(rates):
        for i, sid in enumerate(aliases):
            matrix[i, j] = float(columns[j][sid] * rate)
        matrix[5 + j, j] = float(rate)
    return rates, matrix, disabled_sides


def spans_for(test, tau, horizon):
    events = sorted({0.0, horizon, *[float(s[e]) * tau for s in test["input_segments"] for e in ("start_tau", "end_tau")]})
    spans = []
    for left, right in zip(events[:-1], events[1:]):
        midpoint = (left + right) / 2
        amplitude = sum(float(s["amplitude"]) for s in test["input_segments"]
                        if float(s["start_tau"]) * tau <= midpoint < float(s["end_tau"]) * tau)
        spans.append((left, right, amplitude))
    changes = [spans[i][0] for i in range(1, len(spans)) if spans[i][2] != spans[i - 1][2]]
    return spans, changes


def sparse_reference(base, initial, spans, times):
    """Exponential action uses Krylov/Taylor routines, distinct from dense expm."""
    result = np.empty((len(times), len(initial)))
    current = initial.copy()
    for left, right, amplitude in spans:
        matrix = base.copy()
        matrix[0, -1] = amplitude
        matrix[-2, -1] = amplitude
        sparse = csr_matrix(matrix)
        positions = np.flatnonzero((times >= left) & (times <= right))
        preceding = left
        p = 0
        # Group actual equal-spacing runs. Machine-neighbor duplicate grid
        # points are retained and propagated separately, never coalesced.
        while p < len(positions):
            index = positions[p]
            t = times[index]
            if t > preceding:
                current = expm_multiply(sparse * (t - preceding), current)
            result[index] = current
            preceding = t
            if p + 1 == len(positions):
                p += 1
                continue
            spacing = times[positions[p + 1]] - t
            q = p + 1
            while (q + 1 < len(positions) and spacing > 1e-14 and
                   abs((times[positions[q + 1]] - times[positions[q]]) - spacing) <= 1e-11 * spacing):
                q += 1
            if q > p + 1:
                sequence = expm_multiply(sparse, current, start=0,
                                        stop=times[positions[q]] - t, num=q - p + 1, endpoint=True)
                result[positions[p:q + 1]] = sequence
                current = sequence[-1]
                preceding = times[positions[q]]
                p = q + 1
            else:
                p += 1
        if right > preceding:
            current = expm_multiply(sparse * (right - preceding), current)
    return result


def compare(actual, expected, tolerance=1e-8):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape, (actual.shape, expected.shape)
    assert np.array_equal(np.isnan(actual), np.isnan(expected)), "Undefined-relative mask differs"
    finite = np.isfinite(expected)
    assert np.array_equal(np.isinf(actual), np.isinf(expected)), "Infinite relative values differ"
    maximum = float(np.max(np.abs(actual[finite] - expected[finite]))) if finite.any() else 0.0
    assert maximum <= tolerance, f"absolute discrepancy {maximum:g} exceeds {tolerance:g}"
    return maximum


def verify(root):
    output = root / "results/reduction/chain01_four_step"
    config = read_json(root / "configs/reduction/chain01_four_step_validation.json")
    freeze = read_json(output / "protocol_freeze.json")
    manifest = read_json(output / "source_manifest.json")
    summary = read_json(output / "validation_summary.json")
    assert digest(root / freeze["config_path"]) == freeze["config_sha256"] == summary["config_sha256"]
    assert freeze["frozen_before_first_numerical_run"] is True
    assert digest(output / "source_manifest.json") == freeze["source_manifest_sha256"]
    assert digest(output / "protected_files_before.json") == freeze["protected_snapshot_sha256"]
    assert digest(root / "scripts/reduction/audit_chain01_sources.py") == freeze["audit_script_sha256"]
    for source in freeze["source_files"]:
        assert digest(root / source["path"]) == source["sha256"], source["path"]
    protected = read_json(output / "protected_files_before.json")["files"]
    for path, record in protected.items():
        assert (root / path).is_file() and digest(root / path) == record["sha256"], path
    rates_exact, full_base, side_paths = source_model(root, config, manifest)
    rates = np.array([float(x) for x in rates_exact])
    exact_tau = sum((1 / x for x in rates_exact), Fraction(0))
    tau = float(summary["tau"])
    ke = float(1 / exact_tau)
    assert abs(tau - float(exact_tau)) <= 1e-15 and abs(summary["k_eff"] - ke) <= 1e-14
    variance = float(sum((1 / x ** 2 for x in rates_exact), Fraction(0)))
    dwell = summary["dwell"]
    compare(dwell["full_numeric_mean"], float(exact_tau), 1e-10)
    compare(dwell["full_numeric_variance"], variance, 1e-10)
    compare(dwell["reduced_analytic_variance"], float(exact_tau ** 2), 1e-14)
    # Independently integrate survival and its nested integral as linear
    # coordinates, then restore the exact finite-horizon residual moments.
    horizon = config["sampling"]["end_tau"] * tau
    moments_generator = np.zeros((7, 7))
    moments_generator[:5, :5] = full_base[:5, :5]
    moments_generator[5, :4] = 1.
    moments_generator[6, 5] = 1.
    pulse_moments = expm_multiply(csr_matrix(moments_generator * horizon), np.array([1., 0., 0., 0., 0., 0., 0.]))
    remaining_means = np.array([sum(1 / rates[j:]) for j in range(4)])
    remaining_seconds = np.array([remaining_means[j] ** 2 + sum(1 / rates[j:] ** 2) for j in range(4)])
    tail_mean = pulse_moments[:4] @ remaining_means
    independent_mean = pulse_moments[5] + tail_mean
    independent_second = (2 * (horizon * pulse_moments[5] - pulse_moments[6]) +
                          2 * horizon * tail_mean + pulse_moments[:4] @ remaining_seconds)
    independent_variance = independent_second - independent_mean ** 2
    compare(independent_mean, float(exact_tau), 1e-10)
    compare(independent_variance, variance, 1e-10)
    direct_moment_matrix = np.array([[-ke, 0, 0], [1., 0, 0], [0, 1., 0]])
    direct_moments = expm_multiply(csr_matrix(direct_moment_matrix * horizon), np.array([1., 0., 0.]))
    direct_mean = direct_moments[1] + direct_moments[0] / ke
    direct_second = (2 * (horizon * direct_moments[1] - direct_moments[2]) +
                     direct_moments[0] * (2 * horizon / ke + 2 / ke ** 2))
    compare(direct_mean, float(exact_tau), 1e-10)
    compare(direct_second - direct_mean ** 2, float(exact_tau ** 2), 1e-10)
    reduced_base = np.zeros((5, 5))
    reduced_base[0, 0] = -ke
    reduced_base[1:3, 0] = ke
    results = {}
    in_domain_entire_statuses = []
    all_events = {float(s[e]) * tau for test in config["tests"].values()
                  for s in test["input_segments"] for e in ("start_tau", "end_tau")}
    prospective = np.unique(np.concatenate([
        *[np.linspace(float(i["start_tau"]) * tau, float(i["end_tau"]) * tau, int(i["count"])) for i in config["sampling"]["intervals"]],
        np.array(config["sampling"]["extra_times_tau"]) * tau,
        np.array(sorted(all_events))]))
    for name, test in config["tests"].items():
        data = np.genfromtxt(output / "numerical_results" / f"test_{name}.csv", delimiter=",", names=True)
        error = np.genfromtxt(output / "error_tables" / f"test_{name}_errors.csv", delimiter=",", names=True)
        times = data["t"]
        compare(times, prospective, 1e-14)
        compare(error["t"], times, 0)
        compare(data["t_over_tau"], times / tau, 1e-14)
        spans, events = spans_for(test, tau, config["sampling"]["end_tau"] * tau)
        full_initial = np.r_[test["initial_full"], np.zeros(5), 1.]
        reduced_initial = np.r_[test["initial_reduced"], 0., 0., 1.]
        full = sparse_reference(full_base, full_initial, spans, times)
        reduced = sparse_reference(reduced_base, reduced_initial, spans, times)
        full_max = compare(np.column_stack([data["primary_full_" + s] for s in STATE_LABELS]), full[:, :9])
        reduced_max = compare(np.column_stack([data["primary_reduced_" + s] for s in ("y0", "y4", "xi_eff")]), reduced[:, :3])
        primary_full = np.column_stack([data["primary_full_" + s] for s in STATE_LABELS])
        primary_reduced = np.column_stack([data["primary_reduced_" + s] for s in ("y0", "y4", "xi_eff")])
        convergence = max(compare(primary_full, np.column_stack([data["tight_full_" + s] for s in STATE_LABELS]),
                                  config["gates"]["numerical"]["convergence_absolute"]),
                          compare(primary_reduced, np.column_stack([data["tight_reduced_" + s] for s in ("y0", "y4", "xi_eff")]),
                                  config["gates"]["numerical"]["convergence_absolute"]))
        assert min(float(primary_full.min()), float(primary_reduced.min())) >= -config["gates"]["numerical"]["negative_state_absolute"]
        assert summary["tests"][name]["numerical_status"] == "PASS"
        amount_scale = float(test.get("amount_scale", tau))
        current_scale = float(test.get("current_scale", 1 / tau))
        x = np.column_stack([data["primary_full_x" + str(i)] for i in range(5)])
        extents = np.column_stack([data["primary_full_" + s] for s in STATE_LABELS[5:]])
        y = np.column_stack([data["primary_reduced_" + s] for s in ("y0", "y4", "xi_eff")])
        integral = np.zeros(len(times))
        inlet_right, inlet_left = np.zeros(len(times)), np.zeros(len(times))
        for segment in test["input_segments"]:
            left, right, u = float(segment["start_tau"]) * tau, float(segment["end_tau"]) * tau, float(segment["amplitude"])
            integral += u * np.maximum(0, np.minimum(times, right) - left)
            inlet_right += u * ((times >= left) & (times < right))
            inlet_left += u * ((times > left) & (times <= right))
        # The frozen horizon has no pre-t0 interval. The runner reports its
        # declared inlet value as the initial left-limit convention.
        inlet_left[times == 0] = inlet_right[times == 0]
        compare(data["exact_input_integral"], integral, 1e-14)
        compare(data["input_right"], inlet_right, 0)
        compare(data["input_left"], inlet_left, 0)
        initial = np.array(test["initial_full"])
        residues = [x.sum(axis=1) - initial.sum() - integral,
                    y[:, :2].sum(axis=1) - sum(test["initial_reduced"]) - integral,
                    extents[:, 0] - extents[:, 3] - (x[:, 1:4] - initial[1:4]).sum(axis=1),
                    extents[:, 1] - extents[:, 3] - (x[:, 2:4] - initial[2:4]).sum(axis=1),
                    extents[:, 2] - extents[:, 3] - x[:, 3] + initial[3],
                    extents[:, 1] + x[:, 0] + x[:, 1] - initial[0] - initial[1] - integral,
                    extents[:, 2] + x[:, :3].sum(axis=1) - initial[:3].sum() - integral]
        invariant_max = max(compare(r, np.zeros(len(times))) for r in residues)
        reference = {"product_trajectory": x[:, 4], "product_flux": rates[3] * x[:, 3],
                     "pi_current": rates[1] * x[:, 1], "pi_extent": extents[:, 1],
                     "eftu_gdp_current": rates[2] * x[:, 2], "eftu_gdp_extent": extents[:, 2],
                     "occupancy": x[:, :4].sum(axis=1)}
        candidate = {"product_trajectory": y[:, 1], "pi_extent": y[:, 2], "eftu_gdp_extent": y[:, 2], "occupancy": y[:, 0],
                     "product_flux": ke * y[:, 0], "pi_current": ke * y[:, 0], "eftu_gdp_current": ke * y[:, 0]}
        descriptions = {"hidden_inventory": (x[:, 1:4].sum(axis=1), np.zeros(len(times))),
                        "bound_pi": (x[:, 1], np.zeros(len(times))),
                        "bound_eftu_gdp": (x[:, 1] + x[:, 2], np.zeros(len(times))),
                        "bound_gtp": (x[:, 0], y[:, 0])}
        for description, (reference_value, candidate_value) in descriptions.items():
            compare(data["full_" + description], reference_value, 1e-12)
            compare(data["direct_" + description], candidate_value, 1e-12)
        if "hidden_inventory_signed" in error.dtype.names:
            hidden_ref = descriptions["hidden_inventory"][0]
            hidden_signed = -hidden_ref
            compare(error["hidden_inventory_signed"], hidden_signed, 1e-12)
            compare(error["hidden_inventory_absolute"], np.abs(hidden_signed), 1e-12)
            compare(error["hidden_inventory_normalized_signed"], hidden_signed / amount_scale, 1e-12)
            compare(error["hidden_inventory_normalized_absolute"], np.abs(hidden_signed) / amount_scale, 1e-12)
            hidden_relative = np.where(hidden_ref != 0, -1., np.nan)
            compare(error["hidden_inventory_relative_signed_defined"], hidden_relative, 0)
            compare(error["hidden_inventory_relative_absolute_defined"], np.abs(hidden_relative), 0)
        transient = times <= config["windows"]["initial_layer_end_tau"] * tau
        for event in events:
            transient |= (times >= event) & (times <= event + config["windows"]["input_switch_duration_tau"] * tau)
        windows = {"entire": np.ones(len(times), dtype=bool), "transient": transient,
                   "post_transient": ~transient & (times > config["windows"]["post_transient_start_tau"] * tau),
                   "late": times >= config["windows"]["late_window_start_tau"] * tau}
        for window, mask in windows.items():
            if "in_" + window in error.dtype.names:
                compare(error["in_" + window], mask.astype(int), 0)
        max_error_table_residual = 0.
        gate_results = {}
        for metric in METRICS:
            compare(data["full_" + metric], reference[metric], 1e-10)
            compare(data["direct_" + metric], candidate[metric], 1e-10)
            scale = current_scale if metric.endswith(("flux", "current")) else amount_scale
            signed = candidate[metric] - reference[metric]
            relative = np.full(len(times), np.nan)
            nonzero = reference[metric] != 0
            with np.errstate(over="ignore", invalid="ignore"):
                relative[nonzero] = signed[nonzero] / np.abs(reference[metric][nonzero])
            values = {"signed": signed, "absolute": np.abs(signed), "normalized_signed": signed / scale,
                      "normalized_absolute": np.abs(signed) / scale, "relative_signed_defined": relative,
                      "relative_absolute_defined": np.abs(relative)}
            for suffix, value in values.items():
                residual = compare(error[metric + "_" + suffix], value,
                                   1e-11 if "relative" not in suffix else np.inf)
                # Extremely large relative errors retain their raw value;
                # compare fractionally without changing gate denominators.
                if "relative" in suffix:
                    finite = np.isfinite(value)
                    np.testing.assert_allclose(error[metric + "_" + suffix][finite], value[finite], rtol=1e-11, atol=1e-11)
                else:
                    max_error_table_residual = max(max_error_table_residual, residual)
            group, key = THRESHOLD_KEYS[metric]
            for window, mask in windows.items():
                entry = summary["tests"][name]["metrics"][window][metric]
                max_abs = float(np.max(np.abs(signed[mask])))
                compare(entry["max_absolute"], max_abs, 1e-10)
                compare(entry["max_normalized"], max_abs / scale, 1e-10)
                indices = np.flatnonzero(mask)
                components = np.split(indices, np.flatnonzero(np.diff(indices) > 1) + 1)
                duration = sum(times[c[-1]] - times[c[0]] for c in components if len(c) > 1)
                squared_integral = sum(np.trapz((signed[c] / scale) ** 2, times[c]) for c in components if len(c) > 1)
                rms = np.sqrt(squared_integral / duration)
                compare(entry["rms_normalized"], rms, 1e-10)
                limit = config["gates"][group][key]
                expected_status = "PASS" if max_abs / scale <= limit else "FAIL"
                actual = summary["tests"][name]["gates"][window][group]["metrics"][metric]
                assert actual["status"] == expected_status
                compare(actual["threshold"], limit, 0)
                gate_results[(window, metric)] = expected_status
                for factor in config["sensitivity"]["threshold_factors"]:
                    sensitive = summary["tests"][name]["threshold_sensitivity"][str(factor)][window][group]["metrics"][metric]
                    assert sensitive["status"] == ("PASS" if max_abs / scale <= limit * factor else "FAIL")
                    compare(sensitive["threshold"], limit * factor, 0)
        for window in windows:
            for group, metrics in GROUPS.items():
                expected = "PASS" if all(gate_results[(window, m)] == "PASS" for m in metrics) else "FAIL"
                assert summary["tests"][name]["gates"][window][group]["status"] == expected
                if window == "entire" and test["domain_status"] == "IN_DOMAIN":
                    in_domain_entire_statuses.append(expected)
        if events:
            event_data = np.genfromtxt(output / "numerical_results" / f"test_{name}_event_limits.csv", delimiter=",", names=True, dtype=None, encoding="utf-8")
            assert len(event_data) == 2 * len(events)
        assert summary["tests"][name]["domain_status"] == test["domain_status"]
        if name == "D":
            assert test["initial_reduced"][0] == sum(test["initial_full"][:4])
        results[name] = {"status": "PASS", "sparse_action_full_max_absolute": full_max,
                         "sparse_action_reduced_max_absolute": reduced_max, "invariant_max_absolute": invariant_max,
                         "independently_checked_convergence_max_absolute": convergence,
                         "raw_error_table_max_absolute_discrepancy": max_error_table_residual,
                         "sample_count": len(times), "event_count": len(events)}
    compare(summary["test_A_initial_product_current"]["full"], 0, 0)
    compare(summary["test_A_initial_product_current"]["reduced"], ke, 1e-14)
    expected_screen = ("LOCAL_CANDIDATE_PASSED_REGISTERED_SCREEN" if
                       all(status == "PASS" for status in in_domain_entire_statuses) else
                       "LOCAL_CANDIDATE_FAILED_REGISTERED_SCREEN")
    assert summary["status"] == expected_screen
    return {"status": "PASS", "method": "Independent exact XML/Fraction and CSV audit; sparse scipy.sparse.linalg.expm_multiply; independent raw metric/mask/RMS/gate reconstruction",
            "runner_imported": False, "config_sha256": freeze["config_sha256"], "protected_file_count": len(protected),
            "internal_zero_side_path_count": len(side_paths), "stoichiometry_species_compared": 241,
            "tau_exact": str(exact_tau), "effective_rate_exact": str(1 / exact_tau), "waiting_variance_full": variance,
            "waiting_variance_direct": float(exact_tau ** 2),
            "independent_sparse_moments": {"full_mean": independent_mean, "full_variance": independent_variance,
                                           "direct_mean": direct_mean, "direct_variance": direct_second - direct_mean ** 2},
            "tests": results,
            "scientific_screen_status": summary["status"], "numerical_PASS_does_not_grant_scientific_approval": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    destination = args.repo / "results/reduction/chain01_four_step/independent_verification.json"
    try:
        report = verify(args.repo)
    except Exception as exc:
        report = {"status": "FAIL", "error_type": type(exc).__name__, "error": str(exc),
                  "scientific_approval": "NOT_GRANTED"}
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False))
        raise
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

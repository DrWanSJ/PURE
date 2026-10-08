"""Frozen local CHAIN_01 experiment; no fitting or full-network simulation.

Primary and tighter segmented Radau solves are independently compared with an
augmented matrix exponential. Discontinuous inputs never cross a solver segment.
The source audit and frozen experiment JSON must exist before main() runs.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import platform
import sys
import traceback
from pathlib import Path
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.integrate import quad, solve_ivp
from scipy.linalg import expm

RATE_KEYS = ("k14", "k16", "k17", "k18")
METRICS = ("product_trajectory", "product_flux", "pi_current", "pi_extent",
           "eftu_gdp_current", "eftu_gdp_extent", "occupancy", "hidden_inventory")
GROUPS = {"product_output": ("product_trajectory", "product_flux"),
          "resource_current": ("pi_current", "eftu_gdp_current"),
          "resource_extent": ("pi_extent", "eftu_gdp_extent"),
          "occupancy": ("occupancy",)}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_write(path, obj):
    def sanitize(v):
        if isinstance(v, dict):
            return {str(k): sanitize(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [sanitize(x) for x in v]
        if isinstance(v, np.ndarray):
            return sanitize(v.tolist())
        if isinstance(v, (np.floating, float)):
            return float(v) if np.isfinite(v) else None
        if isinstance(v, np.integer):
            return int(v)
        if isinstance(v, np.bool_):
            return bool(v)
        return v
    Path(path).write_text(json.dumps(sanitize(obj), indent=2, ensure_ascii=False,
                                   allow_nan=False) + "\n", encoding="utf-8")


def write_csv(path, columns, arrays):
    with Path(path).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for row in zip(*arrays):
            writer.writerow([format(float(x), ".17g") if isinstance(x, (float, np.floating))
                             else x for x in row])


def effective_rate(rates):
    rates = np.asarray(rates, dtype=float)
    if rates.shape != (4,) or np.any(rates <= 0):
        raise ValueError("Exactly four strictly positive author rates are required")
    tau = float(np.sum(1 / rates))
    return 1 / tau, tau


def full_matrix(rates):
    """[x0..x4, xi14..xi18], with a linear extents block."""
    matrix = np.zeros((9, 9))
    for index, rate in enumerate(rates):
        matrix[index, index] = -rate
        matrix[index + 1, index] = rate
        matrix[index + 5, index] = rate
    return matrix


def reduced_matrix(k_eff):
    matrix = np.zeros((3, 3))
    matrix[0, 0] = -k_eff
    matrix[1, 0] = k_eff
    matrix[2, 0] = k_eff
    return matrix


def input_segments(test, tau, end):
    """Canonical disjoint piecewise-constant spans, including zero gaps."""
    source = test.get("input_segments", [])
    segments = []
    for entry in source:
        a = float(entry.get("start", entry.get("start_tau", 0) * tau))
        b = float(entry.get("end", entry.get("end_tau", end / tau) * tau))
        amp = float(entry.get("amplitude", entry.get("value", 0)))
        if amp < 0 or a < 0 or b <= a or b > end + 1e-12:
            raise ValueError("Input spans must be nonnegative and inside the fixed horizon")
        segments.append((a, min(b, end), amp))
    segments.sort()
    for previous, current in zip(segments, segments[1:]):
        if current[0] < previous[1]:
            raise ValueError("Input spans must not overlap")
    boundaries = sorted(set([0.0, end] + [v for a, b, _ in segments for v in (a, b)]))
    spans = []
    for a, b in zip(boundaries, boundaries[1:]):
        midpoint = (a + b) / 2
        amplitude = sum(amp for lo, hi, amp in segments if lo <= midpoint < hi)
        spans.append((a, b, amplitude))
    return spans


def input_value(times, spans, side="right"):
    times = np.atleast_1d(times)
    result = np.zeros(times.shape)
    for lo, hi, amplitude in spans:
        mask = ((times >= lo) & (times < hi)) if side == "right" else ((times > lo) & (times <= hi))
        result[mask] = amplitude
    if side == "left":
        result[times == 0] = spans[0][2]
    return result


def exact_input_integral(times, spans):
    times = np.asarray(times)
    result = np.zeros_like(times, dtype=float)
    for lo, hi, amplitude in spans:
        result += amplitude * np.maximum(0, np.minimum(times, hi) - lo)
    return result


def sampling_times(sampling, tau, spans_by_test):
    points = [0.0]
    for item in sampling["intervals"]:
        lo = float(item.get("start", item.get("start_tau", 0) * tau))
        hi = float(item.get("end", item.get("end_tau", 0) * tau))
        count = int(item["count"])
        if count < 2 or hi <= lo:
            raise ValueError("Each fixed sampling interval requires at least two points")
        points.extend(np.linspace(lo, hi, count))
    points.extend(float(x) * tau for x in sampling.get("extra_times_tau", []))
    points.extend(float(x) for x in sampling.get("extra_times", []))
    points.extend(v for spans in spans_by_test.values() for lo, hi, _ in spans for v in (lo, hi))
    times = np.unique(np.array(points))
    if np.any(times < 0):
        raise ValueError("Negative sampling time")
    return times


def initial_vectors(test):
    full = np.array(test["initial_full"], dtype=float)
    reduced = np.array(test["initial_reduced"], dtype=float)
    if full.shape != (5,) or reduced.shape != (2,) or np.any(full < 0) or np.any(reduced < 0):
        raise ValueError("Initial state shape/nonnegativity error")
    if not np.isclose(np.sum(full), np.sum(reduced), atol=1e-15, rtol=0):
        raise ValueError("The initial inventory must be retained by the declared mapping")
    return np.r_[full, np.zeros(4)], np.r_[reduced, 0.0]


def segmented_ode(matrix, initial, spans, times, solver):
    state = initial.copy()
    output = np.full((len(initial), len(times)), np.nan)
    output[:, times == 0] = initial[:, None]
    records = []
    for lo, hi, amplitude in spans:
        forcing = np.zeros(len(initial))
        forcing[0] = amplitude
        began = perf_counter()
        result = solve_ivp(lambda t, z: matrix @ z + forcing, (lo, hi), state,
                           method=solver.get("method", "Radau"),
                           rtol=float(solver["rtol"]), atol=float(solver["atol"]),
                           jac=matrix, dense_output=True)
        elapsed = perf_counter() - began
        records.append({"start": lo, "end": hi, "input": amplitude,
                        "status": int(result.status), "success": bool(result.success),
                        "message": result.message, "nfev": result.nfev, "njev": result.njev,
                        "nlu": result.nlu, "internal_mesh_points": len(result.t),
                        "elapsed_seconds": elapsed})
        if not result.success or result.t[-1] != hi:
            raise RuntimeError("Segment did not reach the registered endpoint: " + result.message)
        mask = (times > lo) & (times <= hi)
        output[:, mask] = result.sol(times[mask])
        state = result.y[:, -1]
    if not np.all(np.isfinite(output)):
        raise RuntimeError("Nonfinite or missing ODE output")
    return output, records


def segmented_expm(matrix, initial, spans, times):
    """Independent constant/input-integral augmentation, not solver interpolation."""
    dimension = len(initial)
    augmented_state = np.r_[initial, 0.0, 1.0]
    output = np.full((dimension + 1, len(times)), np.nan)
    output[:, times == 0] = augmented_state[:-1, None]
    for lo, hi, amplitude in spans:
        augmented = np.zeros((dimension + 2, dimension + 2))
        augmented[:dimension, :dimension] = matrix
        augmented[0, -1] = amplitude
        augmented[dimension, -1] = amplitude
        selected = np.flatnonzero((times > lo) & (times <= hi))
        for index in selected:
            output[:, index] = (expm(augmented * (times[index] - lo)) @ augmented_state)[:-1]
        augmented_state = expm(augmented * (hi - lo)) @ augmented_state
    if not np.all(np.isfinite(output)):
        raise RuntimeError("Nonfinite matrix exponential output")
    return output[:dimension], output[dimension]


def observables(full, reduced, rates, k_eff):
    x = full[:5]
    xi = full[5:]
    current = rates[:, None] * x[:4]
    direct = k_eff * reduced[0]
    ref = {"product_trajectory": x[4], "product_flux": current[3],
           "pi_current": current[1], "pi_extent": xi[1],
           "eftu_gdp_current": current[2], "eftu_gdp_extent": xi[2],
           "occupancy": np.sum(x[:4], axis=0), "hidden_inventory": np.sum(x[1:4], axis=0),
           "bound_pi": x[1], "bound_eftu_gdp": x[1] + x[2], "bound_gtp": x[0]}
    candidate = {"product_trajectory": reduced[1], "product_flux": direct,
                 "pi_current": direct, "pi_extent": reduced[2],
                 "eftu_gdp_current": direct, "eftu_gdp_extent": reduced[2],
                 "occupancy": reduced[0], "hidden_inventory": np.zeros(len(direct)),
                 "bound_pi": np.zeros(len(direct)), "bound_eftu_gdp": np.zeros(len(direct)),
                 "bound_gtp": reduced[0]}
    return ref, candidate


def invariant_residuals(full, reduced, initial_full, initial_reduced, integral):
    x = full[:5]
    xi = full[5:]
    z = initial_full[:5]
    residues = {
        "full_inventory": np.sum(x, axis=0) - np.sum(z) - integral,
        "reduced_inventory": reduced[0] + reduced[1] - np.sum(initial_reduced[:2]) - integral,
        "xi14_minus_xi18_internal": xi[0] - xi[3] - np.sum(x[1:4] - z[1:4, None], axis=0),
        "xi16_minus_xi18_x2x3": xi[1] - xi[3] - np.sum(x[2:4] - z[2:4, None], axis=0),
        "xi17_minus_xi18_x3": xi[2] - xi[3] - (x[3] - z[3]),
        "x4_from_xi18": x[4] - z[4] - xi[3],
        "x0_gtp_from_input_hydrolysis": x[0] - z[0] - integral + xi[0],
        "pi_free_plus_bound_hydrolysis": xi[1] + x[1] - z[1] - xi[0],
        "gdp_free_plus_bound_hydrolysis": xi[2] + x[1] + x[2] - z[1] - z[2] - xi[0],
        "eftu_total_free_plus_bound": xi[2] + np.sum(x[:3], axis=0) - np.sum(z[:3]) - integral,
        "direct_y4_from_extent": reduced[1] - initial_reduced[1] - reduced[2],
    }
    return residues


def declared_windows(times, spans, window_config, tau):
    initial_end = float(window_config["initial_layer_end_tau"]) * tau
    width = float(window_config["input_switch_duration_tau"]) * tau
    post_start = float(window_config["post_transient_start_tau"]) * tau
    events = [spans[i][0] for i in range(1, len(spans)) if spans[i][2] != spans[i - 1][2]]
    transient = times <= initial_end
    for event in events:
        transient |= (times >= event) & (times <= event + width)
    post = (times > post_start) & ~transient
    late = times >= float(window_config["late_window_start_tau"]) * tau
    return {"entire": np.ones(len(times), dtype=bool),
            "transient": transient, "post_transient": post, "late": late}, events


def scale_for(metric, test, tau):
    is_current = metric.endswith("flux") or metric.endswith("current")
    value = test.get("current_scale" if is_current else "amount_scale")
    if value is None:
        rule = test.get("current_scale_rule" if is_current else "amount_scale_rule")
        value = {"tau": tau, "1/tau": 1 / tau}[rule]
    value = float(value)
    if value <= 0:
        raise ValueError("Predeclared normalization scales must be strictly positive")
    return value


def summarize_error(times, reference, candidate, mask, scale):
    indexes = np.flatnonzero(mask)
    if len(indexes) == 0:
        return {"status": "EMPTY_WINDOW", "sample_count": 0}
    signed = candidate[indexes] - reference[indexes]
    absolute = np.abs(signed)
    nonzero = reference[indexes] != 0
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        relative = np.divide(absolute, np.abs(reference[indexes]),
                             out=np.full(len(indexes), np.nan), where=nonzero)
    peak_index = int(indexes[int(np.argmax(absolute))])
    # Integrate each contiguous registered window separately; excluded gaps are
    # not bridged by a trapezoid and never count as post-transient time.
    chunks = np.split(indexes, np.flatnonzero(np.diff(indexes) > 1) + 1)
    area = sum(float(np.trapz(np.abs(candidate[c] - reference[c]), times[c]))
               for c in chunks if len(c) > 1)
    squared_area = sum(float(np.trapz((candidate[c] - reference[c]) ** 2, times[c]))
                       for c in chunks if len(c) > 1)
    duration = sum(float(times[c[-1]] - times[c[0]]) for c in chunks if len(c) > 1)
    return {"status": "COMPUTED", "sample_count": len(indexes),
            "start": float(times[indexes[0]]), "end": float(times[indexes[-1]]),
            "max_absolute": float(np.max(absolute)), "max_signed": float(np.max(signed)),
            "min_signed": float(np.min(signed)), "max_normalized": float(np.max(absolute) / scale),
            "rms_normalized": float(np.sqrt(squared_area / duration) / scale) if duration else None,
            "time_of_max_absolute": float(times[peak_index]),
            "max_relative_defined": ("Infinity (floating-point overflow; raw Inf retained)" if np.any(np.isinf(relative))
                                     else float(np.nanmax(relative))) if np.any(nonzero) else None,
            "max_relative_finite_defined": float(np.max(relative[np.isfinite(relative)])) if np.any(np.isfinite(relative)) else None,
            "relative_overflow_count": int(np.sum(np.isinf(relative))),
            "relative_undefined_count": int(np.sum(~nonzero)),
            "relative_denominator_rule": "abs(reference) exactly nonzero; otherwise NaN; no clipping",
            "reference_min": float(np.min(reference[indexes])),
            "reference_max": float(np.max(reference[indexes])),
            "l1_absolute_integral": area, "window_sampled_duration": duration,
            "normalization_scale": scale}


def threshold_for(metric, gates):
    if "metric_thresholds" in gates:
        return float(gates["metric_thresholds"][metric])
    for group, names in GROUPS.items():
        if metric in names:
            group_gate = gates[group]
            if isinstance(group_gate, (int, float)):
                return float(group_gate)
            if metric in group_gate:
                return float(group_gate[metric])
            short = {"product_trajectory": "trajectory", "product_flux": "flux",
                     "pi_current": "pi", "pi_extent": "pi", "eftu_gdp_current": "eftu_gdp",
                     "eftu_gdp_extent": "eftu_gdp", "occupancy": "uncompleted"}[metric]
            return float(group_gate.get(short, group_gate.get("max_normalized")))
    return None


def screen_metrics(metrics, gates, factor=1):
    result = {}
    for group, names in GROUPS.items():
        details = {}
        for metric in names:
            threshold = threshold_for(metric, gates) * factor
            value = metrics[metric].get("max_normalized")
            details[metric] = {"value": value, "threshold": threshold,
                               "status": "UNRESOLVED" if value is None else ("PASS" if value <= threshold else "FAIL")}
        statuses = [entry["status"] for entry in details.values()]
        result[group] = {"status": "UNRESOLVED" if "UNRESOLVED" in statuses else
                        ("PASS" if all(x == "PASS" for x in statuses) else "FAIL"), "metrics": details}
    return result


def dwell_validation(rates, tau, k_eff, quadrature):
    generator = full_matrix(rates)[:4, :4]
    initial = np.array([1., 0, 0, 0])
    cutoff = 10 * tau
    survival = lambda t: float(np.sum(expm(generator * t) @ initial))
    epsabs = float(quadrature["moment_quadrature_epsabs"])
    epsrel = float(quadrature["moment_quadrature_epsrel"])
    first, first_error = quad(survival, 0, cutoff, epsabs=epsabs, epsrel=epsrel, limit=250)
    second_half, second_error = quad(lambda t: t * survival(t), 0, cutoff,
                                    epsabs=epsabs, epsrel=epsrel, limit=250)
    cutoff_state = expm(generator * cutoff) @ initial
    remaining_time = np.linalg.solve(-generator, cutoff_state)
    tail_first = float(np.sum(remaining_time))
    tail_second_half = cutoff * tail_first + float(np.sum(np.linalg.solve(-generator, remaining_time)))
    numeric_mean = first + tail_first
    numeric_second = 2 * (second_half + tail_second_half)
    numeric_variance = numeric_second - numeric_mean ** 2
    direct_survival = lambda t: np.exp(-k_eff * t)
    direct_first, direct_first_error = quad(direct_survival, 0, cutoff, epsabs=epsabs, epsrel=epsrel)
    direct_half_second, direct_second_error = quad(lambda t: t * direct_survival(t), 0, cutoff,
                                                 epsabs=epsabs, epsrel=epsrel)
    direct_tail = np.exp(-k_eff * cutoff)
    direct_numeric_mean = direct_first + direct_tail / k_eff
    direct_numeric_second = 2 * direct_half_second + direct_tail * (2 * cutoff / k_eff + 2 / k_eff ** 2)
    direct_numeric_variance = direct_numeric_second - direct_numeric_mean ** 2
    variance = float(np.sum(1 / rates ** 2))
    return {"candidate_label": "MEAN_DWELL_MATCHED_CANDIDATE", "exact_markov_lumping": False,
            "full_analytic_mean": tau, "reduced_analytic_mean": 1 / k_eff,
            "full_analytic_variance": variance, "reduced_analytic_variance": 1 / k_eff ** 2,
            "full_numeric_mean": numeric_mean, "full_numeric_variance": numeric_variance,
            "reduced_numeric_mean": direct_numeric_mean, "reduced_numeric_variance": direct_numeric_variance,
            "mean_absolute_error": abs(numeric_mean - tau),
            "mean_relative_error": abs(numeric_mean - tau) / tau,
            "reduced_mean_absolute_error": abs(direct_numeric_mean - tau),
            "reduced_mean_relative_error": abs(direct_numeric_mean - tau) / tau,
            "variance_absolute_error": abs(numeric_variance - variance),
            "reduced_variance_absolute_error": abs(direct_numeric_variance - 1 / k_eff ** 2),
            "quadrature_cutoff": cutoff, "quadrature_cutoff_tau": 10,
            "quadrature_epsabs": epsabs, "quadrature_epsrel": epsrel,
            "tail_survival_probability": survival(cutoff), "mean_tail_correction": tail_first,
            "second_moment_tail_correction": 2 * tail_second_half,
            "reduced_mean_tail_correction": direct_tail / k_eff,
            "reduced_second_moment_tail_correction": direct_tail * (2 * cutoff / k_eff + 2 / k_eff ** 2),
            "quadrature_reported_absolute_error_mean": first_error,
            "quadrature_reported_absolute_error_half_second": second_error,
            "reduced_quadrature_reported_absolute_error_mean": direct_first_error,
            "reduced_quadrature_reported_absolute_error_half_second": direct_second_error,
            "numeric_method": "quad of independent expm survival + exact resolvent tail",
            "coefficient_variation_full": np.sqrt(variance) / tau,
            "coefficient_variation_reduced": 1.0,
            "slow_stage_mean_fraction": float((1 / rates[2]) / tau)}


def figure_caption():
    return ("Full four-step reference; Direct effective candidate (mean dwell matched)\n"
            "Time unit follows source model; rates extracted from author CSV overlay")


def make_figures(directory, runs, tau, config):
    plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.22})
    names = [("01_product_trajectory", "product_trajectory", "S4 accumulated"),
             ("02_product_flux", "product_flux", "S4 formation current"),
             ("03_pi_release_current", "pi_current", "Free Pi release current"),
             ("04_pi_release_extent", "pi_extent", "Free Pi released extent"),
             ("05_eftu_gdp_current", "eftu_gdp_current", "Free EF-Tu.GDP current"),
             ("06_eftu_gdp_extent", "eftu_gdp_extent", "Free EF-Tu.GDP extent"),
             ("07_internal_occupancy", "occupancy", "Uncompleted occupancy S0-S3 / y0")]
    zoom = float(config["sampling"].get("figure_early_end_tau", config["windows"]["initial_layer_end_tau"]))
    def zoom_axes(ax, name, run, series):
        lo, hi = 0.0, zoom
        if name == "C" and run["events"]:
            lo = run["events"][0] / tau
            hi = lo + float(config["windows"]["input_switch_duration_tau"])
        selected = (run["times"] / tau >= lo) & (run["times"] / tau <= hi)
        visible = np.concatenate([np.asarray(values)[selected] for values in series])
        low, high = float(np.min(visible)), float(np.max(visible))
        padding = max((high - low) * .06, max(abs(high), abs(low)) * .01, 1e-12)
        ax.set_xlim(lo, hi)
        ax.set_ylim(low - padding, high + padding)
        return "first input-switch zoom" if name == "C" else "early zoom"
    for filename, metric, ylabel in names:
        fig, axes = plt.subplots(4, 2, figsize=(12, 11), constrained_layout=True)
        for row, (name, run) in enumerate(runs.items()):
            for col in (0, 1):
                ax = axes[row, col]
                ax.plot(run["times"] / tau, run["ref"][metric], label="Full four-step reference", color="#176998")
                ax.plot(run["times"] / tau, run["candidate"][metric], "--", label="Direct effective candidate", color="#d15c24")
                if metric == "occupancy":
                    ax.plot(run["times"] / tau, run["ref"]["hidden_inventory"], ":", color="#45813a", label="Hidden S1-S3 inventory")
                for event in run["events"]:
                    ax.axvline(event / tau, color="grey", alpha=.5, linewidth=.7)
                series = [run["ref"][metric], run["candidate"][metric]]
                if metric == "occupancy":
                    series.append(run["ref"]["hidden_inventory"])
                panel = zoom_axes(ax, name, run, series) if col else "entire window"
                ax.set_title(f"Test {name}: {config['tests'][name].get('label', name)}; " + panel)
                ax.set_xlabel("t / tau (source model time unit)")
                ax.set_ylabel(ylabel)
                if row == 0 and col == 0:
                    ax.legend(fontsize=7)
        fig.suptitle(filename + "\n" + figure_caption(), fontsize=11)
        fig.savefig(directory / (filename + ".png"), dpi=170)
        plt.close(fig)
    fig, axes = plt.subplots(4, 2, figsize=(12, 11), constrained_layout=True)
    for row, (name, run) in enumerate(runs.items()):
        for col in (0, 1):
            ax = axes[row, col]
            series = []
            for metric in METRICS:
                normalized = np.abs(run["candidate"][metric] - run["ref"][metric]) / run["scales"][metric]
                ax.plot(run["times"] / tau, normalized, label=metric)
                series.append(normalized)
            panel = zoom_axes(ax, name, run, series) if col else "entire window"
            ax.set_title(f"Test {name}: " + panel)
            ax.set_xlabel("t / tau (source model time unit)")
            ax.set_ylabel("absolute error / registered scale")
            if row == 0 and col == 0:
                ax.legend(fontsize=6, ncol=2)
    fig.suptitle("08_normalized_errors\n" + figure_caption(), fontsize=11)
    fig.savefig(directory / "08_normalized_errors.png", dpi=170)
    plt.close(fig)
    c_run = runs["C"]
    a_run = runs["A"]
    fig, axes = plt.subplots(3, 2, figsize=(12, 10), constrained_layout=True)
    for col in (0, 1):
        for row, (run, title) in enumerate([(a_run, "A: initial pulse"), (c_run, "C: two rectangular pulses")]):
            ax = axes[row, col]
            for metric, color in [("product_flux", "#176998"), ("pi_current", "#45813a"), ("eftu_gdp_current", "#875eac")]:
                ax.plot(run["times"] / tau, run["ref"][metric], color=color, label="Full " + metric)
            ax.plot(run["times"] / tau, run["candidate"]["product_flux"], "--", color="#d15c24", label="Direct: all three currents")
            for event in run["events"]:
                ax.axvline(event / tau, color="grey", alpha=.5)
            if col:
                if row:
                    half = float(config["windows"]["input_switch_duration_tau"])
                    event = c_run["events"][0] / tau
                    ax.set_xlim(max(0, event - half), event + half)
                else:
                    ax.set_xlim(0, zoom)
            ax.set_title(title + ("; event/early zoom" if col else "; entire"))
            ax.set_xlabel("t / tau (source model time unit)")
            ax.set_ylabel("release / product current")
            ax.legend(fontsize=7)
        ax = axes[2, col]
        ax.step(c_run["times"] / tau, c_run["input_right"], where="post", label="C nonnegative input")
        for event in c_run["events"]:
            ax.axvline(event / tau, color="grey", alpha=.5)
        if col:
            event = c_run["events"][0] / tau
            half = float(config["windows"]["input_switch_duration_tau"])
            ax.set_xlim(max(0, event - half), event + half)
        ax.set_title("Declared C input (right-continuous)")
        ax.set_xlabel("t / tau (source model time unit)")
        ax.set_ylabel("input u")
    fig.suptitle("09_pulse_and_switch_responses\n" + figure_caption(), fontsize=11)
    fig.savefig(directory / "09_pulse_and_switch_responses.png", dpi=170)
    plt.close(fig)
    rows, data = [], []
    for name, run in runs.items():
        for metric in METRICS:
            rows.append(f"{name}: {metric}")
            data.append([run["metrics"][window][metric]["max_normalized"] for window in ("entire", "transient", "post_transient", "late")])
    fig, ax = plt.subplots(figsize=(10, 13), constrained_layout=True)
    values = np.array(data)
    # Linear colors preserve large failures; text contains each raw maximum.
    im = ax.imshow(values, aspect="auto", cmap="YlOrRd")
    ax.set_yticks(range(len(rows)), rows)
    ax.set_xticks(range(4), ["Entire window", "Initial / switch transient", "Post-transient", "Fixed late [5,10] tau"])
    for i in range(len(rows)):
        for j in range(4):
            ax.text(j, i, f"{values[i,j]:.4g}", ha="center", va="center", fontsize=7,
                    color="white" if values[i,j] > np.max(values) * .6 else "black")
    ax.grid(False)
    fig.colorbar(im, ax=ax, label="max |candidate - reference| / registered scale")
    fig.suptitle("10_model_comparison_summary\n" + figure_caption(), fontsize=11)
    fig.savefig(directory / "10_model_comparison_summary.png", dpi=170)
    plt.close(fig)


def run(config_path, freeze_path, source_path, output_path):
    config_path, freeze_path, source_path, output_path = map(Path, (config_path, freeze_path, source_path, output_path))
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    freeze = json.loads(freeze_path.read_text(encoding="utf-8-sig"))
    frozen_sha = freeze.get("config_sha256", freeze.get("sha256"))
    if frozen_sha != sha256(config_path):
        raise ValueError("Protocol SHA-256 does not match its pre-run frozen record")
    source = json.loads(source_path.read_text(encoding="utf-8-sig"))
    if source["audit_status"] != "PASSED_EXACT_SOURCE_AUDIT" or source["stoichiometry_exact"]["status"] != "PASS":
        raise ValueError("The exact source/stoichiometry audit has not passed")
    rates = np.array(source["author_rates"], dtype=float)
    if not np.array_equal(rates, np.array([config["parameters"][key] for key in RATE_KEYS], dtype=float)):
        raise ValueError("Configured rates differ from audited author CSV rates")
    if freeze.get("source_manifest_sha256") != sha256(source_path):
        raise ValueError("Source manifest differs from its pre-run frozen fingerprint")
    repo = config_path.resolve().parents[2]
    for entry in source["sources"]:
        if sha256(repo / entry["path"]) != entry["sha256"]:
            raise ValueError("Audited source bytes have changed: " + entry["path"])
    k_eff, tau = effective_rate(rates)
    end = float(config["sampling"]["end_tau"]) * tau
    spans_by_test = {name: input_segments(test, tau, end) for name, test in config["tests"].items()}
    times = sampling_times(config["sampling"], tau, spans_by_test)
    if times[-1] != end or times[0] != 0 or end < 10 * tau:
        raise ValueError("Sampling must cover exactly zero through at least ten dwell times")
    for subdirectory in ("numerical_results", "error_tables", "figures"):
        (output_path / subdirectory).mkdir(parents=True, exist_ok=True)
    json_write(output_path / "runtime_manifest.json", {"config_sha256": frozen_sha,
               "source_manifest_sha256": sha256(source_path), "runner_sha256": sha256(__file__),
               "python": sys.version, "platform": platform.platform(), "numpy": np.__version__,
               "scipy": scipy.__version__, "matplotlib": matplotlib.__version__,
               "candidate_label": "MEAN_DWELL_MATCHED_CANDIDATE",
               "formal_run_started_after_config_hash_check": True})
    primary_solver = {"method": config["solver"]["method"], "rtol": config["solver"]["rtol"], "atol": config["solver"]["atol"]}
    tight_solver = {"method": config["solver"]["convergence_method"], "rtol": config["solver"]["convergence_rtol"], "atol": config["solver"]["convergence_atol"]}
    numeric_gate = config["gates"]["numerical"]
    numeric_tolerance = float(numeric_gate["matrix_exponential_absolute"])
    convergence_tolerance = float(numeric_gate["convergence_absolute"])
    conservation_tolerance = float(numeric_gate["inventory_absolute"])
    ledger_tolerance = float(numeric_gate["ledger_absolute"])
    positivity_tolerance = float(numeric_gate["negative_state_absolute"])
    runs, summaries, verification = {}, {}, {}
    for name, test in config["tests"].items():
        began = perf_counter()
        spans = spans_by_test[name]
        zfull, zreduced = initial_vectors(test)
        fm, rm = full_matrix(rates), reduced_matrix(k_eff)
        full, full_records = segmented_ode(fm, zfull, spans, times, primary_solver)
        reduced, reduced_records = segmented_ode(rm, zreduced, spans, times, primary_solver)
        tight_full, tight_full_records = segmented_ode(fm, zfull, spans, times, tight_solver)
        tight_reduced, tight_reduced_records = segmented_ode(rm, zreduced, spans, times, tight_solver)
        exact_full, full_augmented_integral = segmented_expm(fm, zfull, spans, times)
        exact_reduced, reduced_augmented_integral = segmented_expm(rm, zreduced, spans, times)
        integral = exact_input_integral(times, spans)
        ref, candidate = observables(full, reduced, rates, k_eff)
        tight_ref, tight_candidate = observables(tight_full, tight_reduced, rates, k_eff)
        exact_ref, exact_candidate = observables(exact_full, exact_reduced, rates, k_eff)
        residuals = invariant_residuals(full, reduced, zfull, zreduced, integral)
        windows, events = declared_windows(times, spans, config["windows"], tau)
        scales = {metric: scale_for(metric, test, tau) for metric in METRICS}
        metrics = {window: {metric: summarize_error(times, ref[metric], candidate[metric], mask, scales[metric])
                            for metric in METRICS} for window, mask in windows.items()}
        gates = {window: screen_metrics(details, config["gates"]) for window, details in metrics.items()}
        sens_factors = config.get("sensitivity", {}).get("threshold_factors", [0.5, 1.0, 2.0])
        sensitivity = {str(factor): {window: screen_metrics(details, config["gates"], float(factor))
                                    for window, details in metrics.items()} for factor in sens_factors}
        domain_checks = {"zero_initial_internal": bool(np.sum(zfull[1:4]) == 0),
                         "internal_author_side_paths_zero": not source["domain_summary"]["internal_author_active_side_reactions"],
                         "exogenous_nonnegative_input": all(span[2] >= 0 for span in spans),
                         "no_S4_consumption": True, "declared_boundary_intervention": True}
        domain_gate = {"status": "PASS" if all(domain_checks.values()) else "FAIL",
                       "checks": domain_checks, "scope": "LOCAL_BOUNDARY_ONLY"}
        for window_gates in gates.values():
            window_gates["domain"] = domain_gate
        for factor_gates in sensitivity.values():
            for window_gates in factor_gates.values():
                window_gates["domain"] = domain_gate
        numerical_errors = {
            "primary_full_vs_expm_max_absolute": float(np.max(np.abs(full - exact_full))),
            "primary_reduced_vs_expm_max_absolute": float(np.max(np.abs(reduced - exact_reduced))),
            "tight_full_vs_expm_max_absolute": float(np.max(np.abs(tight_full - exact_full))),
            "tight_reduced_vs_expm_max_absolute": float(np.max(np.abs(tight_reduced - exact_reduced))),
            "primary_vs_tight_full_max_absolute": float(np.max(np.abs(full - tight_full))),
            "primary_vs_tight_reduced_max_absolute": float(np.max(np.abs(reduced - tight_reduced))),
            "augmented_full_input_integral_max_absolute": float(np.max(np.abs(full_augmented_integral - integral))),
            "augmented_reduced_input_integral_max_absolute": float(np.max(np.abs(reduced_augmented_integral - integral))),
        }
        current_errors = {metric: {"primary_full_vs_expm": float(np.max(np.abs(ref[metric] - exact_ref[metric]))),
                                  "primary_reduced_vs_expm": float(np.max(np.abs(candidate[metric] - exact_candidate[metric]))),
                                  "tight_full_vs_expm": float(np.max(np.abs(tight_ref[metric] - exact_ref[metric]))),
                                  "tight_reduced_vs_expm": float(np.max(np.abs(tight_candidate[metric] - exact_candidate[metric])))}
                          for metric in ("product_flux", "pi_current", "eftu_gdp_current")}
        residual_maxima = {key: float(np.max(np.abs(value))) for key, value in residuals.items()}
        convergence_full = numerical_errors["tight_full_vs_expm_max_absolute"] <= numerical_errors["primary_full_vs_expm_max_absolute"]
        convergence_reduced = numerical_errors["tight_reduced_vs_expm_max_absolute"] <= numerical_errors["primary_reduced_vs_expm_max_absolute"]
        current_pass = all(value <= numeric_tolerance for row in current_errors.values() for value in row.values())
        numeric_pass = (all(value <= (convergence_tolerance if "primary_vs_tight" in key else numeric_tolerance)
                            for key, value in numerical_errors.items()) and current_pass
                        and all(value <= (conservation_tolerance if "inventory" in key else ledger_tolerance)
                                for key, value in residual_maxima.items())
                        and min(np.min(full), np.min(reduced)) >= -positivity_tolerance
                        )
        verification[name] = {"status": "PASS" if numeric_pass else "FAIL", "solver_error": numerical_errors,
                              "derived_current_solver_error": current_errors, "invariant_max_absolute": residual_maxima,
                              "minimum_full": float(np.min(full)), "minimum_reduced": float(np.min(reduced)),
                              "tightening_convergence_full": convergence_full,
                              "tightening_convergence_reduced": convergence_reduced,
                              "solvers": {"primary": primary_solver, "tight": tight_solver,
                                          "independent": "augmented scipy.linalg.expm"},
                              "segments": {"primary_full": full_records, "primary_reduced": reduced_records,
                                           "tight_full": tight_full_records, "tight_reduced": tight_reduced_records}}
        summaries[name] = {"label": test.get("label", name), "domain_status": test.get("domain_status", "IN_DOMAIN"),
                           "initial_full": zfull[:5], "initial_reduced": zreduced[:2],
                           "domain_gate": domain_gate,
                           "input_spans": spans, "events": events, "metrics": metrics,
                           "gates": gates, "threshold_sensitivity": sensitivity,
                           "numerical_status": verification[name]["status"], "elapsed_seconds": perf_counter() - began,
                           "late_currents": {metric: {"full": float(ref[metric][-1]), "reduced": float(candidate[metric][-1])}
                                             for metric in ("product_flux", "pi_current", "eftu_gdp_current")},
                           "late_occupancy": {"full": float(ref["occupancy"][-1]), "reduced": float(candidate["occupancy"][-1])}}
        iright, ileft = input_value(times, spans), input_value(times, spans, "left")
        runs[name] = {"times": times, "ref": ref, "candidate": candidate, "input_right": iright,
                      "events": events, "metrics": metrics, "scales": scales}
        columns = ["t", "t_over_tau", "input_right", "input_left", "exact_input_integral"]
        arrays = [times, times / tau, iright, ileft, integral]
        state_labels = ["x0", "x1", "x2", "x3", "x4", "xi14", "xi16", "xi17", "xi18"]
        for prefix, output in [("primary_full", full), ("tight_full", tight_full), ("expm_full", exact_full)]:
            for label, values in zip(state_labels, output):
                columns.append(prefix + "_" + label)
                arrays.append(values)
        for prefix, output in [("primary_reduced", reduced), ("tight_reduced", tight_reduced), ("expm_reduced", exact_reduced)]:
            for label, values in zip(["y0", "y4", "xi_eff"], output):
                columns.append(prefix + "_" + label)
                arrays.append(values)
        for prefix, observed in [("full", ref), ("direct", candidate)]:
            for metric, values in observed.items():
                columns.append(prefix + "_" + metric)
                arrays.append(values)
        for key, values in residuals.items():
            columns.append("residual_" + key)
            arrays.append(values)
        write_csv(output_path / "numerical_results" / f"test_{name}.csv", columns, arrays)
        error_columns = ["t", "t_over_tau", "in_entire", "in_transient", "in_post_transient", "in_late"]
        error_arrays = [times, times / tau, *[mask.astype(int) for mask in windows.values()]]
        for metric in METRICS:
            signed = candidate[metric] - ref[metric]
            with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
                relative = np.divide(signed, np.abs(ref[metric]), out=np.full(len(times), np.nan), where=ref[metric] != 0)
            for label, values in [("signed", signed), ("absolute", np.abs(signed)),
                                  ("normalized_signed", signed / scales[metric]),
                                  ("normalized_absolute", np.abs(signed) / scales[metric]),
                                  ("relative_signed_defined", relative), ("relative_absolute_defined", np.abs(relative))]:
                error_columns.append(metric + "_" + label)
                error_arrays.append(values)
        write_csv(output_path / "error_tables" / f"test_{name}_errors.csv", error_columns, error_arrays)
        # Continuous states have identical left/right event limits. Input and
        # x0 derivatives can jump; all four release currents are continuous.
        event_rows = []
        endpoint_events = [times[-1]] if iright[-1] != ileft[-1] else []
        for event in events + endpoint_events:
            idx = int(np.flatnonzero(times == event)[0])
            for side in ("left", "right"):
                u = float(input_value([event], spans, side)[0])
                event_rows.append([event, event / tau, side, u, *full[:, idx], *reduced[:, idx],
                                   ref["product_flux"][idx], ref["pi_current"][idx], ref["eftu_gdp_current"][idx],
                                   candidate["product_flux"][idx], u - rates[0] * full[0, idx], u - k_eff * reduced[0, idx]])
        with (output_path / "numerical_results" / f"test_{name}_event_limits.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["t", "t_over_tau", "side", "input", *state_labels, "y0", "y4", "xi_eff",
                             "full_product_current", "full_pi_current", "full_gdp_current", "direct_all_current",
                             "full_x0_derivative", "direct_y0_derivative"])
            writer.writerows(event_rows)
        json_write(output_path / "error_tables" / f"test_{name}_metrics.json", summaries[name])
        print(f"Test {name}: numerical {verification[name]['status']}; output/resources/occupancy saved", flush=True)
    dwell = dwell_validation(rates, tau, k_eff, config["solver"])
    dwell_tolerance = float(numeric_gate["mean_dwell_relative"])
    dwell["status"] = "PASS" if max(dwell["mean_relative_error"], dwell["reduced_mean_relative_error"]) <= dwell_tolerance else "FAIL"
    remaining_means = np.array([sum(1 / rates[i:]) for i in range(4)] + [0.0])
    d_initial = np.array(config["tests"]["D"]["initial_full"], dtype=float)
    dwell["D_full_remaining_mean"] = float(d_initial @ remaining_means)
    dwell["D_restart_remaining_mean"] = tau
    dwell["D_restart_mean_relative_increase"] = tau / dwell["D_full_remaining_mean"] - 1
    numerical_pass = all(v["status"] == "PASS" for v in verification.values()) and dwell["status"] == "PASS"
    required_tests = config.get("screen", {}).get("required_tests", ["A", "B", "C"])
    required_windows = config.get("screen", {}).get("required_windows", ["entire"])
    required_groups = config.get("screen", {}).get("required_gate_groups", list(GROUPS) + ["domain"])
    required_statuses = [summaries[name]["gates"][window][group]["status"]
                         for name in required_tests for window in required_windows for group in required_groups]
    scientific_pass = all(status == "PASS" for status in required_statuses)
    status = "NUMERICALLY_UNRESOLVED" if not numerical_pass else (
        "LOCAL_CANDIDATE_PASSED_REGISTERED_SCREEN" if scientific_pass else "LOCAL_CANDIDATE_FAILED_REGISTERED_SCREEN")
    summary = {"status": status, "candidate_label": "MEAN_DWELL_MATCHED_CANDIDATE",
               "config_sha256": frozen_sha, "source_manifest_sha256": sha256(source_path),
               "rates": dict(zip(RATE_KEYS, rates)), "tau": tau, "k_eff": k_eff,
               "time_unit": "source model unit; no seconds interpretation", "sample_count": len(times),
               "sampling_horizon": end, "sampling_horizon_tau": end / tau,
               "input_endpoint_convention": "Finite span input has a right limit zero at horizon; B integrates u=1 through horizon. Endpoint left/right limits are saved, but the supplementary horizon display event does not alter frozen scientific window masks.",
               "numerical_status": "PASS" if numerical_pass else "FAIL", "dwell": dwell,
               "stoichiometry_status": source["stoichiometry_exact"]["status"],
               "test_A_initial_product_current": {"full": float(runs["A"]["ref"]["product_flux"][0]),
                                                  "reduced": float(runs["A"]["candidate"]["product_flux"][0]),
                                                  "interpretation": "expected structural difference"},
               "tests": summaries, "required_screen": {"tests": required_tests, "windows": required_windows,
                                                        "groups": required_groups},
               "domain": {"local_boundary": "No downstream S4 consumption; fixed author overlay; isolated four-step chain",
                          "boundary_intervention": config["gates"]["domain"]["boundary_intervention_required"],
                          "D": "OUT_OF_DOMAIN_NEGATIVE_CONTROL: inventory moved to y0 restarts waiting and changes initial composition",
                          "human_scientific_approval": "NOT_GRANTED_BY_THIS_EXPLORATORY_SCREEN"},
               "full_coupled_validation": "NOT_STARTED", "E_mid_simulation": "NOT_STARTED",
               "PURE_reduced_core_validation": "NOT_CLAIMED"}
    report = {"status": "PASS" if numerical_pass else "FAIL", "config_sha256": frozen_sha,
              "numerical_threshold": numeric_tolerance, "conservation_threshold": conservation_tolerance,
              "positivity_threshold": positivity_tolerance, "tests": verification, "dwell": dwell,
              "approximation_errors_are_separate_from_solver_errors": True,
              "source_audit_is_separate": True}
    json_write(output_path / "verification_report.json", report)
    json_write(output_path / "validation_summary.json", summary)
    make_figures(output_path / "figures", runs, tau, config)
    print(f"{status}; k_eff={k_eff:.17g}; tau={tau:.17g}; {len(times)} fixed samples", flush=True)
    return summary


def refresh_generated_manifest(output):
    files = []
    for directory in ("numerical_results", "error_tables", "figures", "attempts"):
        files.extend(p for p in (output / directory).rglob("*") if p.is_file())
    for filename in ("validation_summary.json", "verification_report.json", "runtime_manifest.json", "attempts.jsonl"):
        path = output / filename
        if path.exists():
            files.append(path)
    artifacts = [{"path": str(p.relative_to(output)).replace("\\", "/"), "sha256": sha256(p), "bytes": p.stat().st_size}
                 for p in sorted(files)]
    runtime = json.loads((output / "runtime_manifest.json").read_text(encoding="utf-8")) if (output / "runtime_manifest.json").exists() else {}
    json_write(output / "generated_artifact_manifest.json", {"config_sha256": runtime.get("config_sha256"), "artifacts": artifacts})


def regenerate_figures(config_path, freeze_path, output):
    config = json.loads(config_path.read_text(encoding="utf-8-sig"))
    freeze = json.loads(freeze_path.read_text(encoding="utf-8-sig"))
    summary = json.loads((output / "validation_summary.json").read_text(encoding="utf-8"))
    if sha256(config_path) != freeze["config_sha256"] or summary["config_sha256"] != freeze["config_sha256"]:
        raise ValueError("Figure regeneration protocol differs from the numerical frozen protocol")
    runs = {}
    for name, test in summary["tests"].items():
        raw = np.genfromtxt(output / "numerical_results" / f"test_{name}.csv", delimiter=",", names=True)
        ref = {metric: raw["full_" + metric] for metric in METRICS}
        candidate = {metric: raw["direct_" + metric] for metric in METRICS}
        runs[name] = {"times": raw["t"], "ref": ref, "candidate": candidate,
                      "input_right": raw["input_right"], "events": test["events"],
                      "metrics": test["metrics"],
                      "scales": {metric: test["metrics"]["entire"][metric]["normalization_scale"] for metric in METRICS}}
    make_figures(output / "figures", runs, summary["tau"], config)
    runtime_path = output / "runtime_manifest.json"
    runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
    runtime["figure_runner_sha256"] = sha256(__file__)
    runtime["figure_regeneration_scope"] = "Presentation only: independent visible-y autoscale and C first registered input-switch band; numerical rows, errors, windows and gates unchanged"
    json_write(runtime_path, runtime)
    with (output / "attempts.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"event": "FIGURES_REGENERATED", "utc": datetime.now(timezone.utc).isoformat(),
                     "runner_sha256": sha256(__file__), "config_sha256": summary["config_sha256"],
                     "scientific_outputs_unchanged": True}) + "\n")
    refresh_generated_manifest(output)
    print("Figure presentation regenerated from saved numerical rows; scientific outputs unchanged", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[2]
    parser.add_argument("--config", type=Path, default=root / "configs/reduction/chain01_four_step_validation.json")
    parser.add_argument("--freeze", type=Path, default=root / "results/reduction/chain01_four_step/protocol_freeze.json")
    parser.add_argument("--source-manifest", type=Path, default=root / "results/reduction/chain01_four_step/source_manifest.json")
    parser.add_argument("--output", type=Path, default=root / "results/reduction/chain01_four_step")
    parser.add_argument("--figures-only", action="store_true", help="Recreate presentation from saved data; no numerical rerun or gate change")
    args = parser.parse_args()
    if args.figures_only:
        regenerate_figures(args.config, args.freeze, args.output)
        return
    args.output.mkdir(parents=True, exist_ok=True)
    log = args.output / "attempts.jsonl"
    attempt = 1 + (sum(1 for line in log.read_text(encoding="utf-8").splitlines() if '"event": "STARTED"' in line) if log.exists() else 0)
    if attempt > 1:
        # Preserve the complete first attempt, including adverse scientific
        # scores, when regenerating metadata after an implementation repair.
        import shutil
        prior_evidence = args.output / "attempts" / f"attempt_{attempt - 1:03d}"
        if not prior_evidence.exists():
            prior_evidence.mkdir(parents=True)
            for name in ("numerical_results", "error_tables", "figures"):
                if (args.output / name).exists():
                    shutil.copytree(args.output / name, prior_evidence / name)
            for name in ("validation_summary.json", "verification_report.json", "runtime_manifest.json",
                         "generated_artifact_manifest.json", "attempts.jsonl"):
                if (args.output / name).exists():
                    shutil.copy2(args.output / name, prior_evidence / name)
    def record(event, **details):
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"attempt": attempt, "event": event,
                         "utc": datetime.now(timezone.utc).isoformat(), "runner_sha256": sha256(__file__),
                         **details}, ensure_ascii=False) + "\n")
    record("STARTED", config_sha256=sha256(args.config), freeze_sha256=sha256(args.freeze),
           previous_attempt_preserved=attempt > 1)
    try:
        summary = run(args.config, args.freeze, args.source_manifest, args.output)
        record("COMPLETED", status=summary["status"], numerical_status=summary["numerical_status"])
    except Exception as exc:
        record("FAILED", error_type=type(exc).__name__, error=str(exc))
        evidence = args.output / "attempts" / f"attempt_{attempt:03d}"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "exception.txt").write_text(traceback.format_exc(), encoding="utf-8")
        # Native failed-attempt products remain recoverable if implementation
        # repair is necessary; the frozen protocol is never edited.
        import shutil
        for name in ("numerical_results", "error_tables", "figures"):
            if (args.output / name).exists():
                shutil.copytree(args.output / name, evidence / name, dirs_exist_ok=True)
        for name in ("validation_summary.json", "verification_report.json", "runtime_manifest.json"):
            if (args.output / name).exists():
                shutil.copy2(args.output / name, evidence / name)
        raise
    finally:
        refresh_generated_manifest(args.output)


if __name__ == "__main__":
    main()

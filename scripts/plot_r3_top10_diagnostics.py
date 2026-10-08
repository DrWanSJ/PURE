"""Plot R3_BASE Top 10 diagnostics from saved samples; no integration."""
import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter

from runtime_reconstruction_rhs import source_network

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001/R3_BASE"
OUT = RUN / "diagnostic_plots"
names = source_network()[0]  # The exact loader used by SourceCoordinateRuntime.
index = {name: j for j, name in enumerate(names)}
with np.load(RUN / "state_trajectories.npz", allow_pickle=False) as saved:
    times = saved["times"]
    full = saved["full_state"]
    reduced = saved["reduced_state"]
assert times.shape == (201,) and full.shape == reduced.shape == (201, len(names))
assert times[0] == 0 and times[-1] == 1000 and np.all(np.diff(times) > 0)
assert all(np.all(np.isfinite(a)) for a in (times, full, reduced))
scale = np.maximum(np.max(np.abs(full), axis=0), 1e-6)
error = np.abs(reduced - full) / scale
initial = (times >= 0) & (times <= 0.05)
post = (times >= 0.05) & (times <= 1000)
full_max = np.max(error, axis=0)
initial_max = np.max(error[initial], axis=0)
post_max = np.max(error[post], axis=0)
with (RUN / "species_errors.csv").open(encoding="utf-8", newline="") as stream:
    rows = list(csv.DictReader(stream))
assert len(rows) == len(names) and {row["id"] for row in rows} == set(names)
for row in rows:
    j = index[row["id"]]
    assert np.isclose(float(row["reference_scale"]), scale[j], rtol=1e-12, atol=0)
    assert np.isclose(float(row["E_inf"]), full_max[j], rtol=1e-12, atol=1e-15)
    assert np.isclose(float(row["post_0p05_E_inf"]), post_max[j], rtol=1e-12, atol=1e-15)
groups = {
    "full_window": sorted(rows, key=lambda row: float(row["E_inf"]), reverse=True)[:10],
    "post_0p05": sorted(rows, key=lambda row: float(row["post_0p05_E_inf"]), reverse=True)[:10],
}
OUT.mkdir(exist_ok=True)
plt.rcParams.update({
    "font.size": 10, "axes.titlesize": 10, "axes.labelsize": 10,
    "xtick.labelsize": 9, "ytick.labelsize": 9, "figure.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
})
BLUE, RED, DARK = "#1f77b4", "#d62728", "#333333"
legend = [Line2D([], [], color=BLUE, lw=1.8, label="FULL"),
          Line2D([], [], color=RED, lw=1.8, ls="--", label="REDUCED"),
          Line2D([], [], color=DARK, lw=1.6, label="Normalized absolute error"),
          Line2D([], [], color="#7b3294", lw=1.3, ls="--", label="1% acceptance line")]


def trajectory(ax, j, mask):
    # Markers denote original samples; no new points or boundary interpolation.
    ax.plot(times[mask], full[mask, j], color=BLUE, lw=1.7, marker=".", ms=2.6)
    ax.plot(times[mask], reduced[mask, j], color=RED, lw=1.7, ls="--", marker=".", ms=2.6)
    ax.set_ylabel("Concentration (µM)")
    ax.ticklabel_format(axis="y", style="sci", scilimits=(-3, 3), useMathText=True)


def errors(ax, j, mask):
    ax.plot(times[mask], error[mask, j], color=DARK, lw=1.5, marker=".", ms=2.6)
    ax.axhline(0.01, color="#7b3294", lw=1.3, ls="--", zorder=4)
    ax.set_ylabel("Normalized abs. error")
    ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=1))
    ax.set_ylim(0, max(0.012, float(np.max(error[mask, j])) * 1.10))


def time_axis(ax, is_post):
    if is_post:
        ax.set_xscale("log")
        ax.set_xlim(0.05, 1000)
        ax.set_xticks([0.1, 1, 10, 100, 1000], ["0.1", "1", "10", "100", "1000"])
    else:
        ax.set_xlim(0, 0.05)
        ax.set_xticks([0, 0.025, 0.05], ["0", "0.025", "0.05"])
    ax.set_xlabel("Time (s)")
    ax.grid(alpha=0.22)


def plot(filename, selection, mode, title):
    fig, grid = plt.subplots(5, 4, figsize=(18, 17))
    fig.subplots_adjust(left=0.065, right=0.985, bottom=0.055, top=0.91,
                        wspace=0.60, hspace=0.75)
    fig.suptitle(title + "\nReference normalization: max(|FULL|) over all 201 samples, floor 1e-6 µM",
                 fontsize=17, fontweight="bold", y=0.995)
    fig.legend(handles=legend[:2] if mode == "overview" else legend,
               loc="lower center", ncol=4, frameon=False, fontsize=11)
    for rank, row in enumerate(selection, 1):
        grid_row, pair = divmod(rank - 1, 2)
        axes = grid[grid_row, pair * 2:pair * 2 + 2]
        j = index[row["id"]]
        metric = full_max[j] if mode != "post" else post_max[j]
        label = "Full-window" if mode != "post" else "Post-layer"
        left_box, right_box = axes[0].get_position(), axes[1].get_position()
        fig.text((left_box.x0 + right_box.x1) / 2, left_box.y1 + 0.032,
                 f"{rank}. {row['id']}\n{label} E_inf = {metric:.2%}",
                 ha="center", va="bottom", fontsize=11, fontweight="bold")
        if mode == "overview":
            axes[1].sharey(axes[0])
            for ax, mask, is_post in zip(axes, (initial, post), (False, True)):
                trajectory(ax, j, mask)
                time_axis(ax, is_post)
            axes[0].set_title("Initial layer: 0–0.05 s")
            axes[1].set_title("Post layer: 0.05–1000 s")
            axes[1].set_ylabel("")
            axes[1].tick_params(labelleft=False)
        else:
            mask = post if mode == "post" else initial
            trajectory(axes[0], j, mask)
            errors(axes[1], j, mask)
            axes[0].set_title("FULL / REDUCED")
            axes[1].set_title("Absolute difference / reference scale")
            for ax in axes:
                time_axis(ax, mode == "post")
    fig.savefig(OUT / filename, dpi=220)
    plt.close(fig)
    print(OUT / filename)


plot("top10_full_overlay.png", groups["full_window"], "overview",
     "R3_BASE | Full-window Top 10 | 0–1000 s, split time axes")
plot("top10_initial_layer.png", groups["full_window"], "initial",
     "R3_BASE | Full-window Top 10 | Initial layer: 0–0.05 s (linear time)")
plot("top10_post_layer.png", groups["post_0p05"], "post",
     "R3_BASE | Post-layer Top 10 | 0.05–1000 s (log time)")
summary = []
for group, selection in groups.items():
    for rank, row in enumerate(selection, 1):
        j = index[row["id"]]
        summary.append({
            "group": group, "rank": rank, "species_id": row["id"],
            "E_inf": float(full_max[j]), "initial_0_0p05_E_inf": float(initial_max[j]),
            "post_0p05_E_inf": float(post_max[j]),
            "max_error_time_s": float(times[np.argmax(error[:, j])]),
            "initial_max_error_time_s": float(times[initial][np.argmax(error[initial, j])]),
            "post_max_error_time_s": float(times[post][np.argmax(error[post, j])]),
            "reference_scale_uM": float(scale[j]),
        })
with (OUT / "top10_error_summary.csv").open("w", encoding="utf-8", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
    writer.writeheader()
    writer.writerows(summary)
print(OUT / "top10_error_summary.csv")
print("Original samples: initial =", int(initial.sum()), "; post =", int(post.sum()))
print("Post-layer Top 10: peak and last saved sample above 1%; errors near 1/10/100/1000 s")
for row in groups["post_0p05"]:
    j = index[row["id"]]
    above = times[post & (error[:, j] > 0.01)]
    sample_indices = [int(np.argmin(np.abs(times - value))) for value in (1, 10, 100, 1000)]
    print(row["id"], "peak=", float(post_max[j]),
          "peak_time=", float(times[post][np.argmax(error[post, j])]),
          "last_above=", float(above[-1]) if len(above) else None,
          "later_samples=", [(float(times[k]), float(error[k, j])) for k in sample_indices])

"""Plot saved R3_BASE samples only; no ODE or model changes."""
from pathlib import Path
import csv

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# R3ResourceTotalRuntimeV2 -> R3CandidateRuntime -> SourceCoordinateRuntime
# gets its species order from this exact existing runtime loader.
from runtime_reconstruction_rhs import source_network

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "results/reduction/r3_aminoacylation_qssa/run_001/R3_BASE"
OUT = RUN / "diagnostic_plots"
NAMES = ["tRNAGlyGCC", "GlyAMP", "PPi", "MettRNAfMetCAU", "GlytRNAGlyGCC"]
species = source_network()[0]
indices = [species.index(name) for name in NAMES]
with np.load(RUN / "state_trajectories.npz", allow_pickle=False) as saved:
    times = saved["times"]
    full = saved["full_state"]
    reduced = saved["reduced_state"]
assert times.ndim == 1 and np.all(np.diff(times) > 0)
assert full.shape == reduced.shape == (len(times), len(species))
assert np.all(np.isfinite(times))
selected = (times >= 0) & (times <= 10)
t = times[selected]
f = full[selected][:, indices]
r = reduced[selected][:, indices]
assert len(t) > 0 and np.all(np.isfinite(f)) and np.all(np.isfinite(r))
error = np.abs(r - f)
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 11, "axes.titlesize": 12, "figure.facecolor": "white"})

def plot(filename, end, errors=False):
    fig, axes = plt.subplots(5, 1, figsize=(10, 13), sharex=True, layout="constrained")
    mask = t <= end
    for j, (name, ax) in enumerate(zip(NAMES, axes)):
        if errors:
            ax.plot(t[mask], error[mask, j], color="#333333", lw=1.6,
                    marker=".", ms=3, label="abs(REDUCED - FULL)")
        else:
            ax.plot(t[mask], f[mask, j], color="#1f77b4", lw=1.8,
                    marker=".", ms=3, label="FULL")
            ax.plot(t[mask], r[mask, j], color="#d62728", ls="--", lw=1.8,
                    marker=".", ms=3, label="REDUCED")
        if errors or end == 4:
            ax.axvline(2, color="#777777", ls=":", lw=1.2, label="2 s reference")
        ax.set_title(name, loc="left", fontweight="bold")
        ax.set_ylabel("Absolute error (µM)" if errors else "Concentration (µM)")
        ax.grid(alpha=0.22)
        ax.set_xlim(0, end)
        if j == 0:
            ax.legend(loc="best", ncol=3, fontsize=10)
    axes[-1].set_xlabel("Time (s)")
    kind = "absolute error" if errors else "FULL / REDUCED"
    fig.suptitle(f"R3_BASE — {kind}, 0–{end} s\nSaved samples; no ODE rerun", fontsize=14)
    fig.savefig(OUT / filename, dpi=180)
    plt.close(fig)

plot("overlay.png", 10)
plot("error.png", 10, errors=True)
plot("zoom_0_4s.png", 4)
windows = [(0, 2), (2, 4), (4, 10)]  # Closed intervals; no synthetic boundary samples.
maxima = []
for left, right in windows:
    mask = (t >= left) & (t <= right)
    assert np.any(mask)
    maxima.append(np.max(error[mask], axis=0))
with (OUT / "max_absolute_errors.csv").open("w", newline="", encoding="utf-8") as stream:
    writer = csv.writer(stream)
    writer.writerow(["species", "max_abs_error_0_2s_uM", "max_abs_error_2_4s_uM", "max_abs_error_4_10s_uM"])
    writer.writerows([name, *[float(values[j]) for values in maxima]] for j, name in enumerate(NAMES))
print("Runtime species indices (zero-based):", dict(zip(NAMES, indices)))
for left, right in windows:
    tt = t[(t >= left) & (t <= right)]
    print(f"[{left}, {right}] s: {len(tt)} original samples, {tt[0]:.6g}-{tt[-1]:.6g} s")
print("species | 0-2 s | 2-4 s | 4-10 s; maximum absolute error (uM)")
for j, name in enumerate(NAMES):
    print(name, *[f"{values[j]:.4g}" for values in maxima], sep=" | ")
print("Original error samples around 2 s (species order above):")
for ti, row in zip(t, error):
    if 1.5 <= ti <= 3.2:
        print(f"{ti:.6g} s:", ", ".join(f"{value:.4g}" for value in row))
for filename in ("overlay.png", "error.png", "zoom_0_4s.png"):
    print(OUT / filename)

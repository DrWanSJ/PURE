"""Shared style for reproducible topology-first meeting figures.

Coordinates are inches on a 16:9 canvas. Figures are drawn from audit artifacts
or explicitly marked schematic statements; none certifies a reduced model.
"""
from pathlib import Path
import json
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "results" / "topology_audit"
OUTPUT = ROOT / "results" / "figures"
COLORS = {
    "ink": "#162C47", "muted": "#56677D", "paper": "#F7F9FC",
    "white": "#FFFFFF", "blue": "#336BA5", "teal": "#008D8B",
    "amber": "#C07A21", "red": "#AE5361", "line": "#D7E1EC",
    "pale_blue": "#EAF1F9", "pale_teal": "#E5F4F1",
    "pale_amber": "#FFF1DE", "pale_red": "#FAEBEF",
}


def canvas(title, subtitle):
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 13,
        "svg.fonttype": "none", "pdf.fonttype": 42,
        "svg.hashsalt": "pnas2017-topology-first",
        "savefig.facecolor": COLORS["paper"],
    })
    fig = plt.figure(figsize=(16, 9), facecolor=COLORS["paper"])
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    label(ax, .65, 8.48, title, size=27, weight="bold")
    label(ax, .65, 7.98, subtitle, size=13.5, color="muted")
    ax.plot([.65, 15.35], [7.62, 7.62], color=COLORS["line"], lw=1)
    return fig, ax


def label(ax, x, y, value, size=13, color="ink", ha="left", va="center",
          weight="normal", mono=False, **kwargs):
    return ax.text(x, y, value, fontsize=size, color=COLORS.get(color, color),
                   ha=ha, va=va, fontweight=weight,
                   fontfamily="DejaVu Sans Mono" if mono else "DejaVu Sans",
                   linespacing=1.38, **kwargs)


def panel(ax, x, y, w, h, fill="white", edge="line", radius=.12, lw=1.1):
    shape = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad=0,rounding_size={radius}",
                          facecolor=COLORS.get(fill, fill),
                          edgecolor=COLORS.get(edge, edge), linewidth=lw)
    ax.add_patch(shape)
    return shape


def node(ax, x, y, text, width=.9, height=.56, fill="pale_blue",
         edge="blue", size=16, weight="normal"):
    panel(ax, x - width / 2, y - height / 2, width, height,
          fill=fill, edge=edge, radius=.09)
    label(ax, x, y, text, size=size, ha="center", weight=weight)


def arrow(ax, x1, y1, x2, y2, color="blue", lw=1.8, style="-|>",
          curve=0, dashed=False, **kwargs):
    shape = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                            mutation_scale=14, linewidth=lw,
                            color=COLORS.get(color, color),
                            connectionstyle=f"arc3,rad={curve}",
                            linestyle="--" if dashed else "-", **kwargs)
    ax.add_patch(shape)
    return shape


def tag(ax, x, y, text, width, color="amber", size=10):
    panel(ax, x, y - .18, width, .36,
          fill=f"pale_{color}", edge=f"pale_{color}", radius=.07)
    label(ax, x + width / 2, y, text, color=color,
          size=size, ha="center", weight="bold")


def footer(ax, figure_number, source="Canonical PNAS 2017 SBML + topology audit"):
    ax.plot([.65, 15.35], [.66, .66], color=COLORS["line"], lw=1)
    label(ax, .65, .36, source, size=9, color="muted")
    label(ax, 15.35, .36, f"FIGURE {figure_number}  |  HUMAN_REVIEW_REQUIRED",
          size=9, color="amber", ha="right", weight="bold")


def read_json(name):
    return json.loads((AUDIT / name).read_text(encoding="utf-8-sig"))


def read_csv(name):
    with (AUDIT / name).open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def save(fig, basename):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    for ax in fig.axes:
        for artist in ax.texts:
            box = artist.get_window_extent(renderer)
            if (box.x0 < bounds.x0 - 1 or box.x1 > bounds.x1 + 1 or
                    box.y0 < bounds.y0 - 1 or box.y1 > bounds.y1 + 1):
                raise ValueError(f"Figure text leaves canvas: {artist.get_text()}")
    for suffix in ("svg", "pdf", "png"):
        metadata = {"Title": basename.replace("_", " ")}
        if suffix == "pdf":
            metadata.update(CreationDate=None, ModDate=None,
                            Subject="Topology-first structural audit; HUMAN_REVIEW_REQUIRED")
        elif suffix == "svg":
            metadata.update(Date=None,
                            Description="Topology-first structural audit; HUMAN_REVIEW_REQUIRED")
        fig.savefig(OUTPUT / f"{basename}.{suffix}", dpi=240,
                    metadata=metadata)
        if suffix == "svg":
            # Matplotlib emits trailing spaces in multi-line path attributes.
            # Normalize the export in code, retaining newline path separators.
            path = OUTPUT / f"{basename}.svg"
            cleaned = "\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n"
            path.write_text(cleaned, encoding="utf-8", newline="\n")
    plt.close(fig)

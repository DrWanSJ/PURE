"""Draw the topology-first sequence and its human/scientific gates.

Run: python scripts/visualization/plot_reduction_workflow.py
"""
from topology_figure_style import canvas, label, panel, node, arrow, tag, footer, save


def main():
    fig, ax = canvas("Topology first, QSSA second",
                     "A proposed order of operations for the detailed PNAS 2017 translation network")
    xs = [.65, 5.75, 10.85]
    top_y, low_y, w, h = 4.8, 1.54, 4.5, 2.2
    steps = [
        (0, top_y, "01", "Detailed SBML model", "Freeze source provenance\nKeep species and reaction roles\nRecord default activity", "blue"),
        (1, top_y, "02", "Topology analysis", "Chains · branches · cycles\nShared hubs and interfaces\nFull graph + author-CSV support graph", "blue"),
        (2, top_y, "03", "Motif detection", "Find real internal paths\nCheck side branches and storage\nRank structural candidates", "blue"),
        (2, low_y, "04", "Structural lumping", "Effective step or aggregate E\nState assumptions and lost detail\nHuman review before adoption", "amber"),
        (1, low_y, "05", "Local QSSA", "Test local timescale separation\nRetain resource-dependent coupling\nRespect the revised topology", "teal"),
        (0, low_y, "06", "Reduced model validation", "Protein + resource trajectories\nConservation and flux accounting\nDocument startup mismatch", "teal"),
    ]
    for index, y, number, title, body, color in steps:
        x = xs[index]
        panel(ax, x, y, w, h, fill="white", edge=color, lw=1.4)
        tag(ax, x + .25, y + 1.84, number, .47, color=color, size=11)
        label(ax, x + .83, y + 1.84, title,
              size=15 if len(title) > 22 else 16.5, weight="bold")
        label(ax, x + .27, y + .88, body, size=13, color="muted")
    for left, right in [(0, 1), (1, 2)]:
        arrow(ax, xs[left] + w + .05, top_y + 1.1,
              xs[right] - .05, top_y + 1.1, lw=2.2)
    arrow(ax, xs[2] + w / 2, top_y - .08,
          xs[2] + w / 2, low_y + h + .08, color="amber", lw=2.2)
    for right, left in [(2, 1), (1, 0)]:
        arrow(ax, xs[right] - .05, low_y + 1.1,
              xs[left] + w + .05, low_y + 1.1, color="teal", lw=2.2)
    tag(ax, .65, 4.54, "TOPOLOGY + CHEMISTRY BEFORE ELIMINATION", 7.22, color="blue", size=11)
    label(ax, .65, 4.12, "Existing QSSA evidence remains useful as bounded input.", size=12,
          color="muted")
    label(ax, .65, 3.88, "A fast variable is not, by itself, a removable variable.", size=12,
          weight="bold")
    label(ax, .65, 1.02, "Each proposed closure is HUMAN_REVIEW_REQUIRED.  Passing engineering checks does not approve a reduced model.",
          size=11.5, color="muted")
    footer(ax, 3, "Workflow proposal; validation remains a separate scientific gate")
    save(fig, "topology_first_workflow")


if __name__ == "__main__":
    main()

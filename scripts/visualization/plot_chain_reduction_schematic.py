"""Draw the conceptual alternatives; no kinetic claim is implied.

Run: python scripts/visualization/plot_chain_reduction_schematic.py
"""
from topology_figure_style import canvas, label, panel, node, arrow, tag, footer, save


def main():
    fig, ax = canvas(
        "When is a reaction chain replaceable?",
        "Repeated chain growth can sometimes be lumped into an effective step or an aggregate state.")
    panel(ax, .65, 5.57, 14.7, 1.7)
    label(ax, 1.0, 6.99, "DETAILED CHAIN  /  CONCEPTUAL SCHEMATIC", size=10,
          color="muted", weight="bold")
    xs = [1.9, 4.8, 7.7, 10.6, 13.6]
    names = ["A", "$X_1$", "$X_2$", "$X_3$", "B"]
    for index, (x, name) in enumerate(zip(xs, names)):
        node(ax, x, 6.34, name, fill="pale_teal" if index in (0, 4)
             else "pale_blue", edge="teal" if index in (0, 4) else "blue", size=20)
        if index < 4:
            arrow(ax, x + .46, 6.34, xs[index + 1] - .46, 6.34)
    label(ax, 7.7, 5.87, "Remove internal states only after checking branches, storage, observables and stoichiometry.",
          size=12.5, ha="center", color="muted")
    label(ax, .65, 5.12, "Topology identifies a candidate. Chemistry and dynamics decide whether the closure is acceptable.",
          size=13.5, weight="bold")

    starts = [.65, 5.65, 10.65]
    for x in starts:
        panel(ax, x, 1.21, 4.7, 3.5)
    label(ax, .98, 4.35, "OPTION A", size=10, color="teal", weight="bold")
    label(ax, .98, 3.98, "Effective A → B", size=20, weight="bold")
    node(ax, 1.65, 3.32, "A", edge="teal", fill="pale_teal")
    node(ax, 4.3, 3.32, "B", edge="teal", fill="pale_teal")
    arrow(ax, 2.12, 3.32, 3.83, 3.32, color="teal")
    label(ax, 2.98, 3.58, "$v_{eff}$", size=13, ha="center", color="teal")
    label(ax, .98, 2.34, "Negligible transit delay\nNo distinct storage needed\nNet resource ledger retained", size=13)
    tag(ax, .98, 1.52, "CONDITIONAL CANDIDATE", 3.78, color="teal")

    label(ax, 5.98, 4.35, "OPTION B", size=10, color="amber", weight="bold")
    label(ax, 5.98, 3.98, "Aggregate state E", size=20, weight="bold")
    for x, name, fill, edge in [(6.35, "A", "pale_teal", "teal"),
                                (8., "E", "pale_amber", "amber"),
                                (9.65, "B", "pale_teal", "teal")]:
        node(ax, x, 3.32, name, fill=fill, edge=edge)
    arrow(ax, 6.82, 3.32, 7.53, 3.32, color="amber")
    arrow(ax, 8.47, 3.32, 9.18, 3.32, color="amber")
    label(ax, 5.98, 2.34, "Stores total chain occupancy\nUseful when transit delay matters\nRequires an explicit exit closure", size=13)
    tag(ax, 5.98, 1.52, "OCCUPANCY CANDIDATE", 3.78, color="amber")

    label(ax, 10.98, 4.35, "OPTION C", size=10, color="red", weight="bold")
    label(ax, 10.98, 3.98, "Keep explicit", size=20, weight="bold")
    explicit_x = [11.22, 12.07, 12.92, 13.77, 14.62]
    for index, (x, name) in enumerate(zip(explicit_x, ["A", "$X_1$", "$X_2$", "$X_3$", "B"])):
        node(ax, x, 3.32, name, width=.55, height=.48, size=12.5,
             fill="pale_red", edge="red")
        if index < 4:
            arrow(ax, x + .285, 3.32, explicit_x[index + 1] - .285, 3.32, color="red")
    label(ax, 10.98, 2.34, "Side branches or return paths\nResource timing must be tracked\nIntermediate observables matter", size=13)
    tag(ax, 10.98, 1.52, "EXPLICIT RETENTION", 3.78, color="red")
    label(ax, .65, .89, "Local QSSA may follow either retained or aggregated motifs; topology alone does not establish timescale separation.",
          size=11.5, color="muted")
    footer(ax, 2, "Conceptual reduction alternatives; no automatic state deletion or validated closure")
    save(fig, "topology_first_chain_schematic")


if __name__ == "__main__":
    main()

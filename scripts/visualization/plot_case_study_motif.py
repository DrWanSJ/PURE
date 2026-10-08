"""Draw the exact audited first-elongation three-step case.

Reads results/topology_audit/case_study.json. Full species IDs are retained;
S0--S3 are aliases used only to keep the reaction diagram legible.
"""
from topology_figure_style import (
    canvas, label, panel, node, arrow, tag, footer, save, read_json,
)


def main():
    case = read_json("case_study.json")
    species = case["serial_species_ids"]
    reactions = case["serial_reaction_ids"]
    if len(species) != 4 or len(reactions) != 3:
        raise ValueError("Figure 4 requires the audited 3-step / 4-species serial motif")
    expected = [f"re{number:010d}" for number in (16, 17, 18)]
    if reactions != expected:
        raise ValueError("Figure 4 annotations are bound to canonical reactions 16, 17, 18")
    fig, ax = canvas("A real serial subchain: first Gly elongation",
                     "Three forward steps are serial in the author-CSV support graph; the full SBML retains author-disabled side paths.")
    panel(ax, .65, 4.1, 14.7, 3.16)
    label(ax, 1., 6.99, "ORIGINAL SUBCHAIN  /  ACTUAL MODEL IDS", size=10,
          color="muted", weight="bold")
    xs = [1.85, 5.95, 10.05, 14.0]
    for index, x in enumerate(xs):
        node(ax, x, 6.28, f"$S_{index}$", width=1.08, height=.66,
             fill="pale_teal" if index == 3 else "pale_blue",
             edge="teal" if index == 3 else "blue", size=20)
        if index < 3:
            arrow(ax, x + .55, 6.28, xs[index + 1] - .55, 6.28)
            mid = (x + xs[index + 1]) / 2
            label(ax, mid, 6.65, reactions[index], mono=True, size=11, ha="center")
            if index < 2:
                arrow(ax, mid, 6.27, mid, 5.92, color="teal", lw=1.4)
                label(ax, mid, 5.72, "PO4" if index == 0 else "EFTu_GDP",
                      size=12, color="teal", ha="center", weight="bold")
    for index, sid in enumerate(species):
        label(ax, 1.04, 5.22 - .265 * index, f"S{index}  {sid}", mono=True, size=10.2)

    panel(ax, .65, 1.11, 6.54, 2.69, edge="amber")
    label(ax, .98, 3.45, "PROPOSED OCCUPANCY AGGREGATE", size=11,
          color="amber", weight="bold")
    node(ax, 1.71, 2.83, "$S_0$", width=1.03, height=.63,
         fill="pale_blue", edge="blue", size=18)
    node(ax, 3.85, 2.83, "$E_{mid}$", width=1.35, height=.63,
         fill="pale_amber", edge="amber", size=20)
    node(ax, 6.03, 2.83, "$S_3$", width=1.08, height=.63,
         fill="pale_teal", edge="teal", size=18)
    arrow(ax, 2.25, 2.83, 3.16, 2.83, color="amber")
    label(ax, 2.68, 3.10, "$v_{16}$", size=13, color="amber", ha="center")
    arrow(ax, 4.54, 2.83, 5.46, 2.83, color="amber")
    label(ax, 5., 3.10, "$v_{18}$", size=13, color="amber", ha="center")
    label(ax, 1., 2.19, "$E_{mid}=S_1+S_2$   and   $\\dot{E}_{mid}=v_{16}-v_{18}$",
          size=14.5)
    label(ax, 1., 1.68, "Occupancy identity is exact; exit and release laws need closure.\nEFTu_GDP release still depends on internal flux v17.",
          size=11.2, color="muted")

    panel(ax, 7.48, 1.11, 7.87, 2.69)
    label(ax, 7.82, 3.45, "PRESERVED VS LOST / CONDITIONAL", size=11,
          color="muted", weight="bold")
    label(ax, 7.82, 3.02, "Preserve: total bound-ribosome occupancy", size=13,
          color="teal", weight="bold")
    label(ax, 7.82, 2.62, "Net event:  S0 → S3 + PO4 + EFTu_GDP", size=13)
    label(ax, 7.82, 2.22, "Lost without closure: phase memory and separate release timing", size=11.8,
          color="red")
    label(ax, 7.82, 1.78, "This segment consumes no free GTP: S0 is already post-hydrolysis.\nFull-cycle accounting must be handled separately.", size=11.2,
          color="muted")
    label(ax, .65, .87, "Source model represents fMGG with two Gly additions.  Review the author-disabled full-graph branches before promoting this local prototype.",
          size=11.2, color="muted")
    footer(ax, 4, "Canonical SBML IDs; author-CSV support; no reduced-model validation claimed")
    save(fig, "topology_first_case_study")


if __name__ == "__main__":
    main()

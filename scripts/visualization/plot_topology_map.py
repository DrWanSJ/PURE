"""Plot functional modules, real shared interfaces, hubs and the serial case.

The interface matrix is an undirected connectivity map, not a flux or causal
diagram. Counts are read from the audit; matrix diagonal entries are module
species/reaction counts and cannot be summed because membership overlaps.
"""
from matplotlib import colormaps
from topology_figure_style import (
    canvas, label, panel, node, arrow, tag, footer, save, read_json, read_csv,
)


def module_label(row):
    name = row["module_name"].lower()
    rules = [
        ("amino", "Aminoacylation /\nformylation", "AA", 0),
        ("init", "Initiation", "INI", 1),
        ("elong", "Elongation", "ELONG", 2),
        ("term", "Termination /\nribosome recycling", "TERM", 3),
        ("energy", "Energy regeneration", "ENERGY", 4),
        ("small", "Small molecules", "SMALL", 5),
    ]
    for key, display, abbreviation, order in rules:
        if key in name:
            return display, abbreviation, order
    return row["module_name"], row["module_id"][:6], 99


def main():
    summary = read_json("summary.json")
    modules = read_csv("module_table.csv")
    interfaces = read_csv("module_interfaces.csv")
    hubs = read_csv("hub_table.csv")
    case = read_json("case_study.json")
    modules.sort(key=lambda row: module_label(row)[2])
    if not 3 <= len(modules) <= 6:
        raise ValueError("This module map expects 3--6 audited major modules")
    counts = summary.get("counts", summary)
    ns = counts.get("species", counts.get("species_count"))
    nr = counts.get("reactions", counts.get("reaction_count"))
    if ns is None or nr is None:
        raise ValueError("summary.json must provide source species and reaction counts")
    fig, ax = canvas("The network is modular, but its resources are shared",
                     f"PNAS 2017 fMGG reference  |  {ns} species · {nr} reactions  |  full structural graph; overlapping module membership")
    panel(ax, .65, 1.45, 9.13, 5.83)
    label(ax, .98, 6.98, "SHARED-SPECIES INTERFACE MAP", size=11,
          color="muted", weight="bold")
    label(ax, .98, 6.63, "Off-diagonal: shared species  (shared nonhubs)", size=11, color="muted")
    by_pair = {frozenset((edge["module_a"], edge["module_b"])): edge
               for edge in interfaces}
    max_shared = max([int(edge["shared_species_count"]) for edge in interfaces] or [1])
    n = len(modules)
    cell = min(1.10, 4.0 / n)
    x0, top = 3.78, 6.03
    cmap = colormaps["Blues"]
    for col, row in enumerate(modules):
        label(ax, x0 + cell * (col + .5), 6.30, module_label(row)[1],
              size=10, ha="center", weight="bold", color="muted")
    for row_index, row in enumerate(modules):
        cy = top - cell * (row_index + .5)
        display, abbreviation, _ = module_label(row)
        label(ax, 1.0, cy + .12, display, size=12.5,
              color="amber" if abbreviation == "ELONG" else "ink",
              weight="bold" if abbreviation == "ELONG" else "normal")
        label(ax, 1., cy - .25,
              f"{row['species_count']} species / {row['reaction_count']} reactions",
              size=9.5, color="muted")
        for col_index, other in enumerate(modules):
            x = x0 + col_index * cell
            y = top - (row_index + 1) * cell
            if row_index == col_index:
                panel(ax, x + .02, y + .02, cell - .04, cell - .04,
                      fill="pale_amber" if abbreviation == "ELONG" else "pale_teal",
                      edge="white", radius=.035)
                label(ax, x + cell / 2, y + cell / 2, abbreviation,
                      size=9.5, ha="center", color="amber" if abbreviation == "ELONG" else "teal",
                      weight="bold")
            else:
                edge = by_pair.get(frozenset((row["module_id"], other["module_id"])))
                shared = int(edge["shared_species_count"]) if edge else 0
                nonhub = int(edge["nonhub_shared_species_count"]) if edge else 0
                color = cmap(.07 + .53 * shared / max_shared)
                panel(ax, x + .02, y + .02, cell - .04, cell - .04,
                      fill=color, edge="white", radius=.035)
                label(ax, x + cell / 2, y + cell * .60, str(shared),
                      size=16, ha="center", weight="bold")
                label(ax, x + cell / 2, y + cell * .28, f"({nonhub})", size=10,
                      ha="center", color="muted")
    label(ax, .99, 1.76,
          "Most interfaces are shared hubs; nonhub links join elongation to initiation / termination.\nModule memberships overlap and are not isolated systems; their counts cannot be summed.",
          size=9.5, color="muted")

    panel(ax, 10.10, 4.14, 5.25, 3.14)
    label(ax, 10.43, 6.98, "SHARED HUBS  /  KEEP ACCOUNTING EXPLICIT", size=10.3,
          color="teal", weight="bold")
    label(ax, 10.43, 6.60, "Species", size=10, color="muted")
    label(ax, 15.0, 6.60, "reactions / source subnetworks", size=9.1, ha="right", color="muted")
    ranking = sorted(hubs, key=lambda row: -int(row["reactions_participated"]))
    selected = ranking[:3]
    by_id = {row["species_id"]: row for row in hubs}
    for sid in ("ATP", "GTP"):
        if sid in by_id and sid not in {row["species_id"] for row in selected}:
            selected.append(by_id[sid])
    for candidate in ranking:
        if len(selected) >= 5:
            break
        if candidate["species_id"] not in {row["species_id"] for row in selected}:
            selected.append(candidate)
    for index, row in enumerate(selected[:5]):
        y = 6.15 - .34 * index
        label(ax, 10.43, y, row["species_id"], size=12.5, weight="bold")
        label(ax, 15.0, y, f"{row['reactions_participated']} / {row['module_count']}",
              size=12, ha="right")
    label(ax, 10.43, 4.40, "Incidence counts use the full graph.\nHigh degree alone does not justify elimination.", size=9.9,
          color="muted")

    panel(ax, 10.10, 1.45, 5.25, 2.43, edge="amber")
    label(ax, 10.43, 3.53, "HIGHLIGHT: LOCAL SERIAL CANDIDATE", size=10.5,
          color="amber", weight="bold")
    xs = [10.82, 12.19, 13.56, 14.91]
    for index, x in enumerate(xs):
        node(ax, x, 2.98, f"$S_{index}$", width=.60, height=.43,
             fill="pale_amber", edge="amber", size=13)
        if index < 3:
            arrow(ax, x + .31, 2.98, xs[index + 1] - .31, 2.98, color="amber", lw=1.4)
    label(ax, 10.43, 2.54, " → ".join(case["serial_reaction_ids"]), mono=True,
          size=8.4)
    label(ax, 10.43, 2.02,
          f"Strict chains: {counts['full_strict_serial_chains']} full graph / {counts['author_strict_serial_chains']} author support.\nFull-graph branches remain.\nReview aggregate occupancy E before local QSSA.",
          size=10.5, color="muted")
    label(ax, .65, 1.03, "Topology reveals both opportunities and constraints: serial interiors may be grouped; shared resource interfaces must remain auditable.",
          size=11.2, color="muted")
    footer(ax, 1, "Module and hub counts read directly from results/topology_audit; interface map is undirected")
    save(fig, "topology_first_network_map")


if __name__ == "__main__":
    main()

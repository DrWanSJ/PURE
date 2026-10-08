"""Supplementary actual branch/return and open energy-module topology.

Read audited stoichiometry, author coefficients, reverse-pair records, shared
hub incidence, and full-canonical context components. Positive coefficients
define graph support; they do not certify trajectory flux or equilibrium.
"""
import json

from topology_figure_style import (
    canvas, label, panel, node, arrow, footer, save, read_csv,
)


def main():
    reactions = {row["reaction_id"]: row for row in read_csv("reactions_table.csv")}
    ids = [f"re{index:010d}" for index in (13, 14, 21)]
    forward, hydrolysis, reverse = [reactions[rid] for rid in ids]
    substrates = json.loads(forward["substrates_json"])
    products = json.loads(forward["products_json"])
    if (substrates != json.loads(reverse["products_json"]) or
            products != json.loads(reverse["substrates_json"])):
        raise ValueError("Docking / undocking pair must be an exact stoichiometric reverse")
    pair = next(row for row in read_csv("reverse_pairs.csv")
                if {row["forward_id"], row["reverse_id"]} == {ids[0], ids[2]})
    if pair["both_author_positive"] != "True":
        raise ValueError("The displayed return pair must have positive author coefficients")
    if any(float(row["author_rate_coefficient"]) <= 0
           for row in (forward, hydrolysis, reverse)):
        raise ValueError("All displayed branch reactions must be in author-nonzero support")
    aliases = {
        "A": "elRS70SAGGU0002_fMet",
        "T": "EFTu_GTP_GlytRNAGlyGCC",
        "D": next(iter(products)),
        "H": next(iter(json.loads(hydrolysis["products_json"]))),
    }
    if substrates != {aliases["A"]: 1.0, aliases["T"]: 1.0}:
        raise ValueError("Figure is bound to the actual first-Gly docking reaction")
    if json.loads(hydrolysis["substrates_json"]) != {aliases["D"]: 1.0}:
        raise ValueError("Hydrolysis must leave the same docked branch point")
    author_exits = {rid for rid, row in reactions.items()
                    if aliases["D"] in json.loads(row["substrates_json"]) and
                    float(row["author_rate_coefficient"]) > 0}
    if author_exits != {ids[1], ids[2]}:
        raise ValueError("The audited author-nonzero branch must have exactly the two shown exits")
    components = read_csv("context_components.csv")
    energy = []
    for suffix in "ABCD":
        row = next(row for row in components
                   if row["graph_view"] == "FULL_CANONICAL" and
                   row["source_modules"] == f"EnergyRegeneration_{suffix}")
        if json.loads(row["interface_nonhub_species_json"]):
            raise ValueError("Local energy example requires the audited full-view zero-nonhub interface")
        energy.append((suffix, row))
    hubs = {row["species_id"]: row for row in read_csv("hub_table.csv")}

    fig, ax = canvas("Branches, returns and open subnetworks matter",
                     "Actual first-Gly docking branch, an exact reverse pair, and measured shared-resource interfaces")
    panel(ax, .65, 4.03, 9.0, 3.24)
    label(ax, .98, 6.97, "AUTHOR-NONZERO BRANCH + BINDING / UNBINDING RETURN", size=10.8,
          color="muted", weight="bold")
    node(ax, 2.0, 6.05, "A + T", width=1.42, height=.65,
         fill="pale_teal", edge="teal", size=18)
    node(ax, 5.25, 6.05, "D", width=1.10, height=.65,
         fill="pale_amber", edge="amber", size=20)
    node(ax, 8.53, 6.05, "H", width=1.10, height=.65,
         fill="pale_blue", edge="blue", size=20)
    arrow(ax, 2.72, 6.05, 4.69, 6.05, color="teal")
    label(ax, 3.7, 6.43, ids[0], mono=True, size=11.3, ha="center")
    arrow(ax, 5.81, 6.05, 7.97, 6.05, color="blue")
    label(ax, 6.89, 6.43, ids[1], mono=True, size=11.3, ha="center")
    label(ax, 6.89, 5.69, "bound GTP → GDP + PO4", size=11.2,
          color="blue", ha="center")
    arrow(ax, 4.98, 5.73, 2.47, 5.73, color="amber", curve=-.45, lw=2)
    label(ax, 3.7, 4.95, ids[2], mono=True, size=11.3, ha="center", color="amber")
    label(ax, 3.7, 4.65, "exact reverse of docking", size=10.8, ha="center", color="amber")
    label(ax, .98, 4.35,
          "13 + 21 has zero net ledger.  Two author-nonzero exits from D; no flux split or equilibrium is inferred.",
          size=10.1, color="muted")

    panel(ax, .65, 1.12, 9.0, 2.62)
    label(ax, .98, 3.44, "EXACT SPECIES ALIAS KEY", size=10.5,
          color="muted", weight="bold")
    for index, (alias, sid) in enumerate(aliases.items()):
        label(ax, 1., 3.09 - .27 * index, f"{alias}  {sid}", mono=True, size=10.1)
    coefficients = ", ".join(f"{float(row['author_rate_coefficient']):g}"
                             for row in (forward, hydrolysis, reverse))
    label(ax, 1., 1.94, f"Author coefficients for reactions 13, 14, 21:  {coefficients}  (all positive)", size=11)
    label(ax, 1., 1.51,
          "Positive support does not certify instantaneous flux.  H retains bound PO4 until the later release step.",
          size=10.1, color="muted")

    panel(ax, 10., 4.8, 5.35, 2.47)
    label(ax, 10.32, 6.97, "SHARED HUBS REQUIRE RESOURCE LEDGERS", size=10.6,
          color="teal", weight="bold")
    for x, sid in zip([10.96, 12.67, 14.40], ["ATP", "GTP", "PO4"]):
        node(ax, x, 6.21, sid, width=1.03, height=.55,
             fill="pale_teal", edge="teal", size=14, weight="bold")
        label(ax, x, 5.66, f"{hubs[sid]['reactions_participated']} reactions", size=10.4,
              ha="center", color="muted")
    label(ax, 10.32, 5.16,
          "Full-graph incidences; shared across source modules.\nTopology does not establish eliminability or fastness.",
          size=10.5, color="muted")

    panel(ax, 10., 1.12, 5.35, 3.39)
    label(ax, 10.32, 4.18, "LOCALIZED OPEN ENERGY MODULES", size=10.6,
          color="blue", weight="bold")
    label(ax, 10.32, 3.84, "Full context view after declared hub suppression", size=10.3, color="muted")
    for index, (suffix, row) in enumerate(energy):
        y = 3.38 - .39 * index
        label(ax, 10.32, y, f"Energy {suffix}  /  {row['reaction_count']} r", size=11.3,
              weight="bold")
        label(ax, 12.4, y, " · ".join(json.loads(row["interface_species_json"])), size=10.8,
              color="blue")
    label(ax, 10.32, 1.65,
          "Interfaces restored above; zero nonhub interfaces in this view.\nLocalized topology does not imply dynamical independence.",
          size=9.7, color="muted")
    label(ax, .65, .87,
          "Preserve branch competition and shared-resource coupling when designing a structural or local-QSSA closure.",
          size=11.5, color="muted")
    footer(ax, 5, "Reaction and interface records read from results/topology_audit; supplementary topology view")
    save(fig, "topology_first_branch_cycle_interfaces")


if __name__ == "__main__":
    main()

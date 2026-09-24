#!/usr/bin/env python3
"""Generate the PNAS 2017 reduction MAP (Phase 6) — a proposal, not a reduction.

This script NEVER reduces the network. It only:
  * assigns every one of the 968 combined-model reactions to Level A (5 broad
    functional modules), Level B (the original 26 subsystems) and Level C
    (a structural reaction family);
  * proposes a CANDIDATE transformation label for each reaction;
  * records the resource-accounting consequences we can compute mechanically
    (free ATP/GTP/PPi/PO4 net change, net particle-number change);
  * marks every non-KEEP candidate HUMAN_REVIEW_REQUIRED = true.

Reverse pairs are detected structurally: the SBML encodes many reversible
steps as two irreversible reactions whose (reactants, products) are swapped.
Such pairs are the most obvious FAST_EQUILIBRIUM / LUMP candidates and are
labelled as such (still only a candidate).

Output: docs/reduction/reduction_decisions.csv
"""
import csv
import os
from collections import OrderedDict, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIT = os.path.join(ROOT, "models", "pnas2017_full_reference", "audit")
OUT = os.path.join(ROOT, "docs", "reduction")

BROAD = {
    "Initiation": "initiation",
    "Elongation": "elongation",
    "Aminoacylation": "aminoacylation",
    "Termination": "termination_recycling",
    "EnergyRegeneration": "energy_regeneration",
    "FMet": "aminoacylation_formylation",   # flag: mapping is a review decision
    "SmallMolecules": "resource_pool",
}


def broad_of(subsys_files):
    for f in sorted(filter(None, subsys_files.split("|"))):
        for prefix, broad in BROAD.items():
            if f.startswith(prefix):
                return broad
    return "unassigned"


def parse(field):
    out = defaultdict(float)
    for item in filter(None, field.split("|")):
        sid, _, s = item.partition(":")
        out[sid] += float(s or 1)
    return dict(out)


def sig(react, prod):
    return (tuple(sorted(react.items())), tuple(sorted(prod.items())))


def main():
    os.makedirs(OUT, exist_ok=True)
    reactions = list(csv.DictReader(
        open(os.path.join(AUDIT, "reactions.csv"), encoding="utf-8")))
    balance = {r["reaction_id"]: r for r in csv.DictReader(
        open(os.path.join(AUDIT, "reaction_balance_audit.csv"), encoding="utf-8"))}

    # detect reverse pairs structurally
    fwd = {}
    for r in reactions:
        react, prod = parse(r["reactants"]), parse(r["products"])
        fwd[sig(react, prod)] = r["id"]
    reverse_partner = {}
    for r in reactions:
        react, prod = parse(r["reactants"]), parse(r["products"])
        partner = fwd.get(sig(prod, react))
        if partner and partner != r["id"]:
            reverse_partner[r["id"]] = partner

    rows = []
    for r in reactions:
        rid = r["id"]
        b = balance.get(rid, {})
        broad = broad_of(r["subsystem_files"])
        react, prod = parse(r["reactants"]), parse(r["products"])
        is_degraded = any(s.endswith("_degraded")
                          for s in list(react) + list(prod))
        forms_complex = any("_" in s for s in prod) and not any(
            "_" in s for s in react)
        dissociates = any("_" in s for s in react) and not any(
            "_" in s for s in prod)
        n_resources = sum(
            1 for k in ("ATP", "GTP", "ADP", "AMP", "GDP", "PPi", "Pi_PO4",
                        "CP_creatine_phosphate")
            if b.get("%s_free_net" % k, "0") not in ("0", ""))
        is_rev = rid in reverse_partner
        label, reason = propose(rid, broad, int(r["n_reactants"]),
                                int(r["n_products"]), is_rev, n_resources,
                                b, is_degraded, forms_complex, dissociates)
        review = label != "KEEP"
        rows.append(OrderedDict([
            ("reaction_id", rid),
            ("level_A_module", broad),
            ("level_B_subsystems", r["subsystem_files"]),
            ("level_C_family", family(rid, broad, is_rev, n_resources)),
            ("n_reactants", r["n_reactants"]),
            ("n_products", r["n_products"]),
            ("rate_law", r["rate_law"]),
            ("reverse_partner_id", reverse_partner.get(rid, "")),
            ("net_particle_number_change", b.get("net_particle_number_change", "")),
            ("free_ATP_net", b.get("ATP_free_net", "")),
            ("free_ADP_net", b.get("ADP_free_net", "")),
            ("free_AMP_net", b.get("AMP_free_net", "")),
            ("free_GTP_net", b.get("GTP_free_net", "")),
            ("free_GDP_net", b.get("GDP_free_net", "")),
            ("free_PPi_net", b.get("PPi_free_net", "")),
            ("free_Pi_PO4_net", b.get("Pi_PO4_free_net", "")),
            ("free_CP_net", b.get("CP_creatine_phosphate_free_net", "")),
            ("candidate_label", label),
            ("candidate_reason", reason),
            ("required_assumption", assumption(label)),
            ("conservation_consequence",
             "moiety/particle accounting must be re-derived post-reduction"),
            ("osmotic_consequence",
             "net_particle_number_change must be preserved or compensated"),
            ("ionic_strength_consequence",
             "not assessable: species charge/protonation undefined in SBML"),
            ("data_needed_to_validate",
             "timescale / concentration / flux evidence from PNAS SI Datasets"),
            ("HUMAN_REVIEW_REQUIRED", str(review).lower()),
        ]))

    path = os.path.join(OUT, "reduction_decisions.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    from collections import Counter
    lc = Counter(r["candidate_label"] for r in rows)
    bc = Counter(r["level_A_module"] for r in rows)
    print("reverse pairs detected:", len(reverse_partner))
    print("candidate label counts:", dict(lc))
    print("broad module counts:", dict(bc))
    print("wrote", path, "(%d rows)" % len(rows))


def family(rid, broad, is_rev, n_resources):
    if broad == "energy_regeneration":
        return "energy_regeneration"
    if broad == "aminoacylation_formylation":
        return "formylation"
    if broad == "resource_pool":
        return "small_molecule_pool"
    if is_rev:
        return "reversible_binding_step"
    if n_resources:
        return "nucleotide_hydrolysing_step"
    return broad + "_step"


def propose(rid, broad, nr, npd, is_rev, n_resources, bal, is_degraded,
            forms_complex, dissociates):
    if is_rev:
        return ("LUMP_CANDIDATE",
                "structurally one reversible step exported as a forward+reverse "
                "irreversible pair; can be re-combined into a single reversible "
                "reaction. Whether it also sits at FAST_EQUILIBRIUM needs "
                "timescale data (not derivable from SBML structure).")
    if is_degraded:
        return ("DROP_CANDIDATE",
                "irreversible degradation/turnover step that returns monomers "
                "to the resource pools. A common simplification is to drop or "
                "first-order-lump it, but that BREAKS recycling/particle "
                "accounting, so it is explicitly not assumed here.")
    if broad == "resource_pool":
        return ("CHEMOSTAT_CANDIDATE",
                "small-molecule pool reaction; buffering via chemostat is a "
                "reduction option but changes particle accounting")
    if forms_complex:
        return ("QSSA_CANDIDATE",
                "irreversible association forming a bound complex; the complex "
                "is a candidate for a quasi-steady-state intermediate")
    if dissociates:
        return ("QSSA_CANDIDATE",
                "irreversible dissociation of a bound complex; candidate QSSA "
                "on the transient complex")
    if n_resources:
        return ("KEEP", "net free energy-carrier turnover: KEEP unless the "
                        "carrier accounting target is explicitly dropped")
    if int(bal.get("net_particle_number_change", "0")) != 0 and nr >= 2:
        return ("LUMP_CANDIDATE",
                "multi-reactant association changing particle count; a "
                "candidate for lumping of intermediate complex(es)")
    return ("KEEP", "committed irreversible step with no mechanical reduction "
                    "signal: default KEEP, human confirmation required")


def assumption(label):
    return {
        "FAST_EQUILIBRIUM_CANDIDATE": "forward/reverse timescale << system timescale",
        "LUMP_CANDIDATE": "lumped intermediate stays near steady state",
        "QSSA_CANDIDATE": "intermediate concentration remains small and ~dc/dt=0",
        "CHEMOSTAT_CANDIDATE": "species concentration clamped / well-buffered",
        "DROP_CANDIDATE": "species/reaction irrelevant to all accounting targets",
        "KEEP": "n/a",
        "UNKNOWN": "unresolved",
    }.get(label, "unresolved")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Verify graph-aware PNAS2017 reaction-level annotation v1."""
from __future__ import annotations
import csv,json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ANN=ROOT/"docs/reduction/reaction_level_annotation_v1.csv"; FAM=ROOT/"docs/reduction/reaction_family_summary_v1.csv"; MAN=ROOT/"docs/reduction/reaction_graph_manifest_v1.json"; BAL=ROOT/"models/pnas2017_full_reference/audit/reaction_balance_audit.csv"
ES={"ANCHOR":846,"PROPAGATED":42,"FAMILY_PROPAGATED":4,"SHARED_JUNCTION":76}
EJ={"RS_binding;RS_charging":4,"ELONG_energy_coupling;RECYCLE_component_release":2,"INIT_70S_formation;INIT_assembly;INIT_tRNA_recruitment":16,"INIT_assembly;INIT_tRNA_recruitment":54}
ET={"HETERODIMER_ASSOCIATION":266,"DISSOCIATION":266,"STATE_TRANSITION":436}
def read(p):
    with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def main():
    rows,fams,bal=read(ANN),read(FAM),read(BAL); man=json.loads(MAN.read_text(encoding="utf-8"))
    assert len(rows)==968 and len({r["reaction_id"] for r in rows})==968 and {r["reaction_id"] for r in rows}=={r["sbml_reaction_id"] for r in bal}
    assert len(fams)==36
    assert dict(Counter(r["topology_status"] for r in rows))==ES
    assert dict(Counter(r["level_c_functional_contexts"] for r in rows if r["topology_status"]=="SHARED_JUNCTION"))==EJ
    assert dict(Counter(r["mechanistic_reaction_type"] for r in rows))==ET
    assert sum(r["is_functional_anchor"]=="true" for r in rows)==846
    assert not any(r["topology_status"]=="UNRESOLVED" or r["human_review_status"]=="HUMAN_REVIEW_REQUIRED_UNRESOLVED" for r in rows)
    by={r["reaction_id"]:r for r in rows}; pairs=set()
    for r in rows:
        for k in ("reactants_json","products_json","resource_ledger_effect_json","functional_pool_effect_json","conservation_family_effect_json"):json.loads(r[k])
        if r["topology_status"]=="SHARED_JUNCTION": assert r["level_c_primary_stage"]==""
        else: assert r["level_c_primary_stage"]
        if r["reversibility_class"]=="EXACT_REVERSE_PAIR":
            p=by[r["reverse_partner_id"]]; assert p["reverse_partner_id"]==r["reaction_id"]; assert p["reaction_family_id"]==r["reaction_family_id"]; assert p["topology_status"]==r["topology_status"]; assert p["level_c_primary_stage"]==r["level_c_primary_stage"]; assert p["level_c_functional_contexts"]==r["level_c_functional_contexts"]; pairs.add(tuple(sorted((r["reaction_id"],r["reverse_partner_id"]))))
    assert len(pairs)==290
    for rid in ("re0000000308","re0000000327"):
        r=by[rid]; assert r["reaction_family_id"]=="RFAM_014" and r["topology_status"]=="SHARED_JUNCTION" and r["level_c_functional_contexts"]=="ELONG_energy_coupling;RECYCLE_component_release"
    assert man["bipartite_incidence_edges"]==3854 and man["bridge_species_for_propagation"]==170 and man["active_reaction_families"]==35 and man["anchors_total"]==846 and man["human_review_required_count"]==0
    assert man["topology_status_counts"]==ES and man["shared_context_counts"]==EJ
    print("PASS: graph-aware v1 = 968 unique rows")
    print("PASS: 35 active families + RFAM_DEG; 290 reverse channels")
    print("PASS: 846 anchors / 42 propagated / 4 family-propagated / 76 shared junctions")
    print("PASS: EFG/50S pair = shared ELONG_energy_coupling + RECYCLE_component_release")
    print("PASS: unresolved=0; human review reserved for future graph-unresolved rows")
    print("NOTE: graph annotation only; no QSSA/lumping/kinetic validity is tested")
if __name__=="__main__": main()

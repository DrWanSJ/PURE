"""Topology inventory and exact stoichiometric certificates for source cycles.

All nonnegative stationary fluxes in each enzyme transition network decompose
into directed cycles. Enumerating simple cycles independently of rational
nullspace projection establishes physical directionality without signed-flux
assumptions. Source degradation remains separately inventoried.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from fractions import Fraction
import platform
import sys
import networkx as nx
import sympy as sp

from source import ROOT, build_inventory, digest

DOC = ROOT / "docs/reduction/energy_cycles"
RESULT = ROOT / "results/energy_cycles_v1"
NET = {
    "CK":{"CP":-1,"ADP":-1,"Cr":1,"ATP":1},
    "NDK":{"ATP":-1,"GDP":-1,"ADP":1,"GTP":1},
    "MK":{"ATP":-1,"AMP":-1,"ADP":2},
    "PPiase":{"PPi":-1,"PO4":2},
}
MOIETY = {
    "CK":{"adenylate_group":{"ATP":1,"ADP":1},"creatine_group":{"CP":1,"Cr":1},"represented_phosphate_groups":{"ATP":3,"ADP":2,"CP":1}},
    "NDK":{"adenylate_group":{"ATP":1,"ADP":1},"guanylate_group":{"GTP":1,"GDP":1},"represented_phosphate_groups":{"ATP":3,"ADP":2,"GTP":3,"GDP":2}},
    "MK":{"adenylate_group":{"ATP":1,"ADP":1,"AMP":1},"represented_phosphate_groups":{"ATP":3,"ADP":2,"AMP":1}},
    "PPiase":{"represented_phosphate_groups":{"PPi":2,"PO4":1}},
}


def matrix(species, reactions):
    return sp.Matrix([[sp.Rational(str(r["products"].get(s,0)))-sp.Rational(str(r["reactants"].get(s,0))) for r in reactions] for s in species])


def exact_json(m):
    return [[str(x) for x in row] for row in m.tolist()]


def cycles(unit, reactions):
    graph = nx.DiGraph()
    states = set(unit["enzyme_states"])
    for r in reactions:
        er,ep=set(r["reactants"])&states,set(r["products"])&states
        if len(er)!=1 or len(ep)!=1:
            continue
        u,v=next(iter(er)),next(iter(ep))
        if graph.has_edge(u,v):
            raise ValueError("Parallel enzyme transitions need multigraph enumeration")
        graph.add_edge(u,v,reaction=r)
    answer=[]
    for nodes in nx.simple_cycles(graph):
        rs=[graph[nodes[i]][nodes[(i+1)%len(nodes)]]["reaction"] for i in range(len(nodes))]
        delta={s:sum(r["products"].get(s,0)-r["reactants"].get(s,0) for r in rs) for s in unit["boundary_species"]}
        scale=None
        for s,v in NET[unit["name"]].items():
            q=Fraction(delta[s],v)
            if scale is None: scale=q
            elif scale!=q: scale="INDEPENDENT";break
        status="ZERO_BOUNDARY" if not any(delta.values()) else "INDEPENDENT" if scale=="INDEPENDENT" else "FORWARD" if scale and scale>0 else "REVERSE" if scale and scale<0 else "INDEPENDENT"
        ids=[r["id"] for r in rs]
        pivot=ids.index(min(ids));ids=ids[pivot:]+ids[:pivot]
        answer.append({"reaction_ids":ids,"boundary_projection":delta,"net_multiple":str(scale),"classification":status,"flux_witness":"Every listed directed channel has flux 1; all others 0"})
    return sorted(answer,key=lambda row:(row["classification"],len(row["reaction_ids"]),row["reaction_ids"]))


def checks(unit, reactions, all_reactions):
    rows=[r for r in reactions if r["id"] in unit["active_reaction_ids"]]
    states,boundary=unit["enzyme_states"],unit["boundary_species"]
    si,sb=matrix(states,rows),matrix(boundary,rows)
    null=sp.Matrix.hstack(*si.nullspace())
    projected=sb*null
    stoich=sb.col_join(si)
    species=boundary+states
    allrows=[r for r in reactions if r["id"] in unit["reaction_ids"]]
    moieties={"live_enzyme_total":{s:1 for s in states}}
    for label,free in MOIETY[unit["name"]].items():
        weights={s:free.get(s,0) for s in boundary}
        weights.update({state:sum(free.get(s,0)*v for s,v in comp.items()) for state,comp in unit["resource_composition"].items()})
        moieties[label]={s:v for s,v in weights.items() if v}
    moietychecks={}
    for label,weights in moieties.items():
        vector=sp.Matrix([[weights.get(s,0) for s in species]])
        residual=vector*stoich
        bad={r["id"]:sum(weights.get(s,0)*(r["products"].get(s,0)-r["reactants"].get(s,0)) for s in set(r["reactants"])|set(r["products"])) for r in allrows}
        bad={rid:v for rid,v in bad.items() if v}
        moietychecks[label]={"coefficients":weights,"active_symbolic_residual":exact_json(residual),"active_conserved":residual==sp.zeros(1,len(rows)),"all_channel_nonzero_residuals":bad,"initial_inventory":sum(weights.get(s,0)*all_reactions["initial"][s] for s in weights)}
    mw=sp.Matrix([[weights.get(s,0) for s in species] for weights in moieties.values()])
    allsi=matrix(states,allrows)
    allsb=matrix(boundary+unit["degraded_states"],allrows)
    allnull=sp.Matrix.hstack(*allsi.nullspace())
    active_cycles=cycles(unit,rows)
    declared_non_degradation=[r for r in allrows if r["family"]!="RFAM_DEG"]
    all_cycles=cycles(unit,declared_non_degradation)
    # Boundary resource-total coordinates T=B+C*I have an exact catalytic ledger
    # even while bound intermediates accumulate. Free concentrations lack this.
    comp=sp.Matrix([[unit["resource_composition"][s][b] for s in states] for b in boundary])
    projection=sb+comp*si
    source_catalytic=[r["id"] for r in declared_non_degradation if not (set(r["reactants"])|set(r["products"]))&set(boundary)]
    channel_ledger={r["id"]:{b:int(projection[i,j]) for i,b in enumerate(boundary)} for j,r in enumerate(rows)}
    cat_vectors={}
    for rid in source_catalytic:
        r=next(r for r in allrows if r["id"]==rid)
        source,target=next(iter(r["reactants"])),next(iter(r["products"]))
        vector={b:unit["resource_composition"][target][b]-unit["resource_composition"][source][b] for b in boundary}
        cat_vectors[rid]=vector
    ledger_residuals={}
    for rid,vector in channel_ledger.items():
        expected=cat_vectors.get(rid,{b:0 for b in boundary})
        ledger_residuals[rid]={b:vector[b]-expected[b] for b in boundary}
    ledger_exact=not any(v for row in ledger_residuals.values() for v in row.values())
    weights={s:1 for s in states+unit["degraded_states"]}
    degradation_enzyme_residual={r["id"]:sum(weights.get(s,0)*(r["products"].get(s,0)-r["reactants"].get(s,0)) for s in weights) for r in allrows}
    outside=[r["id"] for r in all_reactions["reactions"] if r["k"]>0 and r["id"] not in unit["reaction_ids"] and (set(r["reactants"])|set(r["products"]))&set(states)]
    rank=projected.rank()
    decision="MULTIPLE_NET_DIRECTIONS_REQUIRED" if rank>1 or any(c["classification"]=="INDEPENDENT" for c in active_cycles) else "ONE_NET_DIRECTION_SUPPORTED" if rank==1 else "INSUFFICIENT_EVIDENCE"
    return {"name":unit["name"],"decision":decision,"active_channel_count":len(rows),"internal_species":states,"boundary_species":boundary,"active_internal_rank":si.rank(),"active_nullspace_dimension":null.cols,"active_boundary_projection_rank":rank,"active_full_stoichiometric_rank":stoich.rank(),"active_left_nullity":len(species)-stoich.rank(),"moiety_basis_rank":mw.rank(),"moiety_basis_complete_for_declared_unit":mw.rank()==len(species)-stoich.rank(),"active_internal_matrix":exact_json(si),"active_boundary_matrix":exact_json(sb),"active_nullspace_basis":exact_json(null),"projected_nullspace_basis":exact_json(projected),"active_reaction_order":[r["id"] for r in rows],"net_stoichiometry":NET[unit["name"]],"active_directed_cycles":active_cycles,"active_cycle_counts":dict(Counter(r["classification"] for r in active_cycles)),"declared_all_nondegradation_cycle_counts":dict(Counter(r["classification"] for r in all_cycles)),"source_catalytic_channels":source_catalytic,"moieties":moietychecks,"exact_resource_total_channel_ledger":channel_ledger,"resource_total_identity_symbolic_residual":ledger_residuals,"resource_total_identity_exact":ledger_exact,"enzyme_pool_full_author_active_network_conserved":not outside,"outside_active_enzyme_interfaces":outside,"all_channel_comparison":{"internal_rank":allsi.rank(),"signed_nullspace_dimension":allnull.cols,"signed_boundary_projection_rank":(allsb*allnull).rank(),"degraded_species_included_as_boundary":unit["degraded_states"],"nonnegative_stationary_degradation_flux":"Exactly zero: summing all live-enzyme rows yields minus sum of directed degradation fluxes; nonnegative stationary balance forces each to vanish.","live_plus_degraded_enzyme_residuals":degradation_enzyme_residual,"declared_cycles":all_cycles,"meaning":"Signed nullspace permits unphysical reverse degradation currents. Degradation activation is a transient catalyst-loss problem, not a stationary catalytic cycle."}}


def write_csv(path,rows):
    with path.open("w",newline="",encoding="utf-8") as stream:
        writer=csv.DictWriter(stream,list(rows[0]),lineterminator="\n")
        writer.writeheader();writer.writerows(rows)


def equation(side):
    return " + ".join((str(v)+" " if v!=1 else "")+s for s,v in sorted(side.items())) or "0"


def main():
    data=build_inventory();DOC.mkdir(parents=True,exist_ok=True);RESULT.mkdir(parents=True,exist_ok=True)
    result=[checks(u,data["reactions"],data) for u in data["units"]]
    for result_unit in result:
        if result_unit["decision"]!="ONE_NET_DIRECTION_SUPPORTED" or not result_unit["resource_total_identity_exact"] or not result_unit["moiety_basis_complete_for_declared_unit"] or not all(p["active_conserved"] for p in result_unit["moieties"].values()):
            raise ValueError("STRUCTURAL_CERTIFICATE_FAILURE: "+result_unit["name"])
    selected=set(data["SmallMolecules_reaction_ids"])|{r for u in data["units"] for r in u["reaction_ids"]}
    ownership={rid:u for u in data["units"] for rid in u["reaction_ids"]}
    inventory=[];edges=[]
    for r in data["reactions"]:
        if r["id"] not in selected:continue
        u=ownership.get(r["id"])
        categories={s:"INTERNAL_LIVE_ENZYME" if u and s in u["enzyme_states"] else "BOUNDARY_DEGRADED_ENZYME" if u and s in u["degraded_states"] else "BOUNDARY_FREE_RESOURCE" for s in set(r["reactants"])|set(r["products"])}
        inventory.append({"candidate_reduction_unit":u["name"] if u else "SMALL_MOLECULES_DISABLED_INTERFACE","source_subsystem_id":";".join(r["subsystems"]),"source_subsystem_file":";".join(sorted({p["file"] for p in r["provenance"]})),"reaction_family_id":r["family"],"original_directed_reaction_id":r["id"],"reactants_exact_json":json.dumps(r["reactants"],sort_keys=True),"products_exact_json":json.dumps(r["products"],sort_keys=True),"kinetic_law":r["kinetic_law"],"author_reference_parameter":r["k"],"reference_status":r["reference_activity"],"reverse_partner":r["reverse_partner"] or "","level_c_memberships":";".join(r["level_c"]),"boundary_internal_classification_json":json.dumps(categories,sort_keys=True),"enzyme_occupancy_composition_json":json.dumps({s:u["resource_composition"][s] for s in categories if u and s in u["resource_composition"]},sort_keys=True),"free_resource_delta_json":json.dumps({s:r["products"].get(s,0)-r["reactants"].get(s,0) for s in (u["boundary_species"] if u else categories)},sort_keys=True),"classification_reason":"Live enzyme state and bound composition proven by complete connected binding topology; named boundary free resources retained. Degraded sink separated by active topology." if u else "No catalyst; all author-reference parameters zero. Activating hydrolysis/synthesis adds boundary transformations.","source_provenance_json":json.dumps(r["provenance"],sort_keys=True),"source_sbml_sha256":data["source_hashes"]["models/pnas2017_full_reference/original/fMGG_synthesis.xml"]})
        for role,side in (("reactant",r["reactants"]),("product",r["products"])):
            for s,c in side.items():
                edges.append({"unit":u["name"] if u else "SmallMolecules","reaction_id":r["id"],"from_node":"species:"+s if role=="reactant" else "reaction:"+r["id"],"to_node":"reaction:"+r["id"] if role=="reactant" else "species:"+s,"role":role,"coefficient_exact":c,"activity":r["reference_activity"],"species_class":categories[s],"reverse_partner":r["reverse_partner"] or "","evidence":"EXTRACTED_CANONICAL_MATHML_STOICHIOMETRY"})
    write_csv(DOC/"reaction_inventory.csv",inventory);write_csv(DOC/"topology_edges.csv",edges)
    source_path=RESULT/"source_inventory.json"
    source_path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    # Combined four-unit rank, and all-channel SmallMolecules interface comparison.
    fourstates=sorted({s for u in data["units"] for s in u["enzyme_states"]})
    fourboundary=sorted({s for u in data["units"] for s in u["boundary_species"]})
    fouractive=[r for r in data["reactions"] if r["id"] in ownership and r["k"]>0]
    fi,fb=matrix(fourstates,fouractive),matrix(fourboundary,fouractive)
    fn=sp.Matrix.hstack(*fi.nullspace())
    small=[r for r in data["reactions"] if r["id"] in data["SmallMolecules_reaction_ids"]]
    extended_boundary=sorted(set(fourboundary)|set().union(*(set(r["reactants"])|set(r["products"]) for r in small)))
    combined_nets=sp.Matrix([[NET[u["name"]].get(s,0) for u in data["units"]] for s in extended_boundary])
    additional=matrix(extended_boundary,small)
    report={"status":"STRUCTURE_VERIFIED_AUTHOR_REFERENCE_ACTIVE_SCOPE","source_commit":data["source_commit"],"source_hashes":data["source_hashes"],"source_inventory_sha256":digest(source_path.read_bytes()),"environment":{"python":sys.version,"platform":platform.platform(),"sympy":sp.__version__,"networkx":nx.__version__},"command":"python scripts/energy_cycles/inventory.py","units":result,"four_cycle":{"active_internal_rank":fi.rank(),"active_boundary_projection_rank":(fb*fn).rank(),"boundary_species":fourboundary,"enzyme_states":fourstates,"all_87_directed_channels":len(ownership),"active_61_channels":len(fouractive),"principal_net_matrix":exact_json(combined_nets),"principal_net_rank":combined_nets.rank()},"SmallMolecules":{"all_zero_author_reference":all(r["k"]==0 for r in small),"count":len(small),"interfaces":extended_boundary,"reaction_ids":[r["id"] for r in small],"activated_small_molecules_net_rank":additional.rank(),"activated_four_cycles_plus_small_molecules_net_rank":combined_nets.row_join(additional).rank(),"four_cycles_net_rank":combined_nets.rank(),"reason_outside_reference_units":"They contain no catalyst or enzyme-state cycle and all 12 author-reference channel parameters are zero. Enabling them changes admissible independent chemical directions."},"limitations":["Rational structure certificates do not imply time-dependent free-resource closure.","Moieties are scoped represented biochemical groups, not complete elemental/charge/ionic certificates.","Large microscopic rates do not establish time-scale separation or scientific acceptance."]}
    (DOC/"stoichiometric_checks.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    write_docs(data,result,report,small)
    print(json.dumps({"unit_boundary_ranks":{r["name"]:r["active_boundary_projection_rank"] for r in result},"cycle_counts":{r["name"]:r["active_cycle_counts"] for r in result},"SmallMolecules":report["SmallMolecules"]},indent=2))


def write_docs(data,checks,report,small):
    lines=["# PNAS2017 energy-cycle topology inventory", "", "Status: `SOURCE_VERIFIED`; active-network topology is `STRUCTURE_VERIFIED`. All reduction choices remain `HUMAN_REVIEW_REQUIRED`. Source commit `"+data["source_commit"]+"`. No original inputs or historical decisions were changed.", "", "The independent XML parser evaluates exact constant MathML stoichiometry and matches each combined reaction to the original subsystem ZIP by its complete reactant/product signature. It verifies annotation subsystem memberships, stoichiometry, reverse partners, author parameters and family consistency. The normalized compatibility copy has an identical full stoichiometric inventory, including `re0000000414 -> 2 PO4`.", "", "| Unit | Original subsystem channels | Principal family channels | Reference active | Live enzyme states |", "|---|---:|---:|---:|---:|"]
    for u in data["units"]:
        rs=[r for r in data["reactions"] if r["id"] in u["reaction_ids"]]
        lines.append(f"| {u['name']} | {len(rs)} | {sum(r['family']==u['reaction_family_id'] for r in rs)} ({u['reaction_family_id']}) | {len(u['active_reaction_ids'])} | {len(u['enzyme_states'])} |")
    categories=sorted({stage for r in data["reactions"] for stage in r["level_c"]})
    energy_ids={rid for unit in data['units'] for rid in unit['reaction_ids']}
    energy_rows=[r for r in data['reactions'] if r['id'] in energy_ids]
    deg=sum(r['family']=='RFAM_DEG' for r in energy_rows)
    active=sum(r['k']>0 for r in energy_rows)
    zero=sum(r['k']==0 for r in energy_rows)
    counts_text=(f"The {len(energy_rows)} subsystem channels include {deg} degradation channels classified `RFAM_DEG`; {zero} channels are reference-zero because the NDK catalytic reverse is additionally disabled. The stated RFAM_015–018 are principal catalytic-family labels rather than labels on every subsystem row. Total reference-active channels: {active}. All {len(data['SmallMolecules_reaction_ids'])} SmallMolecules channels are reference-zero. Source-wide reproduced counts: {len(data['species_ids'])} species, {len(data['reactions'])} reactions, {len({s for r in data['reactions'] for s in r['subsystems']})} source subsystems, {sum(v>0 for v in data['initial'].values())} positive author initial components and {sum(r['k']>0 for r in data['reactions'])} nonzero author parameters.")
    lines += ["", counts_text, "", "Level-C category count independently reproduced from reviewed annotation memberships: "+str(len(categories))+". The categories are: "+", ".join("`"+s+"`" for s in categories)+". Energy units span `EN_binding`, `EN_energy_transfer`/`EN_byproduct_processing`, and reference-disabled `DEG_sink`; categories are navigation labels rather than effective reactions.", "", "The bipartite edge list uses species→reaction reactant edges and reaction→species product edges with exact coefficients, activity, direction, and boundary/internal roles. Structural reachability is distinct from kinetic flux. All complete reaction and source-local IDs are in `reaction_inventory.csv`; all 968 source laws and author overlays are in `results/energy_cycles_v1/source_inventory.json`."]
    for u,c in zip(data["units"],checks):
        lines += ["", "## "+u["name"], "", "Source: `"+u["source_file"]+"`; principal family `"+u["reaction_family_id"]+"`. Free boundaries: "+", ".join("`"+s+"`" for s in u["boundary_species"])+".", "", "Complete live enzyme pool: `"+" + ".join(u["enzyme_states"])+"`; author initial total "+str(u["enzyme_total_initial"])+". No external author-active reaction touches this pool, so it is conserved in the full author-reference active network as well as this isolated unit.", "", "| Enzyme state | Bound resources inferred from exact binding edges |", "|---|---|"]
        for state,comp in u["resource_composition"].items():
            bound="; ".join(s+"="+str(v) for s,v in comp.items() if v) or "none (free anchor)"
            lines.append("| `"+state+"` | "+bound+" |")
        lines += ["", "Catalytic source channels: "+", ".join("`"+s+"`" for s in c["source_catalytic_channels"])+". Reference-zero channels: "+", ".join("`"+s+"`" for s in u["zero_reaction_ids"])+".", "", "Directed simple-cycle counts: "+json.dumps(c["active_cycle_counts"],sort_keys=True)+". Every enzyme-state composition follows connected association/dissociation paths from the declared free-enzyme anchor; the complete binding graph has consistent compositions, including alternative binding orders."]
        if u["name"]=="CK":lines += ["", "ADP and CP can bind in either order to CK_CP_ADP; ATP and Cr can release in either order from CK_Cr_ATP. Both catalytic conversions are active. No active independent bypass or resource-consuming futile direction exists."]
        if u["name"]=="NDK":lines += ["", "ATP/GDP binding and ADP/GTP release each branch through both orders. `re0000000364` is the exact catalytic reverse partner but has author k=0. All binding reverse directions remain present; they do not restore reverse net chemistry when the chemical reverse channel is disabled."]
        if u["name"]=="MK":lines += ["", "ATP/AMP binding branches; two distinct one-ADP occupancy states provide alternative product-release orders. MK_ADP_ADP carries two bound ADP molecules. Disabled degradation `re0000000401` releases only one ADP, and `re0000000400` releases ATP without its bound AMP. These exact source effects are retained and would violate the represented nucleotide ledger if activated."]
        if u["name"]=="PPiase":lines += ["", "Complete pathway: PPi binding 405/406; bound conversion 407/408; first PO4 release 409/410; second PO4 release 411/412. Two distinct product-release events yield two free PO4. Contrary to a strictly irreversible conceptual shorthand, source k408=140, k410=0.059 and k412=0.26 support the complete reverse path. Degradation 414 releases two PO4 through its MathML coefficient."]
    lines += ["", "## Reference-disabled SmallMolecules interfaces", "", "| ID | Source equation | Author k |", "|---|---|---:|"]
    for r in small:lines.append(f"| `{r['id']}` | {equation(r['reactants'])} → {equation(r['products'])} | {r['k']} |")
    lines += ["", "The extra free species GMP connects only through these disabled small-molecule channels in this scope. Activating SmallMolecules increases the combined independent boundary net rank from "+str(report["SmallMolecules"]["four_cycles_net_rank"])+" to "+str(report["SmallMolecules"]["activated_four_cycles_plus_small_molecules_net_rank"])+"; four principal net reactions cannot then cover the chemical directions.", "", "## Provenance and limits", "", "Source hashes and original ZIP-member hashes are retained in the JSON and row-level inventory. Canonical combined SBML all-one initial concentrations and k values are structural inputs; execution must use the separately identified author CSV overlay. Parameter and concentration/time units remain unresolved in source metadata. No H2O, H+, Mg2+ or unrepresented chemical species is added."]
    (DOC/"topology_inventory.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    lines=["# Exact energy-cycle stoichiometric reduction certificate", "", "Status: `STRUCTURE_VERIFIED` under fixed author-reference active-channel assumptions. This certificate establishes admissible net chemistry and exact resource identities. It does not establish kinetic lumpability, QSSA, time-scale separation or scientific acceptance.", "", "For each unit B consists of the declared free-resource boundary; I contains the entire live enzyme pool including the free enzyme. Exact rational matrices satisfy `S_I j=0`; the rank of `S_B ker(S_I)` is computed without floating-point tolerances. Nonnegative flux feasibility is independently established by directed simple-cycle enumeration: every stationary nonnegative enzyme-transition flow decomposes into those cycles.", "", "| Unit | rank S_I | dim ker S_I | Boundary rank | Active signed net directions | Decision |", "|---|---:|---:|---:|---|---|"]
    for c in checks:
        directions="forward and reverse" if c["active_cycle_counts"].get("REVERSE",0) else "forward only"
        lines.append(f"| {c['name']} | {c['active_internal_rank']} | {c['active_nullspace_dimension']} | {c['active_boundary_projection_rank']} | {directions} | ONE_NET_DIRECTION_SUPPORTED |")
    lines += ["", "All active simple cycles project to zero or an integer multiple of the stated net direction; there are no independent bypass directions. Zero-boundary loops include association/dissociation excursions and alternate binding-order cycles. They can occupy enzyme and exchange microscopic flux without net chemical conversion; this is not source-certified fuel-consuming hydrolysis. Rational nullspace bases, projected bases, all nonnegative directed cycle witnesses and exact conserved-pool coefficients are supplied in `stoichiometric_checks.json`."]
    for u,c in zip(data["units"],checks):
        lines += ["", "## "+u["name"], "", "Exact net vector: `"+equation({s:-v for s,v in c["net_stoichiometry"].items() if v<0})+" -> "+equation({s:v for s,v in c["net_stoichiometry"].items() if v>0})+"`. Active cone direction: "+("both signs" if c["active_cycle_counts"].get("REVERSE",0) else "nonnegative forward sign only")+".", "", "| Conserved represented pool | Exact nonzero species coefficients |", "|---|---|"]
        for label,m in c["moieties"].items():lines.append("| "+label+" | `"+" + ".join((str(v)+"*" if v!=1 else "")+s for s,v in m["coefficients"].items())+"` |")
        lines += ["", "Every listed pool has zero symbolic active residual. Their independent rank "+str(c["moiety_basis_rank"])+" equals full active left nullity "+str(c["active_left_nullity"])+", so they span the conserved linear pool space of this declared isolated unit. Phosphate-group coefficients use represented nucleotide identities (ATP3, ADP2, AMP1, GTP3, GDP2, CP1, PPi2, PO4 1) and do not assert complete molecular formula or ionic conservation.", "", "One explicit forward stationary nonnegative cycle: "+" + ".join("`"+s+"`" for s in next(x for x in c["active_directed_cycles"] if x["classification"]=="FORWARD")["reaction_ids"])+" (each channel flux=1)."]
        reverse=[x for x in c["active_directed_cycles"] if x["classification"]=="REVERSE"]
        if reverse:lines.append("Reverse witness: "+" + ".join("`"+s+"`" for s in reverse[0]["reaction_ids"])+".")
        ac=c["all_channel_comparison"]
        lines += ["", "When disabled degradation is admitted, signed-nullspace boundary rank becomes "+str(ac["signed_boundary_projection_rank"])+". However, stationary nonnegative live-enzyme balance forces every degradation flux to zero: sum of the live-enzyme rows is minus the sum of degradation currents. Allowing degradation in a transient model depletes the catalytic pool; live+degraded enzyme count remains conserved, but a constant live enzyme total cannot be used."]
        if u["name"]=="MK":lines += ["", "The all-channel signed rank is three because disabled source degradation releases incomplete bound resources. `re0000000400` loses one adenylate/phosphate group (bound AMP); `re0000000401` loses one adenylate and two phosphate groups (bound ADP). Exact active conservation is valid; activating these source channels would invalidate those resource pools. No canonical correction is made."]
    lines += ["", "## Dynamic versus steady identities", "", "Let C map live enzyme states to their bound free-resource inventory, inferred from binding paths. The physical total-resource coordinates are `T=x_B+C*x_I`. Exact source algebra gives `(S_B+C*S_I)j = nu*(j_cat_forward-j_cat_reverse)` for every active channel, without internal stationarity. Binding contributes zero to this total ledger. Therefore `dx_B/dt = nu*j_cat - C*dx_I/dt`: free boundary resource dynamics differ from catalytic net conversion during accumulation or release of bound intermediates. The exact channel ledger is included in JSON. A reduced model must reconstruct C*x_I or retain a storage state if free-resource timing is a required observable.", "", "The steady relation `S_I j=0` removes that storage derivative; it does not justify eliminating dynamic enzyme occupancy. Four net reactions give four independent chemical directions among nine retained free-resource coordinates, and 25 live enzyme occupancy coordinates constrained by four catalyst totals; they do not imply four dynamic states.", "", "## Coupled directions and disabled interfaces", "", "The four-cycle active internal rank is "+str(report["four_cycle"]["active_internal_rank"])+"; coupled boundary projection rank is "+str(report["four_cycle"]["active_boundary_projection_rank"])+". Their shared ATP/ADP pools are represented once. Adding all 12 SmallMolecules channels raises admissible net rank to "+str(report["SmallMolecules"]["activated_four_cycles_plus_small_molecules_net_rank"])+", so that extension requires additional net reactions. The author-reference overlay keeps those channels zero."]
    (DOC/"stoichiometric_certificate.md").write_text("\n".join(lines)+"\n",encoding="utf-8")


if __name__=="__main__":main()

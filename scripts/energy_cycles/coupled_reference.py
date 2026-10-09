"""Frozen E3 microscopic source diagnostics, independent RoadRunner engine.

Read the already verified constant-stoichiometry compatibility copy; overlay
author initial/parameter values in a derived results-only execution XML. No
candidate replacement or reduced comparison is executed here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time
import xml.etree.ElementTree as ET

import numpy as np
import roadrunner

ROOT=Path(__file__).resolve().parents[2]
REG=ROOT/"docs/reduction/energy_cycles/validation_preregistration.json"
INVENTORY=ROOT/"results/energy_cycles_v1/source_inventory.json"
OUTPUT=ROOT/"results/energy_cycles_v1/coupled_reference"
NS="{http://www.sbml.org/sbml/level2/version4}"
NET={"CK":{"CP":-1,"ADP":-1,"Cr":1,"ATP":1},"NDK":{"ATP":-1,"GDP":-1,"ADP":1,"GTP":1},"MK":{"ATP":-1,"AMP":-1,"ADP":2},"PPiase":{"PPi":-1,"PO4":2}}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def derived_xml(data,initial):
    normalized=ROOT/"models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml"
    if sha(normalized)!=data["source_hashes"][str(normalized.relative_to(ROOT)).replace("\\","/")]:
        raise RuntimeError("Normalized compatibility source hash drift")
    root=ET.fromstring(normalized.read_bytes());model=root.find(NS+"model")
    energy={rid for u in data["units"] for rid in u["reaction_ids"]}
    params={r["id"]:r["k"] for r in data["reactions"]}
    for element in model.find(NS+"listOfSpecies"):
        element.set("initialConcentration",format(initial[element.get("id")],".17g"))
    zeroed=[]
    for reaction in model.find(NS+"listOfReactions"):
        rid=reaction.get("id")
        value=params[rid] if rid in energy else 0.
        if rid not in energy:zeroed.append(rid)
        reaction.find(NS+"kineticLaw/"+NS+"listOfParameters/"+NS+"parameter").set("value",format(value,".17g"))
    return ET.tostring(root,encoding="utf-8",xml_declaration=True),zeroed


def engine_run(xml,data,grid,rtol,atol):
    start=time.monotonic();rr=roadrunner.RoadRunner(xml.decode("utf-8"))
    rr.integrator="cvode";rr.integrator.stiff=True
    rr.integrator.relative_tolerance=rtol;rr.integrator.absolute_tolerance=atol
    rr.integrator.maximum_num_steps=1000000
    rr_species=list(rr.model.getFloatingSpeciesIds());rr_reactions=list(rr.model.getReactionIds())
    if set(rr_species)!=set(data["species_ids"]) or set(rr_reactions)!={r["id"] for r in data["reactions"]}:
        raise RuntimeError("Imported source species/reaction identity mismatch")
    expected=np.zeros((len(rr_species),len(rr_reactions)))
    for r in data["reactions"]:
        j=rr_reactions.index(r["id"])
        for sign,side in ((-1,"reactants"),(1,"products")):
            for s,c in r[side].items():expected[rr_species.index(s),j]+=sign*c
    actual=np.asarray(rr.getFullStoichiometryMatrix())
    if not np.array_equal(actual,expected):raise RuntimeError("Imported engine stoichiometry differs from exact source inventory")
    species=data["species_ids"]
    energy=[r for r in data["reactions"] if any(r["id"] in u["reaction_ids"] for u in data["units"])]
    rates=[r["id"] for r in energy]
    selections=["time"]+["["+s+"]" for s in species]+rates
    values=np.asarray(rr.simulate(times=grid.tolist(),selections=selections))
    if values.shape!=(len(grid),len(selections)) or not np.array_equal(values[:,0],grid):
        raise RuntimeError("RoadRunner output identity/grid mismatch")
    if not np.all(np.isfinite(values)):raise RuntimeError("Nonfinite source trajectory")
    return values,{"engine":"libRoadRunner","version":roadrunner.__version__,"integrator":"CVODE","stiff":True,"relative_tolerance":rtol,"absolute_tolerance":atol,"maximum_num_steps":1000000,"elapsed_seconds":time.monotonic()-start,"full241_by968_stoichiometric_matrix_exact_equal":True,"PO4_product_coefficient_re0000000414":float(actual[rr_species.index("PO4"),rr_reactions.index("re0000000414")]),"source_unit_warnings":"Explicit physical concentration/rate dimensions remain unresolved"},rates


def resource_map(data):
    boundary=sorted({s for u in data["units"] for s in u["boundary_species"]})
    species=data["species_ids"]
    A=np.zeros((len(boundary),len(species)))
    for i,s in enumerate(boundary):A[i,species.index(s)]=1
    for u in data["units"]:
        for state,composition in u["resource_composition"].items():
            for s,coefficient in composition.items():A[boundary.index(s),species.index(state)]+=coefficient
    N=np.array([[NET[u["name"]].get(s,0) for u in data["units"]] for s in boundary],float)
    return boundary,A,N


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--condition",choices=["AUTHOR_BASELINE","SHARED_LIMITATION"],required=True)
    args=parser.parse_args()
    if not REG.exists():raise RuntimeError("Preregistration must exist before any execution")
    reg=json.loads(REG.read_text());data=json.loads(INVENTORY.read_text())
    for relative,expected in reg["implementation_sha256"].items():
        if sha(ROOT/relative)!=expected:raise RuntimeError("Frozen candidate code drift: "+relative)
    for relative,expected in reg["source_hashes"].items():
        if sha(ROOT/relative)!=expected:raise RuntimeError("Frozen source drift: "+relative)
    cfg=reg["source_reference_diagnostics"]
    if args.condition not in cfg["E3_conditions"]:raise RuntimeError("Condition absent from preregistration")
    initial=dict(data["initial"])
    if args.condition=="SHARED_LIMITATION":initial.update(cfg["E3_conditions"][args.condition])
    grid=np.asarray(reg["comparison_grid"],float)
    xml,zeroed=derived_xml(data,initial)
    path=OUTPUT/args.condition;path.mkdir(parents=True,exist_ok=True)
    execution=path/"derived_source_execution.xml";execution.write_bytes(xml)
    base,solver,rates=engine_run(xml,data,grid,cfg["relative_tolerance"],cfg["absolute_tolerance"])
    tight,tightsolver,_=engine_run(xml,data,grid,cfg["tight_relative_tolerance"],cfg["tight_absolute_tolerance"])
    species=data["species_ids"];n=len(species);x=base[:,1:n+1];xt=tight[:,1:n+1]
    boundary,A,N=resource_map(data);T=x@A.T;Tt=xt@A.T
    extent=(np.linalg.pinv(N)@(T-T[0]).T).T
    extent_tight=(np.linalg.pinv(N)@(Tt-Tt[0]).T).T
    storage=x@(A-np.array([[int(s==b) for s in species] for b in boundary])).T
    poolchecks={}
    for u in data["units"]:
        pool=x[:,[species.index(s) for s in u["enzyme_states"]]].sum(axis=1)
        poolchecks[u["name"]]={"initial":float(pool[0]),"max_normalized_drift":float(np.max(np.abs(pool-pool[0]))/max(abs(pool[0]),1.))}
    free_scale=np.array([max(initial[s],1.) for s in boundary])
    uncertainty=float(np.max(np.abs(x[:,[species.index(s) for s in boundary]]-xt[:,[species.index(s) for s in boundary]])/free_scale))
    chemical_flux={}
    for u in data["units"]:
        indices=[rates.index(rid) for rid in u["catalytic_pair"]]
        f=base[:,n+1+indices[0]];rev=base[:,n+1+indices[1]] if len(indices)>1 else np.zeros(len(grid))
        chemical_flux[u["name"]]={"max_absolute_net_current":float(np.max(np.abs(f-rev))),"endpoint_net_extent_from_complete_resource_pools":float(extent[-1,data["units"].index(u)]),"endpoint_forward_current":float(f[-1]),"endpoint_reverse_current":float(rev[-1])}
    trajectory=path/"trajectories.npz"
    np.savez_compressed(trajectory,time=grid,species_ids=np.array(species),reaction_ids=np.array(rates),microscopic=x,microscopic_tight=xt,microscopic_source_flux=base[:,n+1:],microscopic_tight_source_flux=tight[:,n+1:],boundary_species=np.array(boundary),retained_total_resource=T,bound_resource=storage,net_extent_from_pools=extent,net_extent_from_pools_tight=extent_tight,net_matrix=N,total_resource_map=A)
    residual=float(np.max(np.abs(T-T[0]-extent@N.T)))
    report={"status":"MICROSCOPIC_COUPLED_REFERENCE_DIAGNOSTIC_ONLY","condition":args.condition,"candidate_compared":False,"source_commit":reg["source_commit"],"source_hashes":reg["source_hashes"],"author_input_members":data["author_input_members"],"preregistration_sha256":sha(REG),"script_sha256":sha(Path(__file__)),"environment":{"python":sys.version,"executable":sys.executable,"platform":platform.platform(),"numpy":np.__version__,"roadrunner":roadrunner.__version__},"command":sys.argv,"initial_conditions":initial,"parameter_set":"Unmodified author CSV on original87 energy channels; all other881 directed channels disabled in results-only derived isolated execution","reference_active_energy_channels":sum(r["k"]>0 for r in data["reactions"] if r["id"] in rates),"all87_reaction_ids":rates,"nonenergy_zeroed_reaction_ids":zeroed,"source_execution_xml":{"path":str(execution.relative_to(ROOT)).replace("\\","/"),"sha256":sha(execution)},"trajectory":{"path":str(trajectory.relative_to(ROOT)).replace("\\","/"),"sha256":sha(trajectory)},"solver":solver,"solver_tight":tightsolver,"minimum_unclipped_species":float(min(np.min(x),np.min(xt))),"maximum_scaled_free_solver_uncertainty":uncertainty,"enzyme_pool_conservation":poolchecks,"exact_net_extent_mapping_balance_residual":residual,"catalytic_flows":chemical_flux,"limitations":["No reduced model is compared; source execution cannot validate a candidate.","Net cumulative extents are reconstructed from exact complete resource-pool balance at t=0, not by treating binding as chemistry.","No forward/reverse gross cumulative integral is claimed by this source diagnostic.","Absolute source concentration/time units remain unresolved."]}
    write_json(path/"run_manifest.json",report)
    summary=json.dumps({"condition":args.condition,"status":report["status"],"uncertainty":uncertainty,"minimum":report["minimum_unclipped_species"],"catalytic_flows":chemical_flux,"enzyme_pool_conservation":poolchecks},indent=2)
    (path/"run.stdout.log").write_text(summary+"\n",encoding="utf-8")
    print(summary,flush=True)


if __name__=="__main__":main()

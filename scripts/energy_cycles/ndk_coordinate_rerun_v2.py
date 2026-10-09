"""Additive engineering reruns: exact NDK coordinate, unchanged scientific study."""
import json
import sys
import time
import traceback
import numpy as np
from runtime import Module,ROOT,OUT,REG,sha,write_json,integrate_micro,compare,observations
from ndk_depletion_coordinate import integrate_reduced_ndk

def main():
    reg=json.loads(REG.read_text());add=ROOT/'docs/reduction/energy_cycles/ndk_numerical_repair_preregistration_v2.json';a=json.loads(add.read_text())
    if sha(REG)!=a['original_preregistration_sha256']:raise RuntimeError('Original registration changed')
    for f,v in a['implementation_sha256'].items():
        if sha(ROOT/f)!=v:raise RuntimeError('Repair code changed after freeze')
    for f,v in reg['implementation_sha256'].items():
        if sha(ROOT/f)!=v:raise RuntimeError('Scientific candidate code changed after freeze')
    d=json.loads((OUT/'source_inventory.json').read_text());unit=next(u for u in d['units'] if u['name']=='NDK');m=Module(d,unit);grid=np.array(reg['comparison_grid'])
    for cid in a['rerun_case_ids']:
        case=next(c for c in reg['scenarios'] if c['id']==cid);dest=OUT/'numerical_ndk_coordinate_v2'/cid
        if dest.exists():raise RuntimeError('Do not overwrite repaired evidence')
        try:
            E=case['enzyme_total'];x0=np.array([case['initial_original'][s] for s in m.species]);T0=m.A@x0;xp,_,_,_=m.closure(T0,E)
            roots=[];rejected=[]
            for f in reg['solver']['initial_multistart_fractions']:
                try:roots.append(m.closure(T0,E,T0*f)[0])
                except Exception as err:rejected.append(str(err))
            spread=max([float(np.max(abs(xx-xp))) for xx in roots]+[0.])
            if spread>1e-7:raise RuntimeError('Distinct physical initial roots')
            base_red,curr,rs=integrate_reduced_ndk(m,T0,E,grid,1e-8,1e-10)
            tight_red,_,rts=integrate_reduced_ndk(m,T0,E,grid,1e-10,1e-12)
            for mode in case['initial_modes']:
                start=time.monotonic();initial=x0 if mode=='ORIGINAL_NONEQUILIBRIUM' else xp;path=dest/mode
                base,bs=integrate_micro(m,initial,grid,1e-8,1e-10,'Radau');tight,ts=integrate_micro(m,initial,grid,1e-10,1e-12,'Radau');bdf,bds=integrate_micro(m,initial,grid,1e-10,1e-12,'BDF')
                result=compare(m,case,mode,reg,grid,base,tight,bdf,base_red,tight_red,{'reference':bs,'reference_tight':ts,'independent_BDF':bds,'candidate':rs,'candidate_tight':rts,'initial_multistart_root_spread':spread,'failed_multistart_seeds':rejected})
                path.mkdir(parents=True);trajectory=path/'trajectories.npz'
                np.savez_compressed(trajectory,time=grid,species=np.array(m.species),reaction_ids=np.array([m.reactions[j]['id'] for j in m.active]),microscopic=base,microscopic_tight=tight,microscopic_independent_bdf=bdf,reduced=base_red,reduced_tight=tight_red,
                    microscopic_active_flux=observations(m,base)['all_active_source_flux'],reconstructed_active_flux=observations(m,base_red)['all_active_source_flux'],net_stoichiometry=m.N,total_mapping=m.A,bound_mapping=m.C)
                result.update({'trajectory':{'path':str(trajectory.relative_to(ROOT)).replace('\\','/'),'sha256':sha(trajectory),'quadrature_columns':['forward_extent','reverse_extent']},
                    'preregistration_sha256':sha(REG),'engineering_addendum_sha256':sha(add),'engineering_implementation_sha256':a['implementation_sha256'],
                    'preserved_native_failure':str((OUT/'numerical'/cid/'failure.json').relative_to(ROOT)).replace('\\','/'),'wall_seconds':time.monotonic()-start})
                write_json(path/'metrics.json',result)
                print(json.dumps({'case':cid,'mode':mode,'status':result['scientific_status'],'long':result['windows'][-1],'coordinate_defect':rs['maximum_extent_coordinate_vs_direct_quadrature_error']}),flush=True)
        except Exception as err:
            write_json(dest/'failure.json',{'id':cid,'scientific_status':'BLOCKED','error':str(err),'traceback':traceback.format_exc(),'preregistration_sha256':sha(REG),'engineering_addendum_sha256':sha(add)})
            print(json.dumps({'case':cid,'status':'BLOCKED','reason':str(err)}),flush=True)

if __name__=='__main__':main()

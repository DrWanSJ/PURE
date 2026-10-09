"""Freeze v1 comparisons before evaluating any microscopic/reduced outcome."""
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/reduction/energy_cycles'
OUT = ROOT/'results/energy_cycles_v1'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    path=DOC/'validation_preregistration.json'
    if path.exists():
        raise RuntimeError('Preregistration already frozen; never overwrite')
    d=json.loads((OUT/'source_inventory.json').read_text())
    scenarios=[]
    substrate_lists={'CK':['CP','ADP'],'NDK':['ATP','GDP'],'MK':['ATP','AMP'],'PPiase':['PPi']}
    grid=np.unique(np.r_[0,np.geomspace(1e-8,.05,101),np.geomspace(.05,1,61),np.geomspace(1,1000,201)])
    for unit in d['units']:
        name=unit['name']; E=unit['enzyme_total_initial']; B=unit['boundary_species']
        authored={s:d['initial'][s] for s in B}
        challenge={s:(authored[s] if authored[s]>0 else max(100.,10*E)) for s in B}
        configs=[('AUTHOR_BASELINE',authored,1.,'Exact author free-resource and catalyst inventories; isolated net catalysis may be dormant.'),
                 ('POSITIVE_CHALLENGE',challenge,1.,'Explicit positive challenge supplies author-absent pools; no claim of author baseline.')]
        for factor,label in ((.5,'HALF'),(2.,'DOUBLE')):
            configs.append(('AUTHOR_CATALYST_'+label,authored,factor,'Individual catalyst perturbation on authored pools.'))
            configs.append(('CHALLENGE_CATALYST_'+label,challenge,factor,'Individual catalyst perturbation on positive challenge.'))
            for s in substrate_lists[name]:
                x=dict(challenge);x[s]*=factor
                configs.append(('CHALLENGE_'+s+'_'+label,x,1.,'Individual substrate perturbation; avoids multiplying a zero authored pool.'))
        low=dict(challenge);low[substrate_lists[name][0]]=.01*E
        configs.append(('LOW_FUEL',low,1.,'Fuel inventory comparable to or below catalyst; retained as domain stress.'))
        rich={s:.1*challenge[s] for s in B}
        for s in B:
            if s not in substrate_lists[name]:rich[s]=10*challenge[s]
        configs.append(('PRODUCT_RICH',rich,1.,'Source-supported reverse driving/product inhibition; NDK reverse remains zero.'))
        limited=dict(challenge)
        for s in substrate_lists[name]:limited[s]=.1*E
        configs.append(('COUPLED_RESOURCE_LIMITATION',limited,1.,'Simultaneous limiting reactant pools within the isolated unit; separate network-coupling stage.'))
        corner={s:0. for s in B}
        for s in substrate_lists[name]:corner[s]=challenge[s]
        configs.append(('ZERO_PRODUCT_CORNER',corner,1.,'Predeclared physically valid microscopic state that can be outside all-enzyme stationary total-closure domain.'))
        for sid,resources,factor,note in configs:
            initial={s:d['initial'][s] for s in unit['all_species']}
            initial.update(resources)
            initial[unit['free_enzyme']]=E*factor
            # The author's enzyme complexes are initially zero in this source.
            assert all(initial[s]==0 for s in unit['enzyme_states'] if s!=unit['free_enzyme'])
            scales={s:max(resources[s],E*factor,1.) for s in B}
            limiting=min(resources[s] for s in substrate_lists[name])
            scenarios.append({'id':name+'__'+sid,'unit':name,'condition':sid,'initial_original':initial,
                'enzyme_total':E*factor,'initial_modes':['ORIGINAL_NONEQUILIBRIUM','PROJECTED_PHYSICAL_CLOSURE'],
                'projection':'Keep each resource form total T_i and enzyme total fixed; solve T=u+C h(u). If no physical root, preserve mathematical domain failure and no reduced trajectory.',
                'concentration_scales':scales,'bound_scales':{s:max(E*factor*max(unit['resource_composition'][e][s] for e in unit['enzyme_states']),1.) for s in B},
                'occupancy_scale':E*factor,'cumulative_extent_scale':max(limiting,E*factor,1.),'note':note})
    codefiles=[p for p in (ROOT/'scripts/energy_cycles').glob('*.py') if p.name in ['source.py','runtime.py','kinetics_analysis.py','preregister.py']]
    if not (ROOT/'scripts/energy_cycles/runtime.py').exists():raise RuntimeError('Write candidate implementation before freezing')
    registration={'version':'energy_cycles_v1','frozen_at_utc':datetime.now(timezone.utc).isoformat(),
      'source_commit':d['source_commit'],'source_hashes':d['source_hashes'],'author_members':d['author_input_members'],
      'candidate_id':'SOURCE_STATIONARY_ENZYME_TOTAL_COORDINATES_V1',
      'candidate_equations':{'enzyme':'Q(u) h=0; 1^T h=E_total, using every active source kinetic transition and exact zero channels',
        'resources':'T=u+C h(u); T(t)=T(0)+N*(extent_forward-extent_reverse)',
        'rate':'Microscopic catalytic forward and actual active reverse currents at reconstructed h,u; never fit constants.',
        'initial_layer':'No switch or matching correction. Original and stationary projected initial microscopic states are compared separately.'},
      'implementation_sha256':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in codefiles},
      'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__},
      'scenarios':scenarios,'comparison_grid':grid.tolist(),'windows':[[0,.05],[.05,1],[1,1000]],
      'solver':{'reference':'scipy solve_ivp Radau generated exactly from checked SBML mass-action laws; independent BDF convergence',
        'relative_tolerance':1e-8,'absolute_tolerance':1e-10,'tight_relative_tolerance':1e-10,'tight_absolute_tolerance':1e-12,
        'reduced':'Radau with source stationary Q linear solves and analytic derivatives, implicit total-inventory root',
        'closure_absolute_residual':1e-8,'physical_negative_allowance_absolute':1e-8,'closure_min_singular_value':1e-8,
        'initial_multistart_fractions':[0,.25,.75,1.],'multistart_root_difference_allowance':1e-7,
        'fast_tangent_max_real_eigenvalue':-1e-8},
      'observations':{'free':'Every boundary resource form','retained':'Every form-specific total free plus bound','bound':'C h','occupancy':'Every enzyme state/Etotal',
        'flux':'Catalytic forward, reverse, net separately','cumulative':'Integrated catalytic forward/reverse/net extents from t=0; net resource flow=N*net extent',
        'losses':'Microscopic release currents are separately recorded; net conversion is not assumed equal to instantaneous free release during storage.'},
      'normalization':{'flux':'max(long-window microscopic RMS net current,0.01*Etotal*(k_forward+k_reverse),1e-12); fixed formula evaluated on reference only',
        'concentration':'Per scenario max(initial free-form inventory,Etotal,1), positive and fixed before integration',
        'cumulative':'Per scenario max(initial limiting reactant inventory,Etotal,1) times absolute net coefficient for each resource',
        'conservation':'max(initial complete invariant magnitude,1)',
        'uncertainty':'Maximum tight/base and independent-BDF difference; uncertainty must be <=10% of corresponding acceptance threshold. Fail confidently if error-uncertainty > threshold; otherwise numerically inconclusive near gate.'},
      'gates':{'symbolic_residual':0,'normalized_conservation':1e-8,'long_concentration':.05,'long_flux_rms':.10,'cumulative_resource_flow':.02,'full_Pept0003_endpoint':.05,
        'negative_inventory_allowance':1e-8,'initial_windows':'Report separately, do not omit or promote a long-window pass into transient accuracy.',
        'bound_occupancy':'Report reconstructed errors; scientific status also requires valid physical root, positivity, local uniqueness and attractivity.'},
      'source_reference_diagnostics':{'engine':'libRoadRunner 2.10.0 CVODE stiff; normalized XML read without regeneration, author CSV overlay in results only',
        'grid':'Same complete grid including t=0 through1000; each source trajectory includes all species and energy-directed rates',
        'relative_tolerance':1e-8,'absolute_tolerance':1e-10,'tight_relative_tolerance':1e-10,'tight_absolute_tolerance':1e-12,
        'E3_conditions':{'AUTHOR_BASELINE':'All author initial values and four energy subsystem channels; all other968-87 channels disabled only in derived isolated execution copy',
          'SHARED_LIMITATION':{'ATP':100.,'ADP':10.,'AMP':10.,'GTP':100.,'GDP':10.,'CP':100.,'Cr':100.,'PPi':10.,'PO4':100.}},
        'E4_condition':'Unmodified full968 reaction author reference operational parameters and all241 initial values; no candidate replacement unless prerequisites qualify'},
      'staging':{'E1_E2':'Execute feasible isolated comparisons for every scenario and both initial modes; domain/solver failures remain explicit.',
        'E3':'Assembled candidate comparison eligible only if all four constituents pass all required E1/E2 gates and domain checks. Otherwise record BLOCKED_BY_FAILED_PREREQUISITES; source microscopic coupled baseline can run independently.',
        'E4':'No candidate full-PNAS replacement after prerequisite failure. Source-faithful imported normalized author-overlay full-reference execution is independent diagnostic; if candidate stage unavailable, no FULL_MODEL_VALIDATED claim.'},
      'scientific_status':'HUMAN_REVIEW_REQUIRED; no approval or automatic promotion; all thresholds are engineering targets'}
    path.write_text(json.dumps(registration,indent=2)+'\n',encoding='utf-8')
    (OUT/'preregistration_freeze.json').write_text(json.dumps({'path':str(path.relative_to(ROOT)),'sha256':sha(path),'frozen_at_utc':registration['frozen_at_utc'],'comparisons_executed_before_freeze':False},indent=2)+'\n')
    print(json.dumps({'scenarios':len(scenarios),'grid_points':len(grid),'sha256':sha(path)}))

if __name__=='__main__':main()

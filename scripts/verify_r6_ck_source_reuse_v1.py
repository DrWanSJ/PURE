"""Independent source provenance, condition, kinetics and uncertainty reuse checks."""
from r6_ck_common_v1 import *
from runtime_reconstruction_rhs import SourceCoordinateRuntime

def verify(write=True):
    s=SourceCoordinateRuntime('source_coordinate_certificate_v4.json')
    snapshot=load(OUT/'historical_snapshot.json')
    old=load(ROOT/'results/reduction/r4_fast_block_screen/source_reuse_verification.json')
    oldrows={r['condition']:r for r in old['conditions']}
    deps={'canonical_sbml':'models/pnas2017_full_reference/original/fMGG_synthesis.xml',
          'grid':'docs/reduction/r3_validation_grid_v1.csv','method':'docs/reduction/r3_aminoacylation_qssa_method.md',
          'protocol':'docs/reduction/r3_coupled_validation_protocol_v1.md',
          'reaction_map':'docs/reduction/r3_source_reaction_candidate_map_v1.csv',
          'aminoacylation_reactions':'models/pnas2017_full_reference/audit/aminoacylation_reactions.csv',
          'runtime_v1':'scripts/r3_resource_total_runtime_v1.py','runtime_v2':'scripts/r3_resource_total_runtime_v2.py',
          'runner':'scripts/run_r3_coupled_grid_v1.py'}
    records=[]
    for name in CONDITIONS:
        p=historical_path(name);res=load(p/'result.json');manifest=load(p/'manifest.json')
        issues=[]
        for key,rel in deps.items():
            if res['inputs_sha256'][key]!=sha(ROOT/rel):issues.append('dependency:'+rel)
        for rel,h in oldrows[name]['transitive_source_dependencies_sha256'].items():
            if sha(ROOT/rel)!=h or snapshot[rel]['sha256']!=h:issues.append('transitive:'+rel)
        if manifest['result_sha256']!=sha(p/'result.json'):issues.append('historical_result_manifest')
        for rel,h in res['outputs_sha256'].items():
            if sha(p/rel)!=h:issues.append('historical_output:'+rel)
        condition=condition_record(name)
        if res['condition_id']!=name or json.loads(res['initial_scale_json'])!=json.loads(condition['initial_scale_json']):issues.append('condition_definition')
        expected={'state':'BDF','extent':'segmented DOP853 ODE states','rtol':1e-10,'atol':1e-14,'start':0.,'end':1000.,'report_points':201}
        if res['solver']!=expected:issues.append('protocol')
        with np.load(p/'full_state.npz') as a:t=a['times'].copy();x=a['state'].copy()
        with np.load(p/'directed_ledgers.npz') as a:
            lt=a['times'].copy();fv=a['full_rates'].copy();fe=a['full_extent'].copy()
        if not np.array_equal(t,TIMES) or not np.array_equal(t,lt):issues.append('time_grid')
        if not np.array_equal(x[0],initial(s,name)):issues.append('initial_values')
        vv=np.array([s.rates(xx) for xx in x])
        rate_error=float(np.max(abs(vv-fv)/np.maximum(abs(vv),1.)))
        if rate_error>1e-13:issues.append('canonical_author_rates')
        if fe.shape!=(201,968) or not np.array_equal(fe[0],np.zeros(968)):issues.append('extent_grid_or_anchor')
        probe=ROOT/'results/reduction/r4_fast_block_screen/source_uncertainty'/name
        pr=load(probe/'result.json')
        if pr['status']!='COMPLETE' or pr['solver']['rtol']!=1e-8 or pr['solver']['atol']!=1e-14 or pr['solver']['end']!=1000:issues.append('source_probe_protocol')
        if pr['extent_solver']['rtol']!=1e-10 or pr['extent_solver']['atol']!=1e-14:issues.append('source_probe_extent_protocol')
        with np.load(probe/'probe_state.npz') as a:px=a['state'].copy();pt=a['times'].copy()
        with np.load(probe/'probe_ledgers.npz') as a:pv=a['rates'].copy();pe=a['extent'].copy();pet=a['times'].copy()
        if not np.array_equal(pt,TIMES) or not np.array_equal(pet,TIMES) or not np.array_equal(px[0],initial(s,name)):issues.append('source_probe_initial_grid')
        pvv=np.array([s.rates(xx) for xx in px])
        if np.max(abs(pvv-pv)/np.maximum(abs(pvv),1.))>1e-13:issues.append('source_probe_kinetics')
        files=[p/'full_state.npz',p/'directed_ledgers.npz',p/'result.json',p/'manifest.json',
               probe/'probe_state.npz',probe/'probe_ledgers.npz',probe/'result.json']
        for f in files:
            rel=f.relative_to(ROOT).as_posix()
            if sha(f)!=snapshot[rel]['sha256']:issues.append('frozen_source_file:'+rel)
        records.append(dict(condition=name,reuse_valid=not issues,issues=issues,
           initial_state_sha256=hashlib.sha256(x[0].tobytes()).hexdigest(),canonical_rate_scaled_check=rate_error,
           primary_directory=p.relative_to(ROOT).as_posix(),uncertainty_directory=probe.relative_to(ROOT).as_posix(),
           file_hashes={f.relative_to(ROOT).as_posix():sha(f) for f in files},
           input_hashes={rel:sha(ROOT/rel) for rel in deps.values()},
           transitive_hashes=oldrows[name]['transitive_source_dependencies_sha256'],
           uncertainty_semantics='historical 1e-8 source probe envelope; no primary source replacement',
           new_reduced_required=True,historical_reduced_reused=False))
    report=dict(schema='R6_CK_SOURCE_REUSE_VERIFICATION_V1',verified_at_utc=stamp(),
                status='PASS' if all(r['reuse_valid'] for r in records) else 'RECOMPUTE_REQUIRED',
                conditions=records,excluded_conditions=['R3_ADVERSE'],
                all_source_inputs_hash_bound=True,initial_values_exactly_matched=True,
                reporting_protocol_exactly_matched=True,no_expensive_source_rerun=True,
                startup_at_switch='new bounded full-source startup solve; no interpolation or source projection')
    if write:write_json(OUT/'source_reuse_verification.json',report)
    assert report['status']=='PASS',[(r['condition'],r['issues']) for r in records]
    return report

if __name__=='__main__':
    report=verify();print([(r['condition'],r['reuse_valid']) for r in report['conditions']],flush=True)

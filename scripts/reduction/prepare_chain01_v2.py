"""R0: source-bound exact mathematics and prospective protocol; no trajectories."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_chain01_sources import audit_sources, parse_sources, csv_rows, CHAIN_IDS

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/reduction/chain01_v2'
CONFIG = ROOT / 'configs/reduction/chain01_v2_validation.json'
MODELS = ('Full', 'Direct', 'Two-stage', 'Three-stage')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def model_specs(manifest):
    k = [F(x) for x in manifest['author_rates_exact']]
    ke = 1 / sum((1/x for x in k), F(0))
    ka = 1 / (1/k[0] + 1/k[1])
    kb = 1 / (1/k[2] + 1/k[3])
    # Retained aliases have their literal chemical compositions. No hidden
    # microstate reconstruction is added or silently counted as a free state.
    return {
        'Full': {'states': ['S0','S1','S2','S3','S4'], 'rates_exact': list(map(str,k)), 'segments': [[14],[16],[17],[18]], 'pi_stage': 1, 'gdp_stage': 2, 'hydrolysis_stage': 0},
        'Direct': {'states': ['S0','S4'], 'rates_exact': [str(ke)], 'segments': [[14,16,17,18]], 'pi_stage': 0, 'gdp_stage': 0, 'hydrolysis_stage': 0},
        'Two-stage': {'states': ['S0','S2','S4'], 'rates_exact': [str(ka),str(kb)], 'segments': [[14,16],[17,18]], 'pi_stage': 0, 'gdp_stage': 1, 'hydrolysis_stage': 0},
        'Three-stage': {'states': ['S0','S1','S2','S4'], 'rates_exact': [str(k[0]),str(k[1]),str(kb)], 'segments': [[14],[16],[17,18]], 'pi_stage': 1, 'gdp_stage': 2, 'hydrolysis_stage': 0},
    }


def coefficients(states):
    """Source-derived local fate equivalents, not full-network atomic balance."""
    return {
        'bound_pi': [int(s == 'S1') for s in states],
        'bound_gdp': [int(s in ('S1','S2')) for s in states],
        'bound_gtp': [int(s == 'S0') for s in states],
        'tu_bound': [int(s in ('S0','S1','S2')) for s in states],
        'phosphate_unreleased': [int(s in ('S0','S1')) for s in states],
        'unfinished': [int(s != 'S4') for s in states],
    }


def build_source():
    audit = audit_sources(ROOT)
    reactions, species, initial, info = parse_sources(ROOT)
    author_rows = csv_rows(ROOT / 'models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat/fMGG_synthesis_reactions.csv')
    author = {r['id']: r for r in author_rows}
    if set(author) != set(reactions):
        raise ValueError('Author reaction CSV coverage differs from canonical SBML')
    selected = (*CHAIN_IDS, 're0000000021')
    for rid in selected:
        r, row = reactions[rid], author[rid]
        for field, sourcefield in [('reactants','reactants_exact'),('products','products_exact')]:
            if set(filter(None,row[field].split(','))) != set(r[sourcefield]):
                raise ValueError('Author reaction CSV identities disagree: '+rid)
        if row['math'] != r['kinetic_law_formula']:
            raise ValueError('Author reaction kinetic law differs: '+rid)
    side = reactions['re0000000021']
    s0 = audit['species_aliases']['S0']
    if side['reactants_exact'] != {s0:'1'} or side['kinetic_factors'] != ['k1',s0]:
        raise ValueError('re21 is not the expected source first-order undocking reaction')
    products = {'EFTu_GTP_GlytRNAGlyGCC':'1','elRS70SAGGU0002_fMet':'1'}
    if side['products_exact'] != products or F(side['author_parameters'][0]['author_value_exact']) != F('0.23'):
        raise ValueError('re21 products or author rate differ; boundary mapping unresolved')
    audit.update({'schema_version':'chain01_v2_source_manifest', 'boundary_reaction':side,
                  'author_reaction_csv_selected_crosscheck':'PASS',
                  'source_snapshot_role':'EXTRACTED; source authority is canonical SBML plus author CSV',
                  'old_alias_mapping':{'old_A':'S1','old_X1':'S2','old_X2':'S3','old_B':'S4'}})
    return audit, reactions, species


def mathematics(manifest, reactions, species):
    specs = model_specs(manifest)
    total = manifest['stoichiometry_exact']['sum_nonzero_exact']
    c = F(manifest['boundary_reaction']['author_parameters'][0]['author_value_exact'])
    cert = {}
    for name, spec in specs.items():
        columns = []
        for segment in spec['segments']:
            col = {}
            for rid in segment:
                for sid, val in reactions[f're{rid:010d}']['net_stoichiometry_exact'].items():
                    col[sid] = col.get(sid,F(0)) + F(val)
            columns.append({s:str(v) for s,v in sorted(col.items()) if v})
        differences = {sid: str(sum((F(col.get(sid,0)) for col in columns),F(0)) - F(total.get(sid,0))) for sid in species}
        assert set(differences.values()) == {'0'}
        rates = list(map(F,spec['rates_exact']))
        waits = [1/r for r in rates]
        props = coefficients(spec['states'])
        steady = {key: sum((F(a)*w for a,w in zip(vals[:-1],waits)),F(0)) for key,vals in props.items()}
        release_delays = {'product':sum(waits,F(0)), 'pi':sum(waits[:spec['pi_stage']+1],F(0)), 'gdp':sum(waits[:spec['gdp_stage']+1],F(0))}
        p = rates[0]/(rates[0]+c)
        q = c/(rates[0]+c)
        boundary_waits = [1/(rates[0]+c)] + [p/r for r in rates[1:]]
        cert[name] = {
            'provenance_class':'INFERRED_FROM_EXACT_SOURCE_COLUMNS', 'states':spec['states'],
            'reaction_count':len(rates), 'chemical_state_count':len(spec['states']),
            'transient_state_count':len(rates), 'extent_counter_count':len(rates),
            'shared_resource_counters':'free Pi/GDP are algebraically read from extents; boundary adds two explicit product amounts plus re21 extent',
            'stoichiometric_columns_exact':columns, 'net_per_species_difference_exact':differences,
            'stoichiometry_status':'PASS', 'source_net_identity_limitation':'reaction-vector identity, not a new atomic/ionic certificate',
            'rate_definitions_exact':spec['rates_exact'], 'steady_unit_input_stage_occupancy_exact':list(map(str,waits)),
            'steady_unit_input_ledger_exact':{key:str(val) for key,val in steady.items()},
            'steady_currents_exact':{'product':'1','pi':'1','gdp':'1'},
            'mean_residence_exact':str(sum(waits,F(0))), 'variance_exact':str(sum((w*w for w in waits),F(0))),
            'release_delay_exact':{key:str(val) for key,val in release_delays.items()},
            'cumulative_asymptote_rule':'For zero initial inventory and constant u: xi_resource = u*(t-release_delay)+o(1). Candidate-minus-Full offset is u*(delay_Full-delay_candidate).',
            'competition':{'c_exact':str(c),'completion_probability_exact':str(p),'escape_probability_exact':str(q),
                           'conditional_success_mean_exact':str(1/(rates[0]+c)+sum(waits[1:],F(0))),
                           'steady_unit_input_stage_occupancy_exact':list(map(str,boundary_waits)),
                           'steady_success_resource_currents_exact':str(p),'steady_re21_current_exact':str(q),
                           'stoichiometry_exact':manifest['boundary_reaction']['net_stoichiometry_exact']},
        }
    full_delays = cert['Full']['release_delay_exact']
    for rec in cert.values():
        rec['cumulative_asymptotic_offsets_vs_full_exact'] = {key:str(F(full_delays[key])-F(val)) for key,val in rec['release_delay_exact'].items()}
    return {'models':cert, 'tau_exact':manifest['tau_exact'],
            'rate_rules':{'ka':'1/(1/k14+1/k16)','kb':'1/(1/k17+1/k18)','ke':'1/(1/k14+1/k16+1/k17+1/k18)'},
            'warning':'Equal eventual current or pulse yield does not identify a correct waiting-time distribution. All coarse models are mean-dwell-matched Markov candidates, not exact lumpability.',
            'resource_identities':[
                'sum(chain states)+undocked ribosome = initial chain inventory + integral(u)',
                'bound_gtp + undocked intact GTP carrier + hydrolysis_extent = initial bound_gtp + integral(u)',
                'bound_pi + pi_extent = initial bound_pi + hydrolysis_extent',
                'bound_gdp + gdp_extent = initial bound_gdp + hydrolysis_extent',
                'tu_bound + gdp_extent + undocked intact GTP carrier = initial tu_bound + integral(u)',
                'unfinished + S4 + undocked ribosome = initial chain inventory + integral(u)',
            ], 'S4_semantics':'Local peptide-extension product remains ribosome-bound; it is neither free final fMGG product nor full PURE protein yield.'}


def protocol(manifest):
    tests = {
        'A_pulse':{'label':'Unit initial S0 cohort','initial_full':[1,0,0,0,0],'input_kind':'zero','end_tau':100,'amount_scale':'1','current_scale':'1/tau','domain':'IN_DOMAIN','gate_windows':['late_5_10','macro_10_end']},
        'B_constant':{'label':'Constant u=1','initial_full':[0,0,0,0,0],'input_kind':'constant','amplitude':1,'end_tau':10000,'amount_scale':'tau','current_scale':'1','domain':'IN_DOMAIN','gate_windows':['late_5_10','macro_10_end']},
        'D_fast':{'label':'V1 two rectangular inputs','initial_full':[0,0,0,0,0],'input_kind':'rectangular','input_segments':[[.5,1,1],[3,3.5,1]],'end_tau':100,'amount_scale':'tau','current_scale':'1','domain':'FAST_INPUT_NEGATIVE_CONTROL','gate_windows':[]},
        'D_inventory':{'label':'V1 nonzero internal inventory','initial_full':[0,.25,.5,.25,0],'input_kind':'zero','end_tau':100,'amount_scale':'1','current_scale':'1/tau','domain':'OUT_OF_DOMAIN_INITIAL_COMPOSITION','gate_windows':[]},
    }
    for ratio in (20,100,1000):
        tests[f'C_slow_{ratio}']={'label':f'u=exp(-t/({ratio} tau))','initial_full':[0,0,0,0,0],'input_kind':'exponential','amplitude':1,'T_slow_tau':ratio,'end_tau':10*ratio,'amount_scale':'tau','current_scale':'1','domain':'IN_DOMAIN','gate_windows':['late_5_10','macro_10_end']}
    return {
        'protocol_id':'CHAIN01_V2_RESOURCE_PRESERVING_STAGED_LUMPING', 'source_start_head':manifest['git_context']['head'],
        'date':'2026-10-08 Asia/Shanghai', 'time_unit':'source model time unit; no seconds interpretation',
        'amount_unit':'dimensionless imposed local cohort, or amount in source concentration convention; not a calibrated shared-pool concentration',
        'scope':'Local exogenous nonnegative input; isolate S4 downstream; fixed author internal side paths remain zero. Base suppresses re21; separate R2 restores exact source re21 products without rebinding.',
        'models':model_specs(manifest),'tests':tests,
        'initial_mapping':{'Full':'[x0,x1,x2,x3,x4]','Direct':'[x0+x1+x2+x3,x4]','Two-stage':'[x0+x1,x2+x3,x4]','Three-stage':'[x0,x1,x2+x3,x4]',
                           'limitation':'Mappings preserve ribosome amount but change chemical composition for D_inventory; no exact resource-inventory reconstruction is asserted.'},
        'sampling':{'first_10_tau_count':2001,'early_0_025_tau_count':501,'late_log_count':301,'slow_linear_count':401,'switch_local_count':101,'switch_band_tau':.25,
                    'checkpoint_tau':[.25,.5,.75,1,1.25,3,3.25,3.5,3.75,5,10,20,100,1000,10000],
                    'maxima':'fixed grid maxima only; not a continuum supremum','convergence_grid':'add all interval midpoints; report maxima change; scientific budgets remain fixed'},
        'windows':{'early_0_10':[0,10],'late_5_10':[5,10],'macro_10_end':[10,None],'10_100':[10,100],'100_1000':[100,1000],'1000_10000':[1000,10000],
                   'V1_transient':'[0,.25] plus each rectangular switch through switch+.25 tau inclusive', 'V1_post':'strict complement of V1_transient within [0,10]'},
        'gates':{
            'numerical':{'state_extent_absolute':1e-8,'current_absolute':1e-8,'convergence_absolute':5e-9,'ledger_absolute':1e-8,'negative_state_absolute':1e-12,'steady_scaled_absolute':1e-8,'dense_grid_maxima_change_absolute':1e-4},
            'product':{'metrics':['product_extent','product_current'],'max_fixed_scale_error':.01},
            'resources':{'metrics':['pi_current','pi_extent','gdp_current','gdp_extent','bound_pi','bound_gdp','bound_gtp','tu_bound','phosphate_unreleased','unfinished'],'max_fixed_scale_error':.01},
            'boundary':{'completion_probability_relative':.01,'escape_probability_relative':.01,'endpoint_yield_relative':.01,'resource_gate_same_as_base':True},
            'domain':{'zero_initial_internal_required':True,'author_rates_only':True,'internal_side_paths_zero_required':True,'input_T_slow_tau_tested':[20,100,1000],'S4_downstream_isolated':True},
            'rule':'Gate 1 resolves numerics before kinetic decisions. Gate 2 and 3 apply to every declared gate window independently. Fast and initial-inventory controls are diagnosed but do not enter the slow-input domain. Local boundary support additionally requires BOTH success and escape allocation budgets.',
        },
        'V1_diagnostic_thresholds':{'product_extent':.01,'product_current':.05,'pi_extent':.01,'pi_current':.05,'gdp_extent':.01,'gdp_current':.05,'unfinished':.05},
        'error_policy':{'signed':'candidate minus Full','fixed_scale':'Initial cohort 1, or constant predeclared u0*tau; current 1/tau or u0. No growing cumulative denominator in gates.',
                        'relative':'absolute / abs(Full) only when exactly nonzero; undefined otherwise; no clipping',
                        'rms':'time-weighted trapezoid RMS within each connected fixed window',
                        'production_integral':'integral of formation current equals directed product extent; window production is extent(b)-extent(a)',
                        'endpoint_relative':'report at 10tau and all declared long checkpoints; descriptive except boundary yield'},
        'rationale':{'macro':'Exploratory 1% resolution for sustained/slow product amount and current after fixed [5,10]tau startup observation. This is an independently registered target, not revision of V1.',
                     'resources':'Same 1% of one input-dwell amount bounds persistent absolute free/bound resource offsets. All early discrepancies retained. No shared ATP/GTP pool trajectory is validated.',
                     'competition':'Apply the same 1% relative resolution to BOTH pathway probabilities so a small escape pathway carrying intact GTP carrier is not hidden by normalization against total input. This gate tests interface allocation, not only dominant product yield.',
                     'windows':'[5,10]tau and [10,end]tau are fixed from source mean dwell before computation; exponential supply at 20,100,1000tau probes progressively slower forcing; 10000tau checks persistent offsets.',
                     'numerics':'Absolute numerical tolerances orders below approximation budgets; noncompletion stays NUMERICALLY_UNRESOLVED.'},
        'solver':{'method':'Radau','rtol':1e-10,'atol':1e-12,'tight_rtol':1e-12,'tight_atol':1e-14,'independent':'augmented dense matrix exponential; additionally source-rebuilt high-precision rational Laplace residues in standalone verifier',
                  'long_horizon':'Same ODE through end; exponential input is autonomous augmented coordinate. Matrix exponentials provide independent propagation at sparse long points and dense early points.'},
        'boundary_experiment':{'reaction_id':'re0000000021','rate_exact':'23/100','products':manifest['boundary_reaction']['products_exact'],
                               'experiments':['A_pulse','B_constant','C_slow_20','C_slow_100','C_slow_1000','D_fast','D_inventory'],
                               'outside_boundary':'re13 rebinding and S4 downstream remain isolated; escaped products accumulate explicitly; this is an open local competition test, not full PNAS replacement.',
                               'parameter_range':'Numerics only at original author c=.23. Analytic p=k_in/(k_in+c) establishes dependence on c>=0; no empirical parameter-range promotion.'},
        'prohibited':['V1 edits','canonical edits','author parameter fitting','threshold or window retuning','full 968-reaction replacement','automatic reduced-core promotion'],
    }


def check_integrity():
    freeze = json.loads((OUT/'protocol_freeze.json').read_text())
    for rel, sha in freeze['bindings'].items():
        if digest(ROOT/rel) != sha:
            raise ValueError('Frozen file changed: '+rel)
    before = json.loads((OUT/'protected_files_before.json').read_text())
    changed = [rel for rel, sha in before['files'].items() if not (ROOT/rel).is_file() or digest(ROOT/rel) != sha]
    if changed:
        raise ValueError('Historical/source bytes changed: '+repr(changed))
    return {'status':'PASS','protected_file_count':len(before['files']),'binding_count':len(freeze['bindings'])}


def prepare():
    if (OUT/'protocol_freeze.json').exists():
        raise ValueError('R0 is immutable; use --check rather than replacing it')
    branch = subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    if branch != 'codex/pnas-topology-first':
        raise ValueError('Wrong working branch')
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'.gitattributes').write_text('* -text\n',encoding='utf-8',newline='\n')
    manifest, reactions, species = build_source()
    dump(OUT/'source_manifest.json',manifest)
    dump(OUT/'mathematical_certificate.json',mathematics(manifest,reactions,species))
    dump(CONFIG,protocol(manifest))
    tracked = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    dump(OUT/'protected_files_before.json', {'source_head':manifest['git_context']['head'],
         'scope':'Every preexisting tracked file; raw working-tree bytes, including V1 and historical R1-R8 evidence available on this branch',
         'files':{p:digest(ROOT/p) for p in tracked if p and (ROOT/p).is_file()}})
    bindings = ['configs/reduction/chain01_v2_validation.json','results/reduction/chain01_v2/source_manifest.json',
                'results/reduction/chain01_v2/mathematical_certificate.json','results/reduction/chain01_v2/protected_files_before.json',
                'scripts/reduction/audit_chain01_sources.py','scripts/reduction/prepare_chain01_v2.py']
    dump(OUT/'protocol_freeze.json',{'protocol_id':'CHAIN01_V2_RESOURCE_PRESERVING_STAGED_LUMPING',
         'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'frozen_before_first_V2_numerical_trajectory':True,
         'bindings':{p:digest(ROOT/p) for p in bindings},'first_run_requirement':'R0 commit must be pushed and remote HEAD verified before R1 numerical execution',
         'thresholds_remain_unchanged_on_failure':True})
    print(json.dumps(check_integrity()))


if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check',action='store_true')
    args=ap.parse_args()
    print(json.dumps(check_integrity())) if args.check else prepare()

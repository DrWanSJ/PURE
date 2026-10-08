"""Add execution-source snapshots, corrected figure presentations and navigation."""
import argparse
import csv
from datetime import datetime,timezone
from fractions import Fraction as F
import json
from pathlib import Path
import shutil
import subprocess
import numpy as np

from prepare_chain01_v2 import ROOT,OUT,digest,dump,check_integrity,coefficients


def capture_base_sources():
    runner=ROOT/'scripts/reduction/validate_chain01_v2.py'; src=runner.read_text()
    current=OUT/'base/attempt_002'
    assert digest(runner)==json.loads((current/'runtime_manifest.json').read_text())['runner_sha256']
    (current/'runner_source.py').write_bytes(runner.read_bytes())
    start=src.index('\n\ndef resolve_grid('); end=src.index('\n\ndef csv_gz(',start)
    old=src[:start]+src[end:]
    old=old.replace("base,first_refined,_=times_for(test,config,tau)\n            times,base_mask,gridexacts,gridrec=resolve_grid(test,config,tau,base,first_refined,c)\n            windows=masks(times,config,test,tau)\n            json_write(attemptpath/(testid+'_sampling_convergence.json'),gridrec)",
                    "base,times,base_mask=times_for(test,config,tau); windows=masks(times,config,test,tau)")
    old=old.replace('exact=gridexacts[name]',"exact,er=propagate(m,z,segments,times,'expm')")
    old=old.replace("testchecks[name]['registered_to_refined_max_change_diagnostic']=densechange\n                testchecks[name]['grid_max_change']=gridrec['last_change_by_model'][name]\n                if testchecks[name]['grid_max_change']>",
                    "testchecks[name]['grid_max_change']=densechange\n                if densechange>")
    path=OUT/'base/attempt_001/runner_source.py'
    path.write_bytes(old.encode('utf-8'))
    expected=json.loads((path.parent/'runtime_manifest.json').read_text())['runner_sha256']
    assert digest(path)==expected,(digest(path),expected)
    verifier=ROOT/'scripts/tests/verify_chain01_v2.py'
    (current/'independent_verifier_source.py').write_bytes(verifier.read_bytes())
    dump(current/'execution_source_receipt.json',{'status':'PASS','runner_matches_native_execution_hash':True,
         'attempt_001_runner_matches_native_execution_hash':True,'verifier_source_sha256':digest(verifier),
         'note':'Verifier source captured after completed analytic verification; unchanged since that execution. Runner sources are matched to the native pre-run hashes.'})
    print('Original execution source snapshots match both native runtime hashes')


def present_base():
    from validate_chain01_v2 import make_figures, METRICS
    index=json.loads((OUT/'base_latest.json').read_text()); summary=json.loads((ROOT/index['summary']).read_text())
    runset={}; tau=summary['tau']; dest=OUT/'figures/base/attempt_002_axis_qa'
    if dest.exists(): raise ValueError('Presentation output already exists; preserve it')
    for testid,models in summary['tests'].items():
        runset[testid]={}
        for name,rec in models.items():
            raw=np.genfromtxt(ROOT/rec['raw_csv'],delimiter=',',names=True)
            obs={key[4:]:raw[key] for key in raw.dtype.names if key.startswith('obs_')}
            runset[testid][name]={'times':raw['t'],'obs':obs}
    make_figures(dest,runset,tau,'base')
    original=OUT/'figures/base/attempt_002'
    shutil.copy2(original/'09_complexity_accuracy_tradeoff.png',dest/'09_complexity_accuracy_tradeoff.png')
    sources=json.loads((original/'data_sources.json').read_text()); sources['presentation_note']='Nonnegative time-axis limits; same original saved arrays and scores. Original images preserved.'
    dump(dest/'data_sources.json',sources)
    dump(dest/'presentation_manifest.json',{'source_summary_sha256':digest(ROOT/index['summary']),'presentation_runner_sha256':digest(ROOT/'scripts/reduction/validate_chain01_v2.py'),
         'no_numerical_rerun':True,'artifacts':[{'path':str(f.relative_to(ROOT)).replace('\\','/'),'sha256':digest(f)} for f in sorted(dest.glob('*.png'))]})
    index['figures']=str(dest.relative_to(ROOT)).replace('\\','/'); dump(OUT/'base_latest.json',index)
    print('Added corrected time-axis presentations from unchanged numerical arrays')


def navigation():
    source=json.loads((OUT/'source_manifest.json').read_text())
    nodes=[{'id':s['path'],'type':'source','provenance':'EXTRACTED','sha256':s['sha256'],'confidence':'EXACT_RAW_BYTE_BINDING','freshness':'R0 source snapshot; current integrity separately verified'} for s in source['sources']]
    edges=[]
    selected=[ROOT/'configs/reduction/chain01_v2_validation.json',OUT/'mathematical_certificate.json',OUT/'protocol_freeze.json',OUT/'validation_summary.json',OUT/'verification_report.json']
    if (OUT/'boundary_analytical_certificate.json').exists(): selected.append(OUT/'boundary_analytical_certificate.json')
    for phase in ('base','boundary'):
        indexpath=OUT/(phase+'_latest.json')
        if not indexpath.exists(): continue
        index=json.loads(indexpath.read_text())
        directory=(ROOT/index['summary']).parent
        selected.extend([ROOT/index['summary'],ROOT/index['verification'],directory/'independent_verification.json',directory/'artifact_manifest.json'])
        selected.extend(sorted((OUT/'numerical_results'/phase/directory.name).glob('*.csv.gz')))
        selected.extend(sorted((OUT/'error_tables'/phase/directory.name).glob('*.csv.gz')))
    for report in ('chain01_v2_base_validation_report.md','chain01_v2_validation_report.md'):
        path=ROOT/'docs/reduction'/report
        if path.exists(): selected.append(path)
    for path in selected:
        rel=str(path.relative_to(ROOT)).replace('\\','/')
        inferred=(path.suffix=='.md' or 'mathematical_certificate' in path.name or 'analytical_certificate' in path.name or 'validation_summary' in path.name or 'verification_report' in path.name or 'independent_verification' in path.name or 'error_tables' in rel or path.name=='chain01_v2_validation.json')
        nodes.append({'id':rel,'type':'derived_evidence','sha256':digest(path),'provenance':'INFERRED' if inferred else 'EXTRACTED',
             'confidence':'MEASURED_OR_GATE_DERIVED; NOT_SCIENTIFIC_PROMOTION','freshness':'Current final artifact bytes at '+datetime.now(timezone.utc).isoformat()})
        edges.append({'from':'configs/reduction/chain01_v2_validation.json','to':rel,'relation':'frozen observable contract constrains interpretation'})
    for s in source['sources']:
        edges.append({'from':s['path'],'to':'results/reduction/chain01_v2/mathematical_certificate.json','relation':'source supports exact columns and author-condition derivation'})
    dump(OUT/'evidence_navigation.json',{'role':'Derived navigation only; canonical sources, frozen protocol and raw evidence remain authoritative',
          'labels':['EXTRACTED','INFERRED','AMBIGUOUS'],'scientific_confidence':'Support is conditional on declared local domain and independent gates; no global approval',
          'nodes':nodes,'edges':edges})
    print('Updated source-bound evidence navigation')


def boundary_math():
    check_integrity()
    config=json.loads((ROOT/'configs/reduction/chain01_v2_validation.json').read_text())
    source=json.loads((OUT/'source_manifest.json').read_text())
    prior=json.loads((OUT/'mathematical_certificate.json').read_text())
    c=F(source['boundary_reaction']['author_parameters'][0]['author_value_exact']); records={}
    for name,spec in config['models'].items():
        k=list(map(F,spec['rates_exact'])); p=k[0]/(k[0]+c); q=c/(k[0]+c)
        waits=[1/(k[0]+c)]+[1/r for r in k[1:]]
        delays={'product':sum(waits,F(0)),'pi':sum(waits[:spec['pi_stage']+1],F(0)),'gdp':sum(waits[:spec['gdp_stage']+1],F(0))}
        stage_occupancy=[1/(k[0]+c)]+[p/r for r in k[1:]]
        inventory={key:sum((F(a)*w for a,w in zip(vec[:-1],stage_occupancy)),F(0)) for key,vec in coefficients(spec['states']).items()}
        assert p==F(prior['models'][name]['competition']['completion_probability_exact'])
        assert delays['product']==F(prior['models'][name]['competition']['conditional_success_mean_exact'])
        assert list(map(str,stage_occupancy))==prior['models'][name]['competition']['steady_unit_input_stage_occupancy_exact']
        records[name]={'completion_probability_exact':str(p),'escape_probability_exact':str(q),
            'conditional_release_delay_exact':{key:str(v) for key,v in delays.items()},
            'unit_input_steady_inventory_exact':{key:str(v) for key,v in inventory.items()},
            'steady_product_pi_gdp_current_per_unit_input_exact':str(p),
            'steady_return_current_per_unit_input_exact':str(q),
            'mean_until_success_or_escape_exact':str(sum(stage_occupancy,F(0))),
            'conditional_success_mean_exact':str(delays['product']),
            'return_delay_exact':str(waits[0]),
            'cumulative_success_rule':'xi_R=u*p*(t-d_R)+o(1); R=product, Pi, or released EF-Tu.GDP',
            'cumulative_return_rule':'each source re21 product = u*q*(t-1/(k_in+c))+o(1)'}
    full=records['Full']
    for name,rec in records.items():
        p=F(rec['completion_probability_exact']); pf=F(full['completion_probability_exact'])
        rec['candidate_minus_full_cumulative_success_asymptote_exact']={key:{'slope_per_unit_input':str(p-pf),
              'intercept_per_unit_input':str(pf*F(full['conditional_release_delay_exact'][key])-p*F(rec['conditional_release_delay_exact'][key]))} for key in ('product','pi','gdp')}
        q=F(rec['escape_probability_exact']); qf=F(full['escape_probability_exact'])
        rec['candidate_minus_full_return_asymptote_exact']={'slope_per_unit_input':str(q-qf),'intercept_per_unit_input':str(qf*F(full['return_delay_exact'])-q*F(rec['return_delay_exact']))}
    # Long-time data are checked against algebraic predictions; no new ODE is run.
    idx=json.loads((OUT/'boundary_latest.json').read_text()); saved=json.loads((ROOT/idx['summary']).read_text()); tau=F(source['tau_exact'])
    comparisons={}
    for name,rec in records.items():
        endpoint=next(r for r in saved['tests']['B_constant'][name]['endpoints'] if r['t_over_tau']==10000)
        comparisons[name]={}
        for label,metric in [('product','product_extent'),('pi','pi_extent'),('gdp','gdp_extent')]:
            asym=rec['candidate_minus_full_cumulative_success_asymptote_exact'][label]
            predicted=float(F(asym['slope_per_unit_input'])*10000*tau+F(asym['intercept_per_unit_input']))
            error=abs(predicted-endpoint[metric]['signed_absolute'])
            assert error<=config['gates']['numerical']['state_extent_absolute']
            comparisons[name][label]={'predicted_signed_offset_at_10000tau':predicted,'saved_signed_offset':endpoint[metric]['signed_absolute'],'discrepancy':error}
    dump(OUT/'boundary_analytical_certificate.json',{'provenance':'INFERRED_EXACT_SOURCE_DERIVATION','source_manifest_sha256':digest(OUT/'source_manifest.json'),
       'c_exact':str(c),'time_unit':config['time_unit'],'models':records,'saved_long_endpoint_checks':comparisons,
       'scope':'Additional analytic explanation of the already frozen boundary experiment; no gate, initial condition, parameter or trajectory changes.'})
    print('Exact boundary currents, occupancies and cumulative slope/intercept predictions match saved long endpoints')


def present_boundary():
    from validate_chain01_v2 import plt, COLORS
    idx=json.loads((OUT/'boundary_latest.json').read_text())
    original=OUT/'figures/boundary/attempt_001'; dest=OUT/'figures/boundary/attempt_001_axis_qa'
    if dest.exists(): raise ValueError('Preserve existing boundary presentation')
    shutil.copytree(original,dest)
    with (dest/'10_competing_boundary_allocation.csv').open(encoding='utf-8',newline='') as f: rows=list(csv.DictReader(f))
    names=[r['model'] for r in rows]; fractions=[float(r['escaped_carrier_amount']) for r in rows]; errors=[float(r['escape_relative_error']) for r in rows]
    fig,axes=plt.subplots(1,2,figsize=(11,4.5),constrained_layout=True)
    for ax,values,title,ylabel in [(axes[0],fractions,'Actual cohort escape through re21','Escaped loaded carrier / initial unit cohort'),
                                   (axes[1],errors,'Frozen 1% allocation budget','Escape fraction relative error')]:
        bars=ax.bar(names,values,color=[COLORS[name] for name in names]); ax.set_title(title); ax.set_ylabel(ylabel)
        if ax is axes[1]: ax.set_yscale('symlog',linthresh=.01); ax.axhline(.01,color='gray',ls=':')
        ax.set_ylim(0,max(values)*1.55)
        ax.bar_label(bars,labels=[f'{v:.6g}' for v in values],padding=4,fontsize=8)
    fig.suptitle('10_competing_boundary_allocation | CHAIN01 V2 boundary\nActual A_pulse at 100tau; author re21=.23; both source products retained')
    fig.savefig(dest/'10_competing_boundary_allocation.png',dpi=150); plt.close(fig)
    source=json.loads((dest/'data_sources.json').read_text()); source['presentation_note']='Allocation chart has explicit headroom and numerical annotations; original images and numeric arrays preserved.'
    dump(dest/'data_sources.json',source)
    dump(dest/'presentation_manifest.json',{'source_summary_sha256':digest(ROOT/idx['summary']),'source_allocation_csv_sha256':digest(original/'10_competing_boundary_allocation.csv'),
        'no_numerical_rerun':True,'artifacts':[{'path':str(f.relative_to(ROOT)).replace('\\','/'),'sha256':digest(f)} for f in sorted(dest.glob('*.png'))]})
    idx['figures']=str(dest.relative_to(ROOT)).replace('\\','/'); dump(OUT/'boundary_latest.json',idx)
    print('Added boundary allocation chart with visible values; numerical evidence unchanged')


def round_records():
    receipts=json.loads((OUT/'git_delivery_manifest.json').read_text())['rounds']
    commands={
        'V2-R0':['git status --short','git branch --show-current','git fetch origin','git log -1 --oneline',
                 'git ls-remote origin refs/heads/codex/pnas-topology-first','python scripts/reduction/prepare_chain01_v2.py',
                 'python scripts/tests/test_chain01_v2.py','git diff --cached --check',
                 'git commit -m "reduction: preregister CHAIN_01 V2 staged lumping validation"','git push origin codex/pnas-topology-first'],
        'V2-R1':['python scripts/tests/test_chain01_v2.py','python scripts/reduction/validate_chain01_v2.py',
                 'python scripts/tests/verify_chain01_v2.py',
                 'python scripts/reduction/maintain_chain01_v2_artifacts.py --capture-base-sources',
                 'python scripts/reduction/maintain_chain01_v2_artifacts.py --present-base','python scripts/reduction/report_chain01_v2.py',
                 'python scripts/reduction/maintain_chain01_v2_artifacts.py --navigation','git diff --cached --check',
                 'git commit -m "reduction: validate CHAIN_01 V2 two-stage and three-stage models"','git push origin codex/pnas-topology-first'],
        'V2-R2':['python scripts/reduction/validate_chain01_v2.py --boundary','python scripts/tests/verify_chain01_v2.py --boundary',
                 'python scripts/tests/test_chain01_v2.py','python scripts/reduction/maintain_chain01_v2_artifacts.py --present-boundary',
                 'python scripts/reduction/maintain_chain01_v2_artifacts.py --boundary-math','python scripts/reduction/report_chain01_v2.py --final',
                 'python scripts/reduction/maintain_chain01_v2_artifacts.py --navigation','python scripts/tests/audit_chain01_v2_completion.py',
                 'git diff --cached --check','git commit -m "reduction: assess CHAIN_01 V2 competing boundary and recommend three-stage"',
                 'git push origin codex/pnas-topology-first'],
    }
    summaries={}
    for phase in ('base','boundary'):
        idx=json.loads((OUT/(phase+'_latest.json')).read_text())
        summaries[phase]=json.loads((ROOT/idx['summary']).read_text())
    records=[]
    for stage in ('V2-R0','V2-R1','V2-R2'):
        rec=next(r for r in receipts if r['round']==stage)
        files=subprocess.check_output(['git','diff-tree','--no-commit-id','--name-only','-r',rec['local_commit_sha']],cwd=ROOT,text=True).splitlines()
        records.append({'round':stage,'completed_work':{'V2-R0':'Exact source audit, derivations, prospective freeze, initial structural tests',
             'V2-R1':'All four local models; seven input/initial tests; numeric convergence, independent residues, ledgers, errors, figures and preserved attempts',
             'V2-R2':'Exact-material re21 restoration, resource allocation, scientific report and minimum eligible local model recommendation'}[stage],
             'commands_actually_executed':commands[stage]+['git ls-remote origin refs/heads/codex/pnas-topology-first'],
             'execution_notes':'R1 runner and verifier were each run for both preserved numerical attempts; only successor attempt_002 passes numerical sampling.' if stage=='V2-R1' else None,
             'numeric_status':'NOT_STARTED; STRUCTURE_PASS' if stage=='V2-R0' else 'PASS',
             'structural_test_count':5 if stage=='V2-R0' else 6,'independent_check_status':'NOT_STARTED' if stage=='V2-R0' else 'PASS',
             'scientific_outcomes':summaries['base' if stage=='V2-R1' else 'boundary']['decisions'] if stage!='V2-R0' else 'PROTOCOL_FROZEN; no trajectory or kinetic approval',
             'added_or_modified_files':files,'delivery':rec,
             'remaining_limits':['Local exogenous input and isolated S4 only','Original author constants only','No complete shared ATP/GTP pool validation','No arbitrary initial-composition reconstruction','No full coupled run or reduced-core approval']})
    dump(OUT/'round_execution_manifest.json',{'rounds':records,'attempt_001_preserved_native_status':'NUMERICALLY_UNRESOLVED_SAMPLING; independent trajectories PASS',
         'scope':'Commands list scientific executions and delivery; incidental read-only diagnostics are omitted.'})
    print('Recorded all three delivered rounds, actual commands, file lists, checks and scientific limits')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capture-base-sources',action='store_true'); ap.add_argument('--present-base',action='store_true'); ap.add_argument('--present-boundary',action='store_true'); ap.add_argument('--boundary-math',action='store_true'); ap.add_argument('--navigation',action='store_true'); ap.add_argument('--round-records',action='store_true')
    args=ap.parse_args()
    if args.capture_base_sources: capture_base_sources()
    if args.present_base: present_base()
    if args.present_boundary: present_boundary()
    if args.boundary_math: boundary_math()
    if args.navigation: navigation()
    if args.round_records: round_records()

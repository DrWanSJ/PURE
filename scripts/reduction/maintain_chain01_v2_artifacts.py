"""Add execution-source snapshots, corrected figure presentations and navigation."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import numpy as np

from prepare_chain01_v2 import ROOT,OUT,digest,dump


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
        nodes.append({'id':rel,'type':'derived_evidence','sha256':digest(path),'provenance':'EXTRACTED' if path.suffix in ('.gz','.json') else 'INFERRED',
             'confidence':'MEASURED_OR_GATE_DERIVED; NOT_SCIENTIFIC_PROMOTION','freshness':'Current final artifact bytes at '+datetime.now(timezone.utc).isoformat()})
        edges.append({'from':'configs/reduction/chain01_v2_validation.json','to':rel,'relation':'frozen observable contract constrains interpretation'})
    for s in source['sources']:
        edges.append({'from':s['path'],'to':'results/reduction/chain01_v2/mathematical_certificate.json','relation':'source supports exact columns and author-condition derivation'})
    dump(OUT/'evidence_navigation.json',{'role':'Derived navigation only; canonical sources, frozen protocol and raw evidence remain authoritative',
          'labels':['EXTRACTED','INFERRED','AMBIGUOUS'],'scientific_confidence':'Support is conditional on declared local domain and independent gates; no global approval',
          'nodes':nodes,'edges':edges})
    print('Updated source-bound evidence navigation')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--capture-base-sources',action='store_true'); ap.add_argument('--present-base',action='store_true'); ap.add_argument('--navigation',action='store_true')
    args=ap.parse_args()
    if args.capture_base_sources: capture_base_sources()
    if args.present_base: present_base()
    if args.navigation: navigation()

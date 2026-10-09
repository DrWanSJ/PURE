#!/usr/bin/env python3
"""Executed B1-2 mutations using exactly the independent positive acceptors."""
from collections import Counter,defaultdict
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json
import sys
import tempfile

sys.dont_write_bytecode=True
import verify_elongation_witnesses as v

def fixture(w,source,ids=None,extra=None):
    """Independent fixture compiler, not imported from the witness builder.

    Build honest markings/allocations for a changed firing list, then corrupt
    one claim. This prevents unrelated stale metadata from masking the target.
    """
    w=deepcopy(w)
    if ids is None:ids=[e['reaction_id'] for e in w['reaction_occurrences']]
    if extra:
        for s,n in extra.items():w['initial_marking'][s]=str(F(w['initial_marking'].get(s,'0'))+F(n))
    lots=[];bal={}
    for s,n in sorted(w['initial_marking'].items()):
        for i in range(int(F(n))):
            o='BOUNDARY:'+s+':'+str(i+1).zfill(2)
            lots.append({'origin':o,'species_id':s,'amount':'1','conditional':True,'author_initial_concentration':False});bal[o,s]=F(1)
    w['boundary_lots']=lots;es=[];dag=[]
    for i,r in enumerate(ids):
        q=source['reactions'][r];eid=f"{w['witness_id']}:E{i+1:02d}";bindings=[]
        for s,n in sorted(q['reactants'].items()):
            remaining=n
            for (o,t),quantity in sorted(bal.items()):
                if t!=s or not quantity:continue
                take=min(remaining,quantity)
                if take:
                    bindings.append({'origin':o,'species_id':s,'amount':str(take)});bal[o,s]-=take;remaining-=take
                    if not o.startswith('BOUNDARY:'):dag.append({'producer_event_id':o,'consumer_event_id':eid,'species_id':s,'amount':str(take),'evidence_status':'EXTRACTED'})
                if not remaining:break
            if remaining:raise ValueError('fixture cannot fire '+r+':'+s)
        for s,n in q['products'].items():bal[eid,s]=n
        es.append({'event_id':eid,'reaction_id':r,'inputs':v.a.strings(q['reactants']),'outputs':v.a.strings(q['products']),
                   'equation':v.a.equation(q['reactants'],q['products']),'input_origins':bindings,'occurrence_origin':eid,
                   'reference_parameter':str(source['parameters'][r]),'reference_activity':'REFERENCE_ENABLED' if source['parameters'][r]>0 else 'REFERENCE_DISABLED',
                   'level_c_contexts':source['annotations'][r]['level_c_functional_contexts']})
    w['reaction_occurrences']=es;w['event_dependencies']=dag;w['occurrence_vector']=dict(sorted(Counter(ids).items()))
    final,trace,net=v.petri(w,source);w['final_marking']=final;w['per_event_markings']=trace;w['exact_net_stoichiometry']=net
    w['net_reaction']=v.a.equation({s:-F(n) for s,n in net.items() if F(n)<0},{s:F(n) for s,n in net.items() if F(n)>0})
    w['resource_ledger']={s:{'initial':w['initial_marking'].get(s,'0'),'final':final.get(s,'0'),'net':net.get(s,'0'),
        'event_membership':[e['event_id'] for e in es if s in e['inputs'] or s in e['outputs']]} for s in v.LEDGER}
    return w

def event(w,n):return next(e for e in w['reaction_occurrences'] if e['reaction_id']==f're{n:010d}')

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input-dir',type=Path,default=v.OUT)
    p.add_argument('--report',type=Path,default=v.OUT/'phase_b1_2_negative_controls.json');args=p.parse_args()
    data=v.load(args.input_dir/'phase_b1_2_witnesses.json');scope=v.load(args.input_dir/'phase_b1_2_source_scope.json');source=v.sources()
    v.source_hashes(source);base=next(w for w in data['witnesses'] if w['witness_id']=='W3');controls=[]
    def test(cid,mutation,code,w=None,operation=None,stored=None,petri_expected=None):
        w=w or deepcopy(base);possible=True;petri_code=None
        try:v.petri(w,source)
        except Exception as e:possible=False;petri_code=getattr(e,'code',type(e).__name__)
        try:
            (operation or (lambda:v.check_witness(w,source)))();actual='ACCEPTED';diag='False claim accepted'
        except Exception as e:actual=getattr(e,'code',type(e).__name__);diag=str(e)
        ok=actual==code and (petri_expected is None or possible==petri_expected)
        controls.append({'id':cid,'input_mutation':mutation,'invariant_tested':code,'expected_rejection_code':code,
            'actual_rejection_code':actual,'petri_firing_possible':possible,'petri_rejection_code':petri_code,
            'required_petri_feasibility':petri_expected,'status':'PASS' if ok else 'FAIL','diagnostic':diag,
            'full_mutated_fixture':stored if stored is not None else w,'acceptance_entrypoint':'verify_elongation_witnesses.'+('check_witness' if operation is None else 'source_or_scope_acceptance')})
    w=deepcopy(base);event(w,13)['inputs'].pop(v.D);test('N01','Delete required first EF-Tu/Gly-tRNA co-reactant','SOURCE_REACTION_MISMATCH',w)
    w=deepcopy(base);event(w,13)['inputs']['tRNAGlyGCC']=event(w,13)['inputs'].pop(v.D);test('N02','Substitute uncharged tRNA for delivery complex','SOURCE_REACTION_MISMATCH',w)
    w=deepcopy(base);w['reaction_occurrences'].remove(event(w,14));test('N03','Skip EF-Tu GTP/GDP/PO4 transition','MISSING_REQUIRED_INPUT',w,petri_expected=False)
    w=deepcopy(base);event(w,16)['outputs']['PO4']='2';test('N04','Change source phosphate coefficient','SOURCE_REACTION_MISMATCH',w)
    w=deepcopy(base);w['reaction_occurrences'].remove(event(w,18));test('N05','Claim peptide formation without original precursor event','MISSING_REQUIRED_INPUT',w,petri_expected=False)
    w=deepcopy(base);w['initial_marking'].pop(v.G);w['boundary_lots']=[b for b in w['boundary_lots'] if b['species_id']!=v.G]
    test('N06','Omit required EF-G GTP supply','MISSING_REQUIRED_INPUT',w,petri_expected=False)
    w=deepcopy(base);e=event(w,25);e['outputs']['EFG_GTP']=e['outputs'].pop('EFG_GDP');test('N07','Replace source EF-G GDP release by GTP recovery','SOURCE_REACTION_MISMATCH',w)
    w=deepcopy(base);event(w,13)['reaction_id']='artificial_E2_Pept0002';test('N08','Invent direct E2 to peptide source reaction','UNKNOWN_REACTION',w,petri_expected=False)
    w=deepcopy(base);w['reaction_occurrences'].remove(event(w,68));test('N09','Enter round two without exact inter-round state','MISSING_REQUIRED_INPUT',w,petri_expected=False)
    w=deepcopy(base);event(w,68)['outputs'].pop('tRNAGlyGCC');test('N10','Falsely omit source uncharged Gly-tRNA release output','SOURCE_REACTION_MISMATCH',w)
    w=deepcopy(base);b=next(b for b in event(w,74)['input_origins'] if b['species_id']==v.D);b['origin']='BOUNDARY:'+v.D+':01'
    test('N11','Claim reuse of first Gly delivery lot despite independent full supplies','INVALID_LINEAGE',w,petri_expected=True)
    w=deepcopy(base);b=next(b for b in event(w,80)['input_origins'] if b['species_id']==v.G);b['origin']='BOUNDARY:'+v.G+':01'
    test('N12','Claim reuse of first EF-G lot without regeneration','INVALID_LINEAGE',w,petri_expected=True)
    w=deepcopy(base);event(w,79)['input_origins'][0]['origin']='NONEXISTENT_PRODUCER:01'
    test('N13','Give peptide precursor no genuine producer, complete Petri inventory retained','INVALID_LINEAGE',w,petri_expected=True)
    w=fixture(base,source,extra={'tRNAGlyGCC':'1'});b=next(b for b in event(w,74)['input_origins'] if b['species_id']==v.D);b['origin']='BOUNDARY:tRNAGlyGCC:01'
    test('N14','Extra unrelated uncharged tRNA lets global marking fire but false carrier allocation remains','INVALID_LINEAGE',w,petri_expected=True)
    # Honest extra round-two carrier is globally available; falsely splice it into
    # the single ribosome history. Regenerate the DAG so edge consistency alone
    # cannot reject the intended mutation.
    w=fixture(base,source,extra={v.ENTRY:'1'});e=event(w,74);b=next(b for b in e['input_origins'] if b['species_id']==v.ENTRY)
    old=b['origin'];b['origin']='BOUNDARY:'+v.ENTRY+':01'
    w['event_dependencies']=[d for d in w['event_dependencies'] if not(d['consumer_event_id']==e['event_id'] and d['species_id']==v.ENTRY)]
    test('N15','Petri-enabled extra second-round ribosome spliced into first-round history','INVALID_LINEAGE',w,petri_expected=True)
    w=deepcopy(base);w['claims']['EFTu_GDP_is_GTP_recovery']=True;test('N16','Treat EF-Tu GDP release as GTP recovery','FALSE_RECOVERY_CLAIM',w)
    sc=deepcopy(scope);sc['reactions']['re0000000069']['reference_activity']='REFERENCE_ENABLED'
    test('N17','Mark zero-parameter reverse 0069 reference-enabled','REFERENCE_ACTIVITY_MISMATCH',operation=lambda:v.check_scope(sc,source),stored=sc)
    w=deepcopy(base);w['occurrence_vector']['re0000000084']=1;test('N18','Automatically count unfired exact reverse 0084','OCCURRENCE_VECTOR_MISMATCH',w)
    w=deepcopy(base);w['resource_ledger']['GTP']['net']='-4';test('N19','Double-count free GTP already in composite supplies','RESOURCE_LEDGER_MISMATCH',w)
    w=deepcopy(base);w['exact_net_stoichiometry']['PO4']='3';test('N20','Miscount two-round PO4 output','NET_STOICHIOMETRY_MISMATCH',w)
    ids=[e['reaction_id'] for e in base['reaction_occurrences']]+['re0000000796']
    w=fixture(base,source,ids,extra={'RF1':'1'});event(w,796)['level_c_contexts']='ELONG_factor_binding'
    test('N21','Fire RF1 termination binding and falsely label elongation','TERMINATION_OUT_OF_SCOPE',w,petri_expected=True)
    w=deepcopy(base);w['claims']['global_moiety_conservation']=True;test('N22','Certify global moiety conservation from composite names','UNSUPPORTED_COMPOSITION_CERTIFICATE',w)
    with tempfile.TemporaryDirectory(prefix='b1-2-mutated-source-') as tmp:
        for suffix,path in [('SBML',v.a.SBML),('PARAMETER',v.a.PARAM),('ZIP',v.a.ZIP)]:
            altered=Path(tmp)/path.name;raw=path.read_bytes();mutated=raw+b'\nB1-2_ADVERSARIAL_MUTATION\n';altered.write_bytes(mutated)
            test('N23-'+suffix,'Alter disposable '+suffix+' source bytes, leaving canonical untouched','SOURCE_HASH_MISMATCH',
                 operation=lambda path=path,altered=altered:v.source_hashes(source,{path:altered}),stored={'source_path':str(path),'mutation':'append LF B1-2_ADVERSARIAL_MUTATION LF',
                 'original_sha256':hashlib.sha256(raw).hexdigest(),'mutated_sha256':hashlib.sha256(mutated).hexdigest(),'reproducible_copy_recipe':'Read original raw bytes and append UTF-8 mutation above; verify override copy'})
    w=deepcopy(base);w['claims']['kinetic_preference_measured']=True;test('N24','Promote ID tie-breaking to measured kinetic preference','UNSUPPORTED_KINETIC_INTERPRETATION',w)
    w=deepcopy(next(x for x in data['witnesses'] if x['witness_id']=='W4'));bridge=event(w,1);duplicate=deepcopy(bridge);duplicate['event_id']='W4:E31';duplicate['occurrence_origin']='W4:E31';w['reaction_occurrences'].append(duplicate)
    test('N25','Duplicate B1-1 initiator tRNA handoff 0001 in composition','DUPLICATE_HANDOFF',w,petri_expected=False)
    w=deepcopy(base);event(w,85)['reaction_id']='invented_translocation_jump';test('N26','Add artificial translocation source-state jump','UNKNOWN_REACTION',w,petri_expected=False)
    w=deepcopy(base);w['event_dependencies'].pop();test('N27','Delete actual producer-consumer DAG edge','EVENT_DAG_MISMATCH',w,petri_expected=True)
    w=deepcopy(base);w['claims']['EFG_GDP_is_GTP_recovery']=True;test('N28','Claim EF-G GTP regenerated from GDP-form release','FALSE_RECOVERY_CLAIM',w)
    passed=sum(c['status']=='PASS' for c in controls);special=[c for c in controls if c['expected_rejection_code']=='INVALID_LINEAGE' and c['petri_firing_possible']]
    report={'status':'PASS' if passed==len(controls) and len(special)>=4 else 'FAIL','controls_run':len(controls),'controls_passed':passed,
        'controls_failed':len(controls)-passed,'controls_not_run':0,'petri_enabled_lineage_invalid_cases':len(special),
        'petri_enabled_lineage_invalid_passed':sum(c['status']=='PASS' for c in special),'controls':controls,
        'canonical_files_modified':False,'acceptance_functions_identical_to_positive':True}
    v.save(args.report,report);print(json.dumps({k:report[k] for k in ('status','controls_run','controls_passed','controls_failed','petri_enabled_lineage_invalid_cases')}))
    if report['status']!='PASS':print(json.dumps([{'id':c['id'],'actual':c['actual_rejection_code'],'diagnostic':c['diagnostic']} for c in controls if c['status']!='PASS']))
    return 0 if report['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())

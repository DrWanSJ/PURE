"""Frozen-invariant adversarial fixtures; canonical inputs stay read-only."""
import copy,json,argparse,sys,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction as F
sys.dont_write_bytecode=True
import verify_witnesses as v
OUT=v.OUT;ROOT=v.ROOT
def main():
    p=argparse.ArgumentParser();p.add_argument('--input-dir',type=Path,default=OUT);p.add_argument('--report',type=Path,default=OUT/'phase_b1_3_negative_controls.json');a=p.parse_args()
    data=v.load(a.input_dir/'phase_b1_3_witnesses.json');inv=v.load(a.input_dir/'phase_b1_3_source_scope.json');src=v.source();allowed=inv['search_direction_ids'];ws={w['witness_id']:w for w in data['witnesses']}
    frozen=v.load(OUT/'phase_b1_3_verification_contract.json')
    v.need(frozen['verifier_sha256']==v.digest(Path(v.__file__)),'CONTRACT_CHANGED','verifier modified after controls registration')
    positives=[v.check_witness(w,src,allowed) for w in ws.values()];controls=[]
    def run(name,base,expected,mutator,mode='witness',description=''):
        original=ws[base] if mode=='witness' else inv if mode=='scope' else data
        fixture=copy.deepcopy(original);mutator(fixture)
        petri_enabled=None;lineage_valid=None;petri_error=None;lineage_error=None
        if mode=='witness':
            try:v.petri(fixture,src);petri_enabled=True
            except Exception as e:petri_enabled=False;petri_error=getattr(e,'code',type(e).__name__)
            if petri_enabled:
                try:v.lineage(fixture,src);lineage_valid=True
                except Exception as e:lineage_valid=False;lineage_error=getattr(e,'code',type(e).__name__)
        try:
            result=v.check_witness(fixture,src,allowed) if mode=='witness' else v.check_scope(fixture,src) if mode=='scope' else v.validate(fixture,inv)
            actual='ACCEPTED';output=json.dumps(result,sort_keys=True)
        except Exception as e:actual=getattr(e,'code',type(e).__name__);output=str(e)
        affected=sorted({e['reaction_id'] for e in fixture.get('reaction_occurrences',[])}) if mode=='witness' else []
        controls.append({'fixture_id':name,'base_witness':base,'mutation':description or name,'expected_error_category':expected,'actual_error_category':actual,'status':'PASS' if actual==expected else 'FAIL','petri_enabled':petri_enabled,'lineage_valid':lineage_valid,'petri_error':petri_error,'lineage_error':lineage_error,'canonical_reactions_affected':affected,'actual_verifier_output':output,'mode':mode,'fixture':fixture,'base_sha256':hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest()})
    def replace_label(w,role,new,event=None,output=True):
        events=w['reaction_occurrences'];e=events[event] if event is not None else next(e for e in events if any(role in t['labels'] for t in e['produced_tokens']))
        t=next(t for t in e['produced_tokens' if output else 'consumed_tokens'] if role in t['labels']);t['labels'][role]=new
    # Ten genuinely Petri-enabled source-state histories with false carrier identities.
    for name,base,role,label in [
      ('L01_SWAP_30S_ORIGIN','W_T1_RF1_RELEASE','R30','UNRELATED_30S_LOT'),
      ('L02_DUPLICATE_50S_AS_30S','W_T1_RF1_RELEASE','R50','INHERITED:'+v.T+':01:R30'),
      ('L03_SWAP_TERMINAL_TRNA','W_T2_RF2_RELEASE','TRNA','UPSTREAM_DISCARDED_GLY_TRNA'),
      ('L04_NEW_PEPTIDE_IDENTITY','W_T1_RF1_RELEASE','PEPTIDE','INVENTED_SECOND_PEPTIDE'),
      ('L05_RF1_RETURN_WITHOUT_ITS_ORIGIN','W_D1_RF1_DIRECT','RF1','UNRELATED_RF1_LOT'),
      ('L06_RF2_RETURN_WITHOUT_ITS_ORIGIN','W_D2_RF2_DIRECT','RF2','UNRELATED_RF2_LOT'),
      ('L07_RF3_WRONG_BOUND_CARRIER','W_F1_RF1_RF3_EXCHANGE','RF3','RF3_OTHER_NUCLEOTIDE_LOT'),
      ('L08_REUSE_CONSUMED_UPSTREAM_EFG','W_R1_RF1_TO_RECYCLING','EFG','B1_2_CONSUMED_EFG_GTP_LOT'),
      ('L09_RRF_TELEPORT','W_R2_RF2_TO_RECYCLING','RRF','UNDECLARED_RRF_LOT'),
      ('L10_MRNA_FROM_OTHER_RIBOSOME','W_R1_RF1_TO_RECYCLING','MRNA','UNRELATED_MRNA_LOT')]:
        run(name,base,'INVALID_LINEAGE',lambda w,role=role,label=label:replace_label(w,role,label))
    def canonical_event(w,r):
        q=src['reactions'][r];i=len(w['reaction_occurrences'])+1
        return {'event_id':w['witness_id']+':E'+str(i).zfill(3),'reaction_id':r,'inputs':v.exact(q['reactants']),'outputs':v.exact(q['products']),'equation':v.independent.equation(q['reactants'],q['products']),'reference_parameter':str(src['parameters'][r]),'reverse_reaction_ids':v.reverse_ids(r,src),'source_segment':'B1_3','consumed_tokens':[],'produced_tokens':[]}
    def add_event(w,r,stock=None):
        for s,n in (stock or {}).items():w['initial_marking'][s]=str(F(w['initial_marking'].get(s,'0'))+n)
        w['reaction_occurrences'].append(canonical_event(w,r))
    run('N11_BOTH_RFS_ONE_CONSUMED_T','W_T1_RF1_RELEASE','NOT_PETRI_ENABLED',lambda w:add_event(w,'re0000000811',{'RF2':1}),description='After RF1 release, attempt RF2 binding with sufficient free RF2 but no T_pre')
    run('N12_DOUBLE_FREE_PEPTIDE_RELEASE','W_T1_RF1_RELEASE','NOT_PETRI_ENABLED',lambda w:add_event(w,'re0000000798'))
    run('N13_PEPTYL_TRNA_AS_FREE_PRODUCT','W_T1_RF1_RELEASE','FINAL_SOURCE_MARKING',lambda w:w['final_marking'].update({'Pept0003tRNAGlyGCC':w['final_marking'].pop('Pept0003')}))
    run('N14_RETURN_RF1_WITHOUT_STEP','W_T1_RF1_RELEASE','FINAL_SOURCE_MARKING',lambda w:w['final_marking'].update({'RF1':'1'}))
    run('N15_RETURN_RF2_WITHOUT_STEP','W_T2_RF2_RELEASE','FINAL_SOURCE_MARKING',lambda w:w['final_marking'].update({'RF2':'1'}))
    def wrong_bound_state(w):
        e=next(e for e in w['reaction_occurrences'] if any('RF3' in t['labels'] for t in e['consumed_tokens']));t=next(t for t in e['consumed_tokens'] if 'RF3' in t['labels']);t['species_id']='RF3_GTP'
    run('N16_REUSE_RF3_IN_INCOMPATIBLE_STATE','W_F1_RF1_RF3_EXCHANGE','INVALID_LINEAGE',wrong_bound_state)
    run('N17_BOUND_GDP_TO_FREE_GTP','W_F1_RF1_RF3_EXCHANGE','RESOURCE_LEDGER',lambda w:w['resource_ledger']['GTP'].update({'final':'1','event_net':'0'}))
    run('N18_REUSE_EFG_GTP_AFTER_CONSUMPTION','W_R1_RF1_TO_RECYCLING','NOT_PETRI_ENABLED',lambda w:add_event(w,'re0000000895',{v.TERM+'_RRF':1}),description='One extra finite terminated complex supplied; only missing input is already consumed EFG_GTP')
    run('N19_PREMATURE_FREE_30S','W_T1_RF1_RELEASE','FINAL_SOURCE_MARKING',lambda w:w['final_marking'].update({'RS30S':'1'}))
    run('N20_PREMATURE_FREE_50S','W_T2_RF2_RELEASE','FINAL_SOURCE_MARKING',lambda w:w['final_marking'].update({'RS50S':'1'}))
    run('N21_OMIT_MRNA_DISPOSITION','W_R1_RF1_TO_RECYCLING','FINAL_SOURCE_MARKING',lambda w:w['final_marking'].pop('mRNA'))
    run('N22_OMIT_TRNA_DISPOSITION','W_R2_RF2_TO_RECYCLING','RESOURCE_LEDGER',lambda w:w['resource_ledger'].pop('tRNAGlyGCC'))
    run('N23_DOUBLE_COUNT_PO4','W_R1_RF1_TO_RECYCLING','RESOURCE_LEDGER',lambda w:w['resource_ledger']['PO4'].update({'final':'2','event_net':'2'}))
    def disabled(w):
        w['initial_marking']={'Pept0003':'1',v.TERM+'_RF1':'1'};w['reaction_occurrences']=[canonical_event({**w,'reaction_occurrences':[]},'re0000000810')]
    run('N24_ZERO_PARAMETER_RELEASE_REVERSE_AS_ACTIVE','W_T1_RF1_RELEASE','AUTHOR_DISABLED_DIRECTION',disabled)
    run('N25_ALTER_EXACT_REVERSE','W_T1_RF1_RELEASE','REVERSE_PAIR_MISMATCH',lambda w:w['reaction_occurrences'][0].update({'reverse_reaction_ids':['re0000000812']}))
    run('N26_ALTER_RELEASE_COEFFICIENT','W_T1_RF1_RELEASE','SOURCE_COEFFICIENT_MISMATCH',lambda w:w['reaction_occurrences'][1]['outputs'].update({'Pept0003':'2'}))
    run('N27_SKIP_OCCUPIED_INTERMEDIATE','W_R1_RF1_TO_RECYCLING','EVENT_HISTORY',lambda w:w['per_event_markings'].__setitem__(2,copy.deepcopy(w['per_event_markings'][3])))
    def similar_state(w):w['initial_marking']={v.TERM+'_RF2':'1','Pept0003':'1'}
    run('N28_SOURCE_DISTINCT_RF_BOUNDARY','W_D1_RF1_DIRECT','NOT_PETRI_ENABLED',similar_state)
    def invalid_order(w):
        e=w['reaction_occurrences'];e[0],e[1]=e[1],e[0]
        for i,x in enumerate(e):x['event_id']=w['witness_id']+':E'+str(i+1).zfill(3)
    run('N29_SAME_NET_INVALID_ORDER','W_T1_RF1_RELEASE','NOT_PETRI_ENABLED',invalid_order)
    run('N30_PARAMETER_FALSIFICATION','W_T2_RF2_RELEASE','PARAMETER_MISMATCH',lambda w:w['reaction_occurrences'][1].update({'reference_parameter':'0.5'}))
    run('N31_OMIT_SOURCE_DIRECTION','', 'SCOPE_COVERAGE',lambda x:x['reactions'].pop('re0000000810'),'scope')
    run('N32_MATHML_COEFFICIENT_LOSS','', 'SOURCE_COEFFICIENT_MISMATCH',lambda x:x['reactions']['re0000000414']['products'].update({'PO4':'1'}),'scope')
    run('N33_DROP_DISABLED_INVENTORY_CONTEXT','', 'SCOPE_MEMBERSHIP',lambda x:x['selected_direction_ids'].remove('re0000000810'),'scope')
    run('N34_SOURCE_BASELINE_HASH_FALSIFIED','', 'SOURCE_HASH_MISMATCH',lambda x:x.update({'source_baseline_sha256':'0'*64}),'data')
    run('N35_FALSE_SCIENTIFIC_APPROVAL','W_T1_RF1_RELEASE','SCIENTIFIC_BOUNDARY',lambda w:w.update({'scientific_status':'B1_3_FORMALLY_ACCEPTED'}))
    run('N36_FALSE_ENDOGENOUS_REGENERATION','W_R2_RF2_TO_RECYCLING','SCIENTIFIC_BOUNDARY',lambda w:w['claims'].update({'endogenous_EFG_GTP_regeneration':True}))
    lineage_cases=[c for c in controls if c['petri_enabled'] and c['lineage_valid'] is False and c['actual_error_category']=='INVALID_LINEAGE']
    passed=sum(c['status']=='PASS' for c in controls)
    report={'status':'PASS' if passed==len(controls) and len(controls)>=24 and len(lineage_cases)>=5 else 'FAIL','controls_run':len(controls),'controls_passed':passed,'controls_failed':len(controls)-passed,'petri_enabled_lineage_invalid_count':len(lineage_cases),'positive_witnesses_checked':len(positives),'verifier_sha256':frozen['verifier_sha256'],'control_contract_sha256':v.digest(OUT/'phase_b1_3_verification_contract.json'),'fixtures':controls,'canonical_files_written':False}
    v.save(a.report,report)
    if report['status']!='PASS':
        with (OUT/'phase_b1_3_failure_evidence.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps({'stage':'negative_controls','failed':[ {k:x[k] for k in ['fixture_id','expected_error_category','actual_error_category','actual_verifier_output']} for x in controls if x['status']=='FAIL']})+'\n')
    print(json.dumps({k:report[k] for k in ['status','controls_run','controls_passed','controls_failed','petri_enabled_lineage_invalid_count']}));return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())

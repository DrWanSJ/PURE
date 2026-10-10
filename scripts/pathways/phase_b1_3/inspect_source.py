"""Source-exact inventory. No pathway discovery or kinetic interpretation."""
import sys
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json, hashlib, csv

sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/reduction/pathways'
sys.path.insert(0,str(ROOT/'scripts/pathways/phase_b0'))
import build_phase_b0_witnesses as source_reader
sys.path.insert(0,str(ROOT/'scripts/pathways/phase_b1_2'))
from build_elongation_witnesses import membership
T='elRS70SAUAA0004_Pept0003tRNAGlyGCC'
TERM='termRS70SUAA0004_tRNAGlyGCC'
CONTEXT={'TERM_factor_binding','TERM_peptide_release','TERM_energy_coupling','RECYCLE_disassembly'}
FACTORS={'RF1','RF2','RF3','RF3_GDP','RF3_GTP','RRF','EFG','EFG_GDP','EFG_GTP'}
TERMFILES={'Termination_A_RF1.xml','Termination_A_RF2.xml','Termination_B_RF1.xml','Termination_B_RF2.xml'}
def load(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_bytes((json.dumps(x,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode())
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def inventory():
    rx=source_reader.read_source();ms=membership(rx)
    term={r for r,q in rx.items() if set(q['level_c'].split(';'))& (CONTEXT-{'RECYCLE_disassembly'}) or any(Path(m['source_file']).name in TERMFILES for m in ms[r])}
    recycle={r for r,q in rx.items() if 'RECYCLE_disassembly' in q['level_c'].split(';') or any(Path(m['source_file']).name=='Termination_C.xml' for m in ms[r])}
    core=term|recycle
    anchors={s for r in core for side in ['reactants','products'] for s in rx[r][side] if s.startswith(('termRS','elRS','RS50S_')) or s in FACTORS}|{T}
    incident={r for r,q in rx.items() if anchors&(set(q['reactants'])|set(q['products']))}
    reverse={s for r in core for s in rx[r]['reverse_reaction_ids']}
    selected=core|incident|reverse
    rows={}
    for r,q in rx.items():
        kind='OUT_OF_B1_3_SCOPE' if r not in selected else 'AUTHOR_DISABLED_CONTEXT' if F(q['reference_parameter'])==0 else 'RECYCLE_SEARCH_SCOPE' if r in recycle else 'TERM_SEARCH_SCOPE' if r in term else 'SOURCE_REVERSE_OR_COMPETITOR' if r in reverse else 'SHARED_BOUNDARY_CONTEXT'
        species=sorted(set(q['reactants'])|set(q['products']))
        rows[r]={**q,'classification':kind,'selected':r in selected,'core':r in core,'original_subsystem_memberships':ms[r],
          'selection_reasons':[k for k,v in [('TERMINATION_CORE',r in term),('RECYCLING_CORE',r in recycle),('ONE_HOP_BOUNDARY',r in incident),('EXACT_REVERSE',r in reverse)] if v],
          'ribosomal_factor_states':[s for s in species if s.startswith(('termRS','elRS','RS30S','RS50S')) or any(f in s for f in FACTORS)],
          'nucleotide_forms':[s for s in species if s in {'GDP','GTP','PO4','ATP','ADP','AMP','PPi'} or '_GDP' in s or '_GTP' in s or '_PO4' in s],
          'boundary_species':[s for s in species if s in anchors],
          'degradation':any('_degraded' in s for s in species),'evidence_status':'EXTRACTED','confidence':'EXACT_SOURCE_DIRECTION','freshness':'CANONICAL_HASH_BOUND','authority':'CANONICAL_SBML_AND_AUTHOR_CSV'}
    allowed=sorted(r for r in core if F(rx[r]['reference_parameter'])>0)
    return {'reactions':rows,'classification_precedence':['OUT_OF_B1_3_SCOPE','AUTHOR_DISABLED_CONTEXT','RECYCLE_SEARCH_SCOPE','TERM_SEARCH_SCOPE','SOURCE_REVERSE_OR_COMPETITOR','SHARED_BOUNDARY_CONTEXT'],
      'core_direction_ids':sorted(core),'selected_direction_ids':sorted(selected),'search_direction_ids':allowed,'boundary_anchor_species':sorted(anchors),
      'coverage':{'all_directions':len(rx),'selected':len(selected),'core':len(core),'search_positive':len(allowed),'selected_positive':sum(F(rx[r]['reference_parameter'])>0 for r in selected),'selected_zero':sum(F(rx[r]['reference_parameter'])==0 for r in selected),'classification_counts':dict(sorted(Counter(q['classification'] for q in rows.values()).items()))},
      'source_provenance':[source_reader.provenance(p,a) for p,a in [(source_reader.SOURCE,'CANONICAL_SBML'),(source_reader.CSV,'AUTHOR_OPERATIONAL_PARAMETER'),(source_reader.V2,'REVIEWED_CONTEXT')]],
      'incidence':{s:{'producers':[r for r,q in rx.items() if s in q['products']],'consumers':[r for r,q in rx.items() if s in q['reactants']]} for s in sorted(anchors)},
      'limits':'One-hop boundary inventory; representative directed Petri witnesses, not complete route enumeration.'}

"""Join frozen functional navigation labels without changing CSP quantities."""
from r4_fast_block_common_v1 import *
import pandas as pd
source=DOC/'reaction_level_annotation_v2.csv';a=pd.read_csv(source,dtype=str).set_index('reaction_id');p=OUT/'mixed_csp_mode_block'
for name in ['m4_reaction_participation.csv','reaction_ranked_support.csv']:
 f=pd.read_csv(p/name);assert set(f.reaction_id)<=set(a.index)
 for dest,src in [('canonical_functional_modules','level_a_module_candidates'),('canonical_functional_subsystems','level_b_subsystem_candidates'),('canonical_functional_stage','level_c_primary_stage'),('functional_annotation_status','functional_annotation_status'),('source_annotation_human_review_status','human_review_status')]:f[dest]=f.reaction_id.map(a[src])
 f['functional_navigation_evidence_status']='EXTRACTED_FROM_FROZEN_ANNOTATION_NOT_REDUCTION_AUTHORITY';f.to_csv(p/name,index=False)
write_json(p/'functional_annotation_provenance.json',{'source_relative_path':str(source.relative_to(ROOT)).replace('\\','/'),'source_sha256':sha(source),'role':'Frozen reaction-local navigation annotation. CSP participation and source equations independently recomputed. No reaction decision or chemical mapping approval.'})
print('Canonical functional annotation joined; numerical quantities unchanged',flush=True)

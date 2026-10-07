"""37 additional frozen laws are diagnostics only, never parent deletion authority."""
from r4_fast_block_common_v1 import *
from fractions import Fraction
def run(completed_only=False):
 s=SourceCoordinateRuntime('source_coordinate_certificate_v4.json');lawrows=list(csv.DictReader((DOC/'conservation_laws_v0.csv').open()));matrix=np.zeros((len(lawrows),241))
 for j,row in enumerate(lawrows):
  for n,v in json.loads(row['species_coefficients_json']).items():matrix[j,s.index[n]]=float(Fraction(str(v)))
 assert sum(row['scope']=='SOURCE_GENERAL' for row in lawrows)==27 and len(lawrows)==64
 records=[];identity=[]
 for family in ['GlyRS','MetRS']:
  r=R4FamilyRuntime(family)
  for j,row in enumerate(lawrows):identity.append({'family':family,'law_id':row['conservation_id'],'scope':row['scope'],'law_D_max_abs':float(max(abs(matrix[j]@r.D))),'role':'GENERIC_INVENTORY' if row['scope']=='SOURCE_GENERAL' else 'FROZEN_PARAMETER_CROSSCHECK_ONLY'})
  for c in REG['conditions']:
   name=c['condition_id'];p=OUT/(family.lower()+'_only')/name
   path=p/'state_trajectories.npz'
   if not path.exists():path=p/'recovered_state_trajectories.npz'
   if not path.exists():
    if completed_only:continue
    continue
   data=np.load(path);full=data['full_state'];red=data['reduced_state'];x0=condition_initial(s,name);initial=matrix@x0
   for j,row in enumerate(lawrows):
    # Stable differences avoid subtracting large nearly equal total values.
    ff=np.array([math.fsum(matrix[j,k]*(x[k]-x0[k]) for k in np.nonzero(matrix[j])[0]) for x in full]);rr=np.array([math.fsum(matrix[j,k]*(x[k]-x0[k]) for k in np.nonzero(matrix[j])[0]) for x in red])
    records.append({'family':family,'condition':name,'law_id':row['conservation_id'],'scope':row['scope'],'initial_inventory':float(initial[j]),'full_max_absolute_inventory_drift':float(max(abs(ff))),'reduced_max_absolute_inventory_drift':float(max(abs(rr))),'full_max_normalized_inventory_drift':float(max(abs(ff))/max(abs(initial[j]),1e-12)),'reduced_max_normalized_inventory_drift':float(max(abs(rr))/max(abs(initial[j]),1e-12)),'zero_inventory_normalization_qualification':'INIT_ZERO_ROUNDOFF_SENSITIVE' if initial[j]==0 else 'NONZERO_INITIAL_INVENTORY','role':'GENERIC_INVENTORY' if row['scope']=='SOURCE_GENERAL' else 'FROZEN_PARAMETER_CROSSCHECK_ONLY','no_new_generic_elimination':True})
 write_csv(OUT/'coordinate_inventory_identities.csv',identity)
 if records:write_csv(OUT/'frozen_law_crosscheck.csv',records)
 write_json(OUT/'frozen_law_crosscheck_summary.json',{'laws':64,'source_general':27,'additional_frozen_only':37,'coordinate_D_all_laws_max_abs':max(row['law_D_max_abs'] for row in identity),'generic_parent_dimension':214,'frozen_execution_dimension_not_used_as_parent':177,'record_count':len(records),'role':'Additional laws are cross-check only; no numerical gate changed. Zero-inventory normalized errors retain explicit roundoff qualification.'})
 print('Frozen-law cross-check records',len(records),flush=True)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--completed-only',action='store_true');a=p.parse_args();run(a.completed_only)

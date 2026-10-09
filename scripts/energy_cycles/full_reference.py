"""Execute the unchanged full PNAS network on a checked derived author overlay.

Uses existing normalized bytes and never rewrites any protected source.
"""
import hashlib
import json
import platform
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np
import roadrunner

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/energy_cycles_v1'
NS='{http://www.sbml.org/sbml/level2/version4}'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    regpath=ROOT/'docs/reduction/energy_cycles/validation_preregistration.json'
    reg=json.loads(regpath.read_text());freeze=json.loads((OUT/'preregistration_freeze.json').read_text())
    if sha(regpath)!=freeze['sha256']:raise RuntimeError('Preregistration mutated')
    d=json.loads((OUT/'source_inventory.json').read_text());dest=OUT/'full_reference_retry1'
    if dest.exists():raise RuntimeError('Do not overwrite reference evidence')
    dest.mkdir()
    normalized=ROOT/'models/pnas2017_full_reference/normalized/fMGG_synthesis_constant_stoichiometry.xml'
    if sha(normalized)!=d['source_hashes'][str(normalized.relative_to(ROOT)).replace('\\','/')]:raise RuntimeError('Normalized source hash differs')
    tree=ET.fromstring(normalized.read_bytes());model=tree.find(NS+'model')
    species=model.findall(NS+'listOfSpecies/'+NS+'species');reactions=model.findall(NS+'listOfReactions/'+NS+'reaction')
    rows={r['id']:r for r in d['reactions']}
    for s in species:s.set('initialConcentration',str(d['initial'][s.get('id')]))
    for r in reactions:r.find(NS+'kineticLaw/'+NS+'listOfParameters/'+NS+'parameter').set('value',str(rows[r.get('id')]['k']))
    overlay=ET.tostring(tree,encoding='utf-8',xml_declaration=True)
    execution=dest/'derived_full_author_conditions.xml';execution.write_bytes(overlay)
    names=d['species_ids'];energy=[r['id'] for r in d['reactions'] if any(r['id'] in u['reaction_ids'] for u in d['units'])]
    grid=np.array(reg['comparison_grid']);results={};manifest={'source_commit':reg['source_commit'],'source_hashes':d['source_hashes'],
      'scientific_status':'SOURCE_REFERENCE_DIAGNOSTIC_ONLY; no candidate embedding or FULL_MODEL_VALIDATED claim',
      'parameter_set':'Author simulator ZIP CSV unmodified, all968 channels and original241 species',
      'initial_conditions':d['initial'],'preregistration_sha256':sha(regpath),'command':sys.argv,
      'code_sha256':sha(Path(__file__)),'environment':{'python':sys.version,'platform':platform.platform(),'roadrunner':roadrunner.__version__,'numpy':np.__version__},
      'execution_sbml_sha256':sha(execution),'units_warning':d['units_warning'],'runs':{}}
    for label,rtol,atol in [('base',1e-8,1e-10),('tight',1e-10,1e-12)]:
        start=time.monotonic();rr=roadrunner.RoadRunner(overlay.decode());rr.setIntegrator('cvode');ig=rr.getIntegrator()
        ig.setValue('stiff',True);ig.setValue('relative_tolerance',rtol);ig.setValue('absolute_tolerance',atol);ig.setValue('maximum_num_steps',200000)
        sid=list(rr.model.getFloatingSpeciesIds());rid=list(rr.model.getReactionIds());S=np.asarray(rr.getFullStoichiometryMatrix())
        expected=np.zeros_like(S);si={s:i for i,s in enumerate(sid)};ri={r:i for i,r in enumerate(rid)}
        for r in d['reactions']:
            for side,sgn in [('reactants',-1),('products',1)]:
                for s,c in r[side].items():expected[si[s],ri[r['id']]]+=sgn*c
        if not np.array_equal(S,expected):raise RuntimeError('Imported source stoichiometry differs')
        if S[si['PO4'],ri['re0000000414']]!=2:raise RuntimeError('MathML coefficient lost')
        a=np.asarray(rr.simulate(times=grid,selections=['time']+['['+s+']' for s in names]+energy))
        if not np.array_equal(a[0,1:242],np.array([d['initial'][s] for s in names])):raise RuntimeError('Engine lost t=0 initial state')
        if not np.all(np.isfinite(a)):raise RuntimeError('Nonfinite reference trajectory')
        path=dest/(label+'.npz');np.savez_compressed(path,time=a[:,0],species=np.array(names),concentrations=a[:,1:242],energy_reaction_ids=np.array(energy),energy_rates=a[:,242:])
        results[label]=a
        manifest['runs'][label]={'solver':'CVODE stiff','relative_tolerance':rtol,'absolute_tolerance':atol,'maximum_num_steps':200000,
          'imported_stoichiometry_exact':True,'PO4_re414_coefficient':2,'all241_initial_values_at_t0_exact':True,
          'minimum_unclipped_species':float(np.min(a[:,1:242])),'Pept0003_endpoint':float(a[-1,names.index('Pept0003')+1]),
          'path':str(path.relative_to(ROOT)).replace('\\','/'),'sha256':sha(path),'wall_seconds':time.monotonic()-start}
        (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        print(json.dumps(manifest['runs'][label]),flush=True)
    diff=abs(results['tight']-results['base']);manifest['convergence']={'maximum_species_absolute_difference':float(np.max(diff[:,1:242])),
      'Pept0003_endpoint_absolute_difference':float(diff[-1,names.index('Pept0003')+1]),
      'energy_resource_max_absolute_difference':{s:float(np.max(diff[:,names.index(s)+1])) for s in ['ATP','ADP','AMP','GTP','GDP','CP','Cr','PPi','PO4']}}
    manifest['execution_status']='COMPLETE_SOURCE_REFERENCE_ONLY'
    (dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()

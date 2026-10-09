"""Preserve an additive attempt and freeze a corrected diagnostics runner."""
import json
from datetime import datetime,timezone
from pathlib import Path
from runtime import ROOT,OUT,sha,write_json

def main():
    old=ROOT/'scripts/energy_cycles/ndk_coordinate_rerun.py'
    new=ROOT/'scripts/energy_cycles/ndk_coordinate_rerun_v2.py'
    if new.exists():raise RuntimeError('Do not overwrite correction')
    text=old.read_text().replace('ndk_numerical_repair_preregistration.json','ndk_numerical_repair_preregistration_v2.json').replace("numerical_ndk_coordinate'","numerical_ndk_coordinate_v2'").replace('maximum_extent_quadrature_coordinate_difference','maximum_extent_coordinate_vs_direct_quadrature_error')
    new.write_text(text)
    before=ROOT/'docs/reduction/energy_cycles/ndk_numerical_repair_preregistration.json';a=json.loads(before.read_text())
    previous=list((OUT/'numerical_ndk_coordinate').rglob('metrics.json'))
    a.update({'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'parent_engineering_addendum_sha256':sha(before),'version':'v2_reporting_key_correction',
      'correction':'Fix a diagnostic print field name that raised after saving the first mode. Physical integration library, scientific candidate, scenarios, gates, grids and tolerances are unchanged.',
      'prior_attempt':'Stopped after one completed comparison was saved and diagnostic print failed; preserve its metrics, reporting failure and native log. It is not counted twice in final scenario statistics.',
      'prior_metric_files':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in previous},
      'commands':['python scripts/energy_cycles/ndk_coordinate_rerun_v2.py'],
      'implementation_sha256':{'scripts/energy_cycles/ndk_depletion_coordinate.py':sha(ROOT/'scripts/energy_cycles/ndk_depletion_coordinate.py'),'scripts/energy_cycles/ndk_coordinate_rerun_v2.py':sha(new)}})
    add=ROOT/'docs/reduction/energy_cycles/ndk_numerical_repair_preregistration_v2.json'
    if add.exists():raise RuntimeError('Addendum already frozen')
    write_json(add,a)
    write_json(OUT/'ndk_reporting_correction.json',{'diagnostic_error':'Wrong dictionary key in progress print, after saved metrics.','preserved_prior_metrics':a['prior_metric_files'],'prior_failure':'numerical_ndk_coordinate/NDK__CHALLENGE_ATP_DOUBLE/failure.json','prior_log':'NDK_coordinate_rerun.log','new_addendum_sha256':sha(add),'scientific_model_change':False})
    print(json.dumps({'new_addendum_sha256':sha(add),'preserved_prior_metrics':len(previous)}))

if __name__=='__main__':main()

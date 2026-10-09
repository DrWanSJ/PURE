"""Separately preregistered supplemental source-supported PPi synthesis probe.

This does not change or rescore the 54 frozen v1 conditions or their decisions.
"""
import json
from datetime import datetime,timezone
from pathlib import Path
import runtime

ROOT=runtime.ROOT;OUT=runtime.OUT

def main():
    original=ROOT/'docs/reduction/energy_cycles/validation_preregistration.json'
    reg=json.loads(original.read_text());d=json.loads((OUT/'source_inventory.json').read_text())
    for f,v in reg['implementation_sha256'].items():
        if runtime.sha(ROOT/f)!=v:raise RuntimeError('Original scientific implementation changed')
    unit=next(u for u in d['units'] if u['name']=='PPiase');E=unit['enzyme_total_initial'];initial={s:d['initial'][s] for s in unit['all_species']}
    initial.update({'PPi':1.,'PO4':10000.})
    case={'id':'PPiase__SUPPLEMENTAL_REVERSE_DRIVE','unit':'PPiase','condition':'SUPPLEMENTAL_REVERSE_DRIVE',
        'initial_original':initial,'enzyme_total':E,'initial_modes':['ORIGINAL_NONEQUILIBRIUM','PROJECTED_PHYSICAL_CLOSURE'],
        'projection':'Same physical total-resource closure and matching inventories as frozen v1',
        'concentration_scales':{'PPi':1.,'PO4':10000.},'bound_scales':{'PPi':1.,'PO4':1.},'occupancy_scale':E,'cumulative_extent_scale':1.,
        'note':'Explicit held-out source-reverse-driving condition. Original v1 product-rich case is retained unchanged and did not give reverse net endpoint; this probe tests chemistry, not threshold improvement or original qualification.'}
    supplemental=ROOT/'docs/reduction/energy_cycles/ppiase_reverse_probe_preregistration.json'
    if supplemental.exists():raise RuntimeError('Do not overwrite supplemental registration')
    reg.update({'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'parent_preregistration_sha256':runtime.sha(original),
      'scope':'SUPPLEMENTAL_SOURCE_DIRECTION_PROBE_NOT_A_REPLACEMENT_FOR_V1','scenarios':[case],
      'rationale':'Exact active source reverse-cycle witness and source stationary-law numerator permit PPi synthesis. No parameter fitting, gate/scale alteration of original cases, or model promotion.',
      'supplemental_runner_sha256':runtime.sha(Path(__file__)),'comparisons_executed_before_supplemental_freeze':False})
    runtime.write_json(supplemental,reg)
    runtime.write_json(OUT/'ppiase_reverse_probe_freeze.json',{'preregistration_sha256':runtime.sha(supplemental),'parent_sha256':runtime.sha(original),'code_sha256':runtime.sha(Path(__file__))})
    # Output routing only: original candidate functions and equations are reused.
    runtime.OUT=OUT/'supplemental_ppiase_reverse';runtime.REG=supplemental
    runtime.run_case(d,case,reg)

if __name__=='__main__':main()

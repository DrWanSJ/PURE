"""Derive research reports, figures and evidence navigation from preserved results."""
from __future__ import annotations
import json
import hashlib
import platform
import sys
from collections import Counter
from pathlib import Path
import numpy as np
from runtime import ROOT, OUT, sha, write_json

DOC=ROOT/'docs/reduction/energy_cycles'

def main():
    d=json.loads((OUT/'source_inventory.json').read_text());reg=json.loads((DOC/'validation_preregistration.json').read_text())
    metricpaths=list((OUT/'numerical').rglob('metrics.json'))+list((OUT/'numerical_ndk_coordinate_v2').rglob('metrics.json'))
    ms=[json.loads(p.read_text()) for p in metricpaths]
    domains=[json.loads(p.read_text()) for p in (OUT/'numerical').rglob('domain_failure.json')]
    native=[json.loads(p.read_text()) for p in (OUT/'numerical').rglob('failure.json')]
    embedding=json.loads((OUT/'embedding_domain_audit.json').read_text())
    full=json.loads((OUT/'full_reference_retry1/manifest.json').read_text())
    supplemental_paths=list((OUT/'supplemental_ppiase_reverse').rglob('metrics.json'))
    supplemental=[json.loads(p.read_text()) for p in supplemental_paths]
    summary={'scientific_status':'KINETIC_CANDIDATES_WITH_BLOCKED_DOMAIN_QUALIFICATION; HUMAN_REVIEW_REQUIRED',
      'source_commit':d['source_commit'],'source_hashes':d['source_hashes'],'preregistration_sha256':sha(DOC/'validation_preregistration.json'),
      'registered_scenarios':len(reg['scenarios']),'completed_comparison_pairs':len(ms),'scenario_gate_statuses':dict(Counter(m['scientific_status'] for m in ms)),
      'supplemental_reverse_probe':{'scope':'Separate frozen probe, excluded from original54condition qualification','completed_pairs':len(supplemental),'statuses':dict(Counter(m['scientific_status'] for m in supplemental)),
        'endpoint_net_extents':{m['initial_mode']:m['endpoint_net_extents'] for m in supplemental}},
      'preserved_superseded_ndk_comparison_pairs':len(list((OUT/'numerical_ndk_coordinate').rglob('metrics.json'))),
      'domain_stops':domains,'native_solver_failures_preserved':native,'units':{},'full_embedding':'BLOCKED; MK/PPiase physical total closures unavailable at actual author startup samples',
      'full_source_reference':full['runs'],'promotion':False,'approved_reduced_SBML_created':False,'PURE_reduced_core':'UNCHANGED_NOT_APPROVED'}
    rows=[]
    nets={'CK':'CP + ADP ⇄ Cr + ATP','NDK':'ATP + GDP → ADP + GTP','MK':'ATP + AMP ⇄ 2 ADP','PPiase':'PPi ⇄ 2 PO4'}
    longkeys=['max_scaled_free','max_scaled_retained','normalized_net_flux_rms','max_normalized_cumulative_resource_flow']
    for u in d['units']:
        name=u['name'];mm=[m for m in ms if m['id'].startswith(name+'__')]
        maxima={k:max(m['windows'][-1][k] for m in mm) for k in longkeys}
        W0={k:max(m['windows'][0][k] for m in mm) for k in longkeys}
        W1={k:max(m['windows'][1][k] for m in mm) for k in longkeys}
        evidence={'net_stoichiometry':nets[name],'source_status':'SOURCE_VERIFIED','structure_status':'STRUCTURE_VERIFIED','kinetic_status':'KINETIC_CANDIDATE',
          'validation_status':'BLOCKED','blocked_reason':'Physical total-closure domain qualification is incomplete','SUBSYSTEM_VALIDATED':False,'FULL_MODEL_VALIDATED':False,
          'recommendation':'REVISE_WITH_EXTRA_STATE','comparison_pairs':len(mm),'long_maxima':maxima,'initial_layer_maxima':W0,'transition_maxima':W1,
          'maximum_normalized_conservation_residual':max(m['normalized_conservation_residual'] for m in mm),
          'maximum_numerical_uncertainty':{k:max(m['windows'][-1]['uncertainty'][k] for m in mm) for k in ['concentration','flux','flow']},
          'minimum_sampled_fast_relaxation_rate':min(m['solver']['candidate']['minimum_fast_relaxation_rate'] for m in mm),
          'maximum_sampled_fast_relaxation_time':1/min(m['solver']['candidate']['minimum_fast_relaxation_rate'] for m in mm),
          'source_original_directed_reactions':len(u['reaction_ids']),'source_active_directed_reactions':len(u['active_reaction_ids']),
          'zero_reaction_ids':u['zero_reaction_ids'],'covered_reaction_ids':u['reaction_ids'],
          'algebraic_enzyme_values':len(u['enzyme_states']),'approximate_independent_occupancy_states_eliminated_in_trials':len(u['enzyme_states'])-1,
          'full_reference_graph_check':embedding['units'][name]}
        summary['units'][name]=evidence
        rows.append(f"| {name} | {nets[name]} | Source steady-enzyme law; implicit form-specific total inversion | {len(mm)} completed comparisons; long gates pass; domain qualification blocked | Zero-product corner"+('; uncertified low-fuel root' if name=='MK' else '')+" |");
    write_json(OUT/'scientific_summary.json',summary)
    report=['# Energy-cycle scientific research report v1','',
      '**Outcome:** all four active networks admit one net stoichiometric direction, but none is approved as a generally validated reduced module. Source-derived stationary kinetics are accurate in the completed tested domains; full all-enzyme elimination has explicit physical-domain limitations. Every recommendation is **HUMAN_REVIEW_REQUIRED**.','',
      '| Cycle | Net stoichiometry | Kinetic closure | Validation status | Failure conditions |','|---|---|---|---|---|',*rows,'',
      '## Frozen scope and execution','',
      f"Source commit `{d['source_commit']}`; main/topology ancestry and all2013 existing tracked-input hashes are in `protected_inputs_before.json`. The unchanged canonical XML SHA-256 is `{d['source_hashes']['models/pnas2017_full_reference/original/fMGG_synthesis.xml']}`. The operational author ZIP has27 positive initial species and483 nonzero channels; structural all-one inputs were not used. The compatibility matrix preserves `re0000000414 → 2 PO4` exactly. The original/normalized/raw sources, classifications and historical decisions remain protected.", '',
      f"The immutable preregistration SHA-256 is `{sha(DOC/'validation_preregistration.json')}`. It contains54 explicit scenarios,362 observation times including0, author numerical interval0–1000, both original nonequilibrium and physically projected initial modes, positive fixed scales and all gates. Completed comparisons: **{len(ms)}**; status counts: `{summary['scenario_gate_statuses']}`. Five scenario initial-domain stops remain: four analytically impossible zero-product corners and one uncertified MK low-fuel root. Seven initial NDK internal-trial solver failures are preserved separately; any coordinate-corrected reruns are additive engineering evidence, with unchanged equations/scenarios/gates/scales/tolerances.", '',
      'Microscopic comparisons use Radau1e-8/1e-10, tightened Radau1e-10/1e-12 and independent BDF1e-10/1e-12. Reduced integrations use the source stationary laws and an implicit physical total-resource inversion. Stationary root residual, positivity and local invertibility are guarded; constrained fast attraction is checked at the initial and observation-grid roots. Multistart agreement supports the selected local branch and proves no global uniqueness theorem. No trajectory is clipped and no parameter is fitted.', '',
      'The generic v1 NDK solver failures occur inside Radau nonlinear collocation trial evaluations, before any accepted negative trajectory. They are engineering stops, not measured reduction-error failures. The additive depletion-coordinate repair is an exact coordinate change when present; its native failures remain accessible.', '',
      'The first additive NDK runner saved one comparison before a diagnostic print used an incorrect field name. That reporting failure and completed duplicate are preserved; the corrected, separately frozen runner completed all14 modes. The final98 original-study pairs count each case/mode once, and do not erase or double-count the saved duplicate.', '',
      'A separate frozen supplemental PPiase reverse-driving probe used PPi=1, PO4=10000 and the authored enzyme total0.16. It leaves all54 original scenarios and their gates unchanged and is excluded from their qualification totals. Both original/projected initial modes completed with the same source-derived candidate and scientific gate formulas. Its negative net catalytic extent demonstrates PPi synthesis permitted by the active source reverse cycle; this is additional chemistry evidence, not approval or retuning of the original product-rich case.', '',
      '## Measured accuracy and initial layer','',
      '| Cycle | Completed pairs | Max long free/pool error | Net-flux normalized RMS | Max cumulative conversion-flow error | Max initial-layer free error |','|---|---:|---:|---:|---:|---:|']
    for n,e in summary['units'].items():
        L=e['long_maxima'];report.append(f"| {n} | {e['comparison_pairs']} | {100*max(L['max_scaled_free'],L['max_scaled_retained']):.6g}% | {100*L['normalized_net_flux_rms']:.6g}% | {100*L['max_normalized_cumulative_resource_flow']:.6g}% | {100*e['initial_layer_maxima']['max_scaled_free']:.6g}% |")
    report += ['',
      'The gates are≤5% long free/retained-pool error,≤10% net-flux RMS and≤2% cumulative conversion-flow error. The initial layer0–0.05 and transition0.05–1 are reported separately and are not removed from the files. CK and MK show meaningful original-initial-state fast-layer discrepancies despite small long errors. The authored isolated baseline is catalytically dormant because ADP/AMP/GDP/PPi are initially absent; its near-exact long tracking cannot establish catalytic validity. Positive challenge and depletion/product-rich conditions provide the nontrivial evidence. The flux floor is1% of enzyme catalytic capacity; a small normalized RMS in a nearly dormant regime has this stated interpretation.', '',
      'Free forms, bound forms and occupancy remain separate in every savedNPZ. Total-resource balances are `T_i=free_i+bound_i`; cumulative chemical conversion is integrated from0 as forward minus reverse catalytic extent. The exact microscopic identity is `Δfree_i+Δbound_i=N_i*extent_net`, so transient free release need not equal catalytic current. Inventory storage is retained in reconstruction, not treated as hydrolysis. Both PPiase sequential release events are in the source flux arrays; their cumulative net releases can be recovered from the double/single-PO4 occupancy balances. No ADP/AMP or ATP/GTP pools are merged.', '',
      '## Four-cycle reference and full-network embedding boundary','',
      'The source microscopic87-channel four-cycle assembly was executed under AUTHOR_BASELINE and SHARED_LIMITATION with common pools and catalyst totals counted once. Both imported stoichiometric matrices equal the exact source, including all zero channels. Shared-limitation endpoint net conversion extents are CK39.3362442679, NDK9.99999999981, MK9.99938691322 and PPiase9.99901271288. These are source reference measurements, not reduced-coupled accuracy evidence.', '',
      f"The full imported241-species/968-reaction source author reference also completed inCVODE with base/tight tolerances. FreePept0003@1000={full['runs']['tight']['Pept0003_endpoint']:.15g}; base/tight endpoint difference={full['convergence']['Pept0003_endpoint_absolute_difference']:.6g}. The initial full-reference import API error is preserved and the successful retry has a separate directory. This source run does not validate a reduced embedding.", '',
      'An actual full-reference boundary-history feasibility audit found13 sampled MK roots and36 PPiase roots with a negative free form beyond the1e-8 allowance. MK first fails at0.00105737 and recovers sampled feasibility at0.00785405; PPiase first fails at0.0000414423 and recovers at0.01069235. This establishes an executable startup obstacle for replacing all four modules with this stationary-total candidate. It is a failure to certify the selected physical graph, not a proof that every alternative closure fails. CK/NDK pass all362 sampled source-path graph checks within the declared allowance; that alone proves no full coupled accuracy. All-four candidate coupling and full replacement are **BLOCKED**, and no full-model candidate trajectory or Pept endpoint comparison is claimed.', '',
      '## Per-cycle scientific answers','']
    for u in d['units']:
        n=u['name'];e=summary['units'][n];mrows=[m for m in ms if m['id'].startswith(n+'__')]
        report += ['### '+n,'',
          '1. **Covered IDs:** '+', '.join('`'+rid+'`' for rid in u['reaction_ids'])+'.',
          '2. **Zero-author channels:** '+', '.join('`'+rid+'`' for rid in u['zero_reaction_ids'])+'. They remain traceable; reference zero is condition-specific.',
          '3. **Complete cycle:** '+('Both substrate-binding orders, chemical conversion, both product-release orders and enzyme regeneration, with exact source reverse binding/chemical channels.' if n!='PPiase' else 'PPi binding, bound PPi↔double-PO4 chemical conversion, first PO4 release, second PO4 release and enzyme regeneration; active reverse bindings traverse the same cycle.'),
          '4. **Net chemistry:** '+e['net_stoichiometry']+'. '+('NDK chemical reverse `re0000000364` is0; product binding still affects occupancy.' if n=='NDK' else 'Reverse direction is supported under the declared source active-channel condition.'),
          '5. **Elimination limits:** equal retained coordinates can have different source projected derivatives, so exact kinetic lumpability fails. Total stationary closure has an analytically impossible positive-substrate/zero-product corner; bound conversion products need time to accumulate.',
          '6. **Law:** `Q(u)h=0`, `sum(h)=E_total`, `T=u+C*h`, with gross/net catalytic source currents evaluated at reconstructed states. Explicit rational formulas and all microscopic constants are in effective_kinetics.md; no empirical fit.',
          '7. **Pools:** complete live enzyme and the independently proved represented resource groups in stoichiometric_certificate.md have zero symbolic active residual. Their isolated scopes are explicit; disabled degradation can invalidate live totals'+(' and source degradation400/401 lose bound AMP/ADP.' if n=='MK' else '.'),
          f"8. **Timescales:** the slowest sampled constrained-fast relaxation rate over completed trials is{e['minimum_sampled_fast_relaxation_rate']:.6g}, giving a maximum local relaxation time{e['maximum_sampled_fast_relaxation_time']:.6g} in the author numerical time convention. This is measured local spectrum evidence, not a uniform singular-perturbation proof. Three-window accuracy and nonequilibrium/projected starts are the practical checks.",
          f"9. **Accuracy:** over{e['comparison_pairs']} completed pairs, long concentration/pool error≤{100*max(e['long_maxima']['max_scaled_free'],e['long_maxima']['max_scaled_retained']):.6g}%, flux RMS≤{100*e['long_maxima']['normalized_net_flux_rms']:.6g}%, cumulative conversion-flow error≤{100*e['long_maxima']['max_normalized_cumulative_resource_flow']:.6g}%. Every numerical uncertainty and bound/occupancy error is retained per run. Max normalized conservation residual={e['maximum_normalized_conservation_residual']:.6g}.",
          '10. **Failures:** the zero-product corner is an analytic no-root case.'+(' Low-fuel initial inversion returns negativefreeATP: no physical root is certified, without proving global nonexistence. Actual full-source startup also contains uncertified roots.' if n=='MK' else ' Actual full-source startup contains uncertified stationary-total roots.' if n=='PPiase' else ' Seven native depletion solver trials were blocked; exact-coordinate reruns are separately qualified.' if n=='NDK' else ' Original nonequilibrium fast-layer free-resource errors are substantial; no uniform all-initial-state approximation is established.'),
          f"11. **Actual trial reduction:** {len(u['enzyme_states'])} live enzyme values are algebraic; one enzyme-total coordinate was exactly constant, so{len(u['enzyme_states'])-1} independent occupancy degrees were approximately eliminated. Source-active{len(u['active_reaction_ids'])} directed channels are represented by{'1' if n=='NDK' else '2'} gross effective directions (one net axis), with all original channels reconstructable at stationarity. No approved or promoted model has eliminated any source state/reaction. The isolated implementation uses one physical conversion coordinate plus cumulative flow quadratures; totals and conserved constants still carry resource information.",
          '12. **Translation coupling:** stationary law may be a useful bounded-domain candidate, but current evidence does not qualify a full translation embedding. Retain/reintroduce physical dynamic occupancy or product-storage states for a separately derived, frozen study. Recommendation: **REVISE_WITH_EXTRA_STATE**, **HUMAN_REVIEW_REQUIRED**.','']
    report += ['## Independent checks, limits and reproducibility','',
      'All12 semantic adversarial controls are rejected by the expected source, structural, mathematical or numerical policy predicate; hash rejection is not used as a substitute. Fixtures include an exact lumpable network, a nonlumpable counterexample and an analytically solved enzyme initial-layer trajectory. Independent canonical parsing, reverse-direction LPs, full resource moieties and source-law kinetic checks agree. Original and additive numerical verification files recompute every completed stored trajectory independently; see independent_test_report.md and results manifests. A testPASS is an evidence-integrity result, not scientific acceptance.', '',
      'No elemental/ionic conservation or quantitative osmotic pressure is claimed. No unrepresentedH2O/H+/Mg2+ is added. The represented PPi↔2PO4 particle proxy changes by+1 for forward net conversion, but physicochemical osmotic/ionic properties are unavailable. Absolute physical concentration/rate dimensions remain unresolved; association parameters have the expected formal inverse concentration/time role and unimolecular parameters inverse time, without repairing author metadata.', '',
      'External methodological context: [Ciliberto et al.2007 totalQSSA networks](https://pmc.ncbi.nlm.nih.gov/articles/PMC1828705/) motivates explicit enzyme-bound inventories; [Eilertsen and Schnell2020](https://pmc.ncbi.nlm.nih.gov/articles/PMC7337988/) distinguishes time scales and approximation domains. These papers do not establish validity of thisPNAS candidate. All acceptance gates are the registered v1 engineering targets.', '',
      'Reproduction on a fresh exact-source checkout with these new scripts: python scripts/energy_cycles/bootstrap_audit.py; python scripts/energy_cycles/inventory.py; python scripts/energy_cycles/kinetics_analysis.py; python scripts/energy_cycles/preregister.py; then python scripts/energy_cycles/runtime.py --unit CK (and NDK/MK/PPiase). The registered sourceengine diagnostics use the existing RoadRunner environment. Every numerical manifest gives executable/environment/parameters/initials/tolerances/command and output hashes. Additive NDK repair commands are frozen in its engineering addendum. Existing evidence directories refuse overwrite. Do not reproduce into frozen historical paths.', '',
      'Final scientific decision remains with the researcher. No existing decision row is altered, no candidate becomesPURE_reduced_core, and no commit/push/merge is performed.']
    if supplemental:
        original_reverse=next(m for m in supplemental if m['initial_mode']=='ORIGINAL_NONEQUILIBRIUM')
        report.insert(-1,f"Supplemental PPiase source net extent@1000={original_reverse['endpoint_net_extents']['microscopic']:.12g}; candidate={original_reverse['endpoint_net_extents']['reduced']:.12g}. Its complete source/initial/code hashes and pre-outcome supplemental registration are retained in `ppiase_reverse_probe_preregistration.json` and `supplemental_ppiase_reverse/`.")
    prose='\n'.join(report)+'\n'
    for old,new in {'all2013':'all 2013','has27':'has 27','and483':'and 483','Radau1e':'Radau 1e','BDF1e':'BDF 1e','all54':'all 54','all14':'all 14','final98':'final 98','total0.16':'total 0.16','are≤':'are ≤','error,≤':'error, ≤','RMS and≤':'RMS and ≤','layer0':'layer 0','transition0':'transition 0','from0':'from 0','is1%':'is 1%','the1e-8':'the 1e-8','with362':'with 362','contains54':'contains 54','scenarios,362':'scenarios, 362','time0':'time 0','times including0':'times including 0','interval0':'interval 0','sources remain':'sources remain','inCVODE':'in CVODE','FreePept0003':'Free Pept0003','source241':'source 241','imported241':'imported 241','network87':'network 87','microscopic87':'microscopic 87','are CK39':'are CK 39','NDK9.':'NDK 9.','MK9.':'MK 9.','PPiase9.':'PPiase 9.','found13':'found 13','and36':'and 36','at0.':'at 0.','gatePASS':'gate PASS','testPASS':'test PASS','All12':'All 12','all362':'all 362','per run':'per run','completeNPZ':'complete NPZ','savedNPZ':'saved NPZ','bound AMP/ADP':'bound AMP/ADP','rate≤':'rate ≤','enzyme values':'enzyme values','so6':'so 6','so3':'so 3','Source-active18':'Source-active 18','Source-active17':'Source-active 17','Source-active8':'Source-active 8','reduced core':'reduced core','model/scenarios':'model/scenarios','sourceengine':'source engine','No ADP':'No ADP','No unrepresentedH2O':'No unrepresented H2O','thisPNAS':'this PNAS','becomesPURE':'becomes PURE','2007 totalQSSA':'2007 total QSSA','Schnell2020':'Schnell 2020','Eilertsen and Schnell':'Eilertsen and Schnell','1e-8 allowance':'1e-8 allowance','freeATP':'free ATP','independent occupancy':'independent occupancy','author numerical':'author numerical'}.items():prose=prose.replace(old,new)
    (DOC/'validation_report.md').write_text(prose,encoding='utf-8')
    human=['# Energy-cycle human scientific review v1','',
      '**HUMAN_REVIEW_REQUIRED**. All existing scientific decisions and PURE_reduced_core are unchanged. No checkboxes are selected.','',
      '| Cycle | Research recommendation | Evidence requiring a new candidate |','|---|---|---|']
    for n in summary['units']:
        why='Positive substrate/zero product has no stationary physical total closure; retain dynamic storage.'
        if n=='MK':why+=' Low-fuel inversion and full author startup also lack a certified root.'
        if n=='PPiase':why+=' Preserve source reversibility and both PO4 releases; full author startup graph fails.'
        if n=='NDK':why+=' Preserve zero catalytic reverse and document additive depletion solver correction.'
        human.append(f'| {n} | REVISE_WITH_EXTRA_STATE | {why} |')
    human += ['',
      'The source/structure certificates are exact within their declared active-channel scopes. Long numerical gates pass for completed feasible cases, but that does not qualify the required domain or the actual all-four translation startup. A revised physical-state candidate would require a new derivation and preregistration; no such successor is executed or approved here. A domain-restricted use of the present laws also needs a human decision about its allowed initializations and observables.', '',
      'Review choices for each cycle:', '',
      '- [ ] Accept the tested domain as a candidate for further investigation.',
      '- [ ] Derive and preregister a successor retaining dynamic bound/product storage.',
      '- [ ] Keep the microscopic network.',
      '- [ ] Request additional mathematical/experimental evidence.', '',
      'Retain the distinction between analytically impossible zero-product corners, uncertified MKlow-fuel/full-startup inversions and NDKinternal-trial numerical stops. No failure is erased by a solver repair. Read validation_report.md and the exact inventories before choosing any scientific transformation.']
    (DOC/'human_review.md').write_text('\n'.join(human)+'\n',encoding='utf-8')
    graph={'schema':'evidence_navigation_v1','source_commit':d['source_commit'],'source_hashes':d['source_hashes'],'freshness':'Bound to current source bytes; verify hashes before reuse',
      'authority':'Derived navigation only; canonical source and explicit human scientific decisions remain authoritative','nodes':[],'edges':[]}
    for u in d['units']:
        name=u['name'];graph['nodes'].append({'id':name,'type':'reduction_unit','evidence_status':'INFERRED','validation':summary['units'][name]['validation_status'],'recommendation':'REVISE_WITH_EXTRA_STATE'})
        for rid in u['reaction_ids']:graph['edges'].append({'source':rid,'target':name,'relation':'source_subsystem_member','evidence_status':'EXTRACTED','authority':u['source_file']})
        for e in u['enzyme_states']:
            graph['edges'].append({'source':e,'target':name,'relation':'enzyme_state','evidence_status':'INFERRED','basis':'Exact source binding stoichiometry and conserved-enzyme residual'})
        graph['nodes'].append({'id':name+'_zero_product_corner','type':'mathematical_domain_failure','evidence_status':'INFERRED','proof':'kinetic_analysis.json and independent_tests.json'})
        graph['edges'].append({'source':name+'_zero_product_corner','target':name,'relation':'blocks_general_all_state_elimination','evidence_status':'INFERRED'})
        graph['nodes'].append({'id':name+'_human_decision','type':'scientific_decision','evidence_status':'AMBIGUOUS','status':'HUMAN_REVIEW_REQUIRED'})
        graph['edges'].append({'source':name+'_human_decision','target':name,'relation':'approval_pending','evidence_status':'AMBIGUOUS'})
    reaction_ids={r for u in d['units'] for r in u['reaction_ids']}
    for r in d['reactions']:
        if r['id'] in reaction_ids:
            graph['nodes'].append({'id':r['id'],'type':'original_directed_reaction','evidence_status':'EXTRACTED','source_authority':'Canonical SBML plus author operational CSV','parameter':r['k'],'provenance':r['provenance'],'family':r['family']})
    for e in sorted({e for u in d['units'] for e in u['enzyme_states']}):
        graph['nodes'].append({'id':e,'type':'original_species_id','evidence_status':'EXTRACTED','source_authority':'Canonical SBML'})
    write_json(OUT/'knowledge_graph.json',graph)
    from plot_report import plots
    plots(d,ms,summary)
    print(json.dumps({'completed_pairs':len(ms),'registered_scenarios':len(reg['scenarios']),'promotion':False}))

if __name__=='__main__':main()

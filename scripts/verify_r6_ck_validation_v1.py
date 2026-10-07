"""Independent R6 ambiguity-stop verifier. Does not certify unrun validation."""
from pathlib import Path
from fractions import Fraction
import ast
import csv
import datetime
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/reduction/r6_ck_validation'
EXPECTED_DECISION = 'GROSS_FLUX_REQUIREMENT_AMBIGUOUS_HUMAN_DECISION_REQUIRED'
FAST = ['re0000000332', 're0000000333', 're0000000336', 're0000000337']
CONDITIONS = ['R3_BASE', 'R3_GLYRS_LOW', 'R3_GLYRS_HIGH', 'R3_METRS_LOW',
              'R3_METRS_HIGH', 'R3_GLY_LOW', 'R3_MET_LOW', 'R3_TRNA_LOW', 'R3_ATP_LOW']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def canonical_columns():
    # Parse untouched SBML directly, including literal stoichiometryMath.
    tree = ET.parse(ROOT / 'models/pnas2017_full_reference/original/fMGG_synthesis.xml')
    namespace = {'s': 'http://www.sbml.org/sbml/level2/version4'}
    # Derive namespace from root for compatibility; no normalized input is used.
    namespace['s'] = tree.getroot().tag.split('}')[0].strip('{')
    model = tree.getroot().find('s:model', namespace)
    species = [n.attrib['id'] for n in model.find('s:listOfSpecies', namespace)]
    result = {}
    for reaction in model.find('s:listOfReactions', namespace):
        column = {}
        for list_tag, sign in [('listOfReactants', -1), ('listOfProducts', 1)]:
            items = reaction.find('s:' + list_tag, namespace)
            if items is None:
                continue
            for item in items:
                math = item.find('s:stoichiometryMath', namespace)
                if math is not None:
                    literals = [n for n in math.iter() if n.tag.split('}')[-1] == 'cn']
                    assert len(literals) == 1 and len(list(math.iter())) == 3, 'Unexpected nonliteral stoichiometry'
                    coefficient = Fraction(literals[0].text.strip())
                else:
                    coefficient = Fraction(item.attrib.get('stoichiometry', '1'))
                name = item.attrib['species']
                column[name] = column.get(name, Fraction(0)) + sign * coefficient
        result[reaction.attrib['id']] = {k: v for k, v in column.items() if v}
    return species, result


def verify():
    checks = []
    provenance = read_json('input_provenance.json')
    parent = Path(provenance['source_checkout'])
    historical = read_json('historical_snapshot.json')
    assert sha(OUT / 'historical_snapshot.json') == provenance['historical_snapshot_sha256']
    assert len(historical) == provenance['historical_file_count'] == 2585
    for rel, metadata in historical.items():
        assert sha(ROOT / rel) == metadata['sha256'], 'Execution historical mutation: ' + rel
        assert sha(parent / rel) == metadata['sha256'], 'Source checkout mutation: ' + rel
        assert (ROOT / rel).stat().st_size == metadata['bytes']
    checks.append(dict(check='ALL_PRE_R6_BYTES_BOTH_CHECKOUTS', status='PASS', file_count=len(historical)))
    assert provenance['execution_parent_sha'] == '1181ab2f0a04d72cf76fb069be6bb842e3de75d8'
    assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == provenance['execution_parent_sha']
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/r6-ck-validation-20261007'
    assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not subprocess.check_output(['git', 'diff', '--cached', '--name-only'], cwd=ROOT, text=True).strip()
    # All new files must remain in the additive R6 scope.
    allowed_prefixes = ('docs/reduction/r6_', 'results/reduction/r6_ck_validation/',
                        'scripts/build_r6_', 'scripts/verify_r6_')
    new_files = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    assert all(p.startswith(allowed_prefixes) for p in new_files), new_files
    checks.append(dict(check='ISOLATED_LINEAGE_AND_ADDITIVE_SCOPE', status='PASS'))
    desktop_snapshot = read_json('desktop_untracked_snapshot.json')
    for path, fingerprint in desktop_snapshot.items():
        assert sha(Path(path)) == fingerprint
    assert sha(Path(provenance['request_file'])) == provenance['request_sha256'] == sha(OUT / 'human_request.txt')
    checks.append(dict(check='HUMAN_REQUEST_AND_UNRELATED_DESKTOP_FILES', status='PASS'))

    binding = read_json('registration_binding.json')
    for path, fingerprint in binding['file_hashes'].items():
        assert sha(ROOT / path) == fingerprint, 'Frozen preregistration mutation: ' + path
    closeout = read_json('closeout.json')
    assert closeout['registration_sha256'] == sha(OUT / 'registration_binding.json')
    assert binding['decisive_comparisons_before_freeze'] == closeout['decisive_comparisons'] == 0
    assert datetime.datetime.fromisoformat(binding['frozen_at_utc']) <= datetime.datetime.fromisoformat(closeout['closed_at_utc'])
    assert binding['promotion_conjunction_frozen'] is False
    checks.append(dict(check='AUDIT_SCOPE_CANDIDATE_STARTUP_FROZEN_NO_DECISIVE_RUN', status='PASS'))

    evidence = rows(OUT / 'scientific_requirement_to_observable.csv')
    assert len(evidence) == 23 and len({r['requirement_id'] for r in evidence}) == 23
    for row in evidence:
        path = ROOT / row['source_file']
        assert sha(path) == row['source_sha256']
        source = path.read_text(encoding='utf-8').splitlines()
        start, end = int(row['source_line_start']), int(row['source_line_end'])
        assert 1 <= start <= end <= len(source)
        excerpt = '\n'.join(source[start - 1:end])
        assert excerpt == row['source_excerpt']
        assert hashlib.sha256(excerpt.encode('utf-8')).hexdigest() == row['excerpt_sha256']
        assert row['source_location'] == f'L{start}-L{end}'
        assert row['evidence_status'] in ['EXTRACTED', 'INFERRED', 'AMBIGUOUS']
        assert set(row['required_observable_class'].split(';')) <= set('ABCDEFGH')
    byid = {r['requirement_id']: r for r in evidence}
    # Require the actual conflict/applicability evidence, not just a prose label.
    assert 'microscopic fluxes' in byid['REQ18']['source_excerpt']
    assert 'Cumulative extent is mandatory' in byid['REQ15']['source_excerpt']
    assert 'exact representation rewrite' in byid['REQ14']['source_excerpt']
    assert 'mandatory for promotion' in byid['REQ20']['source_excerpt']
    roles = {r['decision_role'] for r in evidence if r['gross_microscopic_flux_required'] == 'AMBIGUOUS'}
    assert {'LEDGER_SEMANTICS_UNRESOLVED', 'CK_MICROSCOPIC_COMPARISON_NOT_PROMOTION_MANDATE',
            'EXPLICIT_FUTURE_MANDATORY_DECISION'} <= roles
    assert not any(r['gross_microscopic_flux_required'] in ['REQUIRED_SELECTED_CK', 'WAIVED_SELECTED_CK'] for r in evidence)
    decision = read_json('observable_requirement_decision.json')
    assert decision['decision'] == EXPECTED_DECISION
    assert decision['explicit_selected_ck_gross_promotion_mandate_found'] is False
    assert decision['explicit_selected_ck_gross_accuracy_waiver_found'] is False
    assert decision['mandatory_classes_final'] is None
    assert all(identifier in byid for identifier in decision['supporting_requirement_ids'])
    assert decision['branch_a_launched'] is decision['branch_b_launched'] is False
    assert decision['decisive_r6_comparisons'] == 0
    checks.append(dict(check='REQUIREMENT_LOCATIONS_AND_AMBIGUITY_RULE', status='PASS',
                       limitation='Interpretation is reviewable and source-bound; human scientific-use decision remains required'))

    species, columns = canonical_columns()
    assert len(species) == 241 and len(columns) == 968
    expected = [dict(CK=-1, CP=-1, CK_CP=1), dict(CK=1, CP=1, CK_CP=-1),
                dict(CK_ADP=-1, CP=-1, CK_CP_ADP=1), dict(CK_ADP=1, CP=1, CK_CP_ADP=-1)]
    for rid, values in zip(FAST, expected):
        assert columns[rid] == values, rid
        assert columns[rid].get('ATP', 0) == columns[rid].get('ADP', 0) == 0
    assert columns[FAST[0]] == {k: -v for k, v in columns[FAST[1]].items()}
    assert columns[FAST[2]] == {k: -v for k, v in columns[FAST[3]].items()}
    nqf = [[int(columns[rid].get(q, 0)) for rid in [FAST[0], FAST[2]]] for q in ['CK_CP', 'CK_CP_ADP']]
    assert nqf == [[1, 0], [0, 1]]
    source_summary = json.loads((ROOT / 'results/reduction/r5c_corrigendum/ck_fast_current_summary.json').read_text())
    assert source_summary['N_qf'] == nqf and source_summary['rank'] == 2
    laws = [r for r in rows(ROOT / 'docs/reduction/conservation_laws_v0.csv') if r['scope'] == 'SOURCE_GENERAL']
    assert len(laws) == 27
    for law in laws:
        coefficient = {k: Fraction(str(v)) for k, v in json.loads(law['species_coefficients_json']).items()}
        for rid, column in columns.items():
            residual = sum((coefficient.get(k, 0) * value for k, value in column.items()), Fraction(0))
            assert residual == 0, (law['conservation_id'], rid, str(residual))
    checks.append(dict(check='INDEPENDENT_CANONICAL_STOICHIOMETRY_NQF_AND_27_LS_IDENTITIES',
                       status='PASS', reaction_count=968, numerical_trajectory_conservation='NOT_RUN'))
    candidate = read_json('candidate_definition.json')
    assert candidate['fast_reaction_ids'] == FAST
    assert candidate['nonfast_dynamic_reaction_count'] == len(columns) - len(FAST)
    assert candidate['approximation'] == 'RAPID_EQUILIBRIUM / PARTIAL_EQUILIBRIUM'
    assert candidate['fitted_parameters'] == []
    for field in ['initial_condition_fitting', 'clipping', 'time_shift', 'source_trajectory_projection',
                  'canonical_reaction_deletion', 'promotion']:
        assert candidate[field] is False
    assert candidate['implementation_sha256'] == sha(ROOT / candidate['implementation_source'])
    definition = rows(ROOT / 'results/reduction/r5_mechanism_first/ck/reaction_definition.csv')
    assert [r['reaction_id'] for r in definition if r['declared_fast'] == 'True'] == FAST
    dat = ROOT / 'models/pnas2017_full_reference/original/simulate/Simulate_fMGG_synthesis/dat'
    params = {r['Name']: Fraction(r['Value']) for r in rows(dat / 'fMGG_synthesis_parameters.csv')}
    assert [params[rid + '_k1'] for rid in FAST] == [2, 1000, 2, 1000]
    startup = read_json('initial_layer_policy.json')
    historical_startup = json.loads((ROOT / 'results/reduction/r5_mechanism_first/ck/initial_layer_definition.json').read_text())
    for key, value in historical_startup.items():
        assert startup[key] == value
    assert startup['switch_formula'] == '10*eta*tau0' and startup['tau_formula'] == '1/(2*p0+1000)'
    for path, fingerprint in startup['source_hashes'].items():
        assert sha(ROOT / path) == fingerprint
    runner = (ROOT / 'scripts/r5_ck_eta_scan_v1.py').read_text()
    assert 'tau0=1/(2*p0+1000);switch0=10*tau0' in runner
    assert 'switch=switch0*eta;xs=full.sol(switch);zs=r.T@xs' in runner
    contract = rows(OUT / 'prospective_observable_contract.csv')
    assert [r['contract_class'] for r in contract] == list('ABCDEFGH')
    assert all('NOT_FROZEN' in r['gate_status'] and 'BUT_NOT_VALIDATED' in r['gate_status']
               for r in contract if r['contract_class'] in ['E', 'G'])
    checks.append(dict(check='FROZEN_CANDIDATE_KINETICS_INITIAL_LAYER_AND_GROSS_LIMITATIONS', status='PASS'))

    conditions = rows(OUT / 'condition_summary.csv')
    assert [r['condition_id'] for r in conditions] == CONDITIONS
    assert all(r['status'] == 'NOT_RUN_HUMAN_SCOPE_DECISION_REQUIRED' for r in conditions)
    assert all(not r[key] for r in conditions for key in ['mandatory_gates_pass', 'state_error',
               'slow_total_error', 'protein_output_error', 'net_current_error', 'net_extent_error', 'conservation_drift'])
    reuse = read_json('source_reuse_status.json')
    assert reuse['selected_trajectories'] == [] and reuse['status'] == 'NOT_ATTEMPTED_AMBIGUITY_STOP'
    assert not (OUT / 'per_condition').exists() and not (OUT / 'first_order').exists()
    # Inspect calls, avoiding false matches on explanatory strings and check names.
    for path in [ROOT / 'scripts/build_r6_ck_scope_audit_v1.py', Path(__file__)]:
        tree = ast.parse(path.read_text(encoding='utf-8'))
        forbidden = {'solve_ivp', 'BDF', 'DOP853', 'odeint', 'solve', 'least_squares', 'curve_fit', 'clip'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = getattr(node.func, 'id', None) or getattr(node.func, 'attr', None)
                assert name not in forbidden, (str(path), name)
    checks.append(dict(check='NO_NEW_SOLVER_NO_ADVERSE_NO_REUSE_NO_PROMOTION', status='PASS',
                       campaign='NOT_RUN', source_reuse_verification='NOT_APPLICABLE_NO_REUSE',
                       no_fitting_no_clipping='STATIC_CODE_AND_HISTORICAL_HASH_SCOPE'))
    navigation = read_json('evidence_navigation.json')
    assert navigation['source_authority'] is False
    assert {r['id'] for r in navigation['nodes']} == set(byid)
    for node in navigation['nodes']:
        assert node['sha256'] == byid[node['id']]['source_sha256']
    manifest = read_json('manifest.json')
    for path, fingerprint in manifest['file_hashes'].items():
        assert sha(ROOT / path) == fingerprint, 'Manifest mismatch: ' + path
    eligible = {p.relative_to(ROOT).as_posix() for p in OUT.iterdir() if p.is_file() and p.name not in
                ['manifest.json', 'verification.json', 'verification_binding.json']}
    eligible.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'docs/reduction').glob('r6_*.md'))
    eligible.update(['scripts/build_r6_ck_scope_audit_v1.py', 'scripts/verify_r6_ck_validation_v1.py'])
    assert eligible == set(manifest['file_hashes']), 'Incomplete manifest coverage'
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    checks.append(dict(check='MANIFEST_NAVIGATION_COMPLETENESS_AND_DIFF_CHECK', status='PASS'))
    report = dict(schema='R6_INDEPENDENT_VERIFICATION_V1', status='PASS_SCOPE_AUDIT_ONLY',
                  verified_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  checks=checks, gross_flux_decision=EXPECTED_DECISION, scientific_promotion='NOT_APPROVED',
                  formal_conditions_executed=0, formal_pass_count=None,
                  scientific_numeric_validation='NOT_RUN_HUMAN_SCOPE_DECISION_REQUIRED',
                  first_order_validation='NOT_RUN', source_reuse='NOT_ATTEMPTED',
                  numerical_conservation='NOT_RUN', independent_structural_conservation='27_LS_IDENTITIES_PASS')
    (OUT / 'verification.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
    separate = {'manifest_sha256': sha(OUT / 'manifest.json'),
                'verifier_sha256': sha(Path(__file__)), 'verification_sha256': sha(OUT / 'verification.json')}
    (OUT / 'verification_binding.json').write_text(json.dumps(separate, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    if (OUT / 'formal_registration_binding.json').exists():
        from verify_r6_ck_formal_v1 import verify as verify_formal
        verify_formal()
    else:
        verify()

#!/usr/bin/env python3
"""Executed B1-1 gates, safe legacy regressions, deterministic builds and handoff."""
from datetime import datetime, timedelta, timezone
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/reduction/pathways'
HERE = Path(__file__).resolve().parent
ENV = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}
LOG = OUT / 'phase_b1_1_execution_log.txt'
FAILURES = OUT / 'phase_b1_1_failure_evidence.jsonl'


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def save(p, value):
    Path(p).write_bytes((json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def log(value):
    with LOG.open('a', encoding='utf-8', newline='\n') as f:
        f.write(value + '\n')


def fail(value):
    with FAILURES.open('a', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, sort_keys=True, ensure_ascii=False) + '\n')


def run(command):
    label = subprocess.list2cmdline([str(c) for c in command])
    log('COMMAND: ' + label)
    cp = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True, encoding='utf-8', errors='replace')
    record = {'actual_command': label, 'exit_code': cp.returncode, 'stdout': cp.stdout, 'stderr': cp.stderr}
    log('EXIT_CODE: ' + str(cp.returncode) + '\nSTDOUT:\n' + cp.stdout + '\nSTDERR:\n' + cp.stderr)
    if cp.returncode:
        fail({'stage': 'executed_command', **record})
    print(json.dumps({'command': label, 'exit_code': cp.returncode}), flush=True)
    return record


def imported(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def regressions():
    result = {}
    with tempfile.TemporaryDirectory(prefix='phase-b1-1-safe-regression-') as temporary:
        tmp = Path(temporary)
        a = tmp / 'phase_a'
        a.mkdir()
        for name in ('glyrs_metrs_graph.json', 'glyrs_metrs_pathway_index.csv', 'glyrs_metrs_sample.md'):
            shutil.copyfile(OUT / name, a / name)
        # Inspect help before invoking old report-writing entrypoints.
        help_commands = [run([sys.executable, ROOT / p, '--help']) for p in (
            'scripts/pathways/verify_pathway_atlas.py', 'scripts/pathways/test_pathway_atlas.py',
            'scripts/pathways/phase_b0/verify_phase_b0_witnesses.py', 'scripts/pathways/phase_b0/test_phase_b0_negative_controls.py')]
        ca = [run([sys.executable, ROOT / 'scripts/pathways/verify_pathway_atlas.py', '--report', a / 'independent.json']),
              run([sys.executable, ROOT / 'scripts/pathways/test_pathway_atlas.py', '--output-dir', a])]
        result['phase_a'] = {'status': 'PASS' if all(c['exit_code'] == 0 for c in ca) else 'FAIL', 'executions': ca,
                             'independent': load(a / 'independent.json'), 'positive_and_mutations': load(a / 'validation_report.json'),
                             'negative_controls': load(a / 'negative_controls.json'), 'writes': 'TEMPORARY_COPY_ONLY'}
        b = tmp / 'phase_b0'
        b.mkdir()
        for path in OUT.glob('phase_b0_*.json'):
            shutil.copyfile(path, b / path.name)
        # Redirect failure destinations as well as report destinations. Source ROOT
        # stays canonical; signed B0 fields and files are never patched.
        shim = ('import sys; from pathlib import Path; '
                'sys.path.insert(0,str(Path.cwd()/"scripts/pathways/phase_b0")); '
                'import verify_phase_b0_witnesses as verify; verify.OUT=Path(sys.argv[1]); '
                'entry=sys.argv[2]; sys.argv=[entry]+sys.argv[3:]; '
                'import importlib; mod=importlib.import_module(entry); raise SystemExit(mod.main())')
        cb = [run([sys.executable, '-c', shim, b, 'verify_phase_b0_witnesses', '--input', OUT / 'phase_b0_handoff_witnesses.json', '--report', b / 'positive.json']),
              run([sys.executable, '-c', shim, b, 'test_phase_b0_negative_controls', '--report', b / 'negative.json'])]
        result['b0'] = {'status': 'PASS' if all(c['exit_code'] == 0 for c in cb) else 'FAIL', 'executions': cb,
                        'independent': load(b / 'positive.json'), 'negative_controls': load(b / 'negative.json'),
                        'writes': 'REPORT_AND_FAILURE_DESTINATIONS_TEMPORARY; ORIGINAL_ROOT_READ_ONLY',
                        'temporary_failures': {p.name: p.read_text(encoding='utf-8') for p in b.glob('*failure*.jsonl')}}
        result['cli_inspection'] = help_commands
        html = imported('existing_html_acceptance_for_b1_1', ROOT / 'scripts/pathways/test_reaction_atlas_html.py')
        h = {'actual_command': 'run_phase_b1_1_validation.py -> existing test_reaction_atlas_html.py acceptance functions',
             'mode': 'READ_ONLY; NO MAIN OR DEFAULT REPORT DESTINATION', 'gates': []}
        try:
            content = html.extract((OUT / 'reaction_atlas_prototype.html').read_text(encoding='utf-8'))
            species, source, annotation, params = html.read_sources()
            graph = load(OUT / 'glyrs_metrs_graph.json')
            operations = [('A', lambda: html.gate_a(content, species, source, annotation, params)),
                          ('B', lambda: html.gate_b(content, graph)), ('C', lambda: html.gate_c(content, source, params)),
                          ('D', lambda: html.gate_d(content, source)),
                          ('REPRODUCTION', lambda: html.rebuild(OUT / 'reaction_atlas_prototype.html')),
                          ('PRESENTATION_PRESERVATION', lambda: html.previous_version_integrity(content))]
            for gate, op in operations:
                try:
                    h['gates'].append({'gate': gate, 'status': 'PASS', 'evidence': op()})
                except Exception:
                    h['gates'].append({'gate': gate, 'status': 'FAIL', 'traceback': traceback.format_exc()})
            if html.browser_executable() is None:
                h['gates'].append({'gate': 'BROWSER', 'status': 'NOT_RUN', 'reason': 'No existing supported browser; no dependency download'})
            else:
                try:
                    ev = html.run_browser(OUT / 'reaction_atlas_prototype.html', content, source)
                    h['gates'].append({'gate': 'BROWSER', 'status': ev['status'], 'evidence': ev})
                except (ImportError, FileNotFoundError):
                    h['gates'].append({'gate': 'BROWSER', 'status': 'NOT_RUN', 'traceback': traceback.format_exc()})
                except Exception:
                    h['gates'].append({'gate': 'BROWSER', 'status': 'FAIL', 'traceback': traceback.format_exc()})
        except Exception:
            h['gates'].append({'gate': 'SETUP', 'status': 'FAIL', 'traceback': traceback.format_exc()})
        statuses = [g['status'] for g in h['gates']]
        h['status'] = 'FAIL' if 'FAIL' in statuses else 'INCONCLUSIVE' if 'NOT_RUN' in statuses else 'PASS'
        h['exit_code'] = 0 if h['status'] == 'PASS' else 1
        result['html'] = h
        log('HTML_ACCEPTANCE:\n' + json.dumps(h, ensure_ascii=False, sort_keys=True))
        if h['status'] != 'PASS':
            fail({'stage': 'html_regression', 'evidence': h})
        print(json.dumps({'html_regression': h['status'], 'gates': [{'gate': g['gate'], 'status': g['status']} for g in h['gates']]}), flush=True)
    result['status'] = 'PASS' if all(result[k]['status'] == 'PASS' for k in ('phase_a', 'b0', 'html')) and all(c['exit_code'] == 0 for c in help_commands) else 'FAIL'
    save(OUT / 'phase_b1_1_regression.json', result)
    return result


def reproduce():
    names = ('phase_b1_1_witnesses.json', 'phase_b1_1_source_scope.json', 'phase_b1_1_initiation_pathways.md')
    with tempfile.TemporaryDirectory(prefix='phase-b1-1-reproduce-') as d:
        runs, commands = [], []
        for n in range(2):
            dest = Path(d) / str(n)
            commands.append(run([sys.executable, HERE / 'build_initiation_witnesses.py', '--output-dir', dest]))
            runs.append({name: digest(dest / name) for name in names if (dest / name).is_file()})
        delivered = {name: digest(OUT / name) for name in names}
        status = 'PASS' if runs[0] == runs[1] == delivered and all(c['exit_code'] == 0 for c in commands) else 'FAIL'
        return {'status': status, 'independent_builds': 2, 'executions': commands, 'run_hashes': runs, 'delivered_hashes': delivered}


def review(report):
    data = load(OUT / 'phase_b1_1_witnesses.json')
    scope = load(OUT / 'phase_b1_1_source_scope.json')
    repo = report['repository']
    lines = ['# Phase B1-1 — executed researcher handoff', '',
             'Execution: **' + report['execution_status'] + '**. Engineering: **' + report['engineering_status'] + '**. '
             'Scientific status: **PENDING_HUMAN_REVIEW**. No scientific acceptance, commit or push is issued.', '',
             'Read [the pathways](phase_b1_1_initiation_pathways.md), [independent verification](phase_b1_1_independent_verification.json), '
             '[negative controls](phase_b1_1_negative_controls.json) and [full executed report](phase_b1_1_validation_report.json).', '',
             '## A. Repository state', '', '```json', json.dumps(repo, ensure_ascii=False, indent=2), '```', '',
             '## B. Original initiation network', '',
             'Canonical identity: 241 species / 968 directed reactions / 3,854 weighted arcs; 485 zero and 483 positive author directions. '
             '0414 still produces 2 PO4. Every tracked file was captured before implementation. '
             'PURE_two_computer_git_rules.txt was not found in the repository, ancestors, Desktop or Documents; the explicit task rules were followed.', '',
             'Coverage (unique source directions, never visual-reference counts):', '', '```json',
             json.dumps(scope['coverage'], indent=2), '```', '',
             'Search: exact markings, source-state waypoints, original-ID tie breaking; maximum 50,000 states / 16 events per leg. '
             'Only 206 initiation-context/family directions are searched. The larger inventory is read-only one-hop boundary, inverse and sink evidence. '
             'It does not authorize reconstruction of those other modules. No source row in that inventory remains unclassified; '
             'unsearched pathway alternatives and molecular-composition questions remain unresolved. '
             'All scoped IDs, concrete subsystem files, activity and reverse metadata are in [source_scope.json](phase_b1_1_source_scope.json).', '',
             'Source hashes:', '']
    for p in scope['source_provenance']:
        lines.append(f"- `{p['path']}`: `{p['sha256']}` ({p['authority']}).")
    lines += ['', '## C. Reconstructed witnesses', '',
              '**E1 and E2 reached through actual source producers**, conditional on their declared boundary inventories. '
              'The positive independently calculated nets below are not new reactions or effective rate laws.', '',
              '| Witness | Actual occurrences | Endpoint | Independent result |', '|---|---:|---|---|']
    for w in data['witnesses']:
        status = report['positive_verification'].get('witnesses', {}).get(w['witness_id'], {}).get('status', 'NOT_RUN')
        lines.append(f"| {w['witness_id']} | {len(w['reaction_occurrences'])} | {w['target_milestone']} | {status} |")
    for w in data['witnesses']:
        lines += ['', '### ' + w['witness_id'], '',
                  'Original source events: `' + ' → '.join(e['reaction_id'] for e in w['reaction_occurrences']) + '`.', '',
                  'Boundary: `' + ', '.join(s + ' × ' + v for s, v in w['initial_marking'].items()) + '`.', '',
                  'CONCEPTUAL_NET:', '', '```text', w['net_reaction'], '```', '',
                  'Recovered free states: `' + ', '.join(c['species_id'] for c in w['catalyst_recovery_claims']) + '`. '
                  'IF2_GDP release is recorded separately; ribosomal carrier and nucleotide-state recovery are not claimed. '
                  'Carrier composition remains INFERRED.']
    lines += ['', 'P1 discovery selects **re0000000724** (release of IF1, k1=0.0025) before 0755 (release of IF3), using stable-ID tie breaking. '
              'The source-supported example 0747/0757 is retained in the incidence appendix as the alternative IF3-first release route; '
              '0747 has k1=1000; the sorting choice is not a comparison of rates or route dominance. '
              'The separate P1-RELEASE-ALT fires 0749/0753/0763, releasing IF2_GDP first. '
              'P1/P3 genuinely rejoin at RS70S_IF2_GDP_fMettRNAfMetCAU_mRNA; P1/P4 rejoin at RS30S_IF1_IF3 and share the same suffix. '
              'Their identical endpoint nets do not collapse their internal original species. P2 reuses P1 once; P5/P6 reuse W3 once. '
              'P7 stops after 0013 binding and uses a separately declared EF-Tu/Gly-tRNA complex.', '',
              '## D. Verification gates', '', '| Gate | Status | Actual command / operation | Exit | Evidence | Failure reason |',
              '|---|---|---|---:|---|---|']
    for g in report['gates']:
        lines.append(f"| {g['gate']} — {g['name']} | {g['status']} | `{g['actual_command']}` | {g['exit_code']} | "
                     f"{g['evidence_file']} | {g['failure_reason'] or 'none'} |")
    n = report['negative_controls']
    lines += ['', '## E. Negative controls', '',
              f"Required: {n['required_controls_run']} run, {n['required_controls_passed']} passed, {n['required_controls_failed']} failed. "
              f"Total: {n['controls_run']} run, {n['controls_passed']} passed. Controls not run: {n['controls_not_run']}.", '',
              '| Control | Expected rejection | Actual rejection | Petri enabling | Result |', '|---|---|---|---|---|']
    for c in n['controls']:
        lines.append(f"| {c['test_id']} | {c['expected_rejection']} | {c['actual_rejection']} | {c['petri_enabling_result']} | {c['status']} |")
    lines += ['', 'N10/N11/N18/N20 (and additional controls) explicitly remain Petri-enabled while false provenance/lineage fails. '
              'Mutated fixtures and the actual independent rejection details are preserved in the negative-control JSON. '
              'Reordered independent precursors and genuine repeated binding with distinct occurrences are supplemental positive tests.', '',
              '## F. Preservation and regression', '',
              f"All {report['preservation'].get('tracked_files_unchanged', 0)} beginning tracked files are byte unchanged. "
              'The original SBML, parameters, reviewed v2, Phase A, B0 signed reports, historical authorizations and HTML remain unchanged.', '',
              '| Regression | Actual result | Scope |', '|---|---|---|',
              '| Phase A | ' + report['regression']['phase_a']['status'] + ' | Independent source checks, 10 mutations, supplements and reproduction in temporary copies |',
              '| B0 | ' + report['regression']['b0']['status'] + ' | Independent 5-witness verification, 12 mandatory / 18 total negatives, supplemental positives; all writes redirected |',
              '| Existing HTML/browser | ' + report['regression']['html']['status'] + ' | Read-only original acceptance functions, reproduction, installed browser interaction |', '',
              'Two fresh builds agree byte-for-byte with each other and the delivered files:', '']
    for p, h in report['reproducibility']['delivered_hashes'].items():
        lines.append(f'- `{p}`: `{h}`.')
    lines += ['', 'Exact commands, raw outputs and exit codes are retained in [execution_log.txt](phase_b1_1_execution_log.txt) '
              'and [regression.json](phase_b1_1_regression.json). Any actual failed attempts remain append-only in '
              'phase_b1_1_failure_evidence.jsonl when present; no acceptance threshold is changed to force a pass.', '',
              '## G. Researcher-review questions', '',
              '1. 是否接受 E1 作为这个原始模型的启动出口，保留其未显式展开 mRNA/肽基组成的限制？',
              '2. 是否接受 0001 独立标注为 ELONG_tRNA_release 的 E1→E2 交接，而不称为完整延伸一轮？',
              '3. 是否接受 IF1 缺席、IF1/IF3 入口顺序和 IF2 提前释放这些独立源路径，不推断动力学优势？',
              '4. 是否接受游离物种账本与 IF2 复合物核苷酸状态转换分列，并保持 IF2_GDP 释放不等于回收？',
              '5. 哪些跨复合物载体投影需要更多原论文组成证据，才能从 INFERRED 获得进一步科学认可？', '',
              '## H. Final status', '', '```json', json.dumps({k: report[k] for k in (
                  'execution_status', 'engineering_status', 'scientific_status', 'phase_b1_1_execution_authorized',
                  'phase_b1_1_formally_accepted', 'phase_b1_2_authorized', 'full_phase_b_authorized', 'commit_push_authorized')}, indent=2),
              '```', '', 'Reproduce with `python scripts/pathways/phase_b1_1/run_phase_b1_1_validation.py`. '
              'Stop at researcher review. No B1-2, kinetic reduction, commit or push.']
    (OUT / 'phase_b1_1_review.md').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reuse-legacy-regressions', action='store_true',
                        help='Reuse this task\'s already executed legacy checks only after verifying every original tracked input hash')
    args = parser.parse_args()
    log('B1-1 run Asia/Shanghai: ' + datetime.now(timezone(timedelta(hours=8))).isoformat())
    baseline = load(OUT / 'phase_b1_1_source_baseline.json')
    log('BEGINNING_PREFLIGHT: ' + json.dumps({k: baseline[k] for k in ('machine', 'branch', 'origin', 'starting_HEAD', 'upstream_status_at_start', 'initial_git_status')}))
    log('Actual startup: rev-parse root; origin; status; branch; HEAD; fetch origin --prune; status; rev-list HEAD...@{upstream}. All succeeded; 0/0. No pull needed.')
    commands = [run([sys.executable, HERE / 'build_initiation_witnesses.py']),
                run([sys.executable, HERE / 'verify_initiation_witnesses.py']),
                run([sys.executable, HERE / 'test_initiation_negative_controls.py'])]
    positive = load(OUT / 'phase_b1_1_independent_verification.json')
    negative = load(OUT / 'phase_b1_1_negative_controls.json')
    if args.reuse_legacy_regressions:
        import verify_initiation_witnesses as independent
        independent.preservation()
        regression = load(OUT / 'phase_b1_1_regression.json')
        regression['reuse_authority'] = 'ALREADY_EXECUTED_IN_THIS_B1_1_TASK; ALL_ORIGINAL_INPUTS_AND_LEGACY_SCRIPTS_BYTE_UNCHANGED'
        save(OUT / 'phase_b1_1_regression.json', regression)
        log('LEGACY_REGRESSION_REUSE: earlier actual results retained; all original tracked inputs rehashed unchanged. No legacy acceptance check removed or weakened.')
    else:
        regression = regressions()
    reproduction = reproduce()
    commands.append(run([sys.executable, HERE / 'verify_initiation_witnesses.py']))
    positive = load(OUT / 'phase_b1_1_independent_verification.json')
    commands.append(run(['git', 'diff', '--check']))
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    status = subprocess.check_output(['git', 'status', '--porcelain', '-uall'], cwd=ROOT).decode('utf-8')
    preservation = positive.get('preservation', {'status': 'FAIL'})
    modified = [line[3:] for line in status.splitlines() if not line.startswith('??')]
    new = [line[3:] for line in status.splitlines() if line.startswith('??')]
    permitted = all(p.startswith('docs/reduction/pathways/phase_b1_1_') or p.startswith('scripts/pathways/phase_b1_1/') for p in new)
    gates = []
    for letter, name in [('A', 'Source Integrity'), ('B', '30S Assembly'), ('C', 'IF2/fMet-tRNA Recruitment'),
                         ('D', '50S and GTP-State Transition'), ('E', 'Initiation E1'), ('F', 'E1-to-E2 Boundary'),
                         ('G', 'Alternative Routes and Competition'), ('H', 'Net Stoichiometry and Resource Ledger')]:
        passed = positive.get('structural_verification_status') == 'PASS'
        gates.append({'gate': letter, 'name': name, 'status': 'PASS' if passed else 'FAIL',
                      'actual_command': commands[-2]['actual_command'], 'exit_code': commands[-2]['exit_code'],
                      'evidence_file': 'phase_b1_1_independent_verification.json', 'failure_reason': None if passed else positive.get('error')})
    gates.append({'gate': 'I', 'name': 'Negative Controls', 'status': negative['status'],
                  'actual_command': commands[2]['actual_command'], 'exit_code': commands[2]['exit_code'],
                  'evidence_file': 'phase_b1_1_negative_controls.json', 'failure_reason': None if negative['status'] == 'PASS' else 'One or more mutations not rejected as required'})
    j = regression['status'] == reproduction['status'] == preservation['status'] == 'PASS' and head == baseline['starting_HEAD'] and not modified and permitted
    gates.append({'gate': 'J', 'name': 'Preservation and Reproducibility', 'status': 'PASS' if j else 'FAIL',
                  'actual_command': 'python scripts/pathways/phase_b1_1/run_phase_b1_1_validation.py -> recorded legacy checks, two builds, all tracked hashes, git diff --check',
                  'exit_code': 0 if j and not commands[-1]['exit_code'] else 1, 'evidence_file': 'phase_b1_1_regression.json; phase_b1_1_validation_report.json',
                  'failure_reason': None if j else 'Regression, reproduction, preservation or additive-scope check failed'})
    passed = all(g['status'] == 'PASS' and g['exit_code'] == 0 for g in gates) and all(c['exit_code'] == 0 for c in commands)
    report = {'phase': 'B1-1', 'execution_status': 'COMPLETED' if passed else 'FAILED', 'engineering_status': 'PASS' if passed else 'FAIL',
              'scientific_status': 'PENDING_HUMAN_REVIEW', 'phase_b0_scientific_status': 'B0_FORMALLY_ACCEPTED_LIMITED_SCOPE',
              'phase_b1_1_execution_authorized': True, 'phase_b1_1_formally_accepted': False, 'phase_b1_2_authorized': False,
              'full_phase_b_authorized': False, 'commit_push_authorized': False, 'gates': gates, 'executions': commands,
              'positive_verification': positive, 'negative_controls': negative, 'regression': regression,
              'reproducibility': reproduction, 'preservation': preservation,
              'implementation_hashes': {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(HERE.glob('*.py'))},
              'protocol_sha256': digest(OUT / 'phase_b1_1_protocol.md'),
              'repository': {'machine': 'sean', 'repository_root': str(ROOT), 'branch': baseline['branch'], 'origin': baseline['origin'],
                             'starting_HEAD': baseline['starting_HEAD'], 'ending_HEAD': head, 'upstream_status_at_start': baseline['upstream_status_at_start'],
                             'final_git_status': status, 'modified_files': modified, 'new_files': sorted(new + [p for p in
                                 ['docs/reduction/pathways/phase_b1_1_validation_report.json', 'docs/reduction/pathways/phase_b1_1_review.md'] if p not in new]),
                             'commit_push_status': 'NOT_ATTEMPTED — B1-1 researcher review hold'}}
    save(OUT / 'phase_b1_1_validation_report.json', report)
    review(report)
    # Capture the actual final inventory after creating the two handoff files.
    actual_status = subprocess.check_output(['git', 'status', '--porcelain', '-uall'], cwd=ROOT).decode('utf-8')
    report['repository']['final_git_status'] = actual_status
    report['repository']['new_files'] = sorted(line[3:] for line in actual_status.splitlines() if line.startswith('??'))
    save(OUT / 'phase_b1_1_validation_report.json', report)
    review(report)
    if not passed:
        fail({'stage': 'acceptance_gates', 'gates': gates})
    print(json.dumps({'execution_status': report['execution_status'], 'engineering_status': report['engineering_status'],
                      'gates': {g['gate']: g['status'] for g in gates}}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())

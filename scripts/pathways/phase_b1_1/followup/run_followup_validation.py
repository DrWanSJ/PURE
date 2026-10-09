#!/usr/bin/env python3
"""Additive follow-up execution; never overwrite any historical report or source."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'docs/reduction/pathways'
HERE = Path(__file__).resolve().parent
LOG = OUT / 'phase_b1_1_followup_execution_log.txt'
FAIL = OUT / 'phase_b1_1_followup_failure_evidence.jsonl'
ENV = {**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'}
sys.path.insert(0, str(HERE.parent))
import verify_followup as followup
import run_phase_b1_1_validation as legacy


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, data):
    Path(path).write_bytes((json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def append(path, text):
    with path.open('a', encoding='utf-8', newline='\n') as f:
        f.write(text + '\n')


def run(command):
    label = subprocess.list2cmdline([str(x) for x in command])
    append(LOG, 'COMMAND: ' + label)
    result = subprocess.run(command, cwd=ROOT, env=ENV, capture_output=True, encoding='utf-8', errors='replace')
    record = {'actual_command': label, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    append(LOG, 'EXIT_CODE: ' + str(result.returncode) + '\nSTDOUT:\n' + result.stdout + '\nSTDERR:\n' + result.stderr)
    if result.returncode:
        append(FAIL, json.dumps({'stage': 'executed_command', **record}, ensure_ascii=False))
    print(json.dumps({'command': label, 'exit_code': result.returncode}), flush=True)
    return record


def old_negative_controls():
    with tempfile.TemporaryDirectory(prefix='b1-1-followup-negative-') as d:
        dest = Path(d)
        for name in ('phase_b0_handoff_witnesses.json', 'phase_b1_1_source_baseline.json'):
            shutil.copyfile(OUT / name, dest / name)
        # Redirect the existing verifier module's OUT, including failure writes.
        # Source ROOT stays canonical; --input-dir explicitly reads historical data.
        shim = ('import sys; from pathlib import Path; sys.path.insert(0,str(Path.cwd()/"scripts/pathways/phase_b1_1")); '
                'import verify_initiation_witnesses as v; v.OUT=Path(sys.argv[1]); '
                'import test_initiation_negative_controls as tests; '
                'sys.argv=["test_initiation_negative_controls"]+sys.argv[2:]; raise SystemExit(tests.main())')
        command = run([sys.executable, '-c', shim, dest, '--input-dir', OUT, '--report', dest / 'negative.json'])
        report = load(dest / 'negative.json') if (dest / 'negative.json').is_file() else {'status': 'FAIL', 'error': 'No rerun report'}
        report['execution'] = command
        report['write_policy'] = 'TEMPORARY_REPORT_AND_FAILURE_DESTINATIONS; HISTORICAL_BYTES_READ_ONLY'
        report['actual_failure_records'] = {p.name: p.read_text(encoding='utf-8') for p in dest.glob('*failure*.jsonl')}
        if report['status'] != 'PASS':
            append(FAIL, json.dumps({'stage': 'original_B1_1_negative_rerun', 'evidence': report}, ensure_ascii=False))
        return report


def regressions():
    # Reuse original acceptance functions unchanged, but intercept the sole report
    # destination and replace log/command/failure sinks in memory. No old main().
    destination = OUT / 'phase_b1_1_followup_regression.json'

    def guarded_report(path, report):
        if Path(path) != OUT / 'phase_b1_1_regression.json':
            raise RuntimeError('Unexpected legacy report write: ' + str(path))
        save(destination, report)

    legacy.save = guarded_report
    legacy.run = run
    legacy.log = lambda s: append(LOG, s)
    legacy.fail = lambda x: append(FAIL, json.dumps(x, ensure_ascii=False))
    legacy.LOG, legacy.FAILURES = LOG, FAIL
    report = legacy.regressions()
    report['followup_write_policy'] = 'UNCHANGED_ACCEPTANCE_FUNCTIONS; REPORT_REDIRECTED_TO_FOLLOWUP; OLD_MAIN_NOT_CALLED'
    save(destination, report)
    return report


def reproduce():
    new_names = ('phase_b1_1_followup_witness.json', 'phase_b1_1_followup_pathway.md')
    old_names = ('phase_b1_1_witnesses.json', 'phase_b1_1_source_scope.json', 'phase_b1_1_initiation_pathways.md')
    evidence = {}
    with tempfile.TemporaryDirectory(prefix='b1-1-followup-reproduce-') as d:
        for label, script, names in [('followup', HERE / 'build_followup.py', new_names),
                                     ('historical_B1_1', HERE.parent / 'build_initiation_witnesses.py', old_names)]:
            hashes, commands = [], []
            for n in range(2):
                dest = Path(d) / label / str(n)
                commands.append(run([sys.executable, script, '--output-dir', dest]))
                hashes.append({name: digest(dest / name) for name in names if (dest / name).is_file()})
            delivered = {name: digest(OUT / name) for name in names}
            evidence[label] = {'status': 'PASS' if hashes[0] == hashes[1] == delivered and all(c['exit_code'] == 0 for c in commands) else 'FAIL',
                               'fresh_builds': 2, 'executions': commands, 'build_hashes': hashes, 'delivered_hashes': delivered}
    evidence['status'] = 'PASS' if all(evidence[k]['status'] == 'PASS' for k in ('followup', 'historical_B1_1')) else 'FAIL'
    return evidence


def review(report):
    data = load(OUT / 'phase_b1_1_followup_witness.json')
    lines = ['# B1-1 Human Review Follow-up — executed review record', '',
             '建议审阅状态：**B1_1_CONDITIONALLY_ACCEPTED**。**不是研究者正式签署**；正式确认仍待研究者给出。', '',
             'Execution: `' + report['execution_status'] + '`；engineering: `' + report['engineering_status'] + '`。'
             '原有 A–J PASS、原始 Phase A/B0/B1-1 记录和签署历史均逐字节保留。', '',
             '## H1–H5：用户审阅结论与必要处理', '', '| 项目 | 用户结论 | 已执行处理 |', '|---|---|---|']
    lines += [f"| {h['id']} — {h['item']} | {h['user_conclusion']} | {h['required_treatment']} |" for h in data['human_review']]
    lines += ['', '## 新路径与解释修订', '',
              '独立 IF3-first 正例：`' + ' → '.join(e['reaction_id'] for e in data['new_witness']['reaction_occurrences']) + '`。', '',
              '**精确净计量：**', '', '```text', data['new_witness']['net_reaction'], '```', '',
              '各边界物种供应 1 个形式 token；IF1/IF3 恢复到原始游离态，IF2_GDP 为实际释放产物。'
              '完整方程、参数、逆向、逐事件库存和来源链见 [新路径](phase_b1_1_followup_pathway.md) '
              '及 [机器记录](phase_b1_1_followup_witness.json)。', '',
              '现有 P1 在本次追加记录中标记为 `LEXICOGRAPHIC_STRUCTURAL_WITNESS`。0724 由 ID 排序选中，'
              '不代表动力学主导路线。0724/0747/0749 消耗同一 GDP 复合物；参考参数分别为 0.0025/1000/4，'
              '不是实测路径通量。IF3-first 与 P1 是独立场景，不共同消耗同一个有限 token。', '',
              '0001 是作者模型中的 `ELONG_tRNA_release`，先产生 E2，再由第一次 Gly-tRNA 结合反应 0013 消耗。'
              '这仅验证原模型的状态依赖顺序；不得直接解释成真实细菌核糖体中起始 tRNA 释放、肽键形成和转位的完整物理机制。'
              'E1/E2 的 mRNA、肽基状态及完整复合物组成仍为 `INFERRED`。', '',
              '后续原文证据需求与当前解释限制已在机器记录和路径文档中分列：需要原论文/SI 对 0001/0013 状态含义、'
              'E1/E2 组成及真实物理步骤映射的明确证据。本次没有宣称取得这些证据。', '',
              '## 重新执行的验收', '', '| Check | Status | Evidence |', '|---|---|---|']
    lines += [f"| {g['id']} — {g['name']} | {g['status']} | {g['evidence_file']} |" for g in report['checks']]
    n = report['negative_summary']
    lines += ['', f"原 B1-1 负控重新执行：{n['historical_passed']}/{n['historical_run']}；"
              f"follow-up 负控：{n['followup_passed']}/{n['followup_run']}。总计 {n['total_passed']}/{n['total_run']}；"
              f"未运行 {n['not_run']}。", '',
              f"原有 {report['preservation']['tracked_files_unchanged']} 个 tracked 文件和 {report['preservation']['historical_B1_1_files_unchanged']} 个 B1-1 文件"
              '全部未变；原 A–J 结果仍为 PASS。', '',
              '新 follow-up 两次构建与交付字节一致，原 B1-1 三个确定性文件也重新构建两次并与历史交付字节一致。', '']
    for group in ('followup', 'historical_B1_1'):
        lines += ['- ' + p + ': `' + h + '`.' for p, h in report['reproducibility'][group]['delivered_hashes'].items()]
    lines += ['', '实际命令、stdout/stderr 和退出码见 [执行日志](phase_b1_1_followup_execution_log.txt)。'
              '独立结果见 [验证报告](phase_b1_1_followup_independent_verification.json)，'
              '变异及原负控重跑见 [负控报告](phase_b1_1_followup_negative_controls.json)，'
              'Phase A/B0/HTML/browser 的实际重跑见 [回归报告](phase_b1_1_followup_regression.json)。'
              '若发生真实失败，它会追加到 phase_b1_1_followup_failure_evidence.jsonl，历史失败档案不会被改写。', '',
              '## 仓库与停止状态', '', '```json', json.dumps(report['repository'], ensure_ascii=False, indent=2), '```', '',
              '```json', json.dumps({k: report[k] for k in ('execution_status', 'engineering_status', 'suggested_review_status',
                  'formal_signoff_status', 'researcher_formally_signed', 'phase_b1_1_formally_accepted', 'commit_push_authorized',
                  'phase_b1_2_authorized', 'qssa_authorized', 'kinetic_reduction_authorized')}, ensure_ascii=False, indent=2), '```', '',
              '完成后停止，等待研究者正式确认。未 commit/push，未开始 B1-2、QSSA 或动力学降阶。']
    (OUT / 'phase_b1_1_followup_review.md').write_bytes(('\n'.join(lines) + '\n').encode('utf-8'))


def main():
    append(LOG, 'Human Review Follow-up run (Asia/Shanghai): ' + datetime.now(timezone(timedelta(hours=8))).isoformat())
    baseline = load(OUT / 'phase_b1_1_followup_baseline.json')
    followup.preservation()
    commands = [run([sys.executable, HERE / 'build_followup.py']), run([sys.executable, HERE / 'verify_followup.py']),
                run([sys.executable, HERE / 'test_followup_negative_controls.py'])]
    positive = load(OUT / 'phase_b1_1_followup_independent_verification.json')
    negatives = load(OUT / 'phase_b1_1_followup_negative_controls.json')
    original_negatives = old_negative_controls()
    negatives['original_B1_1_rerun'] = original_negatives
    negatives['status'] = 'PASS' if negatives['status'] == original_negatives['status'] == 'PASS' else 'FAIL'
    save(OUT / 'phase_b1_1_followup_negative_controls.json', negatives)
    regression = regressions()
    reproduction = reproduce()
    commands.append(run([sys.executable, HERE / 'verify_followup.py']))
    positive = load(OUT / 'phase_b1_1_followup_independent_verification.json')
    protected = followup.preservation()
    commands.append(run(['git', 'diff', '--check']))
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip()
    status = subprocess.check_output(['git', 'status', '--porcelain', '-uall'], cwd=ROOT).decode('utf-8')
    initial = set(baseline['protected_file_hashes'])
    new = [x[3:] for x in status.splitlines() if x.startswith('??') and x[3:] not in initial]
    modified = [x[3:] for x in status.splitlines() if not x.startswith('??')]
    scope_ok = not modified and head == baseline['starting_HEAD'] and all(p.startswith('docs/reduction/pathways/phase_b1_1_followup_') or
        p.startswith('scripts/pathways/phase_b1_1/followup/') for p in new)
    checks = [{'id': cid, 'name': name, 'status': check_status, 'evidence_file': file} for cid, name, check_status, file in (
        ('FU1', 'Canonical source and original B1-1 independent rerun', positive['status'], 'phase_b1_1_followup_independent_verification.json'),
        ('FU2', 'IF3-first exact net, marking, lineage, recovery and E1', positive['status'], 'phase_b1_1_followup_independent_verification.json'),
        ('FU3', 'Release competition and P1 lexicographic annotation', positive['status'], 'phase_b1_1_followup_witness.json'),
        ('FU4', 'Model order, composition limits and conditional review authority', positive['status'], 'phase_b1_1_followup_witness.json'),
        ('FU5', 'Historical and follow-up negative controls rerun', negatives['status'], 'phase_b1_1_followup_negative_controls.json'),
        ('FU6', 'Phase A/B0/HTML/browser rerun', regression['status'], 'phase_b1_1_followup_regression.json'),
        ('FU7', 'Two fresh builds of both historical and follow-up outputs', reproduction['status'], 'phase_b1_1_followup_validation_report.json'),
        ('FU8', 'All beginning bytes and additive Git scope', 'PASS' if scope_ok and protected['status'] == 'PASS' else 'FAIL', 'phase_b1_1_followup_baseline.json'))]
    passed = all(c['status'] == 'PASS' for c in checks) and all(c['exit_code'] == 0 for c in commands)
    report = {'execution_status': 'COMPLETED' if passed else 'FAILED', 'engineering_status': 'PASS' if passed else 'FAIL',
              'suggested_review_status': 'B1_1_CONDITIONALLY_ACCEPTED', 'formal_signoff_status': 'PENDING_FINAL_RESEARCHER_CONFIRMATION',
              'researcher_formally_signed': False, 'phase_b1_1_formally_accepted': False, 'commit_push_authorized': False,
              'phase_b1_2_authorized': False, 'qssa_authorized': False, 'kinetic_reduction_authorized': False,
              'checks': checks, 'executions': commands, 'positive_verification': positive, 'preservation': protected,
              'negative_summary': {'historical_run': original_negatives.get('controls_run', 0), 'historical_passed': original_negatives.get('controls_passed', 0),
                  'followup_run': negatives['followup_controls_run'], 'followup_passed': negatives['followup_controls_passed'],
                  'total_run': original_negatives.get('controls_run', 0) + negatives['followup_controls_run'],
                  'total_passed': original_negatives.get('controls_passed', 0) + negatives['followup_controls_passed'],
                  'not_run': len(negatives['controls_not_run']) + len(original_negatives.get('controls_not_run', []))},
              'regression_summary': {k: regression[k]['status'] for k in ('phase_a', 'b0', 'html')}, 'reproducibility': reproduction,
              'implementation_hashes': {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(HERE.glob('*.py'))},
              'protocol_sha256': digest(OUT / 'phase_b1_1_followup_protocol.md'),
              'repository': {'machine': 'sean', 'repository_root': str(ROOT), 'branch': baseline['branch'], 'origin': baseline['origin'],
                  'starting_HEAD': baseline['starting_HEAD'], 'ending_HEAD': head, 'modified_existing_files': modified,
                  'new_followup_files': sorted(new), 'commit_push_status': 'NOT_ATTEMPTED — awaiting formal researcher confirmation'}}
    path = OUT / 'phase_b1_1_followup_validation_report.json'
    save(path, report)
    review(report)
    final_status = subprocess.check_output(['git', 'status', '--porcelain', '-uall'], cwd=ROOT).decode('utf-8')
    report['repository']['final_git_status'] = final_status
    report['repository']['new_followup_files'] = sorted(x[3:] for x in final_status.splitlines() if x.startswith('??') and x[3:] not in initial)
    save(path, report)
    review(report)
    if not passed:
        append(FAIL, json.dumps({'stage': 'followup_acceptance', 'checks': checks}, ensure_ascii=False))
    print(json.dumps({'execution_status': report['execution_status'], 'engineering_status': report['engineering_status'],
                      'checks': {c['id']: c['status'] for c in checks}, 'negative_summary': report['negative_summary']}), flush=True)
    return 0 if passed else 1


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception:
        append(FAIL, json.dumps({'stage': 'followup_runner_exception', 'traceback': traceback.format_exc()}))
        raise

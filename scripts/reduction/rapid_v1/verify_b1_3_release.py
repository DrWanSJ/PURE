"""Replay the frozen B1-3 structural evidence into a new, protected directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
HISTORY = ROOT / 'docs/reduction/pathways'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-id', required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', args.run_id):
        raise ValueError('Unsafe run-id')
    output = ROOT / 'results/reduction/phase_c_release_v1' / args.run_id
    output.mkdir(parents=True, exist_ok=False)
    def guard(event, values):
        if event != 'open' or isinstance(values[0], int):
            return
        path, _, flags = values
        if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            if not Path(os.fsdecode(path)).resolve().is_relative_to(output.resolve()):
                raise RuntimeError('Historical evidence write refused: ' + str(path))
    sys.addaudithook(guard)
    sys.path.insert(0, str(ROOT / 'scripts/pathways/phase_b1_3'))
    import verify_witnesses as verifier
    import test_negative_controls as negative
    import audit_full_matrices as matrices
    report = {'schema': 'B1_3_RELEASE_REPLAY_V1', 'status': 'RUNNING',
              'human_decision': 'Separate additive 2026-10-10 formal acceptance',
              'historical_pending_fields': 'Preserved and tested as original evidence',
              'source_parser': 'Independent canonical XML and author parameter extraction; B1-3 builder not imported'}
    try:
        data = verifier.load(HISTORY / 'phase_b1_3_witnesses.json')
        scope = verifier.load(HISTORY / 'phase_b1_3_source_scope.json')
        positive = verifier.validate(data, scope)
        verifier.save(output / 'independent_verification.json', positive)
        assert positive['status'] == 'PASS' and len(positive['witnesses']) == 34
        # Only negative-control output/log roots change. The verifier continues
        # reading frozen upstream evidence at its original location.
        negative.OUT = output
        shutil.copyfile(HISTORY / 'phase_b1_3_verification_contract.json', output / 'phase_b1_3_verification_contract.json')
        sys.argv = ['test_negative_controls.py', '--input-dir', str(HISTORY), '--report', str(output/'negative_controls.json')]
        assert negative.main() == 0
        sys.argv = ['audit_full_matrices.py', '--input-dir', str(HISTORY), '--output-dir', str(output)]
        assert matrices.main() == 0
        rebuilt = verifier.load(output / 'phase_b1_3_source_matrices.json')
        original = verifier.load(HISTORY / 'phase_b1_3_source_matrices.json')
        assert rebuilt == original
        baseline = verifier.load(ROOT / 'docs/reduction/rapid_reduction/release_preflight_20261010.json')
        changed = [row['path'] for row in baseline['original_research_files']
                   if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest() != row['sha256']]
        assert not changed, changed
        controls = verifier.load(output / 'negative_controls.json')
        report.update(status='PASS', witnesses_checked=34,
                      negative_controls_passed=controls['controls_passed'],
                      negative_controls_run=controls['controls_run'],
                      lineage_invalid_cases=controls['petri_enabled_lineage_invalid_count'],
                      source_matrix_shape=rebuilt['shape'], matrix_semantically_identical=True,
                      protected_original_files=277, changed_original_files=changed)
    except Exception:
        report.update(status='FAIL', error=traceback.format_exc())
        raise
    finally:
        verifier.save(output / 'verification_report.json', report)
    print(json.dumps(report))


if __name__ == '__main__':
    main()

"""Record checkout context and immutable inputs before the new investigation."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/energy_cycles_v1'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    destination = OUT / 'protected_inputs_before.json'
    if destination.exists():
        raise RuntimeError('Baseline is immutable; refusing to replace it')
    files = git('ls-files').splitlines()
    records = {p: digest(ROOT/p) for p in files}
    context = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'source_commit': git('rev-parse', 'HEAD'),
        'expected_commit': '60abf1e371e90f70474bc98174035726cc68f064',
        'branch': git('branch', '--show-current'),
        'remote': git('remote', '-v'),
        'remote_refs_after_fetch': git('for-each-ref', '--format=%(refname) %(objectname)', 'refs/remotes/origin'),
        'main_topology_left_right': git('rev-list', '--left-right', '--count', 'origin/main...origin/codex/pnas-topology-first'),
        'merge_base': git('merge-base', 'origin/main', 'origin/codex/pnas-topology-first'),
        'target_subsequent_remote_commits': git('log', '--oneline', '60abf1e371e90f70474bc98174035726cc68f064..origin/codex/pnas-topology-first'),
        'original_desktop_branch': 'codex/r3-diagnostics-visualizations',
        'original_desktop_head': '775607bf9922c6878be0147bd7c64fa97e86a790',
        'original_desktop_status_before': 'clean',
        'topology_donor_status_before': 'clean',
        'all_existing_tracked_file_sha256': records,
        'authorization': 'New additive research only. No commits, push, merge, rebase, reset or branch deletion.',
    }
    if context['source_commit'] != context['expected_commit']:
        raise RuntimeError('Wrong source checkout')
    destination.write_text(json.dumps(context, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'tracked_inputs': len(records), 'source_commit': context['source_commit']}))

if __name__ == '__main__':
    main()

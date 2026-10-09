"""Read-only verification of reference and evidence availability; Python stdlib only.

Run after git fetch origin --tags, from any clone, with --repo PATH.
No worktree/index changes, scientific solves, or evidence writes are performed.
"""
import argparse, csv, hashlib, json, pathlib, subprocess

def verify(repo, reports):
    def git(*args):
        return subprocess.check_output(['git', '--no-optional-locks', '-C', str(repo), *args])
    advertised = {}
    for line in git('ls-remote', '--heads', '--tags', 'origin').decode().splitlines():
        oid, ref = line.split('\t'); advertised[ref] = oid
    expected = json.loads((reports/'remote_verified_refs.json').read_text())['refs']
    for ref, oid in expected.items():
        assert advertised.get(ref) == oid, ('REMOTE_REF_MOVED_OR_MISSING', ref, oid, advertised.get(ref))
    refs = git('for-each-ref', '--format=%(refname)', 'refs/remotes/origin', 'refs/tags').decode().splitlines()
    objects = {line.split(' ',1)[0] for line in git('rev-list', '--objects', *refs).decode().splitlines()}
    count = 0
    for filename in ['r6_untracked_inventory.csv', 'g1_untracked_inventory.csv']:
        with (reports/filename).open(encoding='utf-8', newline='') as handle:
            for row in csv.DictReader(handle):
                oid = row['remote_blob']
                assert oid in objects, ('NOT_REMOTE_REACHABLE', row['relative_path'])
                data = git('cat-file', 'blob', oid)
                assert hashlib.sha256(data).hexdigest() == row['sha256'], ('BYTE_MISMATCH', row['relative_path'])
                count += 1
    return {'status':'PASS_REFERENCE_AND_BYTE_AVAILABILITY', 'reference_count':len(expected),
            'scientific_artifact_count':count, 'scientific_approval':'NOT_ESTABLISHED_BY_THIS_CHECK'}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--repo',type=pathlib.Path,default=pathlib.Path.cwd())
    args=parser.parse_args()
    print(json.dumps(verify(args.repo,pathlib.Path(__file__).resolve().parent),indent=2))

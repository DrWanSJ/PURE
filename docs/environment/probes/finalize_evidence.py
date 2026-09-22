"""Validate and close the recorded CZ audit; never stage/commit scientific files."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess

root = Path(__file__).resolve().parents[3]
folder = root / 'docs/environment'
out = folder / 'CZ_20260922'


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_log(record):
    # JSON retains exact decoded streams; text logs remove console padding and
    # normalize CR/CRLF for readable, whitespace-clean review diffs.
    metadata = {k:v for k,v in record.items() if k not in ('stdout','stderr')}
    def readable(s):
        return '\n'.join(line.rstrip() for line in s.splitlines())
    return (json.dumps(metadata, indent=2, ensure_ascii=False)+'\n\nSTDOUT:\n'
            +readable(record['stdout'])+'\nSTDERR:\n'
            +(readable(record['stderr']) or '(empty)')+'\n')


initial = json.loads((out/'initial_state.json').read_text(encoding='utf-8'))
changed = [p for p,h in initial['tracked_sha256'].items()
           if not (root/p).is_file() or sha(root/p) != h]
assert not changed, 'Protected original file changed: '+str(changed)
records = {}
for phase in ('inventory','matlab','wolfram'):
    batch = json.loads((out/('results_'+phase+'.json')).read_text(encoding='utf-8'))
    for r in batch:
        records[r['name']] = r
        (out/(r['name']+'.txt')).write_text(render_log(r),encoding='utf-8',newline='\n')

markers = {
    'matlab_smoke_base': 'SMOKE_PASS=base',
    'matlab_smoke_symbolic': 'SMOKE_PASS=symbolic',
    'matlab_smoke_optimization': 'SMOKE_PASS=optimization',
    'matlab_smoke_simbiology': 'SMOKE_PASS=simbiology',
    'project_matlab_literature': 'LITERATURE_TESTS total=9 passed=9 failed=0 incomplete=0',
    'project_matlab_dimensionless': 'PROJECT_PASS=dimensionless',
    'project_sympy': 'NUMERIC CHECK: ALL PASS (5 trials x 12 eqs)',
    'project_wolfram': 'AUDIT ALL PASS: True',
}
checks = {}
for name,marker in markers.items():
    r = records[name]
    checks[name] = r['exit_code']==0 and marker in r['stdout'] and not r['stderr']
    assert checks[name], (name, r)
wolfram = records['wolfram_symbolic']
assert wolfram['exit_code']==0 and wolfram['stdout'].strip()=='0' and not wolfram['stderr']
for package in ('sympy','numpy','scipy','pandas','matplotlib'):
    missing = records['python_'+package]
    installed = records['python3_'+package]
    assert missing['exit_code']==1 and "No module named '"+package+"'" in missing['stderr']
    assert installed['exit_code']==0 and installed['stdout'].strip()
assert records['python_runtime']['argv'][0].lower() != records['python3_runtime']['argv'][0].lower()
assert '25.2.0.3150157 (R2025b) Update 4' in records['matlab_version']['stdout']
for feature in ('MATLAB','Symbolic_Toolbox','Optimization_Toolbox','SimBiology'):
    assert 'LICENSE_TEST | '+feature+' | 1' in records['matlab_capability']['stdout']

status = dict(environment_recorded=True, base_matlab_available=checks['matlab_smoke_base'],
    symbolic_available=checks['matlab_smoke_symbolic'], optimization_available=checks['matlab_smoke_optimization'],
    simbiology_available=checks['matlab_smoke_simbiology'], python_sympy_available=True,
    python_sympy_runtime='python3 / CPython 3.14.3 / SymPy 1.14.0', default_python_sympy_available=False,
    wolfram_available=True, project_smoke_tests_passed=all(v for k,v in checks.items() if k.startswith('project_')),
    scientific_files_modified=False, historical_sean_record_modified=False,
    commit_performed=False, push_performed=False, checks=checks,
    scope='Only listed native capability and four project checks; no full benchmark/release rerun.')
write_json(out/'status.json',status)
(out/'smoke_tests.txt').write_text('\n'.join(
    f'{name}: pass={passed}; native_exit={records[name]["exit_code"]}; evidence={name}.txt'
    for name,passed in checks.items())+'\n',encoding='utf-8',newline='\n')

git_records = []
for argv in (['git','status','--short'], ['git','diff','--check'], ['git','diff','--stat'],
             ['git','diff','--name-only'], ['git','diff','--cached','--name-only'],
             ['git','rev-parse','HEAD'], ['git','rev-parse','origin/main'],
             ['git','status','--porcelain=v1','--untracked-files=all']):
    p = subprocess.run(argv,cwd=root,capture_output=True)
    r = dict(argv=argv,command=subprocess.list2cmdline(argv),exit_code=p.returncode,
             stdout=p.stdout.decode('utf-8'),stderr=p.stderr.decode('utf-8'))
    assert p.returncode==0, r
    git_records.append(r)
assert not git_records[3]['stdout'] and not git_records[4]['stdout']
assert git_records[5]['stdout'].strip() == git_records[6]['stdout'].strip() == '444a90e4503a7b824f38bc8f5daf8551d3c3efed'
for line in git_records[-1]['stdout'].splitlines():
    assert line.startswith('?? docs/environment/'), line
(out/'final_git_audit.txt').write_text('\n'.join(render_log(r) for r in git_records),encoding='utf-8',newline='\n')

write_json(out/'final_audit.json',dict(checked_at=dt.datetime.now().astimezone().isoformat(),
    source_commit=git_records[5]['stdout'].strip(), tracked_files_checked=len(initial['tracked_sha256']),
    all_original_tracked_files_sha256_unchanged=not changed, changed_files=changed,
    original_root_environment_sha256=sha(root/'environment_lock.md'),
    working_tree_scope='Only untracked docs/environment/ additions', staged_changes=False,
    git_diff_check_exit_code=git_records[1]['exit_code'],
    git_diff_stat=git_records[2]['stdout'],
    note='Git diff excludes untracked additions. The separate manifest inventories every environment artifact.',
    privacy='Only whitelisted platform fields; MATLAB ver license identifier redacted before persistence.'))

# Basic deliverable integrity: valid JSON, relative Markdown links, no caches or
# binary artifacts, and clean presentation whitespace (decoded streams in JSON).
files = sorted(p for p in folder.rglob('*') if p.is_file() and p.name!='artifact_manifest.json')
for p in files:
    assert p.suffix in ('.md','.txt','.json','.py','.m'), p
    content = p.read_text(encoding='utf-8')
    assert '\x00' not in content and '\ufffd' not in content, p
    assert not any(line != line.rstrip() for line in content.splitlines()), ('trailing whitespace',p)
    if p.suffix=='.json':
        json.loads(content)
    if p.suffix=='.md':
        for target in re.findall(r'\]\(([^)]+)\)',content):
            if '://' not in target and not target.startswith('#'):
                linked = (p.parent/target.split('#')[0]).resolve()
                assert linked.exists() or linked == out/'artifact_manifest.json', ('broken link',p,target)
    for match in re.finditer(r'(?:MATLAB 许可证编号|MATLAB License Number)\s*[:：]\s*([^\r\n]+)',content):
        assert match.group(1).startswith('[REDACTED]'), ('license identifier',p)
write_json(out/'artifact_manifest.json',dict(excludes='This manifest only (self-reference)',
    files=[dict(path=str(p.relative_to(root)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)) for p in files]))
print(json.dumps(dict(status='PASS',original_tracked_files_unchanged=len(initial['tracked_sha256']),
    environment_files=len(files)+1, total_bytes=sum(p.stat().st_size for p in files)+(out/'artifact_manifest.json').stat().st_size),indent=2))

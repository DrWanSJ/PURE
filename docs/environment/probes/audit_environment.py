"""Record native environment checks without changing scientific source files.

Usage: python3 -B -X utf8 audit_environment.py --repo PATH --output NEW_PATH
The output directory must not exist, except when --resume-initial is supplied
for an initial_state.json captured before this new audit code was added.
Phases inventory, matlab and wolfram can be resumed individually using
--phase NAME --resume-initial; no package installation or source repairs occur.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(data):
    for encoding in ('utf-8', 'gb18030'):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            pass
    return data.decode('utf-8', errors='replace'), 'utf-8 (replacement characters)'


def redact(text):
    # MATLAB ver prints a license identifier; never persist its value.
    return re.sub(r'(?im)^([^\r\n]*(?:license (?:number|id)|许可证(?:编号|号))\s*[:：])[^\r\n]*',
                  r'\1 [REDACTED]', text)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--phase', choices=['all', 'inventory', 'matlab', 'wolfram'], default='all')
parser.add_argument('--resume-initial', action='store_true')
args = parser.parse_args()
root = args.repo.resolve()
out = args.output.resolve()
probes = Path(__file__).resolve().parent
records = []


def execute(name, argv, cwd=None, timeout=600, env_extra=None):
    # Windows CreateProcess also searches the parent executable directory.
    # Resolve via PATH first so `python` cannot silently launch this auditor's
    # own python3 runtime instead of the shell-visible python entry point.
    requested_argv = list(argv)
    argv = [shutil.which(argv[0]) or argv[0], *argv[1:]]
    print('START', name, flush=True)
    started = dt.datetime.now().astimezone().isoformat()
    tic = time.monotonic()
    env = os.environ.copy()
    env.update({'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONIOENCODING': 'utf-8'})
    if env_extra:
        env.update(env_extra)
    status = 'completed'
    try:
        p = subprocess.run(argv, cwd=cwd or root, capture_output=True, timeout=timeout, env=env)
        stdout, stdout_encoding = decode(p.stdout)
        stderr, stderr_encoding = decode(p.stderr)
        code = p.returncode
    except FileNotFoundError as e:
        stdout, stderr, code, status = '', str(e), None, 'unavailable'
        stdout_encoding = stderr_encoding = 'not_applicable'
    except subprocess.TimeoutExpired as e:
        stdout, stdout_encoding = decode(e.stdout or b'')
        stderr, stderr_encoding = decode(e.stderr or b'')
        stderr += '\nProcess timed out; no success inferred; inspect remaining native processes before retry.'
        code, status = None, 'timeout'
    stdout, stderr = redact(stdout), redact(stderr)
    record = dict(name=name, requested_argv=requested_argv, argv=argv, command=subprocess.list2cmdline(argv), cwd=str(cwd or root),
                  started=started, duration_seconds=round(time.monotonic()-tic, 3),
                  exit_code=code, execution_status=status, stdout_encoding=stdout_encoding,
                  stderr_encoding=stderr_encoding, stdout=stdout, stderr=stderr)
    (out/(name+'.txt')).write_text(
        json.dumps({k:v for k,v in record.items() if k not in ('stdout','stderr')}, indent=2)
        +'\n\nSTDOUT:\n'+stdout+'\nSTDERR:\n'+(stderr or '(empty)')+'\n', encoding='utf-8')
    records.append(record)
    print('END', name, 'exit_code='+str(code), 'status='+status, flush=True)
    return record


if not args.resume_initial:
    # Honor the clean-tree gate before writing anything.
    status = subprocess.check_output(['git', 'status', '--porcelain=v1'], cwd=root)
    if status:
        raise SystemExit('Working tree not clean; STOP.\n'+status.decode())
    out.mkdir(parents=True, exist_ok=False)
    initial = [execute('initial_git_'+str(i), cmd) for i, cmd in enumerate([
        ['git','status'], ['git','branch','--show-current'], ['git','rev-parse','HEAD'],
        ['git','rev-parse','origin/main'], ['git','remote','-v'], ['git','log','-1','--oneline']])]
    paths = subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
    (out/'initial_state.json').write_text(json.dumps(dict(git=initial,
        recorded_at=dt.datetime.now().astimezone().isoformat(), repo_path=str(root),
        tracked_sha256={p:sha(root/p) for p in paths if p}),indent=2)+'\n',encoding='utf-8')
else:
    assert (out/'initial_state.json').is_file(), 'Initial clean-state evidence is required.'

initial = json.loads((out/'initial_state.json').read_text(encoding='utf-8'))
changed = [p for p,h in initial['tracked_sha256'].items() if not (root/p).is_file() or sha(root/p)!=h]
assert not changed, 'Tracked files changed since the initial snapshot: '+str(changed)

if not (out/'isolation.json').exists():
    scratch = Path(tempfile.mkdtemp(prefix='PURE_CZ_environment_'))
    copies = []
    for p,h in initial['tracked_sha256'].items():
        if p.startswith(('matlab/','models/')):
            target = scratch/p
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(root/p, target)
            assert sha(target)==h
            copies.append(dict(path=p, sha256=h))
    (out/'isolation.json').write_text(json.dumps(dict(scratch=str(scratch),
        copied_files=copies, byte_identity_verified=True),indent=2)+'\n',encoding='utf-8')
else:
    scratch = Path(json.loads((out/'isolation.json').read_text())['scratch'])
env_extra = {'PURE_AUDIT_SCRATCH': str(scratch)}
matlab = shutil.which('matlab') or 'matlab'
wolfram = shutil.which('wolframscript') or 'wolframscript'
ps = shutil.which('pwsh') or shutil.which('powershell') or 'powershell'

if args.phase in ('all','inventory'):
    execute('git_version', ['git','--version'])
    for exe in ('git','matlab','python','python3','wolframscript'):
        execute('where_'+exe, ['where.exe',exe])
    platform_code = r"""
$ErrorActionPreference='Stop'
$os=Get-CimInstance Win32_OperatingSystem
$cpu=Get-CimInstance Win32_Processor
$cs=Get-CimInstance Win32_ComputerSystem
$win=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
[ordered]@{
 user=$env:USERNAME; hostname=$env:COMPUTERNAME; cwd=(Get-Location).Path
 os_caption=$os.Caption; os_version=$os.Version; os_build=$os.BuildNumber
 display_version=$win.DisplayVersion; update_build_revision=$win.UBR
 os_architecture=$os.OSArchitecture; system_type=$cs.SystemType
 cpu=@($cpu | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors)
 logical_processors=$cs.NumberOfLogicalProcessors; physical_memory_bytes=$cs.TotalPhysicalMemory
 shell_executable=(Get-Process -Id $PID).Path; powershell_version=$PSVersionTable.PSVersion.ToString()
 powershell_edition=$PSVersionTable.PSEdition
} | ConvertTo-Json -Depth 5
"""
    execute('platform', [ps,'-NoProfile','-Command',platform_code])
    execute('powershell_version', [ps,'-NoProfile','-Command',"$PSVersionTable | Format-List; (Get-Process -Id $PID).Path"])
    for exe in ('python','python3'):
        execute(exe+'_version', [exe,'--version'])
        execute(exe+'_runtime', [exe,'-c','import sys; print(sys.executable); print(sys.version)'])
        for package in ('sympy','numpy','scipy','pandas','matplotlib'):
            execute(exe+'_'+package, [exe,'-c',f'import {package}; print({package}.__version__); print({package}.__file__)'])
    execute('project_sympy', ['python3','-B','-X','utf8',str(scratch/'models/literature_reference/dimensionless/derive_dimensionless.py')], cwd=scratch)

if args.phase in ('all','matlab'):
    execute('matlab_version', [matlab,'-batch',"disp(version); disp(version('-release')); ver"], cwd=scratch)
    prefix = "addpath('"+probes.as_posix().replace("'","''")+"'); "
    execute('matlab_capability', [matlab,'-batch',prefix+'matlab_capability'], cwd=scratch)
    lint_targets = [probes/'matlab_capability.m',probes/'matlab_smoke.m',probes/'matlab_project.m',
                    scratch/'matlab/tests/test_pure_literature_reference.m',
                    scratch/'models/literature_reference/dimensionless/derive_dimensionless.m']
    lint = '; '.join("fprintf('CHECKCODE %s\\n', '"+p.name+"'); disp(checkcode('"+p.as_posix()+"', '-id'))" for p in lint_targets)
    execute('matlab_checkcode', [matlab,'-batch',lint], cwd=scratch)
    for kind in ('base','symbolic','optimization','simbiology'):
        execute('matlab_smoke_'+kind, [matlab,'-batch',prefix+"matlab_smoke('"+kind+"')"], cwd=scratch, env_extra=env_extra)
    for kind in ('literature','dimensionless'):
        execute('project_matlab_'+kind, [matlab,'-batch',prefix+"matlab_project('"+kind+"')"], cwd=scratch, env_extra=env_extra)

if args.phase in ('all','wolfram'):
    execute('wolfram_version', [wolfram,'-version'])
    execute('wolfram_kernel', [wolfram,'-code','$Version'])
    execute('wolfram_system', [wolfram,'-code','$SystemID'])
    execute('wolfram_symbolic', [wolfram,'-code','Simplify[D[x^2,x]-2 x]'])
    execute('project_wolfram', [wolfram,'-file',str(scratch/'models/literature_reference/dimensionless/verify_wolfram_v2.wl')], cwd=scratch)

execute('git_status_after_'+args.phase, ['git','status','--short'])
changed = [p for p,h in initial['tracked_sha256'].items() if not (root/p).is_file() or sha(root/p)!=h]
integrity = dict(tracked_files_checked=len(initial['tracked_sha256']), changed=changed,
                 all_unchanged=not changed, checked_at=dt.datetime.now().astimezone().isoformat())
(out/('integrity_'+args.phase+'.json')).write_text(json.dumps(integrity,indent=2)+'\n',encoding='utf-8')
(out/('results_'+args.phase+'.json')).write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
assert not changed, 'Original tracked file bytes changed: '+str(changed)
print('PHASE_COMPLETE',args.phase,'tracked_files_unchanged='+str(len(initial['tracked_sha256'])),flush=True)

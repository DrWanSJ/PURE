# Reproducing the environment audit

These are environment-only probes. They do not install packages, change search
paths persistently, modify scientific source, stage files, commit or push.

From a **clean checkout**, use PowerShell and a new output directory:

```powershell
$repoPath = 'C:\Users\CZ\Desktop\PURE'
$auditOutput = Join-Path $env:TEMP ('PURE_CZ_record_' + (Get-Date -Format yyyyMMdd_HHmmss))
python3 -B -X utf8 "$repoPath\docs\environment\probes\audit_environment.py" --repo $repoPath --output $auditOutput
```

The initial audit began before these new environment files existed. Its clean
Git state and SHA-256 of all 201 tracked files were saved first. The three phases
were then invoked with `--resume-initial` against that saved initial state:

```powershell
python3 -B -X utf8 docs/environment/probes/audit_environment.py --repo 'C:\Users\CZ\Desktop\PURE' --output 'C:\Users\CZ\Desktop\PURE\docs\environment\CZ_20260922' --phase inventory --resume-initial
python3 -B -X utf8 docs/environment/probes/audit_environment.py --repo 'C:\Users\CZ\Desktop\PURE' --output 'C:\Users\CZ\Desktop\PURE\docs\environment\CZ_20260922' --phase matlab --resume-initial
python3 -B -X utf8 docs/environment/probes/audit_environment.py --repo 'C:\Users\CZ\Desktop\PURE' --output 'C:\Users\CZ\Desktop\PURE\docs\environment\CZ_20260922' --phase wolfram --resume-initial
```

Those commands document this run. Use a new output directory for a new audit;
do not overwrite this historical evidence. The default entry refuses a dirty
working tree. The resume option requires an existing initial-state record and
checks that every initially tracked file remains byte-identical.

The runner copies tracked `matlab/` and `models/` files to a uniquely named system
temporary directory and verifies their SHA-256 before execution. Native project
checks run against those unchanged copies. MATLAB's `derive_dimensionless.m`
can therefore write its normal output only inside the temporary snapshot.
The temporary snapshot and its generated CSV/CAS output are not deliverables.
The original `matlab/tools/check_environment.m` is not run because it writes to
the historical `results/environment/toolbox_check.json` location.

The four MATLAB probes run in separate `-batch` processes, so every smoke test
has its own native process exit code. `license('test', ...)` is followed by real
function execution; `license('inuse')` records only feature names. SimBiology is
tested through object construction, not a PURE model or a simulation. The
literature wrapper asserts that every test passed and none was incomplete.

Each text log contains the command/argument vector, working directory, start
time, elapsed time, process exit code, stdout and stderr. Result JSON files retain
the decoded streams. Exit code 0 by itself is not a scientific validation claim;
the profile also requires the relevant pass markers or zero symbolic residual.
Missing packages remain missing; no installation or repair is attempted.

Native executables are resolved through `shutil.which` to absolute paths before
launch. This is essential on Windows: a Python subprocess given bare `python`
can search its own interpreter directory before PATH, yielding a different
runtime from PowerShell. `python_runtime` and `python3_runtime` record
`sys.executable` separately. Use the final `results_inventory.json`, not the
superseded diagnostic capture, for shell-visible Python capabilities.

`command` uses Windows process argument rendering, not PowerShell escaping.
`argv` is authoritative and is directly reproducible with `subprocess.run`.
For manual Wolfram commands in PowerShell, keep `$Version` and `$SystemID` in
single quotes to avoid shell interpolation:

```powershell
wolframscript -code '$Version'
wolframscript -code '$SystemID'
wolframscript -code 'Simplify[D[x^2,x]-2 x]'
```

No environment variables, license files or sensitive configuration are dumped.
MATLAB's `ver` license-number line is redacted in memory before writing logs.
Logs are decoded as UTF-8, falling back to GB18030 for localized MATLAB output;
the original decoding is recorded. Text-log line endings and trailing console
padding are normalized for readability; decoded stdout/stderr in result JSON
remain the evidence source.
Other installed toolboxes are inventoried by `ver`, but are `not_tested` unless
listed as tested in the profile.

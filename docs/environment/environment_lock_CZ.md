# Environment Lock — CZ workstation

This independent execution environment record is based on commands actually run
on 2026-09-22. It neither replaces the sean workstation record nor changes the
scientific model or benchmark baseline. Evidence is in [CZ_20260922](CZ_20260922/README.md).

## Identity

| Item | Measured value |
| --- | --- |
| User | `CZ` |
| Hostname | `DESKTOP-EDVOOH0` |
| Repository | `C:\Users\CZ\Desktop\PURE` |
| Recorded date | 2026-09-22, Asia/Shanghai (`+08:00`) |
| Initial clean-state capture | `2026-09-22T14:32:29.016641+08:00` |
| Native checks | 14:35–14:37 local time; final PATH-resolved Python inventory at 14:36 |
| Source commit | `444a90e4503a7b824f38bc8f5daf8551d3c3efed` |

## Platform

| Item | Measured value |
| --- | --- |
| OS edition | Microsoft Windows 10 专业版 (Pro) |
| Version / display version | `10.0.19045` / `22H2` |
| Build / update build revision | `19045` / `6466` (full build `19045.6466`) |
| Architecture | 64-bit OS; `x64-based PC`; MATLAB `PCWIN64` |
| Current shell | PowerShell Core `7.6.5` |
| Shell executable | `C:\Users\CZ\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe` |
| Working directory | `C:\Users\CZ\Desktop\PURE` |
| CPU reported by Windows | AMD EPYC 7702 64-Core Processor |
| Cores / logical processors | 64 / 128 |
| Physical memory reported by Windows | `549614985216` bytes = `511.868843` GiB |

Sources: [platform command/output](CZ_20260922/platform.txt) and
[PowerShell version](CZ_20260922/powershell_version.txt). This is the machine
configuration exposed by Windows; no hardware identifiers were collected.

## Git

| Item | Measured value |
| --- | --- |
| Version | `2.54.0.windows.1` |
| Executable | `C:\Program Files\Git\cmd\git.exe` |
| Branch | `main` |
| HEAD | `444a90e4503a7b824f38bc8f5daf8551d3c3efed` |
| Local `origin/main` | `444a90e4503a7b824f38bc8f5daf8551d3c3efed` |
| Local/origin sync status | HEAD equals the locally stored `origin/main`; no fetch/remote freshness claim |
| Initial working tree | clean, including no untracked files |
| Remote | `https://github.com/DrWanSJ/PURE.git` (fetch and push) |
| Last commit | `444a90e docs: close B1 human audit for reproduction scope` |
| Final working tree | Only new, untracked environment documents/evidence under `docs/environment/` |

Evidence: [initial Git commands](CZ_20260922/git_status.txt),
[Git version](CZ_20260922/git_version.txt), [executable discovery](CZ_20260922/where_git.txt)
and [final audit](CZ_20260922/final_git_audit.txt). No files were staged, committed or pushed.

## MATLAB

| Item | Measured value |
| --- | --- |
| Executable | `C:\Program Files\MATLAB\R2025b\bin\matlab.exe` |
| Kernel/runtime version | `25.2.0.3150157 (R2025b) Update 4` |
| Release / update | R2025b / Update 4 |
| CLI invocation | `matlab -batch "<command>"` |
| Independent launcher/wrapper version | `not_tested`; the version above is returned inside MATLAB |
| Product/toolbox version | MATLAB, Symbolic Math Toolbox, Optimization Toolbox and SimBiology each report `25.2` |

The complete installed-product inventory is retained in
[the executed `ver` output](CZ_20260922/matlab_version.txt) and
[the capability probe](CZ_20260922/matlab_capability.txt). Other listed products
are installed according to `ver`, but their functionality/licenses are
`not_tested` unless explicitly tested below.

| Product | Installed by `ver` | Tested license feature | `license('test', feature)` | Real smoke test | Native exit | Result / error |
| --- | --- | --- | --- | --- | --- | --- |
| Base MATLAB | yes, 25.2 | `MATLAB` | 1 | `ode15s`, `jsondecode`, `writetable` with readback | 0 | pass / none |
| Symbolic Math Toolbox | yes, 25.2 | `Symbolic_Toolbox` | 1 | `syms x; simplify(diff(x^2,x)-2*x)` returns 0 | 0 | pass / none |
| Optimization Toolbox | yes, 25.2 | `Optimization_Toolbox` | 1 | `lsqnonlin(@(x) x-2,0,[],[],options)` returns x=2, resnorm=0, optimizer exitflag=1 | 0 | pass / none |
| SimBiology | yes, 25.2 | `SimBiology` | 1 | `sbiomodel` plus one compartment and one species | 0 | pass / none |

All feature names returned 1. Actual checkout feature names from
`license('inuse')` were `matlab`, `symbolic_toolbox`, `optimization_toolbox` and
`simbiology`, respectively; the SimBiology process also listed
`statistics_toolbox`. No feature-name correction was needed. The latter is a
checkout observation, not an independent Statistics Toolbox smoke test.

Exact commands are in the separate [base](CZ_20260922/matlab_smoke_base.txt),
[Symbolic](CZ_20260922/matlab_smoke_symbolic.txt),
[Optimization](CZ_20260922/matlab_smoke_optimization.txt) and
[SimBiology](CZ_20260922/matlab_smoke_simbiology.txt) logs. They invoke the saved
`matlab_smoke(kind)` probe in four separate `-batch` processes. All stderr streams
were empty. The base ODE ended at `0.36787943738034734` versus `exp(-1)` =
`0.36787944117144233`, within the probe's `1e-6` tolerance.

SimBiology availability here means successful object construction only;
simulation, `.sbproj` loading/saving and a full PURE SimBiology model are
`not_tested`. The [executed static analysis](CZ_20260922/matlab_checkcode.txt)
retains two non-fatal advisories; source files were not changed to suppress them.

## Python

Both command names were tested separately. They select different runtimes.

| Item | `python` | `python3` |
| --- | --- | --- |
| First PATH executable | `C:\Users\CZ\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` | `C:\Users\CZ\AppData\Local\Python\bin\python3.exe` |
| Actual `sys.executable` | `C:\Users\CZ\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe` | `C:\Users\CZ\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| Runtime | CPython `3.11.15` | CPython `3.14.3` |
| Independent launcher version | `not_tested` | `not_tested` |
| SymPy | `not_installed` | `1.14.0`, import pass |
| NumPy | `not_installed` | `2.4.4`, import pass |
| SciPy | `not_installed` | `1.17.1`, import pass |
| pandas | `not_installed` | `3.0.3`, import pass |
| Matplotlib | `not_installed` | `3.10.9`, import pass |

Each missing `python` package was actually imported in its own process and
raised `ModuleNotFoundError` with exit code 1. Each `python3` package import
exited 0. Package availability is scoped to that runtime's current import path,
not to every interpreter on the machine. pandas was loaded from the user site
at `C:\Users\CZ\AppData\Roaming\Python\Python314\site-packages`; the other
four came from the Python 3.14 installation's `Lib\site-packages`.

Project verification uses **`python3` / CPython 3.14.3 / SymPy 1.14.0**.
No packages were installed or changed. The old observation that `python` lacks
SymPy was independently remeasured; it was not assumed from historical notes.

Evidence: [python runtime](CZ_20260922/python_runtime.txt),
[python3 runtime](CZ_20260922/python3_runtime.txt),
[failed python/SymPy import](CZ_20260922/python_sympy.txt),
[successful python3/SymPy import](CZ_20260922/python3_sympy.txt), and the separate
package logs/argument vectors in [results_inventory.json](CZ_20260922/results_inventory.json).
The [evidence note](CZ_20260922/README.md) documents the first subprocess-resolution
attempt and its correction; that superseded attempt is not used for this table.

## Wolfram

| Item | Measured value |
| --- | --- |
| Executable | `C:\Program Files\Wolfram Research\WolframScript\wolframscript.exe` |
| WolframScript CLI wrapper version | `1.13.0 for Microsoft Windows (64-bit)` |
| Actual kernel `$Version` | `14.3.0 for Microsoft Windows (64-bit) (July 8, 2025)` |
| Kernel `$SystemID` | `Windows-x86-64` |
| Symbolic command | `wolframscript -code 'Simplify[D[x^2,x]-2 x]'` |
| Symbolic result | `0`; native exit 0; stderr empty; pass |

Evidence: [CLI version](CZ_20260922/wolfram_version.txt),
[kernel version](CZ_20260922/wolfram_kernel.txt),
[SystemID](CZ_20260922/wolfram_system.txt), and
[symbolic smoke](CZ_20260922/wolfram_symbolic.txt). Wrapper and kernel versions
are deliberately separate. All five executed Wolfram commands exited 0.

## Project execution checks

The runner copied 71 tracked files under `matlab/` and `models/` into a temporary
snapshot and verified byte equality before execution. `$snapshot` below means
the path in [isolation.json](CZ_20260922/isolation.json). `$probes` means this
repository's `docs/environment/probes`; `PURE_AUDIT_SCRATCH` was set to the
snapshot for the MATLAB wrappers. The logs contain the exact absolute paths,
argument vectors, stdout, stderr and process exits.

| check | command | result | evidence |
| --- | --- | --- | --- |
| Literature MATLAB tests | `matlab -batch "addpath('$probes'); matlab_project('literature')"` → `runtests('$snapshot/matlab/tests/test_pure_literature_reference.m')` | pass: 9/9 passed, 0 failed, 0 incomplete; exit 0 | [native log](CZ_20260922/project_matlab_literature.txt) |
| Dimensionless MATLAB verification | `matlab -batch "addpath('$probes'); matlab_project('dimensionless')"` → `run('$snapshot/models/literature_reference/dimensionless/derive_dimensionless.m')` | pass: 12/12 symbolic ODE equivalences and both sets of five conservation checks; exit 0 | [native log](CZ_20260922/project_matlab_dimensionless.txt) |
| SymPy verification | `python3 -B -X utf8 $snapshot/models/literature_reference/dimensionless/derive_dimensionless.py` | pass: both sets of five conservation checks; 5×12 numerical checks; max absolute residual `2.2204460492503131e-16`; exit 0 | [native log](CZ_20260922/project_sympy.txt) |
| Wolfram verification | `wolframscript -file $snapshot/models/literature_reference/dimensionless/verify_wolfram_v2.wl` | pass: `AUDIT ALL PASS: True`; 12 symbolic ODE identities, conservation/mapping checks, 5×12 numerical checks; max residual `8.881784197001252e-16`; exit 0 | [native log](CZ_20260922/project_wolfram.txt) |

All four stderr streams were empty. The MATLAB dimensionless result was written
only in the snapshot. The canonical JSON, tracked CAS output and frozen results
were untouched. These checks establish execution of the named current sources;
the full repository release suite, full B1 figure/benchmark regeneration, and
the separate historical source-bridge/mutation audit are `not_tested` in this
environment-only task. No parameter fitting or model modification occurred.

## Known environment differences vs sean workstation

The sean column cites the unchanged historical [root record](../../environment_lock.md),
not a fresh measurement of that workstation.

| Item | sean historical record | CZ measured on 2026-09-22 |
| --- | --- | --- |
| Username | `sean` | `CZ` |
| Recorded repository path | `C:\Users\sean\Desktop\SynCell` | `C:\Users\CZ\Desktop\PURE` |
| OS version/build | recorded as `Windows 10.0.22631 x64 (win32)` | Windows 10 Pro `10.0.19045`, UBR 6466 |
| Shell | Git Bash | PowerShell Core 7.6.5 |
| MATLAB executable | `D:\Code\MATLAB\MATLAB2025b\bin\matlab.exe` | `C:\Program Files\MATLAB\R2025b\bin\matlab.exe` |
| MATLAB runtime | `25.2.0.3177638 (R2025b) Update 5` | `25.2.0.3150157 (R2025b) Update 4` |
| Four requested MATLAB capabilities | Historical record reports all four pass | All four remeasured pass here; no availability difference established |
| Python runtimes/packages | Not specified by that environment profile | Separate 3.11.15 and 3.14.3 runtimes; package availability as above |
| Wolfram | Not specified by that environment profile | CLI 1.13.0; kernel 14.3.0; execution pass |

Unspecified sean details remain unknown/`not_tested` here; absence from its
record does not mean `not_installed`. No relative quality judgment is made.

## Preservation and evidence

All 201 originally tracked files have the same SHA-256 before and after this
audit. This includes every original scientific definition, model/parameter file,
baseline result and the root sean profile. See
[initial hashes](CZ_20260922/initial_state.json),
[final audit](CZ_20260922/final_audit.json) and
[new-file manifest](CZ_20260922/artifact_manifest.json).

| Protected file | Unchanged SHA-256 |
| --- | --- |
| `environment_lock.md` | `cd69648821665da0a665cc8aea00cb9ac48435831b0639275e4883e70749ca09` |
| `models/literature_reference/model_definition.json` | `21329848a0089e45426eff6d221eed4d902646e65b83fe65137032aa3c2fdf14` |
| `models/literature_reference/parameters.json` | `5f6473b38a7d2bfdb021aa29c36c818483056bf28ef45f9d6a442530b687699c` |

The environment index was added at `docs/environment/README.md`; the root
`environment_lock.md` remains byte-identical. All additions are environment
documentation, text/JSON evidence or probe source. No binaries, caches, license
files or temporary simulation outputs are included. MATLAB's printed license
identifier is redacted before persistence.

## Status

```yaml
environment_recorded: true
base_matlab_available: true
symbolic_available: true
optimization_available: true
simbiology_available: true
python_sympy_available: true  # python3 / CPython 3.14.3 only
default_python_sympy_available: false  # python / CPython 3.11.15
wolfram_available: true
project_smoke_tests_passed: true  # four checks listed above
scientific_files_modified: false
historical_sean_record_modified: false
commit_performed: false
push_performed: false
```

Machine-readable counterpart: [status.json](CZ_20260922/status.json).
Reproduction: [probe instructions](probes/README.md).

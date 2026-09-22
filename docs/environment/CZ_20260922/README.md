# CZ environment evidence — 2026-09-22

Source commit: `444a90e4503a7b824f38bc8f5daf8551d3c3efed`.
This is an execution/capability audit, not a new scientific baseline.

| Evidence | Contents |
| --- | --- |
| `git_status.txt`, `initial_state.json` | Required initial Git commands, clean working tree, HEAD/local origin/main equality, SHA-256 of 201 original tracked files |
| `platform.txt`, `powershell_version.txt` | Whitelisted OS, CPU, RAM, shell and identity fields |
| `git_version.txt`, `where_*.txt` | Executable discovery and Git version |
| `matlab_version.txt`, `matlab_capability.txt` | MATLAB runtime/update, complete `ver` inventory, four license-feature tests and function locations |
| `matlab_checkcode.txt` | Executed MATLAB static analysis; advisory messages retained |
| `matlab_smoke_*.txt` | Independent base/Symbolic/Optimization/SimBiology native processes |
| `python*_version.txt`, `python*_runtime.txt`, `python*_<package>.txt` | Separate PATH-resolved runtimes, package versions or actual import failures |
| `wolfram_*.txt` | Distinct CLI and kernel versions, SystemID, symbolic residual |
| `project_*.txt`, `smoke_tests.txt` | Four required project checks with native exits and pass markers |
| `results_inventory.json`, `results_matlab.json`, `results_wolfram.json` | Structured commands, decoded stdout/stderr, exit codes and timing |
| `isolation.json` | Scratch location and hashes of 71 byte-identical source copies |
| `integrity_*.json`, `final_audit.json`, `final_git_audit.txt` | Original-file protection and final Git audit |
| `status.json` | Machine-readable availability and smoke-test outcome |
| `artifact_manifest.json` | SHA-256/size inventory of environment deliverables, excluding the manifest itself |

`diagnostic_initial_resolution.json` preserves the superseded first inventory
attempt. The auditor originally used bare executable names under Python 3.14;
Windows resolved both Python names to the auditor's runtime even though PATH
listed the Hermes Python first. This diagnostic is **not evidence that the
PowerShell `python` command has these packages**. Direct PowerShell checks
confirmed the discrepancy; the final inventory was rerun with explicit
PATH-resolved executable paths. The final five `python` package imports all
failed with `ModuleNotFoundError`; the five `python3` imports all succeeded.

MATLAB `checkcode` emitted two performance/unused-variable advisories (`ISCL`
in the environment probe; `NASGU` in the unchanged literature test). Its exit
was 0. These advisories are not represented as a warning-free static-analysis
result, and no scientific source was edited to suppress them.

All four native MATLAB smoke tests and all four project checks exited 0 with
their success evidence and empty stderr. The historical `environment_lock.md`
and all other original tracked files remain byte-identical. Final `git diff`
is empty because all additions are untracked under `docs/environment/`; the
separate artifact manifest enumerates them without staging anything.

Privacy: MATLAB's license identifier is replaced by `[REDACTED]` before
persistence. Only license feature names/results are retained. No product keys,
serial numbers, MAC/IP addresses, tokens, passwords or license files were
collected. These are sanitized text/JSON evidence, not raw binary console dumps.

# Multiple validated environments

The project retains two separate **execution environment records**:

| Profile | Record | Scope |
| --- | --- | --- |
| sean workstation | [Original environment_lock.md](../../environment_lock.md) | Historical B1 benchmark environment; MATLAB R2025b Update 5 |
| CZ workstation | [environment_lock_CZ.md](environment_lock_CZ.md) | Native execution and capability audit on 2026-09-22; MATLAB R2025b Update 4 |

The original root record is preserved byte for byte. These profiles describe
execution environments, not scientific model definitions. The scientific model
does not depend on a username or repository path. Each concrete result must cite
the profile that actually executed it, together with its source commit and run
evidence. Do not merge the two MATLAB update levels into one environment.

The CZ smoke checks do not replace, regenerate, or reattribute the historical B1
baseline. The sean record is historical evidence; that workstation was not
remeasured during the CZ audit. Unrecorded sean capabilities are unknown.

See [probe instructions](probes/README.md) for a repeatable, isolated audit and
[CZ evidence](CZ_20260922/README.md) for commands, outputs, exit codes and hashes.

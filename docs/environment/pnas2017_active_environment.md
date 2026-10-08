# Active PNAS verification environment
Local qualification: Python3.12.4,numpy1.26.4,scipy1.13.1,sympy1.13.1,openpyxl3.1.2.
New source/authority verifier uses Python standard library; existing reduction evidence checks use numpy/scipy/sympy.
Primary optional author ODE requires locally installed MATLAB; author settings are recorded in the benchmark config.
Historical environment_lock.md remains unchanged. No runtime/toolbox is installed by this migration.
The active CI uses Python evidence verification. A local PASS does not prove hosted CI execution.

The initial Ubuntu/pip hosted run failed the unchanged P08 eigenvalue certificate at time0.005291978735958442:
scaled error2.5477468286180927e-7 exceeded the frozen1e-7 requirement. That failed run and its artifact remain preserved.
This is not a source/kinetic change or a figure result; cross-platform equivalence is not established.
The qualification CI therefore uses Windows2022 and the exact local Windows/MKL dependency closure,
including Python3.12.4,NumPy1.26.4 py312hfd52020_0,SciPy1.13.1 py312hbb039d4_0 and MKL2023.1.0.
Exact package URLs/builds/download hashes are in .github/environments/pnas2017-windows-mkl-explicit.conda.lock
and pnas2017-windows-mkl-package-provenance.json; SymPy1.13.1 is the existing pip overlay.
No verifier threshold, historical manifest/output or source byte is changed.

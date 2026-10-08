# Active PNAS verification environment
Local qualification: Python3.12.4,numpy1.26.4,scipy1.13.1,sympy1.13.1,openpyxl3.1.2.
New source/authority verifier uses Python standard library; existing reduction evidence checks use numpy/scipy/sympy.
Primary optional author ODE requires locally installed MATLAB; author settings are recorded in the benchmark config.
Historical environment_lock.md remains unchanged. No runtime/toolbox is installed by this migration.
The active CI uses Python evidence verification. A local PASS does not prove hosted CI execution.

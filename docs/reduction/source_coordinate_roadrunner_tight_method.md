# R1 independent RoadRunner check

This method is registered before a new tight RoadRunner run. Import the
existing hash-verified author-condition compatibility SBML
`bd1029bcb876c052e5a28049ffe16050efbfb518d0fdeac4e57d91ee6fc8327b`.
The compatibility copy carries the canonical literal stoichiometry through
RoadRunner's importer and preserves the author CSV initial values and local
rate parameters. The canonical source remains the scientific authority.
Do not modify the accepted loose author RoadRunner baseline.

Require 241 floating species, 968 original reaction IDs, every canonical
stoichiometric matrix entry within `1e-12`, and every author initial
concentration within `1e-12`. Simulate the independent 241-state RoadRunner
model with CVODE stiff mode, `rtol=1e-12`, `atol=1e-14`, on the same 201
report times from 0 to 1000 s as the R1 v4r3 decisive full-source solve.
Compare all species with the already fixed per-component `E_inf<=1e-6` gate.

For a separate identical-state kinetic-law test, load a fresh RoadRunner
instance. At each of the 201 saved full-source SciPy states, set all 241
floating concentrations, read all 968 directed RoadRunner reaction rates,
align by original reaction ID, and compare with the canonical parser's rates
computed at that *same* state. Require per-component `E_inf<=1e-10` for this
engine-semantic check. A zero-initial rate uses scale 1; otherwise use the
maximum absolute parser-rate trajectory value. Preserve per-component tables,
raw logs, hashes, and the run manifest. A mismatch is investigated as an
import or semantic discrepancy, never repaired by fitting rates.

The accepted historical RoadRunner trajectory uses loose CVODE tolerances
and remains untouched. This new run is a separate R1 validation artifact.

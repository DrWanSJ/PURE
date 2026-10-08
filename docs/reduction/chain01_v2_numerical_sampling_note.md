# V2 numerical sampling convergence repair

The complete base attempt_001 is retained, including its native
NUMERICALLY_UNRESOLVED records, raw arrays, figures and independent verification.
It passed trajectory, current, inventory and source-rebuilt 70-digit residue
checks. Its sole unresolved numerical item was the change in sampled error maxima
between the frozen registered grid and its first all-midpoint refinement.

The implementation now repeats numerical midpoint refinement until the existing
`dense_grid_maxima_change_absolute = 1e-4` budget is met between successive grids.
After the first prescribed all-interval-midpoint refinement, it refines midpoint
neighborhoods of extrema and fixed-window edges, including open V1-post boundaries.
Each level and its maximum changes are saved. This is numerical resolution work;
all original registered scoring nodes remain unchanged. Scientific maxima and
acceptance statuses continue to use only that original grid. All original rates,
initial conditions, windows, scales and thresholds remain byte-bound to R0.

The final arrays are checked against primary and tighter Radau and against a
standalone analytic verifier. No resource or state clipping is performed. Earlier
unresolved attempts are never reclassified as passing evidence. This repair does
not alter V1 or claim a continuum supremum from a finite grid.

# R3 coupled trajectory timescale screen v1

This is a screen, not a QSSA acceptance criterion. Apply it to every saved
201-point full coupled trajectory in the fixed R3 grid.

At each full state, hold the 193 total-QSSA slow coordinates fixed and form
the canonical fast-row Jacobian `G_q` for the 21 selected bound states. If all
21 eigenvalues have negative real part, define `tau_fast` as the reciprocal
of the smallest magnitude negative real part. Record non-attracting modes
explicitly. Use the full source state to evaluate all 968 directed rates and
the exact dynamic slow-coordinate derivative `z'=T*S*v`.

For each slow coordinate `i`, set its fixed trajectory scale to
`max(max_t |z_i(t)|, 1e-6 uM)`. Define the local slow timescale as the minimum
over coordinates with nonzero derivative of `scale_i/|z'_i(t)|`. Then
`epsilon=tau_fast/tau_slow`. This is a conservative fastest-changing-slow-
coordinate screen; zero derivatives contribute infinite timescale. Report
`epsilon<=0.01` only as screening evidence. Neither a passed screen nor
enzyme occupancy alone validates the approximation.

Use the source-derived MetRS/GlyRS enzyme-family rows to report free and
occupied fractions and the free Gly/Met to enzyme-total ratios at every
sample. Do not substitute the frozen-only PPi/PO4 law or change the selected
fast set based on this screen.

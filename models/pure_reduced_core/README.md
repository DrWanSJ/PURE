# PURE_reduced_core (FUTURE — not yet created)

The project's own working model, derived **only** from explicit, human-approved
reduction decisions recorded under `docs/reduction/`. It must **not** be created
by ad-hoc deletion, and its canonical form will be **SBML** (not a hand-written
`rhs`).

Current state: **no model exists here.** See
`docs/reduction/candidate_core_v0.md` for a structural proposal awaiting review
and `docs/reduction/human_reduction_review.md` for the pending decisions.

When realised, `pure_reduced_core/` will hold the reduced SBML + a provenance
file mapping every reduced reaction back to the PNAS `reaction_id`s it
represents (the visualization drill-down contract).

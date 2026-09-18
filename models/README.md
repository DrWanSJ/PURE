# models/

Model definitions. A model is a numerical definition (states, reactions,
rate laws, parameters, observables) — NOT a run condition (see `configs/`).

- `literature_reference/` — `PURE_literature_reference`: frozen literal
  reproduction of R01 (Mavelli 2015). This is the B1 benchmark. Its scientific
  content is locked; see its README.
- `pure_resource_core/` — the project's own working model. Not yet implemented.
- `fixtures/` — small mathematical/software verification models (B0). Not yet
  implemented.

Never "upgrade" or extend `literature_reference` with project mechanisms; new
mechanisms belong to `pure_resource_core` only.

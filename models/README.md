# models/

Model definitions. A model is a numerical definition (states, reactions,
rate laws, parameters, observables) — NOT a run condition (see `configs/`).

- `pnas2017_full_reference/` — active Matsuura 2017 detailed **translation**
  benchmark. `original/` is byte-identical author SBML; `normalized/` is a
  verified solver-compatibility copy; `audit/` contains derived inventories.
- `pure_reduced_core/` — future project model; structural proposal only,
  pending explicit human reduction decisions.
- `literature_reference/` — frozen `Mavelli2015_coarse_reference` implementation
  in its original path, completed through old D7 RS-QSSA. Historical coarse
  comparator; no longer the active primary benchmark.
- `pure_resource_core/` — earlier project-model planning path, preserved as
  legacy context; no model implemented there.
- `fixtures/` — implemented mathematical/software verification models (B0).

Never alter either frozen reference with project mechanisms. New chemistry and
future transcription/transport extensions belong to a separately reviewed
project model, not the PNAS original import.

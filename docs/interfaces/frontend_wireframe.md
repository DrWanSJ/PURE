# Frontend Low-Fidelity Layout

This is the minimum Week 1 layout description required by the interface freeze. Detailed styling and control placement are intentionally deferred.

## Upper panel — reaction / resource-flow view

Display the PURE TX / RS / TL / EN backbone, major dynamic resource states, fixed inputs, and instantaneous reaction flows.

Default behavior:

- show major dynamic states and fixed inputs;
- show reaction direction and current flux/rate;
- hide `D_nt` and `D_TLcat` by default;
- allow accounting/context states in debug mode.

The data semantics come from [flow_contract.json](flow_contract.json).

## Lower panel — time-series view

Display simulation trajectories for selected observables/states, including at minimum:

- mRNA and protein;
- NTP / NXP;
- A;
- T / AT;
- CP / C;
- TLcat;
- optionally `V_TX`, `V_RS`, `V_TL`, `V_EN`.

## Shared interaction

Both panels use the same simulation time.

A time cursor in the lower panel determines the state/flux snapshot displayed in the upper panel.

No additional frontend architecture is frozen at G1.

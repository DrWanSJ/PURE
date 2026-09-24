# models/pnas2017_full_reference — canonical detailed reference (SBML)

The **`PNAS2017_full_reference`** identity: the literal imported Matsuura 2017
translation reaction network, treated as the scientific **source of truth**.
No scientific modification is ever applied to this model.

```
original/     immutable imported artefacts (never edited)
  fMGG_synthesis.xml        combined SBML L2V4 (241 species / 968 reactions)
  subsystems/*.xml          26 per-subsystem SBML files (Level-B modules)
  simulate/                 authors' MATLAB model + dat/ CSVs
                             (real initial values / parameters / reaction export)
normalized/   reserved for loss-free structural normalisation only
             (id sanitisation, unit-metadata completion) — NOT created yet;
             must never change reaction stoichiometry or kinetics
audit/        generated inventory + ledgers (see below)
```

- `original/` is byte-identical to the downloads in
  `references/PNAS2017_Matsuura/raw/`; provenance + SHA-256 live there.
- Generated artefacts in `audit/`: `species.csv`, `reactions.csv`,
  `parameters.csv`, `modules.csv`, `inventory_summary.json`,
  `species_properties.csv`, `reaction_balance_audit.csv`.
- **Do not simulate `original/fMGG_synthesis.xml` as-is**: its kinetic
  parameters are placeholders (`k1 = 1`). Real values are in
  `original/simulate/.../dat/`. See `docs/pnas2017/sbml_audit.md` §4.

Regenerate the audit + ledger with:
```
python scripts/parse_pnas2017_sbml.py
python scripts/build_pnas2017_ledger.py
```

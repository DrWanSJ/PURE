# Dataset S28 observable mapping
Source-only evidence, 2026-10-08. Numerical comparison and figure generation are paused by the user.
The CSV in models/pnas2017_full_reference/audit/s28_observable_mapping.csv records525 exact species headers plus three time columns.
It covers the main state/time columns, not every metadata/supplementary column.
RESOLVED_IDENTITY_ONLY establishes literal species identity; it does not establish chemical unit equivalence, condition equality or reproduction.
Fig2B has241 species,200 stored times, and functional-category metadata in B3:IH3.
Fig3A C2:II2 names241 source species; C3:II199 is197 rows of0/1 QSS flags, not concentrations.
Its exact mapping_expression remains empty/UNRESOLVED. Paper physical page4/E1339 gives the |log-slope|<0.2 persistence description,
but does not quantify the initial-state exclusion for little concentration change or fix estimator/time/zero conventions.
No resolved transform is invented. Last stored Fig3A time is784.282206133768s.
Fig5A has43 direct species and200 times; all8600 source values exactly equal the corresponding Fig2B workbook columns.
This source-data identity check is not a model-to-S28 comparison.
S28 Fig2B HU4 RRF=1600; author CSV No.228 and S27 initial concentrations D229 both give16.
Paper Fig2 caption says S27 inputs. The contradiction remains unresolved; inputs are not changed.
The seven sheets and frozen source fingerprints are recorded in s28_source_audit_20261008.json.
Supplementary metadata and derived columns retain the statuses in s28_figure_inventory.md.

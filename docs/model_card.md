# Model card — PNAS2017_full_reference
Active primary benchmark: Matsuura et al.(2017), PNAS114(8):E1336–E1344.
Reaction dynamics analysis of a reconstituted Escherichia coli protein translation system by computational modeling.
DOI10.1073/pnas.1615351114.

## Source and inventory
Canonical raw SBML: models/pnas2017_full_reference/original/fMGG_synthesis.xml.
SHA256 dc43bcec367f52105fe8d1ba328e59b064935df5faf8f880e078b212a40183df.
241 species,968 reactions and26 subsystem XMLs. Exact original species/reaction identifiers connect all derived tables to sources.

## Execution boundary
mRNA-directed translation, including aminoacylation, initiation, elongation, termination/recycling and resource regeneration.
No DNA→RNA transcription module. No GUV transport extension is present.
27 positive author initial components; author parameter CSV overlays968 k1 values plus its default sentinel.
Raw structural SBML all-one values are placeholders.
Author ODE fMGG_synthesis.m,unchanged author CSVs,ode15s,NonNegative1:241,RelTol1e-3,AbsTol1e-9,
logspace(-4,3,200) over0.0001–1000s. The nearby1e-5 comment is not executable authority.
No post-integration clipping or parameter fitting.

## Compatibility and units
3854 literal stoichiometryMath entries are normalized to identical numerical attributes in a derived compatibility copy.
The source coefficient2 for re0000000414→PO4 is retained. Source reactions and kinetics are unchanged.
SBML and author-CSV absolute chemical units remain unresolved; S28's microM declaration is recorded separately.
Successful integration does not resolve formula, charge, protonation, Mg binding, ionic strength or osmotic-pressure gaps.

## Current evidence
Source frozen,SBML audited,inventory verified,G1-PNAS PASS/CLOSED.
Preserved RoadRunner/SimBiology author-input executions are numerical-integrity evidence.
Published figure reproduction PAUSED_BY_USER / NOT_ESTABLISHED. Fig2B/5A direct identities are mapped;
RRF1600 versus author/S27 RRF16 remains contradicted. Fig3A exact QSS mapping remains UNRESOLVED.
No independent experimental validation is claimed.

## Conservation and future model
241→214 SOURCE_GENERAL exact conservation-coordinate reduction remains unchanged.
The rank177 frozen-author execution view is not SOURCE_GENERAL deletion authority.
H1–H5 and the specific R3 negative/noncompletion results remain unchanged.
PURE_reduced_core NOT_VALIDATED; all968 mechanistic reduction decisions PENDING.
96 process boxes remain governed by their existing human-review contract.

## Current commands and related records
python -B scripts/reproduce_pnas2017_reference.py --verify
python -B scripts/run_pnas2017_preflight.py --report-dir <external-new-directory>
Active registry: docs/project/benchmark_registry.md.
Current theory navigation: docs/pnas2017/theory_notes.md.
Source-coordinate evidence: docs/reduction/source_coordinate_method_v1.md and the existing certificates.
The previous coarse model card is preserved byte-for-byte at docs/legacy/mavelli2015/model_card.md.

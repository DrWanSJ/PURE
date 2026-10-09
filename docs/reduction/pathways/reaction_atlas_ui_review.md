# PURE Reaction Atlas HTML Prototype v1 — UI review

2026-10-09 · Sean · `C:\Users\sean\Desktop\GUV` · `codex/energy-cycles-v1`

Scientific status: `HTML_PROTOTYPE_READY_FOR_HUMAN_REVIEW` ·
`PHASE_A_PATHWAYS_ONLY` · `PHASE_B_NOT_AUTHORIZED`.

## Available interactions

Open `reaction_atlas_prototype.html` directly in a browser. It is one offline
file containing its data, styles and JavaScript; no server, CDN, extension or
development environment is needed to read it.

- The default Functional View has five main biochemical groups plus the
  OTHER / DEG / INACTIVE group, all 23 reviewed Level-C contexts and collapsible
  reading topics. Original multiple classifications remain visible.
- Type A summaries show unions of participating inputs and outputs, with
  “无唯一净反应”. They do not sum unrelated directions in a functional class.
  Source-derived amino acid, ATP and tRNA association groups each contain four
  GlyRS and four MetRS directions. Other topic subdivisions are explicitly
  `SUBSTEP_MAPPING_NOT_VALIDATED` and show their parent's reviewed collection.
- Select GlyRS-P01 or MetRS-P01 to see its eight original steps across
  RS_binding, RS_activation and RS_charging, without breaking the chain at a
  functional boundary. All 20 existing representative paths are accessible.
- Type B nets use exact rational arithmetic over actual reaction occurrences.
  Type C requires a productive path, identical starting and ending free enzyme,
  cancellation of its internal enzyme states and actual target production.
  Eight existing productive paths meet these structural conditions; the twelve
  incomplete entrances remain Type B. These are stoichiometric statements.
- Click a carrier state to open its parallel competition outlets and incoming
  edges. The ternary GlyRS precursor has 0194, 0196, 0197, 0206 and 0214 in a
  parallel grid. Its disabled degradation equation is initially collapsed.
  Degraded-state convergence uses `SINK_CONVERGENCE` and is distinct from
  productive rejoin. GlyRS-P02 rejoins GlyRS-P01 at the next reaction, 0205.
- Exact reverse partners and all 48 finite local return witnesses are
  expandable. They do not replace a productive main path. Reference support
  is computed from every included direction, including disabled witnesses.
- Search all 968 original reactions by ID, species, reviewed context or RFAM;
  search all 241 species and the 20 path IDs. The complete source list has 24
  cards per page. Clicking a card opens the original equation and coefficients,
  reviewed labels, carrier projection, required other reactants, released
  products, reverse partner, competing exits and downstream carrier consumers.
- The inspector provides copy-ID / copy-equation buttons and jumps to existing
  paths or functional classes. Provenance, hashes and author parameter details
  stay collapsed until requested. Copy has a selection-based fallback when
  a browser disallows the clipboard API.
- Filtering parameter-zero directions changes only displayed source lists.
  Source inventory and reconstruction coverage remain fixed. Narrow screens
  provide a classification toggle; native 200% browser page zoom was tested.

## Scope and data authority

The source inventory is **241 species / 968 unique reactions**, the searchable
index is **968 / 968**, Phase A's structural scope is **134 / 968**, and **834**
reactions remain outside that scope. Scope does not mean every reaction belongs
to one of the twenty representative productive/entrance paths. Eight Phase A
enzyme-free channels have no reconstructed carrier pathway and retain that
explicit status in the inspector.

All reaction coefficients and original equations follow canonical SBML, including
0414's `2 PO4`. All 485 directions with zero author-reference parameters are
retained and marked `REFERENCE_DISABLED`; this direction-level marker remains
distinct from the original pair-aware annotation. The six reactions with
multiple reviewed contexts retain all their contexts.

The HTML adapter reuses the published Phase A graph, paths, projections, branch
and convergence inventories, cyclic SCC evidence and boundary incidence.
Its embedded JSON is derived navigation, with original IDs, source authority,
fresh source fingerprints and inference labels retained. It does not replace
canonical SBML or the reviewed v2 annotations.

EF-Tu, MTF, ribosome, initiation, elongation, termination/recycling and energy
regeneration modules have source reaction access only. The 127 external
incidence records remain `PATHWAY_NOT_RECONSTRUCTED` /
`HUMAN_REVIEW_REQUIRED`; sharing ordinary metabolites never creates a pathway.
No Phase B pathway, QSSA, effective rate law or reduction was introduced.

## Independent acceptance results

The machine-readable record is `reaction_atlas_html_test_report.json`.

| Gate | Result | Executed evidence |
|---|---|---|
| A — source | PASS | Independently reparsed canonical SBML, constant MathML, archived author CSV and reviewed v2; checked all 241 species, 968 equations, 23 contexts, multiple labels, coefficients, exact reverse partners and directional zeros. |
| B — Phase A | PASS | Compared all 20 paths and 134 scoped IDs with published artifacts; retained projections, finite witnesses, branches, rejoins and boundary records; checked six published input hashes. |
| C — algebra | PASS | Independently summed canonical S columns for 20 paths and 48 return witnesses; checked both P01 nets, incomplete entrances, shared-suffix rejoins, multiplicities, cycle eligibility and reference support. Executed JavaScript also passed repeated-cycle, perturbed-coefficient, nonclosed-cycle and absent-target controls. |
| D — topology | PASS | Verified common-precursor outlets, inactive 0214, source carrier continuity, P02 rejoin, sink inlets and external incidence boundaries; browser confirmed parallel geometry and sink/rejoin semantics. |
| E — browser | PASS | Chrome 154.0.8037.98 with Playwright, real offline `file://` loading; 164 checks, all 20 paths clicked, all 968 source cards clicked on 41 pages, search, copy, filtering, collapse, provenance, inspector and foreign-module boundaries; no resource requests or console errors. |

The original Phase A test suite passed on temporary copies of its three generated
inputs: original Gates 1–5, ten rejected mutation controls, supplemental checks
and two reproducible builds. Its published reports were never overwritten.
All **2,333 existing tracked files** in the preservation snapshot remained
byte-identical during this acceptance run.

Two independent HTML rebuilds equaled the delivered file byte-for-byte:
`51a9d707893643fa700fadfc8904fd95a504bb20831c78cd2fa2bd1c25d8a4f5`.

Native 200% page zoom was selected in Chromium Settings using a disposable
browser profile: device pixel ratio 2, CSS viewport width 800, client/scroll
width both 800 and no CSS zoom override. A 390 × 844 viewport also had no
horizontal overflow. Screenshots of the default, pathway, branch, narrow and
native zoom views were visually inspected. They are local QA artifacts outside
the repository, not scientific evidence.

No required browser check was left unexecuted. Firefox and Safari were not
tested. Two preliminary harness failures are retained in
`reaction_atlas_html_failures.jsonl`: a string wait predicate rejected by CSP,
then CSS zoom incorrectly used as a substitute for native page zoom. The harness
was corrected and rerun; the page's security policy was not relaxed and no failed
evidence was deleted.

Reproduce from the repository root:

```powershell
python scripts/pathways/build_reaction_atlas_html.py
python scripts/pathways/verify_pathway_atlas.py
python scripts/pathways/test_reaction_atlas_html.py
```

The HTML build introduces no new build dependency. Tests use the already
available Python / NetworkX / Playwright environment and an existing Chrome
binary, with Edge or an existing Playwright Chromium as detection alternatives.
No browser is downloaded. `ATLAS_BROWSER_EXECUTABLE` can specify another
existing compatible Chromium binary. The native zoom check requires its
Chromium Settings page; a browser lacking it must be reported as unsupported,
not credited with a zoom PASS.

## Human review still required

- Confirm biochemical reading titles and the source-derived association
  grouping as suitable navigation; they are not additional reviewed scientific
  classifications. All other substep mappings remain unvalidated.
- Assess whether the representative paths, productive rejoin wording,
  degradation presentation and inferred simultaneous carrier projections are
  scientifically helpful. Their original evidence/status boundaries remain.
- Approve any future Phase B carrier handoff interpretation and subprocess
  mapping separately. This prototype provides source incidence only.
- Net cancellation, source consistency, reproducibility and browser acceptance
  provide no kinetic timescale, QSSA, flux, model-reduction or full-network
  validation claim.

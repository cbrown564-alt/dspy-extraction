# Clinical Extraction Kanban Plan

Status: active steering doc
Last refreshed: 2026-05-28 modularity completion track
Supersedes: the pre-pivot R/A backlog as active priority guidance

This board is current-first. Completed work is summarized only where it changes
active sequencing, while the remaining architecture cleanup is explicit enough
to pull through completion. The project has two active priority sets:

1. radically simplify the codebase so the decomposition program is easy to
   follow, test, and extend;
2. reorganize experiments around the May 28 component-ceiling research program,
   not around old broad-pipeline improvement loops.

Historical cards, rejected arms, and old backlog detail remain provenance in
`kanban_frozen_threads_history.md`, experiment notes, archive indexes, and run
artifacts. They are not active guidance unless this board, `current_research_program.md`,
or `component_ceiling_registry.md` explicitly promotes them.

## Current Priorities

1. **Finish the architecture/modularity cleanup before new broad model work.**
   The remaining audit gap is no longer an umbrella task: pull C12-C20 in order
   until path resolution, metrics, Gan S0, ExECT S0/S1, ExECT S5, primitive
   modules, tests, archive/delete work, and final review are complete.
2. **Keep behavior-preserving cleanup separate from research claims.** Each
   architecture card must preserve scorer, loader, split, benchmark bridge, and
   replay semantics unless a focused policy/test change explicitly says
   otherwise.
3. **ExECT component ceilings before schema stacking.** Follow
   `experiments/exect/exect_task_deep_review_20260528.md`: no-model gates,
   family payloads, raw/bridge/prompt causal splits, then isolated ceilings,
   pairwise interactions, and only then optimized S1*/S2*/S3*/S4*/S5* stacks.
4. **Gan S0 decomposition before prompt polishing.** Follow
   `experiments/gan/gan_s0_pipeline_decomposition_deep_dive_20260528.md`:
   candidate inventory, temporal anchoring, target selection, label
   construction, aggregation, unknown/no-reference policy, and evidence/schema
   diagnostics as separable components.
5. **Preserve benchmark and scorer discipline.** Gan paper comparisons use
   `gan2026_paper_reproduction`; canonical Gan metrics remain diagnostic.
   ExECT Table 1 reproduction remains blocked until CUI-aware all-family
   scoring exists. Holdout is for residual analysis, not tuning.
6. **Separate loadable config count from active experiment count.** The 59 JSON
   configs that currently load now have C4 authority classes; use those statuses
   before calling a config current, historical, rejected, blocked, or diagnostic.

## Ready

### C12 - Unified Archive Path Resolution

- **Outcome:** Active and archived configs/runs resolve through shared helpers
  in `src/clinical_extraction/paths.py`, and duplicate fallback checks are
  removed from config, registry-validation, residual-slice, and explorer catalog
  code without changing which artifacts load.
- **Dependencies:** C2-C4 complete.
- **Parallelizable:** yes, but coordinate with archive/delete work and any
  registry export changes.
- **Owner:** unassigned.
- **Validation:** `uv run pytest tests/test_experiment_configs.py tests/test_experiment_registry_validation.py -q`;
  smoke the affected explorer catalog builders if their imports change.
- **Notes:** This is the first pull from `modularity_audit_report.md`. It
  reduces path drift before files move. Do not use this card to archive or
  rename any config or run directory.

### C13 - Program Metric Surface Migration

- **Outcome:** Gan S0 program metrics and feedback metrics live behind
  Gan-owned scoring/metric modules, ExECT S0/S1 field-family metrics live behind
  ExECT-owned scoring/metric modules, and legacy imports from program files keep
  working during the transition.
- **Dependencies:** C12 helpful but not required; scorer policy documents remain
  frozen unless a separate scorer-semantics card is opened.
- **Parallelizable:** after C12; coordinate with C14 and C15 because all three
  touch program imports.
- **Owner:** unassigned.
- **Validation:** `uv run pytest tests/test_gan_s0_program.py tests/test_gan_scoring.py tests/test_gan_paper_reproduction_scoring.py tests/test_exect_s0_s1_program.py tests/test_exect_scoring.py -q`.
- **Notes:** This is a movement-only card. The metric functions should produce
  byte-for-byte equivalent results on existing fixtures, and reports must still
  label canonical versus paper-reproduction Gan scorer modes explicitly.

### C14 - Gan S0 Program Package Decomposition

- **Outcome:** `programs/gan_frequency_s0.py` becomes an import-compatible
  facade over focused `clinical_extraction.gan.s0` modules for signatures,
  modules, optimizer setup, variant routing, candidate inventory, target
  selection, label construction, prediction bridge, evidence guards, and
  artifact assembly.
- **Dependencies:** C6/C7/C9 stage surfaces complete; C13 preferred so metrics
  do not move at the same time as module construction.
- **Parallelizable:** no for the main extraction; small follow-up test moves can
  run after public surfaces land.
- **Owner:** unassigned.
- **Validation:** `uv run pytest tests/test_gan_s0_program.py tests/test_gan_temporal_candidates.py tests/test_gan_slot_payload.py tests/test_gan_s0_stage_surfaces.py tests/test_gan_scoring.py tests/test_gan_paper_reproduction_scoring.py -q`;
  add fixture-level parity for builder-gap v1 and D1 v1.2b on fixed record IDs.
- **Notes:** Preserve existing class/function names registered by configs and
  historical artifacts. Do not collapse `unknown` and
  `no seizure frequency reference` outside `gan2026_paper_reproduction`.

### C15 - ExECT S0/S1 Program Package Decomposition

- **Outcome:** `programs/exect_s0_s1.py` becomes an import-compatible facade
  over focused `clinical_extraction.exect.s0_s1` modules for signatures,
  program modules, prompt/repair routing, prediction artifact assembly, and
  raw/bridge/final S1 boundary contracts.
- **Dependencies:** C7 S1 boundary surfaces complete; C13 preferred so metrics
  do not move with prediction code.
- **Parallelizable:** no for the main extraction; can proceed independently of
  C14 if imports are kept stable.
- **Owner:** unassigned.
- **Validation:** `uv run pytest tests/test_exect_s0_s1_program.py tests/test_exect_s1_boundary_surfaces.py tests/test_exect_diagnosis_primitives.py tests/test_exect_medication_primitives.py tests/test_exect_scoring.py tests/test_exect_loader.py -q`;
  parity fixtures for diagnosis specificity collapse, seizure-type co-listing,
  brand medication normalization, and current-Rx augmentation.
- **Notes:** Keep ExECT JSON diagnosis/seizure-type source policy, certainty
  threshold, medication CUIPhrase preference, and specificity collapse unchanged
  unless a scorer-policy card changes them explicitly.

### C16 - ExECT S5 Core Split From S4

- **Outcome:** S5 operational stack signatures, modules, medication guards,
  frequency verifier wiring, and stack metadata are separated from S4 family
  component logic while existing S4/S5 config variants remain loadable.
- **Dependencies:** C9 S5 stack surface complete; C13 preferred.
- **Parallelizable:** after C13; coordinate with E7 and any medication/frequency
  isolated component work.
- **Owner:** unassigned.
- **Validation:** `uv run pytest tests/test_exect_s4_program.py tests/test_exect_s5_scoring.py tests/test_exect_s5_frequency_verifier.py -q`;
  parity on the current S5 v2b artifact shape before any new component run.
- **Notes:** S5 v2b remains an operational stacked baseline, not an isolated
  family ceiling. Do not use this split to report a new component result.

### C11 - Stage-Level Test Surface Split

- **Outcome:** Monolithic private-helper tests are gradually replaced by public
  stage-level characterization tests for candidate inventory, target selection,
  label construction, bridge policy, evidence guards, and artifact assembly.
- **Dependencies:** C6, C7, C8, and C9 stage surfaces should exist before
  retiring old helper assertions; C14-C17 should land before the largest
  private-helper assertions are removed.
- **Parallelizable:** after each extracted surface exists.
- **Owner:** unassigned.
- **Validation:** Existing monolithic tests remain as parity nets until the
  replacement stage tests cover the same semantics; full focused domain suites
  pass before any helper assertions are removed.
- **Notes:** Split tests last. The goal is to make future cleanup safer, not to
  lose regression coverage during extraction. 2026-05-28 first slice added
  public stage-level characterization for ExECT S1 boundary surfaces and Gan
  S0 routing/artifact/evidence guards, and moved S5 frequency-verifier
  assertions onto the public `exect.s5_stack` surface. No monolithic parity
  assertions were retired. 2026-05-28 follow-up slice added public Gan S0
  candidate-inventory and target-selection/label-construction surfaces, with
  report builders delegating through those surfaces.

### X3 - Registry And Atlas Refresh

- **Outcome:** Regenerated registry-derived navigation only after May 28
  decisions and component-ceiling statuses are encoded.
- **Dependencies:** X1 complete; C10 complete enough to prevent stale generated
  navigation from hiding C4 status classes or X1 caveats.
- **Parallelizable:** yes for doc-only refresh; coordinate if regenerated
  registry/atlas material touches shared navigation files.
- **Owner:** unassigned.
- **Validation:** Generated artifacts explicitly state they postdate R11-R15,
  X1, C10, and the May 28 component pivot.
- **Notes:** Use the retained C10 manifest and explicit Gan scorer-mode
  surfaces; do not revive the archived pre-pivot atlas as current authority.

### E5 - Medication Lifecycle Target Policy Decision

- **Outcome:** A short decision note states whether medication lifecycle /
  temporality is benchmark-facing, clinical-diagnostic, deferred, or blocked,
  with the gold/proxy source and scoring caveats explicit.
- **Dependencies:** E3.
- **Parallelizable:** yes; no model calls.
- **Owner:** unassigned.
- **Validation:** Decision cites the E3 lifecycle inventory counts, ExECT gold
  audit prescription-temporality caveat, and `deterministic_scorer_semantics.md`;
  no scorer or loader change occurs unless a follow-up card is created.
- **Notes:** ExECT prescription JSON has no native temporality column. Do not
  treat planned/previous/taper/current status as a headline metric until this
  target policy exists.

### E6 - Medication Isolated Current-Rx Ceiling Probe

- **Outcome:** A preregistered isolated medication component probe using the E3
  annotation-current-Rx payload, reporting medication precision, recall, F1,
  and residual categories without lifecycle scoring.
- **Dependencies:** E3; E5 only if the probe includes lifecycle labels.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Compare the isolated medication component against existing S1
  and S5 medication surfaces on validation; report dataset split, model/provider
  if any, scorer mode, bridge/normalization policy, and evidence diagnostics.
- **Notes:** This is the current-Rx ceiling path. Lifecycle rows remain
  diagnostic unless E5 explicitly promotes a target.

### E7 - Medication Stack-Interference Probe

- **Outcome:** A no-model or capped-run analysis attributes S5 medication loss
  to over-emission, non-ASM leakage, historical/planned/taper evidence, dose-only
  rows, or cross-family prompt interference using the E3 payload as the audit
  surface.
- **Dependencies:** E3; E6 helpful if an isolated ceiling is available.
- **Parallelizable:** after E3; coordinate with the S5 stack surface if files
  move.
- **Owner:** unassigned.
- **Validation:** Report S1 versus S5 medication deltas, row-level interference
  categories, and whether an AM guard, payload routing, or prompt isolation is
  the next appropriate mechanism.
- **Notes:** Do not bundle temporality recovery into broad S5 prompts. The goal
  is to explain medication degradation before changing the stack.

### E8 - Family-Span Cap-Slice Prompt Comparison

- **Outcome:** A preregistered cap-slice comparison of full-note prompting versus
  E4 family-span prompting for a narrow target such as S1+investigation or one
  selected family.
- **Dependencies:** E4.
- **Parallelizable:** yes, but keep one family/span surface fixed per run.
- **Owner:** unassigned.
- **Validation:** Report full-note versus family-span prompt substrate, dataset
  split, cap size, model/provider, scorer mode, family F1/precision/recall,
  gold evidence coverage, false-family span counts, and evidence diagnostics.
- **Notes:** This tests typed document geometry. It does not promote the old
  rejected section-aware routing arm unless recall is preserved and the
  preregistered comparison shows a real precision or cost benefit.

### E10 - ExECT Frequency Candidate Selection Split

- **Outcome:** A preregistered component probe separates the completed
  frequency event/rate payload from candidate adjudication and benchmark-label
  construction.
- **Dependencies:** C5 and C8 complete.
- **Parallelizable:** yes, if scorer and bridge semantics are frozen.
- **Owner:** unassigned.
- **Validation:** Compare broad payload, high-precision payload, S4/S5 frequency
  surfaces, and any adjudicator arm on validation. Report split, model/provider
  if any, scorer mode, precision/recall/F1, extra-candidate strata, and whether
  errors are payload coverage, target selection, or label construction.
- **Notes:** C5/C8 cleared recall but not precision. Do not treat the 43/43
  payload coverage result as a frequency ceiling.

## Blocked

### B1 - ExECT Optimized Stack Reconstruction

- **Outcome:** S1*/S2*/S3*/S4*/S5* built from optimized components rather than
  broad prompt ladders.
- **Blocked by:** isolated ceiling reports and pairwise interaction evidence,
  not substrates alone.
- **Parallelizable:** no.
- **Owner:** unassigned.
- **Validation:** Per-family deltas from isolated ceilings, pairwise
  interaction losses, pooled micro F1 as secondary, and holdout residual audit.
- **Notes:** Do not start this until component ceilings exist.
  E3/E4 provide substrates only; E5-E10 and pairwise interaction work are still
  needed before an optimized ExECT stack claim.

### B2 - ExECT Table 1 Benchmark Reproduction

- **Outcome:** Explicit CUI-aware all-family scorer path and benchmark
  reproduction report.
- **Blocked by:** CUI-aware scorer design and replay.
- **Parallelizable:** yes once scorer scope is defined.
- **Owner:** unassigned.
- **Validation:** Report distinguishes published-benchmark metrics from project
  diagnostic field-family metrics.
- **Notes:** Keep separate from S1/S5 local claims.

### B3 - Gan Real-Note Reporting

- **Outcome:** Preregistered protocol for real-note Gan reporting.
- **Blocked by:** dataset access, approval, and reporting protocol.
- **Parallelizable:** after access.
- **Owner:** unassigned.
- **Validation:** Protocol states split, scorer, normalization rules, and what
  can be compared to synthetic validation.

## Backlog

### C17 - ExECT Primitive Family Module Split

- **Outcome:** `src/clinical_extraction/exect/primitives.py` is split into
  family-owned primitive/bridge modules for diagnosis, seizure type,
  medication, and frequency while primitive IDs, registry metadata, and
  compatibility imports remain stable.
- **Dependencies:** C15 preferred so S0/S1 bridge imports settle first; C8
  frequency payload complete.
- **Parallelizable:** after C15; frequency-only cleanup can proceed in parallel
  if it does not change primitive registry contracts.
- **Owner:** unassigned.
- **Validation:** `uv run pytest tests/test_exect_diagnosis_primitives.py tests/test_exect_medication_primitives.py tests/test_exect_frequency_primitives.py tests/test_exect_frequency_slot_payload.py -q`;
  `uv run python scripts/validate_primitives.py --errors-only`.
- **Notes:** This is a modularity cleanup, not a policy change. Preserve raw
  values, normalized values, evidence, flags, and benchmark bridge behavior.

### C18 - Monolithic Test Retirement

- **Outcome:** Large parity-net tests are split or reduced only after public
  stage-level tests cover the same behavior; private-helper assertions that
  block module extraction are retired or moved behind public surfaces.
- **Dependencies:** C14, C15, C16, and C17 complete enough that public module
  surfaces exist.
- **Parallelizable:** after each extracted module has stage coverage.
- **Owner:** unassigned.
- **Validation:** Focused Gan, ExECT S0/S1, ExECT S4/S5, scorer, loader, and
  primitive suites pass; run the full suite before declaring this card complete.
- **Notes:** Keep old tests as parity nets until replacement coverage is real.
  This card completes the test-isolation recommendation from
  `modularity_audit_report.md`.

### C19 - Archive And Delete Obsolete Program Surfaces

- **Outcome:** Rejected and historical configs/scripts/branches identified by
  the C2 inventory are archived, removed, or wrapped behind explicit replay
  paths, and generated registry/navigation outputs no longer present stale arms
  as current work.
- **Dependencies:** C12 path resolution; C14-C18 behavior-preserving extraction;
  X3 registry/atlas refresh should consume the same status classes.
- **Parallelizable:** after C18 for code deletion; doc-only archive maps can be
  prepared earlier.
- **Owner:** unassigned.
- **Validation:** `uv run pytest tests/test_program_variant_registry.py tests/test_experiment_configs.py tests/test_experiment_registry_validation.py -q`;
  `uv run python scripts/validate_experiment_taxonomy.py --errors-only` or
  document any remaining provenance gaps.
- **Notes:** Do not delete any path needed to trace active metrics to run ID,
  config, model/provider, split, scorer mode, and caveat. Archive by decision
  boundary, not age.

### C20 - Modularity Completion Review

- **Outcome:** A final review updates the architecture audit status with what
  was addressed, what remains intentionally retained, file-size/module boundary
  evidence, validation commands, and any residual risk accepted for
  reproducibility.
- **Dependencies:** C12-C19 complete.
- **Parallelizable:** no.
- **Owner:** unassigned.
- **Validation:** Re-run the focused architecture validation matrix from C12-C19
  plus the full test suite if feasible; update docs only after the result is
  known.
- **Notes:** Completion means the P1 monolith risks are closed or explicitly
  reclassified with rationale. It does not require deleting replay-provenance
  contracts that are still needed for historical runs.

### X2 - Pairwise ExECT Interaction Plan

- **Outcome:** A preregistered plan for diagnosis+seizure type,
  seizure type+frequency, medication+temporality, investigation+comorbidity,
  and other high-value pairwise interactions.
- **Dependencies:** initial component ceiling reports; E5 before treating
  medication+temporality as a scored pair.
- **Parallelizable:** after E1-E4.
- **Owner:** unassigned.
- **Validation:** Each pair has hypothesis, support counts, primary family
  metrics, interference criteria, and stop rule.

### E9 - Family-Span Promotion Or Rejection Decision

- **Outcome:** A decision note classifies family-span prompting as promoted,
  diagnostic-only, rejected arm, or still mechanism-open.
- **Dependencies:** E8.
- **Parallelizable:** after E8.
- **Owner:** unassigned.
- **Validation:** Decision cites the E4 no-model coverage audit, E8 cap-slice
  results, full-note baseline, false-family span counts, and recall/cost
  tradeoffs.
- **Notes:** Promotion requires evidence against a full-note baseline. Existence
  of `exect.sections.family_spans.v1` is substrate evidence only.

### G4 - Gan Explicit Reason-Code Adjudicator

- **Outcome:** A preregistered Gan S0 adjudicator that emits explicit
  target-selection reason codes, selected-candidate references, and exact label
  construction inputs separately from the final benchmark-facing label.
- **Dependencies:** G2 model-arm comparison complete; G3 unknown/no-reference
  policy probe complete.
- **Parallelizable:** yes for same-slice adjudicator design from G3 outputs;
  implementation should stay single-threaded with any Gan S0 artifact/metadata
  contract changes.
- **Owner:** unassigned.
- **Validation:** Compare against free adjudication, candidate-constrained
  adjudication, and the seeded answer-options selector surrogate on the same
  validation slice first; report both `gan2026_paper_reproduction` and
  canonical scorer views, selected reason-code distributions, unsupported
  candidate cases, and whether errors are target-selection, label-construction,
  policy, or evidence failures.
- **Notes:** This is the explicit follow-up to the G2 seeded
  reason-code/answer-options surrogate. G3 has pinned down policy-isolation
  cues; do not promote or full-validate a new adjudicator until it beats the
  same-slice baselines under both scorer views.

### G5 - Gan Paper-Scorer Rescore Pack

- **Outcome:** Current promoted Gan synthetic baselines are rescored under
  `gan2026_paper_reproduction` before any benchmark-comparison table or paper
  claim uses them.
- **Dependencies:** Current promoted Gan baseline artifacts remain available.
- **Parallelizable:** yes; no model calls unless a missing baseline must be
  regenerated by a separate preregistered card.
- **Owner:** unassigned.
- **Validation:** Report canonical versus paper-reproduction scorer views,
  repair/range/tolerance options, dataset split, config/run IDs, and the
  synthetic-only caveat.
- **Notes:** This routes the registry paper-comparison action. It does not
  unblock Real(300) or Real(150) reporting by itself.

### E11 - ExECT Holdout Residual Attribution

- **Outcome:** A residual-analysis report attributes S1 and S5 holdout drops to
  raw extraction, benchmark bridges, prompt policy, stack interference, family
  support, or scorer/label-policy effects without tuning from holdout.
- **Dependencies:** E2 complete; E10, E6, and E7 helpful where frequency or
  medication residuals dominate.
- **Parallelizable:** yes for artifact replay and no-model error bucketing.
- **Owner:** unassigned.
- **Validation:** Report validation versus test split, family-level metrics,
  residual categories, raw/bridge/prompt/stack attribution where available, and
  explicit confirmation that no scorer, loader, split, bridge, or prompt was
  tuned from holdout.
- **Notes:** This routes the registry holdout-transfer action. Findings can
  motivate validation-only component probes, not holdout-driven prompt edits.

### E12 - Investigation Isolated Ceiling Confirmation

- **Outcome:** A narrow isolated investigation-family probe or decision note
  states whether broad-stack investigation performance is enough to classify the
  component as near ceiling, still diagnostic, or blocked by family-contract
  ambiguity.
- **Dependencies:** Initial component ceiling reports; X2 helpful if
  investigation is tested as part of an interaction pair.
- **Parallelizable:** yes, if scorer and bridge semantics stay frozen.
- **Owner:** unassigned.
- **Validation:** Report support counts, validation split, model/provider if
  any, scorer mode, precision/recall/F1, modality/result normalization policy,
  and any holdout residual caveat as diagnostic only.
- **Notes:** This routes the registry investigation action. Broad-stack
  stability is not enough by itself to call the investigation component solved.

## Done Or Frozen

The old R/A backlog is frozen as active guidance. Keep its evidence, but do not
pull from it directly without translating the work into one of the current
cards above. Detailed completion notes live in linked reports, generated
artifacts, and git history; this section only keeps the steering implications.

| Evidence | Current interpretation |
| --- | --- |
| C1-C4 architecture and registry cleanup, 2026-05-28 | The cleanup map, typed program variant registry, and active-status review exist. The live config tree remains loadable, but active authority is now separated from replay/provenance rows. |
| C10 registry provenance and Gan analysis script cleanup, 2026-05-28 | Historical cap-25 registry backfill specs moved to `docs/archive/experiments/synthesis/pre_component_pivot/hybrid_cap25_registry_backfill_manifest_20260528.json`; `scripts/backfill_hybrid_cap25_registry.py` now loads retained provenance instead of carrying static rows; `scripts/analyze_gan_frequency_run.py` exposes explicit canonical versus paper-reproduction scorer mode and paper options. Focused C10 export and Gan scorer tests passed. |
| C5/C8 ExECT frequency substrate, 2026-05-28 | Broad frequency payload covers 43/43 validation gold labels and 24/24 gold-bearing documents, but broad precision is 22.2%; selection/adjudication is the active problem. |
| C6/C7/C9 boundary splits, 2026-05-28 | Gan S0 routing/bridge, ExECT S1 boundary metadata, and ExECT S5 stack surfaces were extracted as behavior-preserving architecture work. Use them for stage attribution; do not infer new metric claims. |
| E2 S1 raw/bridge/prompt split, 2026-05-28 | S1 validation strength depends heavily on benchmark bridges; holdout transfer drops keep diagnosis and seizure-type mechanisms open. |
| E3 medication payload, 2026-05-28 | Annotation-derived current-Rx payload reproduces 47/47 validation medication gold labels; lifecycle/temporality remains diagnostic or deferred until E5 decides the target policy. |
| E4 family-span payload, 2026-05-28 | `exect.sections.family_spans.v1` gives high evidence coverage and a cap-slice substrate; it is not promoted over full-note prompting until E8/E9. |
| G1/G2 Gan target split evidence, 2026-05-28 | Restrained high-recall deterministic candidates now cover 278/299 exact gold labels in G1, 292/299 Purist-equivalent labels, and 295/299 Pragmatic-equivalent labels; the G2 candidate-constrained arm has 299/299 selectable candidate support with no invalid candidate labels. Keep the remaining exact misses as a parser/adjudicator queue rather than forcing brittle 100% deterministic exact recall. |
| G3 Gan unknown vs no-reference policy probe, 2026-05-28 | Post-adjudication rules simulated on G2 predictions shows that checking option ambiguity flags successfully isolates policy choices (e.g. abstaining on uncertain denominators), trading off category accuracy for conservative precision. |
| X1 component ceiling registry backfill, 2026-05-28 | `component_ceiling_registry.md` now preserves row-level model/provider, split, scorer, config/run or artifact, bridge/normalization policy, classification, and caveat metadata for promoted baselines, diagnostic substrates, rejected arms, active risks, and blocked benchmark claims. |
| Gan rejected or blocked arms, 2026-05-28 | CLINES-style entity-first prompting, self-consistency, broad relative-anchor guardrails, and Qwen GEPA without compact-delta clearance are not active pulls. |
| ExECT S5 v2b and holdout report | S5 v2b remains the operational stacked baseline. Holdout drops are residual-analysis triggers, not tuning targets or component-ceiling evidence. |

## Dependency Notes

- C1-C4 are complete enough to guide cleanup, but the modularity review shows
  the core program monoliths are still open. Treat C12-C20 as the active
  architecture completion lane until C20 reclassifies or closes the P1 risks.
- C12 should land before archive moves or path-sensitive cleanup. It centralizes
  config/run fallback behavior so future file movement does not create path
  drift across loaders, registry validation, residual analysis, and explorer
  catalog scripts.
- C13 should happen before large program splits. Moving metric surfaces first
  reduces churn when C14, C15, and C16 relocate signatures, modules, optimizers,
  and prediction artifact code.
- C14 and C15 are the two largest behavior-preserving program decompositions.
  They can be done in either order after C13, but each should be single-threaded
  while imports and compatibility wrappers are moving.
- C16 can proceed after C13 and the existing C9 S5 stack surface, but it should
  coordinate with ExECT medication/frequency follow-ups so operational-stack
  cleanup is not mistaken for isolated component progress.
- C17 follows C15 for most ExECT family primitive movement; frequency-only work
  can proceed earlier only if primitive IDs and registry contracts stay stable.
- C18 is intentionally late. Monolithic tests are still useful parity nets until
  C14-C17 expose public module surfaces with replacement characterization tests.
- C19 is the first broad archive/delete pass. It depends on C12 path helpers and
  enough C14-C18 extraction to avoid deleting code that still carries active
  behavior.
- C20 is the completion gate: rerun a strict architecture review and update the
  audit status only after the code, tests, registry, and archive/delete path are
  actually settled.
- The typed program variant registry preserves loadable contracts and classifies
  registry/config rows as current-authority, replay/provenance, historical,
  rejected, blocked, or diagnostic.
- C6-C9 completed the first behavior-preserving architecture extractions: Gan
  S0 routing/bridge surfaces, ExECT S1 boundary metadata, ExECT frequency
  payload/bridge surfaces, and the ExECT S5 stack boundary. These are inputs to
  C14-C18, not proof that the monolith problem is finished.
- E2, E3, and E4 are complete as no-model/artifact-only ExECT decomposition
  audits, and G1 is complete as a no-model Gan candidate-inventory coverage
  report. ExECT frequency candidate-selection design can now consume C8; E3/E4
  follow-ups should use the completed substrates for isolated medication or
  family-span comparison plans, not broad-stack model runs.
- G3 is complete as a post-adjudication policy probe; use its ambiguity-flag
  findings to keep unknown/no-reference policy separate from new adjudicator
  prompt design.
- G4 is the explicit reason-code adjudicator follow-up, but it should consume
  G3 policy outputs rather than baking unknown/no-reference decisions into a new
  prompt surface.
- G5 is the registry-routed paper-scorer rescore pack; it is only needed before
  benchmark-comparison tables or paper claims, and it does not create Real(300)
  or Real(150) evidence.
- E5 is the policy gate before medication lifecycle/temporality can become a
  scored target. E6 is the current-Rx ceiling path; E7 is the stack-interference
  path. E8 tests the family-span mechanism, and E9 is the promotion/rejection
  decision after that comparison.
- E11 routes holdout residual attribution without tuning from holdout. E12
  routes the registry's unproven investigation-near-ceiling action.
- B1 is blocked until component substrates and isolated ceilings exist,
  including medication current-Rx and family-span follow-ups where they affect
  the optimized stack.
- C11 has started but is not done. The first replacement-test slice covers
  ExECT S1 boundary metadata, Gan S0 bridge/evidence guards, and S5
  frequency-verifier stack surfaces; a follow-up slice covers Gan S0 candidate
  inventory, target selection, and label construction. No monolithic parity
  assertions have been retired yet.
- C10 completed the provenance cleanup needed before generated registry
  navigation is refreshed: historical cap-slice backfill rows are retained in
  an archive manifest, and Gan analysis scripts now expose scorer mode and
  paper-reproduction options explicitly.
- X3 is unblocked by X1 and C10, but final registry/atlas navigation should be
  coordinated with C19 so archived or deleted surfaces do not immediately make
  regenerated navigation stale.

## Parallelization Opportunities

- **Safe now:** C12 unified path resolution; C13 metric-surface planning and
  focused parity tests; X3 doc-only prep if it does not regenerate stale
  navigation; G5 paper-scorer rescore if needed for a paper table; E5
  medication lifecycle policy decision. These should preserve scorer, loader,
  split, and benchmark bridge semantics.
- **After C13:** C14 Gan S0 package decomposition, C15 ExECT S0/S1 package
  decomposition, and C16 ExECT S5 split are all eligible, but each should be
  single-threaded within its own file cluster.
- **After C14-C17:** C18 monolithic test retirement can proceed stage by stage.
  C19 archive/delete follows once path resolution and replacement surfaces make
  replay provenance safe.
- **Research lane still safe, but secondary:** E6, E8, E10, G4, and E11 remain
  valid work, but new broad model/prompt changes should wait until the current
  architecture lane is no longer the bottleneck.
- **Single-threaded or carefully sequenced:** C14-C17 import-moving refactors,
  C19 archive/delete, registry/archive regeneration in X3, and any change to
  scorer, loader, split, benchmark bridge, or shared primitive contracts.
- **Blocked together:** B1 waits on ExECT component ceilings.
- **Model-call gated:** E3/E4 audits are complete, so any related model run now
  needs a preregistered comparison against the full-note/current-stack baseline;
  any Gan selector full-validation run should wait until G3 policy isolation
  explains the remaining unknown/no-reference and LLM-option tradeoffs. G4
  should begin as a same-slice adjudicator comparison, not a full-validation
  promotion run.

## Recommended Next Pull

1. **C12 - Unified Archive Path Resolution** is the next codebase-simplification
   pull. It is small, behavior-preserving, and reduces risk for every later
   archive/delete or program split.
2. **C13 - Program Metric Surface Migration** should follow so metrics are
   anchored in domain scoring modules before the big program files move.
3. **C14 - Gan S0 Program Package Decomposition** should then shrink the largest
   remaining monolith behind stable public imports.
4. **C15 - ExECT S0/S1 Program Package Decomposition** should split raw
   extraction, prompt/repair routing, and bridge/final artifact assembly.
5. **C16 - ExECT S5 Core Split From S4** should separate the operational stack
   from S4 component logic before more stack-interference work.
6. **C17 - ExECT Primitive Family Module Split** should retire the remaining
   over-bundled primitive module while preserving registry IDs.
7. **C18 - Monolithic Test Retirement** should remove private-helper coupling
   only after the replacement public surfaces are covered.
8. **C19 - Archive And Delete Obsolete Program Surfaces** should use C2/C4
   status classes and C12 path helpers to move stale arms without losing replay
   provenance.
9. **C20 - Modularity Completion Review** should close the architecture lane by
   updating audit status, residual risks, and validation evidence.
10. **Then resume research-lane pulls** such as X3, G5, E5, E6, E10, and E8
    according to paper/experiment need.

## Standing Guardrails

- Do not silently change scorer semantics; update tests and documentation when
  semantics change.
- Do not compare metrics across changed scorer modes unless the report says so
  explicitly.
- Use `gan2026_paper_reproduction` for Gan paper-comparison tables.
- Keep Gan canonical `unknown` and `no seizure frequency reference` distinct
  except inside explicitly named paper-reproduction scorer views.
- Treat ExECT clean ladder results as diagnostic baselines, not component
  ceilings.
- Do not describe `configs/experiments` loadability counts as active experiment
  counts; use the C4 authority classes in the generated registry report.
- Treat rejected arms as rejected arms unless a mechanism-level review closes
  the mechanism.
- Holdout metrics trigger residual analysis only; do not tune from holdout.
- Prefer typed payloads, primitives, bridges, and scorer policies over prompt
  bloat and broad mode flags.

# Clinical Extraction Kanban Plan

Status: active steering doc
Last refreshed: 2026-05-28 evening refocus
Supersedes: the pre-pivot R/A backlog as active priority guidance

This board is intentionally small. The project has two active priority sets:

1. radically simplify the codebase so the decomposition program is easy to
   follow, test, and extend;
2. reorganize experiments around the May 28 component-ceiling research program,
   not around old broad-pipeline improvement loops.

Historical cards, rejected arms, and old backlog detail remain provenance in
`kanban_frozen_threads_history.md`, experiment notes, archive indexes, and run
artifacts. They are not active guidance unless this board, `current_research_program.md`,
or `component_ceiling_registry.md` explicitly promotes them.

## Current Priorities

1. **Codebase simplification before more broad model work.** Use
   `thermo-nuclear-code-quality-review` to remove bloat, split bundled program
   logic into real domain concepts, and make Gan/ExECT decomposition stages
   inspectable without changing scorer, loader, split, or benchmark semantics.
2. **ExECT component ceilings before schema stacking.** Follow
   `experiments/exect/exect_task_deep_review_20260528.md`: no-model gates,
   family payloads, raw/bridge/prompt causal splits, then isolated ceilings,
   pairwise interactions, and only then optimized S1*/S2*/S3*/S4*/S5* stacks.
3. **Gan S0 decomposition before prompt polishing.** Follow
   `experiments/gan/gan_s0_pipeline_decomposition_deep_dive_20260528.md`:
   candidate inventory, temporal anchoring, target selection, label
   construction, aggregation, unknown/no-reference policy, and evidence/schema
   diagnostics as separable components.
4. **Preserve benchmark and scorer discipline.** Gan paper comparisons use
   `gan2026_paper_reproduction`; canonical Gan metrics remain diagnostic.
   ExECT Table 1 reproduction remains blocked until CUI-aware all-family
   scoring exists. Holdout is for residual analysis, not tuning.
5. **Separate loadable config count from active experiment count.** The 59 JSON
   configs that currently load now have C4 authority classes; use those statuses
   before calling a config current, historical, rejected, blocked, or diagnostic.

## Ready

### C9 - ExECT S5 Stack Boundary Split

- **Outcome:** S5 operational stack composition is separated from S4 family
  program logic, with medication guard and frequency verifier behavior callable
  as explicit bridge/verifier components.
- **Dependencies:** C2, C3, C4; C7 and C8 are helpful if shared bridge surfaces
  move first.
- **Parallelizable:** no; keep single-threaded because it touches stacked
  baseline reproducibility.
- **Owner:** unassigned.
- **Validation:** Parity on the current S5 v2b full-validation artifact shape;
  `uv run pytest tests/test_exect_s4_program.py tests/test_exect_s5_scoring.py
  tests/test_exect_s5_frequency_verifier.py -q`.
- **Notes:** Do not report S5 stack deltas as isolated component ceilings, and
  keep medication temporality diagnostic unless the gold policy changes.

### C10 - Registry Provenance And Analysis Script Cleanup

- **Outcome:** Hard-coded historical registry/backfill knowledge is either
  moved into retained provenance manifests or replaced by registry-generated
  views; retained Gan analysis scripts expose scorer mode explicitly.
- **Dependencies:** C2, C3, C4; X1 for component-ceiling status backfill where
  registry exports would otherwise be stale.
- **Parallelizable:** after X1 for export regeneration; scorer-flag cleanup can
  start independently.
- **Owner:** unassigned.
- **Validation:** `uv run pytest tests/test_export_registry_matrix.py
  tests/test_export_research_atlas.py -q`; `uv run pytest
  tests/test_analyze_gan_frequency_run.py
  tests/test_gan_paper_reproduction_scoring.py -q`.
- **Notes:** Archive run IDs, decision documents, and scorer caveats before
  deleting generated or hard-coded registry material.

### C11 - Stage-Level Test Surface Split

- **Outcome:** Monolithic private-helper tests are gradually replaced by public
  stage-level characterization tests for candidate inventory, target selection,
  label construction, bridge policy, evidence guards, and artifact assembly.
- **Dependencies:** C6, C7, C8, and C9 stage surfaces should exist before
  retiring old helper assertions.
- **Parallelizable:** after each extracted surface exists.
- **Owner:** unassigned.
- **Validation:** Existing monolithic tests remain as parity nets until the
  replacement stage tests cover the same semantics; full focused domain suites
  pass before any helper assertions are removed.
- **Notes:** Split tests last. The goal is to make future cleanup safer, not to
  lose regression coverage during extraction.

### E3 - Medication Current-Rx And Lifecycle Payload

- **Outcome:** A medication payload that separates annotated current medication
  extraction from lifecycle/temporality reasoning.
- **Dependencies:** none.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Reproduce S1 medication strength from the payload; quantify
  non-ASM, historical, planned, taper, dose-only, and prescription-list cases;
  decide whether temporality is headline, diagnostic, deferred, or blocked.
- **Notes:** Do not bundle temporality recovery back into broad S5 prompts before
  this target is defined.

### E4 - Family-Span Payload

- **Outcome:** `exect.sections.family_spans.v1` or equivalent typed substrate
  for diagnosis/problem, seizure, medication, investigation, history/background,
  frequency, and plan/follow-up spans.
- **Dependencies:** none for design; injection should follow coverage audit.
- **Parallelizable:** yes, but coordinate with C2 if files are being split.
- **Owner:** unassigned.
- **Validation:** Gold evidence coverage by family, false-family span count, and
  at least one cap-slice comparison of full-note versus family-span prompting.
- **Notes:** Section-aware prompt routing failed as an arm; this card tests the
  typed document-geometry mechanism.

### G1 - Gan Candidate Inventory Coverage Report

- **Outcome:** A first-class coverage report for Gan S0 candidate inventory
  under the current D1/builder substrate.
- **Dependencies:** none.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Candidate recall by label family and hard strata:
  multi/highest, seizure-free conflict, cluster, vague frequency,
  unknown-with-events, no-reference, and gold-equivalent Purist/Pragmatic
  coverage.
- **Notes:** Measure coverage before adding more adjudicator or prompt variants.

### G2 - Gan Target Selection And Label Construction Split

- **Outcome:** An ablation plan, then implementation, that separates selected
  candidate/reason-code choice from exact Gan label emission.
- **Dependencies:** G1 for coverage and strata.
- **Parallelizable:** after G1.
- **Owner:** unassigned.
- **Validation:** Compare free adjudication, candidate-constrained adjudication,
  reason-code selector, and deterministic label constructor where supported.
  Report both `gan2026_paper_reproduction` and canonical diagnostic views.
- **Notes:** This is the largest bundled Gan semantic stage after R11/R15.

### G3 - Gan Unknown Versus No-Reference Policy Probe

- **Outcome:** A narrow post-adjudication policy probe for `unknown`,
  `no seizure frequency reference`, weak quantified labels, and seizure-free
  conflict cases.
- **Dependencies:** G1; ideally after G2 defines selected-candidate metadata.
- **Parallelizable:** after G1.
- **Owner:** unassigned.
- **Validation:** Stratified confusion report under canonical scorer and paper
  reproduction scorer. Must not repeat the broad unknown-overuse guard.
- **Notes:** The goal is policy isolation, not generic certainty prompting.

## Blocked

### B1 - ExECT Optimized Stack Reconstruction

- **Outcome:** S1*/S2*/S3*/S4*/S5* built from optimized components rather than
  broad prompt ladders.
- **Blocked by:** E1-E4 component substrates and at least initial isolated
  ceiling reports.
- **Parallelizable:** no.
- **Owner:** unassigned.
- **Validation:** Per-family deltas from isolated ceilings, pairwise
  interaction losses, pooled micro F1 as secondary, and holdout residual audit.
- **Notes:** Do not start this until component ceilings exist.

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

### X1 - Component Ceiling Registry Backfill

- **Outcome:** Existing Gan and ExECT results backfilled into
  `component_ceiling_registry.md` or a linked detail table with caveats for
  whether each row is an isolated ceiling, operational stack, diagnostic result,
  rejected arm, or blocked benchmark claim.
- **Dependencies:** C1/C2 helpful; can proceed from docs alone.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Every promoted baseline has model/provider, split, scorer,
  config/run ID where available, normalization/bridge policy, and caveat.

### X2 - Pairwise ExECT Interaction Plan

- **Outcome:** A preregistered plan for diagnosis+seizure type,
  seizure type+frequency, medication+temporality, investigation+comorbidity,
  and other high-value pairwise interactions.
- **Dependencies:** initial component ceiling reports.
- **Parallelizable:** after E1-E4.
- **Owner:** unassigned.
- **Validation:** Each pair has hypothesis, support counts, primary family
  metrics, interference criteria, and stop rule.

### X3 - Registry And Atlas Refresh

- **Outcome:** Regenerated registry-derived navigation only after May 28
  decisions and component-ceiling statuses are encoded.
- **Dependencies:** X1.
- **Parallelizable:** after X1.
- **Owner:** unassigned.
- **Validation:** Generated artifacts explicitly state they postdate R11-R15 and
  the May 28 component pivot.

## Done Or Frozen

The old R/A backlog is frozen as active guidance. Keep its evidence, but do not
pull from it directly without translating the work into one of the current
cards above.

### C1 - Thermo-Nuclear Codebase Architecture Audit

- **Outcome:** Completed as
  `docs/planning/thermo_nuclear_codebase_architecture_audit_20260528.md`.
- **Validation:** Review artifact with file/line references, dataset/scorer
  preservation risks, and a ranked cleanup sequence.
- **Notes:** C2 now provides the deletion map; broad deletions still wait on a
  typed program variant registry plus active-status review.

### C2 - Program Surface Inventory And Deletion Map

- **Outcome:** Completed as
  `docs/planning/program_surface_inventory_deletion_map_20260528.md`.
- **Validation:** Inventory maps active surfaces, consolidation candidates,
  archive/delete candidates, retained provenance, and focused validation gates.
- **Notes:** Do not delete code or move configs until the typed program variant
  registry and C4 status review preserve current-authority, historical, rejected,
  and replay-provenance status.

### C3 - Typed Program Variant Registry

- **Outcome:** Introduced a typed source of truth for program variant contracts,
  dataset/schema/scorer compatibility, active status, and provenance notes.
- **Evidence:** `src/clinical_extraction/experiments/program_variant_registry.py`;
  `docs/experiments/synthesis/program_variant_registry.md`;
  `scripts/report_program_variant_registry.py`.
- **Validation:** `uv run pytest tests/test_program_variant_registry.py -q`
  passed with 13 tests; selected Gan config compatibility tests passed; all 59
  JSON configs under `configs/experiments` loaded through
  `load_experiment_config`.
- **Notes:** This completed the registry prerequisite from C2 and moved config
  validation away from a large literal table in `config.py`. The 59-config check
  is deliberately loadability evidence only; C4 now supplies the status
  authority layer.

### C4 - Active Experiment Status Review

- **Outcome:** Completed as
  `docs/planning/active_experiment_status_review_20260528.md`.
- **Evidence:** `src/clinical_extraction/experiments/program_variant_registry.py`
  now distinguishes current-authority rows from loadable replay rows and renders
  a per-config inventory in
  `docs/experiments/synthesis/program_variant_registry.md`.
- **Validation:** `uv run pytest tests/test_program_variant_registry.py -q`
  passed with 15 tests.
- **Notes:** The live config tree still has 59 loadable JSON configs, but C4
  classifies them as 34 current-authority config rows and 25 loadable-replay
  rows. Loadability is not active experiment authority, and no scorer, loader,
  split, or benchmark semantics changed.

### C5 - ExECT Frequency Event/Rate Payload Gate

- **Outcome:** Completed as
  `docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.md`
  with generated companion JSON at
  `docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.json`.
- **Validation:** `uv run python scripts/audit_exect_frequency_event_rate_payload.py`
  generated the audit; broad deterministic payload coverage improved from the
  archived 11.6% baseline to 43/43 validation gold labels and 24/24 full-label
  gold documents. Coverage is 100% across quantified rate, qualitative,
  seizure-free, zero-rate, type-associated, temporal-scope, and multi-label
  validation cases.
- **Notes:** This clears the E1 coverage gate but does not close the component.
  Broad candidate precision is 22.2% with 151 extra validation candidates, so
  the next frequency work should split candidate selection/adjudication from
  label construction before any model-backed stack work.

### C6 - Gan S0 Surface Split

- **Outcome:** Completed by extracting Gan S0 variant/spec routing to
  `src/clinical_extraction/gan/s0/variant_routing.py` and prediction-bridge /
  artifact assembly behavior to
  `src/clinical_extraction/gan/s0/prediction_bridge.py`, while preserving the
  public `src/clinical_extraction/programs/gan_frequency_s0.py` wrappers for
  existing configs, tests, and scripts.
- **Evidence:** `GanS0VariantSpec`, default prompt routing, stage-graph lookup,
  `predict_gan_records`, `_predict_record`, evidence guards, label
  normalization repairs, and `gan_frequency_s0_run_metadata` now live in
  focused Gan S0 package surfaces.
- **Validation:** `uv run pytest tests/test_gan_s0_program.py
  tests/test_gan_temporal_candidates.py tests/test_gan_slot_payload.py -q`
  passed with 178 tests; `uv run pytest tests/test_gan_scoring.py
  tests/test_gan_paper_reproduction_scoring.py -q` passed with 13 tests.
- **Notes:** Behavior-preserving architecture batch only. Candidate generation,
  scorer behavior, public wrappers, and `unknown` versus
  `no seizure frequency reference` policy were preserved. Generated reports
  should still label scorer mode explicitly.

### C7 - ExECT S1 Bridge Boundary Split

- **Outcome:** Completed by adding a typed S1 boundary metadata contract at
  `src/clinical_extraction/exect/s1_boundary.py` and attaching
  `s1_boundary_surfaces` to S1 `DocumentPrediction.metadata` from
  `src/clinical_extraction/programs/exect_s0_s1.py`.
- **Evidence:** The metadata now separates raw model outputs, deterministic
  benchmark-bridge rows, bridge flags, prompt-policy provenance, and final
  benchmark-facing artifact values without changing the scored
  `ExtractedValue` list.
- **Validation:** Added raw/bridge parity fixtures for diagnosis specificity
  collapse, seizure-type split/co-listing, brand medication normalization, and
  current Rx augmentation in `tests/test_exect_s0_s1_program.py`.
  `uv run pytest tests/test_exect_s0_s1_program.py
  tests/test_exect_diagnosis_primitives.py
  tests/test_exect_medication_primitives.py -q` passed with 104 tests;
  `uv run pytest tests/test_exect_scoring.py tests/test_exect_loader.py -q`
  passed with 11 tests; `uv run pytest
  tests/test_exect_seizure_type_primitives.py -q` passed with 6 tests.
- **Notes:** No loader, scorer, split, benchmark-source, certainty-threshold,
  CUIPhrase preference, medication temporality, or specificity-collapse
  semantics changed. C7 now provides the architecture substrate for E2.

### C8 - ExECT Frequency Payload Extraction

- **Outcome:** Completed by extracting ExECT frequency event/rate/cue parsing,
  candidate payload construction, high-precision candidate mode, and
  benchmark-bridge recovery into
  `src/clinical_extraction/exect/frequency_payload.py`.
- **Evidence:** Frequency-specific S4 imports, slot payloads, primitive fixture
  invokers, and the no-model audit script now consume the frequency payload
  module directly; `src/clinical_extraction/exect/primitives.py` keeps
  compatibility re-exports for existing callers.
- **Validation:** `uv run pytest tests/test_exect_frequency_primitives.py
  tests/test_exect_frequency_slot_payload.py -q` passed with 20 tests;
  `uv run python scripts/audit_exect_frequency_event_rate_payload.py` preserved
  the C5 result: broad gold coverage 100.0%, broad precision 22.2%, and
  24/24 full-label gold documents. Additional checks passed:
  `tests/test_exect_high_precision_candidates.py`,
  `tests/test_exect_s4_prompt_policy.py`, `tests/test_exect_s4_program.py`,
  `tests/test_primitive_contracts.py`, and
  `tests/test_primitive_fixture_library.py`.
- **Notes:** No loader, split, scorer, gold-source, seizure-type inference, or
  Gan-to-ExECT label policy changed. ExECT abstention remains empty-list policy,
  not Gan no-reference policy.

### E2 - S1 Raw/Bridge/Prompt Causal Split

- **Outcome:** Completed by adding a deterministic artifact-only S1 split audit
  at `scripts/audit_exect_s1_raw_bridge_prompt_split.py` with reusable helpers
  in `src/clinical_extraction/evaluation/exect_s1_split_audit.py`.
- **Evidence:** The generated report
  `docs/experiments/exect/exect_s1_raw_bridge_prompt_split_audit_20260528.md`
  decomposes diagnosis and seizure-type performance across schema-only raw
  cap-25, v4.10 policy raw cap-25, v4.10 post-bridge cap-25, full-validation
  raw/post-bridge GPT surfaces, and the promoted Qwen validation/test-holdout
  clean-v2 surfaces.
- **Validation:** `uv run pytest tests/test_exect_s1_split_audit.py -q` passed
  with 4 tests; `uv run python
  scripts/audit_exect_s1_raw_bridge_prompt_split.py` produced JSON and
  Markdown artifacts with 0 model calls. Full-validation bridge deltas were
  +32.3 pp diagnosis and +33.1 pp seizure type; Qwen test holdout minus
  validation was -28.5 pp diagnosis and -22.1 pp seizure type.
- **Notes:** E2 supports keeping S1 as a strong validation anchor, but not a
  near-ceiling mechanism claim. No loader, split, scorer, benchmark bridge, or
  model-run behavior changed; test-holdout residuals are reported only as an
  existing transfer warning and are not tuning targets.

Recent evidence that remains active:

| Evidence | Current interpretation |
| --- | --- |
| Typed program variant registry + C4 status review, 2026-05-28 | Registry-backed config contract surface exists, renders a synthesis report, and classifies each live config as current-authority or loadable replay/provenance. |
| ExECT E1 frequency event/rate payload audit, 2026-05-28 | Broad deterministic frequency payload now covers all validation gold labels and gold-bearing docs, but low candidate precision keeps selection/adjudication open. |
| Gan C6 S0 surface split, 2026-05-28 | Gan S0 variant/spec routing and prediction-bridge artifact assembly are behavior-preserving package surfaces; use them for G1/G2 stage attribution without changing scorer or no-reference policy. |
| ExECT C7 S1 bridge boundary metadata, 2026-05-28 | S1 raw model output, prompt-policy provenance, deterministic bridge rows/flags, and final artifact values are inspectable separately without scorer or loader changes; use this as the substrate for E2. |
| ExECT C8 frequency payload extraction, 2026-05-28 | Frequency candidate payload, high-precision mode, slot payload, and benchmark bridge now share a typed frequency module without changing C5 coverage or scorer semantics. |
| ExECT E2 S1 split audit, 2026-05-28 | S1 full-validation GPT is near ceiling only after benchmark bridges; Qwen test holdout transfer drops keep S1 validation-aligned rather than mechanism-solved. |
| ExECT deep review, 2026-05-28 | Current ExECT decomposition doctrine; component ceilings before stacking. |
| Gan S0 deep dive, 2026-05-28 | Current Gan decomposition doctrine; split candidate inventory, target selection, label construction, and policy. |
| Gan R11/R15 | D1 v1.2b schema-guard-only is the mechanism baseline; arithmetic and broad relative-anchor guardrails are diagnostic or rejected arms. |
| Gan R12 | CLINES-style entity-first interface is a rejected arm, not mechanism closure. |
| Gan R13 | Self-consistency is rejected for current Gan S0 compute allocation without a new instability hypothesis. |
| Gan R14 | Qwen GEPA remains blocked until compact-delta gate clears. |
| ExECT holdout report | Transfer warning and residual-analysis trigger; not a tuning target. |
| S5 v2b | Current operational ExECT core-stack baseline; not proof of component ceilings. |

## Dependency Notes

- C1/C2/C3/C4 are complete enough to unblock carefully sequenced archive/delete
  proposals, but broad moves still need row-level provenance checks.
- The typed program variant registry preserves loadable contracts and classifies
  registry/config rows as current-authority, replay/provenance, historical,
  rejected, blocked, or diagnostic.
- C6-C11 translate the C1 thermo-nuclear cleanup sequence into pullable
  architecture batches. C6 is now complete for Gan S0 routing and prediction
  bridge surfaces; C7 is complete for the ExECT S1 bridge-boundary surface; C8
  is complete for the ExECT frequency payload and bridge surface without
  changing dataset, split, scorer, or benchmark semantics.
- E2 is complete as an artifact-only causal split audit. E3, E4, and G1 remain
  safe first pulls because they do not require model calls. G1 should consume
  the completed C6 Gan S0 stage surfaces; ExECT frequency candidate-selection
  design can now consume C8, but is not a broad-stack model run.
- G2 and G3 depend on G1 because target-selection and policy probes need known
  candidate coverage strata.
- B1 is blocked until component substrates and isolated ceilings exist.
- C9 should wait until S1/frequency bridge boundaries are stable enough to avoid
  moving S5 stack logic twice.
- C10 should not delete or regenerate registry material until X1 refreshes
  component-ceiling rows and export scripts consume C4 status classes; otherwise
  it will recreate stale navigation.
- X3 should not run until X1 and C10 are complete enough to prevent stale
  navigation from being regenerated.

## Parallelization Opportunities

- **Safe now:** E3, E4, and G1. G1 should consume the completed C6 Gan S0 stage
  surfaces; ExECT frequency candidate-selection work should consume the
  completed C8 payload surface.
- **Single-threaded or carefully sequenced:** broad code deletions after C1/C2;
-  C9 stack separation; any change to scorer, loader, split, benchmark bridge,
  or shared primitive contracts.
- **Blocked together:** C11 waits on extracted stage surfaces; B1 waits on
  ExECT component ceilings; X3 waits on X1 and C10.
- **Model-call gated:** E1/E3/E4/G1 audits should finish before related model
  runs.

## Recommended Next Pull

1. **G1 - Gan Candidate Inventory Coverage Report** if the next slot is Gan
   decomposition analysis using the completed C6 stage surfaces.
2. **E3 - Medication Current-Rx And Lifecycle Payload** if the next slot is an
   ExECT medication substrate that separates current-Rx extraction from
   lifecycle/temporality reasoning.
3. **E4 - Family-Span/List Payload** if the next slot is ExECT document
   structure and family-span substrate work.

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

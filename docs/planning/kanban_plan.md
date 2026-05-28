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

## Ready

### C1 - Thermo-Nuclear Codebase Architecture Audit

- **Outcome:** A strict repo-grounded code-quality review that identifies the
  largest bloat, bundling, duplicated helper, mode-flag, and file-size risks
  blocking the Gan and ExECT decomposition work.
- **Dependencies:** none.
- **Parallelizable:** yes, but it should precede broad refactors.
- **Owner:** unassigned.
- **Validation:** Review report with file/line references, preservation risks
  for dataset/scorer/reproducibility semantics, and a ranked cleanup sequence.
- **Notes:** Use `thermo-nuclear-code-quality-review`. Also invoke the relevant
  domain guardrail skill when reviewing loaders, scorers, schemas, primitives,
  DSPy programs, or benchmark-facing extraction logic.

### C2 - Program Surface Inventory And Deletion Map

- **Outcome:** A concise inventory of active versus obsolete Gan/ExECT programs,
  configs, scripts, and helper modules, with candidates for deletion, archival,
  or consolidation.
- **Dependencies:** C1 recommended, but basic inventory can start immediately.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Inventory maps each cleanup candidate to replacement code,
  retained run provenance, and focused tests needed before removal.
- **Notes:** The goal is not cosmetic reorganization. Delete or isolate
  complexity only when behavior and experiment provenance remain traceable.

### E1 - ExECT Frequency Event/Rate Payload Gate

- **Outcome:** A no-model ExECT frequency payload audit that materially improves
  over the prior 11.6% gold-label coverage baseline before any new S5 frequency
  model grid.
- **Dependencies:** none.
- **Parallelizable:** yes, no model calls required.
- **Owner:** unassigned.
- **Validation:** Coverage, precision, and full-label coverage by document and
  label type: quantified rate, qualitative, seizure-free, zero-rate,
  type-associated, temporal-scope, and multi-label cases.
- **Notes:** This is the highest-priority ExECT substrate gap identified in the
  deep review.

### E2 - S1 Raw/Bridge/Prompt Causal Split

- **Outcome:** Diagnosis and seizure-type performance decomposed into raw model
  extraction, deterministic bridge effects, prompt-policy effects, and final
  benchmark-facing output.
- **Dependencies:** none.
- **Parallelizable:** yes, analysis-first.
- **Owner:** unassigned.
- **Validation:** Validation plus holdout residual samples by family, with
  failures classified as extraction, bridge, policy, specificity/collapse, or
  scope errors. No holdout tuning.
- **Notes:** This replaces the old ambiguous bridge/prompt backlog item. The goal
  is to decide whether S1 is near ceiling or only validation-aligned.

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

Recent evidence that remains active:

| Evidence | Current interpretation |
| --- | --- |
| ExECT deep review, 2026-05-28 | Current ExECT decomposition doctrine; component ceilings before stacking. |
| Gan S0 deep dive, 2026-05-28 | Current Gan decomposition doctrine; split candidate inventory, target selection, label construction, and policy. |
| Gan R11/R15 | D1 v1.2b schema-guard-only is the mechanism baseline; arithmetic and broad relative-anchor guardrails are diagnostic or rejected arms. |
| Gan R12 | CLINES-style entity-first interface is a rejected arm, not mechanism closure. |
| Gan R13 | Self-consistency is rejected for current Gan S0 compute allocation without a new instability hypothesis. |
| Gan R14 | Qwen GEPA remains blocked until compact-delta gate clears. |
| ExECT holdout report | Transfer warning and residual-analysis trigger; not a tuning target. |
| S5 v2b | Current operational ExECT core-stack baseline; not proof of component ceilings. |

## Dependency Notes

- C1 should happen before large cleanup PRs, but C2 can run in parallel as an
  inventory.
- E1, E2, E3, E4, and G1 are safe first pulls because they do not require model
  calls.
- G2 and G3 depend on G1 because target-selection and policy probes need known
  candidate coverage strata.
- B1 is blocked until component substrates and isolated ceilings exist.
- X3 should not run until registry/component status is refreshed; otherwise it
  will recreate stale navigation.

## Parallelization Opportunities

- **Safe now:** C1, C2, E1, E2, E3, E4, G1.
- **Single-threaded or carefully sequenced:** broad code deletions after C1/C2;
  any change to scorer, loader, split, benchmark bridge, or shared primitive
  contracts.
- **Blocked together:** B1 waits on ExECT component ceilings; X3 waits on X1.
- **Model-call gated:** E1/E3/E4/G1 audits should finish before related model
  runs.

## Recommended Next Pull

1. **C1 - Thermo-Nuclear Codebase Architecture Audit.** Establish the cleanup
   map before editing core programs.
2. **C2 - Program Surface Inventory And Deletion Map.** Identify what can be
   removed, consolidated, or isolated without losing provenance.
3. **E1 - ExECT Frequency Event/Rate Payload Gate** or **G1 - Gan Candidate
   Inventory Coverage Report**, depending on whether the next implementation
   slot is ExECT or Gan.

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
- Treat rejected arms as rejected arms unless a mechanism-level review closes
  the mechanism.
- Holdout metrics trigger residual analysis only; do not tune from holdout.
- Prefer typed payloads, primitives, bridges, and scorer policies over prompt
  bloat and broad mode flags.

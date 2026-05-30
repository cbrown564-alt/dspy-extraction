# Clinical Extraction Kanban Plan

Status: active steering doc
Last refreshed: 2026-05-30 after P2 G30 standard50 GEPA result and P5 ExECT frequency adjudicator preregistration
Supersedes: the pre-pivot R/A backlog as active priority guidance

This board is current-first. Completed work is retained only when it changes
active sequencing. Detailed history belongs in
`component_ceiling_registry.md`, experiment reports, generated artifacts,
archive indexes, and git history.

The active program is the May 28 component-ceiling pivot:

1. estimate or explain isolated component ceilings;
2. test pairwise interference before rebuilding stacks;
3. keep scorer, loader, split, benchmark bridge, and prediction-repair
   semantics fixed unless a card explicitly changes them.

## Current Priorities

1. **Gan S0: G29 is implemented and rejected as tested.** The G24/G28
   evidence-first selector is useful on validation but not promoted as an
   operational default after G27. Full synthetic validation improves over
   stored builder-gap GPT under the paper scorer, but frozen-test monthly is
   essentially tied and lower on pragmatic category. G29 added the
   validation-residual-family checkpoint and preserved trace / label-contract
   validity, but full validation regressed versus G27: 243/299 paper monthly
   versus 247/299, with 10 gains and 14 regressions. Do not promote G29 or run
   a frozen-test check for this arm.

2. **ExECT: move from substrates to isolated ceilings and corrected pairwise
   arms.** E11 remains a residual router only. The E1-E13 synthesis now routes
   the next ExECT experiments to frequency adjudication over the fixed broad
   payload, S1 diagnosis/seizure raw-bridge ceiling comparators, medication
   prompt isolation or deterministic routing after E13, and corrected X2
   pairwise arms. B1 stays blocked until isolated family ceilings and
   component-isolated interaction evidence exist.

3. **Gan GEPA has cleared the hosted teacher-runner runtime gate, but the G30
   standard50 arm is rejected as tested.** P2/G30 proves GPT-4.1-mini
   prediction and a separate hosted GPT-5.5 reflection config can run
   end-to-end over the evidence-first selector. With `max_metric_calls=80`,
   GEPA accepted reflected candidates and improved its 16-record compile
   objective, but the final standard50 result was only 41/50 paper monthly,
   below G24/G28 at 44/50 and below the G25 43/50 gate. Do not full-validate,
   run Qwen GEPA, inspect frozen test, or scale the accepted policy-wall
   instruction from this arm.

4. **Medication follow-up needs a new mechanism, not the rejected E13 shape.**
   E13 rejects the tested AM+MT lifecycle-context routing arm because it lost
   annotated-medication recall without reducing false positives. Any next
   medication card should test prompt isolation or deterministic routing while
   keeping annotated medication as the sole scored endpoint and lifecycle /
   temporality as diagnostic context only.

5. **Frequency and target-selection work must stay decomposed.** For Gan,
   separate frequency-content gating, candidate inventory, temporal anchoring,
   aggregation, special-label policy, and final target selection. For ExECT,
   treat broad frequency payloads as recall substrates until an adjudicator or
   ranker is preregistered against the fixed payload.

6. **Architecture cleanup is no longer a standing workstream.** C12-C32 closed
   the active cleanup and current-authority pass. New cleanup needs a concrete
   runtime contract or active-authority ambiguity, not historical card
   carryover.

7. **Benchmark and scorer policy stay frozen by default.** Gan paper-comparison
   tables use `gan2026_paper_reproduction`; canonical Gan metrics remain
   diagnostic. ExECT Table 1 reproduction remains blocked until CUI-aware
   all-family scoring exists. Holdout and frozen-test rows are residual-analysis
   surfaces, not tuning surfaces.

## Active Pulls

### P1 - Gan Validation-First Selector Follow-Up

- **Outcome:** A preregistered and implemented Gan mechanism arm targeting
  specific G27 validation residual families without using frozen-test rows for
  wording, policy, or candidate-surface tuning.
- **Dependencies:** G24/G28/G27 reports, G25 generalization policy, G19/G17/G22
  row ledgers, G21 constructed-option surface.
- **Parallelizable:** yes with ExECT follow-up planning.
- **Owner:** Codex.
- **Status:** rejected as tested after G29 implementation.
- **Validation:** Smoke trace and label-contract gates passed. Full validation
  scored 243/299 paper monthly, below G27 at 247/299, with 10 gains and 14
  regressions.
- **Notes:** See
  `docs/experiments/gan/gan_s0_g29_validation_residual_selector_preregistration_20260529.md`
  and
  `docs/experiments/gan/gan_s0_g29_validation_residual_selector_results_20260529.md`.
  Treat the evidence-first selector as a useful validation mechanism arm, not a
  new default. Treat G29 as a rejected arm, not mechanism closure.

### P2 - Gan G30 GEPA Teacher-Runner Mechanism Card

- **Outcome:** A preregistered Gan optimizer mechanism path that gives GEPA a
  real test over the current strongest frequency-selector architecture, using
  GPT-4.1-mini for predictions and a stronger hosted GPT-5-family reflection
  teacher when available, and records whether the hosted smoke and standard50
  gates justify any further optimizer scale-up.
- **Dependencies:** R14 GEPA postmortem and compact-delta gate, G24/G28/G27
  evidence-first selector reports, G25 standard50/generalization policy,
  G19/G17/G22/G23/G29 residual ledgers, G21 constructed-option surface, Gan
  audit, and runner support for separate prediction and reflection model
  configs.
- **Parallelizable:** design and runner/config support can run with ExECT
  planning; model calls wait for preregistration, dry-run validation, and
  teacher-model availability.
- **Owner:** Codex.
- **Status:** completed for hosted teacher-runner smoke and rejected standard50
  GEPA arm.
- **Validation:** Add config/runtime support proving the prediction LM and GEPA
  reflection LM can differ; preregister G30 controls; dry-run configs; preserve
  fixed scorer, loader, split, benchmark bridge, candidate-builder,
  constructor, and prediction-repair semantics; run smoke before standard50.
  Implemented runtime support with `optimizer.reflection_model_config_path`,
  added matched-control and GEPA smoke configs, dry-ran both successfully, fixed
  GEPA optimizer artifact serialization for path-valued reflection configs, and
  ran live smoke. Matched control
  `gan_s0_g30_evidence_first_control_gpt4_1_mini_smoke6_20260530T200132Z`
  completed 6/6 valid predictions. Corrected GEPA smoke
  `gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_smoke6_20260530T200635Z`
  used `max_metric_calls=12`, invoked GPT-5.5 reflection, retained no new
  candidate, and produced the same final labels as control. Both scored 0/6
  paper monthly and 1/6 pragmatic on the smoke rows, with 6/6 schema validity
  and 5/5 evidence support among present quotes; this is a runtime gate, not a
  performance estimate. The standard50 GEPA follow-up
  `gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_standard50_20260530T203349Z`
  used `max_metric_calls=80`, accepted reflected candidates, improved the
  compile-set objective from 10.25/16 to 11.1/16, and wrote a 14,639-character
  final instruction. It scored 41/50 paper monthly, 42/50 Purist, 43/50
  Pragmatic, 50/50 schema validity, and 44/44 evidence support among present
  quotes, with 6/50 missing prediction evidence. Against G24/G28 standard50 at
  44/50 monthly, the row movement was 2 fixes, 4 regressions, 5 shared misses,
  and 39 shared hits, so it misses the G25 gate and is rejected as tested.
- **Notes:** Treat GPT-5.4 as a requested teacher alias that must be verified
  against available model config before live calls. If unavailable, use the
  repo's strongest approved hosted GPT-5-family teacher config or add a
  clearly named private model config. Use `gan2026_paper_reproduction` as the
  primary benchmark-facing scorer and keep canonical Gan metrics diagnostic.
  The tested GEPA-over-evidence-first arm does not authorize full validation,
  Qwen GEPA, frozen-test inspection, or scaling the accepted policy-wall
  instruction. Future GEPA work should be a new compact or stripped-prompt
  mechanism card with its own standard50 gate and row ledger. Promotion still
  requires a standard50 gate of at least 43/50 paper monthly or a
  preregistered row-ledger exception with no special-label regression; full
  validation must beat G27's 247/299 paper monthly or justify a narrower
  arm-level decision. Qwen remains blocked until the hosted compact-delta gate
  clears. See
  `docs/experiments/gan/gan_s0_g30_gepa_teacher_runner_preregistration_20260530.md`,
  `docs/experiments/gan/gan_s0_g30_gepa_teacher_runner_smoke_results_20260530.md`,
  `docs/experiments/gan/gan_s0_g30_gepa_teacher_runner_standard50_results_20260530.md`,
  `configs/experiments/gan_s0_g30_evidence_first_control_gpt4_1_mini_smoke6.json`,
  `configs/experiments/gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_smoke6.json`,
  and
  `configs/experiments/gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_standard50.json`.

### P3 - ExECT Medication Prompt-Isolation Or Routing Card

- **Outcome:** A narrow validation-only medication mechanism card, and then a
  run only if the card is explicit enough, that accounts for E7/E13 false-
  positive and recall-regression evidence.
- **Dependencies:** E6 current-Rx ceiling substrate, E7 stack-interference
  attribution, E13 rejected lifecycle-context arm, E5 lifecycle target policy.
- **Parallelizable:** yes with P5 and P6; model calls should wait for the card.
- **Owner:** unassigned.
- **Validation:** Annotated medication remains the sole scored endpoint;
  lifecycle / temporality is diagnostic only; scorer and bridge semantics stay
  fixed; E7 false-positive rows are reported as a before/after ledger.
- **Notes:** Do not rerun AM+MT lifecycle context as tested. Do not count
  annotation-policy or missing-gold false-positive suppression as a clean
  precision gain unless the report says so explicitly.

### P4 - ExECT Pair 4 Investigation + Comorbidity Design

- **Outcome:** A corrected Pair 4 design that defines the comorbidity side
  before model calls, then compares investigation-only versus
  investigation-plus-comorbidity and comorbidity-only versus
  comorbidity-plus-investigation if the design clears support and policy gates.
- **Dependencies:** X2 plan and corrected-result note, E12 investigation
  near-ceiling confirmation, comorbidity support/representability review.
- **Parallelizable:** design can run with P3/P5/P6; model calls wait for the
  comorbidity side to be defined.
- **Owner:** unassigned.
- **Validation:** Target-component-alone versus target-plus-paired-component
  arms, same scored endpoint, validation split, declared interference threshold,
  and patient-history versus family-history/background leakage categories.
- **Notes:** Do not use S1-S4 ladder comparisons as pairwise evidence. E12
  solves the investigation comparator, not comorbidity.

### P5 - ExECT Frequency Adjudicator Design

- **Outcome:** A preregistered adjudicator or ranker plan against the fixed broad
  frequency event/rate payload, followed by a validation-only arm only after
  the endpoint and comparator are frozen.
- **Dependencies:** E1 frequency event/rate payload, E10 candidate-selection
  split, E11 frequency holdout residual caveat.
- **Parallelizable:** yes with P3/P6; implementation should wait until endpoint
  and comparator are explicit.
- **Owner:** Codex.
- **Status:** preregistered; implementation/model calls not yet run.
- **Validation:** Fixed payload, fixed scorer, declared precision/recall tradeoff,
  comparison to S4/S5 frequency baselines, candidate precision/recall, oracle
  gap, type-associated and multi-label strata, and label-construction
  residuals. The P5 preregistration freezes the endpoint, comparator set,
  validity gates, and stop rules.
- **Notes:** Do not run another coverage audit or broad-stack prompt loop as the
  next frequency step. Do not tune from holdout; use holdout only later as a
  residual audit. See
  `docs/experiments/exect/exect_frequency_adjudicator_p5_preregistration_20260530.md`.

### P6 - ExECT Diagnosis And Seizure-Type Ceiling Comparators

- **Outcome:** A validation-only design for isolated diagnosis and seizure-type
  ceiling comparators that separates raw extraction, benchmark bridge,
  specificity collapse, scope, and policy residuals before Pair 1 or S1*
  claims.
- **Dependencies:** E2 raw/bridge/prompt split, E11 holdout residual routing,
  ExECT gold audit, implemented diagnosis and seizure-type benchmark bridges.
- **Parallelizable:** yes with P3 and P5.
- **Owner:** unassigned.
- **Validation:** Per-family diagnosis and seizure-type precision, recall, F1,
  raw versus bridged deltas, bridge-flagged value counts, and residual classes
  under fixed `exect_field_family_deterministic_v1` semantics.
- **Notes:** Do not infer diagnosis from seizure-type evidence alone, and do
  not create seizure-type labels from frequency rows. Holdout rows remain
  residual-analysis evidence only.

## Blocked

### B1 - ExECT Optimized Stack Reconstruction

- **Outcome:** S1*/S2*/S3*/S4*/S5* built from optimized components rather than
  broad prompt ladders.
- **Blocked by:** isolated ceiling reports and corrected pairwise interaction
  evidence, not substrates alone.
- **Parallelizable:** no.
- **Owner:** unassigned.
- **Validation:** Per-family deltas from isolated ceilings, pairwise interaction
  losses, pooled micro F1 as secondary, and holdout residual audit.
- **Notes:** Do not start this until component ceilings and interaction evidence
  exist.

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

## Historical Context

These are the completed-work facts that still shape sequencing. They are not
pullable done cards.

- **Gan selector evidence:** G8, G10, G15, and G22 are rejected selector arms
  under fixed scorer, loader, split, bridge, candidate-builder, and repair
  semantics. G23 explains why: many misses already had an exact answer option,
  so the failure is often final target selection rather than candidate
  discovery. G24/G28 improved the interface with evidence-first narration,
  constrained special-label escape, and construction-aware option priority; G27
  shows validation lift but no frozen-test promotion.

- **Gan component substrates:** G13 establishes the frequency-content gate
  baseline; G14 establishes temporal anchoring diagnostics; G16/G20/G21 define
  and implement the first quantified-rate aggregation constructor; G17 defines
  the nine-row special-label policy surface. Candidate discovery and constructed
  answer-option coverage are stronger than final option choice, but neither is
  a solved operational selector.

- **Gan evaluation policy:** G6 defines `gan_s0_g6_standard50_v1` as the default
  mechanism slice and keeps the old 25-record enriched slice smoke-only. G25
  defines standard50/full-validation/frozen-test interpretation. G5 remains the
  synthetic paper-scorer pack for paper-facing Gan tables; Real(300)/Real(150)
  reporting remains blocked.

- **ExECT residual routing:** E11 attributes the validation-to-holdout drop
  without changing scorer, loader, split, bridge, prompt, prediction repair, or
  artifact semantics. S1 transfer loss concentrates in diagnosis and seizure
  type; S5 frequency loss mixes payload generalization with adjudication.
  Holdout remains residual analysis only.

- **ExECT substrates and rejected arms:** E6 confirms annotation-derived
  medication current-Rx is representable on validation; E7 attributes S5
  medication loss to over-emission; E13 rejects the lifecycle-context routing
  arm as tested. E10 shows the broad frequency payload is recall-sufficient but
  low precision. E8/E9 reject broad family-span substitution while preserving
  family spans as a diagnostic document-geometry substrate. E12 confirms
  investigation is near ceiling and unblocks corrected Pair 4 planning.
  The E1-E13/X2 synthesis report turns these into the active ExECT pull set:
  P3 medication routing, P4 Pair 4 design, P5 frequency adjudication, and P6
  diagnosis/seizure-type ceiling comparators.

- **Architecture cleanup:** C12-C32 and active-authority pruning are complete as
  research blockers. Ordinary active configs, run lookup, and program factories
  should remain current-only by default; archive/provenance access requires
  explicit reporting or replay intent.

## Frozen Work

The old R/A backlog and completed C-card cleanup lane are frozen as active pull
sources. Keep their evidence, but do not pull from them directly without
translating the work into a current component, benchmark, or runtime-contract
card.

## Dependency Notes

- B1 waits on isolated component ceilings and corrected pairwise interaction
  evidence. Substrates alone are not enough to rebuild optimized ExECT stacks.
- Any ExECT pairwise follow-up must use target-component-alone versus
  target-plus-paired-component arms, not schema-ladder comparisons.
- Pair 1 diagnosis + seizure type waits on P6 isolated comparators. Pair 2
  seizure type + frequency waits on P5 frequency adjudicator design. Pair 4
  investigation + comorbidity waits on a comorbidity-side support and
  representability review even though E12 confirms investigation.
- Medication lifecycle / temporality remains diagnostic unless a new target
  policy and scorer design explicitly make it benchmark-facing.
- Any future G30/GEPA follow-up starts from the rejected standard50 row ledger,
  not from a scale-up assumption. It needs a new compact or stripped-prompt
  mechanism card with explicit budget, the preregistered 43/50 paper-monthly
  gate, and no frozen-test tuning.
- Future Gan selector work must cite the G19/G17/G22/G23/G27 failure class it
  targets and preserve a row-level before/after ledger.
- G21 constructed answer options improve coverage only; selector performance is
  a separate claim.
- Frozen-test rows can motivate residual families but must not drive prompt,
  candidate, scorer, bridge, or repair changes.
- CUI-aware ExECT Table 1 reproduction is separate from project field-family
  metrics.

## Parallelization Opportunities

- **Safe now:** P3 ExECT medication follow-up planning, P5 frequency adjudicator
  implementation planning, P6 diagnosis/seizure ceiling-comparator design, and
  report/readme cleanup tied to completed artifacts. P4 Pair 4 design is also
  safe if it starts with comorbidity support/representability rather than model
  calls.
- **Single-threaded or carefully sequenced:** scorer, loader, split, benchmark
  bridge, shared primitive contracts, registry/archive regeneration, and any
  active runtime authority changes.
- **Blocked together:** optimized ExECT stack reconstruction and external ExECT
  benchmark claims.
- **Model-call gated:** any new Gan selector/adjudicator, ExECT medication arm,
  ExECT frequency adjudicator, ExECT diagnosis/seizure arm, or ExECT pairwise
  arm must be preregistered with fixed controls before calls are spent.
  Any future GEPA follow-up additionally requires a new compact or
  stripped-prompt mechanism card, because the G30 evidence-first standard50 arm
  is already rejected as tested.

## Recommended Next Pull

1. For ExECT, P5 design is preregistered; next pull either implements its
   deterministic comparator plus capped smoke config, or pulls P6 to design
   diagnosis/seizure raw-bridge ceiling comparators before Pair 1 claims.
2. In parallel, write P3 as a medication prompt-isolation or deterministic
   routing card that uses the E7 row ledger and avoids the rejected E13
   lifecycle-context shape.
3. Start P4 only as Pair 4 design and comorbidity support review; defer model
   calls until the target-component-alone comparators are explicit.
4. If staying on Gan, do not scale the G30 GEPA evidence-first arm. The
   standard50 run exercised `max_metric_calls=80` but scored 41/50 and regressed
   versus G24/G28; any optimizer follow-up should be a new compact or
   stripped-prompt mechanism card.
5. Add cleanup work only when it names a concrete active runtime contract or
   active-authority ambiguity.

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
- Do not describe `archive/configs` as active experiment loadability; active
  config authority lives in `configs/experiments` and the generated registry
  report's active inventory.
- Treat rejected arms as rejected arms unless a mechanism-level review closes
  the mechanism.
- Holdout and frozen-test metrics trigger residual analysis only; do not tune
  from them.
- New Gan experiments must cite the failure class they intend to reduce and
  preserve a row-level before/after ledger for that class.
- Standard50 is a mechanism surface, not a promotion surface. Future Gan
  selector plans must say how full-validation and frozen-test residual evidence
  will be interpreted before model calls are spent.
- Qwen Gan selector comparisons must be matched comparisons with fixed scorer,
  loader, split, benchmark bridge, candidate-builder, constructor, and
  prediction-repair semantics.
- Prefer typed payloads, primitives, bridges, and scorer policies over prompt
  bloat and broad mode flags.

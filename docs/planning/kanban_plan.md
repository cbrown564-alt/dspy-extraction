# Clinical Extraction Kanban Plan

**Active steering doc** - future work only. Closed pathways, rejected arms, and detailed walkthroughs live in [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md) and the linked experiment notes.

**Last refreshed:** 2026-05-28 (morning refresh — ExECT deep review E1–E6 cards added)

## Current Priorities

1. **ExECT frequency fundamentals first (E1).** Build and audit the deterministic frequency event payload before any more model runs on ExECT frequency. No-model coverage was 11.6%; this must improve before E2.
2. **Explain holdout drops before new tuning (E5).** S1 drops −14.5pp and S5 frequency drops −26.8pp validation→holdout. Do not reopen validation-side tuning until the shift is diagnosed.
3. **Keep optimizer work gated by the R14 postmortem.** Prior GEPA failures are arm rejects; Qwen GEPA remains blocked until a hosted compact-delta gate clears.
4. **Use the paper-reproduction scorer as the primary Gan benchmark-comparison view.** Keep canonical Gan metrics separate from `gan2026_paper_reproduction` scorer mode and label them as diagnostics or sensitivity analysis.
5. **Preserve reproducibility and scorer semantics.** No scorer, loader, gold-label, or test-holdout behavior changes without explicit tests and documentation.

## Carry-Forward Signals

| Finding | Implication |
| --- | --- |
| ExECT paper defaults are stable on validation. | Use the May 25 table pack and claims/caveats note; reopen ExECT only for E1–E6 cards, a concrete paper claim, or targeted S5 frequency iteration. |
| ExECT holdout drops are large and unexplained. | S1 GPT drops −14.5pp (92.3 → 77.8); S5 GPT frequency drops −26.8pp (73.9 → 47.1). Do not treat validation behavior as stable; E5 holdout shift audit is required before new paper frequency claims. |
| ExECT frequency fundamentals are skipped. | No-model frequency candidate coverage was only 11.6% in the prior audit. The frequency verifier compensates for a weak substrate; E1 must expose a typed event payload before more model frequency tuning. |
| Section-aware S1 failed as a prompt routing arm, not as a mechanism. | Deterministic family-span/list payload (E3) remains open. Do not conflate prompt-routing rejection with mechanism rejection. |
| Medication temporality is benchmark-ambiguous. | S4 temporality is excluded from S5 defaults; target definition (E4) must precede further model work on this family. |
| Gan default remains GPT-led. | Builder-gap v1 is the operational default: GPT 80.6% monthly vs Qwen 70.7%. D1 v1.2b reaches 79.9% with schema guard only; calculator + anchor guardrail discarded. Qwen work should be narrow transfer/calibration, not broad mechanism search. |
| Gan Qwen exact-policy ceiling is 71.3% monthly. | R1.1 schema-guard full validation (299 records) achieved 71.3% monthly, 79.2% Purist, 83.9% Pragmatic, 93.3% schema validity. Held after R10; builder-gap v1 Qwen (70.7%) remains the test-holdout baseline. |
| R11 D1 won; R12 C1 & R13 S1-S4 rejected. | Deterministic date/events (D1) integrated. Pre-tagging entities (C1) causes severe context-loss regression. Self-consistency (S1-S4) has 0% variance and 0.0pp gain at temp 0.7. |
| R14 GEPA postmortem is complete. | Qwen GEPA is not justified now; reopen only through a hosted compact-delta gate with instruction-length, semantic-label, schema, evidence, and token/cost controls. |
| Paper evidence is frozen. | Table pack (May 25), claims/caveats note, and experiment registry (215 rows) are current. Do not change scorer semantics or bridges without updating the table pack. |
| Rejected arms remain rejected. | S5 per-family parallel decomposition, S1 family-split probes, Gan unknown-overuse, GEPA G1/G2, high-precision frequency pruning, and medication temporal guard arms need new preregistrations to reopen. |
| Tool-during and GEPA remain open mechanisms with prior failed arms. | New work must isolate interface/objective/model track and compare against equivalent pre/post deterministic helpers. |
| Gan scorer has a paper-reproduction mismatch. | Current canonical metrics must not be compared to Gan 2026 paper numbers without the explicit `gan2026_paper_reproduction` scorer mode (infrastructure complete). |


### Ready

*(No active Ready cards)*

## In Progress

*(No active cards in progress)*

## Active Threads

These threads are no longer backlog. Keep them visible and proceed as soon as their dependencies or gates clear.

### E1 - ExECT Frequency Event Payload No-Model Audit

- **Outcome:** Deterministic typed payload for ExECT seizure-frequency evidence; no-model coverage audit on validation split before any model run. Coverage must rise materially above 11.6% (prior audit) before proceeding to E2.
- **Dependencies:** None. Implement alongside current `exect.primitives` and run against validation split.
- **Parallelizable:** yes, no model calls required.
- **Owner:** unassigned.
- **Validation:** Report coverage by template class: quantified rate, implicit rate, qualitative change, seizure-free, seizure-free-since-year, zero-rate window, multi-type block. Stop if coverage stays low.
- **Notes:** Direct analogue of Gan D1 deterministic date/event payload. Prior no-model coverage was only 11.6%; do not spend another model run on ExECT frequency until this audit improves that baseline. See [exect_task_deep_review_20260528.md](../experiments/exect/exect_task_deep_review_20260528.md).

### E2 - ExECT Frequency Event Payload Cap-25 Integration

- **Outcome:** Inject E1 payload into current S5 v2b stack; cap-25 comparison against promoted S5 baseline.
- **Dependencies:** E1 (no-model coverage must be materially above 11.6% and inspectable).
- **Parallelizable:** only after E1 gate clears.
- **Owner:** unassigned.
- **Validation:** Cap-25 S5; compare frequency precision/recall/F1, S5 micro, and non-frequency family regressions. Reject arm if gains come only from recall collapse or if diagnosis/seizure/medication/investigation regress materially.
- **Notes:** Promotion gate: frequency F1 +3pp or precision +5pp without recall loss >3pp.

### E3 - Deterministic Family-Span Primitive

- **Outcome:** Implement `exect.sections.family_spans.v1` as a structured payload (not a section-aware prompt decomposition). No-model evidence coverage audit, then one-family cap-25 injection.
- **Dependencies:** None for the primitive; E1 should guide which family to inject first (likely frequency or seizure type).
- **Parallelizable:** primitive can be built in parallel with E1; cap-25 injection only after coverage audit.
- **Owner:** unassigned.
- **Validation:** No-model: gold evidence quote coverage, family-span recall, false-family span count. Cap-25: one high-error family first.
- **Notes:** Section-aware S1 prompt arm rejection does NOT close this mechanism. This is a deterministic span payload, not a prompt routing arm.

### E4 - Medication Lifecycle Audit

- **Outcome:** Decide whether medication temporality is a benchmark target, clinical auxiliary target, or excluded noisy family. No-model audit first.
- **Dependencies:** None.
- **Parallelizable:** yes, no model calls for the audit.
- **Owner:** unassigned.
- **Validation:** Compare lifecycle table against annotated medication gold and medication-temporality gold separately; stratify by current/previous/planned/taper/stop/non-ASM/dose-only.
- **Notes:** Do not tune further on medication temporality until E4 defines the target. S5 exclusion of temporality remains default.

### E5 - S1/S5 Holdout Residual and Bridge/Prompt Causal Split

- **Outcome:** Explain how much S1/S5 performance comes from prompt policy, model extraction, and deterministic bridge normalization. Produce holdout residual samples by family.
- **Dependencies:** None; uses existing run artifacts.
- **Parallelizable:** yes, analysis only.
- **Owner:** unassigned.
- **Validation:** Validation + holdout replay (no holdout tuning); raw vs post-bridge output; family-level residual taxonomy. Output informs whether Qwen-specific or holdout-specific fixes are warranted.
- **Notes:** S1 validation 92.3 → holdout 77.8 for GPT (−14.5pp). S5 frequency validation 73.9 → holdout 47.1 for GPT (−26.8pp). These drops require explanation before new validation-tuning cycles.

### E6 - CUI-Aware Scorer Replay

- **Outcome:** Unblock Table 1-style benchmark reproduction; identify ontology-level sensitivity.
- **Dependencies:** None for scorer-only replay; required before any published-benchmark reproduction claim.
- **Parallelizable:** yes, scorer-only, no model calls.
- **Owner:** unassigned.
- **Validation:** Scorer-only replay over gold labels and current predictions; no program changes; report metric deltas and label classes affected.
- **Notes:** Prerequisite for any CUI-aware Table 1 reproduction claim. Keep separate from canonical project metrics.

### A3 - Analyze S1 Qwen Seizure-Type Local Gap

- **Outcome:** Dedicated local-gap analysis only if the paper needs more than the clean-ladder correction.
- **Dependencies:** paper narrative need.
- **Parallelizable:** yes, but not during another Ollama job.
- **Owner:** unassigned.
- **Validation:** Side-by-side family metrics against best closed S1 anchor.
- **Notes:** S1 clean v2 already restores the ladder; reopen S1 only when it changes a claim.

### A4 - Design Next S5 Frequency Verifier/Policy Iteration

- **Outcome:** Next ExECT S5 frequency arm that targets residual precision/recall tradeoffs without candidate narrowing.
- **Dependencies:** new preregistration and cap-25 gate.
- **Parallelizable:** yes, after paper priorities.
- **Owner:** unassigned.
- **Validation:** Cap-25 before full validation; preserve high-recall candidate baseline.
- **Notes:** Out of scope: v1.3 + strict qualitative stacking and high-precision pruning.

### A7 - Tool-During Agent Tool Suite Design

- **Outcome:** Define a proper tool-during ablation suite for date resolution, current/past event status, canonical frequency validation, medication/entity normalization, and rate/cluster calculation.
- **Dependencies:** R11 has defined the first date/event payload and optional tool-during resolver interface; broader tools should reuse that interface rather than inventing a parallel surface.
- **Parallelizable:** design can proceed with R12; model execution should wait for R11.
- **Owner:** unassigned.
- **Validation:** tool-during arms must be compared against equivalent pre/post deterministic helpers so the varied factor is genuinely agent-loop tool use.
- **Notes:** Prior ReAct remains an arm reject only; do not describe tool-during as mechanism-rejected.

## Blocked

### B1 - ExECTv2 Table 1 Reproduction

- **Outcome:** Explicit benchmark reproduction plan and CUI-aware scorer path.
- **Blocked by:** dedicated reproduction workstream and scorer design.
- **Parallelizable:** after scorer decision.
- **Owner:** unassigned.
- **Validation:** Reproduction report distinguishes benchmark-facing metrics from project diagnostic metrics.
- **Notes:** Do not fold this into current clean-ladder claims.

### B2 - Gan Real(300) / Real(150) Reporting

- **Outcome:** Preregistered protocol for real-note Gan reporting.
- **Blocked by:** dataset access and reporting approval.
- **Parallelizable:** after access.
- **Owner:** unassigned.
- **Validation:** Protocol states split, scorer, normalization rules, and what can be compared to synthetic validation.

## Backlog

### R15 - Bridges Vs Prompt Policy Causal Split

- **Outcome:** ExECT ablation separating benchmark prompt policy from deterministic post-bridges.
- **Dependencies:** lower priority than Gan temporal/date ablations.
- **Validation:** cap-25 before full validation; same scorer and field-family support.

### R16 - Medication Temporality Recovery Outside S5 Default

- **Outcome:** A safer medication-temporality arm that does not repeat the over-pruning S5 temporal guard.
- **Dependencies:** new preregistration and a clear benchmark-facing vs clinically-facing target.
- **Validation:** recall guard must be explicit; do not promote if benchmark medication recall collapses.

### R17 - Optimal Stage Count for Gan S0 (Axis 1)

- **Outcome:** Ablation grid testing 1-stage vs 2-stage vs 3-stage graphs under a fixed candidate source.
- **Dependencies:** R11 date/event extraction baseline.
- **Validation:** Cap-25 comparison on the monthly target to confirm if A3 (g2_candidates_adjudicate) holds its lead.

### R18 - Optimal Stage Count for ExECT S1 (Axis 1)

- **Outcome:** Controlled comparison of D1→L0→L1→L1+policy stage decompositions.
- **Dependencies:** ExECT clean ladder baseline.
- **Validation:** Compare F1 performance across S1 families.

### R19 - Gan Single-Stage vs Three-Stage Necessity (Axis 1)

- **Outcome:** Direct comparison isolating the candidate generation source to determine if/why three-stage (candidates + VR) is necessary vs single-stage.
- **Dependencies:** R17.

### R20 - LLM vs Deterministic Temporal Candidate Generation (Axis 2)

- **Outcome:** Controlled comparison of deterministic candidate builders against LLM-based (JSON path or other) candidate generators.
- **Dependencies:** R11 baselines.
- **Notes:** In the May 28 iteration, the D2 LLM-only candidate extractor was refined with `dspy.ChainOfThought`, concrete unit formats, and calendar math guidelines, which raised D2 accuracy from 24.0% to 40.0% (GPT-4-mini). However, it remains constrained compared to the deterministic parser (D1 at 96.0%) due to minor event tally omissions and subtle calendar rounding discrepancies.

### R21 - Gan Verify-Repair as Second Stage (Axis 2)

- **Outcome:** Re-evaluation of the verify-repair module (V0-V7) to isolate why det-evidence front-ends were harmful in prior runs.
- **Dependencies:** R11.

### R22 - ExECT S2 Comorbidity Atomization Bridge (Axis 2)

- **Outcome:** Test C0/C1 comorbidity bridges beyond the current cap-25 null results.
- **Dependencies:** ExECT S2 baseline.

### R23 - ExECT S2 Investigation ECG Drop Guard (Axis 2)

- **Outcome:** Validate the I0 investigation drop guard to see if the +5.6pp F1 improvement holds on broader validation.
- **Dependencies:** ExECT S2 baseline.

### R24 - General ExECT Pre-Context/Candidate Presentation (Axis 2)

- **Outcome:** Sweep other context and candidate presentation formats across ExECT families (S1–S5) to identify non-harmful designs.
- **Dependencies:** None.

### R25 - ExECT Post-Bridge Only Intervention (Axis 2)

- **Outcome:** Ablated comparison of post-bridge logic separately from the policy decomposition to check for interaction effects.
- **Dependencies:** None.

### R26 - DSPy General Optimizers Compile Sweep (Axis 3)

- **Outcome:** Controlled compile sweep of basic DSPy optimizers (Bootstrap, MIPRO, etc.) on stripped L0/L1 pipelines to diagnose the policy substitution drop.
- **Dependencies:** None.

### R27 - Multi-Stage GEPA over Gan Skeletons (Axis 3)

- **Outcome:** Implement and evaluate the multistage GEPA strategy over candidate/adjudicator or verify-repair skeletons as proposed in the workstream doc.
- **Dependencies:** `docs/workstreams/optimizer/gan_s0_multistage_gepa_workstream_20260524.md`
- **Validation:** Compare against direct single-stage GEPA baseline.

### R28 - Gan Candidate Presentation format (Axis 3)

- **Outcome:** Resolve the cap-50 null results for candidate presentation format (Table vs JSON vs Prose).
- **Dependencies:** None.

### R29 - Gan Canonical Format Examples Residual Sweep (Axis 3)

- **Outcome:** Residual analysis of canonical format examples (C1) on the 30-record slice where replay was null.
- **Dependencies:** `docs/experiments/gan/gan_s0_canonical_format_residual_slice_replay_20260521.md`.

### R30 - ExECT S4 Frequency Structured Slots (Axis 3)

- **Outcome:** Sweep structured slots configuration for S4 frequency to improve on the cap-25 null S2 arm.
- **Dependencies:** None.

## Done Or Frozen

Full decision notes and run IDs live in decision docs linked below and in [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md).

### Recent completions (May 28)

| Item | Outcome | Decision doc |
| --- | --- | --- |
| R38 - Repo cleanup | 279 configs + 460 runs archived; typo dir deleted. | — |
| R39 / R15 - D1 full val + guardrail ablation | D1 v1.2b: **79.9% monthly** (schema guard only). Calculator −6.2pp, anchor guardrail −4.6pp discarded. Not promoted; builder-gap v1 (80.6%) remains default. | [r15 decision](../experiments/gan/gan_s0_r15_d1_guardrail_ablation_decision_20260528.md) |
| R32/R33 - Gan temporal/date ablations | D1 won cap-25. D2 (LLM) lifted 24%→40% with CoT but trails D1 (96%). | [r11 decision](../experiments/gan/gan_s0_r11_temporal_date_stage_decision_20260528.md) |
| R34/R35 - CLINES entity-first gate | C1 rejected; severe context-loss regression. | [r12 decision](../experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md) |
| R36/R37 - Self-consistency variance probe | S1–S4 rejected; 0% variance at temp 0.7, 0.0pp gain. | [r13 decision](../experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md) |
| R14 - GEPA postmortem | Qwen GEPA blocked; compact-delta gate required before reopening. | [r14 doc](../experiments/gan/gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md) |
| A5/A6 - Test-holdout runs + report | Holdout queue complete. Large drops flagged (see Carry-Forward). | [holdout report](../experiments/synthesis/test_holdout_evaluation_report_20260527.md) |
| ExECT task deep review | E1–E6 cards added to Active Threads. Frequency fundamentals identified as primary gap. | [deep review](../experiments/exect/exect_task_deep_review_20260528.md) |

### Earlier completions (May 25–27)

| Item | Outcome |
| --- | --- |
| R31 - Gan paper-reproduction scorer | `gan2026_paper_reproduction` mode added alongside canonical scorer; regression tests pass. |
| R10 - Gan holdout selection review | Builder-gap v1 GPT/Qwen selected; R9 held as schema-recovery evidence. |
| Gan R1.1 schema-guard (cap-25 + full val) | 71.3% monthly, 93.3% schema validity (299 records); held, not promoted. Qwen ceiling characterized. |
| Gan R9 unknown-hybrid recovery | 99.7% schema validity; held after R10, not promoted to holdout. |
| A2 - Best-closed GPT-5.5 anchor | S5 GPT-5.5 anchor added; did not improve headline. No further anchor without new claim. |
| R4 - Experiment registry refresh | 215 rows; current defaults and superseded artifacts marked. |
| ExECT S5 v2b verifier + AM guard | Promoted; current ExECT S5 operational default. |
| ExECT S1/S2/S3 clean-ladder Qwen | Clean ladder is the current breadth story baseline. |
| Paper table pack + claims/caveats | May 25 table pack and claims/caveats note are current; paper evidence frozen. |

### Rejected arms

| Arm | Rejection reason |
| --- | --- |
| S5 per-family parallel ceiling | Cap-25 null; context fragmentation. |
| Gan unknown-overuse guard | Cap-25 reject; overconstrained. |
| GEPA G1/G2 (Qwen direct) | Mechanism failed; now postmortem-gated. |
| C1 CLINES entity-first | Severe context-loss regression. |
| S1–S4 self-consistency aggregation | Zero variance; zero gain. |
| High-precision frequency pruning | Recall collapse. |
| Medication temporal guard (broad) | Recall collapse; S4 family target undefined. |

## Operational Defaults

| Surface | Current default | GPT 4.1-mini | Qwen3.6:35b | Caveat |
| --- | --- | ---: | ---: | --- |
| Gan S0 (paper default) | builder-gap v1 | 80.6% monthly | 70.7% monthly | Synthetic validation; Qwen gap characterized but not closed. |
| Gan S0 D1 pipeline best | D1 v1.2b (`v1_2b_schema_guard_only`) | 79.9% monthly | — | Schema guard only; calculator + anchor guardrail discarded (R15 ablation). Within 0.7pp of builder-gap v1. |
| ExECT S1 | clean v2 for Qwen ladder; GPT frozen S1 anchor | 92.3% micro | 85.9% micro | Qwen clean v2 is the comparable local ladder anchor. |
| ExECT S2 | clean ladder v1 | 82.7% micro | 84.4% micro | Transferable AM guard included. |
| ExECT S3 | clean ladder v1 | 74.4% micro | 75.3% micro | Cause remains sparse/weak. |
| ExECT S4 | frozen clean/default anchor | 65.5% micro | 67.5% micro | Per-family profiles differ. |
| ExECT S5 | pre-vocab + AM guard + v2b frequency verifier | 85.8% micro; 73.9% freq F1 | 85.4% micro; 71.4% freq F1 | Accepted local transfer; Qwen frequency recall trails GPT. |

## Dependency Notes

- R11/R12/R13/R14/R31/R38/R39/R15: all complete; see Done Or Frozen.
- Qwen GEPA stays blocked; a hosted compact-delta gate must clear first.
- Direct Gan 2026 paper comparisons must use `gan2026_paper_reproduction` scorer mode and report its options.
- E2 is gated by E1 coverage audit; do not run E2 if no-model coverage stays near 11.6%.
- A3 depends on paper narrative need; A4 requires a new preregistration and cap-25 gate before full validation.
- B1 and B2 require explicit protocol decisions before implementation.

## Parallelization Opportunities

- **Safe now (no model calls):** E1 frequency payload audit, E3 family-span primitive design, E4 medication lifecycle audit, E5 holdout causal split analysis, E6 CUI scorer replay.
- **Single-threaded:** Any Qwen/Ollama model execution, full validation runs, and future GEPA gates.
- **Blocked together:** B1 and B2 depend on reporting/scorer protocol decisions; E2 is blocked by E1 coverage gate.
- **Proceed after gates:** A7 after reviewing R11/R12 interfaces; A3 after paper-need confirmation; A4 after a new preregistration; E2 after E1.

## Recommended Next Pull

1. **E1 - ExECT Frequency Event Payload No-Model Audit.** Build a deterministic typed ExECT frequency event payload and run a no-model coverage audit on the validation split. This is the Gan D1 analogue for ExECT: expose the weak LLM subproblem as a structured intermediate before spending more model runs on frequency. Requires no model calls.
2. **E5 - S1/S5 Holdout Residual and Bridge/Prompt Causal Split.** Explain the large validation-to-holdout drops (S1: −14.5pp GPT, S5 frequency: −26.8pp GPT) before new validation tuning. Analysis only; no model calls.
3. **E3 - Deterministic Family-Span Primitive (design phase).** Design and implement the `exect.sections.family_spans.v1` primitive. Can proceed in parallel with E1/E5.

## Standing Guardrails

- Do not silently change scorer semantics; update tests and document interpretation.
- Gan gold is `seizure_frequency_number[0]`; `reference[0]` is diagnostic only.
- Distinguish `unknown` from `no seizure frequency reference` in canonical Gan diagnostics; collapse no-reference into unknown only in an explicitly named Gan 2026 paper-reproduction scorer mode.
- Keep arm rejection separate from mechanism rejection; name `decision_scope` in inspection docs.
- ExECT S5 families are diagnosis, seizure type, annotated medication, investigation, and seizure frequency.
- High-recall ExECT frequency candidates remain the baseline; high-precision pruning is rejected.
- CLINES-style entity-first and date-processing stages are open mechanisms, not defaults.
- Self-consistency is a compute-allocation ablation; report variance, latency, and cost, not only accuracy.
- Tool-during and GEPA remain open mechanisms with prior arm rejects; new work needs preregistered comparison groups.
- S2/S3 clean-ladder ports include only transferable promoted S5 techniques.
- Do not overlap local Qwen jobs on the same Ollama instance.
- Cursor SDK drafts are leads, not evidence, until promoted from primary artifacts.

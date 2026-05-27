# Clinical Extraction Kanban Plan

**Active steering doc** - future work only. Closed pathways, rejected arms, and detailed walkthroughs live in [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md) and the linked experiment notes.

**Last refreshed:** 2026-05-28

## Current Priorities

1. **Preregister the next Gan temporal/date-stage ablation grid.** The holdout queue is complete; the next research value is cleaner ablation of temporal reasoning, not additional default polishing.
2. **Test CLINES-inspired decomposition as a real stage-graph hypothesis.** Specifically: entity tagging with offsets/context before normalization/date processing and final schema attribute extraction.
3. **Add self-consistency as a controlled compute-allocation ablation.** Measure both accuracy and response variance before considering more complex multi-agent systems.
4. **Reopen tool-during and GEPA only through scoped preregistrations.** Prior ReAct and GEPA outcomes are arm rejects, not mechanism closures; new work must isolate tool interface, optimizer objective, and model track.
5. **Preserve reproducibility and scorer semantics.** No scorer, loader, gold-label, or test-holdout behavior changes without explicit tests and documentation.

## Recent Findings To Carry Forward

| Finding | Implication |
| --- | --- |
| ExECT current paper defaults are stable: S5 v2b is promoted; Qwen S1-S4 clean ladder is coherent; S2/S3 GPT anchors include only transferable S5 lessons. | Use the May 25 table pack and claims/caveats note for manuscript numbers; do not reopen ExECT defaults unless a paper claim requires it. |
| Gan G0 remains GPT-led: 80.6% monthly GPT vs 70.7% Qwen; Qwen errors are mixed, not a uniform local-model failure. | Target narrow Qwen policy/calibration gates rather than broad mechanism search. |
| Gan R1.1 full validation had useful category scores but failed schema validity: 70.3% monthly, 78.4% Purist, 83.3% Pragmatic, 90.0% schema validity. | Do not promote R1.1 as-is. R5-R8 added tested guards for null no-reference outputs, final-slot noncanonical labels, and narrow inequality repair. |
| R5-R8 preserve scorer semantics: invalid hybrids/concatenations/prose are rejected with metadata; leading inequality repair is allowed only when the stripped label is already canonical. | The guarded replay improved contract behavior, but R9 must decide whether quantified unknown hybrids are prevented upstream or handled by a verifier before any Gan test selection. |
| Gan R1.1 schema-guard replay is complete but not yet the final policy. | Treat `gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T092508Z` as validation evidence for R9/promotion review, not as an automatic holdout candidate. |
| Experiment registry is refreshed for current defaults and late R9 evidence. | `experiment_registry.json` now includes curated rows for ExECT clean-ladder/S5 defaults, Gan R9 Qwen recovery, GPT exact-policy comparison, and superseded Gan hybrid-resolution/F0 artifacts. |
| Gan R10 promotion/holdout review is complete. | R10 selects builder-gap v1 GPT as the primary Gan test-holdout candidate and builder-gap v1 Qwen as local-transfer companion; R9 Qwen recovery is held as schema-recovery evidence, not promoted to holdout. |
| Gan R9 recovery run is successful: v1.8 prompt + active recovery policy is the current Qwen validation candidate. | Run `gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T122351Z` delivered 99.7% schema validity rate (1 invalid abstention), 69.1% monthly accuracy, and 298 valid predictions. |
| GPT-4.1-mini exact policy validation run is successful. | Run `gan_s0_l2_exact_policy_full_gpt4_1_mini_20260526T123247Z` delivered 99.7% schema validity (1 invalid natural abstention) and 78.5% monthly frequency accuracy on the full validation split (299 records). |
| A2 ExECT S5 GPT 5.5 closed-model anchor is complete. | Run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z` delivered 82.6% micro F1 and 74.5% seizure-frequency F1 under the fixed v2b stack; it does not displace GPT 4.1-mini as the S5 headline anchor. |
| Rejected arms remain rejected: S5 per-family parallel decomposition, S1 family-split probes, Gan unknown-overuse, GEPA G1/G2, high-precision frequency pruning, and medication temporal guard arms. | Keep them out of active planning unless a new preregistration changes the decision question. |
| Retrospective review updated the research focus. | [experimentation_retrospective_report.md](../experiments/synthesis/experimentation_retrospective_report.md) now emphasizes cleaner ablations, holdout split sensitivity, CLINES-style date/entity stages, self-consistency, proper tool-during tests, and GEPA postmortem work. |
| CLINES suggests two underexplored skeletons. | Specialist date processing and entity-first tagging should be tested as explicit stage graph/executor hypotheses, not folded into prompt tweaks. |
| Holdout wins are selective, not broad local-model superiority. | Qwen wins some ExECT S5 and Gan category metrics, but GPT still leads Gan monthly accuracy; future claims need per-surface wording. |


## Ready

### R11 - Preregister Gan Temporal/Date-Stage Ablation Grid

- **Outcome:** A preregistration and config plan for comparing specialist date/event extraction strategies under the same Gan S0 downstream adjudicator and scorer.
- **Axis:** 1/2 first; stage graph and stage executor placement.
- **Candidate arms:** deterministic date extractor, LLM date extractor, hybrid deterministic+LLM merge, tool-during date resolver.
- **Dependencies:** none; use GPT 4.1-mini cap-25 before any Qwen/full validation.
- **Validation:** cap-25 gate with monthly, Purist, Pragmatic, schema validity, evidence support, and temporal-error slice reporting.
- **Notes:** Do not change Gan scorer semantics; gold remains `seizure_frequency_number[0]`.

### R12 - Design CLINES-Style Entity-First Pipeline Gate

- **Outcome:** A small preregistered cap-25 gate for `note -> entity tags with offsets/context -> normalization/date processing -> attribute extraction -> schema aggregation`.
- **Axis:** 1 first, then 2; tests whether entity recall and schema filling should be disentangled.
- **Candidate first target:** Gan S0 if the date-stage grid needs entity/event candidates, otherwise ExECT S5 to test broad core-field extraction.
- **Dependencies:** inspect CLINES pipeline notes and map the skeleton to existing primitives/contracts.
- **Validation:** compare against promoted default on the same split/cap without scorer changes.

### R13 - Self-Consistency Variance Probe

- **Outcome:** A controlled repeated-sampling protocol for Gan S0 and/or ExECT S5 that reports accuracy, response variance, cost, and latency.
- **Axis:** 3 implementation variant / compute allocation.
- **Candidate arms:** single pass, majority vote over repeated runs, confidence-weighted vote, deterministic tie-break.
- **Dependencies:** choose one promoted surface and one capped split; avoid tuning prompts from holdout results.
- **Validation:** cap-25 first; report record-level disagreement and whether variance predicts errors.

### R14 - GEPA Failure Postmortem And Qwen Gate Design

- **Outcome:** A short optimizer postmortem explaining GPT G1/G2 failure modes and defining whether a compact Qwen GEPA gate is justified.
- **Axis:** 3 implementation variant / optimizer strategy.
- **Dependencies:** inspect generated GEPA instructions, metric objective, output length/cost, and failure examples.
- **Validation:** no new model run until the postmortem defines a smaller benchmark-contract-aligned objective.

## In Progress

*(No active cards in progress)*

## Active Threads

These threads are no longer backlog. Keep them visible and proceed as soon as their dependencies or gates clear.

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
- **Dependencies:** R11 should define the first temporal tool interface before broader tools are built.
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

| Area | Status |
| --- | --- |
| A5 - Test/Holdout Runs | Done; test-holdout queue completed successfully. |
| A6 - Report Overnight Test-Holdout Queue | Done; test-holdout evaluation report completed in [test_holdout_evaluation_report_20260527.md](../experiments/synthesis/test_holdout_evaluation_report_20260527.md). |
| R10 - Write Gan Promotion/Holdout Selection Review | Done; [gan_s0_r10_promotion_holdout_selection_review_20260526.md](../experiments/gan/gan_s0_r10_promotion_holdout_selection_review_20260526.md) selects builder-gap v1 GPT/Qwen for Gan test-holdout reporting and holds R9 as schema-recovery validation evidence. |
| A2 - Run Best-Closed Comparison Anchors | Done; [exect_s5_best_closed_gpt5_5_anchor_inspection_20260526.md](../experiments/exect/exect_s5_best_closed_gpt5_5_anchor_inspection_20260526.md) adds the S5 GPT 5.5 fixed-stack anchor. S4 GPT 5.5 already existed; S5 GPT 5.5 did not improve the overall headline, so no further A2 anchor is pulled without a new paper claim need. |
| R4 - Refresh Experiment Registry For Current Defaults | Done; registry row count is 215, with current ExECT clean-ladder/S5 defaults including the A2 GPT 5.5 S5 anchor, Gan builder-gap defaults, late R9 recovery evidence, GPT exact-policy comparison, and superseded F0/hybrid-resolution artifacts marked. |
| Gan R9 - Address Gan Quantified Unknown Hybrids Upstream | Done; v1.8 prompt paired with prediction-bridge recovery policy improved schema validity (99.7%, 298 valid predictions) but is held after R10, not promoted to holdout. |
| Gan R1.1 schema-guard cap-25 (R1.1c) | Done; run `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260526T092006Z` has 100% schema validity, 100% evidence support, 68.0% monthly accuracy, 76.0% Purist, and 84.0% Pragmatic accuracy. Decision: Pass; proceed to full R1.1 replay. |
| Gan R1.1 schema-guard full validation replay | Done; run `gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T092508Z` completed with 93.3% schema validity, 98.9% evidence support, 71.3% monthly, 79.2% Purist, and 83.9% Pragmatic accuracy. Clean rejections (20 records) successfully converted to abstentions; inequality operator bug fixed. |
| ExECT S5 v2b verifier + AM guard | Promoted for current operational default. |
| ExECT S5 Qwen true-v2b transfer | Done; accepted near-parity, not Qwen-leading. |
| ExECT S1/S2/S3 clean-ladder Qwen correction/replay | Done; use clean ladder for current breadth story. |
| ExECT S2/S3 clean-ladder GPT validation | Done. |
| Gan G0 builder-gap v1 | Frozen operational default; GPT 80.6%, Qwen 70.7% monthly. |
| Gan L2 Qwen forensics | Done; enables only the narrow exact-policy slice or surface-repair tests. |
| Gan L2 Qwen exact-policy slice | Done; run `gan_s0_l2_qwen_exact_policy_slice_qwen35b_ollama_20260525T160918Z` has 82.4% monthly accuracy but failed schema/canonical gate (94.4% schema, "many per month" non-canonical). Decision: Hold/Redesign; v1.8 schema-validity patch is now ready for rerun. |
| Gan L2 Qwen exact-policy cap-25 follow-up | Done and superseded by R1.1 full validation; v1.7 run `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T162702Z` has 69.6% monthly accuracy and 92% schema validity. v1.8 run `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T171037Z`, post-hoc re-evaluated under the tightened validator, has 72.0% monthly and 100% schema validity. |
| Gan R1.1 exact-policy full validation | Done; run `gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T054752Z` has 70.3% monthly, 78.4% Purist, 83.3% Pragmatic, 90.0% schema validity, 58.0% normalized-label accuracy, and 98.9% evidence quote support over 299 validation records. Invalid-schema error report completed in [gan_s0_r1_1_invalid_schema_error_report_20260526.md](../experiments/gan/gan_s0_r1_1_invalid_schema_error_report_20260526.md). Decision: do not promote as-is; pursue R5-R8 schema-validity follow-ups. |
| Gan R1.1 schema-guard follow-up R5-R8 | Done; regression fixtures, no-reference abstention repair, final-label canonical guard, and narrow inequality repair are implemented/tested. Decision note: [gan_s0_r1_1_schema_guard_followup_20260526.md](../experiments/gan/gan_s0_r1_1_schema_guard_followup_20260526.md). |
| Paper result table pack refresh | Done; [paper_result_table_pack_20260525.md](../experiments/synthesis/paper_result_table_pack_20260525.md) supersedes the 2026-05-24 table pack for current manuscript tables. |
| Manuscript claims/caveats draft | Done; [paper_claims_caveats_20260525.md](../experiments/synthesis/paper_claims_caveats_20260525.md) separates supported, plausible, risky, and unsupported claims. |
| S5 per-family parallel ceiling | Rejected after cap-25; no full validation. |
| Gan unknown-overuse, GEPA G1/G2 | Rejected. |
| Paper evidence freeze D1-D3 and workflow readiness | Done. |

## Operational Defaults

| Surface | Current default | GPT 4.1-mini | Qwen3.6:35b | Caveat |
| --- | --- | ---: | ---: | --- |
| Gan S0 | builder-gap v1 | 80.6% monthly | 70.7% monthly | Synthetic validation; Qwen gap characterized but not closed. |
| ExECT S1 | clean v2 for Qwen ladder; GPT frozen S1 anchor | 92.3% micro | 85.9% micro | Qwen clean v2 is the comparable local ladder anchor. |
| ExECT S2 | clean ladder v1 | 82.7% micro | 84.4% micro | Transferable AM guard included. |
| ExECT S3 | clean ladder v1 | 74.4% micro | 75.3% micro | Cause remains sparse/weak. |
| ExECT S4 | frozen clean/default anchor | 65.5% micro | 67.5% micro | Per-family profiles differ. |
| ExECT S5 | pre-vocab + AM guard + v2b frequency verifier | 85.8% micro; 73.9% freq F1 | 85.4% micro; 71.4% freq F1 | Accepted local transfer; Qwen frequency recall trails GPT. |

## Dependency Notes

- R1.1 full validation, schema-guard replay, R9 recovery, GPT exact-policy comparison, R10 holdout selection, and A5/A6 holdout reporting are complete; future work should not tune from test outcomes.
- R5-R8 are complete; they repaired adapter contract behavior without changing scorer semantics, and the late R9 recovery row is held as schema-recovery evidence after R10.
- R2 and R3 are complete; use the May 25 table pack and claims/caveats note for paper drafting.
- R4 is complete; registry rows now distinguish current defaults, held validation candidates, and superseded arms.
- A2 is complete for the currently material paper claim: the S5 GPT 5.5 anchor did not improve the fixed-stack headline, and further closed-model anchors should require a new explicit claim need.
- A3 depends on paper narrative need and should not consume local model capacity during R9.
- A4 requires a new preregistration and cap-25 gate before any full validation.
- R11 should be pulled before R12/R13 model execution because it addresses the highest-value unsolved Gan bottleneck: temporal/date reasoning.
- R12 and R13 can be designed in parallel with R11, but their first model runs should be capped and should not overlap with local Qwen jobs.
- R14 is analysis-only until it justifies a new compact optimizer gate.
- B1 and B2 require explicit protocol decisions before implementation.

## Parallelization Opportunities

- **Safe now:** R11 preregistration, R12 skeleton design, R13 aggregation protocol design, and R14 GEPA postmortem can proceed without model calls.
- **Single-threaded:** Any Qwen/Ollama model execution, especially self-consistency or GEPA gates.
- **Blocked together:** B1 and B2 depend on reporting/scorer protocol decisions.
- **Proceed after gates:** A3 after paper-need confirmation; A4 after preregistration; A7 after R11 defines the first temporal tool interface.

## Recommended Next Pull

1. **R11 - Preregister the Gan temporal/date-stage ablation grid.** Make the comparison group, axis, stage graph IDs, varied factor, cap-25 gates, and scorer caveats explicit.
2. **R12 - Draft the CLINES-style entity-first skeleton after R11 names the first date/event interface.** Keep it capped and scorer-stable.
3. **R13/R14 - In parallel, design the self-consistency aggregation protocol and write the GEPA failure postmortem.** Do not launch model runs until the protocols are reviewed.

This pull moves from frozen holdout reporting into a cleaner ablation program.

## Standing Guardrails

- Do not silently change scorer semantics; update tests and document interpretation.
- Gan gold is `seizure_frequency_number[0]`; `reference[0]` is diagnostic only.
- Distinguish `unknown` from `no seizure frequency reference`.
- Keep arm rejection separate from mechanism rejection; name `decision_scope` in inspection docs.
- ExECT S5 families are diagnosis, seizure type, annotated medication, investigation, and seizure frequency.
- High-recall ExECT frequency candidates remain the baseline; high-precision pruning is rejected.
- CLINES-style entity-first and date-processing stages are open mechanisms, not defaults.
- Self-consistency is a compute-allocation ablation; report variance, latency, and cost, not only accuracy.
- Tool-during and GEPA remain open mechanisms with prior arm rejects; new work needs preregistered comparison groups.
- S2/S3 clean-ladder ports include only transferable promoted S5 techniques.
- Do not overlap local Qwen jobs on the same Ollama instance.
- Cursor SDK drafts are leads, not evidence, until promoted from primary artifacts.

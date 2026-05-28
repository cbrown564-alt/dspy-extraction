# Clinical Extraction Kanban Plan

**Active steering doc** - future work only. Closed pathways, rejected arms, and detailed walkthroughs live in [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md) and the linked experiment notes.

**Last refreshed:** 2026-05-28

## Current Priorities

1. **Re-run the winning R11 D1 arm on full validation.** D1 (deterministic date/events candidates) won the cap-25 gate with +4pp (GPT-4) and +8pp (Qwen-35B) monthly accuracy. Confirmatory full validation is required for promotion.
2. **Repository cleanup (R38).** Clean up and archive old configurations, runs, and scripts to prepare the codebase for full validation and test-holdout runs.
3. **Keep optimizer work gated by the R14 postmortem.** Prior GEPA failures are arm rejects; Qwen GEPA remains blocked.
4. **Use the paper-reproduction scorer before comparing to Gan 2026 paper numbers.** Keep canonical Gan metrics separate from author-evaluator compatibility metrics.
5. **Preserve reproducibility and scorer semantics.** No scorer, loader, gold-label, or test-holdout behavior changes without explicit tests and documentation.

## Carry-Forward Signals

| Finding | Implication |
| --- | --- |
| ExECT paper defaults are stable. | Use the May 25 table pack and claims/caveats note; reopen ExECT only for a concrete paper claim or targeted S5 frequency iteration. |
| Gan default remains GPT-led. | Builder-gap v1 is the operational default: GPT 80.6% monthly vs Qwen 70.7%; Qwen work should be narrow transfer/calibration, not broad mechanism search. |
| Gan R9/Qwen recovery improved schema validity but did not become the holdout candidate. | Keep R9 as schema-recovery evidence after R10; do not tune from test-holdout outcomes. |
| R11 D1 won; R12 C1 & R13 S1-S4 rejected. | Deterministic date/events (D1) passes to integration/full-val. Pre-tagging entities (C1) causes severe context-loss regression. Self-consistency aggregation (S1-S4) offers 0% variance and 0.0pp gain. |
| R14 GEPA postmortem is complete. | Qwen GEPA is not justified now; reopen only through a hosted compact-delta gate with instruction-length, semantic-label, schema, evidence, and token/cost controls. |
| Rejected arms remain rejected. | S5 per-family parallel decomposition, S1 family-split probes, Gan unknown-overuse, GEPA G1/G2, high-precision frequency pruning, and medication temporal guard arms need new preregistrations to reopen. |
| Tool-during and GEPA remain open mechanisms with prior failed arms. | New work must isolate interface/objective/model track and compare against equivalent pre/post deterministic helpers. |
| Gan scorer comparison found a paper-reproduction mismatch. | Current canonical metrics must not be compared to Gan 2026 paper numbers without an explicit `gan2026_paper_reproduction` scorer mode. |


### Ready

### R38 - Clean up and Archive Historical Configurations, Runs, and Scripts

- **Outcome:** Clean repository layout with historical items in archive directories, typo directories deleted, and runner scripts restructured.
- **Axis:** Repository maintenance / ablation readiness.
- **Dependencies:** None.
- **Parallelizable:** Yes, does not affect active run queue logic.
- **Owner:** unassigned.
- **Validation:** `validate_primitives.py` checks pass; smoke run verifies path resolution is intact.
- **Notes:** Move old config JSONs, local runs, and one-off/detached scripts to `archive/` directories. Delete `configs/experiments` typo directory.

### R39 - Run R11 D1 Full Validation Replay

- **Outcome:** Rerun the winning R11 D1 arm on the full Gan 2026 synthetic validation split (299 records) to confirm the accuracy improvement.
- **Axis:** Gan S0 temporal/date validation.
- **Dependencies:** D1 cap-25 gate pass.
- **Parallelizable:** Yes, once local Ollama resources are free.
- **Owner:** unassigned.
- **Validation:** Full-validation metrics table, error analysis, and formal promotion review documentation.

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

| Area | Status |
| --- | --- |
| R32 / R33 - Run & Analyze Gan Temporal/Date Ablations | Done; D1 (deterministic date/events candidates) won the cap-25 gate. D2 (LLM extractor) was subsequently debugged and refined (ChainOfThought + calendar math cues), lifting D2 accuracy from 24% to 40% (GPT-4), though it still trails D1 (96%). [gan_s0_r11_temporal_date_stage_decision_20260528.md](../experiments/gan/gan_s0_r11_temporal_date_stage_decision_20260528.md). |
| R34 / R35 - Run & Analyze CLINES Entity-First Pipeline Gate | Done; C1 (LLM entity tags) rejected due to severe regression from context-loss. [gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md](../experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md). |
| R36 / R37 - Run & Analyze Self-Consistency Variance Probe | Done; S1-S4 majority aggregation rejected due to zero variance under temp 0.7 and 0.0pp gain. [gan_s0_r13_self_consistency_variance_probe_decision_20260528.md](../experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md). |
| A5 - Test/Holdout Runs | Done; test-holdout queue completed successfully. |
| A6 - Report Overnight Test-Holdout Queue | Done; test-holdout evaluation report completed in [test_holdout_evaluation_report_20260527.md](../experiments/synthesis/test_holdout_evaluation_report_20260527.md). |
| R12 - Design CLINES-Style Entity-First Pipeline Gate | Done; [gan_s0_clines_entity_first_pipeline_gate_preregistration_20260528.md](../experiments/gan/gan_s0_clines_entity_first_pipeline_gate_preregistration_20260528.md) defines `gan_s0_entity_first_stage_graph_gpt_cap25_v1`, C0-C2 arms, entity tag interface, gates, and R11 integration decision rules. |
| R11 - Preregister Gan Temporal/Date-Stage Ablation Grid | Done; [gan_s0_temporal_date_stage_ablation_grid_preregistration_20260528.md](../experiments/gan/gan_s0_temporal_date_stage_ablation_grid_preregistration_20260528.md) defines `gan_s0_temporal_date_stage_gpt_cap25_v1`, `g3_date_events_candidates_adjudicate`, D0-D4 arms, config plan, gates, and temporal-error slice reporting. |
| R13 - Self-Consistency Variance Probe | Done; [gan_s0_self_consistency_variance_probe_preregistration_20260528.md](../experiments/gan/gan_s0_self_consistency_variance_probe_preregistration_20260528.md) defines `gan_s0_self_consistency_compute_allocation_gpt_cap25_v1` over frozen Gan builder-gap v1, S0-S4 aggregation arms, variance diagnostics, cost/latency reporting, and cap-25 gates. No model runs launched. |
| R14 - GEPA Failure Postmortem And Qwen Gate Design | Done; [gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md](../experiments/gan/gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md) concludes compact Qwen GEPA is not justified now; Qwen GEPA stays blocked until a hosted compact-delta instruction clears a cap gate. No model runs launched. |
| R31 - Implement Gan 2026 Paper-Reproduction Scorer Mode | Done; added explicit `gan2026_paper_reproduction` scorer infrastructure alongside canonical `gan_frequency_deterministic_v1`, with author-evaluator compatibility conversion, CLI mode/options reporting, regression coverage, and Gan audit caveat. Existing Gan metrics remain under their recorded scorer semantics until explicitly replayed. |
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

- R11/R12/R13 runs and analysis are complete.
- R39 (R11 D1 full validation) requires the validated D1 candidate program variant.
- R14 is complete; Qwen GEPA stays blocked unless a hosted compact-delta gate first produces a short passing instruction.
- R31 scorer infrastructure is complete; direct Gan 2026 paper comparisons must use `gan2026_paper_reproduction` and report its options.
- A3 depends on paper narrative need; A4 requires a new preregistration and cap-25 gate before full validation.
- B1 and B2 require explicit protocol decisions before implementation.

## Parallelization Opportunities

- **Safe now:** R38 cleanup, R39 full validation planning.
- **Single-threaded:** Any Qwen/Ollama model execution, full validation runs, and future GEPA gates.
- **Blocked together:** B1 and B2 depend on reporting/scorer protocol decisions.
- **Proceed after gates:** A7 after reviewing R11/R12 interfaces; A3 after paper-need confirmation; A4 after a new preregistration.

## Recommended Next Pull

1. **R39 - Run R11 D1 Full Validation Replay.** Confirm the D1 (+4pp/+8pp) signal on the full validation split.
2. **R38 - Clean up and Archive Historical Configurations, Runs, and Scripts.** Prepare the codebase structure for cleaner run logging.

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

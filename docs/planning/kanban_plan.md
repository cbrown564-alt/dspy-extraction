# Clinical Extraction Kanban Plan

**Active steering doc** - future work only. Closed pathways, rejected arms, and detailed walkthroughs live in [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md) and the linked experiment notes.

**Last refreshed:** 2026-05-28

## Current Priorities

1. **Run and analyze the preregistered Gan cap-25 gates.** R11/R12/R13 designs are complete; the next value is executing the capped GPT 4.1-mini experiments and writing decision notes, not designing more arms.
2. **Promote only from explicit decision reports.** Each run needs a short artifact that states pass/hold/reject, temporal/date error findings, variance/cost caveats where relevant, and whether a full-validation or Qwen-transfer follow-up is justified.
3. **Keep optimizer work gated by the R14 postmortem.** Prior GEPA failures are arm rejects; Qwen GEPA is blocked until a hosted compact-delta instruction first clears a cap gate.
4. **Add paper-reproduction scorer infrastructure before comparing to Gan 2026 paper numbers.** Keep canonical Gan metrics separate from author-evaluator compatibility metrics.
5. **Preserve reproducibility and scorer semantics.** No scorer, loader, gold-label, or test-holdout behavior changes without explicit tests and documentation.

## Carry-Forward Signals

| Finding | Implication |
| --- | --- |
| ExECT paper defaults are stable. | Use the May 25 table pack and claims/caveats note; reopen ExECT only for a concrete paper claim or targeted S5 frequency iteration. |
| Gan default remains GPT-led. | Builder-gap v1 is the operational default: GPT 80.6% monthly vs Qwen 70.7%; Qwen work should be narrow transfer/calibration, not broad mechanism search. |
| Gan R9/Qwen recovery improved schema validity but did not become the holdout candidate. | Keep R9 as schema-recovery evidence after R10; do not tune from test-holdout outcomes. |
| R11/R12/R13 are preregistered but not run. | Pull implementation, capped execution, and analysis cards before designing additional Gan S0 mechanisms. |
| R14 GEPA postmortem is complete. | Qwen GEPA is not justified now; reopen only through a hosted compact-delta gate with instruction-length, semantic-label, schema, evidence, and token/cost controls. |
| Rejected arms remain rejected. | S5 per-family parallel decomposition, S1 family-split probes, Gan unknown-overuse, GEPA G1/G2, high-precision frequency pruning, and medication temporal guard arms need new preregistrations to reopen. |
| Tool-during and GEPA remain open mechanisms with prior failed arms. | New work must isolate interface/objective/model track and compare against equivalent pre/post deterministic helpers. |
| Gan scorer comparison found a paper-reproduction mismatch. | Current canonical metrics must not be compared to Gan 2026 paper numbers without an explicit `gan2026_paper_reproduction` scorer mode. |


## Ready

### R32 - Implement And Run R11 Gan Temporal/Date Cap-25 Gate

- **Outcome:** Configs/adapters and GPT 4.1-mini cap-25 runs for the R11 D0-D4 temporal/date-stage grid.
- **Axis:** Gan S0 temporal/date reasoning stage graph.
- **Dependencies:** [R11 preregistration](../experiments/gan/gan_s0_temporal_date_stage_ablation_grid_preregistration_20260528.md); fixed canonical Gan scorer semantics.
- **Parallelizable:** implementation can overlap with R33 template setup; model execution should be one run queue at a time.
- **Owner:** unassigned.
- **Validation:** run artifacts for each preregistered arm, scorer report, schema-validity/evidence-support checks, and temporal-error slice export.
- **Notes:** Do not add new arms while executing R11. The purpose is to test the date/event payload interface and D0-D4 comparison group as written.

### R33 - Analyze R11 Temporal/Date Results

- **Outcome:** Short decision report with pass/hold/reject for the R11 date-stage mechanism and a recommendation on full-validation, Qwen-transfer, or redesign.
- **Axis:** analysis / promotion decision.
- **Dependencies:** R32 run artifacts.
- **Parallelizable:** after R32; can overlap with R34 implementation if model execution is idle.
- **Owner:** unassigned.
- **Validation:** report links run IDs, cap-25 metrics, schema validity, evidence support, temporal-error findings, scorer mode, and decision caveats.
- **Notes:** This is where R11 results should be interpreted; do not bury analysis in the Kanban itself.

### R34 - Implement And Run R12 CLINES Entity-First Cap-25 Gate

- **Outcome:** Configs/adapters and GPT 4.1-mini cap-25 runs for the R12 C0-C2 entity-first stage graph.
- **Axis:** Gan S0 entity-first decomposition / CLINES-inspired stage graph.
- **Dependencies:** [R12 preregistration](../experiments/gan/gan_s0_clines_entity_first_pipeline_gate_preregistration_20260528.md), accepted R11 payload interface, fixed canonical Gan scorer semantics.
- **Parallelizable:** implementation can overlap with R32/R33; launch after R11 execution unless explicitly testing independent queue behavior.
- **Owner:** unassigned.
- **Validation:** run artifacts for C0-C2, offset/context entity-tag inspection sample, scorer report, schema-validity/evidence-support checks.
- **Notes:** Keep the entity tag interface stable enough that R12 can be compared to R11 instead of becoming a separate prompt experiment.

### R35 - Analyze R12 Entity-First Results

- **Outcome:** Decision report stating whether entity-first decomposition improves temporal/frequency extraction, whether the entity interface should be retained, and whether a combined R11+R12 follow-up is justified.
- **Axis:** analysis / mechanism decision.
- **Dependencies:** R34 run artifacts and R33 R11 decision report.
- **Parallelizable:** after R34; can overlap with R36 implementation planning.
- **Owner:** unassigned.
- **Validation:** report links run IDs, cap-25 metrics, entity-offset error findings, temporal/frequency error slices, scorer mode, and integration decision.
- **Notes:** Compare mechanism behavior, not only headline monthly accuracy.

### R36 - Implement And Run R13 Self-Consistency Variance Probe

- **Outcome:** GPT 4.1-mini cap-25 repeated-sampling runs and aggregation reports for the R13 S0-S4 compute-allocation arms.
- **Axis:** compute allocation / response variance.
- **Dependencies:** [R13 preregistration](../experiments/gan/gan_s0_self_consistency_variance_probe_preregistration_20260528.md); frozen builder-gap v1 surface; cost/latency logging.
- **Parallelizable:** implementation can proceed now; execution should wait until R11/R12 cap-25 jobs are not competing for attention.
- **Owner:** unassigned.
- **Validation:** per-arm accuracy, response variance, disagreement examples, schema validity, latency, cost, and deterministic tie-break behavior.
- **Notes:** This is not a multi-agent claim. Treat it as a controlled compute-allocation ablation.

### R37 - Analyze R13 Self-Consistency Results

- **Outcome:** Decision report stating whether self-consistency improves Gan S0 enough to justify additional compute, and whether any unstable examples should seed future error analysis.
- **Axis:** analysis / compute-allocation decision.
- **Dependencies:** R36 run artifacts.
- **Parallelizable:** after R36.
- **Owner:** unassigned.
- **Validation:** report links run IDs, aggregation method, variance/cost/latency metrics, scorer mode, and pass/hold/reject recommendation.
- **Notes:** Accuracy without variance and cost is not sufficient evidence.

### R31 - Implement Gan 2026 Paper-Reproduction Scorer Mode

- **Outcome:** Add an explicit `gan2026_paper_reproduction` scorer mode alongside the current canonical Gan scorer, reproducing Yujian Gan's author-provided evaluator semantics for comparison to paper results.
- **Axis:** scorer/reproducibility infrastructure; not a model-performance arm.
- **Dependencies:** `docs/datasets/gan/gan_scorer_comparison_report.md`, `data/Gan (2026)/previous_paper_scorer/`, and a Gan audit caveat update distinguishing paper-reproduction from clinical/canonical scorer semantics.
- **Validation:** focused regression tests for no-reference vs unknown, seizure-free, dynamic `multiple`, range midpoint math, cluster labels, optional repair, and tolerance flags; generated reports must state scorer mode and options.
- **Notes:** Do not silently rewrite existing Gan metrics. Existing experiment comparisons remain under their recorded scorer semantics until explicitly replayed.

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
| R12 - Design CLINES-Style Entity-First Pipeline Gate | Done; [gan_s0_clines_entity_first_pipeline_gate_preregistration_20260528.md](../experiments/gan/gan_s0_clines_entity_first_pipeline_gate_preregistration_20260528.md) defines `gan_s0_entity_first_stage_graph_gpt_cap25_v1`, C0-C2 arms, entity tag interface, gates, and R11 integration decision rules. |
| R11 - Preregister Gan Temporal/Date-Stage Ablation Grid | Done; [gan_s0_temporal_date_stage_ablation_grid_preregistration_20260528.md](../experiments/gan/gan_s0_temporal_date_stage_ablation_grid_preregistration_20260528.md) defines `gan_s0_temporal_date_stage_gpt_cap25_v1`, `g3_date_events_candidates_adjudicate`, D0-D4 arms, config plan, gates, and temporal-error slice reporting. |
| R13 - Self-Consistency Variance Probe | Done; [gan_s0_self_consistency_variance_probe_preregistration_20260528.md](../experiments/gan/gan_s0_self_consistency_variance_probe_preregistration_20260528.md) defines `gan_s0_self_consistency_compute_allocation_gpt_cap25_v1` over frozen Gan builder-gap v1, S0-S4 aggregation arms, variance diagnostics, cost/latency reporting, and cap-25 gates. No model runs launched. |
| R14 - GEPA Failure Postmortem And Qwen Gate Design | Done; [gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md](../experiments/gan/gan_s0_r14_gepa_failure_postmortem_qwen_gate_design_20260528.md) concludes compact Qwen GEPA is not justified now; Qwen GEPA stays blocked until a hosted compact-delta instruction clears a cap gate. No model runs launched. |
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

- R11/R12/R13 design cards are done; R32-R37 are the active execution and analysis chain.
- R32 should run before R34 so the R11 date/event payload is tested before the CLINES entity-first gate depends on it.
- R33 should be written before any full-validation or Qwen-transfer follow-up from R11.
- R35 should compare against R33, not only against historical builder-gap metrics.
- R36/R37 can proceed after the R11/R12 run queue because self-consistency competes mainly for execution attention and cost tracking, not interface design.
- R14 is complete; Qwen GEPA stays blocked unless a hosted compact-delta gate first produces a short passing instruction.
- R31 is scorer infrastructure and should be completed before making any direct claim against Gan 2026 paper metrics.
- A3 depends on paper narrative need; A4 requires a new preregistration and cap-25 gate before full validation.
- B1 and B2 require explicit protocol decisions before implementation.

## Parallelization Opportunities

- **Safe now:** R32 implementation, R33 report scaffold, R34 implementation planning, R36 aggregation harness planning, and R31 scorer-mode design.
- **Run queue:** Execute R11 first (R32), analyze it (R33), then execute R12 (R34) and analyze it (R35). Run R13 (R36) after those unless there is a deliberate reason to spend compute earlier.
- **Single-threaded:** Any Qwen/Ollama model execution, self-consistency batches, and future GEPA gates.
- **Blocked together:** B1 and B2 depend on reporting/scorer protocol decisions.
- **Proceed after gates:** A7 after reviewing R11/R12 interfaces; A3 after paper-need confirmation; A4 after a new preregistration.

## Recommended Next Pull

1. **R32 - Implement and run the R11 Gan temporal/date cap-25 gate.** This is the first missing execution step after the completed design.
2. **R33 - Analyze R11 temporal/date results.** Decide whether the date/event interface deserves full validation, Qwen transfer, or redesign.
3. **R34 - Implement and run the R12 CLINES entity-first cap-25 gate.** Launch after R11 has produced enough evidence that the shared payload interface is usable.

This pull moves the board from preregistered designs into executable Gan S0 evidence.

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

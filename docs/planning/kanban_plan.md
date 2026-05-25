# Clinical Extraction Kanban Plan

**Active steering doc** - future work only. Closed pathways, rejected arms, and detailed walkthroughs live in [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md) and the linked experiment notes.

**Last refreshed:** 2026-05-25

## Current Priorities

1. **Resolve the Gan L2 Qwen exact-policy follow-through.** L2 forensics narrowed the local Gan gap to Qwen calibration and canonical-label selection under sparse candidate coverage. The slice and cap-25 follow-up are complete; the next empirical decision is whether to redesign the full-validation patch or rerun the promoted full-validation config.
2. **Keep manuscript evidence current.** ExECT S5 local transfer, the clean schema ladder, Gan G0 limits, and rejected mechanism arms now have a refreshed table pack and claims/caveats draft; future paper edits should cite those artifacts rather than older narrative-only drafts.
3. **Promote the former backlog into active gated threads.** Gan L2 cap-25, invalid-surface repair tests, best-closed anchors, S1 Qwen seizure-type analysis, and S5 frequency policy iteration should proceed once their listed dependencies or gates are complete.
4. **Keep new mechanism search tightly gated.** Pull only preregistered, narrow arms that answer a decision question. Avoid replaying closed pathways or stacking rejected techniques.
5. **Preserve reproducibility and scorer semantics.** No scorer, loader, or gold-label behavior changes without explicit tests and documentation.

## Recent Findings To Carry Forward

| Finding | Implication |
| --- | --- |
| ExECT S5 v2b is the current promoted stack: GPT 4.1-mini 85.8% micro / 73.9% frequency F1; Qwen3.6:35b 85.4% micro / 71.4% frequency F1. | Local S5 transfer is accepted as near-parity on synthetic validation, but the paper should not claim Qwen leads or deployment readiness. |
| The clean ExECT ladder is now coherent for Qwen after the S1 clean v2 correction: S1 85.9%, S2 84.4%, S3 75.3%, S4 67.5% micro. | Use the clean ladder for current local-model breadth claims; treat older S1 v4.10-only comparisons as superseded for ladder shape. |
| S2/S3 clean GPT anchors improved after transferable S5 lessons: S2 82.7%, S3 74.4% micro. | AM brand/non-ASM guard transferred; frequency-only and rejected S5 techniques stay out of S2/S3. |
| Gan G0 builder-gap v1 remains GPT-led: 80.6% monthly GPT vs 70.7% Qwen. L2 found 55 GPT-correct/Qwen-failed records and 24 Qwen-correct/GPT-failed records. | The local Gan gap is real but not uniform. Target Qwen policy calibration before any new full validation. |
| Gan residuals are dominated by exact rate/window drift, cluster collapse, and coarse-label fallback, mostly when deterministic candidates are absent. | Do not treat this as a scorer/data bug or a simple candidate-builder coverage issue. |
| S5 per-family parallel decomposition, S1 family-split probes, Gan unknown-overuse, GEPA G1/G2, high-precision frequency pruning, and medication temporal guard arms are rejected. | Keep these out of active planning unless a new preregistration changes the decision question. |

## Ready

### R1.1 - Gan L2 Qwen Exact-Policy Full Validation

- **Outcome:** Full validation (299 records) of the exact-policy Qwen prompt patch.
- **Dependencies:** v1.8 cap-25 schema gate.
- **Status:** Ready for full-validation launch when Ollama is free.
- **Notes:** v1.8 schema-validity prompt patch added after the v1.7 slice/cap-25 showed non-canonical outputs (`many per month`, `4 to 6 per cluster`, `1 per night`). Completed v1.8 cap-25 run `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T171037Z` plus deterministic post-hoc re-evaluation under the tightened validator has 100% schema validity, 100% evidence support, 72.0% monthly accuracy, 80.0% Purist, and 88.0% Pragmatic. See [gan_s0_l2_qwen_exact_policy_v1_8_cap25_schema_gate_20260525.md](../experiments/gan/gan_s0_l2_qwen_exact_policy_v1_8_cap25_schema_gate_20260525.md). A later clean cap-25 relaunch stalled after 1/25 and was stopped; premature full-validation processes were stopped before completion and are not evidence.

### R2 - Write Current Results Table Pack

- **Outcome:** Paper-facing table pack that separates operational defaults, local-vs-closed comparisons, arm rejects, and synthetic-validation caveats.
- **Dependencies:** none.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Tables trace each number to run IDs or frozen inspection docs; no metric copied from narrative-only sources.
- **Status:** Done.
- **Notes:** Completed as [paper_result_table_pack_20260525.md](../experiments/synthesis/paper_result_table_pack_20260525.md), using [paper_frozen_operational_defaults_20260524.md](../experiments/synthesis/paper_frozen_operational_defaults_20260524.md), [l1_2_s5_local_vs_closed_comparison_20260525.md](../experiments/synthesis/l1_2_s5_local_vs_closed_comparison_20260525.md), S1/S2/S3 clean-ladder inspections, [gan_s0_qwen35b_builder_gap_l2_error_forensics_20260525.md](../experiments/gan/gan_s0_qwen35b_builder_gap_l2_error_forensics_20260525.md), and the Gan exact-policy cap-25 inspection.

### R3 - Draft Manuscript Caveats And Claims

- **Outcome:** Short claims/caveats section covering synthetic validation, local-model transfer, Gan benchmark limits, scorer semantics, and rejected mechanism arms.
- **Dependencies:** none; benefits from R2 but can start in parallel.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Each claim is tied to a primary artifact; no deployment, real-world, or benchmark-reproduction claim exceeds current evidence.
- **Status:** Done.
- **Notes:** Completed as [paper_claims_caveats_20260525.md](../experiments/synthesis/paper_claims_caveats_20260525.md). Keeps "accepted local transfer" distinct from "deployment ready" and arm rejection distinct from mechanism rejection.

### R4 - Refresh Experiment Registry For Current Defaults

- **Outcome:** Registry and synthesis references identify the current default runs for Gan G0 and ExECT S1-S5, with superseded runs marked clearly.
- **Dependencies:** none.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Registry entries agree with this board and frozen operational defaults; superseded S5 Qwen v1/A3 comparison is not treated as v2b evidence.
- **Notes:** This is documentation hygiene only unless registry schema changes are required.

### R5 - Test Narrow Gan Invalid-Surface Repairs

- **Outcome:** Regression tests for one-to-one canonical surface repairs such as `many per month` -> `multiple per month` and `q2 - 3wk` -> `1 per 2 to 3 week`, if pursued.
- **Dependencies:** none.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Tests prove repairs do not alter broader cluster, unknown, or temporal-window semantics.
- **Notes:** This is surface normalization only, not a substitute for R1.

## In Progress

No active card is currently claimed in this board.

## Active Threads

These threads are no longer backlog. Keep them visible and proceed as soon as their dependencies or gates clear.

### A2 - Run Best-Closed Comparison Anchors

- **Outcome:** One controlled comparison per hard surface where a stronger closed model may matter.
- **Dependencies:** R2/R3 clarify which comparison would change the paper.
- **Parallelizable:** after prioritization.
- **Owner:** unassigned.
- **Validation:** Preregistered config, fixed scorer, explicit comparison group.
- **Notes:** Candidate anchors: GPT 5.5 on S4; GPT 5.5 or Gemini on S5 promoted stack; Gemini on Gan builder-gap v1.

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

### A5 - Test/Holdout Reporting Protocol and Runs (formerly B3)

- **Outcome:** Clear policy for when validation findings can move to test/holdout reporting, and overnight runs for frozen defaults.
- **Dependencies:** R1.1 completed/run, and protocol design.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Protocol prevents exploratory tuning from leaking into final reporting.
- **Notes:** Promoted to active threads to execute overnight runs of frozen configurations.

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

No active card remains in backlog. New backlog items should be useful but not ready or not urgent; otherwise place them in Ready or Active Threads with explicit dependencies.

## Done Or Frozen

| Area | Status |
| --- | --- |
| ExECT S5 v2b verifier + AM guard | Promoted for current operational default. |
| ExECT S5 Qwen true-v2b transfer | Done; accepted near-parity, not Qwen-leading. |
| ExECT S1/S2/S3 clean-ladder Qwen correction/replay | Done; use clean ladder for current breadth story. |
| ExECT S2/S3 clean-ladder GPT validation | Done. |
| Gan G0 builder-gap v1 | Frozen operational default; GPT 80.6%, Qwen 70.7% monthly. |
| Gan L2 Qwen forensics | Done; enables only the narrow exact-policy slice or surface-repair tests. |
| Gan L2 Qwen exact-policy slice | Done; run `gan_s0_l2_qwen_exact_policy_slice_qwen35b_ollama_20260525T160918Z` has 82.4% monthly accuracy but failed schema/canonical gate (94.4% schema, "many per month" non-canonical). Decision: Hold/Redesign; v1.8 schema-validity patch is now ready for rerun. |
| Gan L2 Qwen exact-policy cap-25 follow-up | Done but superseded for full-validation gating; v1.7 run `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T162702Z` has 69.6% monthly accuracy and 92% schema validity. v1.8 run `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T171037Z`, post-hoc re-evaluated under the tightened validator, has 72.0% monthly and 100% schema validity. Decision: proceed to full validation when local Ollama is free. |
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

- R1.1 is the only model-backed follow-through candidate; the v1.8 cap-25 schema gate is cleared with the caveat documented in the schema-gate note. Keep local Ollama free before full validation.
- R2 and R3 are complete; use the May 25 table pack and claims/caveats note for paper drafting.
- R5 can proceed independently, but should remain a test-backed surface-normalization task.
- A1 depends strictly on R1 passing the preregistered slice gate.
- A2 should wait until R2/R3 show which closed-model anchor would materially strengthen the paper.
- A3 depends on paper narrative need and should not consume local model capacity during R1.
- A4 requires a new preregistration and cap-25 gate before any full validation.
- A5 depends on R1.1 completion to isolate local model capacity, and establishing the protocol.
- B1 and B2 require explicit protocol decisions before implementation.

## Parallelization Opportunities

- **Safe now:** R4 and R5.
- **Single-threaded:** any renewed R1.1/Qwen/Ollama job.
- **Blocked together:** B1 and B2 depend on reporting/scorer protocol decisions.
- **Proceed after gates:** R1.1 after explicit restart/redesign decision; A5 sequentially after R1.1 completes; A2 is now unblocked for prioritization by the May 25 paper pack; A3 after paper-need confirmation; A4 after preregistration.

## Recommended Next Pull

1. **R4 - Refresh Experiment Registry For Current Defaults.**
2. **R5 - Test Narrow Gan Invalid-Surface Repairs.**
3. **R1.1 - Launch Gan exact-policy v1.8 full validation when local Ollama is free.**
4. **A5 - Establish Test/Holdout Reporting Protocol and prepare overnight runs.**

This pull keeps documentation traceability moving, starts the narrow test-backed Gan repair thread, runs R1.1 gate checks, and kicks off the test/holdout protocol and scripting.

## Standing Guardrails

- Do not silently change scorer semantics; update tests and document interpretation.
- Gan gold is `seizure_frequency_number[0]`; `reference[0]` is diagnostic only.
- Distinguish `unknown` from `no seizure frequency reference`.
- Keep arm rejection separate from mechanism rejection; name `decision_scope` in inspection docs.
- ExECT S5 families are diagnosis, seizure type, annotated medication, investigation, and seizure frequency.
- High-recall ExECT frequency candidates remain the baseline; high-precision pruning is rejected.
- S2/S3 clean-ladder ports include only transferable promoted S5 techniques.
- Do not overlap local Qwen jobs on the same Ollama instance.
- Cursor SDK drafts are leads, not evidence, until promoted from primary artifacts.

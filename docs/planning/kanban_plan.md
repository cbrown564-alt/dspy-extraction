# Clinical Extraction Kanban Plan

**Active steering doc** - future work only. Closed pathways, rejected arms, and detailed walkthroughs live in [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md) and the linked experiment notes.

**Last refreshed:** 2026-05-26

## Current Priorities

1. **Refresh registry references after the R9/Gan policy decision.** R4 should mark current defaults and superseded R1.1/R5-R9 artifacts now that the final Gan validation candidate (v1.8 + active recovery policy) is selected.
2. **Keep Gan holdout blocked until promotion review.** The Gan test candidate should not be selected from raw validation metrics alone; require an explicit promotion/hold note before creating or running a Gan test config.
3. **Run ExECT S5 v2b test holdout as the immediate A5 confirmation pair.** GPT 4.1-mini and Qwen3.6:35b S5 v2b are frozen validation defaults with matching test configs; report them as one-shot confirmation, not tuning feedback.
4. **Preserve reproducibility and scorer semantics.** No scorer, loader, gold-label, or test-holdout behavior changes without explicit tests and documentation.

## Recent Findings To Carry Forward

| Finding | Implication |
| --- | --- |
| ExECT current paper defaults are stable: S5 v2b is promoted; Qwen S1-S4 clean ladder is coherent; S2/S3 GPT anchors include only transferable S5 lessons. | Use the May 25 table pack and claims/caveats note for manuscript numbers; do not reopen ExECT defaults unless a paper claim requires it. |
| Gan G0 remains GPT-led: 80.6% monthly GPT vs 70.7% Qwen; Qwen errors are mixed, not a uniform local-model failure. | Target narrow Qwen policy/calibration gates rather than broad mechanism search. |
| Gan R1.1 full validation had useful category scores but failed schema validity: 70.3% monthly, 78.4% Purist, 83.3% Pragmatic, 90.0% schema validity. | Do not promote R1.1 as-is. R5-R8 added tested guards for null no-reference outputs, final-slot noncanonical labels, and narrow inequality repair. |
| R5-R8 preserve scorer semantics: invalid hybrids/concatenations/prose are rejected with metadata; leading inequality repair is allowed only when the stripped label is already canonical. | The guarded replay improved contract behavior, but R9 must decide whether quantified unknown hybrids are prevented upstream or handled by a verifier before any Gan test selection. |
| Gan R1.1 schema-guard replay is complete but not yet the final policy. | Treat `gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T092508Z` as validation evidence for R9/promotion review, not as an automatic holdout candidate. |
| Gan R9 recovery run is successful: v1.8 prompt + active recovery policy is the final choice. | Delivering 99.7% schema validity rate (1 invalid abstention) and 69.1% monthly accuracy (206 correct predictions, an absolute match increase of +7 over baseline). |
| GPT-4.1-mini exact policy validation run is successful. | Delivered 99.7% schema validity (1 invalid natural abstention) and 78.5% monthly frequency accuracy on the full validation split (299 records). |
| Rejected arms remain rejected: S5 per-family parallel decomposition, S1 family-split probes, Gan unknown-overuse, GEPA G1/G2, high-precision frequency pruning, and medication temporal guard arms. | Keep them out of active planning unless a new preregistration changes the decision question. |


## Ready

### R4 - Refresh Experiment Registry For Current Defaults

- **Outcome:** Registry and synthesis references identify the current default runs for Gan G0 and ExECT S1-S5, with superseded runs marked clearly.
- **Dependencies:** preferably after R9 determines the final Gan validation/promotion policy.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Registry entries agree with this board and frozen operational defaults; superseded S5 Qwen v1/A3 comparison is not treated as v2b evidence; Gan R1.1/R9 artifacts are clearly marked promoted, held, or superseded.
- **Notes:** Documentation hygiene only unless registry schema changes are required. Include R5-R9 and R1.1c artifacts when refreshing Gan entries.

## In Progress

*(No active cards in progress)*

## Active Threads

These threads are no longer backlog. Keep them visible and proceed as soon as their dependencies or gates clear.

### A2 - Run Best-Closed Comparison Anchors

- **Outcome:** One controlled comparison per hard surface where a stronger closed model may matter.
- **Dependencies:** paper-claim prioritization from the May 25 table pack and claims/caveats note.
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

- **Outcome:** Clear policy for when validation findings can move to test/holdout reporting, plus one-shot holdout runs for frozen defaults once eligible.
- **Dependencies:** ExECT S5 v2b GPT/Qwen can proceed now as a paired confirmation set; Gan holdout is blocked until R9 completes and a promotion/hold review selects the final Gan policy.
- **Parallelizable:** yes.
- **Owner:** unassigned.
- **Validation:** Protocol prevents exploratory tuning from leaking into final reporting; test configs must match frozen validation configs except for `split_name`, `report_on_test_split`, and test-prefixed IDs/output paths.
- **Notes:** Do not tune from ExECT S5 holdout results. Do not create or run a Gan test config from raw R1.1/R9 metrics alone; require promotion review first.

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
| Gan R9 - Address Gan Quantified Unknown Hybrids Upstream | Done; v1.8 prompt paired with prediction-bridge recovery policy is chosen as final Gan S0 configuration (99.7% schema validity, 69.1% monthly accuracy, 298 valid predictions). |
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

- R1.1 full validation and schema-guard replay are complete; R9 is the active Gan policy thread because quantified unknown hybrids remain semantic/policy failures.
- R5-R8 are complete; they repaired adapter contract behavior without changing scorer semantics, but they do not solve Qwen's unknown-prefix quantified-hybrid failures.
- R2 and R3 are complete; use the May 25 table pack and claims/caveats note for paper drafting.
- R4 is documentation hygiene and should follow the R9/Gan promotion-review decision unless someone specifically needs registry cleanup first.
- A2 should pull only if a closed-model anchor would materially strengthen a paper claim.
- A3 depends on paper narrative need and should not consume local model capacity during R9.
- A4 requires a new preregistration and cap-25 gate before any full validation.
- A5 ExECT S5 GPT/Qwen holdout is unblocked as a one-shot paired confirmation set; A5 Gan holdout is blocked until R9 plus promotion review.
- B1 and B2 require explicit protocol decisions before implementation.

## Parallelization Opportunities

- **Safe now:** ExECT S5 v2b GPT/Qwen test-holdout preparation can proceed under the frozen-config protocol; R4 can proceed only if it records current defaults without pre-deciding R9.
- **Single-threaded:** R9 and any renewed Gan Qwen/Ollama validation job.
- **Blocked together:** B1 and B2 depend on reporting/scorer protocol decisions.
- **Proceed after gates:** Gan holdout only after R9 validation evidence and promotion review; A2 is unblocked for prioritization by the May 25 paper pack; A3 after paper-need confirmation; A4 after preregistration.

## Recommended Next Pull

1. **R9 - Address Gan Quantified Unknown Hybrids Upstream.**
2. **Run/inspect the R9 cap-25 gate under unchanged scorer semantics.**
3. **A5 - Run ExECT S5 v2b GPT/Qwen test holdout as a paired one-shot confirmation set.**
4. **Gan promotion review - decide whether R9/R1.1 becomes the final Gan test candidate.**
5. **R4 - Refresh Experiment Registry For Current Defaults.**

This pull tests whether Gan's remaining quantified-unknown hybrid failures can be prevented upstream before any final Gan policy or holdout candidate is selected, while allowing ExECT S5 holdout confirmation to proceed independently.

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

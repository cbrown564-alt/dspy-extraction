# Clinical Extraction Kanban Plan

**Active steering doc** - sole execution board for current and near-future work. Detailed completed run ledgers live in inspection docs, learning logs, synthesis docs, and `docs/planning/kanban_frozen_threads_history.md`.

**Last refreshed:** 2026-05-23

## Steering References

| Purpose | Source |
| --- | --- |
| Core research direction | `docs/outline.md` |
| Hybrid research doctrine | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| Mechanism status | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| Scorer / dataset guardrails | `docs/policies/deterministic_scorer_semantics.md`, `docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md` |
| Active run / decision registry | `docs/experiments/synthesis/experiment_registry.json` |
| Historical detail archive | `docs/planning/kanban_frozen_threads_history.md` |

## Current Focus

The active work is now housekeeping and controlled follow-through after the Gan builder-gap and Cursor SDK findings:

1. Make the review-only Cursor SDK operating mode visible in the source docs.
2. Preserve and verify the recovered Gan candidate-builder code state before any rerun.
3. Decide whether to spend on a verified G16 GPT full-validation rerun.
4. Decide whether the paper needs ExECT S2/S3 model-suite extension evidence.

No Qwen transfer, registry promotion, or operational-default change is cleared from the stale G16 artifact.

## Active Board

### Ready

| Card | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- |
| **C11 - Refresh SDK workflow index / source docs** | `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md` and `docs/memory/workflow_index.md` reflect the promoted review-only operating mode, canonical draft folders, mutating-workflow block, and draft-to-source promotion boundary | C10 completed | yes | Source docs point to canonical draft folders; mutating SDK workflows remain blocked outside disposable worktrees |
| **G17 - Preserve Gan builder-gap code state** | Recovered `gan_s0_candidate_builder_gap_v1` deterministic builder state is protected before model spend, with a clear commit/stash/branch decision recorded outside the run artifact | G16 reconciliation | no | `git status` reviewed; no-model checks pass on the preserved state |
| **M3 - Decide S2/S3 model-suite extension** | Explicit yes/no note for `model_suite_exect_s2_s3_extension_v1`; default is no further model runs unless the paper needs middle-ladder model-profile evidence | Completed frozen model suite | yes | Decision note cites the current model-suite synthesis and paper need |

### Blocked / Gated

| Card | Blocker | Release Condition | Validation |
| --- | --- | --- | --- |
| **G18 - Verified G16 GPT full-validation rerun** | Do not rerun until G17 preserves the recovered builder state and no-model parity checks pass immediately before launch | Accepted code state plus rerun decision | Rerun `configs/experiments/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation.json`; inspection must report enriched-slice candidate parity and full-split gold-in-candidates coverage |
| **C12 - Mutating SDK workflow protocol** | Shared dirty workspace is unsafe for SDK mutation workflows | Disposable clone/worktree with explicit rollback protocol | Pre/post `git status`; rollback affects disposable workspace only |
| **Provider adapter validation backlog** | Cursor SDK compatibility report is review-only; no config changes promoted from it | Targeted tests are planned before provider config changes | `uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py` plus relevant provider smoke checks |

### Backlog / Deferred

| Item | Status | Trigger |
| --- | --- | --- |
| Registry / paper-claim backfill for G16 | Deferred | Only after a verified rerun or an explicit reject/hold decision from primary artifacts |
| Targeted Gan examples | Optional | Only after candidate coverage work stabilizes; keep as narrow single-family packs |
| LLM candidate extraction | Open mechanism | Needs stricter candidate schema and numeric slots before more model spend |
| Candidate-constrained verification | Open mechanism | Revisit only after candidate recall improves |
| Published ExECTv2 reproduction | Blocked | CUI-aware all-family scoring |
| Gan Real(300)/Real(150) | Blocked | Data access |
| Test holdout reporting | Deferred | Only for arms clearing dev/cap gates with explicit test-reporting config |
| Optimizer rungs / GEPA | Deferred | Requires a narrow preregistered objective and train-demo alignment |

## Recommended Next Pull

1. **C11 - Refresh SDK workflow index / source docs.** This is the cleanest immediate pull because it removes stale routing outside the Kanban without touching scorer, dataset, or model code.
2. **G17 - Preserve Gan builder-gap code state.** Do this before any more G16 discussion turns into model spend.
3. **M3 - Decide S2/S3 model-suite extension.** Keep this as a paper-need decision, not an inertia run.

## Parallelization Notes

- C11 and M3 can run in parallel because they touch different source docs.
- G17 and G18 should stay single-threaded because they govern the shared Gan candidate-builder contract and model-spend gate.
- Provider adapter validation can proceed independently if it stays test-only and does not change provider configs.
- Mutating SDK workflow work must not run in the shared workspace.

## Operational Defaults

| Track | Default | Evidence / Caveat |
| --- | --- | --- |
| Gan S0 | Expanded builders + prose F0 for full-validation model comparisons; v1.4 no-example policy remains the GPT enriched-slice control | F0 GPT full 68.1% monthly; builder-gap G16 artifact is stale-check evidence only |
| ExECT S1 | v4_10 + inline bridges on all tracks | GPT full 92.3% micro; Qwen v4.12 rejected at cap-25 |
| ExECT S2 | Frozen GPT v1.3 | 80.9% micro; five-family scope |
| ExECT S3 | Frozen GPT v1.2 | 72.1% micro; accepted comorbidity gap |
| ExECT S4 | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | GPT full 65.5% micro; frequency remains weak |
| Cursor SDK | Review-only research operations assistant | Drafts are not source-of-truth edits, benchmark evidence, registry rows, or paper claims until human/Codex promotion |

## Recent Findings Moved Out Of The Board

| Finding | Current Status | Source Of Detail |
| --- | --- | --- |
| Gan G11-G15 builder-gap slice work | Completed; slice gate passed | `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` |
| Gan G16 full-validation artifact | Reconciled as rerun-risk / stale-check evidence; not promoted | `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_reconciliation_20260523.md` |
| Cursor SDK pilot and evening queue | Promoted as review-only operations guidance; canonical drafts remain draft artifacts | `docs/workstreams/cursor_sdk/cursor_sdk_value_reliability_assessment_20260523.md`, `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md` |
| Frozen model suite | Complete for planned tracks; synthesis-only unless paper need changes | `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md`, `docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md` |
| Historical ExECT / Gan run arcs | Archived | `docs/planning/kanban_frozen_threads_history.md` |

## Standing Guardrails

- Do not silently change scorer semantics. If scorer behavior changes, update tests and document interpretation.
- Gan primary gold is `seizure_frequency_number[0]`; `reference[0]` is a secondary difficulty signal.
- Evidence support is diagnostic unless an experiment explicitly makes it prediction-affecting.
- Keep arm rejection separate from mechanism closure.
- Do not promote model-suite leaderboard results to operational defaults.
- Do not run Qwen transfer for Gan builder-gap v1 until a trustworthy GPT full-validation run clears the gate.
- Do not let SDK-generated prose become evidence for paper claims unless it points to primary artifacts and is manually promoted.

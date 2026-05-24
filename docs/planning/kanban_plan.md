# Clinical Extraction Kanban Plan

**Active steering doc** - sole execution board for current and near-future work. Detailed completed run ledgers live in inspection docs, learning logs, synthesis docs, and `docs/planning/kanban_frozen_threads_history.md`.

**Last refreshed:** 2026-05-24

## Steering References

| Purpose | Source |
| --- | --- |
| Core research direction | `docs/outline.md` |
| Hybrid research doctrine | `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` |
| Mechanism status | `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md` |
| Scorer / dataset guardrails | `docs/policies/deterministic_scorer_semantics.md`, `docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md` |
| Active run / decision registry | `docs/experiments/synthesis/experiment_registry.json` |
| Cursor SDK expansion | `docs/workstreams/cursor_sdk/cursor_sdk_capability_expansion_report_20260524.md` |
| Historical detail archive | `docs/planning/kanban_frozen_threads_history.md` |

## Current Focus

The 2026-05-23 housekeeping and controlled follow-through pass is complete:

1. Cursor SDK operating mode is now review-only in source docs, with canonical draft folders and live mutation blocking.
2. The recovered Gan candidate-builder code state is preserved by commit and verified with no-model checks.
3. The verified GPT full-validation rerun completed and supersedes the stale G16 artifact.
4. ExECT S2/S3 model-suite extension is explicitly declined unless the paper later needs a middle-ladder claim.
5. The Gan operational-default promotion review is completed, promoting `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini to the operational default.
6. The Qwen transfer preregistration decision (G20) is complete; preregistration and config for the Qwen candidate-builder gap v1 validation are drafted.
7. The Qwen transfer validation run (G21) completed successfully, achieving 70.7% monthly accuracy and satisfying all preregistered validation gates. The run has been registered in the experiment registry.
8. The paper-synthesis update for Gan builder-gap v1 and post-suite priorities is complete as a source synthesis note.
9. Cursor SDK capability expansion is now scoped: keep authority review-only in the shared workspace, but test higher-throughput orchestration through ledgers, draft indexes, review swarms, disposable worktrees, DAG-style jobs, and later cloud/PR experiments.

## Active Board

### Ready

| Card | Intended outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- |
| **C13 - Cursor SDK instrumentation and draft index** | Create the bookkeeping layer needed before high-volume SDK experimentation: run ledger, canonical draft index, prompt-rehearsal vs live-draft naming, and review statuses for existing SDK outputs. | C12 remains gated for mutating work; C13 is review/index only | yes | Index names canonical/substantive/stub/superseded drafts; no source-of-truth claims promoted from SDK drafts |

### Completed

| Card | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- |
| **C13 prep - Cursor SDK capability expansion report** | Reviewed implementation outcomes, external SDK patterns, reliability risks, and a staged weekend experiment program for broader SDK use. | Cursor SDK pilot/evening queue complete | yes | Report at `docs/workstreams/cursor_sdk/cursor_sdk_capability_expansion_report_20260524.md` |
| **P1 - Paper synthesis update for Gan builder-gap and post-suite priorities** | Paper-facing source note incorporates the verified GPT builder-gap default, Qwen transfer result, frozen-suite status, claim-readiness caveats, and next priorities after current Kanban completion. | G21 completed; frozen model suite completed | yes | Source synthesis at `docs/experiments/synthesis/paper_synthesis_update_20260524.md` |
| **G21 - Qwen transfer validation run** | Qwen3.6:35b run achieved 70.7% monthly accuracy, clearing all validation gates. Registered in registry. | G20 completed | yes | Inspection document at `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_inspection_20260523.md` |
| **G20 - Qwen transfer preregistration decision** | Preregistration and config drafted; decision made to test Qwen transferability | G19 completed | yes | Preregistration document at `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_preregistration_20260523.md` |

### Blocked / Gated

| Card | Blocker | Release Condition | Validation |
| --- | --- | --- | --- |
| **C12 - Mutating SDK workflow protocol** | Shared dirty workspace is unsafe for SDK mutation workflows | Disposable clone/worktree with explicit rollback protocol | Pre/post `git status`; rollback affects disposable workspace only |
| **Provider adapter validation backlog** | Cursor SDK compatibility report is review-only; no config changes promoted from it | Targeted tests are planned before provider config changes | `uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py` plus relevant provider smoke checks |

### Backlog / Deferred

| Item | Status | Trigger |
| --- | --- | --- |
| Registry / paper-claim backfill for stale G16 artifact | Superseded | Use the verified rerun artifact instead |
| Targeted Gan examples | Optional | Only after candidate coverage work stabilizes; keep as narrow single-family packs |
| LLM candidate extraction | Open mechanism | Needs stricter candidate schema and numeric slots before more model spend |
| Candidate-constrained verification | Open mechanism | Revisit only after candidate recall improves |
| Published ExECTv2 reproduction | Blocked | CUI-aware all-family scoring |
| Gan Real(300)/Real(150) | Blocked | Data access |
| Test holdout reporting | Deferred | Only for arms clearing dev/cap gates with explicit test-reporting config |
| Optimizer rungs / GEPA | Deferred | Requires a narrow preregistered objective and train-demo alignment |
| Cursor SDK cloud/PR experiments | Deferred until C13 and disposable-worktree protocol | Use only after run ledger, draft index, and mutating workflow isolation are verified |

## Recommended Next Pull

1. **C13 Cursor SDK instrumentation and draft index.** Build the run ledger/review index before exploiting the discounted SDK window; this unlocks safe review swarms and later disposable mutation sprints.
2. **Paper result table freeze.** Convert the current source syntheses into a compact manuscript table pack with run IDs, configs, splits, scorer modes, denominators, decision scopes, and caveats.
3. **Gan builder-gap residual forensics.** Compare GPT and Qwen builder-gap mismatches by candidate availability, gold pragmatic stratum, invalid-label cases, and semantic mismatch type before opening another model-backed arm.
4. **Provider adapter validation backlog.** Keep this test-only unless a config change is explicitly pulled.

## Parallelization Notes

- Paper result table freeze and Gan builder-gap residual forensics can run in parallel if the table work stays source-only and does not reinterpret residual categories.
- C13 can run in parallel with paper/result analysis because it should only index SDK artifacts and add bookkeeping, not promote draft claims or edit experiment conclusions.
- Provider adapter validation can proceed independently if it stays test-only and does not change provider configs.
- Mutating SDK workflow work must not run in the shared workspace.
- Cursor SDK review-only swarms can start after C13 produces a ledger/index; disposable mutation sprints remain gated by C12.
- Any new Gan model-backed arm should wait for residual forensics and a preregistered decision question.

## Operational Defaults

| Track | Default | Evidence / Caveat |
| --- | --- | --- |
| Gan S0 | `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini is the operational default | Rerun 80.6% monthly, 86.0% Purist, 88.6% Pragmatic on Gan synthetic validation |
| ExECT S1 | v4_10 + inline bridges on all tracks | GPT full 92.3% micro; Qwen v4.12 rejected at cap-25 |
| ExECT S2 | Frozen GPT v1.3 | 80.9% micro; five-family scope |
| ExECT S3 | Frozen GPT v1.2 | 72.1% micro; accepted comorbidity gap |
| ExECT S4 | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | GPT full 65.5% micro; frequency remains weak |
| Cursor SDK | Review-only research operations assistant | Drafts are not source-of-truth edits, benchmark evidence, registry rows, or paper claims until human/Codex promotion |

## Recent Findings Moved Out Of The Board

| Finding | Current Status | Source Of Detail |
| --- | --- | --- |
| Cursor SDK source-doc refresh | Completed; review-only mode and mutation block promoted | `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md`, `docs/memory/workflow_index.md`, `scripts/cursor_sdk_workflows.py` |
| Gan G17 preservation gate | Completed; recovered builder state preserved by commit and no-model checks passed | `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_preservation_note_20260523.md` |
| Gan G18 verified GPT rerun | Completed; verified rerun supersedes stale G16 artifact | `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`, `runs/gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` |
| Gan G19 registry backfill | Completed for verified rerun; later promotion review moved builder-gap v1 to operational default | `docs/experiments/synthesis/experiment_registry.json`, `docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md` |
| ExECT S2/S3 model-suite extension decision | Completed; do not run unless paper need reopens | `docs/experiments/synthesis/model_suite_exect_s2_s3_extension_v1_decision_20260523.md` |
| Paper synthesis update for Gan builder-gap and post-suite priorities | Completed; source note added for final results narrative and next-priority sequencing | `docs/experiments/synthesis/paper_synthesis_update_20260524.md` |
| Gan G11-G15 builder-gap slice work | Completed; slice gate passed | `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_preregistration_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_slice_inspection_20260523.md` |
| Gan G16 full-validation artifact | Reconciled as rerun-risk / stale-check evidence; not promoted | `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_reconciliation_20260523.md` |
| Cursor SDK pilot and evening queue | Promoted as review-only operations guidance; canonical drafts remain draft artifacts | `docs/workstreams/cursor_sdk/cursor_sdk_value_reliability_assessment_20260523.md`, `docs/workstreams/cursor_sdk/cursor_sdk_research_workflows_20260523.md` |
| Cursor SDK capability expansion review | Completed; recommends moving from single-agent drafting to instrumented review swarms, DAG jobs, and disposable-worktree mutation experiments while preserving shared-workspace guardrails | `docs/workstreams/cursor_sdk/cursor_sdk_capability_expansion_report_20260524.md` |
| Frozen model suite | Complete for planned tracks; synthesis-only unless paper need changes | `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md`, `docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md` |
| Historical ExECT / Gan run arcs | Archived | `docs/planning/kanban_frozen_threads_history.md` |

## Standing Guardrails

- Do not silently change scorer semantics. If scorer behavior changes, update tests and document interpretation.
- Gan primary gold is `seizure_frequency_number[0]`; `reference[0]` is a secondary difficulty signal.
- Evidence support is diagnostic unless an experiment explicitly makes it prediction-affecting.
- Keep arm rejection separate from mechanism closure.
- Do not promote model-suite leaderboard results to operational defaults.
- Do not run further Gan builder-gap transfer or model-backed arms without a preregistered decision question after residual forensics.
- Do not let SDK-generated prose become evidence for paper claims unless it points to primary artifacts and is manually promoted.
- Do not run high-volume SDK swarms without a run ledger and draft index; do not run SDK mutation outside disposable worktrees with pre/post git status captured.

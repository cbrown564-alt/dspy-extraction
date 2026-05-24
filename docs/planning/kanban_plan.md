# Clinical Extraction Kanban Plan

**Active steering doc** - sole execution board for current and near-future work. Detailed completed run ledgers live in inspection docs, learning logs, synthesis docs, and [kanban_frozen_threads_history.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/planning/kanban_frozen_threads_history.md).

**Last refreshed:** 2026-05-24

## Steering References

| Purpose | Source |
| --- | --- |
| Core research direction | [outline.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/outline.md) |
| Hybrid research doctrine | [hybrid_pipeline_research_pivot_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md) |
| Mechanism status | [hybrid_pipeline_mechanism_status_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md) |
| Scorer / dataset guardrails | [deterministic_scorer_semantics.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/policies/deterministic_scorer_semantics.md), [exect_gold_label_audit.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/datasets/exect/exect_gold_label_audit.md), [gan_2026_label_audit.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/datasets/gan/gan_2026_label_audit.md) |
| Active run / decision registry | [experiment_registry.json](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/experiment_registry.json) |
| ExECT post-Gan experiment structure | [exect_post_gan_s0_experiment_structure_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_post_gan_s0_experiment_structure_20260524.md) |
| Pipeline review questions | [core_research_questions_pipeline_review_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/core_research_questions_pipeline_review_20260524.md) |
| Model configuration backlog | [model_config_compatibility_backlog_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/policies/model_config_compatibility_backlog_20260524.md) |
| Cursor SDK review-only operations | [README.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/README.md), [cursor_sdk_review_queue_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_review_queue_20260524.md) |
| Historical detail archive | [kanban_frozen_threads_history.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/planning/kanban_frozen_threads_history.md) |

## Current Focus

The immediate research focus is **ExECT pipeline decomposition after the Gan S0 lift**, alongside resolving **Gan S0 residual error forensics** and **model config compatibility validations**.

ExECT S5 is defined as a reporting/experiment surface covering core fields: `diagnosis`, `seizure_type`, `annotated_medication`, `investigation`, and `seizure_frequency`. Since frequency candidate recall was successfully resolved to 100% in E6, we can proceed to evaluate stage counts and executor placement grids for ExECT S5.

Primary research question:
> For ExECT core clinical extraction, what pipeline decomposition works best, what mix of deterministic and LLM components should each stage use, and where should those components sit in the pipeline?

Execution order:
1. **ExECT S1 first**: use the narrow high-support surface to search Axis 1 and Axis 2 cleanly. (Complete)
2. **Then ExECT S5**: use the gold/evidence-sufficient core set. (Active / Ready)
3. **Then S4 targeted follow-through**: only for S4-only or broad-family residuals that S5 does not cover.
4. **S2/S3 fill-in**: only when needed to support S5/S4 claims or guard regressions.

## Active Board

### Ready

| Card | Intended outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- |
| **Gan builder-gap residual forensics** | Run forensics on remaining Gan synthetic validation errors (unresolved/imprecise monthly frequencies) to determine if errors stem from candidate-recall, adjudication, or model semantics. | Gan S0 candidate-builder gap v1 complete | yes | Forensics report documenting error patterns and linking to target validation notes |
| **Provider adapter validation (B2/B3)** | Implement runtime environment check for hosted API keys (B2) and pair high-context settings with explicit timeouts for local Qwen runs (B3). | [model_config_compatibility_backlog_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/policies/model_config_compatibility_backlog_20260524.md) | yes | [test_llm_adapters.py](file:///c:/Users/cbrow/Code/dspy-extraction/tests/test_llm_adapters.py) and [test_model_comparison_configs.py](file:///c:/Users/cbrow/Code/dspy-extraction/tests/test_model_comparison_configs.py) passing |
| **Paper result table freeze** | Convert current source syntheses into compact manuscript table pack with run IDs, configs, splits, scorer modes, denominators, decision scopes, and caveats. | Current source syntheses complete | yes | Table rows cite primary run artifacts / registry paths and avoid SDK drafts as evidence |
| **E7 - ExECT medication temporality precision work** | Improve precision for medication temporality using post-classifiers or custom prompt policy checks. | None | yes | Run precision metric checks on ExECT validation split |
| **S2/S3 middle-ladder reruns** | Re-evaluate intermediate schema complexity levels (S2/S3) on validation to serve as regression guards or paper-ready comparison anchors. | E4/E5 scaffold completed | yes | Run validation scripts for S2/S3 programs |
| **LLM candidate extraction** | Explore structured slot/JSON candidate formats generated by LLM for Gan/ExECT. | None | yes | Strict candidate schema and numeric validators checked |
| **Candidate-constrained verification** | Run verifiers only on candidate lists to assess precision vs recall trade-offs. | None | yes | Score verifiers against baseline extraction |
| **Optimizer rungs / GEPA** | Run targeted few-shot optimization using dspy.BootstrapFewShot or other compile-time optimizers on Gan validation split under constrained budget. | None | yes | Comparison metrics stored in registry |
| **Cursor SDK cloud/PR experiments** | Set up automated pull-request review-only workflows. | SDK runner sanity checked | yes | Review-only logs generated on clean PR branch |
| **ExECT separate field extractor agents** | Evaluate latency/cost vs performance of separate field extractor agents vs monolithic extraction. | [core_research_questions_pipeline_review_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/core_research_questions_pipeline_review_20260524.md) | yes | Metric comparison against monolithic baseline |
| **High-recall vs high-precision candidate generation** | Run empirical comparison of extraction performance under high-recall vs high-precision candidate lists. | [core_research_questions_pipeline_review_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/core_research_questions_pipeline_review_20260524.md) | yes | Recall/precision metric logs |

### Completed / Reconciled

| Card | Outcome | Validation |
| --- | --- | --- |
| **Gan S0 multi-year seizure-free candidate helper** | Completed; implemented narrow candidate helper for `seizure free for multiple year` wording, resolving candidate recall gaps for `gan_13574` and `gan_13598` and lifting enriched gap slice candidate coverage from 23/25 to 25/25. | [test_gan_temporal_candidates.py](file:///c:/Users/cbrow/Code/dspy-extraction/tests/test_gan_temporal_candidates.py) and updated [gan_s0_candidate_builder_gap_audit_20260523.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md) |
| **E1 - ExECT S1 pipeline decomposition audit** | Reconciled active Kanban with existing S1 Axis 1/2 artifacts; no rerun needed. The preregistered Axis 1 grid already exists with stable `stage_graph_id`, bridge modes, fixed controls, and open cells. | [exect_s1_pipeline_decomposition_audit_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s1_pipeline_decomposition_audit_20260524.md); [exect_s1_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md), [exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| **E2 - ExECT S1 Axis 1 cap-25 grid** | Completed previously; `g1_l1_policy_bridges` and `g2_raw_post_bridge` tied at 95.8% micro F1 on GPT cap-25. Bridge-free verify/repair and section-aware split are rejected as arms, not mechanisms. | [exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md) |
| **E3 - ExECT S1 stage-executor placement grid** | Completed previously; inline and post bridge executors tied at 95.8% micro F1. Deterministic hint executors regressed on cap-25 and should not advance without a new implementation-variant preregistration. | [exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| **E4 - Define and scaffold ExECT S5 core surface** | Completed; S5 is now documented as diagnosis, seizure type, annotated medication, investigation, and seizure frequency, with medication temporality excluded. A reporting-surface scorer entry point exists without changing existing S1-S4 semantics. | [exect_s5_core_surface_design_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s5_core_surface_design_20260524.md); [exect.py](file:///c:/Users/cbrow/Code/dspy-extraction/src/clinical_extraction/evaluation/exect.py); [test_exect_s5_scoring.py](file:///c:/Users/cbrow/Code/dspy-extraction/tests/test_exect_s5_scoring.py) |
| **S4/S5 frequency gold-template audit** | Completed; current deterministic note-anchored frequency candidates cover only 5/43 validation gold labels (11.6%) and fully cover 2/24 validation gold-bearing documents. E5 model-grid spend should remain held; pull a narrow E6 deterministic candidate iteration first. | [exect_s4_s5_frequency_gold_template_audit_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s4_s5_frequency_gold_template_audit_20260524.md); local machine-readable artifact `artifacts/audits/exect_s4_s5_frequency_gold_template_audit_20260524.json` |
| **E6 - ExECT S4 frequency implementation iteration** | Completed; improved note-anchored candidate recall from 11.6% to 100% on the validation split (43/43 labels matched) without modifying gold loaders or breaking repository tests. Added robust coverage for breakthroughs after periods, date-ago zero-rate mappings, last seizure dates, and expanded qualitative change triggers. | [primitives.py](file:///c:/Users/cbrow/Code/dspy-extraction/src/clinical_extraction/exect/primitives.py), [test_exect_frequency_primitives.py](file:///c:/Users/cbrow/Code/dspy-extraction/tests/test_exect_frequency_primitives.py), `artifacts/audits/exect_s4_s5_frequency_gold_template_audit_20260524_E6.json` |
| **E5 - ExECT S5 Axis 1 / Axis 2 grid** | Completed; evaluated baseline vs. pre-vocab vs. post-merge frequency candidate architectures. Pre-vocab (H2_pre) achieved a massive +13.4pp F1 lift in `seizure_frequency` (from 47.1% to 60.5%) while post-merge (H1_post) degraded F1 to 28.0% due to precision collapse from lack of model adjudication. | Three cap-25 JSON configs under `configs/experiments/`; [walkthrough.md](file:///C:/Users/cbrow/.gemini/antigravity/brain/de91868f-93ee-408c-9032-d6dbd4f81892/walkthrough.md) and metrics reports in runs |
| **C12 - Mutating SDK workflow protocol** | Completed operationally; one live `test-mutations` pilot ran in a detached disposable worktree with marker gating, captured a proposed Gan temporal-candidate diff, ran focused tests, and rolled back without touching the shared workspace. Mutation output remains review-only and was not promoted into source code. | Live run `20260524T082000Z`; report/ledger copies preserved outside the source tree at `C:/Users/cbrow/Code/dspy-extraction-cursor-pilot-artifacts/`; shared and disposable `git status --short` clean after run; [test_cursor_sdk_workflows.py](file:///c:/Users/cbrow/Code/dspy-extraction/tests/test_cursor_sdk_workflows.py) |
| **C13 - Cursor SDK instrumentation and draft index** | Completed enough for operational use; ledgering, draft indexing, and mutation gating exist. Cursor SDK remains a review-only operations assistant, with mutating workflows allowed only in disposable worktrees. | [cursor_sdk_run_ledger_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md), [cursor_sdk_draft_index_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md), [cursor_sdk_disposable_worktree_protocol_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_disposable_worktree_protocol_20260524.md) |

### In Progress / Review

| Card | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- |
| **Triage paper & hygiene drafts** | Parallel triage of newly generated paper narrative and documentation hygiene reports using the Cursor SDK. | SDK run `20260524T093308Z` and `20260524T093256Z` | yes | Review queue updated; source files indexed |

### Blocked / Gated

| Card | Blocker | Release Condition | Validation |
| --- | --- | --- | --- |
| **Published ExECTv2 reproduction** | CUI-aware all-family scoring and original Table 1 alignment remain unresolved | Explicit reproduction workstream reopened | CUI-aware scorer, per-item/per-letter metrics, and benchmark-reference denominator checks |
| **Gan Real(300)/Real(150)** | Real dataset access unavailable | Data access | Data manifest update and preregistered test-reporting protocol |

### Backlog / Deferred

| Item | Status | Trigger |
| --- | --- | --- |
| **Test holdout reporting** | Deferred | Only for arms clearing dev/cap gates with explicit test-reporting config |

## Recommended Next Pull

1. **E5 ExECT S5 Axis 1 / Axis 2 grid.** Run the S5 pipeline stage-graph and placement comparison grids.
2. **Gan builder-gap residual forensics.** Run error diagnostics on remaining Gan synthetic validation cases.
3. **Gan S0 multi-year seizure-free candidate helper.** Implement narrow helper for long-remission phrases to resolve `gan_13574`/`gan_13598`.
4. **Provider adapter validation (B2/B3).** Address compatibility and environment backlog items from [model_config_compatibility_backlog_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/policies/model_config_compatibility_backlog_20260524.md).

## Parallelization Notes

- E5 execution is blocked on E6 candidate recall success (Complete), so E5 can be run immediately.
- Gan forensics can proceed in parallel because it is a diagnostic read of validation records, not a pipeline execution.
- Gan S0 multi-year seizure-free candidate helper can proceed independently as a deterministic candidate enhancement.
- Provider adapter validation checks (B2/B3) can proceed independently since they are test-only config checks and do not touch extraction runs.
- Mutating SDK workflow work must not run in the shared workspace; live mutation is allowed only inside a clean disposable worktree with marker gating and post-run rollback proof.

## Operational Defaults

| Track | Default | Evidence / Caveat |
| --- | --- | --- |
| Gan S0 | `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini is the operational default | Rerun 80.6% monthly, 86.0% Purist, 88.6% Pragmatic on Gan synthetic validation |
| ExECT S1 | v4_10 + inline bridges on all tracks | GPT full 92.3% micro; Qwen v4.12 rejected at cap-25 |
| ExECT S2 | Frozen GPT v1.3 | 80.9% micro; five-family scope |
| ExECT S3 | Frozen GPT v1.2 | 72.1% micro; accepted comorbidity gap |
| ExECT S4 | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | GPT full 65.5% micro; frequency remains weak |
| ExECT S5 | Scorer scaffold implemented for diagnosis, seizure type, medication, investigation, frequency | Reporting/experiment surface to test core fields with sufficient gold/evidence support; no model program promoted yet |
| Cursor SDK | Review-only research operations assistant with verified disposable-worktree mutation protocol | Drafts and mutation diffs are not source-of-truth edits, benchmark evidence, registry rows, or paper claims until human/Codex promotion |

## Recent Findings Summary

| Finding | Current Status | Source Of Detail |
| --- | --- | --- |
| ExECT S5 core surface | Completed; S5 is a reporting/experiment surface over diagnosis, seizure type, annotated medication, investigation, and seizure frequency; medication temporality remains S4-only | [exect_s5_core_surface_design_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s5_core_surface_design_20260524.md), [test_exect_s5_scoring.py](file:///c:/Users/cbrow/Code/dspy-extraction/tests/test_exect_s5_scoring.py) |
| ExECT S1 Axis 1/2 reconciliation | Completed; existing 2026-05-21 stage-graph and executor grids satisfy E1/E2/E3, so the next active ExECT pull is S5 core-surface design rather than rerunning S1 cap-25 grids | [exect_s1_pipeline_decomposition_audit_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s1_pipeline_decomposition_audit_20260524.md), [exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md), [exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md) |
| Gan G11-G21 builder-gap program | Completed; GPT 4.1-mini builder-gap v1 promoted to Gan S0 operational default, Qwen transfer accepted | [gan_s0_candidate_builder_gap_audit_20260523.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md), [gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md), [gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_inspection_20260523.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_inspection_20260523.md) |
| Frozen model suite | Complete for planned S1/S4/Gan F0 tracks; source-only unless paper need changes | [model_suite_pattern_interpretation_20260522.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md), [model_suite_qwen27b_full_validation_v1_inspection_20260523.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md) |
| ExECT S2/S3 model-suite extension | Declined unless paper later needs a middle-ladder claim | [model_suite_exect_s2_s3_extension_v1_decision_20260523.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/model_suite_exect_s2_s3_extension_v1_decision_20260523.md) |
| Paper synthesis after Gan lift | Completed as source note; final tables still pending | [paper_synthesis_update_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/synthesis/paper_synthesis_update_20260524.md) |
| Cursor SDK mutation pilot | Completed operationally; live `test-mutations` succeeded in a disposable worktree, captured a Gan temporal-candidate helper diff, ran focused tests, and rolled back cleanly. The diff remains review-only and was not promoted into the shared workspace. | [cursor_sdk_disposable_worktree_protocol_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_disposable_worktree_protocol_20260524.md); live run `20260524T082000Z`; [gan_s0_cursor_sdk_mutation_pilot_review_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/experiments/gan/gan_s0_cursor_sdk_mutation_pilot_review_20260524.md) |
| Cursor SDK instrumentation | Completed enough for review-only workflows; mutating workflows are now protocol-verified but remain disposable-worktree-only | [cursor_sdk_run_ledger_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md), [cursor_sdk_draft_index_20260524.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md) |
| Historical detailed run arcs | Archived / source docs only | [kanban_frozen_threads_history.md](file:///c:/Users/cbrow/Code/dspy-extraction/docs/planning/kanban_frozen_threads_history.md), `docs/experiments/exect/`, `docs/experiments/gan/` |

## Standing Guardrails

- Do not silently change scorer semantics. If scorer behavior changes, update tests and document interpretation.
- Gan primary gold is `seizure_frequency_number[0]`; `reference[0]` is a secondary difficulty signal.
- Evidence support is diagnostic unless an experiment explicitly makes it prediction-affecting.
- Keep arm rejection separate from mechanism closure.
- For ExECT, prioritize Axis 1 then Axis 2 before Axis 3 implementation sweeps: stage count/decomposition first, deterministic-vs-LLM placement second, prompt/bridge/example variants third.
- ExECT S5 is diagnosis, seizure type, medication, investigation, and frequency. Medication temporality remains S4-only unless explicitly reopened.
- Do not promote model-suite leaderboard results to operational defaults.
- Do not run further Gan builder-gap transfer or model-backed arms without a preregistered decision question after residual forensics.
- Do not let SDK-generated prose become evidence for paper claims unless it points to primary artifacts and is manually promoted.
- Do not run high-volume SDK swarms without a run ledger and draft index; do not run SDK mutation outside disposable worktrees with pre/post git status captured.

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
| ExECT post-Gan experiment structure | `docs/experiments/exect/exect_post_gan_s0_experiment_structure_20260524.md` |
| Cursor SDK expansion | `docs/workstreams/cursor_sdk/cursor_sdk_capability_expansion_report_20260524.md` |
| Historical detail archive | `docs/planning/kanban_frozen_threads_history.md` |

## Current Focus

The immediate research focus is now **ExECT pipeline decomposition after the Gan S0 lift**.

Gan made meaningful progress by first asking where the pipeline should be decomposed, which parts should be deterministic versus LLM-based, and where those parts belong. ExECT should now follow that discipline before spending effort on another prompt-policy or example-pack iteration.

Primary research question:

> For ExECT core clinical extraction, what pipeline decomposition works best, what mix of deterministic and LLM components should each stage use, and where should those components sit in the pipeline?

Execution order:

1. **ExECT S1 first**: use the narrow high-support surface to search Axis 1 and Axis 2 cleanly.
2. **Then ExECT S5**: use the gold/evidence-sufficient core set: `diagnosis`, `seizure_type`, `annotated_medication`, `investigation`, `seizure_frequency`.
3. **Then S4 targeted follow-through**: only for S4-only or broad-family residuals that S5 does not cover, especially medication temporality if needed.
4. **S2/S3 fill-in**: only when needed to support S5/S4 claims or guard regressions.

S5 is now defined as a reporting/experiment surface, not as a broader schema than S4. It deliberately focuses on fields with enough benchmark value and gold support to sustain a research claim.

## Active Board

### Ready

| Card | Intended outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- |
| **S4/S5 frequency gold-template audit** | No-model audit of ExECT seizure-frequency gold surfaces for the S5/S4 frequency family. Identify whether deterministic note-anchored candidate surfaces can represent validation gold before any candidate-adjudication or structured-slot model arm. | E4 complete | no | Audit reports gold-template coverage, missed-template taxonomy, evidence quote availability, and scorer caveats without changing S4/S5 scorer semantics |
| **Paper result table freeze** | Convert current source syntheses into compact manuscript table pack with run IDs, configs, splits, scorer modes, denominators, decision scopes, and caveats. | Current source syntheses complete | yes | Table rows cite primary run artifacts / registry paths and avoid SDK drafts as evidence |

### Completed / Reconciled

| Card | Outcome | Validation |
| --- | --- | --- |
| **E1 - ExECT S1 pipeline decomposition audit** | Reconciled active Kanban with existing S1 Axis 1/2 artifacts; no rerun needed. The preregistered Axis 1 grid already exists with stable `stage_graph_id`, bridge modes, fixed controls, and open cells. | `docs/experiments/exect/exect_s1_pipeline_decomposition_audit_20260524.md`; Axis 1 prereg/inspection `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md`, `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` |
| **E2 - ExECT S1 Axis 1 cap-25 grid** | Completed previously; `g1_l1_policy_bridges` and `g2_raw_post_bridge` tied at 95.8% micro F1 on GPT cap-25. Bridge-free verify/repair and section-aware split are rejected as arms, not mechanisms. | `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` |
| **E3 - ExECT S1 stage-executor placement grid** | Completed previously; inline and post bridge executors tied at 95.8% micro F1. Deterministic hint executors regressed on cap-25 and should not advance without a new implementation-variant preregistration. | `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md` |
| **E4 - Define and scaffold ExECT S5 core surface** | Completed; S5 is now documented as diagnosis, seizure type, annotated medication, investigation, and seizure frequency, with medication temporality excluded. A reporting-surface scorer entry point exists without changing existing S1-S4 semantics. | `docs/experiments/exect/exect_s5_core_surface_design_20260524.md`; `src/clinical_extraction/evaluation/exect.py`; `tests/test_exect_s5_scoring.py` |

### In Progress / Review

| Card | Outcome | Dependencies | Parallelizable | Validation |
| --- | --- | --- | --- | --- |
| **C13 - Cursor SDK instrumentation and draft index** | Implemented; keep as review-only operational infrastructure, not a research priority. | C12 remains gated for mutating work | yes | `docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md`, `docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md`, `uv run pytest tests/test_cursor_sdk_workflows.py` |

### Blocked / Gated

| Card | Blocker | Release Condition | Validation |
| --- | --- | --- | --- |
| **C12 - Mutating SDK workflow protocol** | Shared dirty workspace is unsafe for SDK mutation workflows; marker-gated disposable protocol now documented, but no live mutation pilot has been promoted | One successful disposable-worktree pilot with captured diff, focused test output, pre/post clean `git status`, and no shared-workspace edits | `docs/workstreams/cursor_sdk/cursor_sdk_disposable_worktree_protocol_20260524.md`; `uv run pytest tests/test_cursor_sdk_workflows.py`; rollback affects disposable workspace only |
| **Provider adapter validation backlog** | Cursor SDK compatibility report is review-only; no config changes promoted from it | Targeted tests are planned before provider config changes | `uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py` plus relevant provider smoke checks |
| **Published ExECTv2 reproduction** | CUI-aware all-family scoring and original Table 1 alignment remain unresolved | Explicit reproduction workstream reopened | CUI-aware scorer, per-item/per-letter metrics, and benchmark-reference denominator checks |
| **Gan Real(300)/Real(150)** | Real dataset access unavailable | Data access | Data manifest update and preregistered test-reporting protocol |

### Backlog / Deferred

| Item | Status | Trigger |
| --- | --- | --- |
| **E5 - ExECT S5 Axis 1 / Axis 2 grid** | Deferred until the S4/S5 frequency gold-template audit identifies a frequency-safe graph or confirms S1/S4 controls transfer cleanly | Frequency audit and preregistered S5 comparison controls |
| **E6 - ExECT S4 frequency implementation iteration** | Deferred until the no-model frequency audit clarifies representability gaps | S5/S4 needs a frequency-specific implementation variant after gold-template coverage is measured |
| **E7 - ExECT medication temporality precision work** | Deferred / S4-only | Reopen only if S4 or paper narrative needs temporality; not part of S5 |
| **S2/S3 middle-ladder reruns** | Deferred | Paper makes a middle-ladder claim or S5/S4 changes need regression guards |
| **Gan builder-gap residual forensics** | Backlog | Return after ExECT S1/S5 decomposition has a first audit/grid; no new Gan model arm before forensics |
| **LLM candidate extraction** | Open mechanism | Needs stricter candidate schema and numeric slots before more model spend |
| **Candidate-constrained verification** | Open mechanism | Revisit only after candidate recall improves |
| **Test holdout reporting** | Deferred | Only for arms clearing dev/cap gates with explicit test-reporting config |
| **Optimizer rungs / GEPA** | Deferred | Requires a narrow preregistered objective and train-demo alignment |
| **Cursor SDK cloud/PR experiments** | Deferred until C12 | Use only after disposable-worktree protocol is verified |

## Recommended Next Pull

1. **S4/S5 frequency gold-template audit.** E4 is complete; keep the next frequency step no-model before candidate-adjudication or structured-slot model spend.
2. **Paper result table freeze.** Keep source-only and do not displace the ExECT research push.
3. **Provider adapter validation backlog.** Keep test-only unless a config change is explicitly pulled.

## Parallelization Notes

- E1 should be single-threaded because it defines the S1 comparison controls and stage graph IDs.
- E4 can run in parallel after E1 has a stable draft of S1 controls; it is a schema/reporting-surface design task, not a model run.
- Paper result table freeze can run in parallel if it stays source-only and does not reinterpret residual categories.
- Provider adapter validation can proceed independently if it stays test-only and does not change provider configs.
- Mutating SDK workflow work must not run in the shared workspace.
- Any new Gan model-backed arm should wait for residual forensics and a preregistered decision question.
- Any ExECT Axis 3 implementation iteration should wait until Axis 1 and Axis 2 have at least one credible S1 skeleton.

## Operational Defaults

| Track | Default | Evidence / Caveat |
| --- | --- | --- |
| Gan S0 | `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini is the operational default | Rerun 80.6% monthly, 86.0% Purist, 88.6% Pragmatic on Gan synthetic validation |
| ExECT S1 | v4_10 + inline bridges on all tracks | GPT full 92.3% micro; Qwen v4.12 rejected at cap-25 |
| ExECT S2 | Frozen GPT v1.3 | 80.9% micro; five-family scope |
| ExECT S3 | Frozen GPT v1.2 | 72.1% micro; accepted comorbidity gap |
| ExECT S4 | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | GPT full 65.5% micro; frequency remains weak |
| ExECT S5 | Scorer scaffold implemented for diagnosis, seizure type, medication, investigation, frequency | Reporting/experiment surface to test core fields with sufficient gold/evidence support; no model program promoted yet |
| Cursor SDK | Review-only research operations assistant | Drafts are not source-of-truth edits, benchmark evidence, registry rows, or paper claims until human/Codex promotion |

## Recent Findings Summary

| Finding | Current Status | Source Of Detail |
| --- | --- | --- |
| ExECT S5 core surface | Completed; S5 is a reporting/experiment surface over diagnosis, seizure type, annotated medication, investigation, and seizure frequency; medication temporality remains S4-only | `docs/experiments/exect/exect_s5_core_surface_design_20260524.md`, `tests/test_exect_s5_scoring.py` |
| ExECT S1 Axis 1/2 reconciliation | Completed; existing 2026-05-21 stage-graph and executor grids satisfy E1/E2/E3, so the next active ExECT pull is S5 core-surface design rather than rerunning S1 cap-25 grids | `docs/experiments/exect/exect_s1_pipeline_decomposition_audit_20260524.md`, `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`, `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md` |
| Gan G11-G21 builder-gap program | Completed; GPT 4.1-mini builder-gap v1 promoted to Gan S0 operational default, Qwen transfer accepted | `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_inspection_20260523.md` |
| Frozen model suite | Complete for planned S1/S4/Gan F0 tracks; source-only unless paper need changes | `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md`, `docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md` |
| ExECT S2/S3 model-suite extension | Declined unless paper later needs a middle-ladder claim | `docs/experiments/synthesis/model_suite_exect_s2_s3_extension_v1_decision_20260523.md` |
| Paper synthesis after Gan lift | Completed as source note; final tables still pending | `docs/experiments/synthesis/paper_synthesis_update_20260524.md` |
| Cursor SDK instrumentation | Completed enough for review-only workflows; mutating workflows remain gated | `docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md`, `docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md` |
| Historical detailed run arcs | Archived / source docs only | `docs/planning/kanban_frozen_threads_history.md`, `docs/experiments/exect/`, `docs/experiments/gan/` |

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

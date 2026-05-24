# Cursor SDK Source Map

Use this file only when planning a Cursor SDK workflow or an agent swarm.

## Active Workflow Surface

| Need | Primary source |
| --- | --- |
| Current SDK operating rules | `docs/workstreams/cursor_sdk/README.md` |
| Review queue and decision vocabulary | `docs/workstreams/cursor_sdk/cursor_sdk_review_queue_20260524.md` |
| Ledger fields and status meanings | `docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md` |
| Old draft archive map | `docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md` |
| Live mutation boundary | `docs/workstreams/cursor_sdk/cursor_sdk_disposable_worktree_protocol_20260524.md` |
| Runner implementation | `scripts/cursor_sdk_workflows.py` |
| Runner tests | `tests/test_cursor_sdk_workflows.py` |

## Workflow Outputs

| Workflow | Default output area | Normal authority |
| --- | --- | --- |
| `memory-pass` | `docs/memory/dreams/` | review lead only |
| `inspection-draft` | `docs/experiments/cursor_sdk_drafts/` | review lead only |
| `hygiene-scan` | `docs/workstreams/cursor_sdk/hygiene_scans/` | review lead only |
| `paper-synthesis` | `docs/experiments/cursor_sdk_drafts/` | review lead only |
| `model-compatibility` | `docs/workstreams/cursor_sdk/compatibility/` | test backlog lead only |
| `adapter-mutation` | `docs/experiments/cursor_sdk_drafts/` | proposal only |
| `test-mutations` | `docs/experiments/cursor_sdk_drafts/` | disposable-worktree proposal only |

## Source Manifests For Common Swarms

Paper result table freeze:
- `docs/planning/kanban_plan.md`
- `docs/experiments/synthesis/paper_synthesis_update_20260524.md`
- `docs/experiments/synthesis/experiment_registry.json`
- `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md`
- promoted Gan and ExECT inspection docs for rows being reported
- matching `runs/<run_id>/config.json` and `runs/<run_id>/metrics.json`

Hybrid pipeline report:
- `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md`
- `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_inspection_20260523.md`
- `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/exect/exect_s1_pipeline_decomposition_audit_20260524.md`
- `docs/experiments/exect/exect_s5_core_surface_design_20260524.md`
- `docs/experiments/exect/exect_s4_s5_frequency_gold_template_audit_20260524.md`

Safety/policy review:
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
- `docs/taxonomy/experiment_taxonomy_schema.md`

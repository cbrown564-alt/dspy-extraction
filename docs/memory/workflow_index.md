# Workflow Index

Last reviewed: 2026-05-23
Status: Promoted routing map

Use this as a routing map. It does not replace the skills or source docs.

## Dataset, Gold, Scorer, Or Benchmark Semantics

Skills:

- `dataset-audit-first`
- `gold-scorer-integrity`
- `exect-label-policy-alignment` for ExECT S0/S1 benchmark-facing work
- `gan-frequency-error-forensics` for Gan seizure-frequency inspection

Read:

- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/dataset_splits_policy.md`

Validate:

- focused scorer/loader tests such as `tests/test_gan_scoring.py`, `tests/test_exect_scoring.py`, `tests/test_dataset_splits_policy.py`
- broader tests only after behavior changes

## New Or Changed Experiments

Skills:

- `dspy-experiment-design`
- `experiment-run-lifecycle`
- `hybrid-pipeline-exploration`
- `model-config-compatibility` when provider/model configs are involved

Read:

- `docs/templates/experiment_decision_template.md`
- `docs/templates/primitive_inspection_template.md`
- `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- `docs/experiments/synthesis/experiment_registry.json`

Validate:

- `uv run pytest tests/test_experiment_configs.py`
- `uv run pytest tests/test_experiment_registry_validation.py`
- relevant program tests for the changed backend
- Gan deterministic candidate-builder changes: read G11 audit/prereg, run `scripts/audit_gan_candidate_builder_gap.py`, validate `tests/test_gan_temporal_candidates.py` and `scripts/validate_primitives.py --errors-only`

Memory warning:

- State exactly one primary `varied_factor` per comparison group unless the preregistration explicitly permits multi-factor interpretation.
- Preserve `decision_scope: arm | mechanism | operational`; failed single configs are arm evidence by default.
- No scorer, prompt, or model edits hidden in candidate-builder cards.

## Taxonomy Primitives

Skills:

- `taxonomy-primitive-design`
- `tdd` for behavior changes

Read:

- `docs/taxonomy/taxonomy_primitive_contract.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
- `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`

Validate:

- `uv run python scripts/validate_primitives.py --errors-only`
- primitive-specific tests such as `tests/test_primitive_contracts.py`

Memory warning:

- Compose existing primitives before adding new abstraction.

## Model Provider And Windows/Local Runtime Work

Skills:

- `model-config-compatibility`
- `windows-portability`
- `experiment-run-lifecycle`

Read:

- `docs/policies/model_config_smoke_tests.md`
- `docs/policies/provider_smoke_ledger_20260524.md`
- `docs/policies/qwen_dspy_latency_policy.md`
- `docs/planning/kanban_plan.md`

Validate:

- provider smoke configs before full replay
- `uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py`

Memory warning:

- Hosted API calls can run while one Ollama job is active; do not run two Ollama jobs at once.

## Research Synthesis, Paper Notes, Or Handoff

Skills:

- `research-synthesis`
- `paper-narrative-synthesis`
- `paper-critical-review`
- `research-drift-audit`
- `research-supervisor-review`
- `skill-system-review`

Read:

- `docs/planning/kanban_plan.md`
- `docs/research_atlas/evidence_matrix.md`
- `docs/experiments/synthesis/experiment_registry_matrix_20260520.md`
- relevant inspection docs and run IDs

Validate:

- check source paths and run IDs exist
- avoid paper-facing claims from memory alone

Memory warning:

- Separate facts, interpretation, and uncertainty. Treat model-suite comparisons as model-profile evidence, not operational defaults.
- Paper-facing claims should cite run artifacts, configs, inspection docs, or policy caveats directly; memory can route the citation but cannot be the citation.

## Memory Consolidation

Skills:

- `research-synthesis`
- `skill-system-review`
- `research-drift-audit` when checking stale claims against the pivot or Kanban

Read:

- `docs/memory/README.md`
- `docs/memory/dreams/TEMPLATE.md`
- `docs/workstreams/memory/research_memory_layer_design_20260522.md`
- `docs/planning/kanban_plan.md`
- relevant source docs for the topic being consolidated

Validate:

- check all source paths exist
- check decision statuses use `operational`, `arm`, `mechanism`, `open`, `blocked`, or `stale_check`
- check confidence labels use `direct_source`, `inferred_from_sources`, or `needs_review`

Memory warning:

- Memory files are derived review surfaces. Do not rewrite audits, scorers, registry rows, or Kanban from a memory consolidation pass unless the user explicitly asks for that source-doc edit.
- Cursor SDK outputs are review-only artifacts. Memory candidates live under `docs/memory/dreams/`; experiment and paper drafts live under `docs/experiments/cursor_sdk_drafts/`; hygiene scans live under `docs/workstreams/cursor_sdk/hygiene_scans/`; compatibility reports live under `docs/workstreams/cursor_sdk/compatibility/`.

## Cursor SDK Review-Only Operations

Read:

- `docs/workstreams/cursor_sdk/README.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_review_queue_20260524.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_run_ledger_20260524.md`
- `docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md`
- `scripts/cursor_sdk_workflows.py`
- the source artifacts named by the specific workflow prompt

Commands:

- Check SDK availability: `uv run python scripts/cursor_sdk_workflows.py check`
- Draft memory: `uv run python scripts/cursor_sdk_workflows.py memory-pass`
- Draft inspection: `uv run python scripts/cursor_sdk_workflows.py inspection-draft --topic "<topic>" --run-dir runs/<run_id>`
- Draft hygiene scan: `uv run python scripts/cursor_sdk_workflows.py hygiene-scan`
- Draft paper synthesis: `uv run python scripts/cursor_sdk_workflows.py paper-synthesis`
- Draft compatibility report: `uv run python scripts/cursor_sdk_workflows.py model-compatibility`

Validate:

- Check `docs/workstreams/cursor_sdk/cursor_sdk_runs.jsonl` for run attribution after live or prompt-only SDK runs.
- Check `docs/workstreams/cursor_sdk/cursor_sdk_draft_index_20260524.md` before reviewing older SDK outputs.
- Treat every SDK output as `needs_review` until a reviewer checks source paths and promotes specific wording.
- Do not use SDK drafts as paper evidence, benchmark evidence, registry rows, or source-of-truth updates.
- Live mutation workflow `test-mutations` is blocked in the shared workspace. Use `--prompt-only` for prompt review; live execution requires a disposable clone/worktree and `CURSOR_SDK_ALLOW_MUTATING_WORKFLOW=disposable-worktree`.

Memory warning:

- The SDK is an operations assistant, not a model-comparison track.
- Mutating SDK workflows must not run against the shared working tree or any workspace containing uncommitted source work.

## Frontend Review Tooling

Skills:

- `frontend-direction-review` or frontend skills only when explicitly doing UI work

Read:

- `exect-explorer/`
- relevant review queue/export scripts

Validate:

- app-specific tests/builds
- browser visual checks after UI changes

Memory warning:

- UI work should support repeated review workflows, not become detached polish.

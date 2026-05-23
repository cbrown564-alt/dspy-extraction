# Workflow Index

Last reviewed: 2026-05-22
Status: Pilot memory seed

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
- Cursor SDK pilot (C1–C4): outputs under `docs/memory/dreams/` are review-only artifacts. Pilot validated on 2026-05-23 (C1–C3 completed successfully with zero SDK-agent edits to source-of-truth docs).

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

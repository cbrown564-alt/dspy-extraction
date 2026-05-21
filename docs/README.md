# Documentation Guide

This folder separates stable project guidance from research memory. Keep top-level
`docs/` small: the overall research plan stays in `outline.md`; everything else
should live under the nearest topic folder.

## Start Here

- `outline.md` - overall research plan and system shape.
- `planning/kanban_plan.md` - current execution board and active decisions.
- `research_atlas/` - registry-derived decision maps and evidence summaries.

## Stable Guidance

- `datasets/exect/` - ExECTv2 gold-label audits and dataset-specific guidance.
- `datasets/gan/` - Gan gold-label audits, normalization baselines, and dataset-specific guidance.
- `policies/` - scorer semantics, split policy, model latency policy, JSON decoding, benchmark metrics, and other stable operating rules.
- `architecture/` - codebase, runner, backend, and schema-sequencing design notes.
- `taxonomy/` - primitive contracts, primitive catalog, experiment taxonomy schema, and taxonomy workstream notes.

## Research Memory

- `experiments/exect/` - ExECT preregistrations, inspections, label-policy implementation notes, residual analyses, and schema-ladder run notes.
- `experiments/gan/` - Gan S0 preregistrations, inspections, error reads, validation notes, and frequency-specific experiment records.
- `experiments/synthesis/` - experiment registry, registry matrix, cross-experiment reports, and best-pipeline syntheses.
- `workstreams/hybrid/` - hybrid deterministic/LLM placement doctrine, mechanism status, and exploration plan.
- `workstreams/optimizer/` - DSPy optimizer investigations, GEPA/ReAct practice notes, and Qwen latency experiment context.
- `planning/` - Kanban history, drift audits, phase plans, status recaps, and literature-review planning notes.
- `archive/prior-context/` - historical prompt/error-analysis context retained for traceability.

## Filing Rules

- Put new preregistrations and post-run inspections under the dataset-specific
  experiment folder (`experiments/exect/` or `experiments/gan/`).
- Put durable rules that should guide future code or evaluation behavior under
  `policies/`, `datasets/`, or `taxonomy/`.
- Put cross-experiment conclusions and registry exports under
  `experiments/synthesis/`.
- Keep old links repo-root relative (`docs/...`) so scripts, configs, and
  Markdown references remain stable after moves.
- Update `experiments/synthesis/experiment_registry.json` when a run becomes a
  decision artifact, and regenerate the matrix with
  `uv run python scripts/export_experiment_registry_matrix.py` when needed.

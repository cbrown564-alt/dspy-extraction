# Agent Guide

This project uses Codex agents to help build a DSPy-based clinical extraction research system. The work is both engineering and research: agents should preserve reproducibility, dataset fidelity, and research traceability, not only make code pass tests.

## Project Context

Start with `docs/outline.md` for the overall research plan.

The two core datasets have important quirks. Read the relevant audit before touching loaders, schemas, scorers, benchmark reproduction, or evaluation logic:

- ExECTv2: `docs/exect_gold_label_audit.md`
- Gan: `docs/gan_2026_label_audit.md`

Treat these audits as active project guidance. If the raw data or implementation appears to disagree with an audit, investigate before changing behavior.

## Local Skills

Project skills live in `.agents/skills`. Use them by name in prompts, for example:

```text
Use dataset-audit-first and gold-scorer-integrity to implement the Gan scorer.
```

Available project skills:

- `dataset-audit-first`: use before touching data loading, gold labels, splits, or benchmark reproduction.
- `gold-scorer-integrity`: use when changing scorers, metrics, label normalization, benchmark comparisons, or evaluation reports.
- `clinical-schema-design`: use when changing Pydantic models, JSON schemas, DSPy signatures, field groups, validators, or structured outputs.
- `dspy-experiment-design`: use when creating or changing DSPy programs, experiment configs, optimizer runs, ablations, model comparisons, or run tracking.
- `plan-to-kanban`: use to convert loose plans into dependency-aware Kanban boards with blockers and parallelization opportunities.
- `research-synthesis`: use to convert engineering work, results, architecture notes, or Kanban progress into research logs or standalone research writeups.
- `tdd`: use for behavior changes where tests should drive the implementation.
- `grill-with-docs`: use to stress-test a plan against repo docs and existing patterns before implementation.

## Recommended Workflow

For loose planning:

1. Use `plan-to-kanban` to turn the idea into cards.
2. Identify dependencies, blockers, and parallelizable work.
3. Pull the smallest set of cards that unlocks useful progress.

For implementation:

1. Use the relevant domain skill first.
2. Read nearby code and existing patterns before adding new structure.
3. Use `tdd` for behavior changes, especially loaders, normalizers, scorers, validators, and pipeline contracts.
4. Keep changes scoped to the requested behavior.
5. Run focused validation first, then broader validation when available.

For experiments:

1. Use `dspy-experiment-design`.
2. Define the hypothesis, dataset, split, model, schema level, program variant, scorer, and artifacts before running.
3. Change one experimental factor at a time unless explicitly testing an interaction.
4. Preserve failed examples for later error analysis.

For research memory:

1. Use `research-synthesis` after meaningful implementation, evaluation, or analysis.
2. Record what changed, what was observed, what it suggests, and what remains uncertain.
3. Keep claims tied to concrete artifacts such as file paths, run IDs, configs, metrics, and dataset splits.

## Engineering Principles

- Prefer deterministic loaders, validators, normalizers, and scorers around LLM components.
- Keep model-specific behavior in configuration or adapters rather than hardcoding provider assumptions.
- Preserve raw values separately from normalized values when both matter.
- Require evidence for extracted clinical facts unless a field is explicitly metadata.
- Distinguish absent, unknown, negated, historical, planned, resolved, and present facts.
- Do not silently change scorer semantics. If scorer behavior changes, update tests and document the interpretation.
- Do not compare experiment results across changed scorer semantics unless the report says so explicitly.

## Clinical Extraction Pitfalls

- Seizure frequency can refer to current status, a historical period, or a specific seizure type.
- Gan `seizure_frequency_number[0]` is the gold label; `reference` is a secondary cross-check.
- `unknown` and `no seizure frequency reference` mean different things.
- ExECTv2 diagnosis specificity, certainty, and medication normalization affect benchmark validity.
- Evidence spans can support a raw quote without supporting the normalized interpretation.
- Gold ambiguity should be surfaced with flags or caveats, not silently erased.

## Documentation Expectations

When finishing a substantial task, summarize:

- what changed
- which files were touched
- which skill or audit guidance mattered
- what validation was run
- what remains risky or unresolved

For research-facing work, also record:

- dataset and split
- model/provider
- schema level or field group
- DSPy program variant
- scorer mode and normalization rules
- metric caveats

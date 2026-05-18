---
name: experiment-run-lifecycle
description: Use when running, reviewing, or scaling DSPy/model-backed experiments from configs, including dry runs, capped runs, full validation, artifact inspection, metric caveats, and post-run documentation.
---

# Experiment Run Lifecycle

Use this skill when an experiment moves from code/config into model execution or run-artifact review.

## Workflow

1. Identify the experiment config, model config, dataset, split, schema level, program variant, scorer mode, and output root.
2. Read the relevant experiment-design and audit docs before model calls:
   - `docs/outline.md`
   - `docs/first_dspy_schema_sequence.md`
   - `docs/deterministic_scorer_semantics.md`
   - `docs/qwen_dspy_latency_policy.md`, when using local Qwen models or changing DSPy reasoning/optimizer settings
   - dataset audit for the target dataset
3. Validate the config path and model config path. Prefer a dry run before model calls.
4. Before launching local Qwen runs, check latency multipliers:
   - `ChainOfThought` adds model-visible reasoning tokens and should not be the default for Qwen3.6:35b.
   - `BootstrapFewShot` adds compile-time model calls and can expand every prediction prompt with demos.
   - Qwen3.6:35b runs with partial CPU/RAM offload should avoid optimizers except explicit overnight optimizer experiments.
   - Qwen3.5:9b may be used to test `ChainOfThought + BootstrapFewShot` because it should fit in GPU VRAM, but that is a secondary workstream.
5. Start with a capped run when changing the program, prompt policy, optimizer, provider, model, split, or structured-output strategy.
6. For Qwen3.6:35b, prefer direct structured extraction without model-visible reasoning unless reasoning is the experimental factor.
7. Inspect artifacts before scaling:
   - `metadata.json`
   - `config.json`
   - `prompts.json`
   - `predictions.json`
   - `metrics.json`
   - `errors.json`
   - `artifacts/compiled_state.json`, when present
8. Promote to full validation only if the capped run clears the explicit gate for schema validity, evidence support, latency feasibility, and the target benchmark-facing metric.
9. After a full validation run, write or update an error-read note and refresh `docs/kanban_plan.md`.

## Reporting Rules

- Always distinguish capped runs, validation runs, and test reporting.
- Always separate benchmark-facing metrics from diagnostic metrics.
- Include confidence intervals when the report generated them.
- Report optimizer metric and benchmark scorer mode separately.
- For optimizer runs, report estimated model-call count, whether compilation was used, and whether demos expanded prediction prompts.
- For local Qwen runs, report whether the model was fully GPU-resident or partially offloaded to system RAM.
- Mention structured-output strategy and whether Pydantic validation was the acceptance gate.
- Preserve run IDs and artifact paths in summaries.
- Do not describe Gan synthetic validation as published benchmark reproduction.
- Do not report test-split results unless the config explicitly allows test reporting.

## Common Commands

Use existing scripts and configs rather than ad hoc runners:

```bash
uv run python scripts/run_experiment.py --experiment <config> --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment <config> --env-file .env
```

Run focused tests after code changes that affect experiment contracts:

```bash
uv run --extra dev pytest tests/test_experiment_configs.py tests/test_gan_s0_program.py
```

## Completion Criteria

Before finishing, summarize:

- experiment config and model config
- dataset, split, schema level, program variant, and scorer mode
- dry run, capped run, or full validation status
- run ID and artifact paths inspected
- benchmark-facing and diagnostic metric caveats
- next decision or Kanban update needed

---
name: experiment-run-lifecycle
description: Use when running, reviewing, or scaling DSPy/model-backed experiments from configs, including dry runs, capped runs, full validation, artifact inspection, metric caveats, and post-run documentation.
---

# Experiment Run Lifecycle

Use this skill when an experiment moves from code/config into model execution or run-artifact review.

## Workflow

1. Identify the experiment config, model config, dataset, split, schema level, program variant, scorer mode, and output root.
2. Read the relevant experiment-design and audit docs before model calls:
   - `docs/current_research_program.md`
   - `docs/component_ceiling_registry.md`
   - `docs/planning/kanban_plan.md`
   - `docs/policies/deterministic_scorer_semantics.md`
   - `docs/policies/published_benchmark_metrics.md`, when making external benchmark claims
   - `docs/taxonomy/taxonomy_primitive_catalog.md`, when the run composes typed primitives
   - `docs/policies/qwen_dspy_latency_policy.md`, when using local Qwen models or changing DSPy reasoning/optimizer settings
   - dataset audit for the target dataset
3. Validate the config path and model config path. Prefer a dry run before model calls.
4. When the experiment uses deterministic helpers, confirm the primitive IDs, interleaving positions, and prediction-affecting flags are documented in the config or inspection note.
5. Before launching local Qwen runs, check latency multipliers:
   - `ChainOfThought` adds model-visible reasoning tokens and should not be the default for Qwen3.6:35b.
   - `BootstrapFewShot` adds compile-time model calls and can expand every prediction prompt with demos.
   - Qwen3.6:35b runs with partial CPU/RAM offload should avoid optimizers except explicit overnight optimizer experiments.
   - Qwen3.5:9b may be used to test `ChainOfThought + BootstrapFewShot` because it should fit in GPU VRAM, but that is a secondary workstream.
6. Start with a capped run when changing the program, prompt policy, optimizer, provider, model, split, or structured-output strategy.
7. For Qwen3.6:35b, prefer direct structured extraction without model-visible reasoning unless reasoning is the experimental factor.
8. **For local Ollama runs on Windows (Qwen3.6:35b and other long jobs), launch outside Cursor/IDE background shells.** Cursor background terminals have repeatedly stalled or killed cap-25/full runs (log frozen at `1/N` or ~`20/25`, Python CPU flat while Ollama stays loaded). This is a process-tree issue, not a bad experiment config.
   - **Do not** start long local runs via Cursor agent background shells or `block_until_ms: 0` terminal jobs.
   - **Do** use the repo detached launchers: `scripts/run_exect_s*_cap25_qwen35b.ps1` / `run_exect_s*_full_qwen35b.ps1` with logging under `runs/overnight_logs/`.
   - **Do** spawn those launchers via `Start-Process` so they are not children of the IDE terminal: `scripts/start_exect_s4_cap25_qwen35b_detached.ps1`, `scripts/start_exect_s4_full_qwen35b_detached.ps1` (mirror for other steps as added).
   - **Or** run the launcher directly from an external PowerShell window.
   - **Monitor** via log tail, not terminal attachment: `Get-Content runs\overnight_logs\<run>_*.log -Tail 20 -Wait`. Progress prints at records 1, 10, 20, and N only — silence for several minutes between lines is normal on live inference.
   - **Stall signal:** log mtime unchanged for 30+ min past record 1 with flat Python CPU → kill and relaunch detached; partial predictions may remain in DSPy disk cache.
   - **Ollama contention:** do not overlap long ExECT ladder steps with Gan ReAct or other local Qwen jobs on the same machine.
9. Inspect artifacts before scaling:
   - `metadata.json`
   - `config.json`
   - `prompts.json`
   - `predictions.json`
   - `metrics.json`
   - `errors.json`
   - `artifacts/compiled_state.json`, when present
10. Promote to full validation only if the capped run clears the explicit gate for schema validity, evidence support, latency feasibility, and the target benchmark-facing metric.
11. After a full validation run, write or update an error-read note using the
    templates in `docs/templates/`; refresh `docs/planning/kanban_plan.md`,
    `docs/component_ceiling_registry.md`, or the generated program-variant
    registry when the result changes active status or the next pull.

## Reporting Rules

- Always distinguish capped runs, validation runs, and test reporting.
- Always separate benchmark-facing metrics from diagnostic metrics.
- Include confidence intervals when the report generated them.
- Report optimizer metric and benchmark scorer mode separately.
- For Gan S0 paper comparisons, use `gan2026_paper_reproduction` as the
  primary benchmark-facing scorer. Treat canonical Gan metrics as diagnostics
  or a clearly labeled sensitivity view.
- For optimizer runs, report estimated model-call count, whether compilation was used, and whether demos expanded prediction prompts.
- For local Qwen runs, report whether the model was fully GPU-resident or partially offloaded to system RAM.
- Mention structured-output strategy and whether Pydantic validation was the acceptance gate.
- Preserve run IDs and artifact paths in summaries.
- Include primitive IDs, taxonomy fields, scorer mode, normalization rules, and evidence rules in promotion, freeze, hold, or reject notes.
- Do not describe Gan synthetic validation as published benchmark reproduction.
- Do not report test-split results unless the config explicitly allows test reporting.
- Do not use holdout metrics for tuning. Treat them as residual-analysis
  triggers unless the current plan explicitly says otherwise.

## Common Commands

Use existing scripts and configs rather than ad hoc runners:

```bash
uv run python scripts/run_experiment.py --experiment <config> --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment <config> --env-file .env
```

**Local Qwen on Windows — dry run and smokes only in IDE terminals; cap-25/full via detached PS:**

```powershell
# OK in IDE / agent shell (no model calls or very short)
uv run python scripts/run_experiment.py --experiment <config> --env-file .env --dry-run

# Long Ollama runs — use Start-Process wrapper or external PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_exect_s4_cap25_qwen35b_detached.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_exect_s4_full_qwen35b_detached.ps1

# Monitor (any shell)
Get-Content runs\overnight_logs\exect_s4_cap25_qwen35b_*.log -Tail 20 -Wait
```

Run focused tests after code changes that affect experiment contracts:

```bash
uv run --extra dev pytest tests/test_experiment_configs.py tests/test_experiment_arm_templates.py tests/test_gan_s0_program.py
uv run python scripts/validate_primitives.py --errors-only
```

## Completion Criteria

Before finishing, summarize:

- experiment config and model config
- dataset, split, component/stage, schema level, program variant, and scorer mode
- dry run, capped run, or full validation status
- run ID and artifact paths inspected
- benchmark-facing and diagnostic metric caveats
- next decision or Kanban update needed

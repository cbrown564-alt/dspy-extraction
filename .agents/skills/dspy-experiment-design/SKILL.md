---
name: dspy-experiment-design
description: Use when creating or modifying DSPy signatures, modules, compiled programs, optimizer runs, experiment configs, ablations, model comparisons, or run-tracking behavior.
---

# DSPy Experiment Design

Treat each experiment as a reproducible program variant, not a loose prompt edit.

**Research program (2026-05-21 pivot):** use `hybrid-pipeline-exploration` for stage-count,
det-vs-LLM placement, and arm-vs-mechanism decision discipline. This skill covers config
metadata, primitives, and run hygiene; the hybrid skill covers *what* to test next.

Follow this workflow:

1. State the experiment hypothesis in one sentence.
2. Identify the dataset, split, model config, schema level, and scorer before changing code.
3. Search for existing DSPy signatures, modules, configs, primitive registry entries, and run artifact conventions.
4. Compose deterministic helpers from typed primitives rather than ad hoc helper edits unless the experiment is explicitly testing a new primitive.
5. Change one experimental factor at a time unless the experiment explicitly tests an interaction.
6. Record enough configuration for the run to be reproduced later.

## Run Lifecycle

For model-backed experiments, use this sequence unless the task is only a code or config review:

1. Validate the experiment config and model config before any model calls.
2. Run a dry run or capped run first when a new program, prompt policy, optimizer, provider, or split is involved.
3. Inspect the produced run artifacts before scaling up: config, prompts, predictions, metrics, errors, and compiled state when an optimizer is used.
4. Promote to full validation only after the capped run clears the stated validity and evidence gates.
5. After full validation, write or update an error-read note before choosing the next implementation target.
6. Update the Kanban board with completed run IDs, metric caveats, and the recommended next pull.

## Required Experiment Metadata

Every experiment should make these explicit:

- dataset and split
- model and provider
- schema or field group
- DSPy signatures/modules used
- prompt or instruction source
- few-shot/demo policy
- context selection policy
- verifier, repair, or abstention policy
- primitive IDs and interleaving positions used
- scorer and metric mode
- output artifact paths

## Hybrid Taxonomy (required on new configs)

Add a `taxonomy` block to every new `configs/experiments/*.json` file, or add the
experiment to `docs/experiment_registry.json` in the same change. Controlled
values live in `docs/experiment_taxonomy_schema.md`.

Minimum config fields:

- `dataset`
- `schema_complexity`
- `program_architecture`
- `hybrid_balance_class`
- `interleaving_positions`
- `varied_factor`
- `comparison_group`
- `intended_decision`

When writing a promotion, freeze, hold, or reject note, include a **Taxonomy**
section with the same dimensions plus `clinical_task_family` and `outcome`.
Use the inspection templates in `docs/templates/` and the section contracts in
`src/clinical_extraction/experiments/inspection_templates.py`.

## Taxonomy Primitives (required on new deterministic helpers)

Prefer existing typed primitives from `docs/taxonomy_primitive_catalog.md` and
`src/clinical_extraction/primitives.py` before adding new helper code inside a
program module.

For new L1/H1/H2/H3/H4/D1 arms, start from
`src/clinical_extraction/experiments/arm_templates.py` via `build_experiment_arm_config`
so taxonomy metadata, comparison groups, and primitive compatibility are checked
before the config is emitted.

Every experiment that uses deterministic helpers should make these explicit:

- primitive IDs and versions
- interleaving positions (`pre`, `during`, `tool_during`, `post`, `eval_only`)
- control mode (soft hint, hard constraint, tool affordance, posthoc correction, diagnostic-only)
- whether each primitive is prediction-affecting or scorer-only/diagnostic

When adding or changing primitives, use `taxonomy-primitive-design`.

After adding or editing configs, registry rows, or primitive metadata, run:

```powershell
uv run python scripts/validate_experiment_taxonomy.py --errors-only
uv run python scripts/validate_primitives.py --errors-only
```

## Build-Before-Run Policy

The taxonomy-primitives phase is complete enough that new model-backed runs should
compose existing primitives rather than quietly changing bridge behavior, evidence
policy, or prompt surfaces in program code.

Limit new model-backed experiments to cases that answer an active research decision
already tracked in `docs/kanban_plan.md`. Otherwise favor deterministic validation,
fixture design, config generation, and inspection templates until the next
systematic run batch.

## Program Variant Guidance

Use named variants rather than anonymous prompt edits:

- monolithic extraction
- section-aware extraction
- field-family extraction
- context-injected extraction
- extract-then-verify
- extract-verify-repair
- minimal-schema-first expansion

When optimizing with DSPy, keep the optimized object, training examples, metric, and compilation settings tied together in artifacts.

Do not treat an optimizer metric as the benchmark scorer. Optimizer-only metrics may include evidence or formatting gates, but reports must still state the benchmark-facing scorer mode separately.

## Decision Scope (required in inspections)

State `decision_scope` on every outcome:

- `operational` — frozen default for reproducibility; does not close the mechanism class
- `arm` — this specific config under these controls failed or passed gates
- `mechanism` — hypothesis class closed only after mechanism review (≥2 arms or positions)

Do not write "verify-repair is rejected" or "H2 is closed" in summaries unless
`decision_scope: mechanism` is justified in the inspection doc.

## Ablation Discipline

- Define the baseline before the ablation.
- Keep the dataset, split, model, and scorer stable unless they are the factor under test.
- State which **research axis** (1 stage graph, 2 stage executor, 3 implementation) the group tests.
- Track latency, token usage, or local inference time alongside quality metrics.
- Preserve failed examples for error analysis.
- Do not compare runs if scorer semantics changed unless the report says so explicitly.
- Do not compare capped runs and full-validation runs without saying which split and record cap each metric used.
- Do not move to test-set reporting unless the experiment config explicitly allows it.

## Completion Criteria

Before finishing, summarize:

- hypothesis tested
- experimental factor changed
- fixed controls
- artifacts produced or expected
- run IDs or artifact paths inspected
- metric caveats

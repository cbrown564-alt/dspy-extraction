---
name: dspy-experiment-design
description: Use when creating or modifying DSPy signatures, modules, compiled programs, optimizer runs, experiment configs, ablations, model comparisons, or run-tracking behavior.
---

# DSPy Experiment Design

Treat each experiment as a reproducible program variant, not a loose prompt edit.

Follow this workflow:

1. State the experiment hypothesis in one sentence.
2. Identify the dataset, split, model config, schema level, and scorer before changing code.
3. Search for existing DSPy signatures, modules, configs, and run artifact conventions.
4. Change one experimental factor at a time unless the experiment explicitly tests an interaction.
5. Record enough configuration for the run to be reproduced later.

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
- scorer and metric mode
- output artifact paths

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

## Ablation Discipline

- Define the baseline before the ablation.
- Keep the dataset, split, model, and scorer stable unless they are the factor under test.
- Track latency, token usage, or local inference time alongside quality metrics.
- Preserve failed examples for error analysis.
- Do not compare runs if scorer semantics changed unless the report says so explicitly.

## Completion Criteria

Before finishing, summarize:

- hypothesis tested
- experimental factor changed
- fixed controls
- artifacts produced or expected
- metric caveats

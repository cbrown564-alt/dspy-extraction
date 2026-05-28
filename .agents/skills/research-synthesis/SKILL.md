---
name: research-synthesis
description: Use when converting engineering plans, architecture notes, experiment configs, implementation details, evaluation results, error analysis, or Kanban progress into research-facing documentation such as an ongoing research log, standalone research note, methods section, results analysis, or discussion draft.
---

# Research Synthesis

Use this skill when project work needs to become research memory or research prose.

This skill has two modes:

- `Research log`: append or draft a dated record of what changed, why, what was observed, and what remains uncertain.
- `Standalone writeup`: turn artifacts into a self-contained research-style note, methods section, results section, or discussion draft.

For current research synthesis, start from the active authority surfaces before
older notes:

1. `docs/README.md`
2. `docs/current_research_program.md`
3. `docs/component_ceiling_registry.md`
4. `docs/planning/kanban_plan.md`
5. the relevant domain map: `docs/experiments/gan/README.md`,
   `docs/experiments/exect/README.md`, or
   `docs/experiments/synthesis/README.md`

Treat older experiment notes as evidence unless a current index explicitly
promotes them.

## Workflow

1. Identify the source artifacts:
   - plans, Kanban boards, architecture diagrams, configs, code changes, experiment outputs, evaluation tables, error samples, or discussion notes
2. Identify the target audience:
   - future project maintainer
   - experiment reviewer
   - paper/thesis reader
   - clinical collaborator
3. Separate facts from interpretation:
   - facts: what was run, changed, measured, or observed
   - interpretation: what the result suggests
   - uncertainty: what is not yet known
4. Preserve traceability to concrete artifacts:
   - file paths
   - run IDs
   - dataset/split names
   - model configs
   - scorer versions
5. Identify the status of the claim or result:
   - `active guidance`
   - `current synthesis`
   - `component ceiling registry`
   - `promoted baseline`
   - `operational default`
   - `mechanism open`
   - `rejected arm`
   - `mechanism rejected`
   - `diagnostic only`
   - `benchmark-facing`
   - `clinical diagnostic`
   - `superseded`
   - `blocked`
   - `paper evidence`
   - `archive`
6. Write in research language without hiding engineering constraints.

## Research Log Format

Use this shape for ongoing logs:

```markdown
## YYYY-MM-DD - Short Title

### Context
What question, plan, or problem motivated the work.

### Work Completed
What changed or was run, with paths or run IDs.

### Observations
What was learned from outputs, tests, metrics, or inspection.

### Interpretation
What the observations likely mean for the research question.

### Caveats
Limitations, confounds, data quality issues, scorer caveats, or implementation risks.

### Next Steps
Concrete follow-up tasks or experiment cards.
```

## Standalone Writeup Shape

Use this shape for research-facing notes:

```markdown
# Title

## Research Question
The question this work addresses.

## Motivation
Why the question matters for the project.

## Method
Dataset, split, schema, model, pipeline, scorer, and experimental controls.

## Results
Metrics, qualitative findings, failure modes, and notable examples.

## Interpretation
What the results suggest, including competing explanations.

## Limitations
Confounds, missing comparisons, scorer issues, dataset quirks, and threats to validity.

## Next Experiments
The smallest useful follow-up experiments.
```

## Writing Rules

- Do not overclaim. Keep claims tied to evidence.
- Say what the new synthesis supersedes, if anything.
- Link to `docs/component_ceiling_registry.md` if the writeup changes or
  interprets active component status.
- Distinguish benchmark reproduction from exploratory experiments.
- Mention scorer semantics when results depend on them.
- Mention dataset quirks when they affect interpretation.
- Include negative results and failed attempts when they change future decisions.
- Keep implementation details only when they explain methodology, reproducibility, or validity.
- Prefer clear prose over paper-like ornament.
- Do not promote archived experiment notes, archived configs, or archived runs
  back to active guidance without a current registry, domain README, or Kanban
  update.
- Treat holdout metrics as residual-analysis evidence only unless the current
  plan explicitly states a different reporting purpose.

## Clinical Extraction Specific Checks

For this project, always consider whether the writeup should mention:

- dataset: ExECTv2, Gan, or both
- split: train, dev, test, or exploratory subset
- component, family, or decomposition stage
- schema level or field group
- model/provider
- DSPy program variant
- evidence requirement
- verifier/repair/abstention policy
- scorer mode and normalization rules
- gold-label caveats from the audit docs
- result status: isolated ceiling, stacked baseline, diagnostic substrate,
  rejected arm, mechanism open, blocked benchmark claim, or paper evidence

For model-backed experiment results, also mention:

- run ID and artifact directory
- whether the run was capped, full validation, or test reporting
- primitive IDs and interleaving positions used, when relevant
- optimizer metric and compiled-state artifact, when present
- benchmark-facing metrics versus diagnostic metrics
- confidence intervals, if generated
- the next decision the result supports
- whether archived artifacts are being used as docs/file provenance rather than
  default loadability contracts

For promotion, freeze, hold, or reject notes, prefer the templates in `docs/templates/` and include primitive IDs, taxonomy fields, scorer mode, normalization rules, and evidence rules when they affect interpretation.

## Completion Criteria

Before finishing, provide:

- the research log entry or standalone writeup
- artifact references used
- run IDs, configs, and metric files used when summarizing experiments
- claims that remain tentative
- recommended next research or engineering step

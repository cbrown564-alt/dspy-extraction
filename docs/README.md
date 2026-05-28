# Documentation Guide

Status: active guidance
Last updated: 2026-05-28

This docs tree is being refocused around the May 28 decomposition pivot. The
active project question is no longer "which broad pipeline wins?" It is:

> Which task components can be independently represented, optimized, and scored
> before they are stacked into broader clinical extraction systems?

## Read First

1. `current_research_program.md` - the current research doctrine and stop rules.
2. `component_ceiling_registry.md` - current component status, baselines, open
   mechanisms, rejected arms, and blocked claims.
3. `planning/kanban_plan.md` - active execution board and next pull.
4. `datasets/exect/exect_gold_label_audit.md` and
   `datasets/gan/gan_2026_label_audit.md` - dataset and gold-label policy.
5. `policies/deterministic_scorer_semantics.md` and
   `policies/published_benchmark_metrics.md` - scorer and benchmark rules.

## Domain Maps

- `experiments/gan/README.md` - Gan S0 decomposition map and evidence index.
- `experiments/exect/README.md` - ExECT component-ceiling map and evidence index.
- `experiments/synthesis/README.md` - paper, registry, holdout, and synthesis
  status.

## Authority Rule

Everything outside the active docs above is historical evidence unless a current
index explicitly promotes it. Old experiment notes are valuable provenance, but
they are not active guidance by default.

Use these status labels when adding or revising docs:

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

## Filing Rules

- New decomposition plans go under the relevant domain folder and must link back
  to `component_ceiling_registry.md`.
- New preregistrations and post-run inspections go under
  `experiments/gan/` or `experiments/exect/`.
- New scorer, dataset, split, or benchmark semantics go under `policies/` or
  `datasets/`, not inside experiment notes.
- New cross-experiment conclusions go under `experiments/synthesis/` only when
  they supersede or explicitly route older synthesis docs.
- Archive by decision boundary, not by age. Keep run IDs and caveats traceable.

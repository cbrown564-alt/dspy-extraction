---
name: research-drift-audit
description: Use when checking whether recent commits, current development focus, experiment plans, or active implementation work have drifted from docs/current_research_program.md, docs/component_ceiling_registry.md, docs/planning/kanban_plan.md, or the original proposal context in docs/outline.md.
---

# Research Drift Audit

Use this skill when the user asks whether the repo is still aligned with the core research plan.

## Workflow

1. Read the core project direction:
   - `docs/README.md`
   - `docs/current_research_program.md`
   - `docs/component_ceiling_registry.md`
   - `docs/planning/kanban_plan.md`
   - `docs/outline.md` as original proposal context, not current steering
   - `docs/policies/deterministic_foundation_decisions.md`, if relevant
   - latest research synthesis or error-analysis docs for the active workstream
2. Inspect recent git history and changed files.
3. Identify the active development focus by file clusters, commit messages, run artifacts, and updated docs.
4. Compare active work against the stated research goals:
   - component decomposition and isolated ceiling measurement
   - benchmark reproduction and improvement
   - deterministic infrastructure before model complexity
   - Gan versus ExECT sequencing
   - reproducible experiments and ablations
   - local versus closed-model comparison
   - downstream use-case exploration
5. Classify deviations:
   - aligned progress
   - useful detour with evidence
   - unresolved drift risk
   - likely distraction or overbuild
6. Recommend whether to continue, narrow, pause, or reframe the workstream.

## Drift Signals

- implementation expands without a corresponding Kanban card or research question
- broad prompt or stack optimization resumes before component substrates and
  ceilings are defined
- model runs proceed before scorer/data contracts are stable
- UI/tooling work starts to dominate without serving review, reproducibility, or downstream use
- a narrow benchmark task turns into broad architecture work without an ablation plan
- new metrics are compared against old metrics without scorer caveats

## Completion Criteria

Before finishing, summarize:

- docs and commits inspected
- current active focus
- alignment with core research objectives
- divergences and whether they are justified
- recommended correction or next pull

# Research Memory

Status: Pilot memory layer
Created: 2026-05-22

This directory contains derived, reviewable research memory for agent handoff and stale-claim detection.

## Source Precedence

If a memory file conflicts with a source artifact, trust the source artifact.

1. Dataset audits and policies: `docs/datasets/`, `docs/policies/`
2. Raw run artifacts: `runs/*`
3. Experiment configs: `configs/experiments/`, `configs/models/`
4. Preregistration and inspection docs: `docs/experiments/`
5. Active research program and component status: `docs/current_research_program.md`
   and `docs/component_ceiling_registry.md`
6. Active planning board: `docs/planning/kanban_plan.md`
7. Experiment registry: `docs/experiments/synthesis/experiment_registry.json`
8. Historical mechanism doctrine/status: `docs/workstreams/hybrid/`
9. This memory directory

Memory files are allowed to summarize, point, and warn. They should not silently change scorer semantics, gold-label policy, experiment outcomes, or operational defaults.

## Memory Rules

- Include source paths for claims.
- Label decisions as `operational`, `arm`, `mechanism`, `open`, `blocked`, or `stale_check`.
- Label confidence as `direct_source`, `inferred_from_sources`, or `needs_review`.
- Include a next action when the memory item implies one; use `none` when it is only a warning.
- Prefer short handoff notes over full restatements of source docs.
- Treat LLM-generated dream outputs as candidates until reviewed.
- Do not use memory files as evidence for paper claims unless they point to primary artifacts.
- Do not upgrade `arm` evidence to `mechanism` evidence from memory alone.

## Promotion Checklist

Before adding or updating a memory item, check:

- source paths exist
- decision scope is explicit
- confidence is explicit
- stale-risk language such as "closed", "best", "leader", "default", or "rejected" is scoped
- source-of-truth docs were not rewritten as a side effect

## Current Files

| File | Purpose |
| --- | --- |
| `dreams/TEMPLATE.md` | Template for reviewable memory consolidation candidates. |

## Archived Memory Files

Superseded memory routing notes were moved to `docs/archive/memory/` during the
May 28 archive pass:

- `session_brief.md`
- `workflow_index.md`
- `20260522_model_suite_handoff_candidate.md`

## Dream Candidates

Dream candidates live under `docs/memory/dreams/`. They are review artifacts, not promoted memory.

Use a dream candidate when consolidating across multiple source docs, checking stale claims, or proposing updates to memory files. A candidate may recommend edits to `session_brief.md`, `workflow_index.md`, or future memory caches, but it must not edit source-of-truth docs automatically.

Promotion requires:

- every proposed update has at least one source path
- every decision or warning has a status and confidence label
- overbroad terms such as "closed", "best", "default", "leader", and "rejected" are scoped
- conflicting source claims are surfaced rather than smoothed over
- reviewer confirms which proposed updates should move into promoted memory files

## Design

See `docs/workstreams/memory/research_memory_layer_design_20260522.md`.

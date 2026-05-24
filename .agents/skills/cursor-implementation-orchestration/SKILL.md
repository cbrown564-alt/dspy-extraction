---
name: cursor-implementation-orchestration
description: Use when Codex should orchestrate, supervise, and review ambitious Cursor SDK implementation workstreams that may write core project files, such as ExECT or Gan benchmark-improvement campaigns, multi-agent swarms, long-running feature branches, scorer-preserving pipeline changes, experiment scaffolds, tests, docs, and source-backed research promotion. Use when Cursor is the implementer and Codex/GPT-5.5 is the planner, reviewer, benchmark gatekeeper, and final promoter.
---

# Cursor Implementation Orchestration

## Overview

Use Cursor SDK as a capable implementation engine under a stronger Codex orchestration layer. Unlike `cursor-sdk-research-ops`, this skill permits Cursor to write source, tests, configs, and research docs when the workstream has an explicit goal, branch/worktree isolation, domain-skill guardrails, and Codex review before merge or promotion.

## Operating Model

Codex/GPT-5.5 owns:

- workstream goal, success metrics, scope boundaries, and stop rules
- choice of project skills/audits to load before implementation
- decomposition into Cursor tasks and swarm lanes
- review of every source-of-truth change before merge
- final claims about benchmark performance, scorer semantics, paper evidence, and operational defaults

Cursor owns:

- implementation patches in isolated branches/worktrees
- focused tests, dry runs, reports, and candidate experiment configs
- swarm-style independent implementation or review lanes
- draft inspection notes and exact source-map evidence for Codex review

## Preconditions

Before delegating mutation:

- Create or select an isolated branch/worktree. Do not let Cursor mutate an unscoped shared workspace.
- State the workstream goal in benchmark terms, for example: "beat the published ExECTv2 S5-relevant benchmark surface while preserving scorer semantics."
- Name the allowed write surfaces: source modules, tests, configs, docs, scripts, or generated artifacts.
- Name forbidden changes: raw data, gold labels, scorer semantics, split definitions, registry rows, paper claims, or operational defaults unless the task explicitly targets them and the relevant project skills are loaded.
- Load domain skills first. Examples: `dataset-audit-first`, `gold-scorer-integrity`, `clinical-schema-design`, `taxonomy-primitive-design`, `dspy-experiment-design`, `experiment-run-lifecycle`, `exect-label-policy-alignment`, or `gan-frequency-error-forensics`.
- Define validation gates before implementation starts.

## Workstream Loop

1. **Frame**: Write a short mission brief with dataset/split, benchmark target, model/provider, schema level, scorer mode, metric caveats, allowed files, and stop rules.
2. **Slice**: Break the mission into narrow implementation cards. Each card must have a test or artifact that can prove progress.
3. **Delegate**: Assign Cursor one card or one swarm lane at a time. Include the relevant source files and audits, not just the desired result.
4. **Inspect**: Require Cursor to report changed files, tests run, run IDs, metric deltas, caveats, and suspected risks.
5. **Review**: Codex reads the diff and primary artifacts, reruns focused validation when feasible, and rejects, revises, or promotes the patch.
6. **Record**: Update the Kanban, registry, inspection docs, or memory only after source-backed review.

## Allowed Mutation Classes

Cursor may write core project files when explicitly delegated:

- deterministic primitives, adapters, validators, and bridge helpers
- DSPy program variants, experiment configs, and prompt modules
- focused tests and regression tests
- analysis scripts, inspection drafts, and promoted docs after Codex review
- UI or exploration tools that support the workstream

Cursor must not unilaterally:

- alter raw datasets, gold-label interpretation, split membership, or scorer semantics
- promote experiment results into operational defaults
- rewrite the paper narrative from unverified draft claims
- merge broad refactors with benchmark-facing changes
- compare metrics across changed denominators or scorer modes without explicit caveats

## Swarm Design

Use swarms when lanes can be independently checked. Prefer roles like:

- implementation lane: writes the narrow patch and tests
- regression lane: tries to break scorer, loader, schema, and dataset assumptions
- benchmark lane: inspects run artifacts and metric denominators
- evidence lane: maps claims to primary files and run IDs
- critic lane: argues why the proposed promotion is not yet justified

Do not ask multiple lanes to modify the same files simultaneously unless Codex has a planned merge sequence.

## ExECT Benchmark Campaign Pattern

For a long ExECT campaign, frame the mission around beating the relevant published benchmark or current project baseline while preserving audit-aligned semantics.

Minimum brief:

- dataset: ExECTv2
- split: validation/dev/test as applicable; do not touch split definitions
- surface: S1/S4/S5 or all-family reproduction
- current baseline and target metric
- model/provider and budget
- scorer entry point and normalization rules
- candidate decomposition axes: stage count, deterministic-vs-LLM placement, field-family agents, candidate injection, verification, repair, optimizer rung
- no-go changes: gold reinterpretation, scorer denominator drift, CUI-aware reproduction claims unless explicitly implemented

## Review Checklist

Before accepting Cursor work:

- `git diff` contains only the delegated scope.
- Tests cover the behavior change and fail for the old behavior where practical.
- Dataset audits and scorer policies still hold.
- Any metric claim names the run ID, config, split, model/provider, scorer mode, denominator, and caveat.
- Any registry, Kanban, paper, or memory update is traceable to primary artifacts.
- Failed examples and residual errors are preserved for the next iteration.

## Relationship To Research Ops

Use `cursor-sdk-research-ops` for bounded review-only drafting, source maps, hygiene scans, compatibility stale-checks, and disposable mutation pilots. Use this skill when the intent is supervised implementation that may write core files and advance a benchmark-facing workstream.

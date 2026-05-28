---
name: thermo-nuclear-code-quality-review
description: Use when performing an unusually strict code quality, maintainability, abstraction, modularity, or architecture review of this repo, especially after large code changes, before merging broad pipeline/program changes, when files grow past healthy size boundaries, or when the user asks for a thermonuclear/thermo-nuclear/deep/harsh code quality review.
---

# Thermo-Nuclear Code Quality Review

Use this skill for a demanding maintainability review of implementation structure. The goal is to find changes that work but make the codebase harder to build research on.

This skill is adapted for this clinical extraction repo from Cursor's `thermo-nuclear-code-quality-review` rubric. Apply the structural pressure, but preserve this project's higher-order constraints: dataset fidelity, scorer semantics, reproducibility, and research traceability.

## Review Bar

Do not approve merely because tests pass or behavior appears correct. The review should block or strongly challenge:

- structural regressions that make future experiment work harder;
- files pushed past roughly 1000 lines without a strong reason;
- new ad-hoc branches, mode flags, or special cases in already busy flows;
- broad LLM program edits that mix extraction, policy, bridge, scoring, evidence repair, and reporting in one place;
- thin wrappers, identity abstractions, or helper layers that add indirection without reducing concepts;
- generic or magical mechanisms that hide simple dataset or schema invariants;
- duplicated helpers where a canonical loader, primitive, bridge, scorer, or registry utility already exists;
- code that leaks feature-specific behavior into shared infrastructure;
- cast-heavy, optional-heavy, or `Any`-heavy contracts where a typed model or explicit boundary would clarify invariants;
- refactors that move complexity around instead of deleting it.

## Repo-Specific Non-Negotiables

Before recommending code movement or simplification, identify whether the touched area is governed by one of these skills:

- `dataset-audit-first` for loaders, gold labels, splits, or benchmark reproduction.
- `gold-scorer-integrity` for scorers, metric aggregation, label normalization, reports, or benchmark comparison.
- `clinical-schema-design` for Pydantic models, JSON schemas, DSPy signatures, validators, or structured outputs.
- `taxonomy-primitive-design` for primitives, registry metadata, adapters, bridges, or primitive fixtures.
- `dspy-experiment-design` and `experiment-run-lifecycle` for programs, configs, optimizer runs, and run artifacts.
- `exect-label-policy-alignment` or `gan-frequency-error-forensics` for benchmark-facing ExECT or Gan extraction logic.

If one applies, use it as a guardrail. Never simplify by silently changing scorer semantics, benchmark policy, gold interpretation, split behavior, evidence rules, or experiment comparability.

## Primary Questions

For every meaningful change, ask:

- Is there a simpler decomposition that removes whole branches, flags, modes, or layers?
- Does this change belong in a canonical layer: dataset, primitive, bridge, program, scorer, runner, registry, or report?
- Is the code separating raw extraction, deterministic substrate, benchmark bridge, model adjudication, scoring, and evidence diagnostics?
- Did the diff add mode-specific branching where a typed policy, registry entry, config, or dedicated module would be clearer?
- Does a large program file need a focused module split around a real concept, not a cosmetic extraction?
- Does the abstraction earn its keep by reducing the number of concepts a reader must hold?
- Are validation and tests strong enough for the semantic surface being touched?
- Could this cleanup accidentally invalidate earlier experiment comparisons?

## Preferred Remedies

Prefer recommendations that delete or isolate complexity:

- extract a real domain concept into a focused module;
- replace repeated conditionals with a typed policy object, registry entry, or explicit dispatcher;
- split broad program files around pipeline stages or benchmark families;
- move benchmark policy into bridge/scorer/policy surfaces instead of prompts or scattered branches;
- separate orchestration from business logic;
- make raw values, normalized values, evidence, flags, and metadata explicit rather than implicit;
- collapse duplicate flows into one canonical helper;
- remove wrappers that do not clarify ownership or invariants;
- add focused tests before changing semantics-sensitive code.

Avoid suggesting broad rewrites unless the path preserves behavior and validation is clear. In this repo, a smaller behavior-preserving simplification is often better than a beautiful refactor that muddles research provenance.

## Output Format

Lead with findings, ordered by severity. For each finding include:

- file and line reference when available;
- why this is a structural/code-quality problem;
- why it matters for this research system;
- the concrete simplification or decomposition to pursue;
- any validation needed to protect scorer/dataset/reproducibility semantics.

If no blocking issues are found, say so explicitly and list remaining residual risks, especially large files, bundled semantics, or missing tests.

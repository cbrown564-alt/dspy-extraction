---
name: gan-frequency-error-forensics
description: Use when inspecting Gan seizure-frequency run artifacts, errors, repair candidates, evidence support failures, unknown/no-reference confusions, cluster mistakes, temporal-window errors, or deciding the next Gan S0 improvement.
---

# Gan Frequency Error Forensics

Use this skill after a Gan run or when changing Gan S0 repair, verifier, evidence, or prompt/example behavior.

## Required Context

Read these before drawing conclusions:

- `docs/gan_2026_label_audit.md`
- `docs/deterministic_scorer_semantics.md`
- `docs/taxonomy_primitive_catalog.md` for Gan frequency primitives
- latest relevant Gan run note, especially `docs/gan_s0_full_validation_error_read.md` when working from the current S0 baseline
- the run's `metrics.json`, `errors.json`, and `predictions.json`

## Error Triage

Classify failures before proposing a fix:

- schema-invalid output
- repairable surface form
- non-repairable semantic format gap
- monthly-frequency mismatch
- Purist or Pragmatic category mismatch
- `unknown` versus `no seizure frequency reference`
- seizure-free threshold error
- cluster frequency or per-cluster error
- temporal-window denominator error
- highest-current-frequency selection error
- unsupported evidence quote
- paraphrased, stitched, or non-contiguous evidence
- abstention boundary error

## Repair Rules

Allowed deterministic repair is narrow:

- quoted special labels such as `"unknown"`
- unambiguous denominator range surfaces such as `1 per 3 week to 1 per 2 week`
- other one-to-one canonical surface repairs with regression tests

Do not deterministically repair:

- incomplete cluster labels such as `1 cluster per week`
- labels with `unknown per cluster`
- null outputs where a label was required
- `unknown` versus `no seizure frequency reference` based only on label shape
- temporal-window choices that require reading the note

For non-repairable failures, prefer verifier/repair DSPy work, prompt/example policy changes, or targeted schema/metric changes with tests.

When changing deterministic Gan frequency behavior, check the typed primitives in `src/clinical_extraction/gan/primitives.py` first:

- `gan.frequency.label_policy_bridge.v1`
- `gan.frequency.evidence_guard.v1`

Add or reuse fixture cases in `data/fixtures/primitive_cases.json` for regression coverage before changing bridge or evidence-guard logic.

## Evidence Rules

- Gan `seizure_frequency_number[0]` remains gold.
- `reference` remains a secondary cross-check and difficulty signal.
- Evidence quote support is diagnostic unless the experiment defines an evidence-facing optimizer objective.
- Exact contiguous source quotes are required for strict evidence support.
- Do not treat elided, paraphrased, or secondary-reference evidence as simple gold quote failure without checking the audit caveats.

## Completion Criteria

Before finishing, summarize:

- run ID and artifact files inspected
- counts by failure class
- which failures are deterministic repair candidates
- which failures require semantic verifier/repair or prompt/example changes
- regression tests needed before code changes
- whether scorer semantics are preserved or changed

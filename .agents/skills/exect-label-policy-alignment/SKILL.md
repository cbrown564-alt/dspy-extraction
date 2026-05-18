---
name: exect-label-policy-alignment
description: Use when designing, prompting, scoring, or evaluating ExECTv2 benchmark-facing diagnosis, seizure-type, medication, or S0/S1 field-family extraction where annotation policy may differ from clinically richer labels.
---

# ExECT Label Policy Alignment

Use this skill before ExECT S0/S1 benchmark-facing extraction or scorer work.

## Required Context

Read:

- `docs/exect_gold_label_audit.md`
- `docs/deterministic_scorer_semantics.md`
- `docs/prior_prompt_error_analysis_synthesis.md`
- relevant ExECT loader, schema, scorer, and test files

## Core Principle

Separate benchmark-facing annotation policy from clinically rich extraction.

A label may be clinically plausible but wrong for the audited ExECT scoring view. Benchmark-facing outputs should match the current canonical scoring view; clinically richer outputs should be preserved only through an explicit bridge or separate schema level.

## Diagnosis Checks

- Do not infer epilepsy subtype from seizure-type evidence alone.
- Do not turn single seizure events into established epilepsy diagnosis unless the letter explicitly supports it under the audited scoring view.
- Preserve diagnosis specificity collapse when the current scorer requires it.
- Treat negation, certainty, and family-history-only mentions according to the audit.
- Investigate empty-list/null behavior before reporting diagnosis exact-match results.

## Seizure-Type Checks

- Avoid ILAE-specific surfaces when the benchmark-facing label is coarser, unless a tested mapping layer is explicit.
- Do not infer seizure type from diagnosis alone.
- Secondary generalisation is not a separate current seizure type unless independently named as current.
- `unknown seizure type` and absent seizure type need explicit scorer semantics before being mixed.

## Medication Checks

- Use the audited prescription source and normalization rules.
- Do not score current/planned/historical medication status as benchmark-facing unless the source and scorer semantics have been audited for that purpose.
- Preserve raw medication text separately from canonical medication names.

## Completion Criteria

Before finishing, summarize:

- ExECT fields or field families touched
- whether the output is benchmark-facing, clinically rich, or a bridge
- label-policy rules applied
- tests or examples covering nulls, coarse labels, inference boundaries, and normalization
- scorer caveats that must appear in reports

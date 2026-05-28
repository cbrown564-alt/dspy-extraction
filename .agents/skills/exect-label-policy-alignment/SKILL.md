---
name: exect-label-policy-alignment
description: Use when designing, prompting, scoring, or evaluating ExECTv2 benchmark-facing field-family or component extraction where annotation policy may differ from clinically richer labels, including diagnosis, seizure type, medication/current-Rx, seizure frequency, investigation, family spans, S0/S1 bridges, S4/S5 stacks, or Table 1 benchmark-reproduction work.
---

# ExECT Label Policy Alignment

Use this skill before ExECT benchmark-facing extraction, bridge, prompt, scorer,
or component-ceiling work when clinical labels and audited annotation policy may
diverge.

## Required Context

Read:

- `docs/current_research_program.md`
- `docs/component_ceiling_registry.md`
- `docs/experiments/exect/README.md`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/policies/published_benchmark_metrics.md` when making external benchmark
  or Table 1 claims
- `docs/taxonomy/taxonomy_primitive_catalog.md` for implemented ExECT benchmark bridges
- relevant ExECT loader, schema, scorer, primitive, and test files

Use archived prompt/error notes only when tracing a specific historical arm.
They are provenance, not current steering authority.

## Core Principle

Separate benchmark-facing annotation policy from clinically rich extraction.

A label may be clinically plausible but wrong for the audited ExECT scoring view. Benchmark-facing outputs should match the current canonical scoring view; clinically richer outputs should be preserved only through an explicit bridge or separate schema level.

Implemented benchmark bridges live in the ExECT primitive modules and typed registry, including:

- `exect.diagnosis.benchmark_bridge.v1`
- `exect.seizure_type.benchmark_bridge.v1`
- `exect.medication.benchmark_bridge.v1`
- `exect.frequency.benchmark_bridge.v1`

When changing label-policy behavior, update or extend typed primitives rather
than duplicating bridge logic in program modules. CUI/ontology-aware Table 1
reproduction remains blocked under the current B2 benchmark-reproduction
surface until an explicit all-family scorer exists.

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
- Treat annotated current-Rx medication as the benchmark-facing medication
  surface unless a new target policy says otherwise.
- Use lifecycle and temporality rows as diagnostic or interference-attribution
  evidence unless a preregistered scorer/gold-proxy design promotes them.
- Do not score current/planned/historical medication status as benchmark-facing unless the source and scorer semantics have been audited for that purpose.
- Preserve raw medication text separately from canonical medication names.

## Frequency Checks

- Treat frequency payload coverage as a substrate, not an isolated ceiling, until
  candidate selection, adjudication, and label construction are separately
  measured.
- Do not infer seizure type from frequency rows unless a tested bridge explicitly
  supports that behavior.
- Report broad payload precision and extra-candidate strata when using E1/E10
  frequency surfaces.

## Investigation And Family-Span Checks

- Treat broad-stack investigation strength as suggestive, not solved, until an
  isolated family probe or E12 decision confirms the component.
- Treat family-span payloads as prompt substrates until a preregistered
  full-note versus span comparison preserves recall and shows benefit.
- Keep false-family spans, evidence coverage, and character-budget effects
  visible in family-span reports.

## Completion Criteria

Before finishing, summarize:

- ExECT fields or field families touched
- whether the output is benchmark-facing, clinically rich, or a bridge
- whether the result is an isolated component ceiling, stacked baseline,
  diagnostic substrate, rejected arm, or blocked benchmark claim
- label-policy rules applied
- tests or examples covering nulls, coarse labels, inference boundaries, and normalization
- scorer caveats that must appear in reports

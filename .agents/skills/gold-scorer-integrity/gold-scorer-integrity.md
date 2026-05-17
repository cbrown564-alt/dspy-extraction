---
name: gold-scorer-integrity
description: Use when implementing or modifying scorers, metric aggregation, label normalization, benchmark comparisons, evaluation reports, or tests that assert model performance against gold labels.
---

# Gold Scorer Integrity

Scoring is part of the research claim. Treat scorer changes as high-risk even when the code looks small.

Follow this workflow:

1. Read the relevant dataset audit before changing scorer behavior:
   - ExECTv2: `docs/exect_gold_label_audit.md`
   - Gan: `docs/gan_2026_label_audit.md`
2. Identify whether the scorer is annotation-faithful, clinically corrected, or experimental. Do not mix these modes silently.
3. Normalize labels before comparing values. Put normalization in explicit functions with focused tests.
4. Preserve field-specific scoring where fields have different semantics.
5. Add or update regression examples for edge cases described in the audits.
6. Report metric definitions clearly in generated summaries and benchmark outputs.

## Required Design Checks

- Distinguish missing gold from true negative labels.
- Distinguish schema-invalid predictions from field-level wrong predictions.
- Keep exact match, normalized match, partial span match, and evidence support as separate concepts.
- Avoid averaging categorical evidence-support statuses as if they were numeric scores.
- Make `unknown`, abstention, and no-reference behavior explicit.
- Preserve enough per-document detail for error analysis, not just aggregate metrics.

## ExECTv2 Scoring Notes

- Diagnosis specificity and certainty handling can change apparent performance dramatically.
- Medication status and normalization must be scored consistently with the gold representation.
- Gold quality warnings should be available downstream when interpreting results.

## Gan Scoring Notes

- Convert seizure-frequency labels to the canonical numeric/month representation before ordinal or numeric scoring.
- Preserve special labels such as `unknown`, `no seizure frequency reference`, and `seizure free`.
- Handle cluster expressions through deterministic conversion.
- Apply plural unit normalization before conversion.
- Label/reference disagreement is a difficulty flag, not a replacement gold label.

## Completion Criteria

Before finishing, summarize:

- metric semantics changed or preserved
- normalization rules added or reused
- regression tests or examples used
- remaining scorer limitations

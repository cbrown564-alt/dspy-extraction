# Gan S0 Full-Validation Error Read

Date: 2026-05-18

Run artifact: `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z`

## Scope

This note reviews the synthesis-backed Gan S0 full-validation run before changing the next experiment target. It is grounded in `docs/gan_2026_label_audit.md`: `seizure_frequency_number[0]` remains the gold label, `reference` remains a secondary cross-check, and evidence quote support remains diagnostic rather than benchmark-facing label scoring.

## Metrics Snapshot

- Records predicted: 299 validation records.
- Schema-valid prediction rate: 97.3% with 95% bootstrap CI 95.7%-99.0%.
- Normalized-label accuracy: 51.5% with 95% bootstrap CI 45.7%-57.4%.
- Monthly-frequency accuracy: 62.9% with 95% bootstrap CI 57.0%-68.0%.
- Purist category accuracy: 70.1% with 95% bootstrap CI 64.9%-74.9%.
- Pragmatic category accuracy: 73.9% with 95% bootstrap CI 68.7%-79.0%.
- Evidence quote support rate: 89.9% with 95% bootstrap CI 86.3%-93.1%.

## Error Shape

The run emitted 8 invalid predictions, 20 monthly-frequency mismatches, and 20 evidence-support errors. Extra predictions were absent.

Invalid predictions split into two groups:

- Repairable surface forms: quoted special label (`"unknown"`) and reversed denominator ranges such as `1 per 3 week to 1 per 2 week`.
- Not safely repairable without changing meaning: incomplete cluster labels such as `1 cluster per week`, cluster labels with `unknown per cluster`, and null/abstained outputs where a label was required.

Monthly-frequency mismatches remain mostly semantic:

- 7 frequent gold labels were predicted as `unknown`, mostly cluster-frequency cases.
- 5 `unknown` gold labels were predicted as `no seizure frequency reference`.
- 1 `unknown` gold label was predicted as an infrequent quantified rate.
- 7 mismatches stayed inside the same frequent Pragmatic category but missed exact monthly value or Purist bucket.

Evidence-support errors remain a separate diagnostic problem:

- 9 quotes used ellipsis-style stitching or otherwise non-contiguous text.
- 2 joined multiple quotes into one evidence string.
- 1 used the label text `no seizure frequency reference` as evidence.
- 8 were paraphrased or lightly transformed source text.

## Decision

The next safe code change is a narrow deterministic postprocessor for repairable model-output surface forms only. It should preserve raw model output, mark `normalized_label_repaired`, and avoid guessing missing cluster counts or unknown per-cluster values.

Verifier/repair DSPy work is still warranted, but it should target the remaining semantic failures: cluster-to-unknown mistakes, unknown versus no-reference confusion, temporal-window denominator errors, and non-contiguous/paraphrased evidence quotes.

## Implemented Follow-Up

`clinical_extraction.programs.gan_frequency_s0` now normalizes two additional repairable surfaces in the prediction artifact bridge:

- quoted special labels such as `"unknown"` and `'unknown'`
- matching-count denominator ranges such as `1 per 10 day to 1 per 7 day` to `1 per 7 to 10 day`

The scorer semantics did not change. Raw exact, normalized-label, monthly-frequency, Purist, Pragmatic, and evidence-support metrics remain separate.

Follow-up regression coverage now also locks the non-repair boundary for semantic cluster failures observed in the same run. Incomplete labels such as `1 cluster per week`, `2 cluster per 3 month`, and `1 cluster per month, unknown per cluster` must remain unrepaired by the deterministic artifact bridge because adding the missing per-cluster count would require evidence-aware model or rule logic.

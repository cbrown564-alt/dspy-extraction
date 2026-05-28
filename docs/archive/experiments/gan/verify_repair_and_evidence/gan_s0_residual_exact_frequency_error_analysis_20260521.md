# Gan S0 Residual Exact-Frequency Error Analysis

Date: 2026-05-21  
Status: Research synthesis from full-validation run artifacts  
Run: `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`  
Dataset / split: `gan_2026_fixed_v1:validation`  
Scorer: `gan_frequency_deterministic_v1`  
Model / program: GPT 4.1-mini, temporal candidates + verify-repair guardrails  
Generated artifacts:

- `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/analysis/summary.json`
- `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/analysis/records.jsonl`

Follow-up residual slice artifacts:

- `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/analysis/exact_frequency_residual_slice/summary.json`
- `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/analysis/exact_frequency_residual_slice/monthly_misses.jsonl`
- `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/analysis/exact_frequency_residual_slice/error_read_selection.jsonl`
- `docs/experiments/gan/gan_s0_exact_frequency_residual_slice_error_read_20260521.md`
- `docs/experiments/gan/gan_s0_exact_frequency_residual_manual_read_20260521.md`

## Question

What is still preventing the promoted Gan S0 pipeline from matching the exact monthly seizure-frequency label, after it already reaches strong Purist/Pragmatic category performance and near-perfect schema/evidence diagnostics?

## Audit Assumptions

This analysis follows `docs/datasets/gan/gan_2026_label_audit.md` and `docs/policies/deterministic_scorer_semantics.md`:

- Primary gold is `seizure_frequency_number[0]`.
- `reference[0]` is a secondary difficulty signal, not gold.
- `unknown` and `no seizure frequency reference` remain distinct.
- Monthly-frequency, Purist, and Pragmatic metrics are benchmark-facing; normalized-label exact is a stricter format-fidelity diagnostic.
- Evidence support is diagnostic unless a comparison group explicitly makes it prediction-affecting.

## Metrics Snapshot

The analysis covered all 299 validation records. One prediction was invalid, leaving 298 scored predictions.

| Metric | Correct / valid | Accuracy |
| --- | ---: | ---: |
| Normalized label exact | 156 / 298 | 52.3% |
| Monthly frequency | 194 / 298 | 65.1% |
| Purist category | 228 / 298 | 76.5% |
| Pragmatic category | 251 / 298 | 84.2% |

The exact-frequency gap is therefore **104 valid monthly misses**, plus **1 invalid prediction** operationally.

## Metric Divergence

| Pattern | Meaning | Count |
| --- | --- | ---: |
| `1111` | normalized label, monthly, Purist, and Pragmatic all match | 156 |
| `0111` | monthly/category match, but label surface differs | 38 |
| `0011` | Purist and Pragmatic match, but exact monthly value differs | 34 |
| `0001` | only Pragmatic category matches | 23 |
| `0000` | normalized, monthly, Purist, and Pragmatic all miss | 47 |

Read: **57/104 exact-monthly misses still preserve a category-level benchmark signal** (`0011` or `0001`). The remaining **47/104** are clinically and benchmark-severe across all coarse views.

## Residual Monthly-Frequency Failure Classes

| Failure class | Count | Interpretation |
| --- | ---: | --- |
| `pragmatic_match_monthly_divergence` | 31 | Correct coarse frequent/infrequent and Purist bin, wrong exact monthly conversion. Examples include `10 per 3 month` → `6 per 2 month`. |
| `purist_bin_boundary_within_pragmatic` | 20 | Correct Pragmatic bucket but wrong Purist bin/monthly value. Often high-frequency or boundary rates. |
| `other_semantic_mismatch` | 11 | Broad semantic failures, commonly specific frequency predicted as `unknown`. |
| `unknown_as_high_rate` | 10 | Gold `unknown` predicted as a frequent quantified rate. |
| `frequent_undercalled` | 8 | Frequent gold collapsed below the Pragmatic threshold. |
| `cluster_semantic_mismatch` | 7 | Cluster count/window/per-cluster components partly wrong. |
| `cluster_collapsed_to_rate` | 5 | Cluster structure lost or mapped to `unknown`/simple rate. |
| `frequent_overcalled` | 4 | Infrequent gold overcalled as frequent. |
| `unknown_as_quantified_rate` | 4 | Gold `unknown` predicted as an infrequent quantified rate. |
| `unknown_vs_seizure_free` | 2 | Gold `unknown` predicted as seizure-free. |
| `cluster_structure_swap` | 1 | Unknown cluster spacing converted to an explicit cluster frequency. |
| `unknown_vs_no_reference` | 1 | Gold `unknown` predicted as no frequency reference. |

Separately, **38 normalized-label misses are diagnostic-only** because monthly/Purist/Pragmatic still match:

- `seizure_free_label_shape_mismatch`: 21
- `monthly_match_label_surface_mismatch`: 7
- `seizure_free_to_no_reference_monthly_match`: 6
- `unknown_cluster_label_shape_mismatch`: 4

These should not drive the next benchmark-facing model intervention unless the project explicitly targets label-scheme reproduction.

## Strata

| Stratum | Records | Monthly accuracy | Operational failure rate |
| --- | ---: | ---: | ---: |
| Frequent gold | 152 | 62.9% | 37.5% |
| Infrequent gold | 51 | 43.1% | 56.9% |
| Unknown gold | 40 | 55.0% | 45.0% |
| No seizure information | 56 | 98.2% | 1.8% |
| Hard cases (`label != reference`) | 39 | 71.8% | 28.2% |
| Non-hard cases | 260 | 64.1% | 36.2% |

The surprising result is that audit-defined hard cases are **not** the main residual weakness. The pipeline does worse on ordinary non-hard cases than on `label != reference` cases. That suggests the remaining problem is less "ambiguous second reader" and more exact arithmetic/window extraction under the Gan label scheme.

The weakest bucket is **infrequent gold**: only **43.1%** monthly accuracy, with 29 exact-monthly misses. This includes long-denominator rates and low-frequency ranges such as:

- `2 to 3 per 15 month` → `1 to 3 per month`
- `2 to 4 per 3 month` → `2 to 4 per month`
- `1 per 4 to 5 week` → `1 per 4 week`
- `7 per year` → `1 per month`

## Candidate-Scaffold Finding

The deterministic temporal candidate diagnostics show low exact gold coverage on the full validation split:

- Gold label present in candidate set: **16/299 (5.4%)**
- Among monthly misses: **6/104** had gold present in the candidate set
- Among monthly misses: **7/104** had any deterministic candidate at all

This does **not** contradict the cap-25 gains from temporal candidates. The candidate scaffold appears useful as a cueing/attention mechanism, not because it usually enumerates the final gold label. For exact-frequency improvement, the current candidate primitive is too sparse.

## Interpretation

The promoted Gan pipeline has mostly solved "is there seizure-frequency information?" and is strong on no-information records. It has not solved exact numeric normalization.

The residual errors fall into three useful groups:

1. **Arithmetic/window precision errors**: `pragmatic_match_monthly_divergence` and many boundary cases. These preserve coarse category but miss numerator, denominator, or unit. This is the largest actionable group.
2. **Unknown-vs-quantified policy errors**: 17 unknown-related monthly misses (`unknown_as_high_rate`, `unknown_as_quantified_rate`, `unknown_vs_seizure_free`, `unknown_vs_no_reference`, `cluster_structure_swap`). These are clinically meaningful because they invent specificity where gold says frequency is unclear.
3. **Cluster composition errors**: 13 cluster-related monthly misses (`cluster_semantic_mismatch`, `cluster_collapsed_to_rate`, `cluster_structure_swap`). These need explicit cluster-slot handling; deterministic repair should not guess missing per-cluster counts.

The main non-actionable group for benchmark improvement is label-shape mismatch where monthly already matches. Those cases may matter for label-scheme fidelity, but they are not the limiting benchmark metric.

## Deterministic Repair Candidates

No broad deterministic repair is justified from this analysis.

Allowed narrow repair remains the existing surface bridge behavior:

- quoted special labels such as `"unknown"`
- unambiguous denominator range surfaces such as `1 per 3 week to 1 per 2 week`
- label-shape repairs that preserve monthly/Purist/Pragmatic values and keep raw output separately

Do **not** deterministically repair:

- cluster labels missing per-cluster counts
- `unknown` versus quantified rates
- `unknown` versus no-reference or seizure-free
- long-window denominator choices requiring note interpretation

Those are semantic failures, not surface normalization bugs.

## Recommended Next Work

1. **Create a Gan exact-frequency residual slice** from the 104 monthly misses, stratified into:
   - arithmetic/window precision
   - unknown-vs-quantified
   - cluster composition
   - infrequent long-denominator rates

2. **Run an error-read on ~30 representative records** before any new model calls:
   - 10 arithmetic/window cases
   - 8 unknown-vs-quantified cases
   - 8 cluster cases
   - 4 infrequent boundary cases

   Status: exported as `docs/experiments/gan/gan_s0_exact_frequency_residual_slice_error_read_20260521.md`.
   The read queue covers 30 records from the 104 benchmark-severe monthly misses and leaves
   13 `other_benchmark_severe` misses visible but unselected for this targeted pass.
   Manual-read synthesis is recorded in
   `docs/experiments/gan/gan_s0_exact_frequency_residual_manual_read_20260521.md`.

3. **Design a revised candidate primitive only after that read**. Candidate coverage is currently too sparse to fix exact monthly errors. The likely useful primitive is not "more candidate labels" generically, but structured slots:
   - numerator / range
   - denominator count
   - denominator unit
   - current-window cue
   - cluster frequency
   - per-cluster count
   - unknown/no-reference/seizure-free policy cue

4. **Test as Axis 3 on the winning Gan skeleton**, not as a new architecture:
   - fixed `stage_graph_id`: `g2_candidates_adjudicate` or promoted full-validation skeleton if confirmatory
   - varied factor: `implementation_variant`
   - comparison group candidate: `gan_s0_exact_frequency_slot_payload_gpt_cap25_v1`

5. **Keep full validation/Qwen deferred** until a GPT cap-25 exact-frequency slice shows a real monthly lift, especially on infrequent and unknown strata.

## Caveats

- This is local synthetic validation, not Gan Real(300)/Real(150) reproduction.
- Metrics are from valid predictions only unless explicitly described as operational failure rate.
- The analysis uses the current deterministic failure taxonomy; some `other_semantic_mismatch` records need manual review before being assigned to a more specific mechanism.
- Candidate diagnostics report whether the exact gold label appeared in deterministic candidates, not whether candidate text helped model attention.

# Gan S0 Error Analysis: gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice

## Run

- Artifact directory: `runs\gan_s0_candidate_builder_gap_v1_gpt4_1_mini_slice_20260523T164046Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `record_ids_filter`
- Records in split: 299
- Records analyzed: 25
- Valid scored predictions: 25
- Invalid or missing predictions: 0

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 92.0% | 23 | 25 |
| monthly_frequency | 92.0% | 23 | 25 |
| purist_category | 92.0% | 23 | 25 |
| pragmatic_category | 92.0% | 23 | 25 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Stratified operational reporting

- All-record denominator: 25 (valid scored: 25; invalid/missing: 0)
- Overall operational failure rate: 8.0% (2 failures)

| Stratum | All records | Valid scored | Operational failure rate | Monthly (valid only) |
| --- | ---: | ---: | ---: | ---: |
| hard_case=true | 2 | 2 | 0.0% | 100.0% |
| hard_case=false | 23 | 23 | 8.7% | 91.3% |
| row_ok=true | 24 | 24 | 8.3% | 91.7% |
| row_ok=false | 1 | 1 | 0.0% | 100.0% |
| gold_pragmatic=frequent | 5 | 5 | 0.0% | 100.0% |
| gold_pragmatic=infrequent | 18 | 18 | 11.1% | 88.9% |
| gold_pragmatic=no_seizure_information | 2 | 2 | 0.0% | 100.0% |

## Temporal candidate diagnostics (deterministic scaffold)

These candidates are extracted without model calls and do not change benchmark-facing scoring.
- Gold label present in candidate set: 23/25 (92.0%)

| Record | Gold | Candidates | Gold in candidates |
| --- | --- | --- | --- |
| `gan_13058` | `2 per 7 month` | `2 per 7 month` | yes |
| `gan_13123` | `1 per year` | `1 per year` | yes |
| `gan_13149` | `3 per year` | `3 per year` | yes |
| `gan_13190` | `1 per 5 month` | `1 per 5 month` | yes |
| `gan_13574` | `seizure free for multiple year` | — | no |
| `gan_13598` | `seizure free for multiple year` | — | no |
| `gan_14214` | `2 to 4 per month` | `2 to 4 per month` | yes |
| `gan_14250` | `2 per month` | `2 per month` | yes |
| `gan_14485` | `2 per 3 month` | `2 per 3 month` | yes |
| `gan_14562` | `3 per 6 month` | `3 per 6 month` | yes |
| `gan_14628` | `2 per 2 month` | `2 per 2 month` | yes |
| `gan_14689` | `3 per 2 month` | `3 per 2 month` | yes |
| `gan_14792` | `1 per month` | `1 per month` | yes |
| `gan_14821` | `1 per month` | `1 per month` | yes |
| `gan_14881` | `1 per month` | `1 per month` | yes |
| `gan_14965` | `1 per 3 month` | `1 per 3 month` | yes |
| `gan_14973` | `1 per month` | `1 per month` | yes |
| `gan_15127` | `5 per 13 month` | `5 per 13 month` | yes |
| `gan_15168` | `multiple per 15 month` | `multiple per 15 month` | yes |
| `gan_15193` | `multiple per 13 month` | `multiple per 13 month` | yes |
| `gan_15302` | `1 to 2 per 14 month` | `1 to 2 per 14 month` | yes |
| `gan_15442` | `1 cluster per 4 day, 2 per cluster` | `1 cluster per 4 day, 2 per cluster` | yes |
| `gan_16529` | `1 per 5 day` | `1 per 5 day` | yes |
| `gan_16645` | `5 per 7 month` | `5 per 7 month` | yes |
| `gan_16750` | `6 per 7 month` | `6 per 7 month` | yes |

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 23 | 92.0% |
| `0000` | all_four_wrong | 2 | 8.0% |

### Logical containment on this run

- Normalized exact (23 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (23 records): always implies Purist and Pragmatic; 23 also have normalized exact.
- Purist match (23 records): always implies Pragmatic; 23 also match monthly.
- Pragmatic-only wins (pattern `0001`): 0 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 0 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 0
- **pragmatic_match_monthly_divergence**: 0
- **purist_match_monthly_divergence**: 0
- **monthly_match_label_surface_mismatch**: 0

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 2 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| other_semantic_mismatch | 1 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 1 |
| frequent_overcalled | 1 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| other_semantic_mismatch | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| other_semantic_mismatch | 1 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| other_semantic_mismatch | 1 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| other_semantic_mismatch | 1 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure classes on this run are `frequent_overcalled`, `other_semantic_mismatch` (1 scored miss each). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 0 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 0 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 0; pragmatic-without-monthly: 0. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 0 abstentions/null outputs and 0 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_13058 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 7 month | 2 per 7 month |
| gan_13123 | scored | Y | Y | Y | Y | all_metrics_match | 1 per year | 1 per year |
| gan_13149 | scored | Y | Y | Y | Y | all_metrics_match | 3 per year | 3 per year |
| gan_13190 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 5 month | 1 per 5 month |
| gan_13574 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple year | seizure free for multiple year |
| gan_13598 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple year | seizure free for multiple year |
| gan_14214 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 4 per month | 2 to 4 per month |
| gan_14250 | scored | Y | Y | Y | Y | all_metrics_match | 2 per month | 2 per month |
| gan_14485 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 3 month | 2 per 3 month |
| gan_14562 | scored | Y | Y | Y | Y | all_metrics_match | 3 per 6 month | 3 per 6 month |
| gan_14628 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 2 month | 2 per 2 month |
| gan_14689 | scored | Y | Y | Y | Y | all_metrics_match | 3 per 2 month | 3 per 2 month |
| gan_14792 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_14821 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_14881 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_14965 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 3 month | 1 per 3 month |
| gan_14973 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_15127 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 13 month | 5 per 13 month |
| gan_15168 | scored | N | N | N | N | other_semantic_mismatch | multiple per 15 month | unknown |
| gan_15193 | scored | N | N | N | N | frequent_overcalled | multiple per 13 month | multiple per month |
| gan_15302 | scored | Y | Y | Y | Y | all_metrics_match | 1 to 2 per 14 month | 1 to 2 per 14 month |
| gan_15442 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster |
| gan_16529 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 5 day | 1 per 5 day |
| gan_16645 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 7 month | 5 per 7 month |
| gan_16750 | scored | Y | Y | Y | Y | all_metrics_match | 6 per 7 month | 6 per 7 month |

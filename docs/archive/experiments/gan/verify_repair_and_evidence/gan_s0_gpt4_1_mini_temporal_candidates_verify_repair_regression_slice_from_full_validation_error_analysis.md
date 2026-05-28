# Gan S0 Error Analysis: gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails

## Run

- Artifact directory: `runs\gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `record_ids_filter`
- Records in split: 299
- Records analyzed: 14
- Valid scored predictions: 14
- Invalid or missing predictions: 0

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 50.0% | 7 | 14 |
| monthly_frequency | 57.1% | 8 | 14 |
| purist_category | 64.3% | 9 | 14 |
| pragmatic_category | 64.3% | 9 | 14 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Stratified operational reporting

- All-record denominator: 14 (valid scored: 14; invalid/missing: 0)
- Overall operational failure rate: 42.9% (6 failures)

| Stratum | All records | Valid scored | Operational failure rate | Monthly (valid only) |
| --- | ---: | ---: | ---: | ---: |
| hard_case=true | 0 | 0 | n/a | n/a |
| hard_case=false | 14 | 14 | 42.9% | 57.1% |
| row_ok=true | 12 | 12 | 41.7% | 58.3% |
| row_ok=false | 2 | 2 | 50.0% | 50.0% |
| gold_pragmatic=frequent | 6 | 6 | 16.7% | 83.3% |
| gold_pragmatic=infrequent | 4 | 4 | 75.0% | 25.0% |
| gold_pragmatic=no_seizure_information | 1 | 1 | 0.0% | 100.0% |
| gold_pragmatic=unknown | 3 | 3 | 66.7% | 33.3% |

## Temporal candidate diagnostics (deterministic scaffold)

These candidates are extracted without model calls and do not change benchmark-facing scoring.
- Gold label present in candidate set: 10/14 (71.4%)

| Record | Gold | Candidates | Gold in candidates |
| --- | --- | --- | --- |
| `gan_10509` | `unknown` | — | no |
| `gan_10751` | `unknown` | — | no |
| `gan_11221` | `unknown` | — | no |
| `gan_11733` | `no seizure frequency reference` | — | no |
| `gan_12130` | `multiple per week` | `multiple per week` | yes |
| `gan_12810` | `5 per 2 month` | `5 per 2 month` | yes |
| `gan_12823` | `9 per month` | `9 per month` | yes |
| `gan_10052` | `4 cluster per 3 month, multiple per cluster` | `4 cluster per 3 month, multiple per cluster` | yes |
| `gan_10003` | `1 cluster per week, multiple per cluster` | `1 cluster per week, multiple per cluster` | yes |
| `gan_10410` | `1 cluster per week, 3 to 4 per cluster` | `1 cluster per week, 3 to 4 per cluster` | yes |
| `gan_13123` | `1 per year` | `1 per year` | yes |
| `gan_14485` | `2 per 3 month` | `2 per 3 month` | yes |
| `gan_14881` | `1 per month` | `1 per month` | yes |
| `gan_15306` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | yes |

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 7 | 50.0% |
| `0000` | all_four_wrong | 5 | 35.7% |
| `0111` | monthly_purist_pragmatic_not_normalized | 1 | 7.1% |
| `0011` | purist_pragmatic_not_monthly | 1 | 7.1% |

### Logical containment on this run

- Normalized exact (7 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (8 records): always implies Purist and Pragmatic; 7 also have normalized exact.
- Purist match (9 records): always implies Pragmatic; 8 also match monthly.
- Pragmatic-only wins (pattern `0001`): 0 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 1 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 0
- **pragmatic_match_monthly_divergence**: 1
- **purist_match_monthly_divergence**: 1
- **monthly_match_label_surface_mismatch**: 1

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 6 |
| diagnostic_only | 1 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| frequent_undercalled | 1 |
| other_semantic_mismatch | 1 |
| pragmatic_match_monthly_divergence | 1 |
| unknown_as_high_rate | 1 |
| unknown_vs_seizure_free | 1 |

#### diagnostic_only

| Failure class | Count |
| --- | ---: |
| monthly_match_label_surface_mismatch | 1 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| unknown_as_high_rate | 1 |
| unknown_vs_seizure_free | 1 |
| frequent_undercalled | 1 |
| monthly_match_label_surface_mismatch | 1 |
| pragmatic_match_monthly_divergence | 1 |
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
| frequent_undercalled | 1 |
| monthly_match_label_surface_mismatch | 1 |
| other_semantic_mismatch | 1 |
| pragmatic_match_monthly_divergence | 1 |
| unknown_as_high_rate | 1 |
| unknown_vs_seizure_free | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| frequent_undercalled | 1 |
| other_semantic_mismatch | 1 |
| pragmatic_match_monthly_divergence | 1 |
| unknown_as_high_rate | 1 |
| unknown_vs_seizure_free | 1 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| frequent_undercalled | 1 |
| other_semantic_mismatch | 1 |
| unknown_as_high_rate | 1 |
| unknown_vs_seizure_free | 1 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| frequent_overcalled | 1 |
| frequent_undercalled | 1 |
| other_semantic_mismatch | 1 |
| unknown_as_high_rate | 1 |
| unknown_vs_seizure_free | 1 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure classes on this run are `frequent_overcalled`, `frequent_undercalled`, `other_semantic_mismatch`, `pragmatic_match_monthly_divergence`, `unknown_as_high_rate`, `unknown_vs_seizure_free` (1 scored miss each). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 0 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 0 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 1; pragmatic-without-monthly: 1. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 0 abstentions/null outputs and 0 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10509 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_10751 | scored | N | N | N | N | unknown_as_high_rate | unknown | 1 cluster per week, multiple per cluster |
| gan_11221 | scored | N | N | N | N | unknown_vs_seizure_free | unknown | seizure free for 4 month |
| gan_11733 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_12130 | scored | N | N | N | N | frequent_undercalled | multiple per week | 3 per year |
| gan_12810 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 2 month | 5 per 2 month |
| gan_12823 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 9 per month | 9 per 1 month |
| gan_10052 | scored | Y | Y | Y | Y | all_metrics_match | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster |
| gan_10003 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster |
| gan_10410 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster |
| gan_13123 | scored | Y | Y | Y | Y | all_metrics_match | 1 per year | 1 per year |
| gan_14485 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 2 per 3 month | 1 per 3 month |
| gan_14881 | scored | N | N | N | N | other_semantic_mismatch | 1 per month | unknown |
| gan_15306 | scored | N | N | N | N | frequent_overcalled | 2 to 3 per 15 month | 1 to 3 per month |

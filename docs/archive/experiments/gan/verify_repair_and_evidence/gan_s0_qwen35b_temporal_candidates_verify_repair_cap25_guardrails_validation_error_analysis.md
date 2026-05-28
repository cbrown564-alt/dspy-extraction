# Gan S0 Error Analysis: gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation

## Run

- Artifact directory: `runs\gan_s0_qwen35b_temporal_candidates_verify_repair_cap25_guardrails_validation_20260519T183213Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `predicted_subset`
- Records in split: 299
- Records analyzed: 25
- Valid scored predictions: 25
- Invalid or missing predictions: 0

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 40.0% | 10 | 25 |
| monthly_frequency | 44.0% | 11 | 25 |
| purist_category | 64.0% | 16 | 25 |
| pragmatic_category | 84.0% | 21 | 25 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Stratified operational reporting

- All-record denominator: 25 (valid scored: 25; invalid/missing: 0)
- Overall operational failure rate: 56.0% (14 failures)

| Stratum | All records | Valid scored | Operational failure rate | Monthly (valid only) |
| --- | ---: | ---: | ---: | ---: |
| hard_case=true | 5 | 5 | 60.0% | 40.0% |
| hard_case=false | 20 | 20 | 55.0% | 45.0% |
| row_ok=true | 24 | 24 | 58.3% | 41.7% |
| row_ok=false | 1 | 1 | 0.0% | 100.0% |
| gold_pragmatic=frequent | 16 | 16 | 68.8% | 31.2% |
| gold_pragmatic=infrequent | 4 | 4 | 0.0% | 100.0% |
| gold_pragmatic=no_seizure_information | 2 | 2 | 0.0% | 100.0% |
| gold_pragmatic=unknown | 3 | 3 | 100.0% | 0.0% |

## Temporal candidate diagnostics (deterministic scaffold)

These candidates are extracted without model calls and do not change benchmark-facing scoring.
- Gold label present in candidate set: 4/25 (16.0%)

| Record | Gold | Candidates | Gold in candidates |
| --- | --- | --- | --- |
| `gan_10052` | `4 cluster per 3 month, multiple per cluster` | — | no |
| `gan_10434` | `multiple cluster per week, 2 to 3 per cluster` | — | no |
| `gan_10618` | `unknown, 4 to 6 per cluster` | — | no |
| `gan_12679` | `1 per day` | — | no |
| `gan_13123` | `1 per year` | `1 per year` | yes |
| `gan_14485` | `2 per 3 month` | `2 per 3 month` | yes |
| `gan_14881` | `1 per month` | `1 per month` | yes |
| `gan_15306` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | yes |
| `gan_1584` | `11 per month` | — | no |
| `gan_15997` | `10 per 3 month` | — | no |
| `gan_16251` | `14 per 4 month` | — | no |
| `gan_16772` | `9 per 5 month` | — | no |
| `gan_16825` | `10 per 6 month` | — | no |
| `gan_17287` | `1 per 1 to 2 day` | — | no |
| `gan_1794` | `8 per 2 month` | — | no |
| `gan_2609` | `1 per day` | — | no |
| `gan_3246` | `2 cluster per month, 4 per cluster` | — | no |
| `gan_4113` | `1 per 1 to 2 day` | — | no |
| `gan_4702` | `multiple per day` | — | no |
| `gan_4709` | `multiple per day` | — | no |
| `gan_4956` | `seizure free for 7 month` | — | no |
| `gan_536` | `1 per 2 day` | — | no |
| `gan_6532` | `unknown, multiple per cluster` | — | no |
| `gan_7894` | `seizure free for multiple year` | — | no |
| `gan_9566` | `unknown` | — | no |

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 10 | 40.0% |
| `0011` | purist_pragmatic_not_monthly | 5 | 20.0% |
| `0000` | all_four_wrong | 4 | 16.0% |
| `0001` | pragmatic_only | 5 | 20.0% |
| `0111` | monthly_purist_pragmatic_not_normalized | 1 | 4.0% |

### Logical containment on this run

- Normalized exact (10 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (11 records): always implies Purist and Pragmatic; 10 also have normalized exact.
- Purist match (16 records): always implies Pragmatic; 11 also match monthly.
- Pragmatic-only wins (pattern `0001`): 5 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 5 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 5
- **pragmatic_match_monthly_divergence**: 10
- **purist_match_monthly_divergence**: 5
- **monthly_match_label_surface_mismatch**: 1

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 14 |
| diagnostic_only | 1 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| purist_bin_boundary_within_pragmatic | 5 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_semantic_mismatch | 2 |
| cluster_collapsed_to_rate | 1 |
| cluster_structure_swap | 1 |
| other_semantic_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

#### diagnostic_only

| Failure class | Count |
| --- | ---: |
| seizure_free_label_shape_mismatch | 1 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| purist_bin_boundary_within_pragmatic | 5 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_semantic_mismatch | 2 |
| cluster_structure_swap | 1 |
| other_semantic_mismatch | 1 |
| cluster_collapsed_to_rate | 1 |
| seizure_free_label_shape_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| purist_bin_boundary_within_pragmatic | 5 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_semantic_mismatch | 2 |
| cluster_collapsed_to_rate | 1 |
| cluster_structure_swap | 1 |
| other_semantic_mismatch | 1 |
| seizure_free_label_shape_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| purist_bin_boundary_within_pragmatic | 5 |
| pragmatic_match_monthly_divergence | 3 |
| cluster_semantic_mismatch | 2 |
| cluster_collapsed_to_rate | 1 |
| cluster_structure_swap | 1 |
| other_semantic_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| purist_bin_boundary_within_pragmatic | 5 |
| cluster_collapsed_to_rate | 1 |
| cluster_structure_swap | 1 |
| other_semantic_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| cluster_collapsed_to_rate | 1 |
| cluster_structure_swap | 1 |
| other_semantic_mismatch | 1 |
| unknown_as_quantified_rate | 1 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure class on this run is `purist_bin_boundary_within_pragmatic` (5 scored misses). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 4 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 5 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 5; pragmatic-without-monthly: 10. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 0 abstentions/null outputs and 0 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10052 | scored | Y | Y | Y | Y | all_metrics_match | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster |
| gan_10434 | scored | N | N | Y | Y | cluster_semantic_mismatch | multiple cluster per week, 2 to 3 per cluster | multiple cluster per week, multiple per cluster |
| gan_10618 | scored | N | N | N | N | cluster_structure_swap | unknown, 4 to 6 per cluster | 1 cluster per week, multiple per cluster |
| gan_12679 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per day | 1 to 2 cluster per month, multiple per cluster |
| gan_13123 | scored | Y | Y | Y | Y | all_metrics_match | 1 per year | 1 per year |
| gan_14485 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 3 month | 2 per 3 month |
| gan_14881 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_15306 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 15 month | 2 to 3 per 15 month |
| gan_1584 | scored | Y | Y | Y | Y | all_metrics_match | 11 per month | 11 per month |
| gan_15997 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 10 per 3 month | 8 per 3 month |
| gan_16251 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 14 per 4 month | 7 per month |
| gan_16772 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 9 per 5 month | 9 per 3 month |
| gan_16825 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 10 per 6 month | 10 per 3 month |
| gan_17287 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 1 to 2 day | 1 per day |
| gan_1794 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 8 per 2 month | 6 per 2 month |
| gan_2609 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_3246 | scored | N | N | Y | Y | cluster_semantic_mismatch | 2 cluster per month, 4 per cluster | 2 cluster per month, multiple per cluster |
| gan_4113 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 1 to 2 day | 1 per day |
| gan_4702 | scored | Y | Y | Y | Y | all_metrics_match | multiple per day | multiple per day |
| gan_4709 | scored | N | N | N | N | other_semantic_mismatch | multiple per day | unknown |
| gan_4956 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 7 month | seizure free for 7 month |
| gan_536 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_6532 | scored | N | N | N | N | cluster_collapsed_to_rate | unknown, multiple per cluster | 5 per 2 week |
| gan_7894 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple year | seizure free for 35 year |
| gan_9566 | scored | N | N | N | N | unknown_as_quantified_rate | unknown | 1 to 2 per 8 week |

# Gan S0 Error Analysis: gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails

## Run

- Artifact directory: `runs\gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T180329Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `record_ids_filter`
- Records in split: 299
- Records analyzed: 14
- Valid scored predictions: 14
- Invalid or missing predictions: 0

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 100.0% | 14 | 14 |
| monthly_frequency | 100.0% | 14 | 14 |
| purist_category | 100.0% | 14 | 14 |
| pragmatic_category | 100.0% | 14 | 14 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Stratified operational reporting

- All-record denominator: 14 (valid scored: 14; invalid/missing: 0)
- Overall operational failure rate: 0.0% (0 failures)

| Stratum | All records | Valid scored | Operational failure rate | Monthly (valid only) |
| --- | ---: | ---: | ---: | ---: |
| hard_case=true | 0 | 0 | n/a | n/a |
| hard_case=false | 14 | 14 | 0.0% | 100.0% |
| row_ok=true | 12 | 12 | 0.0% | 100.0% |
| row_ok=false | 2 | 2 | 0.0% | 100.0% |
| gold_pragmatic=frequent | 6 | 6 | 0.0% | 100.0% |
| gold_pragmatic=infrequent | 4 | 4 | 0.0% | 100.0% |
| gold_pragmatic=no_seizure_information | 1 | 1 | 0.0% | 100.0% |
| gold_pragmatic=unknown | 3 | 3 | 0.0% | 100.0% |

## Temporal candidate diagnostics (deterministic scaffold)

These candidates are extracted without model calls and do not change benchmark-facing scoring.
- Gold label present in candidate set: 4/14 (28.6%)

| Record | Gold | Candidates | Gold in candidates |
| --- | --- | --- | --- |
| `gan_10509` | `unknown` | — | no |
| `gan_10751` | `unknown` | — | no |
| `gan_11221` | `unknown` | — | no |
| `gan_11733` | `no seizure frequency reference` | — | no |
| `gan_12130` | `multiple per week` | — | no |
| `gan_12810` | `5 per 2 month` | — | no |
| `gan_12823` | `9 per month` | — | no |
| `gan_10003` | `1 cluster per week, multiple per cluster` | — | no |
| `gan_10052` | `4 cluster per 3 month, multiple per cluster` | — | no |
| `gan_10410` | `1 cluster per week, 3 to 4 per cluster` | — | no |
| `gan_13123` | `1 per year` | `1 per year` | yes |
| `gan_14485` | `2 per 3 month` | `2 per 3 month` | yes |
| `gan_14881` | `1 per month` | `1 per month` | yes |
| `gan_15306` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | yes |

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 14 | 100.0% |

### Logical containment on this run

- Normalized exact (14 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (14 records): always implies Purist and Pragmatic; 14 also have normalized exact.
- Purist match (14 records): always implies Pragmatic; 14 also match monthly.
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

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

_No misses._

#### Misses against **monthly**

_No misses._

#### Misses against **purist**

_No misses._

#### Misses against **pragmatic**

_No misses._

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

No benchmark-severe scored misses appear in this run; remaining cleanup is diagnostic-only or operational invalid/abstention handling.

Cluster-format errors account for 0 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 0 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 0; pragmatic-without-monthly: 0. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 0 abstentions/null outputs and 0 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_10509 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_10751 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_11221 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_11733 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_12130 | scored | Y | Y | Y | Y | all_metrics_match | multiple per week | multiple per week |
| gan_12810 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 2 month | 5 per 2 month |
| gan_12823 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_10003 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster |
| gan_10052 | scored | Y | Y | Y | Y | all_metrics_match | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster |
| gan_10410 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster |
| gan_13123 | scored | Y | Y | Y | Y | all_metrics_match | 1 per year | 1 per year |
| gan_14485 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 3 month | 2 per 3 month |
| gan_14881 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_15306 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 15 month | 2 to 3 per 15 month |

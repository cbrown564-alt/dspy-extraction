# Gan S0 Expanded Builders — Residual Slice Replay v3

Date: 2026-05-21  
Parent: `docs/experiments/gan/gan_s0_residual_candidate_builder_expansion_20260521.md`  
Prior replay: `docs/experiments/gan/gan_s0_exact_frequency_slot_payload_residual_slice_replay_v2_20260521.md`  
Comparison group: `gan_s0_exact_frequency_slot_payload_residual_slice_gpt_v1` (same config; builder-gap code change only)

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema | S0 seizure frequency |
| Research axis | 3 — expanded deterministic builders (builder-gap pass) |
| `stage_graph_id` | `g2_candidates_adjudicate` |
| `implementation_variant` | `cand_prose_v1` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed: GPT 4.1-mini, 30-record residual queue, single-pass adjudication v1.1, scorer `gan_frequency_deterministic_v1`, no verify-repair.

Varied: post-v2 **builder-gap** surfaces in `temporal_candidates.py` (`_last_convulsive_with_occasional_clusters`, `_daily_seizure_type_frequency`).

## Runs

| arm | run_id | monthly | norm exact | schema | evidence |
| --- | --- | ---: | ---: | ---: | ---: |
| v2 S0 (expanded builders) | `gan_s0_slot_s0_residual_slice_gpt4_1_mini_20260521T071756Z` | **63.3%** (19/30) | 60.0% | 100% | 100% |
| **v3 S0 (builder gaps)** | `gan_s0_slot_s0_residual_slice_gpt4_1_mini_20260521T075145Z` | **76.7%** (23/30) | 73.3% | 100% | 100% |

Replay artifact: `artifacts/gan_expanded_builders_residual_replay_v3_20260521/summary.json`

## v2 vs v3 headline

| Metric | v2 | v3 | Δ |
| --- | ---: | ---: | ---: |
| Monthly correct | 19/30 | **23/30** | **+4** (+13.4pp) |
| Normalized exact | 60.0% | 73.3% | +13.3pp |
| Monthly recoveries vs v2 | — | **5** | — |
| Monthly regressions vs v2 | — | **1** | — |

**Net read:** builder-gap pass yields **directional lift** on the hard queue (+4 monthly net). Not sufficient alone for full-validation promotion (slice n=30, paired tradeoff).

## Builder-gap target records (5)

| record_id | gold | v2 monthly | v3 monthly | v3 predicted | Notes |
| --- | --- | --- | --- | --- | --- |
| `gan_12667` | `1 per day` | miss | **hit** | `1 per day` | daily absences candidate |
| `gan_12679` | `1 per day` | miss | **hit** | `1 per day` | daily absences candidate |
| `gan_15240` | `multiple cluster per 12 month, multiple per cluster` | miss | **hit** | match | long-window cluster builder |
| `gan_15255` | `multiple cluster per 15 month, multiple per cluster` | miss | **hit** | match | long-window cluster builder |
| `gan_12562` | `1 per day` | miss | miss | `3 to 4 per week` | `1 per day` in candidates; model prefers GTC quote |

**Builder-gap hit rate:** 4/5 monthly (80%) when gold enters candidate set.

## Paired deltas vs v2

| Category | record_ids |
| --- | --- |
| Monthly recoveries (+5) | `gan_12667`, `gan_12679`, `gan_10751`, `gan_15240`, `gan_15255` |
| Monthly regressions (−1) | `gan_10434` (`multiple cluster per week, 2 to 3 per cluster` → `1 cluster per week, 2 to 3 per cluster`) |

`gan_10751` recovery is incidental (unknown stratum); not targeted by builder-gap pass.

## Per-group monthly correct

| Residual group | records | v2 S0 | v3 S0 | Δ |
| --- | ---: | ---: | ---: | ---: |
| `arithmetic_window_precision` | 10 | 5/10 | **7/10** | +2 |
| `cluster_composition` | 8 | 5/8 | **7/8** | +2 |
| `unknown_vs_quantified` | 8 | 6/8 | 6/8 | 0 |
| `infrequent_long_denominator_or_boundary` | 4 | 3/4 | 3/4 | 0 |

## Persistent misses (7)

| record_id | gold | v3 predicted | Mechanism |
| --- | --- | --- | --- |
| `gan_12562` | `1 per day` | `3 to 4 per week` | concurrent-type priority — candidate present, adjudication wrong |
| `gan_10434` | `multiple cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | cluster spacing collapse (v2 regression) |
| `gan_13290` | `4 per 6 month` | `2 per 6 month` | breakthrough count mismatch |
| `gan_14081` | `unknown` | `2 to 3 per month` | unknown phrasing |
| `gan_14092` | `unknown` | `5 per 2 month` | unknown phrasing |
| `gan_16947` | `2 per week` | `4 per 2 month` | concurrent absence selection |
| `gan_16964` | `2 per week` | `4 to 5 per 2 month` | concurrent absence selection |

## Outcomes

| arm | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| v3 S0 | **hold (directional confirm)** | arm | +13.4pp monthly vs v2 on hard queue; 4/5 builder-gap targets hit |

## Operational recommendation

- **Keep F0 skeleton** (`g2_candidates_adjudicate` + expanded builders) as monthly leader at full validation (68.1%).
- Builder-gap code is **confirmed helpful** on residual queue but does **not** warrant a standalone full-validation re-run without cap-50 spot-check — net +4 on n=30 with 1 regression.
- **Next builder work:** concurrent-type adjudication policy (`gan_12562`, `gan_16947`/`gan_16964`), unknown phrasing (`gan_14081`/`gan_14092`), breakthrough count (`gan_13290`).

## Mechanism review

Not applicable for mechanism closure.

Directional evidence: long-window cluster and daily-frequency candidates **transfer to monthly gains** when the LLM selects them; candidate presence alone is insufficient for concurrent-type priority (`gan_12562`). Det-candidate generation mechanism class remains **open**.

## Open cells

- Full-validation re-run with builder gaps (optional; F0 already at 68.1%)
- Adjudication prompt / policy for highest-frequency concurrent type
- Qwen port of F0 skeleton

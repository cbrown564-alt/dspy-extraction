# Gan S0 Residual Candidate Builder Expansion

Date: 2026-05-21  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (item 12)  
Residual queue: `data/fixtures/gan_s0_exact_frequency_residual_slice.json`

## Summary

Expanded deterministic temporal-candidate builders in `src/clinical_extraction/gan/temporal_candidates.py` to target arithmetic/window, unknown-vs-quantified, cluster-composition, and long-denominator failure modes identified in `docs/experiments/gan/gan_s0_exact_frequency_residual_manual_read_20260521.md`.

Slot-payload enrichment (`src/clinical_extraction/gan/slot_payload.py`) is unchanged; new candidates flow through existing slot derivation.

## Coverage audit (30-record residual queue)

Command:

```bash
uv run python scripts/audit_gan_residual_candidate_coverage.py
```

Artifact: `artifacts/gan_residual_candidate_coverage/summary.json`

| Metric | Before expansion | After expansion | After builder gaps (2026-05-21) |
| --- | ---: | ---: | ---: |
| Gold label in deterministic candidates | 1/30 (`gan_15306`) | **19/30 (63%)** | **24/30 (80%)** |

### Covered groups (examples)

| Residual group | Records in queue | Gold-in-candidate after expansion |
| --- | ---: | ---: |
| Arithmetic/window precision | 10 | 5 (`gan_15923`, `gan_16251`, `gan_16753`, `gan_14250`, `gan_14271`) |
| Unknown-vs-quantified | 8 | 4 (`gan_13993`, `gan_14025`, `gan_14036`, `gan_14137`) + `gan_10618` cluster-unknown |
| Cluster composition | 8 | 6 |
| Infrequent long-denominator | 4 | 2 (`gan_14354`, `gan_15302`; `gan_15306` already covered) |

### Remaining misses (6)

| Mechanism | Records | Notes |
| --- | --- | --- |
| Unknown (unmatched phrasing) | `gan_10751`, `gan_14081`, `gan_14092` | Need additional anchor patterns |
| Gold label mismatch on breakthrough | `gan_13290` | Builder emits `2 per 6 month`; gold is `4 per 6 month` |
| Concurrent-type frequency | `gan_16947`, `gan_16964` | Absence vs tonic-clonic target selection |

**Closed in builder-gap pass (2026-05-21):**

| Mechanism | Records | Builder |
| --- | --- | --- |
| Highest-frequency seizure-type selection | `gan_12562`, `gan_12667`, `gan_12679` | `_daily_seizure_type_frequency` → `1 per day` |
| Long-window cluster labels | `gan_15240`, `gan_15255` | `_last_convulsive_with_occasional_clusters` → `multiple cluster per N month, multiple per cluster` |

## New builder surfaces

| Builder | Target strata | Example label |
| --- | --- | --- |
| `_in_month_named_event_tallies` | Calendar aggregation | `8 per 2 month` |
| `_reverse_chronological_month_convulsion_counts` | Calendar aggregation | `14 per 4 month` |
| `_diary_named_month_event_tallies` | Calendar aggregation | `19 per 6 month` |
| `_following_week_events_monthly_rate` | Window precision | `2 per month` |
| `_unanchored_count_with_latest_date_unknown` | Unknown policy | `unknown` |
| `_morning_cluster_shorthand` | Cluster composition | `2 cluster per month, 2 to 4 per cluster` |
| `_month_beginning_cluster_bursts` | Cluster composition | `1 cluster per month, multiple per cluster` |
| `_some_weeks_morning_grouped_spells` | Cluster composition | `1 cluster per week, multiple per cluster` |
| `_several_mornings_intra_morning_repeats` | Cluster composition | `multiple cluster per week, 2 to 3 per cluster` |
| `_seizure_free_then_single_day_cluster` | Cluster spacing | `1 cluster per 4 month, 3 to 4 per cluster` |
| `_breakthrough_after_months_seizure_free` | Long denominator | `2 per 6 month` |
| `_withdrawal_moment_seizure_count` | Long denominator | `2 to 4 per 3 month` |
| `_vague_grouped_spells_unknown` | Unknown + cluster | `unknown, 4 to 6 per cluster` |
| `_last_convulsive_with_occasional_clusters` | Long-window cluster | `multiple cluster per 12 month, multiple per cluster` |
| `_daily_seizure_type_frequency` | Concurrent-type priority | `1 per day` |

Extended `_count_range_since_prior_month_year` for `since M - YYYY` anchors (`gan_15302`).

## Residual-slice replay v2 (completed)

Runs: `gan_s0_slot_s0_residual_slice_gpt4_1_mini_20260521T071756Z`, `gan_s0_slot_s1_residual_slice_gpt4_1_mini_20260521T071836Z`  
Inspection: `docs/experiments/gan/gan_s0_exact_frequency_slot_payload_residual_slice_replay_v2_20260521.md`

| Metric | v1 replay | v2 replay |
| --- | ---: | ---: |
| S0 monthly (30-record queue) | 13.3% | **63.3%** |
| S1 monthly | 13.3% | 60.0% |
| S1 − S0 | 0 | −3.3pp |

Builders explain ~50pp monthly lift on the hard queue. Slot-payload S1 does **not** beat prose S0 on residual.

**Cap-50 confirm (2026-05-21):** `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md` — prose + expanded builders **68.0%** monthly on 50 validation records vs pre-expansion **62.0%** (+6pp); 3 recoveries (`gan_10993`, `gan_15923`, `gan_16251`), 0 regressions.

## Next steps

1. Use prose + expanded builders as default Gan S0 det-candidate surface for new runs.
2. Remaining builder gaps: unmatched unknown phrasing (`gan_14081`/`gan_14092`), breakthrough count mismatch (`gan_13290`), concurrent absence selection (`gan_16947`/`gan_16964`).
3. Residual-slice replay v3 confirms +13.4pp monthly on hard queue (23/30); optional full-validation re-run deferred — see `docs/experiments/gan/gan_s0_expanded_builders_residual_slice_replay_v3_20260521.md`.

## decision_scope

`operational` for builder code; cap-50 outcome is **confirm (arm)** per inspection above.

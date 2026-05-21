# Gan S0 Exact-Frequency Slot Payload GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/gan_s0_exact_frequency_slot_payload_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_exact_frequency_slot_payload_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation variant (structured candidate slot payload) |
| Comparison group | `gan_s0_exact_frequency_slot_payload_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` cap-25, scorer `gan_frequency_deterministic_v1`, program `gan_frequency_s0_temporal_candidates_single_pass`, deterministic temporal candidates (unchanged builders), no verify-repair.

## Arms (cap-25)

| arm_id | implementation_variant | run_id | monthly | purist | pragmatic | norm exact | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S0 | `cand_prose_v1` | `gan_s0_slot_s0_prose_control_cap25_gpt4_1_mini_20260521T070800Z` | 52.0% | 60.0% | 76.0% | 40.0% | 100% | 100% | 25 |
| S1 | `slot_payload_v1` | `gan_s0_slot_s1_payload_cap25_gpt4_1_mini_20260521T070809Z` | **60.0%** | 68.0% | 80.0% | **48.0%** | 100% | 100% | 25 |

Delta S1 − S0: **+8.0pp monthly**, **+8.0pp normalized exact**, +8.0pp Purist, +4.0pp Pragmatic.

S0 reproduces E1/I0 at 52% monthly on the same 25 records.

## Prediction overlap (cap-25)

Identical normalized labels: **19/25**.

Notable S1 monthly recoveries vs S0:

- `gan_1794`: `2 per month` → `8 per 2 month` (calendar/window aggregation)
- `gan_14881`: `unknown` → `1 per month` (long-window residual count)
- `gan_16825`: `unknown` → `10 per 6 month` (long-window residual count)

Notable S1 regression vs S0:

- `gan_4113`: `1 per 1 to 2 day` → `unknown` (not on cap-25 monthly-miss list for S0; S0 had correct label)

Mixed signal on unknown gold:

- `gan_9566`: both arms invent `1 to 2 per 8 week` vs gold `unknown` (unchanged miss)

## Gates (prereg cap-25)

| Check | S1 vs S0 | Gate | Outcome |
| --- | --- | --- | --- |
| Monthly (primary) | +8.0pp (60% vs 52%) | ≥ +3.0pp | **pass** |
| Normalized exact | +8.0pp (48% vs 40%) | diagnostic | improved |
| Pragmatic overcall | 1 record (`gan_4702`: unknown → no-reference) | ≤ 1 | **pass** (at limit) |
| Schema | 100% | ≥ 95% | pass |
| Evidence | 100% headline | ≥ 96% | pass (1 missing-evidence row on `gan_4702` in error_analysis; quote support rate still 100%) |

**Outcome: hold (arm) on cap-25.** S1 clears the preregistered monthly promotion threshold. Residual-slice replay required before full-validation promotion.

## Residual-slice replay (30-record queue)

Runs:

| arm | run_id | monthly | norm exact |
| --- | --- | ---: | ---: |
| S0 | `gan_s0_slot_s0_residual_slice_gpt4_1_mini_20260521T070908Z` | 13.3% (4/30) | 10.0% (3/30) |
| S1 | `gan_s0_slot_s1_residual_slice_gpt4_1_mini_20260521T070912Z` | 13.3% (4/30) | 10.0% (3/30) |

Replay artifact: `artifacts/gan_slot_payload_residual_replay_20260521/summary.json`

| Group | records | monthly recovery | monthly regression |
| --- | ---: | ---: | ---: |
| `arithmetic_window_precision` | 10 | 0 | 0 |
| `unknown_vs_quantified` | 8 | 0 | 1 (`gan_13993`: S0 `unknown` → S1 `2 to 3 per month`) |
| `cluster_composition` | 8 | 1 (`gan_10993`: cluster spacing fix) | 0 |
| `infrequent_long_denominator_or_boundary` | 4 | 0 | 0 |

Headline: 1 monthly recovery, 1 monthly regression — **null on hard queue**. Wins are not concentrated in arithmetic/window or unknown-vs-quantified target groups.

**Residual gate: not met.** Do not promote to full validation from residual evidence alone.

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| S0 | hold | arm | Reproduces E1 control at 52% monthly |
| S1 | hold | arm | +8pp monthly and normalized exact on cap-25; residual replay null |

## Mechanism review

Not applicable — single slot-presentation variant plus prompt addendum; mechanism classes (seizure-type selection, calendar aggregation, unknown denominator, cluster slots) stay **open**.

Directional cap-25 signal suggests structured slot exposure helps adjudication on the Lane-A slice, but one implementation on one cap is insufficient for mechanism closure.

## Open cells

- Expanded deterministic candidate builders (regex coverage still sparse on full validation)
- Verify-repair skeleton (`g3_candidates_extract_repair`) not tested with slot payload
- Cap-50 / full validation deferred (residual gate not met)
- Qwen port deferred
- Interaction with table presentation (`cand_table_v1`) not tested

## Residual-slice replay v2 (expanded builders)

See `docs/gan_s0_exact_frequency_slot_payload_residual_slice_replay_v2_20260521.md`.

| Replay | S0 monthly | S1 monthly |
| --- | ---: | ---: |
| v1 (sparse builders) | 13.3% | 13.3% |
| v2 (expanded builders) | **63.3%** | 60.0% |

Builder expansion drives most hard-queue lift; S1 does not beat S0 on the 30-record queue (−3.3pp monthly). Residual promotion gate for slot_payload remains **not met**.

## Next steps

1. Default adjudication presentation to prose/table with expanded builders; do not promote slot_payload_v1 from residual v2.
2. Optional cap-50 on prose + expanded builders only if new prereg is written.
3. Registry backfill for cap-25 rows when inspection is accepted.

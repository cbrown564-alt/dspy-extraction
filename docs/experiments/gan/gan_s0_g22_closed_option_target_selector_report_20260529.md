# Gan S0 G22 Closed-Option Target Selector

Generated: `2026-05-29T10:57:58.154986+00:00`

## Scope

- Status: `completed_standard50_mechanism_slice`
- Decision scope: `arm`
- Dataset/split: `gan_2026` / `gan_2026_fixed_v1:validation`
- Surface: `gan_s0_g6_standard50_v1`
- Model/provider: GPT-4.1-mini / OpenAI
- Program variant: `gan_frequency_s0_closed_option_target_selector`
- Prompt version: `gan_frequency_s0_closed_option_target_selector_v1_2`
- Primary scorer: `gan2026_paper_reproduction`; canonical `gan_frequency_deterministic_v1` is diagnostic.
- Claim scope: closed-option target selection only; G19/G17/G21 are reporting overlays.

## Decision

- Recommendation: `do_not_full_validate_g22`
- Stop rule: `failed`
- Rationale: G22 paper-monthly count is 39 versus best baseline 41; two-record lift gate failed. Motivating overlay regressions remain: seizure_free_vs_quantified, unknown_no_reference. G17 builder-gap regressions remain: `gan_9566`, `gan_5974`, `gan_6607`, `gan_14002`, `gan_11380`.

## Arm Summary

| Arm | Run ID | Paper monthly | Canonical monthly | Canonical pragmatic |
| --- | --- | ---: | ---: | ---: |
| `builder_gap_gpt` | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | 82.0% | 84.0% | 96.0% |
| `d1_v1_2b_schema_guard` | `gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z` | 80.0% | 84.0% | 88.0% |
| `g8_special_class_selector` | `gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z` | 74.0% | 72.0% | 82.0% |
| `g10_candidate_ranking_selector` | `gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50_20260529T005458Z` | 72.0% | 70.0% | 82.0% |
| `g15_support_aware_selector` | `gan_s0_g15_support_aware_target_selector_gpt4_1_mini_standard50_20260529T013751Z` | 62.0% | 60.0% | 70.0% |
| `g22_closed_option_target_selector` | `gan_s0_g22_closed_option_target_selector_gpt4_1_mini_standard50_20260529T105421Z` | 78.0% | 78.0% | 88.0% |

## G22 Trace Diagnostics

- Closed answer options present: 50/50
- Selected closed option present: 50/50
- Constructed-option rows: 6/50
- Final label copied from selected option: 50/50
- Selected option sources: `deterministic_aggregation_constructor`=2, `deterministic_temporal_candidate`=48
- Selected option families: `cluster_rate`=3, `cluster_spacing_unknown`=2, `no_reference`=3, `quantified_rate`=31, `seizure_free`=10, `unclear_frequency`=1

## Challenge Overlays

| Overlay | `builder_gap_gpt` paper monthly | `d1_v1_2b_schema_guard` paper monthly | `g8_special_class_selector` paper monthly | `g10_candidate_ranking_selector` paper monthly | `g15_support_aware_selector` paper monthly | `g22_closed_option_target_selector` paper monthly |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `target_selection` | 34/43 (79.1%) | 34/43 (79.1%) | 30/43 (69.8%) | 31/43 (72.1%) | 26/43 (60.5%) | 34/43 (79.1%) |
| `seizure_free_vs_quantified` | 18/21 (85.7%) | 17/21 (81.0%) | 13/21 (61.9%) | 14/21 (66.7%) | 12/21 (57.1%) | 17/21 (81.0%) |
| `unknown_no_reference` | 10/10 (100.0%) | 9/10 (90.0%) | 6/10 (60.0%) | 4/10 (40.0%) | 5/10 (50.0%) | 5/10 (50.0%) |
| `candidate_coverage` | 2/4 (50.0%) | 2/4 (50.0%) | 0/4 (0.0%) | 0/4 (0.0%) | 0/4 (0.0%) | 2/4 (50.0%) |
| `cluster` | 21/24 (87.5%) | 19/24 (79.2%) | 19/24 (79.2%) | 18/24 (75.0%) | 15/24 (62.5%) | 18/24 (75.0%) |
| `temporal_anchoring` | 11/15 (73.3%) | 12/15 (80.0%) | 11/15 (73.3%) | 11/15 (73.3%) | 9/15 (60.0%) | 12/15 (80.0%) |
| `vague_frequency` | 9/10 (90.0%) | 8/10 (80.0%) | 10/10 (100.0%) | 9/10 (90.0%) | 8/10 (80.0%) | 8/10 (80.0%) |

## Before/After Ledger

| Record | Gold | G19 classes | G17 bucket | G21 constructed exact | Selected option | Before paper monthly | G22 paper monthly | Tags |
| --- | --- | --- | --- | ---: | --- | --- | ---: | --- |
| `gan_14485` | `2 per 3 month` | `target_selection__seizure_free_over_quantified` | `` | no | `raw_1` `2 per 3 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | yes | `g22_corrects_baseline_miss` |
| `gan_6532` | `unknown, multiple per cluster` | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | `unknown_cluster_misrouted_as_concrete` | no | `raw_2` `unknown, multiple per cluster` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_10434` | `multiple cluster per week, 2 to 3 per cluster` | `none` | `` | no | `raw_1` `multiple cluster per week, 2 to 3 per cluster` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_4956` | `seizure free for 7 month` | `none` | `` | no | `raw_1` `seizure free for 7 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_13123` | `1 per year` | `target_selection__seizure_free_over_quantified` | `` | no | `raw_1` `1 per year` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=no | yes | `g22_corrects_baseline_miss` |
| `gan_4702` | `multiple per day` | `target_selection__quantified_vs_abstention` | `` | no | `raw_2` `multiple per day` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_10052` | `4 cluster per 3 month, multiple per cluster` | `none` | `` | no | `raw_1` `4 cluster per 3 month, multiple per cluster` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_2609` | `1 per day` | `none` | `` | no | `raw_5` `1 per day` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_1794` | `8 per 2 month` | `target_selection__wrong_quantified_rate_or_window` | `` | no | `raw_1` `8 per 2 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_15306` | `2 to 3 per 15 month` | `target_selection__seizure_free_over_quantified` | `` | no | `raw_1` `2 to 3 per 15 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | yes | `g22_corrects_baseline_miss` |
| `gan_7894` | `seizure free for multiple year` | `scorer_mode_discordance__canonical_only_correct` | `seizure_free_no_reference_scorer_discordance` | no | `raw_3` `seizure free for multiple year` `deterministic_temporal_candidate` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_3246` | `2 cluster per month, 4 per cluster` | `cluster_policy_or_cluster_target_selection` | `` | no | `raw_2` `4 per month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_4113` | `1 per 1 to 2 day` | `target_selection__quantified_vs_abstention`, `target_selection__seizure_free_over_quantified`, `target_selection__wrong_quantified_rate_or_window` | `` | no | `raw_2` `1 per 1 to 2 day` `deterministic_temporal_candidate` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=no | yes | `g22_corrects_baseline_miss` |
| `gan_14881` | `1 per month` | `target_selection__seizure_free_over_quantified` | `` | no | `raw_1` `1 per month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=no | yes | `g22_corrects_baseline_miss` |
| `gan_536` | `1 per 2 day` | `none` | `` | no | `raw_1` `1 per 2 day` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_4709` | `multiple per day` | `target_selection__quantified_vs_abstention` | `` | no | `raw_2` `multiple per day` `deterministic_temporal_candidate` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_9566` | `unknown` | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | `unknown_misrouted_as_concrete` | no | `raw_2` `1 to 2 per 8 week` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_12679` | `1 per day` | `target_selection__wrong_quantified_rate_or_window` | `` | no | `raw_5` `1 to 2 per month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_1584` | `11 per month` | `none` | `` | no | `raw_2` `11 per month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_15997` | `10 per 3 month` | `aggregation_block__temporal_slot_missing` | `` | yes | `constructed_1` `10 per 3 month` `deterministic_aggregation_constructor` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | yes | `g22_corrects_baseline_miss` |
| `gan_17287` | `1 per 1 to 2 day` | `target_selection__wrong_quantified_rate_or_window` | `` | no | `raw_1` `1 per 1 to 2 day` `deterministic_temporal_candidate` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_16251` | `14 per 4 month` | `none` | `` | no | `raw_1` `14 per 4 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_16772` | `9 per 5 month` | `aggregation_block__temporal_slot_missing` | `` | yes | `raw_3` `11 per 3 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `unchanged_vs_available_baselines` |
| `gan_16825` | `10 per 6 month` | `aggregation_block__temporal_slot_missing` | `` | yes | `raw_2` `12 per 3 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_12950` | `7 per 3 month` | `none` | `` | no | `raw_3` `7 per 3 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_10047` | `2 cluster per 3 month, multiple per cluster` | `none` | `` | no | `raw_1` `2 cluster per 3 month, multiple per cluster` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_12810` | `5 per 2 month` | `none` | `` | no | `raw_1` `5 per 2 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_10398` | `1 cluster per week, 2 per cluster` | `cluster_policy_or_cluster_target_selection` | `` | no | `raw_7` `unknown, 2 per cluster` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_16041` | `9 per 3 month` | `target_selection__wrong_quantified_rate_or_window` | `` | no | `raw_3` `9 per 2 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `unchanged_vs_available_baselines` |
| `gan_714` | `2 per day` | `none` | `` | no | `raw_1` `2 per day` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_12465` | `1 per day` | `target_selection__quantified_vs_abstention` | `` | no | `raw_2` `1 per day` `deterministic_temporal_candidate` | `builder_gap_gpt`=no, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_4011` | `1 per month` | `none` | `` | no | `raw_3` `1 per month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_804` | `1 per month` | `cluster_policy_or_cluster_target_selection` | `` | no | `raw_2` `1 per month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_22` | `3 per day` | `target_selection__seizure_free_over_quantified` | `` | no | `raw_2` `3 per day` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=no | yes | `g22_corrects_baseline_miss` |
| `gan_16335` | `7 per 3 month` | `aggregation_block__temporal_slot_missing` | `` | yes | `constructed_1` `7 per 3 month` `deterministic_aggregation_constructor` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | yes | `g22_corrects_baseline_miss` |
| `gan_3867` | `3 per day` | `none` | `` | no | `raw_1` `3 per day` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_13574` | `seizure free for multiple year` | `none` | `` | no | `raw_1` `seizure free for multiple year` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_5974` | `unknown` | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | `unknown_misrouted_as_seizure_free` | no | `raw_1` `seizure free for 1 year` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_6607` | `unknown` | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | `unknown_misrouted_as_concrete` | no | `raw_1` `2 to 3 per month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_8564` | `seizure free for 6 month` | `none` | `` | no | `raw_1` `seizure free for 6 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_6387` | `unknown` | `unknown_no_reference_policy__over_concrete` | `unknown_overcalled_as_concrete` | no | `raw_2` `unknown` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_8264` | `seizure free for 4 month` | `scorer_mode_discordance__canonical_only_correct` | `seizure_free_no_reference_scorer_discordance` | no | `raw_3` `seizure free for 4 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=no, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `g22_corrects_baseline_miss` |
| `gan_14002` | `unknown` | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | `unknown_misrouted_as_seizure_free` | no | `raw_1` `seizure free for multiple month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_11380` | `unknown` | `frequency_content_gate__unclear_or_cluster_misrouted_as_concrete` | `unknown_misrouted_as_concrete` | no | `raw_3` `2 per 3 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=no, `g10_candidate_ranking_selector`=no, `g15_support_aware_selector`=no | no | `g22_regresses_from_baseline_correct` |
| `gan_11408` | `no seizure frequency reference` | `none` | `` | no | `raw_1` `no seizure frequency reference` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_11841` | `no seizure frequency reference` | `none` | `` | no | `raw_1` `no seizure frequency reference` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_7818` | `seizure free for 2 year` | `none` | `` | no | `raw_1` `seizure free for 26 month` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_13598` | `seizure free for multiple year` | `none` | `` | no | `raw_1` `seizure free for multiple year` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_13595` | `seizure free for multiple year` | `none` | `` | no | `raw_1` `seizure free for multiple year` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |
| `gan_11874` | `no seizure frequency reference` | `none` | `` | no | `raw_1` `no seizure frequency reference` `deterministic_temporal_candidate` | `builder_gap_gpt`=yes, `d1_v1_2b_schema_guard`=yes, `g8_special_class_selector`=yes, `g10_candidate_ranking_selector`=yes, `g15_support_aware_selector`=yes | yes | `unchanged_vs_available_baselines` |

## Interpretation

- G22 is evaluated as a new target-selection mechanism, not as a rerun of G8, G10, or G15 prompt shapes.
- The model-facing surface contains closed option IDs only; final labels are copied from the selected option.
- Row-specific G19 failure classes, G17 special-label buckets, and G21 constructed-option exactness are joined only after prediction for the before/after ledger.

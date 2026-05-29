# Gan S0 G15 Support-Aware Target Selector

Generated: `2026-05-29T01:42:12.105433+00:00`

## Scope

- Status: `completed_standard50_mechanism_slice`
- Decision scope: `arm`
- Dataset/split: `gan_2026` / `gan_2026_fixed_v1:validation`
- Surface: `gan_s0_g6_standard50_v1` (50 records)
- Model/provider: GPT-4.1-mini / OpenAI
- Program variant: `gan_frequency_s0_support_aware_target_selector`
- Prompt version: `gan_frequency_s0_support_aware_target_selector_v1_0`
- Primary scorer: `gan2026_paper_reproduction`; canonical `gan_frequency_deterministic_v1` is diagnostic.
- Claim scope: target-selection/semantic adjudication only; no exact aggregation-constructor claim.

## Decision

- Recommendation: `do_not_full_validate_or_promote_as_tested`
- Stop rule: `failed`
- Rationale: G15 reached 31/50 paper monthly versus best baseline builder_gap_gpt at 41/50. The G6 stop rule requires at least a two-record lift and no motivating-overlay regression; regressions: target_selection, seizure_free_vs_quantified, unknown_no_reference.

## Arm Summary

| Arm | Run ID | Paper monthly | Paper purist | Paper pragmatic | Canonical monthly | Canonical pragmatic |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `builder_gap_gpt` | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | 82.0% | 88.0% | 94.0% | 84.0% | 96.0% |
| `d1_v1_2b_schema_guard` | `gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z` | 80.0% | 82.0% | 84.0% | 84.0% | 88.0% |
| `g8_special_class_selector` | `gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z` | 74.0% | 78.0% | 84.0% | 72.0% | 82.0% |
| `g10_candidate_ranking_selector` | `gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50_20260529T005458Z` | 72.0% | 74.0% | 84.0% | 70.0% | 82.0% |
| `g15_support_aware_selector` | `gan_s0_g15_support_aware_target_selector_gpt4_1_mini_standard50_20260529T013751Z` | 62.0% | 64.0% | 72.0% | 60.0% | 70.0% |

## G15 Trace Diagnostics

- Support context present: 50/50
- Selected candidate references present: 49/50
- Label-construction inputs present: 49/50

| Target semantic class | Count |
| --- | ---: |
| `cluster_spacing_unknown` | 6 |
| `current_quantified_frequency` | 23 |
| `no_seizure_frequency_reference` | 3 |
| `seizure_free_duration` | 15 |
| `unclear_frequency` | 1 |
| `unknown` | 1 |
| `unknown_frequency` | 1 |

| Support policy decision | Count |
| --- | ---: |
| `cluster_burden_without_spacing` | 6 |
| `direct_candidate` | 20 |
| `no_reference_only` | 3 |
| `quantified_count_window_supported` | 2 |
| `seizure_free_current_state` | 15 |
| `trigger_conditioned_unknown` | 4 |

## Challenge Overlays

| Overlay | G15 paper monthly | Builder-gap GPT | D1 v1.2b | G8 | G10 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `target_selection` | 26/43 (60.5%) | 34/43 (79.1%) | 34/43 (79.1%) | 30/43 (69.8%) | 31/43 (72.1%) |
| `seizure_free_vs_quantified` | 12/21 (57.1%) | 18/21 (85.7%) | 17/21 (81.0%) | 13/21 (61.9%) | 14/21 (66.7%) |
| `unknown_no_reference` | 5/10 (50.0%) | 10/10 (100.0%) | 9/10 (90.0%) | 6/10 (60.0%) | 4/10 (40.0%) |
| `candidate_coverage` | 0/4 (0.0%) | 2/4 (50.0%) | 2/4 (50.0%) | 0/4 (0.0%) | 0/4 (0.0%) |
| `cluster` | 15/24 (62.5%) | 21/24 (87.5%) | 19/24 (79.2%) | 19/24 (79.2%) | 18/24 (75.0%) |
| `temporal_anchoring` | 9/15 (60.0%) | 11/15 (73.3%) | 12/15 (80.0%) | 11/15 (73.3%) | 11/15 (73.3%) |
| `vague_frequency` | 8/10 (80.0%) | 9/10 (90.0%) | 8/10 (80.0%) | 10/10 (100.0%) | 9/10 (90.0%) |

## Pairwise Paper-Monthly Deltas

| Baseline | G15 correct / baseline wrong | G15 wrong / baseline correct |
| --- | --- | --- |
| `builder_gap_gpt` | `gan_1794`, `gan_7894`, `gan_4709`, `gan_17287`, `gan_12465` | `gan_14485`, `gan_13123`, `gan_15306`, `gan_3246`, `gan_14881`, `gan_9566`, `gan_12679`, `gan_16825`, `gan_10398`, `gan_22`, `gan_16335`, `gan_5974`, `gan_6607`, `gan_14002`, `gan_11380` |
| `d1_v1_2b_schema_guard` | `gan_4702`, `gan_7894`, `gan_4709`, `gan_804`, `gan_6387`, `gan_8264` | `gan_14485`, `gan_13123`, `gan_15306`, `gan_3246`, `gan_14881`, `gan_9566`, `gan_12679`, `gan_16825`, `gan_10398`, `gan_22`, `gan_16335`, `gan_5974`, `gan_6607`, `gan_14002`, `gan_11380` |
| `g8_special_class_selector` | `gan_6532` | `gan_13123`, `gan_3246`, `gan_4113`, `gan_10398`, `gan_22`, `gan_6607`, `gan_14002` |
| `g10_candidate_ranking_selector` | `gan_6532` | `gan_13123`, `gan_3246`, `gan_4113`, `gan_14881`, `gan_10398`, `gan_22` |

## Upstream Caveats

- G13 gate-caveated standard50 rows: `gan_6532`, `gan_9566`, `gan_13574`, `gan_5974`, `gan_6607`, `gan_8564`, `gan_14002`, `gan_11380`, `gan_7818`, `gan_13598`, `gan_13595`, `gan_11874`.
- G14 temporal-slot misses on standard50: `gan_15997`, `gan_16772`, `gan_16825`, `gan_16335`.

## Interpretation

- G15 tests whether explicit support metadata improves target semantics over the fixed candidate surface.
- The run preserves scorer, loader, split, benchmark bridge, candidate-builder, label-construction, and prediction-repair semantics.
- G13 gate confusions and G14 temporal-slot misses are carried as upstream caveats rather than pure selector failures.

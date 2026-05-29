# Gan S0 G10 Candidate-Ranking Target Selector

Generated: `2026-05-29T00:59:28.295044+00:00`

## Scope

- Status: `rejected_arm`
- Decision scope: `arm`
- Dataset/split: `gan_2026` / `gan_2026_fixed_v1:validation`
- Surface: `gan_s0_g6_standard50_v1` (50 records)
- Model/provider: GPT-4.1-mini / OpenAI
- Program variant: `gan_frequency_s0_candidate_ranking_target_selector`
- Prompt version: `gan_frequency_s0_candidate_ranking_target_selector_v1_0`
- Primary scorer: `gan2026_paper_reproduction`; canonical `gan_frequency_deterministic_v1` is diagnostic.
- Claim scope: category-level/candidate-ranking only; no exact closed answer-option construction claim.

## Decision

- Recommendation: `do_not_full_validate_or_promote_as_tested`
- Stop rule: `failed`
- Rationale: G10 paper monthly was 72.00% (36/50), below builder-gap GPT 82.00% (41/50), D1 v1.2b 80.00% (40/50), and G8 74.00% (37/50). It therefore fails the G6/G10 gate requiring at least a two-record monthly lift, no paper-metric regression, and no targeted-overlay regression.

## Arm Summary

| Arm | Run ID | Paper monthly | Paper purist | Paper pragmatic | Canonical monthly | Canonical pragmatic |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `builder_gap_gpt` | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | 82.0% | 88.0% | 94.0% | 84.0% | 96.0% |
| `d1_v1_2b_schema_guard` | `gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z` | 80.0% | 82.0% | 84.0% | 84.0% | 88.0% |
| `g8_special_class_selector` | `gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z` | 74.0% | 78.0% | 84.0% | 72.0% | 82.0% |
| `g10_candidate_ranking_selector` | `gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50_20260529T005458Z` | 72.0% | 74.0% | 84.0% | 70.0% | 82.0% |

## G10 Trace Diagnostics

- `category_decision` present: 50/50
- `candidate_ranking` present: 50/50
- `selected_candidate_reference` present: 49/50
- `label_construction_inputs` present: 49/50
- `reason_code_adjudication` present: 50/50

| Category decision | Count |
| --- | ---: |
| `cluster` | 4 |
| `no_reference` | 4 |
| `quantified_rate` | 29 |
| `seizure_free` | 11 |
| `unknown` | 1 |
| `unknown_frequency` | 1 |

## Challenge Overlays

| Overlay | G10 paper monthly | Builder-gap GPT | D1 v1.2b | G8 |
| --- | ---: | ---: | ---: | ---: |
| `target_selection` | 31/43 (72.1%) | 34/43 (79.1%) | 34/43 (79.1%) | 30/43 (69.8%) |
| `seizure_free_vs_quantified` | 14/21 (66.7%) | 18/21 (85.7%) | 17/21 (81.0%) | 13/21 (61.9%) |
| `unknown_no_reference` | 4/10 (40.0%) | 10/10 (100.0%) | 9/10 (90.0%) | 6/10 (60.0%) |
| `candidate_coverage` | 0/4 (0.0%) | 2/4 (50.0%) | 2/4 (50.0%) | 0/4 (0.0%) |
| `cluster` | 18/24 (75.0%) | 21/24 (87.5%) | 19/24 (79.2%) | 19/24 (79.2%) |
| `temporal_anchoring` | 11/15 (73.3%) | 11/15 (73.3%) | 12/15 (80.0%) | 11/15 (73.3%) |
| `vague_frequency` | 9/10 (90.0%) | 8/10 (80.0%) | 7/10 (70.0%) | 9/10 (90.0%) |

## Pairwise Paper-Monthly Deltas

| Baseline | G10 correct / baseline wrong | G10 wrong / baseline correct |
| --- | --- | --- |
| `builder_gap_gpt` | `gan_1794`, `gan_7894`, `gan_4113`, `gan_4709`, `gan_17287`, `gan_12465` | `gan_14485`, `gan_6532`, `gan_15306`, `gan_9566`, `gan_12679`, `gan_16825`, `gan_16335`, `gan_5974`, `gan_6607`, `gan_14002`, `gan_11380` |
| `d1_v1_2b_schema_guard` | `gan_4702`, `gan_7894`, `gan_4113`, `gan_4709`, `gan_804`, `gan_6387`, `gan_8264` | `gan_14485`, `gan_6532`, `gan_15306`, `gan_9566`, `gan_12679`, `gan_16825`, `gan_16335`, `gan_5974`, `gan_6607`, `gan_14002`, `gan_11380` |
| `g8_special_class_selector` | `gan_14881` | `gan_6607`, `gan_14002` |

## Interpretation

- G10 preserved schema, evidence, and traceability, but the candidate-ranking prompt did not improve target selection on the standard50 mechanism surface.
- The result is an arm rejection, not a closure of all target-selection mechanisms.
- Full validation is not authorized by the G10 stop rule. Exact-label aggregation remains blocked on temporal anchoring plus aggregation policy or a separate deterministic aggregation constructor.

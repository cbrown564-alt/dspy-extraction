# ExECT S5 Frequency Verifier v2b Full-Validation Promotion Review

Date: 2026-05-24  
Decision scope: **operational** (paper D1 freeze promotion)  
Status: **Promoted**

## Promotion Decision

Promote the ExECT S5 stack **pre-vocab + AM guard + v2b frequency verifier** (v1.2 extractor + v2 temporal/scope verifier rules, no strict qualitative guard) to the paper-frozen operational default (D1), superseding the v1 verifier + A3 row.

| Field | Value |
| --- | --- |
| Promoted run ID | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini.json` |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` |
| Split | `exectv2_fixed_v1:validation` / 40 records |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |
| Superseded run | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z` |

## Gate Check

| Metric | Superseded (v1 + A3) | Promoted (v2b) | Delta | Gate |
| --- | ---: | ---: | ---: | --- |
| seizure_frequency F1 | 72.3% | **73.9%** | +1.6pp | Pass |
| seizure_frequency precision | 66.7% | **69.4%** | +2.7pp | Pass |
| seizure_frequency recall | 79.1% | **79.1%** | ~0 | Pass |
| annotated_medication F1 | 88.7% | **88.7%** | 0 | Pass |
| diagnosis F1 | 90.0% | **90.0%** | 0 | Pass |
| seizure_type F1 | 84.0% | **84.0%** | 0 | Pass |
| investigation F1 | 96.7% | **96.7%** | 0 | Pass |
| pooled micro F1 | 85.5% | **85.8%** | +0.3pp | Pass |

Combined v2 arm (v1.3 extractor + strict qualitative guard + v2 verifier) remains **rejected** at cap-25; factor isolation implicated abstention/guard stacking, not v2 temporal/scope rules alone.

## Rationale

1. v2b cap-25 cleared all gates (+4.7pp freq F1 vs v1 cap-25, recall +8.0pp).
2. Full validation confirms modest but scorer-safe frequency gain with flat recall and zero guard-family regression.
3. v1 A3 verifier rules are retained in v2b signature (rules 1–6); v2 adds rules 7–9 for temporal/current scope without v1.3 extractor abstention.

## Caveats Preserved

- Partial five-family S5 diagnostic surface; not CUI-aware ExECTv2 Table 1 reproduction.
- Medication temporality excluded from S5.
- Second LLM pass (reject-only frequency verifier) retained; inference cost unchanged vs v1 stack.
- Scorer semantics unchanged.
- Gain is incremental (+1.6pp freq F1), not a large step change like the original verifier promotion (+12.1pp).

## Artifacts Updated

- `docs/archive/experiments/synthesis/pre_component_pivot/paper_frozen_operational_defaults_20260524.md`
- `docs/archive/experiments/synthesis/pre_component_pivot/paper_frozen_results_narrative_20260524.md`
- `docs/archive/experiments/synthesis/pre_component_pivot/paper_frozen_arm_reject_table_20260524.md`
- `docs/planning/kanban_plan.md`

Primary metric source: `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z/metrics.json`

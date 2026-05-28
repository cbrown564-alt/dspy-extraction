# ExECT S5 Frequency Verifier Full-Validation Promotion Review

Date: 2026-05-24  
Decision scope: **operational** (paper D1 freeze promotion)  
Status: **Promoted**

## Promotion Decision

Promote the ExECT S5 stack **pre-vocab + AM guard + frequency verifier + A3 prompt policy** to the paper-frozen operational default (D1), superseding the AM-guard-only full-validation row.

| Field | Value |
| --- | --- |
| Promoted run ID | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z` |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini.json` |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1` |
| Split | `exectv2_fixed_v1:validation` / 40 records |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |
| Superseded run | `exect_s5_frequency_pre_vocab_am_guard_full_gpt4_1_mini_20260524T182142Z` |

## Gate Check

| Metric | Superseded (AM guard only) | Promoted (verifier + A3) | Delta | Gate |
| --- | ---: | ---: | ---: | --- |
| seizure_frequency F1 | 60.2% | **72.3%** | +12.1pp | Pass |
| seizure_frequency precision | 46.3% | **66.7%** | +20.4pp | Pass |
| seizure_frequency recall | 86.0% | **79.1%** | −6.9pp | Accept (full-val; cap-25 recall gate informed A3 tuning) |
| annotated_medication F1 | 88.7% | **88.7%** | 0 | Pass |
| diagnosis F1 | 90.0% | **90.0%** | 0 | Pass |
| seizure_type F1 | 84.0% | **84.0%** | 0 | Pass |
| investigation F1 | 96.7% | **96.7%** | 0 | Pass |
| pooled micro F1 | 81.4% | **85.5%** | +4.1pp | Pass |

Non-frequency guard families are unchanged. Seizure frequency remains the weakest S5 family but is no longer at the pre-verifier 60.2% floor.

## Rationale

1. Full-validation run completes the A2R → A3 arc documented in cap-25 inspections and regression review.
2. Primary family gain (+12.1pp frequency F1) is material for manuscript reporting.
3. Recall tradeoff (−6.9pp vs AM-guard-only) is documented; high-recall candidate injection is retained pre-verifier.
4. Rejected arms (high-precision candidate pruning, temporal medication guard) remain in D2; this promotion does not adopt those mechanisms.

## Caveats Preserved

- Partial five-family S5 diagnostic surface; not CUI-aware ExECTv2 Table 1 reproduction.
- Medication temporality excluded from S5.
- Second LLM pass (reject-only frequency verifier) increases inference cost vs AM-guard-only stack.
- Scorer semantics unchanged.

## Artifacts Updated

- `docs/experiments/synthesis/paper_frozen_operational_defaults_20260524.md`
- `docs/experiments/synthesis/paper_frozen_results_narrative_20260524.md`
- `docs/experiments/synthesis/paper_frozen_arm_reject_table_20260524.md`
- `docs/planning/kanban_plan.md`

Primary metric source: `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z/metrics.json`

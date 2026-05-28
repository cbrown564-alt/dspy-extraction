# ExECT S5 Frequency Verifier Cap-25 Inspection

Date: 2026-05-24
Decision scope: arm
Status: hold for A2R review before full validation

## Research Question

Can a reject-only, evidence-sensitive verifier over the existing high-recall ExECT S5 seizure-frequency candidate surface improve frequency precision and F1 without losing the recall that made the high-recall arm useful?

## Method

- Dataset: ExECTv2
- Split: `exectv2_fixed_v1:validation`, capped to 25 records
- Model/provider: `gpt-4.1-mini` via OpenAI
- Schema level: `exect_s5_core_field_family`
- Program variant: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1`
- Config: `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini.json`
- Run ID: `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T193119Z`
- Scorer mode: `exect_s5_core_field_family_deterministic_v1`
- Baseline comparison: `exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini_20260524T182134Z`

The implementation keeps the high-recall `exect.frequency.rate_candidates.v1` pre-vocabulary unchanged, runs the existing S5 extractor, applies a second LLM verifier only to initial `seizure_frequency` outputs, blocks verifier-added labels, requires evidence to be a note substring rather than an injected candidate echo, and then applies the existing annotated-medication guard unchanged.

## Results

| Metric | AM-guard cap-25 baseline | A2 verifier cap-25 | Delta |
| --- | ---: | ---: | ---: |
| seizure_frequency precision | 45.1% | 64.3% | +19.2pp |
| seizure_frequency recall | 92.0% | 72.0% | -20.0pp |
| seizure_frequency F1 | 60.5% | 67.9% | +7.4pp |
| diagnosis F1 | 93.0% | 93.0% | 0.0pp |
| seizure_type F1 | 92.5% | 92.5% | 0.0pp |
| annotated_medication F1 | 87.9% | 87.9% | 0.0pp |
| investigation F1 | 93.8% | 93.8% | 0.0pp |
| micro F1 | 83.1% | 86.6% | +3.5pp |

The arm clears the preregistered precision/F1 improvement signal and preserves guard-family F1 on cap-25, but it does not clear the recall gate: seizure_frequency recall drops from 92.0% to 72.0%, worse than the allowed 3.0pp degradation.

## Interpretation

The verifier is doing the intended precision work, especially by removing unsupported qualitative emissions, but it is too aggressive for the A2 gate as written. The result is useful as an implementation lead and mechanism signal, not ready for full-validation promotion. The next useful question is whether the recall loss is caused by deterministic evidence guards, the verifier prompt, or the no-add recovery filter that blocks post-recovery co-label augmentation.

## Caveats

- This is a cap-25 gate, not full validation or test reporting.
- S5 is a five-family diagnostic surface, not CUI-aware ExECTv2 Table 1 reproduction.
- The recall drop may reflect benchmark-policy tension around qualitative labels such as `frequency increased`, not only incorrect verifier behavior.
- Gold-empty and annotation-policy caveats from the ExECT audit still apply; this run does not reinterpret gold labels or scorer denominators.
- Evidence quote support is diagnostic and not part of benchmark-facing field-family F1.

## Taxonomy

- dataset: `exect_v2`
- schema_complexity: `exect_s5`
- clinical_task_family: `frequency`, `medication`
- program_architecture: `verify_repair`
- hybrid_balance_class: `H2_pre_deterministic`, `H1_post_deterministic`, `H4_deterministic_first_llm_adjudicates`
- interleaving_positions: `pre`, `during`, `post`
- varied_factor: `verification_strategy`
- comparison_group: `exect_s5_axis1_axis2_decomposition_gpt_cap25_v1`
- outcome: `hold`
- decision_scope: `arm`

## Next Steps

Run A2R as a regression/critic review before any full validation. Focus on examples where recall was lost relative to the AM-guard cap-25 baseline, especially EA0008, EA0050, EA0059, and EA0069, and decide whether to tune the verifier prompt, relax deterministic guards, or keep A2 as a rejected-as-gated precision-only arm.

# Gan S0 L2 Qwen Exact-Policy Slice — Pre-Registration

Date: 2026-05-25  
Status: **Pre-registration before Qwen slice run**  
Comparison group: `gan_s0_l2_qwen_exact_policy_v1`  
Parent forensics: `docs/experiments/gan/gan_s0_qwen35b_builder_gap_l2_error_forensics_20260525.md`  
Kanban: `docs/planning/kanban_plan.md`

## Research Question

Can a narrow Qwen-specific prompt-policy patch reduce the paired local-model gap on Gan S0 records where GPT-4.1-mini was monthly-correct but Qwen3.6:35b failed under the same `gan_s0_candidate_builder_gap_v1` surface?

This arm tests prompt policy only. It does not expand deterministic candidate builders, change scorer semantics, change gold labels, add few-shot examples, or add a verifier stage.

## Fixed Controls

| Control | Value |
| --- | --- |
| Dataset / split | Gan 2026 synthetic, `gan_2026_fixed_v1:validation` |
| Slice | `data/fixtures/gan_s0_l2_qwen_policy_slice.json` (18 records) |
| Model | Qwen3.6:35b via Ollama, `configs/models/gan_s0_qwen35b_ollama.json` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Candidate surface | `gan_s0_candidate_builder_gap_v1` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_7_qwen_exact_policy` |
| Scorer | `gan_frequency_deterministic_v1` |
| Repair policy | `artifact_bridge_surface_normalization_only` |
| ChainOfThought / optimizer | None |

## Slice Composition

The slice is sampled from the 55 GPT-correct/Qwen-failed paired validation records in L2. It emphasizes:

| Failure family | Records |
| --- | --- |
| Cluster collapsed to non-cluster rate | `gan_10052`, `gan_10993`, `gan_15442`, `gan_10031` |
| Cluster semantic mismatch | `gan_3246`, `gan_11207` |
| Exact count/window/range softened to coarse label | `gan_714`, `gan_2513`, `gan_15876`, `gan_12296` |
| Purist boundary or denominator drift | `gan_13123`, `gan_9365` |
| Unknown fallback despite quantifiable rate | `gan_22`, `gan_4597` |
| Unknown/seizure-free boundary | `gan_6131`, `gan_14036` |
| Invalid or non-canonical surface | `gan_338`, `gan_3225` |

## Decision Rule

Promote to a cap-25 validation gate only if all conditions hold on this slice:

- Monthly-frequency accuracy improves over the parent Qwen outputs on the same 18 records by at least 4 records.
- Schema validity is 100%.
- Evidence support is at least 85%.
- Cluster-family records improve by at least 2 records without creating new unknown/no-reference regressions.
- Invalid/non-canonical surfaces are eliminated.

Reject or redesign if monthly accuracy is flat/regresses, schema validity drops below 100%, or gains are limited to surface canonicalization without improving monthly-frequency correctness.

## Audit Guardrails

- Gan gold remains `seizure_frequency_number[0]`.
- `reference[0]` remains a secondary cross-check and difficulty signal, not gold.
- `unknown` and `no seizure frequency reference` remain distinct labels.
- Evidence support is diagnostic for this arm.
- Scorer semantics are unchanged.

## Validation Plan

1. Validate the config with `uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_l2_qwen_exact_policy_slice_qwen35b_ollama.json --env-file .env --dry-run`.
2. Run the 18-record Qwen slice only if no other local Ollama job is active.
3. Inspect `metadata.json`, `config.json`, `prompts.json`, `predictions.json`, `metrics.json`, and `errors.json`.
4. Compare against parent Qwen outputs for the same record IDs before deciding on any cap-25 follow-up.

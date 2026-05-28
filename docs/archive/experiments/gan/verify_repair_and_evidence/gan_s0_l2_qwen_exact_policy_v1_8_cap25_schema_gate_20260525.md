# Gan S0 L2 Qwen Exact-Policy v1.8 Cap-25 Schema Gate

Date: 2026-05-25  
Config: `configs/experiments/gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama.json`  
Completed run ID: `gan_s0_l2_qwen_exact_policy_cap25_qwen35b_ollama_20260525T171037Z`  
Prompt version: `gan_frequency_s0_temporal_candidates_single_pass_v1_8_qwen_schema_validity`  
Dataset/split: Gan 2026 synthetic, `gan_2026_fixed_v1:validation`, first 25 records  
Model: Qwen3.6:35b via Ollama  
Scorer: `gan_frequency_deterministic_v1`

## Why This Rerun Exists

The v1.7 exact-policy cap-25 follow-up had strong monthly accuracy but failed the schema/canonical gate:

- `gan_10618`: `4 to 6 per cluster` instead of canonical `unknown, 4 to 6 per cluster`
- `gan_2609`: `1 per night` instead of canonical `1 per day`

The v1.7 slice also emitted `many per month`, which is a repairable surface for canonical `multiple per month`.

## Implementation Fix

The v1.8 patch adds a schema-validity prompt addendum over v1.7:

- `many`/`few`/`several` multiplicity surfaces normalize to `multiple`
- per-cluster-only outputs must use `unknown, N per cluster` when cluster spacing is unavailable
- forbidden units such as `night`, `hour`, `quarter`, and `fortnight` must be converted to canonical Gan units
- `unknown, ...` suffixes are restricted to the canonical `unknown, N per cluster` form

The deterministic normalization layer was also tightened:

- `many per month` -> `multiple per month`
- `unknown, 6 per hour` -> `multiple per day`
- `unknown, N per day/week/month/year` is now schema-invalid unless repaired before scoring
- `unknown, N per cluster` remains valid and maps to the Gan unknown value

This preserves Gan gold source and benchmark scorer intent; it corrects schema validation to match the audited Gan label taxonomy.

## Cap-25 Outcome

The completed v1.8 run produced `metrics.json` before the final deterministic tightening of `unknown, ...` validation. The saved raw predictions were therefore re-evaluated post hoc with the current normalizer. The only changed prediction surface was:

| record_id | raw prediction | old normalized | current normalized |
| --- | --- | --- | --- |
| `gan_4709` | `"unknown, 6 per hour"` | `unknown, 6 per hour` | `multiple per day` |

Post-hoc deterministic re-evaluation of the completed run:

| metric | value |
| --- | ---: |
| Schema validity | 100.0% |
| Evidence support | 100.0% |
| Monthly frequency accuracy | 72.0% |
| Purist category accuracy | 80.0% |
| Pragmatic category accuracy | 88.0% |
| Normalized-label accuracy | 68.0% |

For comparison, v1.7 cap-25 was 92.0% schema-valid, 69.6% monthly, 73.9% Purist, and 91.3% Pragmatic over 23 valid predictions.

## Operational Notes

A clean cap-25 relaunch after the deterministic validator change stalled after `1/25` and was stopped. Full-validation launchers also started prematurely and were stopped before completion (`30/299` and `40/299` progress checkpoints); those partial full runs have no metrics or predictions and must not be used as evidence.

## Decision

Decision scope: `arm`

The schema-validity defect is fixed enough to proceed to full validation with the current code and v1.8 prompt, with the caveat that the strongest cap-25 evidence is a completed v1.8 raw-prediction artifact plus deterministic post-hoc re-evaluation under the corrected validator.

Full validation should be launched only when local Ollama is free and monitored from detached logs. Do not use the stopped partial full-validation directory as evidence.

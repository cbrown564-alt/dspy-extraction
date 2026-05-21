# Gan S0 Post-Repair Validation Replay

Date: 2026-05-18

## Research Question

Did the narrow Gan S0 artifact-bridge surface repairs improve full-validation behavior without changing scorer semantics or crossing into semantic repair?

## Method

Source run:

- `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z`

Replay artifact:

- `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_surface_replay_20260518T000000Z`

The replay reused the stored raw model outputs from the full-validation `predictions.json`, reapplied the current `clinical_extraction.programs.gan_frequency_s0` artifact-bridge normalization to `raw_value`, and then evaluated the resulting `PredictionSet` with `gan_frequency_deterministic_v1`.

No model calls were made. The dataset, validation split, prompt/program variant, model config, and deterministic scorer were otherwise unchanged. Gan `seizure_frequency_number[0]` remains the gold label; `reference[0]` remains a secondary difficulty signal; evidence quote support remains diagnostic.

## Results

| Metric | Pre-repair run | Post-repair replay | Change |
|---|---:|---:|---:|
| Evaluated validation records | 299 | 299 | 0 |
| Valid predictions | 291 | 294 | +3 |
| Invalid predictions | 8 | 5 | -3 |
| Schema-valid prediction rate | 97.3% | 98.3% | +1.0 pp |
| Normalized-label accuracy | 51.5% | 52.0% | +0.5 pp |
| Monthly-frequency accuracy | 62.9% | 63.3% | +0.4 pp |
| Purist category accuracy | 70.1% | 70.4% | +0.3 pp |
| Pragmatic category accuracy | 73.9% | 74.1% | +0.3 pp |
| Evidence quote support rate | 89.9% | 90.0% | +0.1 pp |

Post-repair 95% bootstrap confidence intervals:

- Schema validity: 96.7%-99.7%
- Normalized-label accuracy: 46.3%-57.8%
- Monthly-frequency accuracy: 57.5%-68.7%
- Purist category accuracy: 65.0%-75.5%
- Pragmatic category accuracy: 69.0%-78.9%
- Evidence quote support: 86.1%-93.2%

The replay changed exactly three stored predictions:

| Record | Raw model label | Replayed normalized label |
|---|---|---|
| `gan_4100` | `1 per 3 week to 1 per 2 week` | `1 per 2 to 3 week` |
| `gan_4602` | `1 per 10 day to 1 per 7 day` | `1 per 7 to 10 day` |
| `gan_2135` | `"unknown"` | `unknown` |

All three changes are output-surface repairs that preserve the model's apparent meaning. The replay wrote these cases to:

- `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_surface_replay_20260518T000000Z/artifacts/surface_replay_changes.json`

## Remaining Error Shape

The remaining five invalid predictions are not safe deterministic repairs:

- `gan_10003`: incomplete cluster label, `1 cluster per week`
- `gan_10047`: incomplete cluster label, `2 cluster per 3 month`
- `gan_16523`: cluster label emitted where gold is a simple rate, `1 cluster per 5 day`
- `gan_16574`: unknown per-cluster count, `1 cluster per month, unknown per cluster`
- `gan_4700`: abstained or null output where the gold label is `multiple per day`

The remaining monthly-frequency errors are semantic rather than surface-only:

- frequent cluster gold labels predicted as `unknown`
- `unknown` gold labels predicted as `no seizure frequency reference`
- one `unknown` gold label predicted as an infrequent quantified rate
- denominator/window errors that remain inside the frequent pragmatic category

Evidence errors also remain diagnostic and separate from label scoring. The most common forms are stitched/non-contiguous quotes, paraphrases, joined quotes, and using label text as evidence.

## Interpretation

The current deterministic surface repairs are worthwhile but small. They mostly improve schema validity by converting three format-invalid labels into valid labels. The benchmark-facing metric lift is modest because the dominant residual failures are not malformed strings.

This supports the current repair boundary:

- deterministic repair may normalize one-to-one output surfaces such as quoted sentinels and matching-count denominator ranges
- incomplete clusters, `unknown per cluster`, abstentions, unknown/no-reference confusion, and temporal-window choices require an explicit verifier/repair program variant or a prompt/example change

## Follow-Up

Targeted regression fixtures now cover the observed boundary in `tests/test_evaluation_cli.py` and `tests/test_gan_s0_program.py`. The next Gan implementation should not add more deterministic postprocessing until an evidence-aware verifier/repair or abstention-calibration variant is explicitly designed and reported side by side with extraction-only metrics.

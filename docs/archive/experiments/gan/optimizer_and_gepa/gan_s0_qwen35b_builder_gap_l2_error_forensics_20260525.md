# Gan S0 L2 Qwen35b Builder-Gap Error Forensics

Date: 2026-05-25
Status: L2 forensics complete; no scorer, loader, or prediction changes
Decision scope: local-model error analysis for Gan S0 `builder-gap v1`

## Scope

| Field | Value |
| --- | --- |
| Dataset / split | Gan 2026 synthetic, `gan_2026_fixed_v1:validation` |
| Primary Qwen run | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` |
| GPT comparison run | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` |
| Implementation variant | `gan_s0_candidate_builder_gap_v1` |
| Scorer | `gan_frequency_deterministic_v1` |

Note: `runs/gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260525T071929Z/` contains config/metadata/prompts only, not scored prediction artifacts. This inspection therefore uses the completed Qwen run from 2026-05-23.

## Audit Guardrails

- Gan gold remains `seizure_frequency_number[0]`.
- `reference[0]` is a secondary cross-check and hard-case signal, not an alternate gold.
- `unknown` and `no seizure frequency reference` remain distinct benchmark-facing labels.
- Evidence support is diagnostic unless a run explicitly makes evidence prediction-affecting.
- Scorer semantics are unchanged.

## Headline Comparison

| Outcome on same 299 validation records | Count |
| --- | ---: |
| GPT correct, Qwen correct | 186 |
| GPT correct, Qwen monthly-failed/invalid | 55 |
| GPT monthly-failed, Qwen correct | 24 |
| GPT monthly-failed, Qwen monthly-failed/invalid | 34 |

Qwen is not simply a uniformly weaker copy of GPT: it recovers 24 records GPT misses. The local gap is still real, but it is concentrated in Qwen calibration and canonical label selection under sparse candidate coverage.

## Qwen Failure Counts

Qwen has 89 non-monthly-correct records relative to the 299-record validation run: 87 valid monthly mismatches plus 2 invalid predicted labels.

| Failure class | Count | Interpretation |
| --- | ---: | --- |
| `pragmatic_match_monthly_divergence` | 30 | Coarse clinical bucket right, exact monthly value wrong |
| `purist_bin_boundary_within_pragmatic` | 19 | Near-boundary/bin error inside same pragmatic bucket |
| `other_semantic_mismatch` | 13 | Heterogeneous semantic selection errors |
| `cluster_collapsed_to_rate` | 11 | Cluster structure lost, usually by reducing clusters to raw rate |
| `frequent_undercalled` | 5 | Frequent gold predicted as infrequent |
| `cluster_semantic_mismatch` | 4 | Cluster structure retained but count/window/per-cluster semantics wrong |
| `unknown_as_high_rate` | 2 | Unknown gold over-interpreted as frequent |
| `unknown_vs_seizure_free` | 2 | Unknown gold interpreted as seizure-free |
| `invalid_predicted_label` | 2 | Non-canonical surfaces: `many per month`, `q2 - 3wk` |
| `unknown_as_quantified_rate` | 1 | Unknown gold over-interpreted as quantified rate |

Gold pragmatic strata among Qwen failures:

| Gold pragmatic category | Count |
| --- | ---: |
| frequent | 68 |
| infrequent | 15 |
| unknown | 5 |
| no seizure information | 1 |

## Candidate Coverage

The deterministic candidate builder is not the dominant remaining coverage solution for the full validation split.

| Qwen failure candidate relation | Count |
| --- | ---: |
| No deterministic candidates emitted | 77 |
| Gold in candidates, Qwen predicted another label | 10 |
| Gold not in candidates, Qwen predicted a candidate | 1 |
| Gold not in candidates, Qwen predicted another label | 1 |

For the 55 records where GPT is monthly-correct and Qwen fails, 47 have no deterministic candidates. That means GPT often solved these from note text alone, while Qwen either picked a softened label, collapsed cluster structure, or fell back to `unknown`.

## Error Shape

| Shape | Count |
| --- | ---: |
| Rate-to-rate numeric/window mismatch | 54 |
| Specific label predicted as `unknown` | 12 |
| Cluster collapsed to non-cluster label | 11 |
| Cluster-to-cluster semantic mismatch | 4 |
| Unknown predicted as quantified/seizure-free label | 5 |
| Invalid label surface | 2 |
| Seizure-free confusion | 1 |

The largest tractable pattern is not missing evidence support. It is Qwen's tendency to replace precise canonical labels with coarser labels such as `multiple per day`, `multiple per week`, `unknown`, or a non-cluster rate.

## Deterministic Repair Candidates

Narrow possible repairs, requiring regression tests before any code change:

| Record | Gold | Qwen prediction | Repair assessment |
| --- | --- | --- | --- |
| `gan_338` | `multiple per month` | `many per month` | Possible canonical synonym repair from `many` to `multiple`, but only if treated as a surface-form repair with fixture coverage. |
| `gan_4100` | `1 per 2 to 3 week` | `q2 - 3wk` | Possible shorthand repair to `1 per 2 to 3 week`, but should be tested as a one-to-one shorthand normalization case. |

Do not deterministically repair the broader cluster, unknown, or temporal-window errors. Those require reading the note and deciding the intended current frequency.

## Evidence Note

`gan_16883` is monthly-correct for Qwen (`4 per 3 month`) but has an unsupported evidence quote because the prediction appended explanatory reasoning to an otherwise relevant quote. This is an evidence-format problem, not a frequency-label problem. A future evidence guard could trim commentary, but that should remain diagnostic unless preregistered as prediction-affecting.

## Recommended Next Work

1. Create a small Qwen regression/error slice from the 55 GPT-correct/Qwen-failed records, emphasizing cluster collapse, precise range/rate preservation, and `unknown` fallback.
2. Preregister one Qwen-specific policy arm that tells the model to preserve exact candidate/quote arithmetic and avoid replacing numeric ranges with `multiple` when the note gives explicit numbers.
3. Keep deterministic candidate builders unchanged for now. Full-split Qwen failures mostly lack candidate coverage, and expanding builders would be a new mechanism rather than a targeted L2 fix.
4. Add regression tests only if implementing the two narrow invalid-label surface repairs.

## Validation

- Parsed both run `predictions.json` files with the current repo package via `uv run python`.
- Rebuilt record-level rows using `build_gan_record_report_rows`.
- Recomputed paired GPT/Qwen monthly outcomes and deterministic candidate diagnostics with `build_temporal_candidate_diagnostics`.
- No model calls were made.
- No scorer semantics were changed.

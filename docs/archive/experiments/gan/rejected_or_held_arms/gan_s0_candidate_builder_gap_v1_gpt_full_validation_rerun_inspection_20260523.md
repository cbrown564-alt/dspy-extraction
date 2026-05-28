# Gan S0 Candidate Builder Gap V1 GPT Full-Validation Rerun Inspection

Date: 2026-05-23  
Status: Verified full-validation pass  
Run ID: `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z`  
Related: `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_reconciliation_20260523.md`, `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_preservation_note_20260523.md`

## Scope

| Field | Value |
| --- | --- |
| Dataset / split | Gan 2026 synthetic, `gan_2026_fixed_v1:validation` |
| Records | 299/299 validation records predicted and scored |
| Model / provider | GPT 4.1-mini / OpenAI |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` |
| Implementation variant | `gan_s0_candidate_builder_gap_v1` |
| Scorer | `gan_frequency_deterministic_v1` |
| Structured output | provider JSON schema with Pydantic validation |
| Varied factor | `implementation_variant` |

## Results

| Metric | Result |
| --- | ---: |
| Monthly-frequency accuracy | 80.6% (241/299) |
| Purist category accuracy | 86.0% (257/299) |
| Pragmatic category accuracy | 88.6% (265/299) |
| Normalized-label exact accuracy | 71.2% (213/299) |
| Schema-valid prediction rate | 100.0% |
| Evidence quote support rate | 100.0% |

Confidence intervals from `metrics.json`:

| Metric | 95% CI |
| --- | --- |
| Monthly-frequency accuracy | 76.3-85.3% |
| Purist category accuracy | 81.9-89.6% |
| Pragmatic category accuracy | 84.9-92.0% |
| Normalized-label exact accuracy | 66.2-76.6% |

Runtime: 506.0 seconds total, 299 estimated model calls, 1,068,355 prompt tokens and 12,340 completion tokens.

## Candidate-Emission Verification

The rerun clears the stale G16 failure mode. The enriched 25-record slice now replays the deterministic candidate surface:

| Check | Result |
| --- | ---: |
| Enriched-slice emitted candidate lists | 23/25 non-empty |
| Enriched-slice gold-in-emitted-candidates | 23/25 |
| Enriched-slice monthly accuracy | 23/25 |
| Full-split emitted candidate lists | 61/299 non-empty |
| Full-split gold-in-emitted-candidates | 58/299 |
| Full-split deterministic no-model gold-in-candidates | 58/299 |

The two enriched-slice no-candidate records were `gan_13574` and `gan_13598`, both with gold `seizure free for multiple year`; these were already the remaining no-model coverage misses. This differs from the stale G16 artifact, where the same enriched slice had empty candidate lists for 19/25 records and only 5/25 gold-in-candidates.

## Error Profile

There were 58 monthly-frequency mismatches.

| Failure class | Count |
| --- | ---: |
| `other_semantic_mismatch` | 17 |
| `pragmatic_match_monthly_divergence` | 16 |
| `purist_bin_boundary_within_pragmatic` | 7 |
| `frequent_undercalled` | 7 |
| `unknown_as_quantified_rate` | 3 |
| `unknown_vs_seizure_free` | 2 |
| `unknown_as_high_rate` | 2 |
| `cluster_collapsed_to_rate` | 2 |
| `frequent_overcalled` | 1 |
| `unknown_vs_no_reference` | 1 |

Gold pragmatic strata among monthly mismatches: frequent 42, unknown 8, infrequent 8. Nine records had no prediction evidence span, but evidence support was 100% for predictions with spans.

## Interpretation

This rerun validates that the recovered candidate-builder surface is active at full-validation runtime. It also materially improves over both the operational F0 GPT anchor and the stale G16 artifact:

| Run | Monthly | Purist | Pragmatic | Validity | Evidence |
| --- | ---: | ---: | ---: | ---: | ---: |
| F0 GPT anchor | 68.1% | not restated here | not restated here | 100.0% | 100.0% |
| Stale G16 artifact | 75.9% | 81.3% | 85.6% | 100.0% | 100.0% |
| Verified rerun | 80.6% | 86.0% | 88.6% | 100.0% | 100.0% |

The mechanism should be treated as a successful arm-level implementation variant, not as a broad closure of Gan S0. Full-split deterministic candidate coverage remains sparse at 58/299 because the builder-gap work targeted a specific enriched residual slice. The remaining failures are mostly semantic adjudication and frequency-selection errors, not a replay of the empty-candidate incident.

## Decision

| Item | Position |
| --- | --- |
| Stale G16 artifact | Superseded by verified rerun |
| `gan_s0_candidate_builder_gap_v1` GPT arm | Promote as verified full-validation arm evidence |
| Operational default | Eligible for a separate promotion review; do not silently replace defaults from this inspection alone |
| Qwen transfer | Unblocked as a possible follow-up, but should be separately preregistered |
| Registry / paper evidence | May be backfilled from this verified rerun, with caveat that this is Gan synthetic validation |

Scorer semantics are unchanged: primary gold remains `seizure_frequency_number[0]`; `reference[0]` remains a secondary difficulty signal; normalized-label exact remains diagnostic.

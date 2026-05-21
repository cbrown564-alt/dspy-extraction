# Gan S0 Exact-Frequency Residual Manual Read

Date: 2026-05-21  
Status: Manual error-read of exported residual slice  
Run: `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`  
Dataset / split: `gan_2026_fixed_v1:validation`  
Model / program: GPT 4.1-mini, temporal candidates + verify-repair guardrails  
Scorer: `gan_frequency_deterministic_v1`  
Source artifacts:

- `docs/gan_s0_residual_exact_frequency_error_analysis_20260521.md`
- `docs/gan_s0_exact_frequency_residual_slice_error_read_20260521.md`
- `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/analysis/exact_frequency_residual_slice/summary.json`
- `runs/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z/analysis/exact_frequency_residual_slice/error_read_selection.jsonl`

## Research Question

After the promoted Gan S0 pipeline reaches strong schema/evidence diagnostics and good coarse category performance, what specific mechanisms explain its remaining exact monthly-frequency misses, and what should the next candidate primitive expose?

## Audit Assumptions

This read preserves the Gan audit and deterministic scorer semantics:

- Primary gold remains `seizure_frequency_number[0]`.
- `reference[0]` is a secondary difficulty signal, not gold.
- Evidence support is diagnostic unless an experiment explicitly makes it prediction-affecting.
- Exact monthly-frequency misses are benchmark-facing; normalized-label-only misses are not the target here.
- No deterministic repair should infer unknown-vs-quantified, cluster spacing, or long-window denominators from label shape alone.

## Slice Read

The queue contains 30 representative records from the 104 benchmark-severe monthly-frequency misses:

| Slice group | Selected | Main mechanism from manual read |
| --- | ---: | --- |
| Arithmetic/window precision | 10 | Wrong policy target or denominator despite real supporting quote |
| Unknown-vs-quantified | 8 | Model invents a denominator/window when the note only gives an unanchored count or vague cluster spacing |
| Cluster composition | 8 | Cluster slots are present in text, but the model loses spacing, count, or per-cluster separation |
| Infrequent long-denominator/boundary | 4 | Model treats residual count as monthly/recent rate instead of dividing over the elapsed long window |

## Mechanism Counts

| Mechanism | Records | Interpretation |
| --- | ---: | --- |
| Highest-frequency seizure-type selection failure | 5 | A lower-frequency seizure type is quoted correctly, but gold follows a higher-frequency concurrent seizure type. |
| Calendar/window aggregation failure | 5 | Counts across dated months or follow-up intervals are not summed and divided over the correct denominator. |
| Unknown denominator hallucination | 6 | The note gives a count since an anchor or with a latest date, but insufficient denominator; model creates a per-month/per-week rate. |
| Unknown cluster spacing hallucination | 2 | Per-cluster counts or episodic bursts are present, but cluster spacing is unclear; model invents daily/weekly spacing. |
| Cluster slot omission/abstention | 4 | Text implies clusters, but model outputs `unknown` rather than preserving cluster structure. |
| Cluster spacing/count swap | 4 | Model confuses within-cluster duration/frequency shorthand with cluster spacing, or collapses `2x/3x per month` to `1 cluster per month`. |
| Long-window residual-count compression | 4 | Model treats a residual count as a monthly current rate instead of tying it to a seizure-free-since or withdrawal/follow-up window. |

The same surface failure class can reflect different mechanisms. For example, `purist_bin_boundary_within_pragmatic` includes both “picked the wrong seizure type” and “used the wrong denominator after a real count.”

## Representative Findings

### 1. The verifier confirms quote validity, not benchmark policy

Most wrong predictions are supported by a real contiguous quote. The verifier repeatedly confirms because the label matches a phrase in the note, even when that phrase is not the Gan gold target.

Examples:

- `gan_12562`: predicted `4 per week` from generalised tonic-clonic seizures, but gold is `1 per day` from daily drop attacks.
- `gan_12667` and `gan_12679`: predicted monthly generalised tonic-clonic frequency, but gold is daily absences.
- `gan_16947` and `gan_16964`: predicted generalised tonic-clonic events every two months, but gold is twice-weekly absences.

Implication: evidence support must not be treated as semantic sufficiency. The next verifier needs an explicit “selected target is the benchmark-facing highest/current frequency” check.

### 2. Calendar aggregation is missing, not merely arithmetic

Several records require summing counts across named months or elapsed follow-up periods:

- `gan_15923`: gold `8 per 2 month`; model predicts `7 per month` despite quoting both October and November counts.
- `gan_16251`: gold `14 per 4 month`; model predicts `7 per month` from the largest single month.
- `gan_16753`: gold `19 per 6 month`; model predicts `5 per month` from the latest/highest monthly count.
- `gan_14250` and `gan_14271`: model converts “in the following week” directly to a weekly rate even though the gold denominator is the broader observation/follow-up window.

Implication: the candidate primitive needs event-count aggregation plus denominator provenance, not just more candidate labels.

### 3. Unknown labels usually protect against unanchored denominators

The unknown-vs-quantified misses often contain a real count but no benchmark-usable time window:

- `gan_13993`: “two-three seizures” since discharge, latest date given; model predicts `2 to 3 per month`.
- `gan_14025`, `gan_14036`, `gan_14081`, `gan_14092`, `gan_14137`: counts are anchored to diet/medication start or latest date, but the model creates a denominator.
- `gan_10618` and `gan_10751`: cluster runs are described, but spacing is unclear; model invents daily/weekly cluster frequency.

Implication: the next primitive should emit an explicit `denominator_status` such as `explicit`, `derivable_from_dates`, `missing_or_ambiguous`, plus an `unknown_policy_cue`.

### 4. Cluster errors are slot errors

Cluster failures are not one thing:

- `gan_10031`, `gan_10673`, and `gan_15240`: model abstains as `unknown` where gold preserves cluster form with vague but benchmark-sanctioned spacing such as weekly/monthly/annual cluster occurrence.
- `gan_10434`: gold combines “several mornings each week” with “two or three times within the same morning”; model collapses to `unknown`.
- `gan_15255`: model mistakes “a few mornings within the same week before settling” for a weekly cluster rate, while gold uses a long-window cluster label.
- `gan_15404`: model uses “single day” as cluster spacing, but gold uses a 4-month cluster interval with `3 to 4 per cluster`.
- `gan_10984` and `gan_10993`: shorthand `3x/month` and `2x/month` is correctly quoted but decoded as `1 cluster per month`.

Implication: a useful slot payload needs separate fields for `cluster_count`, `cluster_window_count`, `cluster_window_unit`, `per_cluster_count`, and a flag distinguishing `within_cluster_duration` from `cluster_spacing`.

### 5. Infrequent long-window records need abstention from local monthly compression

The infrequent failures are severe because the model turns low-rate long-window evidence into frequent current rates:

- `gan_13290`: gold `4 per 6 month`; model predicts `2 per 3 week`.
- `gan_14354`: gold `2 to 4 per 3 month`; model predicts `2 to 4 per month`.
- `gan_15302`: gold `1 to 2 per 14 month`; model predicts `1 to 2 per month`.
- `gan_15306`: gold `2 to 3 per 15 month`; the deterministic candidate includes the exact gold, but confirm-first verification keeps `1 to 3 per month`.

Implication: the verifier should be allowed to prefer a structured candidate over the initial label when the candidate has explicit long-window provenance and the initial prediction has a missing or guessed denominator.

## Candidate Primitive Design Implication

Do not build a generic “more labels” candidate primitive. The evidence points to a structured slot payload:

| Slot | Purpose |
| --- | --- |
| `candidate_label` | Canonical Gan label only after slot provenance is available |
| `event_count_or_range` | Numerator or numerator range |
| `event_type` | Seizure type whose frequency is being counted |
| `target_priority_cue` | Whether this is highest/current benchmark-facing frequency versus a lower-frequency concurrent type |
| `window_count` | Denominator count |
| `window_unit` | Denominator unit |
| `window_source` | Explicit text, calendar aggregation, elapsed since date, follow-up interval, or missing |
| `denominator_status` | `explicit`, `derivable`, `missing_or_ambiguous`, or `not_applicable` |
| `cluster_count_or_range` | Number of clusters in the window |
| `per_cluster_count_or_range` | Events per cluster |
| `cluster_spacing_source` | Explicit spacing versus within-cluster duration versus vague recurrence |
| `unknown_policy_cue` | Whether label should remain `unknown` because denominator/spacing is not benchmark-derivable |
| `supporting_quote` | Exact contiguous quote for the slot, not only for the final label |

The primitive should be evaluated first as a diagnostic payload and then as a fixed Axis 3 implementation variant on the winning Gan skeleton. It should not deterministically rewrite labels outside a preregistered experiment.

## Deterministic Repair Assessment

No broad deterministic repair is justified.

Allowed existing repairs remain narrow surface repairs such as quoted special labels or unambiguous canonical denominator-range surfaces. The manual read does not support deterministic repair for:

- selecting a higher-frequency seizure type from competing frequency mentions,
- converting unanchored counts into `unknown`,
- deriving elapsed denominators from dates,
- assigning cluster spacing from vague recurrence language,
- replacing an initial prediction with a candidate label.

Those choices require semantic reading of the note and should be tested via a verifier/repair or candidate-slot experiment.

## Recommended Next Experiment

Preregister an Axis 3 implementation variant on the current winning Gan skeleton:

- Dataset / split: `gan_2026_fixed_v1`, cap-25 first, then validation if lifted.
- Stage graph: keep `g2_candidates_adjudicate` or the promoted temporal-candidates verify-repair skeleton fixed.
- Varied factor: implementation variant only.
- Candidate variant: `gan_s0_exact_frequency_slot_payload_gpt_cap25_v1`.
- Primary metric: monthly-frequency accuracy under `gan_frequency_deterministic_v1`.
- Required stratified readouts: infrequent gold, unknown gold, cluster-label gold, and the 30-record residual slice.
- Required diagnostic readouts: candidate gold coverage, candidate selected rate, denominator-status distribution, verifier repairs from initial label to candidate label, and false repairs where initial label was monthly-correct.

Promotion gate should require monthly lift on the cap slice without increasing unknown/no-reference confusions or cluster hallucinations. Full validation and Qwen transfer should stay deferred until the cap-25 slot payload shows a real lift.

## Caveats

- This is a manual read of a representative 30-record slice, not a full reclassification of all 104 monthly misses.
- The 13 `other_benchmark_severe` misses were intentionally left unselected and still need review before a final taxonomy freeze.
- The read uses current generated artifacts; no new model calls were made.
- Some Gan gold choices encode benchmark policy rather than a clinically singular “true” current frequency, especially when multiple seizure types coexist.

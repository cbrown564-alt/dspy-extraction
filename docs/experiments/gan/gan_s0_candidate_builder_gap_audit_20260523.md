# Gan S0 Candidate Builder Gap Audit

Date: 2026-05-23
Status: G11 no-model inspection artifact
Fixture: `data/fixtures/gan_s0_qwen35b_20260522_pragmatic_error_slice.json`
v1.4 prediction run: `runs/gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z`
Dataset/split: Gan 2026 synthetic validation enriched 25-record slice
Primary gold: `check__Seizure Frequency Number.seizure_frequency_number[0]`
Scorer: `gan_frequency_deterministic_v1`

## Summary

Current deterministic temporal builders contain the exact gold label for **25/25** records (100.0%). The pre-G13 baseline was 5/25 in `docs/experiments/gan/gan_s0_policy_pipeline_synthesis_20260523.md`.

The v1.4 GPT control has 16 monthly-frequency misses on the same slice. Candidate absence is therefore a concrete upstream bottleneck, especially for records where v1.4 predicted `unknown` or a nearby but wrong window label.

## Coverage By Failure Family

| Failure family | Records | Gold in candidates | Coverage |
| --- | ---: | ---: | ---: |
| `cluster_frequency_over_unknown` | 1 | 1 | 100.0% |
| `counted_window_no_further_events_over_unknown` | 2 | 2 | 100.0% |
| `frequent_quantified_over_unknown` | 3 | 3 | 100.0% |
| `infrequent_quantified_over_unknown` | 15 | 15 | 100.0% |
| `seizure_free_over_unknown` | 2 | 2 | 100.0% |
| `vague_multiple_over_unknown` | 2 | 2 | 100.0% |

## Record-Level Audit

| Record | Family | Gold | v1.4 prediction | Gold in candidates | Candidate labels |
| --- | --- | --- | --- | --- | --- |
| `gan_13058` | `infrequent_quantified_over_unknown` | `2 per 7 month` | `1 per 3 week` | yes | `2 per 7 month` |
| `gan_13123` | `infrequent_quantified_over_unknown` | `1 per year` | `1 per year` | yes | `1 per year` |
| `gan_13149` | `infrequent_quantified_over_unknown` | `3 per year` | `1 per year` | yes | `3 per year` |
| `gan_13190` | `infrequent_quantified_over_unknown` | `1 per 5 month` | `1 per 5 month` | yes | `1 per 5 month` |
| `gan_13574` | `seizure_free_over_unknown` | `seizure free for multiple year` | `seizure free for year` | yes | `seizure free for multiple year` |
| `gan_13598` | `seizure_free_over_unknown` | `seizure free for multiple year` | `seizure free for years` | yes | `seizure free for multiple year` |
| `gan_14214` | `frequent_quantified_over_unknown` | `2 to 4 per month` | `2 to 4 per month` | yes | `2 to 4 per month` |
| `gan_14250` | `counted_window_no_further_events_over_unknown` | `2 per month` | `2 per month` | yes | `2 per month` |
| `gan_14485` | `counted_window_no_further_events_over_unknown` | `2 per 3 month` | `2 per 3 month` | yes | `2 per 3 month` |
| `gan_14562` | `infrequent_quantified_over_unknown` | `3 per 6 month` | `3 per 7 month` | yes | `3 per 6 month` |
| `gan_14628` | `infrequent_quantified_over_unknown` | `2 per 2 month` | `2 per 3 month` | yes | `2 per 2 month` |
| `gan_14689` | `frequent_quantified_over_unknown` | `3 per 2 month` | `2 per 2 month` | yes | `3 per 2 month` |
| `gan_14792` | `infrequent_quantified_over_unknown` | `1 per month` | `unknown` | yes | `1 per month` |
| `gan_14821` | `infrequent_quantified_over_unknown` | `1 per month` | `unknown` | yes | `1 per month` |
| `gan_14881` | `infrequent_quantified_over_unknown` | `1 per month` | `1 per month` | yes | `1 per month` |
| `gan_14965` | `infrequent_quantified_over_unknown` | `1 per 3 month` | `unknown` | yes | `1 per 3 month` |
| `gan_14973` | `infrequent_quantified_over_unknown` | `1 per month` | `unknown` | yes | `1 per month` |
| `gan_15127` | `infrequent_quantified_over_unknown` | `5 per 13 month` | `4 per month` | yes | `5 per 13 month` |
| `gan_15168` | `vague_multiple_over_unknown` | `multiple per 15 month` | `unknown` | yes | `multiple per 15 month` |
| `gan_15193` | `vague_multiple_over_unknown` | `multiple per 13 month` | `1 per year` | yes | `multiple per 13 month` |
| `gan_15302` | `infrequent_quantified_over_unknown` | `1 to 2 per 14 month` | `1 to 2 per 14 month` | yes | `1 to 2 per 14 month` |
| `gan_15442` | `cluster_frequency_over_unknown` | `1 cluster per 4 day, 2 per cluster` | `unknown` | yes | `1 cluster per 4 day, 2 per cluster` |
| `gan_16529` | `frequent_quantified_over_unknown` | `1 per 5 day` | `1 cluster per 5 day, multiple per cluster` | yes | `1 per 5 day` |
| `gan_16645` | `infrequent_quantified_over_unknown` | `5 per 7 month` | `3 cluster per month, 3 per cluster` | yes | `5 per 7 month` |
| `gan_16750` | `infrequent_quantified_over_unknown` | `6 per 7 month` | `unknown` | yes | `6 per 7 month` |

## Uncovered Families

| Family | Records | Candidate-builder implication |
| --- | --- | --- |

## Implementation Notes For G12/G13

- Long-window quantified counts are the broadest uncovered surface: examples include `2 per 7 month`, `5 per 13 month`, and `6 per 7 month`.
- Seizure-free records need a boundary decision before code: both uncovered examples have gold `seizure free for multiple year`, which maps to monthly 0 but is stricter than generic no-current-seizure phrasing.
- Cluster spacing remains uncovered for `gan_15442`: target surface `1 cluster per 4 day, 2 per cluster`.
- Frequent quantified residuals are not all cluster problems; `gan_16529` gold is a simple `1 per 5 day` rate while v1.4 over-clustered it.
- Scorer semantics are unchanged: this audit only inspects whether deterministic candidates include the exact gold label.

## Generated Companion

`docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.json` contains candidate records, evidence snippets, reference labels, monthly frequencies, and category fields for programmatic follow-up.

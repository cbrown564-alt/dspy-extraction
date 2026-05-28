# Gan S0 G2 Model-Arm Comparison

Generated: `2026-05-28T14:57:05.701439+00:00`

## Scope

- Dataset: `gan_2026`
- Split: `gan_2026_fixed_v1:validation`
- Records: `25` enriched validation records
- Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`
- Comparison group: `gan_s0_g2_model_arm_comparison_v1`

## Arm Summary

| Arm | Run ID | Program variant | Valid | Paper monthly | Canonical monthly | Canonical normalized | Canonical purist | Canonical pragmatic | Mean candidates | Mean options | Selected source counts |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `free_adjudication` | `gan_s0_g2_free_adjudication_gpt4_1_mini_slice_20260528T155000Z` | `gan_frequency_s0_direct_single_pass` | 25/25 | 16.0% | 16.0% | 8.0% | 56.0% | 76.0% | 0.0 | 0.0 |  |
| `candidate_constrained` | `gan_s0_g2_candidate_constrained_gpt4_1_mini_slice_20260528T155000Z` | `gan_frequency_s0_temporal_candidates_single_pass` | 25/25 | 92.0% | 92.0% | 92.0% | 92.0% | 92.0% | 1.0 | 0.0 |  |
| `reason_code_selector` | `gan_s0_g2_reason_code_selector_gpt4_1_mini_slice_20260528T155000Z` | `gan_frequency_s0_seeded_multiple_answer_det_selector` | 25/25 | 92.0% | 92.0% | 92.0% | 92.0% | 100.0% | 1.0 | 3.3 | `deterministic_temporal_candidate`=23, `llm_answer_option`=2 |

## Pairwise Signal

| Scorer | Metric | Best arms | Best accuracy |
| --- | --- | --- | ---: |
| `paper_reproduction` | monthly | `candidate_constrained`, `reason_code_selector` | 92.0% |
| `paper_reproduction` | normalized label | `candidate_constrained`, `reason_code_selector` | 92.0% |
| `paper_reproduction` | pragmatic category | `reason_code_selector` | 100.0% |
| `canonical` | monthly | `candidate_constrained`, `reason_code_selector` | 92.0% |
| `canonical` | normalized label | `candidate_constrained`, `reason_code_selector` | 92.0% |
| `canonical` | pragmatic category | `reason_code_selector` | 100.0% |

## Interpretation

- The candidate-constrained and seeded selector arms both recover the G2 target-selection lift on this enriched slice; free full-note adjudication does not.
- The seeded selector is reported as a reason-code/answer-options surrogate because it preserves option source, status, ambiguity flags, and deterministic selection metadata, but it is not a newly designed explicit reason-code adjudicator.
- Slice metrics are diagnostic. They should guide mechanism selection and error forensics, not stand in for full-validation or test performance.

## Differential Records

| Record | Gold | Free | Candidate | Reason-code surrogate | Canonical monthly pattern |
| --- | --- | --- | --- | --- | --- |
| `gan_13058` | `2 per 7 month` | `1 per 7 week` | `2 per 7 month` | `1 per 1 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=False |
| `gan_13123` | `1 per year` | `1 per year` | `1 per year` | `1 per multiple months` | `candidate_constrained`=True, `free_adjudication`=True, `reason_code_selector`=False |
| `gan_13149` | `3 per year` | `1 per 3 month` | `3 per year` | `3 per year` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_13190` | `1 per 5 month` | `1 per 3 month` | `1 per 5 month` | `1 per 5 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14214` | `2 to 4 per month` | `1 to 4 per month` | `2 to 4 per month` | `2 to 4 per month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14250` | `2 per month` | `2 per week` | `2 per month` | `2 per month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14485` | `2 per 3 month` | `1 per 3 month` | `2 per 3 month` | `2 per 3 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14562` | `3 per 6 month` | `3 per 7 month` | `3 per 6 month` | `3 per 6 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14628` | `2 per 2 month` | `2 per 3 month` | `2 per 2 month` | `2 per 2 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14689` | `3 per 2 month` | `1 to 3 per 2 month` | `3 per 2 month` | `3 per 2 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14792` | `1 per month` | `unknown` | `1 per month` | `1 per month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14881` | `1 per month` | `unknown` | `1 per month` | `1 per month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14965` | `1 per 3 month` | `unknown` | `1 per 3 month` | `1 per 3 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_14973` | `1 per month` | `unknown` | `1 per month` | `1 per month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_15127` | `5 per 13 month` | `5 per year` | `5 per 13 month` | `5 per 13 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_15168` | `multiple per 15 month` | `1 per month` | `unknown` | `multiple per 15 month` | `candidate_constrained`=False, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_15193` | `multiple per 13 month` | `1 per month` | `multiple per month` | `multiple per 13 month` | `candidate_constrained`=False, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_15302` | `1 to 2 per 14 month` | `1 to 2 per month` | `1 to 2 per 14 month` | `1 to 2 per 14 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_15442` | `1 cluster per 4 day, 2 per cluster` | `1 cluster per day, 2 per cluster` | `1 cluster per 4 day, 2 per cluster` | `1 cluster per 4 day, 2 per cluster` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_16529` | `1 per 5 day` | `1 cluster per 5 day, multiple per cluster` | `1 per 5 day` | `1 per 5 day` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_16645` | `5 per 7 month` | `1 cluster per 6 month, 3 per cluster` | `5 per 7 month` | `5 per 7 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |
| `gan_16750` | `6 per 7 month` | `4 per 6 month` | `6 per 7 month` | `6 per 7 month` | `candidate_constrained`=True, `free_adjudication`=False, `reason_code_selector`=True |

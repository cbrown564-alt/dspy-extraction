# Gan S0 R10 Promotion And Holdout Selection Review

Date: 2026-05-26
Status: Completed
Decision scope: operational holdout selection
Related board card: `docs/planning/kanban_plan.md` R10

## Research Question

Which Gan S0 validation candidate should be allowed to move to the fixed test
holdout queue, and should the late R9 Qwen recovery candidate replace the
existing builder-gap v1 default?

## Decision

**Do not promote R9 Qwen recovery to the Gan test holdout.** Hold it as useful
validation evidence for schema-recovery policy, but not as the final test
candidate.

**Promote the existing builder-gap v1 Gan pair to test-holdout reporting:**

| Role | Config | Validation anchor |
| --- | --- | --- |
| Primary hosted Gan S0 candidate | `configs/experiments/test_holdout/gan_s0_builder_gap_v1_gpt4_test.json` | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` |
| Local-transfer companion | `configs/experiments/test_holdout/gan_s0_builder_gap_v1_qwen35b_test.json` | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` |

These configs already use `gan_2026_fixed_v1:test` and
`report_on_test_split: true`. They should be run as one-shot confirmation
reports only. Do not tune prompts, adapters, scorers, or bridge policy from test
results.

## Evidence Considered

| Candidate | Run ID | Model | Monthly | Purist | Pragmatic | Schema valid | Evidence support | Valid / predicted |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Builder-gap v1 operational default | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | GPT 4.1-mini | 80.6% | 86.0% | 88.6% | 100.0% | 100.0% | 299 / 299 |
| Builder-gap v1 local transfer | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` | Qwen3.6:35b | 70.7% | 83.2% | 90.6% | 99.3% | 99.7% | 297 / 299 |
| R9 recovery candidate | `gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T122351Z` | Qwen3.6:35b | 69.1% | 76.5% | 81.2% | 99.7% | 99.0% | 298 / 299 |
| GPT exact-policy comparison | `gan_s0_l2_exact_policy_full_gpt4_1_mini_20260526T123247Z` | GPT 4.1-mini | 78.5% | 86.9% | 90.3% | 99.7% | 100.0% | 298 / 299 |

R9 improves schema validity relative to earlier R1.1 replays, but it does not
beat the accepted builder-gap Qwen transfer on monthly, Purist, Pragmatic, or
evidence-support metrics. The same exact-policy surface also trails the GPT
builder-gap operational default on monthly accuracy. That makes R9 valuable as a
schema-recovery result, not the best final holdout candidate.

## Fixed Controls For Holdout

| Control | Value |
| --- | --- |
| Dataset | Gan 2026 synthetic |
| Split | `gan_2026_fixed_v1:test` |
| Gold source | `seizure_frequency_number[0]` |
| Reference field | Diagnostic cross-check only |
| Schema level | `gan_frequency_s0` |
| Scorer mode | `gan_frequency_deterministic_v1` |
| Program variant | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt version | `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` |
| Implementation variant | `gan_s0_candidate_builder_gap_v1` |
| Structured output | Provider JSON schema with Pydantic validation |
| Primitive surface | `gan.frequency.temporal_candidates.v1` with deterministic candidate preconditioning and LLM adjudication |

## Interpretation

The builder-gap v1 surface remains the strongest validated Gan S0 operational
candidate. The GPT arm is the primary paper-facing hosted candidate because it
has the highest validation monthly accuracy and perfect validation schema/evidence
rates. The Qwen arm should be reported as local-transfer evidence because it
cleared its preregistered acceptance gate and remains stronger than the late R9
Qwen recovery candidate on benchmark-facing metrics.

R9 should be cited narrowly: it demonstrates that schema recovery can nearly
eliminate invalid abstentions, but the recovery policy did not improve the core
frequency decision enough to justify replacing builder-gap v1 for holdout.

## Audit And Scorer Caveats

- Gan gold remains `seizure_frequency_number[0]`; `reference[0]` is not gold.
- `unknown` and `no seizure frequency reference` must remain distinct.
- Label-reference disagreements are difficulty signals, not gold failures.
- Evidence support is deterministic quote/source grounding, not clinical
  adjudication.
- Raw exact and normalized-label exact metrics remain diagnostic unless an
  experiment explicitly targets label-scheme reproduction.
- Gan Real(300) / Real(150) reporting remains blocked by data access and a
  separate reporting protocol; this review covers only the synthetic fixed test
  split.

## Operational Consequence

Gan is no longer blocked by R10 for the overnight test queue. The queue may run
the two builder-gap v1 Gan test configs listed above after the earlier scheduled
ExECT holdout entries. Report the resulting run IDs and metrics as holdout
confirmation, not as input for further prompt or scorer tuning.

## Validation

This review used existing artifacts only. No scorer, loader, split, prompt, or
config semantics were changed.

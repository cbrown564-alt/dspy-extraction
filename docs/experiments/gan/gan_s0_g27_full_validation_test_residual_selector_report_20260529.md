# Gan S0 G27 Full-Validation And Test-Residual Selector Report

Status: completed full-validation and frozen-test residual check
Date: 2026-05-29
Kanban card: G27 - Gan Full-Validation And Test-Residual Selector Check
Dataset/splits: Gan 2026 synthetic (`gan_2026_fixed_v1:validation` and frozen `gan_2026_fixed_v1:test`)
Model/provider: GPT-4.1-mini / OpenAI
Program variant: `gan_frequency_s0_evidence_first_target_selector`
Prompt version: `gan_frequency_s0_evidence_first_target_selector_v1_0`
Primary scorer: `gan2026_paper_reproduction` with repair, range, and tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1`

## Scope

G27 scales the G24/G28 evidence-first target selector after G28 cleared the G25
standard50 gate. It does not change scorer, loader, split, benchmark bridge,
candidate-builder, `gan.frequency.aggregation_constructor.v1`, prediction
repair, prompt version, model, or structured-output strategy.

Frozen-test evidence is residual-analysis evidence only. It was not used to
tune selector wording, candidate policy, special-label policy, scorer policy,
or repair policy.

## Runs

| Scope | Config | Run ID | Records | Model calls |
| --- | --- | --- | ---: | ---: |
| Validation | `configs/experiments/gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_full_validation.json` | `gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_full_validation_20260529T132143Z` | 299 | 299 |
| Frozen test | `configs/experiments/test_holdout/gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_test.json` | `test_holdout_gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_20260529T134518Z` | 301 | 301 |

Inspected artifacts:

- `runs/gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_full_validation_20260529T132143Z/metadata.json`
- `runs/gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_full_validation_20260529T132143Z/metrics.json`
- `runs/gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_full_validation_20260529T132143Z/errors.json`
- `runs/gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_full_validation_20260529T132143Z/artifacts/canonical_metrics.json`
- `runs/test_holdout_gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_20260529T134518Z/metadata.json`
- `runs/test_holdout_gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_20260529T134518Z/metrics.json`
- `runs/test_holdout_gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_20260529T134518Z/errors.json`
- `runs/test_holdout_gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_20260529T134518Z/artifacts/canonical_metrics.json`

## Results

### Paper-Reproduction Metrics

| Scope | Monthly | 95% CI | Purist | Pragmatic | Schema valid | Evidence quote support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| G28 standard50 | 44/50 (88.0%) | 78.0%-96.0% | 88.0% | 90.0% | 100.0% | 100.0% |
| G27 validation | 247/299 (82.6%) | 78.3%-87.0% | 85.3% | 88.6% | 100.0% | 100.0% |
| G27 frozen test | 196/301 (65.1%) | 59.5%-70.4% | 70.8% | 74.1% | 100.0% | 100.0% |

Validation improves over the stored synthetic paper-default builder-gap GPT
baseline from G5 (239/299, 79.9% paper monthly) by 8 records / 2.7 percentage
points. It also exceeds the D1 v1.2b mechanism baseline (229/299, 76.6%) by 18
records / 6.0 percentage points. This is synthetic-validation evidence only,
not Real(300)/Real(150) benchmark reproduction.

### Canonical Diagnostic Metrics

| Scope | Monthly | 95% CI | Purist | Pragmatic | Normalized label |
| --- | ---: | ---: | ---: | ---: | ---: |
| G27 validation | 245/299 (81.9%) | 77.6%-86.3% | 84.3% | 87.6% | 75.9% |
| G27 frozen test | 193/301 (64.1%) | 58.5%-69.4% | 69.8% | 73.1% | 57.8% |

The canonical view tracks the paper-reproduction view closely, so the
validation-to-test drop is not just a paper-scorer artifact.

## Residual Analysis

### Validation Misses

G27 validation has 52 paper-monthly mismatches. By gold-label family:

| Gold family | Misses |
| --- | ---: |
| quantified_rate | 31 |
| unknown | 17 |
| unknown_cluster | 1 |
| seizure_free | 1 |
| vague_or_multiple_rate | 1 |
| cluster | 1 |

The dominant validation residual is still target selection among quantified
rates plus unclear-frequency rows routed into concrete or seizure-free outputs.
The most common mismatch pairs are quantified-to-quantified (17),
unknown-to-seizure-free (11), quantified-to-seizure-free (9), and
unknown-to-quantified (4).

### Frozen-Test Misses

G27 frozen test has 105 paper-monthly mismatches. By gold-label family:

| Gold family | Misses |
| --- | ---: |
| quantified_rate | 67 |
| cluster | 14 |
| unknown | 10 |
| vague_or_multiple_rate | 9 |
| seizure_free | 4 |
| unknown_cluster | 1 |

The test residual is broader than the validation residual. Quantified-rate
misses remain the largest class, but cluster rows and vague/multiple-rate rows
become more visible. The most common mismatch pairs are
quantified-to-quantified (26), quantified-to-unknown (24),
quantified-to-seizure-free (13), cluster-to-unknown (5), cluster-to-quantified
(5), and unknown-to-quantified (6).

### Paired Test Comparison Against Builder-Gap GPT

Against the stored frozen-test builder-gap GPT run, G27 is almost tied in
aggregate paper-monthly accuracy:

| Arm | Paper monthly | Purist | Pragmatic |
| --- | ---: | ---: | ---: |
| Builder-gap GPT frozen test | 197/301 (65.4%) | 70.8% | 77.1% |
| G27 evidence-first frozen test | 196/301 (65.1%) | 70.8% | 74.1% |

The aggregate hides substantial row churn:

- G27 fixes 43 builder-gap monthly misses.
- G27 regresses 41 builder-gap monthly hits.
- 64 rows are wrong in both arms.
- 153 rows are right in both arms.

G27 fixes builder misses mainly in quantified_rate (24), seizure_free (7), and
cluster (6) rows, but regresses builder hits mainly in quantified_rate (27) and
unknown (6) rows. The most concerning regression pattern is
quantified_rate-to-unknown (11 rows) and quantified_rate-to-seizure_free (4
rows), because it suggests the evidence-first interface can overuse abstention
or seizure-free interpretations on test notes even while it improved the
standard50 mechanism slice.

## Interpretation

G27 confirms that the evidence-first selector is the strongest current
synthetic-validation GPT selector surface under the paper-reproduction scorer.
The G28 standard50 lift was directionally real on validation, though smaller:
88.0% on standard50 became 82.6% on full validation.

The frozen-test residual check does not promote the selector as a new
operational default. Test monthly accuracy is essentially tied with the older
builder-gap GPT test run, and pragmatic accuracy is lower. The right conclusion
is not to tune from test rows; it is to treat the frozen-test result as evidence
that target-selection improvements on validation still have a transfer problem,
especially for quantified-rate, cluster, vague/multiple-rate, and unknown
boundary rows.

## Decision

G27 is complete.

Decision scope:

- G24/G28/G27 evidence-first target selection is validated as a useful
  synthetic-validation mechanism arm.
- It is not promoted as the new Gan S0 operational default because frozen-test
  residual behavior is tied with builder-gap GPT on monthly accuracy and worse
  on pragmatic category accuracy.
- Frozen-test rows remain residual-analysis evidence only and must not be used
  for prompt, scorer, loader, bridge, constructor, candidate, or repair tuning.
- Any next selector mechanism should target the validation-visible and
  test-visible residual families with a new preregistered mechanism rather than
  editing G24 post hoc.

## Caveats

- These are synthetic Gan 2026 subset results, not real-letter Gan benchmark
  results.
- The test split is frozen and was used only after G24/G28/G27 validation
  scope was fixed.
- Paper-reproduction metrics and canonical metrics use different special-label
  semantics; both show the same transfer-risk pattern.
- Evidence quote support remains diagnostic and does not prove semantic target
  selection correctness.

# Gan S0 G8 Special-Class Target Selector Report

Status: rejected arm  
Date: 2026-05-29  
Related: `docs/experiments/gan/gan_s0_g7_special_class_target_selector_preregistration_20260528.md`

## Research Question

Can a class-first Gan S0 target selector improve benchmark-facing target
selection for quantified current frequency, seizure-free duration, unknown
frequency, no-reference, and cluster special classes while preserving G4-style
traceability?

## Method

- Dataset/split: Gan 2026 synthetic, `gan_2026_fixed_v1:validation`.
- Gold source:
  `check__Seizure Frequency Number.seizure_frequency_number[0]`.
- Reference policy: `reference[0]` is a difficulty signal, not gold.
- Model/provider: GPT-4.1-mini / OpenAI.
- Program variant: `gan_frequency_s0_special_class_target_selector`.
- Configs:
  `configs/experiments/gan_s0_g8_special_class_target_selector_gpt4_1_mini_smoke25.json`,
  `configs/experiments/gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50.json`.
- Runs:
  `runs/gan_s0_g8_special_class_target_selector_gpt4_1_mini_smoke25_20260528T232759Z`,
  `runs/gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z`.
- Benchmark-facing scorer: `gan2026_paper_reproduction`, repair/range/tolerance
  disabled.
- Diagnostic scorer: `gan_frequency_deterministic_v1`.

No scorer, loader, split, benchmark bridge, candidate-builder, or
prediction-repair behavior changed. The varied factor was target-selection
policy.

## Smoke Result

The smoke run passed the G7 stop-rule gate for traceability:

| Trace field | Count |
| --- | ---: |
| Target semantic class | 25/25 |
| Selected candidate reference | 25/25 |
| Label-construction inputs | 25/25 |
| Adjudication JSON | 25/25 |
| D1 date/event payload | 25/25 |

Smoke metrics were weak, but smoke is compatibility-only: paper monthly,
Purist, Pragmatic, and normalized-label accuracy were all 16/25 (64.0%).
Canonical metrics matched the same 16/25.

## Standard-50 Result

| Scorer view | Monthly | Purist | Pragmatic | Normalized label |
| --- | ---: | ---: | ---: | ---: |
| `gan2026_paper_reproduction` | 37/50 (74.0%) | 39/50 (78.0%) | 42/50 (84.0%) | 35/50 (70.0%) |
| `gan_frequency_deterministic_v1` | 36/50 (72.0%) | 38/50 (76.0%) | 41/50 (82.0%) | 35/50 (70.0%) |

Comparator performance on the same G6 standard-50 records:

| Arm | Paper monthly | Canonical monthly |
| --- | ---: | ---: |
| G8 special-class selector | 37/50 (74.0%) | 36/50 (72.0%) |
| D1 v1.2b schema guard GPT | 40/50 (80.0%) | 42/50 (84.0%) |
| Builder-gap v1 GPT | 41/50 (82.0%) | 42/50 (84.0%) |

## Challenge Overlays

Paper-reproduction monthly accuracy:

| Challenge overlay | G8 | D1 v1.2b | Builder-gap GPT |
| --- | ---: | ---: | ---: |
| Target selection standard | 30/43 (69.8%) | 34/43 (79.1%) | 34/43 (79.1%) |
| Seizure-free versus quantified | 13/21 (61.9%) | 17/21 (81.0%) | 18/21 (85.7%) |
| Unknown/no-reference policy | 6/10 (60.0%) | 9/10 (90.0%) | 10/10 (100.0%) |
| Cluster policy | 19/24 (79.2%) | 19/24 (79.2%) | 21/24 (87.5%) |
| Temporal anchoring | 11/15 (73.3%) | 12/15 (80.0%) | 11/15 (73.3%) |
| Candidate-coverage exact misses in standard50 | 0/4 (0.0%) | 2/4 (50.0%) | 2/4 (50.0%) |

## Failure Read

The standard-50 run had 13 paper-monthly misses. Primary failure classes:

| Primary failure | Count |
| --- | ---: |
| Target selection | 9 |
| Candidate coverage | 4 |

The class-first selector preserved trace fields but did not solve the intended
bottleneck. It still chose seizure-free labels over gold-compatible quantified
labels on records such as `gan_14485`, `gan_15306`, and `gan_14881`; it chose
quantified labels for `unknown` gold cases such as `gan_9566` and `gan_11380`;
and it failed all four standard-50 exact-miss candidate-coverage records.

Target semantic class counts were:

| Target semantic class | Count |
| --- | ---: |
| `frequency_present_quantified` | 29 |
| `seizure_free_duration` | 12 |
| `no_seizure_frequency_reference` | 4 |
| `seizures_referenced_frequency_unclear` | 3 |
| `cluster_spacing_unknown` | 2 |

## Decision

Do not full-validate this arm as tested. It is below D1 by 3 records and below
builder-gap GPT by 4 records under the paper-reproduction monthly scorer on the
G6 standard-50 surface. It also regresses on the motivating
seizure-free-versus-quantified and unknown/no-reference challenge overlays.

This rejects the G8 class-first prompt arm, not the target-selection mechanism
class. The mechanism remains open, but the next attempt should not simply add
more special-class labels to the same prompt shape. It should either compare a
standard-50 candidate-constrained/answer-options selector directly against D1,
or first inspect whether the four standard-50 exact-miss records require a
candidate-inventory challenge-set pass before another selector run.

## Caveats

- The G6 standard-50 surface is challenge-balanced and is not an unbiased
  validation estimate.
- This is synthetic-validation evidence only, not Real(300), Real(150), or
  external Gan benchmark reproduction.
- The canonical scorer remains a diagnostic sensitivity view; paper-facing
  interpretation should lead with `gan2026_paper_reproduction`.
- The result does not change Gan scorer semantics or dataset policy.

# Gan S0 G29 Validation-Residual Selector Results

Status: rejected arm
Date: 2026-05-29
Kanban card: P1 - Gan Validation-First Selector Follow-Up
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Model/provider: GPT-4.1-mini / OpenAI
Program variant: `gan_frequency_s0_validation_residual_family_selector`
Prompt version: `gan_frequency_s0_validation_residual_family_selector_v1_0`
Primary scorer: `gan2026_paper_reproduction`, with repair, range, and
tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1`
Decision scope: arm

## Research Question

Can the G29 validation-residual-family checkpoint reduce G27 validation misses
without changing scorer, loader, split, benchmark bridge, candidate-builder,
`gan.frequency.aggregation_constructor.v1`, gold-label policy, or
prediction-repair semantics?

## Method

G29 adds model-visible residual-family checkpoint fields before the existing
G24/G27 closed-option or constrained-special-label final choice. The final
prediction contract remains unchanged:

- if a closed option is adequate, the final label must be copied from a closed
  option by `option_id`;
- if no option is adequate, the only allowed final labels are `unknown` and
  `no seizure frequency reference`;
- no free-written quantified rates, duration repairs, cluster construction, or
  post-prediction repair are allowed.

Configs:

- `configs/experiments/gan_s0_g29_validation_residual_family_selector_gpt4_1_mini_smoke6.json`
- `configs/experiments/gan_s0_g29_validation_residual_family_selector_gpt4_1_mini_full_validation.json`

Runs:

- Smoke: `runs/gan_s0_g29_validation_residual_family_selector_gpt4_1_mini_smoke6_20260529T175908Z`
- Full validation: `runs/gan_s0_g29_validation_residual_family_selector_gpt4_1_mini_full_validation_20260529T180049Z`

## Smoke Gate

The six-row smoke completed with 6/6 schema-valid predictions and 100% evidence
quote support. All required G29 trace fields were present, and all six final
labels obeyed the closed-option copy or constrained-special-label escape
contract.

Smoke performance was weak: 1/6 paper monthly, 1/6 Purist, and 2/6 Pragmatic.
Because the preregistered smoke gate was trace completeness plus label-contract
validity, not performance, the arm proceeded to full validation.

## Full Validation Results

G29 full validation produced 299/299 valid predictions.

| Arm | Paper monthly | Purist | Pragmatic | Schema valid | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| G27 evidence-first selector | 247/299 (82.6%) | 255/299 (85.3%) | 265/299 (88.6%) | 100.0% | 100.0% |
| G29 residual-family selector | 243/299 (81.3%) | 250/299 (83.6%) | 257/299 (86.0%) | 100.0% | 100.0% |

Paired monthly comparison against G27:

- both correct: 233
- both wrong: 42
- G29 gains: 10
- G29 regressions: 14

By gold-label family:

| Gold family | Rows | G27 correct | G29 correct | Paired change |
| --- | ---: | ---: | ---: | --- |
| quantified_rate | 174 | 142 | 141 | 9 gains / 10 regressions |
| unknown | 35 | 18 | 15 | 0 gains / 3 regressions |
| unknown_cluster | 5 | 4 | 4 | 1 gain / 1 regression |
| cluster | 29 | 28 | 28 | unchanged |
| seizure_free | 45 | 44 | 44 | unchanged |
| no_reference | 11 | 11 | 11 | unchanged |

## Target Residual Families

G29 did not clear its motivating validation-residual families.

| G27 residual family | Rows | G29 correct |
| --- | ---: | ---: |
| all G27 paper-monthly mismatches | 52 | 10 |
| quantified wrong rate/window with quantified G27 prediction | 18 | 6 |
| unknown or unknown-cluster over-called as seizure-free | 11 | 0 |
| quantified rate over-called as seizure-free | 9 | 1 |
| unknown or unknown-cluster over-called as quantified | 6 | 1 |
| cluster / unknown-cluster gold diagnostic stratum | 34 | 32 |

The cluster diagnostic stratum remained strong, and G29 did recover
`gan_10618` from G27's concrete-rate overcall to the correct
`unknown, 4 to 6 per cluster`. That gain was not enough to offset regressions
on unknown and quantified-rate rows.

Notable gains:

- `gan_10618`: `4 to 6 per day` -> `unknown, 4 to 6 per cluster`
- `gan_14655`: seizure-free overcall -> `2 per 2 month`
- `gan_2226`: `5 per week` -> `3 to 10 per 2 week`
- `gan_2262`: `3 per week` -> `7 to 9 per 3 week`

Notable regressions:

- `gan_10542`: `unknown, 2 to 4 per cluster` -> `1 per 3 month`
- `gan_14036`: `unknown` -> `1 per month`
- `gan_14214`, `gan_14271`, `gan_14821`, `gan_14965`, `gan_15306`: quantified
  gold rows regressed to seizure-free labels
- `gan_16772`: `9 per 5 month` -> `11 per 3 month`

## Interpretation

The residual-family checkpoint preserved schema, evidence, and final-label
contract validity, but it did not improve target selection. It lowered monthly,
Purist, and Pragmatic validation metrics versus G27 and created more monthly
regressions than gains.

The arm is therefore rejected as tested. This does not reject residual-family
analysis as a mechanism class, but it does reject this single-pass prompt shape
as a G27 successor. In particular, simply naming the residual family before
closed-option choice did not fix unknown-to-seizure-free errors, and it
introduced new quantified-rate-to-seizure-free regressions.

## Caveats

- This is synthetic validation mechanism evidence, not Real(300), Real(150), or
  published Gan benchmark reproduction.
- Frozen-test rows were not used for prompt wording, candidate policy, scorer
  policy, bridge behavior, or repair changes.
- `reference[0]` remains a secondary difficulty signal only; the gold source is
  `seizure_frequency_number[0]`.
- Direct comparisons above use `gan2026_paper_reproduction`. Canonical Gan
  metrics remain diagnostic.
- The report compares against the stored G27 validation run
  `gan_s0_g27_evidence_first_target_selector_gpt4_1_mini_full_validation_20260529T132143Z`.

## Next Steps

Do not promote G29 or run a frozen-test check for this arm. The next Gan S0 work
should either pause selector prompting and move to another current Kanban pull,
or write a new mechanism card that addresses the observed failure more directly:
unknown/seizure-free competition remained unresolved, and quantified rows still
regressed to seizure-free despite the checkpoint.

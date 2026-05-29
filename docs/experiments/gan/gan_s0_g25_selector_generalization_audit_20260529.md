# Gan S0 G25 Selector Generalization And Sample-Size Audit

Status: current synthesis / generalization-gate audit
Date: 2026-05-29
Kanban card: G25 - Gan Selector Generalization And Sample-Size Audit
Dataset/splits: Gan 2026 synthetic (`gan_2026_fixed_v1:validation` and frozen `gan_2026_fixed_v1:test`)
Primary scorer: `gan2026_paper_reproduction` monthly-frequency match, with repair, range, and tolerance disabled
Diagnostic scorer: `gan_frequency_deterministic_v1`
Model calls: none
Scorer, loader, split, bridge, prompt, model, candidate-builder, constructor, target-selection, and prediction-repair semantics: unchanged

## Research Question

Does `gan_s0_g6_standard50_v1` hide enough generalization behavior that a
selector with lower standard50 performance could still deserve full validation
or frozen-test residual inspection?

## Method

This is a no-model audit over stored artifacts.

Inputs:

- G6 evaluation-surface protocol: `docs/experiments/gan/gan_s0_g6_evaluation_slice_standard_decision_20260528.md`.
- G5 validation rescore pack: `docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.json`.
- G19/G22/G23 standard50 ledgers:
  `docs/experiments/gan/gan_s0_g19_post_g16_error_attribution_audit_20260529.json`,
  `docs/experiments/gan/gan_s0_g22_closed_option_target_selector_report_20260529.json`,
  and `docs/experiments/gan/gan_s0_g23_selector_failure_mechanism_audit_20260529.md`.
- Stored standard50 selector runs:
  `runs/gan_s0_g8_special_class_target_selector_gpt4_1_mini_standard50_20260528T233005Z`,
  `runs/gan_s0_g10_candidate_ranking_target_selector_gpt4_1_mini_standard50_20260529T005458Z`,
  `runs/gan_s0_g15_support_aware_target_selector_gpt4_1_mini_standard50_20260529T013751Z`,
  and `runs/gan_s0_g22_closed_option_target_selector_gpt4_1_mini_standard50_20260529T105421Z`.
- Frozen-test builder-gap runs:
  `runs/test_holdout_gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260527T095116Z`
  and
  `runs/test_holdout_gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260527T095815Z`.

The frozen-test builder-gap predictions were rescored with the paper-compatible
scorer using:

```powershell
uv run python scripts/evaluate_predictions.py --predictions runs\test_holdout_gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260527T095116Z\predictions.json --output $env:TEMP\gan_g25_test_builder_gap_gpt_paper.json --scorer-mode gan2026_paper_reproduction --bootstrap-samples 1000
uv run python scripts/evaluate_predictions.py --predictions runs\test_holdout_gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260527T095815Z\predictions.json --output $env:TEMP\gan_g25_test_builder_gap_qwen_paper.json --scorer-mode gan2026_paper_reproduction --bootstrap-samples 1000
```

Uncertainty treatment:

- Standard50 rows use Wilson 95% intervals for the binomial monthly-match
  rate. These intervals are descriptive because standard50 is a designed
  mechanism slice, not a random iid sample.
- Full-validation and frozen-test rows use the existing percentile-bootstrap
  confidence intervals emitted by the evaluation CLI.
- Same-standard50 arm comparisons use a paired win/loss ledger against
  builder-gap GPT. The paired sign-test p-value is reported only as a
  diagnostic; mechanism decisions still depend on the row-level failure class.

## Results

### Standard50 Aggregate Uncertainty

Each standard50 row is worth 2.0 percentage points. Around the current
baseline level, a 50-row aggregate has an uncertainty band of roughly plus or
minus 10 to 13 points.

| Arm | Scope | Paper monthly | 95% interval | Full-validation paper monthly |
| --- | ---: | ---: | ---: | ---: |
| Builder-gap v1 GPT | 50 | 41/50 (82.0%) | 69.2%-90.2% | 239/299 (79.9%; 75.3%-84.9%) |
| D1 v1.2b schema guard GPT | 50 | 40/50 (80.0%) | 67.0%-88.8% | 229/299 (76.6%; 71.9%-81.3%) |
| G22 closed-option selector | 50 | 39/50 (78.0%) | 64.8%-87.2% | not run |
| G8 class-first selector | 50 | 37/50 (74.0%) | 60.4%-84.1% | not run |
| G10 candidate-ranking selector | 50 | 36/50 (72.0%) | 58.3%-82.5% | not run |
| G15 support-aware selector | 50 | 31/50 (62.0%) | 48.2%-74.1% | not run |

Standard50 slightly overestimated the two full-validation baselines available
on the same validation split:

- Builder-gap GPT: standard50 82.0% versus full-validation paper 79.9%
  (+2.1pp).
- D1 v1.2b: standard50 80.0% versus full-validation paper 76.6% (+3.4pp).

This does not show that standard50 is broken as a mechanism slice. It does show
that one- to three-record differences are not a stable promotion signal.

### Paired Standard50 Evidence

Because all standard50 arms share the same 50 records, paired row movement is
more informative than independent aggregate intervals.

| Arm compared with builder-gap GPT | Arm fixes builder miss | Arm regresses builder hit | Net | Diagnostic sign p |
| --- | ---: | ---: | ---: | ---: |
| D1 v1.2b schema guard GPT | 3 | 4 | -1 | 1.000 |
| G22 closed-option selector | 7 | 9 | -2 | 0.804 |
| G8 class-first selector | 6 | 10 | -4 | 0.454 |
| G10 candidate-ranking selector | 6 | 11 | -5 | 0.332 |
| G15 support-aware selector | 5 | 15 | -10 | 0.041 |

Only G15 is clearly worse by this simple paired diagnostic. G8, G10, and G22
are still rejected as tested, but not because their aggregate standard50 scores
alone prove the mechanisms cannot generalize. They are rejected because their
row ledgers show the wrong mechanism behavior: regressions on the motivating
special-label and seizure-free-versus-quantified slices, plus G17/G22 failures
where exact answer options were available or where unknown labels were absent
from the option surface.

### Validation-To-Test Drift

The larger risk is not standard50 versus validation. It is validation versus
frozen test for the current builder-gap surface.

| Arm | Validation paper monthly | Frozen-test paper monthly | Change |
| --- | ---: | ---: | ---: |
| Builder-gap v1 GPT | 239/299 (79.9%; 75.3%-84.9%) | 194/301 (64.5%; 59.5%-69.8%) | -15.5pp |
| Builder-gap v1 Qwen | 210/299 (70.2%; 65.2%-75.3%) | 178/301 (59.1%; 53.5%-64.8%) | -11.1pp |

D1 v1.2b has a full-validation paper result (229/299, 76.6%) but no stored
frozen-test run. The G8/G10/G15/G22 selector arms have standard50 runs only.

This means future selector design should not use frozen test to choose wording,
candidate policy, special-label escapes, or construction policy. Test evidence
can only be a residual-analysis check after the mechanism and full-validation
criteria are frozen.

### Gate Power Check

The current "43/50" lift threshold is high specificity but low power. Under a
simple binomial approximation:

| Assumed true monthly rate | P(score >= 43/50) | P(score <= 39/50) |
| ---: | ---: | ---: |
| 78% | 11.3% | 55.5% |
| 80% | 19.0% | 41.6% |
| 85% | 51.9% | 12.0% |
| 88% | 75.3% | 3.2% |

So a genuinely near-80% arm can easily score 39/50, and a genuinely 85% arm
will still miss 43/50 almost half the time. A 43/50 gate is useful as a cheap
"obvious win" trigger, but it should not be the only path to full validation.

## Interpretation

Standard50 is still useful as the default mechanism-comparison surface because
it concentrates the G19/G17/G21/G22 failure rows and supports row-level
before/after ledgers. It should not be treated as a promotion surface.

The existing rejected selector arms remain rejected:

- G8, G10, and G15 fail their mechanism goals and regress on targeted overlays.
- G22 is closer in aggregate, but it regresses on the G17 special-label slice
  and fails the closed-option interface hypothesis from G23.

The important policy change is for future arms: aggregate standard50 deltas
should route inspection and full-validation decisions, not replace them.

## Proposed Generalization Gate For Future Selectors

Use this gate before spending full-validation, Qwen, or frozen-test budget on a
new Gan selector:

1. **Always preserve fixed controls.** Scorer, loader, split, benchmark bridge,
   candidate-builder, G21 constructor, and prediction-repair semantics stay
   fixed unless a separate policy card changes them.
2. **Require trace completeness.** The selector must emit the preregistered
   evidence-first target narration, special-label escape state, selected option
   or constructed final label, and row-level reason fields for all standard50
   records before aggregate scoring is interpreted.
3. **Use 43/50 as an obvious-pass trigger only.** If an arm reaches at least
   43/50 paper monthly on standard50 and does not regress the motivating
   overlays, run full validation.
4. **Allow a near-baseline exception at 39-42/50.** A 39-42/50 arm may still
   run full validation only if its paired ledger shows a preregistered
   mechanism gain: more fixes than regressions on the targeted G19/G17/G21/G22
   rows, no more than one new G17 special-label regression, and no unaccounted
   schema/evidence failures.
5. **Block ordinary full validation below 39/50.** A lower arm needs an
   explicit generalization exception written before model calls, such as a
   named challenge set that standard50 intentionally undersamples. The
   exception must state which full-validation strata are expected to improve
   and what regressions would reject the arm.
6. **Do not use frozen test for selection.** Test residual inspection is
   allowed only after a full-validation result is frozen and the test question
   is diagnostic: transfer behavior, residual-family shift, or matched
   model-effect comparison. Test rows must not change prompts, selector
   wording, candidate policy, scorer policy, or repair policy.
7. **Qwen replication is downstream of the mechanism, not a search loop.**
   A Qwen run should test a specific model-effect hypothesis from a frozen GPT
   row ledger, with the same scorer, loader, split, bridge, candidate-builder,
   constructor, and repair controls.

Applied retrospectively, this gate keeps G22 rejected despite its 39/50 score
because it regressed five G17 builder-gap rows (`gan_9566`, `gan_5974`,
`gan_6607`, `gan_14002`, `gan_11380`) and did not pass the special-label
escape requirement that G23 now motivates.

## Decision

G25 is complete as a no-model generalization and sample-size audit.

Decision scope:

- `gan_s0_g6_standard50_v1` remains the default mechanism-comparison slice.
- Standard50 aggregate score is no longer sufficient by itself to authorize or
  reject full validation for near-baseline selector arms.
- G24 should preregister the next selector around evidence-first target
  narration, constrained special-label escape, and construction-aware option
  priority, using the gate above for run-scope decisions.
- G26 and G27 remain blocked until G24 freezes the selector mechanism and a
  future standard50 run satisfies either the obvious-pass gate or a
  preregistered near-baseline exception.

## Caveats

- Standard50 intervals are descriptive because G6 selected a mechanism slice,
  not an iid random sample.
- The frozen-test evidence is available only for builder-gap GPT and Qwen in
  this audit. It demonstrates transfer risk for the current operational
  surface, not selector generalization.
- D1 v1.2b and the G8/G10/G15/G22 selectors do not have stored frozen-test
  outputs.
- The paper-compatible test rescores were produced from stored predictions only;
  no model calls or artifact mutations were made.
- External Gan benchmark claims remain blocked without Real(300)/Real(150)
  access or an explicitly synthetic-only comparison protocol.

## Next Step

Pull G24: preregister the evidence-first selector interface. The preregistration
should leave model-call scope conditional on the G25 gate and should explicitly
name the G17/G21/G22/G23 row ledger it expects to improve.

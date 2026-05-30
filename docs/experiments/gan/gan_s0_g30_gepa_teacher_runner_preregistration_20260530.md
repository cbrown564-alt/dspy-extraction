# Gan S0 G30 GEPA Teacher-Runner Preregistration

Status: active guidance
Date: 2026-05-30

## Hypothesis

GEPA deserves one hosted teacher-runner test over the current strongest Gan S0
target-selection architecture before the optimizer mechanism is judged again:
GPT-4.1-mini should remain the prediction runner, while a stronger hosted
GPT-5-family model supplies reflection feedback over stage-attributed Gan S0
errors.

## Fixed Controls

- Dataset and split: `gan_2026`, `gan_2026_fixed_v1:validation`.
- Scorer: primary `gan2026_paper_reproduction`; canonical Gan metrics are
  diagnostic only.
- Program substrate: G27/G24 evidence-first target selector with deterministic
  temporal candidates, G21 constructed answer options, closed-option copy, and
  constrained special-label escape.
- Gold policy: `seizure_frequency_number[0]` remains the gold label; `reference`
  is a secondary difficulty signal only.
- Frozen-test rows: residual-analysis only, never prompt wording, candidate,
  scorer, bridge, repair, or policy tuning input.

## Arms

1. Matched control:
   `configs/experiments/gan_s0_g30_evidence_first_control_gpt4_1_mini_smoke6.json`.
2. GEPA evidence-first teacher-runner smoke:
   `configs/experiments/gan_s0_g30_evidence_first_gepa_gpt4_1_mini_gpt5_5_reflection_smoke6.json`.
3. Standard50 GEPA arm, only after the smoke gate clears.
4. Distilled compact instruction arm with no compile, only if GEPA produces a
   compact, inspectable instruction delta.

## Gates

- Dry-run both smoke configs before live calls.
- Smoke may proceed only if config loading proves prediction and reflection LMs
  can differ.
- Standard50 promotion gate: at least 43/50 paper monthly, or a preregistered
  row-ledger exception with no special-label regression.
- Full-validation promotion gate: beat G27's 247/299 paper monthly, or justify a
  narrower arm-level decision.
- Reject policy-wall wins if instruction length grows substantially without
  benchmark-facing lift.

## Interpretation

This card tests one GEPA arm under better teacher-runner conditions. A failed
G30 arm rejects the arm as tested; it does not close GEPA as a mechanism unless
a later mechanism review compares multiple GEPA positions or prompts.

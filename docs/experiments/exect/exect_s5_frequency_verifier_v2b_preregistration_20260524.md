# ExECT S5 Frequency Verifier v2b Preregistration

Date: 2026-05-24
Parent: v2 rejection — [exect_s5_frequency_verifier_v2_cap25_rejection_20260524.md](../../archive/experiments/exect/model_comparison_diagnostics/exect_s5_frequency_verifier_v2_cap25_rejection_20260524.md)
Decision scope: arm (isolated factor)

## Hypothesis

Applying **v2 verifier temporal/scope rules only** on the unchanged **v1.2 extractor** (no v1.3 qualitative evidence gate, no `strict_qualitative` deterministic guard) will reduce precision-dominated frequency false positives without the −16.0pp recall collapse observed in combined v2.

## Isolated Factor

| Component | v1 (baseline) | v2 (rejected) | **v2b (this arm)** |
| --- | --- | --- | --- |
| Extractor prompt | v1.2 | v1.3 | **v1.2** |
| Verifier policy | v1 (rules 1–6) | v2 (rules 1–9) | **v2 (rules 1–9)** |
| Strict qualitative guard | off | on | **off** |

## Fixed Controls

Same as v1 paper freeze: high-recall pre-vocab, AM guard, `gpt-4.1-mini`, cap-25 first.

## Config

`configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_cap25_gpt4_1_mini.json`

## Cap-25 Gate

Compare vs v1 cap-25 (`71.7%` freq F1, `76.0%` recall):

- Primary: freq F1 ≥ v1 **or** precision +≥3pp with recall drop ≤3pp
- Guard families within −2pp
- Recall floor: ≥ v1 −3pp

## Stop Rules

Same as v2 prereg; reject if recall drops >3pp without compensating precision.

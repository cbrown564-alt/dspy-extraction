# ExECT S5 Frequency Verifier v2b Full-Validation Review

Date: 2026-05-24
Decision scope: **operational** (promoted to D1)
Status: **Promoted**

See [exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md](exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md) for gate check and artifact list.

## Runs

| Arm | Run ID |
| --- | --- |
| v2b cap-25 (gate) | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_cap25_gpt4_1_mini_20260524T211133Z` |
| v2b full validation | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` |

## Full Validation vs Paper-Frozen v1

| Metric | v1 (paper freeze) | v2b full | Delta |
| --- | ---: | ---: | ---: |
| seizure_frequency F1 | 72.3% | **73.9%** | +1.6pp |
| seizure_frequency precision | 66.7% | **69.4%** | +2.7pp |
| seizure_frequency recall | 79.1% | **79.1%** | ~0 |
| diagnosis F1 | 90.0% | 90.0% | 0 |
| seizure_type F1 | 84.0% | 84.0% | 0 |
| annotated_medication F1 | 88.7% | 88.7% | 0 |
| investigation F1 | 96.7% | 96.7% | 0 |
| pooled micro F1 | 85.5% | **85.8%** | +0.3pp |

## Interpretation

v2b isolates v2 temporal/scope verifier rules on the unchanged v1.2 extractor. Full validation shows a **modest but scorer-safe frequency gain** (+1.6pp F1) with **recall held** and **no guard-family regression**. Combined v2 remains rejected; the recall collapse was attributable to v1.3 abstention + strict qualitative guard, not the v2 verifier rules.

Gain is smaller than the original v1 verifier promotion (+12.1pp) but directionally consistent and factor-isolated.

## Recommendation

**`hold_for_promotion_review`**

Material enough to consider superseding paper freeze if review accepts +1.6pp freq F1 as worth the second-pass verifier complexity. Not auto-promoted — update D1 only after explicit promotion sign-off.

## Caveats

- Partial S5 surface; not Table 1 reproduction.
- Scorer semantics unchanged.
- Cap-25 was optimistic; full-val delta (+1.6pp) is the operative estimate.

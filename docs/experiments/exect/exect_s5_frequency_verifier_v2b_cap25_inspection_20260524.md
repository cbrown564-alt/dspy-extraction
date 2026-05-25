# ExECT S5 Frequency Verifier v2b Cap-25 Inspection

Date: 2026-05-24
Decision scope: **arm**
Status: **Hold — cap-25 gate passed; full validation recommended**

## Run

| Field | Value |
| --- | --- |
| Run ID | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_cap25_gpt4_1_mini_20260524T211133Z` |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_cap25_gpt4_1_mini.json` |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` |
| Isolated factor | v2 verifier rules 7–9 only; v1.2 extractor; no strict qualitative guard |

## Gate Comparison

| Metric | v1 cap-25 | v2 (rejected) | **v2b** | v2b vs v1 | Gate |
| --- | ---: | ---: | ---: | ---: | --- |
| seizure_frequency F1 | 71.7% | 68.2% | **76.4%** | +4.7pp | **Pass** |
| seizure_frequency precision | 67.9% | 78.9% | **70.0%** | +2.1pp | Pass |
| seizure_frequency recall | 76.0% | 60.0% | **84.0%** | +8.0pp | **Pass** |
| diagnosis F1 | 93.0% | 93.0% | 93.0% | 0 | Pass |
| seizure_type F1 | 92.5% | 88.2% | **92.5%** | 0 | Pass |
| annotated_medication F1 | 87.9% | 84.8% | **87.9%** | 0 | Pass |
| investigation F1 | 93.8% | 93.8% | 93.8% | 0 | Pass |
| micro F1 | 87.4% | 85.4% | **88.2%** | +0.8pp | Pass |

## Interpretation

Factor isolation confirms the v2 recall collapse was driven by **v1.3 extractor abstention + strict qualitative guard**, not the v2 temporal/scope verifier rules themselves. v2b improves frequency F1 (+4.7pp) and recall (+8.0pp) vs v1 cap-25 while restoring guard-family parity.

Combined v2 remains **rejected**. Paper freeze stays on v1 until full validation confirms v2b on 40 records.

## Recommendation

**`proceed_to_full_validation`**

Create `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini.json` and run full validation before any operational-default promotion.

## Caveats

- Cap-25 only; systematically optimistic vs full validation.
- S5 partial surface; scorer unchanged.
- Evidence support 93.8% (diagnostic).

# ExECT S5 Frequency Verifier v2 Cap-25 Rejection

Date: 2026-05-24
Decision scope: **arm**
Status: **Rejected** at cap-25 gate

## Run

| Field | Value |
| --- | --- |
| Run ID | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2_cap25_gpt4_1_mini_20260524T205934Z` |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2_cap25_gpt4_1_mini.json` |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2` |
| Split | `exectv2_fixed_v1:validation` cap-25 |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |

## Gate Comparison vs v1 Cap-25 Baseline

Baseline source: repaired v1 run `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T194925Z` (A2R review).

| Metric | v1 cap-25 | v2 cap-25 | Delta | Gate |
| --- | ---: | ---: | ---: | --- |
| seizure_frequency F1 | 71.7% | **68.2%** | −3.5pp | Fail |
| seizure_frequency precision | 67.9% | **78.9%** | +11.0pp | Pass (precision arm) |
| seizure_frequency recall | 76.0% | **60.0%** | −16.0pp | **Fail** (>3pp) |
| diagnosis F1 | 93.0% | 93.0% | 0 | Pass |
| seizure_type F1 | 92.5% | 88.2% | −4.3pp | Fail |
| annotated_medication F1 | 87.9% | 84.8% | −3.1pp | Fail |
| investigation F1 | 93.8% | 93.8% | 0 | Pass |
| micro F1 | 87.4% | 85.4% | −2.0pp | Borderline |

## Interpretation

v2 achieved the intended **precision lift** on seizure frequency (+11.0pp) but at an unacceptable **recall cost** (−16.0pp), repeating the early A2 failure mode rather than improving on the paper-frozen v1 stack. The strict qualitative guard and v1.3 abstention policy appear to over-prune true labels (notably `frequency increased`, `infrequent`, zero-rate windows).

Representative recall misses from `errors.json`:

| Doc | FN labels | Notes |
| --- | --- | --- |
| EA0008 | `frequency increased` | Qualitative gate / evidence omission |
| EA0048 | `0 per 3 week` | Zero-rate dropped |
| EA0050 | `infrequent`, `frequency decreased` | Over-abstention |
| EA0059 | `infrequent` | Recall guard target still missed |
| EA0069 | `frequency increased` | Temporal reconciliation still failing |
| EA0098 | `frequency increased`, `seizure free since 2019` | Temporal anchor policy too aggressive |
| EA0125 | `frequency increased` | Missed despite note support |

Guard-family regression on seizure_type (−4.3pp) and annotated_medication (−3.1pp) suggests collateral extractor prompt effects beyond frequency, not just verifier pruning.

## Decision

**Reject v2 arm** at cap-25. Do not run full validation. Paper-frozen operational default remains v1 (`72.3%` full-validation freq F1).

## Next Options (Not Implemented)

1. Relax `strict_qualitative` deterministic guard — require note-level markers, not evidence-quote markers only.
2. Split arms: v2 verifier rules without v1.3 extractor prompt change (isolate factor).
3. Targeted rule tuning on rules 7–9 only, without strict qualitative guard.

## Caveats

- Cap-25 only; not comparable to full-validation 72.3% headline.
- S5 partial surface; not Table 1 reproduction.
- Scorer semantics unchanged.

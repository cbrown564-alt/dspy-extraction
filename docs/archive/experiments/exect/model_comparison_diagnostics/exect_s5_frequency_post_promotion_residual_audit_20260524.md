# ExECT S5 Frequency Post-Promotion Residual Audit

Date: 2026-05-24
Kanban card: S5 frequency residual iteration (post-freeze)
Status: Source-backed residual taxonomy for v2 arm
Decision scope: residual taxonomy for next verifier/policy tuning

## Primary Run (Paper-Frozen Baseline)

| Field | Value |
| --- | --- |
| Run ID | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z` |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini.json` |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1` |
| Split | `exectv2_fixed_v1:validation` / 40 records |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |

## Headline Metrics (Promoted Stack)

| Metric | Pre-verifier (AM guard) | Promoted (v1 + A3) | Delta |
| --- | ---: | ---: | ---: |
| seizure_frequency F1 | 60.2% | **72.3%** | +12.1pp |
| seizure_frequency precision | 46.3% | **66.7%** | +20.4pp |
| seizure_frequency recall | 86.0% | **79.1%** | −6.9pp |
| pooled micro F1 | 81.4% | **85.5%** | +4.1pp |

The verifier + A3 stack materially improved frequency F1 but recall remains below the pre-verifier high-recall baseline. Residual errors are still precision-dominated.

## Remaining Residual Categories (Mapped from A1)

Categories overlap; counts describe documents from the pre-verifier A1 audit still relevant at 72.3% F1.

| Category | A1 docs | v2 target mechanism |
| --- | ---: | --- |
| Qualitative over-emission | 17 | v1.3 extractor qualitative evidence gate + v2 verifier rule 8 + strict qualitative guard |
| Temporal/current-scope mismatch | 7 | v2 verifier rules 7 and 9 |
| Evidence mismatch / candidate echo | 12 | Existing v1 guards + v1.3 no-candidate-echo prompt |
| Multi-type or range normalization | 6 | Out of scope for v2 (no scorer/bridge change) |
| Gold-empty clinical-frequency | 10 | Caveats only — not encoded as benchmark truth |
| Gold-policy ambiguity | 9 | Caveats only |

## v2 Arm Focus Documents

| Doc | Residual | v2 mechanism |
| --- | --- | --- |
| EA0008 | FP `infrequent` | Qualitative evidence gate |
| EA0053 | FP `infrequent` | Qualitative evidence gate |
| EA0131 | FP `infrequent` | Qualitative evidence gate |
| EA0170 | FP `frequency same` | Qualitative evidence gate |
| EA0174 | FP rate + candidate echo | Qualitative gate + existing candidate-echo guard |
| EA0029 | FP `frequency decreased` from med control | Existing med-control guard + prompt |
| EA0069 | FP `seizure free` vs current weekly | Temporal scope rule 7 |
| EA0142 | FP historical rate + current free | Temporal scope rule 7 |
| EA0098 | FP quantified from last-seizure anchor | Temporal scope rule 9 |
| EA0059 | FN `infrequent` | Recall guard — explicit infrequent wording must pass |
| EA0173 | FN `seizure free` | v1 A3 rules retained in v2 |

## Recommended Next Pull

1. Run cap-25 gate: `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2_cap25_gpt4_1_mini.json`
2. Compare vs paper-frozen v1 cap-25 and full-validation baselines
3. Full validation only if cap-25 clears: frequency F1 ≥ v1 cap-25 or precision +≥3pp with recall drop ≤3pp; guard families within −2pp

## Validation

- Cross-checked promotion metrics from [exect_s5_frequency_verifier_full_validation_promotion_review_20260524.md](exect_s5_frequency_verifier_full_validation_promotion_review_20260524.md)
- Mapped A1 per-document residuals from [exect_s5_frequency_residual_audit_20260524.md](exect_s5_frequency_residual_audit_20260524.md)

Scorer semantics changed: no.

# Gan S0 Verify-Repair v2 Full Validation (2026-05-19)

## Purpose

Full fixed-validation run (299 records) for `gan_frequency_s0_direct_verify_repair` with prompt `gan_frequency_s0_direct_verify_repair_v2`, compared against the established synthesis-backed BootstrapFewShot baseline and the cap-25 v2 gate.

## Artifacts

- **Verify-repair v2 full**: `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z`
- **Config**: `configs/experiments/gan_s0_verify_repair_full_validation_gpt4_1_mini.json`
- **Cap-25 v2 gate**: `docs/experiments/gan/gan_s0_verify_repair_cap25_v2_inspection_20260519.md`
- **Synthesis baseline** (documented): `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` (metrics from kanban / prior error-read)

## Headline Metrics (299 validation records)

| Metric | Synthesis BootstrapFewShot | Verify-Repair v2 | Delta (v2 − synthesis) |
|--------|---------------------------|------------------|------------------------|
| Schema validity | 97.3% | **96.7%** | −0.6 pp |
| Normalized-label exact | 51.5% | **52.9%** | **+1.4 pp** |
| Monthly-frequency accuracy | 62.9% | **65.4%** | **+2.5 pp** |
| Purist category accuracy | 70.1% | **72.7%** | **+2.6 pp** |
| Pragmatic category accuracy | 73.9% | **79.2%** | **+5.3 pp** |
| Evidence quote support | 89.9% | **92.7%** | **+2.8 pp** |
| Invalid predictions | 8 | 10 | +2 |

Scorer: `gan_frequency_deterministic_v1` unchanged. Synthesis baseline figures are from the prior full-validation artifact documented in `docs/planning/kanban_plan.md`.

## Verifier Behavior (full split)

| Decision | Count | Share |
|----------|------:|------:|
| confirm | 242 | 81.0% |
| repair | 53 | 17.7% |
| abstain | 4 | 1.3% |

Abstention rate is low (4/299). The verifier most often confirms the direct extractor output rather than over-repairing to `unknown`.

## Runtime and Cost

- Prediction duration: **840.1 s** (~14 min total)
- **2.81 s/record** (two model calls per record: extract + verify)
- Token usage (DSPy history aggregate): 849,779 prompt + 40,270 completion = 890,049 total
- Compare synthesis full-validation: single-pass + BootstrapFewShot compile overhead (not re-run here)

## Error Profile (diagnostic)

From `metrics.json` error counts on valid+invalid predictions:

- `normalization.label_mismatch`: 136
- `normalization.monthly_frequency_mismatch`: 100
- `classification.purist_category_mismatch`: 79
- `classification.pragmatic_category_mismatch`: 60
- `evidence.unsupported_quote`: 20 (vs synthesis full-validation ~30 unsupported at 89.9% support)
- `normalization.invalid_label`: 6
- `abstention.predicted_abstention`: 4

Remaining failures are predominantly semantic/temporal (label and monthly-frequency mismatch), not evidence-grounding at scale.

## Conclusions

1. **Verify-repair v2 scales**: cap-25 evidence gains (91.3% support) largely hold at full validation (**92.7%** vs synthesis **89.9%**).
2. **Label metrics improve vs synthesis** on this split: normalized exact (+1.4 pp), monthly (+2.5 pp), Purist (+2.6 pp), Pragmatic (+5.3 pp) — unexpected for a zero-shot direct+verify path vs few-shot synthesis, and worth spot-checking before strong claims.
3. **Schema validity** is slightly below synthesis (96.7% vs 97.3%; 10 invalid vs 8). Invalid labels remain a small tail (`invalid_label` count 6).
4. **Cost**: ~2× latency and API calls vs direct-only; feasible for validation but not for tight interactive loops.

## Recommendations

- Treat verify-repair v2 as a **credible alternative** to synthesis BootstrapFewShot for Gan S0 on GPT 4.1-mini, pending error-read on whether label gains concentrate on repair wins or extractor luck.
- Run a matched **direct-only full validation** with the same guardrails prompt if a strict apples-to-apples ablation is needed (not run in this cycle).
- Do **not** promote as default local-Qwen path without a Qwen-paced cap/full probe.
- Next: targeted error-read on repair decisions (53 records) and invalid-label cases (10 records).

## Validation

- Config test: `test_verify_repair_full_validation_config_has_no_cap`
- Dry-run: 299 records, no optimizer
- Full run completed with standard artifact layout

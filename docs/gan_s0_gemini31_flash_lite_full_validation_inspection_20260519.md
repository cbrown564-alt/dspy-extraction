# Gan S0 Gemini 3.1 Flash-Lite Direct Full-Validation Inspection (2026-05-19)

## Purpose

Confirm whether Gemini 3.1 Flash-Lite direct extraction preserves cap-25 label metrics and schema validity at 299-record scale, and compare against the GPT 4.1-mini verify-repair v2 hosted quality anchor.

## Artifacts

- Gemini direct full validation (this run): `runs/gan_s0_direct_full_validation_gemini31_flash_lite_20260519T101710Z`
- Config: `configs/experiments/gan_s0_direct_full_validation_gemini31_flash_lite.json`

Anchors (unchanged `gan_frequency_deterministic_v1` scorer):

- Gemini direct cap-25: `runs/gan_s0_direct_cap25_gemini31_flash_lite_20260519T100621Z`
- Gemini verify-repair cap-25: `runs/gan_s0_verify_repair_cap25_gemini31_flash_lite_20260519T101555Z`
- GPT verify-repair v2 full validation: `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z`
- Synthesis BootstrapFewShot full validation: `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z`

## Full-Validation Results (299 records)

| Variant | Pred (s/rec) | Schema validity | Norm exact | Monthly | Purist | Pragmatic | Evidence support |
|---------|-------------:|----------------:|-----------:|--------:|-------:|----------:|-----------------:|
| Gemini direct | **0.59** | **97.3%** | 50.5% | 63.9% | 71.8% | **81.4%** | 84.9% |
| GPT verify-repair v2 | ~2.81 | 96.7% | **52.9%** | **65.4%** | **72.7%** | 79.2% | **92.7%** |
| Synthesis BootstrapFewShot | — | 97.3% | 51.5% | 62.9% | 70.1% | 73.9% | 89.9% |

Cap-25 Gemini direct (for scale check): schema 92.0%, monthly 52.2%, Purist 56.5%, evidence 86.4%.

Token usage (Gemini full validation): 379,449 total (367,173 prompt + 12,276 completion); 274 history entries on 299 records.

## Interpretation

1. **Label metrics are competitive at scale.** Monthly (63.9%) and Purist (71.8%) sit between synthesis baseline (62.9%/70.1%) and GPT verify-repair v2 (65.4%/72.7%). Pragmatic (81.4%) beats both anchors. Normalized exact (50.5%) is slightly below GPT verify-repair (52.9%) and synthesis (51.5%).

2. **Schema validity holds.** 97.3% matches synthesis baseline and exceeds cap-25 (92.0%), suggesting cap-25 was a noisy slice rather than a systematic Gemini weakness.

3. **Evidence support remains the blocker.** 84.9% full-validation evidence trails GPT verify-repair v2 (92.7%, −7.8 pp) and synthesis (89.9%, −5.0 pp). This confirms the cap-25 evidence gap (86.4%) is not an artifact of the small slice.

4. **Latency is strongly favorable.** ~0.59 s/record (~3 min total) vs ~2.81 s/record (~14 min) for GPT verify-repair v2 on the same split.

5. **Not a primary-model swap.** Gemini direct wins on speed and Pragmatic category but loses on evidence support and slightly on monthly/Purist/normalized exact vs the hosted anchor. Billing was not measured.

## Promotion Gate

| Criterion | Met? |
|-----------|------|
| Schema validity ≥ 95% | Yes (97.3%) |
| Evidence support ≥ GPT verify-repair v2 | No (84.9% vs 92.7%) |
| Monthly/Purist competitive with GPT anchor | Close (monthly −1.5 pp; Purist −0.9 pp) |
| Full-scale behavior recorded | Yes |

**Decision:** Gemini 3.1 Flash-Lite direct is a viable **cost/latency candidate** for label-metric exploration but **does not replace** GPT 4.1-mini verify-repair v2 as the hosted quality anchor. If evidence support must improve on Gemini, prefer targeted quote-policy or artifact-bridge work over scaling Gemini verify-repair (cap-25 showed cluster-stripping regressions).

## Validation

- `uv run --extra dev pytest tests/test_experiment_configs.py -k gemini31_flash_lite`
- Dry-run and full validation: `configs/experiments/gan_s0_direct_full_validation_gemini31_flash_lite.json`

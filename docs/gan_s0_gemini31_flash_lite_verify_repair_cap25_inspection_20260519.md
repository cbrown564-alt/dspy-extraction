# Gan S0 Gemini 3.1 Flash-Lite Verify-Repair Cap-25 Inspection (2026-05-19)

## Purpose

Test whether Gemini 3.1 Flash-Lite verify-repair v2 closes the evidence-support gap from the matched direct cap-25 run while preserving monthly/Purist label gains versus GPT 4.1-mini verify-repair v2.

## Artifacts

- Gemini verify-repair v2 (this run): `runs/gan_s0_verify_repair_cap25_gemini31_flash_lite_20260519T101555Z`
- Config: `configs/experiments/gan_s0_verify_repair_cap25_gemini31_flash_lite.json`

Anchors (same cap, unchanged `gan_frequency_deterministic_v1` scorer):

- Gemini direct: `runs/gan_s0_direct_cap25_gemini31_flash_lite_20260519T100621Z`
- GPT verify-repair v2: `runs/gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T084511Z`
- GPT verify-repair v2 full validation (299 records): `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z`

## Cap-25 Results (valid predictions only for label metrics)

| Variant | Pred (s/rec) | Schema validity | Norm exact | Monthly | Purist | Pragmatic | Evidence support |
|---------|-------------:|----------------:|-----------:|--------:|-------:|----------:|-----------------:|
| Gemini verify-repair v2 | **0.86** | 84.0% | **38.1%** | **52.4%** | 52.4% | 71.4% | **95.0%** |
| Gemini direct | 0.61 | **92.0%** | 34.8% | 52.2% | **56.5%** | **73.9%** | 86.4% |
| GPT verify-repair v2 | ~1.95 | **92.0%** | 26.1% | 34.8% | 47.8% | 69.6% | 91.3% |

Token usage (Gemini verify-repair): 51,894 total (49,431 prompt + 2,463 completion); 25 history entries on 25 records (~2× direct token load, consistent with two-stage pipeline).

## Interpretation

1. **Evidence support clears the gap.** At 95.0%, Gemini verify-repair beats both Gemini direct (86.4%, +8.6 pp) and GPT verify-repair v2 (91.3%, +3.7 pp). Unsupported-quote count drops from 3 (direct) to 1; the verifier repairs wrapper quotes and preserves note-contained spans on most records.

2. **Schema validity regresses.** Validity falls to 84.0% (4 invalid) from 92.0% (2 invalid) on Gemini direct. New invalid labels come from verifier **repair** decisions that strip cluster structure (`gan_10434` → `2 to 3 per cluster`, `gan_10618` → `4 to 6 per cluster`). These are semantic repair failures, not surface-form issues.

3. **Monthly frequency is preserved.** 52.4% ties Gemini direct (52.2%) and remains well above GPT verify-repair v2 (34.8%).

4. **Purist and Pragmatic slip slightly.** Purist drops 4.1 pp vs Gemini direct (56.5% → 52.4%); Pragmatic drops 2.5 pp (73.9% → 71.4%). Normalized exact improves +3.3 pp vs direct.

5. **Latency stays favorable.** ~0.86 s/record is faster than GPT verify-repair (~1.95 s/record) with roughly double the token use of Gemini direct.

6. **Not a primary-model decision.** This is still a 25-record synthetic validation cap. Billing was not measured. Schema-validity regression and Purist slip block promotion despite the evidence win.

## Promotion Gate

| Criterion | Met? |
|-----------|------|
| Schema validity ≥ 90% | **No** (84.0%) |
| Evidence support ≥ GPT verify-repair v2 | **Yes** (95.0% vs 91.3%) |
| Monthly/Purist ≥ GPT verify-repair v2 | **Yes** (monthly +17.6 pp; Purist +4.6 pp) |
| Monthly/Purist ≥ Gemini direct | Monthly yes; Purist **no** (−4.1 pp) |
| Matched-cap comparison recorded | Yes |

**Decision:** Gemini verify-repair v2 **partially** meets the kanban hypothesis — evidence support is fixed, monthly gains hold vs GPT, but schema validity and Purist regress vs Gemini direct. **Do not** promote Gemini verify-repair to full validation yet. **Next hosted step:** run Gemini **direct** full validation (299 records) to confirm label metrics and schema validity at scale; keep GPT verify-repair v2 as the hosted quality anchor until Gemini direct full-validation evidence is recorded.

## Validation

- `uv run --extra dev pytest tests/test_experiment_configs.py -k gemini31_flash_lite`
- Dry-run and capped run: `configs/experiments/gan_s0_verify_repair_cap25_gemini31_flash_lite.json`

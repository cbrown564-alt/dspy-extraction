# Gan S0 Gemini 3.1 Flash-Lite Cap-25 Inspection (2026-05-19)

## Purpose

First matched 25-record quality comparison for `gemini-3.1-flash-lite` direct Gan S0 extraction against GPT 4.1-mini verify-repair v2 and direct-path ladder anchors on the fixed validation slice.

## Artifacts

- Gemini direct (this run): `runs/gan_s0_direct_cap25_gemini31_flash_lite_20260519T100621Z`
- Config: `configs/experiments/gan_s0_direct_cap25_gemini31_flash_lite.json`

Anchors (same cap, unchanged `gan_frequency_deterministic_v1` scorer):

- Verify-repair v2: `runs/gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T084511Z`
- Synthesis LabeledFewShot: `runs/gan_s0_ladder_labeled_fewshot_cap25_gpt4_1_mini_20260519T091940Z`
- Full-validation verify-repair v2 (299 records): `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z`

## Cap-25 Results (valid predictions only for label metrics)

| Variant | Pred (s/rec) | Schema validity | Norm exact | Monthly | Purist | Pragmatic | Evidence support |
|---------|-------------:|----------------:|-----------:|--------:|-------:|----------:|-----------------:|
| Gemini 3.1 Flash-Lite direct | **0.61** | 92.0% | **34.8%** | **52.2%** | **56.5%** | **73.9%** | 86.4% |
| Verify-repair v2 (GPT 4.1-mini) | ~2.8 | 92.0% | 26.1% | 34.8% | 47.8% | 69.6% | **91.3%** |
| LabeledFewShot direct (GPT 4.1-mini) | 1.32 | 92.0% | **34.8%** | 43.5% | **56.5%** | 69.6% | 100.0% |

Token usage (Gemini): 33,652 total (32,538 prompt + 1,114 completion); 24 history entries on 25 records.

## Interpretation

1. **Label metrics beat verify-repair v2 on this cap.** Gemini direct reaches the highest monthly-frequency accuracy (+17.4 pp) and ties LabeledFewShot on normalized exact and Purist. Pragmatic is also highest (+4.3 pp vs verify-repair).

2. **Evidence support is the main gap.** At 86.4%, Gemini trails verify-repair v2 (91.3%) and LabeledFewShot (100%). Dominant failures are unsupported quotes with extra wrapper punctuation (e.g. leading/trailing single quotes on otherwise-close spans).

3. **Schema validity matches the cap anchor.** Both Gemini and verify-repair v2 sit at 92.0% with the same two invalid predictions (`gan_10052` incomplete cluster, `gan_4702` forbidden `per hour`).

4. **Latency is favorable.** ~0.61 s/record is faster than GPT 4.1-mini verify-repair (~2.8 s/record) and comparable to direct GPT paths.

5. **Not a primary-model decision yet.** This is a 25-record synthetic validation cap. Cost/billing was not measured. Full-validation confirmation and a verify-repair or evidence-policy variant on Gemini are still required before replacing GPT 4.1-mini as the hosted anchor.

## Promotion Gate

| Criterion | Met? |
|-----------|------|
| Schema validity ≥ 90% | Yes (92.0%) |
| Evidence support ≥ verify-repair v2 | No (86.4% vs 91.3%) |
| Monthly/Purist ≥ verify-repair v2 | Yes |
| Matched-cap comparison recorded | Yes |

**Decision:** Gemini 3.1 Flash-Lite clears the label-metric and latency bar on cap-25 but not the evidence-support bar. Next hosted step: either Gemini verify-repair cap-25 or Gemini full-validation direct run with explicit evidence-quote policy comparison — not a primary-model swap yet.

## Validation

- `uv run --extra dev pytest tests/test_experiment_configs.py -k gemini31_flash_lite`
- Dry-run and capped run with `--env-file .env`

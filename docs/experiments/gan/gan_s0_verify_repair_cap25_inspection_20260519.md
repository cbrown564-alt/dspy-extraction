# Gan S0 Verify-Repair Cap-25 Inspection (2026-05-19)

## Purpose

Compare extraction-only (`gan_frequency_s0_direct_single_pass`) against two-stage extract-verify-repair (`gan_frequency_s0_direct_verify_repair`) on the same 25-record GPT 4.1-mini validation cap, under identical artifact-bridge surface normalization and scorer semantics.

## Artifacts

- Direct extraction-only: `runs/gan_s0_direct_cap25_gpt4_1_mini_20260519T081439Z`
- Verify-repair: `runs/gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T081441Z`
- Configs: `configs/experiments/gan_s0_direct_cap25_gpt4_1_mini.json`, `configs/experiments/gan_s0_verify_repair_cap25_gpt4_1_mini.json`

## Bridge Change During This Cycle

The artifact bridge `_normalize_predicted_label` was expanded to strip outer single or double quotes from **any** fully-quoted label, not only `unknown` / `no seizure frequency reference`. This is deterministic surface normalization only — it preserves model meaning while fixing a quoting artifact that affected both direct and verify-repair outputs. The inspection below uses the **post-fix** reruns.

## Headline Comparison (post-quote-fix)

| Metric | Direct | Verify-Repair | Delta |
|--------|--------|---------------|-------|
| Schema validity | 92.0% | 92.0% | 0.0 pp |
| Normalized-label exact | 26.1% | 21.7% | **-4.4 pp** |
| Monthly-frequency accuracy | 34.8% | 39.1% | **+4.3 pp** |
| Purist category accuracy | 47.8% | 52.2% | **+4.4 pp** |
| Pragmatic category accuracy | 69.6% | 69.6% | 0.0 pp |
| Evidence quote support | 34.8% | 31.8% | **-3.0 pp** |
| Invalid predictions | 2 | 2 | 0 |
| Prediction seconds/record | ~1.32 s | ~1.96 s | +49% latency |
| Estimated model calls | 25 | 50 | 2× cost |

## Per-Record Verifier Behavior

The verifier made decisions on 7 of 25 records (all `repair` except `gan_15306` which was `confirm`).

| Record | Gold | Direct | Verify-Repair | Decision | Assessment |
|--------|------|--------|---------------|----------|------------|
| `gan_10434` | `multiple cluster per week, 2 to 3 per cluster` | `multiple per week` (MISS) | `unknown` (MISS) | repair | Worse — valid wrong → abstained wrong; lost all frequency signal |
| `gan_10618` | `unknown, 4 to 6 per cluster` | `1 cluster per day, 4 to 6 per cluster` (MISS) | `unknown` (MATCH on monthly/Purist) | repair | **Win** — incorrect cluster rate → `unknown` matches gold's monthly freq (1000) and Purist category |
| `gan_14485` | `2 per 3 month` | `seizure free for 1 month` (MISS) | `unknown` (MISS) | repair | Mixed — correct 6-month threshold reasoning, but `unknown` is not the right repair; should compute a rate |
| `gan_14881` | `1 per month` | `no seizure frequency reference` (MISS) | `3 per month` (MISS) | repair | Worse — incorrect arithmetic (one seizure in 3 weeks → 3 per month is wrong); over-repair |
| `gan_4956` | `seizure free for 7 month` | `seizure free for 7 month` (**MATCH**) | `no seizure frequency reference` (MISS) | repair | **Major regression** — correct label destroyed by misapplied "not canonical" reasoning |
| `gan_7894` | `seizure free for multiple year` | `seizure free for 35 year` (MISS) | `no seizure frequency reference` (MISS) | repair | Worse — at least direct kept the `seizure free` category; verifier wrongly rejected `seizure free for N unit` as non-canonical |
| `gan_15306` | `2 to 3 per 15 month` | `2 to 3 per week` (MISS) | `2 to 3 per week` (MISS) | confirm | No change |

### Score decomposition

- **Exact-label wins**: 0
- **Exact-label losses**: 1 (`gan_4956` correct → wrong)
- **Category wins**: 1 (`gan_10618` Purist/monthly matched)
- **Category neutral**: 1 (`gan_7894` both wrong, same monthly)
- **Category losses / no improvement**: 5

## Verifier Failure Modes Observed

1. **Misapplies `seizure free` canonicality rule**
   - `gan_4956`: 7 months seizure-free is valid (>6 months), yet verifier repaired to `no seizure frequency reference`.
   - `gan_7894`: `seizure free for 35 year` is a canonical Gan label, yet verifier rejected it.
   - Root cause: verifier prompt does not clearly state that `seizure free for N unit` **is** in the canonical vocabulary when N ≥ 6 months.

2. **Over-repairs imprecise but valid labels to `unknown`**
   - `gan_10434`: `multiple per week` is imprecise but valid; verifier should repair toward the nearest canonical form or keep it, not abstain.
   - `gan_14485`: `seizure free for 1 month` is indeed invalid per the 6-month threshold, but the right repair is to compute a rate from the note (events over period), not to emit `unknown`.

3. **Incorrect arithmetic / temporal inference**
   - `gan_14881`: "one seizure in three weeks" was translated to `3 per month` instead of `1 per 3 week` or roughly `1.3 per month`.

4. **Evidence support regression**
   - Verifier sometimes drops or changes evidence quotes that the direct extractor had already supplied. On this cap, evidence support fell from 34.8% to 31.8%.

5. **Quote wrapping on `confirm` decisions**
   - `gan_15306`: verifier `confirm`ed but wrapped the label in quotes, which the artifact bridge now strips. Pre-fix this would have been an invalid prediction. The verifier should not add wrapper punctuation.

## Latency and Cost

- Direct: 25 model calls, 33.0 s total, 1.32 s/record
- Verify-repair: 50 model calls, 49.1 s total, 1.96 s/record
- Verify-repair adds **+49% latency** and **2× API calls** with no exact-label improvement.

## Conclusions and Next Steps

1. **The verifier/repair architecture is wired and runnable**, but the current v1 verifier prompt is too aggressive and misapplies canonicality rules.
2. **Do not promote verify-repair as the default Gan S0 path** until the prompt is tightened.
3. **The quote-stripping bridge fix is valuable on its own** — it improved schema validity from 76% → 92% on direct extraction by fixing fully-quoted labels.
4. **Recommended verifier v2 improvements**:
   - Explicitly list `seizure free for N unit` (N ≥ 6 months) as a valid canonical label.
   - Distinguish "repair to a better canonical label" from "abstain to `unknown`" — abstention should be a last resort.
   - Require the verifier to preserve or improve evidence quote support, not replace supported quotes with unsupported ones.
   - Add arithmetic guardrails: verifier must not invent frequencies from vague temporal references.
   - Consider a `repair_policy` config flag that gates whether the verifier may change labels at all.

## Validation

- `uv run --extra dev pytest tests/test_gan_s0_program.py tests/test_experiment_configs.py` — all green.
- Dry-runs passed for both configs.
- Real-model runs completed with standard artifact layout (predictions.json, metrics.json, errors.json, prompts.json, metadata.json).

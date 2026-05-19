# Gan S0 Hosted Model Comparison Matrix

Last updated: 2026-05-19

## Purpose

Fixed-condition comparison of Gan S0 seizure-frequency extraction across hosted
models on `gan_2026_fixed_v1:validation` with unchanged
`gan_frequency_deterministic_v1` scorer semantics.

This table is for research traceability and cost/latency planning. It is not
published Gan benchmark reproduction.

## Fixed Conditions

| Field | Value |
| --- | --- |
| Dataset / split | `gan_2026` / `gan_2026_fixed_v1:validation` |
| Schema level | `gan_frequency_s0` |
| Scorer | `gan_frequency_deterministic_v1` |
| Benchmark-facing metrics | Monthly frequency, Purist category, Pragmatic category |
| Diagnostic metrics | Normalized-label exact, schema validity, evidence quote support |
| Structured output | `provider_json_schema_with_pydantic_validation` |

Program variants differ by row. Prompt versions are noted per run artifact.

## Quality Anchor

**GPT 4.1-mini verify-repair v2** remains the hosted quality anchor:

- Run: `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z`
- Config: `configs/experiments/gan_s0_verify_repair_full_validation_gpt4_1_mini.json`
- Inspection: `docs/gan_s0_verify_repair_full_validation_v2_20260519.md`

Do not replace this anchor with Gemini direct or semantic-bootstrap paths until
evidence support and promotion-gate criteria are met on matched caps.

## Full Validation (299 records)

| Model | Program | Prompt | Run artifact | Pred s/rec | Schema | Monthly | Purist | Pragmatic | Norm exact | Evidence |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT 4.1-mini | verify-repair v2 | `gan_frequency_s0_direct_verify_repair_v2` | `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` | 2.81 | 96.7% | **65.4%** | **72.7%** | 79.2% | **52.9%** | **92.7%** |
| Gemini 3.1 Flash-Lite | direct | `gan_frequency_s0_synthesis_v1` | `runs/gan_s0_direct_full_validation_gemini31_flash_lite_20260519T101710Z` | **0.57** | 97.3% | 63.9% | 71.8% | **81.4%** | 50.5% | 84.9% |
| Qwen3.6:35b (local) | direct + guardrails | `gan_frequency_s0_direct_guardrails_v1` | `runs/gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` | 9.61 | 94.0% | 55.9% | 61.9% | 70.5% | 43.8% | **99.6%** |

Synthesis BootstrapFewShot full validation (historical reference, extraction-only):
`runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z` —
monthly 62.9%, Purist 70.1%, Pragmatic 73.9%, evidence 89.9%, schema 97.3%.

## Cap-25 Matched Slice

| Model | Program | Run artifact | Pred s/rec | Schema | Monthly | Purist | Pragmatic | Norm exact | Evidence |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT 4.1-mini | verify-repair v2 | `runs/gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T084511Z` | 1.95 | 92.0% | 34.8% | 47.8% | 69.6% | 26.1% | **91.3%** |
| GPT 4.1-mini | direct | `runs/gan_s0_direct_cap25_gpt4_1_mini_20260519T081439Z` | 0.01 | 92.0% | 34.8% | 47.8% | 69.6% | 26.1% | 34.8% |
| Gemini 3.1 Flash-Lite | direct | `runs/gan_s0_direct_cap25_gemini31_flash_lite_20260519T100621Z` | **0.61** | 92.0% | **52.2%** | **56.5%** | **73.9%** | **34.8%** | 86.4% |
| Gemini 3.1 Flash-Lite | verify-repair v2 | `runs/gan_s0_verify_repair_cap25_gemini31_flash_lite_20260519T101555Z` | 0.86 | 84.0% | 52.4% | 52.4% | 71.4% | 38.1% | 95.0% |

Inspection notes:

- Gemini direct cap-25: `docs/gan_s0_gemini31_flash_lite_cap25_inspection_20260519.md`
- Gemini verify-repair cap-25: `docs/gan_s0_gemini31_flash_lite_verify_repair_cap25_inspection_20260519.md`
- Gemini full validation: `docs/gan_s0_gemini31_flash_lite_full_validation_inspection_20260519.md`

## Token Usage and Billing Estimates

Token counts come from `metrics.json` → `runtime.token_usage` when the provider
exposes usage metadata. Costs below use **Google AI paid-tier list prices** for
`gemini-3.1-flash-lite` ($0.25 / 1M input, $1.50 / 1M output text) and **OpenAI
list prices** for `gpt-4.1-mini` ($0.40 / 1M input, $1.60 / 1M output) as of
2026-05-19. These are **estimates**, not invoices.

| Run | Prompt tokens | Completion tokens | Total tokens | Est. input $ | Est. output $ | Est. total $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Gemini direct cap-25 | 32,538 | 1,114 | 33,652 | $0.008 | $0.002 | **$0.010** |
| Gemini verify-repair cap-25 | 49,431 | 2,463 | 51,894 | $0.012 | $0.004 | **$0.016** |
| Gemini direct full (299) | 367,173 | 12,276 | 379,449 | $0.092 | $0.018 | **$0.110** |
| GPT verify-repair full (299) | 849,779 | 40,270 | 890,049 | $0.340 | $0.064 | **$0.404** |

### Billing Caveats

- **Free tier vs paid**: Gemini runs may be $0 on the free tier; paid-tier math
  above is for production cost planning only.
- **Verify-repair call multiplier**: GPT verify-repair uses ~2 model calls per
  record (548 history entries on 299 records). Gemini verify-repair cap-25 shows
  similar inflation (25 records, 25 history entries).
- **Not comparable to local Qwen**: Ollama runs do not report billable tokens;
  cost is hardware time (see `docs/qwen_local_latency_experiment_20260518.md`).
- **Prompt/version drift**: Gemini direct full validation used
  `gan_frequency_s0_synthesis_v1`; Qwen guardrails used
  `gan_frequency_s0_direct_guardrails_v1`. Cross-row prompt differences limit
  strict A/B interpretation.
- **Evidence vs cost**: Gemini direct is ~25× faster and ~4× cheaper per full
  validation than GPT verify-repair v2 on these estimates, but trails on evidence
  support (84.9% vs 92.7%). Do not treat cost alone as a promotion gate.

## Decisions (2026-05-19)

| Question | Decision |
| --- | --- |
| Primary hosted quality anchor | GPT 4.1-mini verify-repair v2 full validation |
| Cost/latency candidate | Gemini 3.1 Flash-Lite direct |
| Scale Gemini verify-repair? | **No** — cap-25 cluster-stripping regressions (`gan_10434`, `gan_10618`) |
| Scale semantic bootstrap / semantic GEPA? | **No** — failed cap-25 promotion gates |
| Improve Gemini evidence? | Target quote-policy or artifact-bridge work, not verifier scaling |

## Related Docs

- `docs/model_config_smoke_tests.md` — one-record provider compatibility
- `docs/gan_s0_gepa_vs_synthesis_decision_20260519.md` — GEPA pivot to verify-repair
- `docs/kanban_plan.md` — active sequencing

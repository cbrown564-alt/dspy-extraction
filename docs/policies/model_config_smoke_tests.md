# Gan S0 Model-Config Smoke Tests

Last updated: 2026-05-24

## Purpose

These smoke tests check whether each provider/model config can execute its
target frozen DSPy contract and write the standard run artifact layout.
The legacy Gan smokes are one-record compatibility checks; model-suite surface
smokes are capped three-record compatibility checks. They are not performance
estimates, model comparisons, or published Gan benchmark reproduction.

For hosted model quality, latency, and billing comparisons on Gan S0, read
`docs/experiments/gan/gan_s0_hosted_model_comparison_matrix.md`.

Canonical run IDs, gate status, and structured-output fields for model-suite tracks:
[provider_smoke_ledger_20260524.md](provider_smoke_ledger_20260524.md).

For local Qwen scaling decisions, also read
`docs/policies/qwen_dspy_latency_policy.md`. In particular, Qwen3.6:35b should not use
`ChainOfThought + BootstrapFewShot` as the default experiment path while it is
partially offloaded to system RAM.

Legacy Gan S0 smoke configs use:

- Dataset/split: `gan_2026_fixed_v1:validation`
- Record cap: `max_records=1`
- Schema level: `gan_frequency_s0`
- Program variant: `gan_frequency_s0_single_pass`
- Scorer mode: `gan_frequency_deterministic_v1`
- Prompt version: `gan_frequency_s0_v2_vocab_guided`
- Optimizer: none

## Configs

- `configs/experiments/gan_s0_smoke_gpt4_1_mini.json`
- `configs/experiments/gan_s0_smoke_gpt5_5_openai.json`
- `configs/experiments/gan_s0_smoke_gemini3_flash.json`
- `configs/experiments/gan_s0_smoke_gemini31_flash_lite.json`
- `configs/experiments/gan_s0_smoke_claude_sonnet_4_6_anthropic.json`
- `configs/experiments/gan_s0_smoke_qwen35b_ollama.json`
- `configs/experiments/gan_s0_expanded_builders_prose_smoke_qwen27b_ollama.json`
- `configs/experiments/exect_s0_s1_smoke_qwen27b_ollama.json`
- `configs/experiments/exect_s4_smoke_qwen27b_ollama.json`
- `configs/experiments/gan_s0_smoke_qwen9b_ollama.json`

Hosted-provider smokes load credentials from the local `.env` file. Claude
Sonnet 4.6 uses `ANTHROPIC_API_KEY` via
`configs/models/gan_s0_claude_sonnet_4_6_anthropic.json`.

## Results On Windows Laptop

| Model config | Status | Artifact or blocker |
| --- | --- | --- |
| `gan_s0_claude_sonnet_4_6_anthropic.json` | Completed on Windows 2026-05-22 | One-record Gan smoke: `runs/gan_s0_smoke_claude_sonnet_4_6_anthropic_20260522T080515Z` (schema 100%, evidence 100%). Model-suite smokes (3 records each): Gan F0 `…080527Z`, ExECT S1 `…080538Z`, ExECT S4 `…080625Z` — all completed with standard artifacts; schema ≥ 96%, evidence ≥ 96%. Compatibility only; not performance estimates. |
| `gan_s0_gpt4_1_mini.json` | Completed | `runs/gan_s0_smoke_gpt4_1_mini_20260518T130500Z` |
| `gan_s0_gpt5_5_openai.json` | Completed after config fix | `runs/gan_s0_smoke_gpt5_5_openai_20260518T130600Z` |
| `gan_s0_gemini3_flash.json` | Completed after model-id fix | `runs/gan_s0_smoke_gemini3_flash_20260518T134109Z`; config uses `gemini-3-flash-preview`. Previous blocker was a 404 for invalid `models/gemini-3-flash`. The smoke run completed but produced an invalid Gan label on the one record, so treat this as provider/runtime compatibility only. |
| `gan_s0_gemini31_flash_lite.json` | Completed | Uses **GA** model id `gemini-3.1-flash-lite` per [Gemini 3.1 Flash-Lite docs](https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite), not `gemini-3.1-flash-lite-preview`. Smoke: `runs/gan_s0_smoke_gemini31_flash_lite_20260519T100246Z`, GA re-smoke `runs/gan_s0_smoke_gemini31_flash_lite_20260519T101222Z`. Cap-25 direct: `runs/gan_s0_direct_cap25_gemini31_flash_lite_20260519T100621Z` (see `docs/experiments/gan/gan_s0_gemini31_flash_lite_cap25_inspection_20260519.md`). Cap-25: schema 92.0%, monthly 52.2%, Purist 56.5%, evidence 86.4%, ~0.61 s/record. Promising labels/latency; evidence gap vs verify-repair v2 before primary-model claims. |
| `gan_s0_qwen35b_ollama.json` | Deferred to Windows laptop | Local Qwen runs should be performed on the Windows laptop with the target GPU. This Mac's Ollama tags do not include `qwen3.6:35b`. |
| `gan_s0_qwen27b_ollama.json` / `exect_qwen27b_ollama.json` | Completed on Windows 2026-05-22 | Ollama tag confirmed as `qwen3.6:27b`. Phase-0 smokes passed with standard artifacts: Gan F0 `runs/gan_s0_expanded_builders_prose_smoke_qwen27b_ollama_20260522T091754Z` (3 records; schema/evidence 100%; 48.9 s/record; 69%/31% CPU/GPU at context 4096), ExECT S1 `runs/exect_s0_s1_smoke_qwen27b_ollama_20260522T095301Z` (3 records; micro 94.7%; evidence 100%; 537.5 s/record; 71%/29% CPU/GPU at context 65536), ExECT S4 `runs/exect_s4_smoke_qwen27b_ollama_20260522T102006Z` (3 records; micro 68.0%; evidence 100%; 551.8 s/record; 71%/29% CPU/GPU at context 65536). The first ExECT S1 attempt used `num_ctx=262144`, loaded at 81%/19% CPU/GPU, and timed out before prediction artifacts; the config now uses bounded `num_ctx=65536` / `max_tokens=16384` for smoke feasibility. Compatibility only; not performance estimates. |
| `gan_s0_qwen9b_ollama.json` | Completed on Windows 2026-05-22 | One-record Gan smoke: `runs/gan_s0_smoke_qwen9b_ollama_20260522T092032Z` (schema/evidence 100%; 23.1 s/record; 29%/71% CPU/GPU at context 4096). Compatibility only; not a performance estimate. Earlier Mac partial artifact remains `runs/gan_s0_smoke_qwen9b_ollama_20260518T130640Z`. |

Gemini 3 Flash currently uses the preview model code
`gemini-3-flash-preview`, confirmed against the Google model list API on
2026-05-18. The one-record smoke run completed and wrote a standard artifact,
but Gemini predicted an unsupported label (`'2 per 4 month'`) for the sampled
record, so schema validity was 0/1.

GPT-5.5 rejected `temperature=0`, so `configs/models/gan_s0_gpt5_5_openai.json`
now sets `"temperature": null`. The provider adapter omits temperature when the
config value is null, leaving the provider default in place.

## Windows Qwen Handoff

Run from the repo root on the Windows laptop after installing dependencies and
starting Ollama:

```powershell
uv run --extra dev pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py tests/test_experiment_configs.py
```

Compatibility backlog B6 adds a stricter offline guard: when model/provider
config work resumes, add or run config-level coverage that exercises
`build_dspy_lm` for every `configs/models/*.json` file, not only
`build_chat_adapter`. The check should stay offline and assert provider kwargs
such as Ollama `think: False`, Gemini `reasoning_effort`, Anthropic
`extra_body`, and GPT-5-family null-temperature handling.

Compatibility backlog B7 also gates broad Gemini comparisons: make the intended
Gemini `reasoning_effort` behavior explicit in config/tests, or replace the
current substring default with a provider-verified allowlist, before treating
Gemini 3 Flash and Gemini 3.1 Flash-Lite runs as adapter-policy comparable.

Check that Ollama sees the required model tags:

```powershell
ollama list
```

Expected tags for the current comparison matrix:

- `qwen3.6:35b`
- `qwen3.6:27b`
- `qwen3.5:9b`

Run the dry checks first:

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_smoke_qwen35b_ollama.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_expanded_builders_prose_smoke_qwen27b_ollama.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_qwen27b_ollama.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_smoke_qwen27b_ollama.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_smoke_qwen9b_ollama.json --env-file .env --dry-run
```

Then run the Qwen smoke tests:

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_smoke_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_expanded_builders_prose_smoke_qwen27b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_smoke_qwen27b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s4_smoke_qwen27b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_smoke_qwen9b_ollama.json --env-file .env
```

Record the resulting run IDs in [provider_smoke_ledger_20260524.md](provider_smoke_ledger_20260524.md)
and keep the caveat that these capped runs validate runtime compatibility only.

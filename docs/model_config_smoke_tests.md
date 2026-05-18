# Gan S0 Model-Config Smoke Tests

Last updated: 2026-05-18

## Purpose

These smoke tests check whether each provider/model config can execute the fixed
Gan S0 single-pass DSPy contract and write the standard run artifact layout.
They are one-record compatibility checks only. They are not performance
estimates, model comparisons, or published Gan benchmark reproduction.

All smoke configs use:

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
- `configs/experiments/gan_s0_smoke_qwen35b_ollama.json`
- `configs/experiments/gan_s0_smoke_qwen9b_ollama.json`

## Results On This Mac

| Model config | Status | Artifact or blocker |
| --- | --- | --- |
| `gan_s0_gpt4_1_mini.json` | Completed | `runs/gan_s0_smoke_gpt4_1_mini_20260518T130500Z` |
| `gan_s0_gpt5_5_openai.json` | Completed after config fix | `runs/gan_s0_smoke_gpt5_5_openai_20260518T130600Z` |
| `gan_s0_gemini3_flash.json` | Blocked | Google returned 404 for `models/gemini-3-flash` through LiteLLM's Gemini path. Confirm the Gemini 3 Flash model identifier/API version before retrying. Partial artifact: `runs/gan_s0_smoke_gemini3_flash_20260518T130620Z`. |
| `gan_s0_qwen35b_ollama.json` | Deferred to Windows laptop | Local Qwen runs should be performed on the Windows laptop with the target GPU. This Mac's Ollama tags do not include `qwen3.6:35b`. |
| `gan_s0_qwen9b_ollama.json` | Deferred to Windows laptop | Local Qwen runs should be performed on the Windows laptop for comparability with the 35B target runtime. A Mac attempt was stopped before prediction completion. Partial artifact: `runs/gan_s0_smoke_qwen9b_ollama_20260518T130640Z`. |

GPT-5.5 rejected `temperature=0`, so `configs/models/gan_s0_gpt5_5_openai.json`
now sets `"temperature": null`. The provider adapter omits temperature when the
config value is null, leaving the provider default in place.

## Windows Qwen Handoff

Run from the repo root on the Windows laptop after installing dependencies and
starting Ollama:

```powershell
uv run --extra dev pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py tests/test_experiment_configs.py
```

Check that Ollama sees the required model tags:

```powershell
ollama list
```

Expected tags for the current comparison matrix:

- `qwen3.6:35b`
- `qwen3.5:9b`

Run the dry checks first:

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_smoke_qwen35b_ollama.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_smoke_qwen9b_ollama.json --env-file .env --dry-run
```

Then run the one-record Qwen smoke tests:

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_smoke_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_smoke_qwen9b_ollama.json --env-file .env
```

Record the resulting run IDs in `docs/kanban_plan.md` and keep the caveat that
these one-record runs validate runtime compatibility only.

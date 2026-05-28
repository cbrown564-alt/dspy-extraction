# Gan S0 G5 Paper-Scorer Rescore Pack

Generated: `2026-05-28T21:50:25.491293+00:00`

## Scope

- Dataset: `gan_2026`
- Split: `gan_2026_fixed_v1:validation`
- Schema level: `gan_frequency_s0`
- Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`
- Reference policy: reference[0] is a secondary cross-check and difficulty signal, not gold.
- Run mode: Post-hoc rescore of stored synthetic-validation predictions; no model calls were made.

## Paper Scorer Options

| Option | Enabled |
| --- | ---: |
| `apply_paper_prediction_repair` | `False` |
| `allow_paper_prediction_range` | `False` |
| `allow_paper_error_tolerance` | `False` |

## Rescore Summary

| Baseline | Run ID | Model | Paper monthly | Paper purist | Paper pragmatic | Canonical monthly | Canonical purist | Canonical pragmatic | Paper-canonical monthly | Valid paper/canonical |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Builder-gap v1 GPT | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | gpt-4.1-mini / openai | 79.9% | 85.3% | 88.0% | 80.6% | 86.0% | 88.6% | -0.7pp | 299/299 |
| Builder-gap v1 Qwen | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` | qwen3.6:35b / ollama | 70.2% | 81.3% | 89.6% | 70.7% | 83.2% | 90.6% | -0.5pp | 299/297 |
| D1 v1.2b schema guard GPT | `gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z` | gpt-4.1-mini / openai | 76.6% | 80.9% | 83.6% | 79.9% | 84.9% | 87.6% | -3.3pp | 299/298 |

## Interpretation

- G5 is now available as a synthetic-validation rescore pack for paper-facing Gan S0 tables.
- Builder-gap v1 GPT remains the strongest promoted synthetic operational baseline in the paper-reproduction view.
- D1 v1.2b remains the cleaner mechanism baseline: it is close to builder-gap GPT while exposing the date/event candidate payload.
- The paper-reproduction scorer can change both metric values and denominator behavior for malformed predictions; canonical rows are retained as diagnostic sensitivity views.

## Caveats

- Synthetic validation only: this is not Real(300), Real(150), or a published Gan benchmark reproduction.
- Paper-reproduction metrics are the benchmark-facing view for direct Gan scorer compatibility; canonical metrics remain diagnostic sensitivity analyses.
- The primary paper-reproduction rows report the repair, range, and tolerance options explicitly.
- Stored prediction artifacts were rescored as-is; no scorer, loader, split, bridge, prompt, or prediction artifact was tuned.

## Source Artifacts

| Baseline | Role | Run directory | Config |
| --- | --- | --- | --- |
| Builder-gap v1 GPT | promoted synthetic operational default | `C:\Users\cbrow\Code\dspy-extraction\archive\runs\gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | `C:\Users\cbrow\Code\dspy-extraction\archive\runs\gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z\config.json` |
| Builder-gap v1 Qwen | accepted local-transfer baseline | `C:\Users\cbrow\Code\dspy-extraction\archive\runs\gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` | `C:\Users\cbrow\Code\dspy-extraction\archive\runs\gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z\config.json` |
| D1 v1.2b schema guard GPT | mechanism baseline / operational D1 surface | `C:\Users\cbrow\Code\dspy-extraction\runs\gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z` | `C:\Users\cbrow\Code\dspy-extraction\runs\gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z\config.json` |

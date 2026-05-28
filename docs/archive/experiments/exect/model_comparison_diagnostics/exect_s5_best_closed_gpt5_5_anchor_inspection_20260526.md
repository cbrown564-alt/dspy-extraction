# ExECT S5 Best-Closed GPT 5.5 Anchor Inspection

Date: 2026-05-26  
Status: Completed  
Decision scope: arm; closed-model anchor for A2, not mechanism closure  
Comparison group: `exect_s5_frequency_verify_v2b_model_comparison`; varied factor: `model_track`

## Research Question

Holding the promoted ExECT S5 v2b stack fixed, does GPT 5.5 materially strengthen the paper claim beyond the GPT 4.1-mini and Qwen3.6:35b anchors?

## Method

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2, `exectv2_fixed_v1:validation` |
| Run scope | Full validation, 40 records |
| Model / provider | GPT 5.5 via OpenAI |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai.json` |
| Run ID | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z` |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |
| Structured output | Provider JSON schema with Pydantic validation |
| Fixed controls | v1.2 extractor prompt, high-recall seizure-frequency candidates, AM guard, reject-only v2b frequency verifier, no optimizer |

S5 remains a partial ExECT diagnostic surface: diagnosis, seizure type, annotated medication, investigation, and seizure frequency. It is not a CUI-aware ExECTv2 Table 1 reproduction.

## Results

| Model | Run ID | Micro F1 | Micro P | Micro R | Diagnosis F1 | Seizure type F1 | Annotated medication F1 | Investigation F1 | Seizure frequency F1 | Evidence quote support |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT 4.1-mini | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` | 85.8% | 82.1% | 90.0% | 90.0% | 84.0% | 88.7% | 96.7% | 73.9% | 94.1% |
| Qwen3.6:35b | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_qwen35b_ollama_20260525T072245Z` | 85.4% | 83.9% | 87.1% | 92.5% | 82.5% | 88.7% | 94.9% | 71.4% | 95.5% raw / 100.0% repaired |
| GPT 5.5 | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z` | 82.6% | 77.4% | 88.5% | 88.3% | 73.7% | 88.5% | 94.9% | 74.5% | 99.5% |

Runtime for the GPT 5.5 run was 1,276.0 seconds total, 31.9 seconds per record, with 249,912 total tokens.

## Interpretation

GPT 5.5 does not strengthen the overall S5 paper claim under the fixed v2b stack. It improves seizure-frequency F1 slightly versus GPT 4.1-mini (74.5% vs 73.9%) and Qwen (74.5% vs 71.4%), but the gain is offset by lower seizure-type F1 (73.7% vs 84.0% GPT 4.1-mini and 82.5% Qwen) and lower pooled micro F1.

The supported paper-facing wording remains: Qwen3.6:35b is near GPT 4.1-mini on the promoted S5 v2b synthetic-validation surface, while frequency remains a family-specific caveat. A stronger closed model does not currently displace the GPT 4.1-mini anchor for the S5 headline row.

## Caveats

- This is synthetic validation on the fixed 40-record ExECTv2 validation split, not test reporting.
- No scorer, loader, prompt, verifier, or candidate policy changed.
- Evidence support is deterministic quote/source grounding and is diagnostic, not clinician adjudication.
- The run is an A2 closed-model anchor only; it should not trigger tuning from its residual errors.

## Artifacts

| Artifact | Path |
| --- | --- |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai.json` |
| Run directory | `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z/` |
| Metrics | `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z/metrics.json` |
| Predictions | `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z/predictions.json` |
| Prompts | `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt5_5_openai_20260526T130247Z/prompts.json` |

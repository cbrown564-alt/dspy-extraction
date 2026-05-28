# ExECT S1 Qwen v4.12 Diagnosis-Stabilized Prompt - Preregistration

Date: 2026-05-21  
Status: Preregistered; cap-25 completed 2026-05-21 (reject arm)  
Parent: `exect_s1_residual_error_analysis_20260521.md` and held v4.11 inspection  
Comparison group: `exect_s1_qwen_diagnosis_stabilized_v1`

## Research Question

Can a prompt-only v4.12 follow-up preserve the Qwen v4.11 seizure-type gain while preventing the diagnosis drift that blocked promotion?

## Fixed Controls

| Control | Value |
| --- | --- |
| Dataset / split | `exectv2_fixed_v1:validation` |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Model track | Qwen3.6:35b via Ollama |
| Program | `exect_s0_s1_field_family_single_pass` |
| Repair policy | `artifact_benchmark_bridge_only` for Qwen, `none` for GPT guardrail |
| Varied factor | `prompt_policy` only |

## Baselines

| Run | Prompt | Micro F1 | Diagnosis F1 | Seizure F1 | Decision |
| --- | --- | ---: | ---: | ---: | --- |
| `exect_s1_interleaving_h1_post_bridge_qwen35b_ollama_20260520T210722Z` | v4.10 | 79.0% | 95.1% | 55.7% | Frozen Qwen anchor |
| `exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama_20260520T231850Z` | v4.11 | 84.3% | 90.0% | 74.2% | Hold |

## Intervention

`exect_s0_s1_field_family_v4_12_label_policy` composes:

- v4.10 base label policy;
- v4.11 Qwen seizure rules for plural surfaces, absence/myoclonic abstention, and secondary-generalisation;
- new diagnosis-stability rules that keep seizure policy from changing diagnosis labels.

No deterministic bridge, scorer, loader, schema, or model config changes are included.

## Gates

| Stage | Gate |
| --- | --- |
| GPT cap-25 | No material S1 regression versus v4.10/v4.11 GPT cap anchors; primarily protects shared prompt surface. |
| Qwen cap-25 | Seizure F1 remains at least +8pp versus v4.10 cap anchor and diagnosis does not regress by >=2pp versus v4.10 cap anchor. |
| Qwen full | Seizure F1 >= v4.11 full -2pp, diagnosis F1 improves by >=3pp versus v4.11 full, medication F1 does not regress by >=2pp versus v4.10 full. |

Promotion remains blocked if diagnosis stays near v4.11 full (90.0%) even if seizure remains high.

## Planned Configs

- `configs/experiments/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_qwen35b_ollama.json`
- `configs/experiments/exect_s1_qwen_v4_12_diagnosis_stabilized_full_qwen35b_ollama.json`

## Caveats

This remains an S1 three-family benchmark-facing diagnostic, not published ExECTv2 Table 1 reproduction. Evidence support remains diagnostic only.

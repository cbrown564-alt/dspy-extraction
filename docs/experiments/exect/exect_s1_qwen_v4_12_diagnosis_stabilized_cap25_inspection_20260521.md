# ExECT S1 Qwen v4.12 Diagnosis-Stabilized — Cap-25 Inspection

Date: 2026-05-21  
Comparison group: `exect_s1_qwen_diagnosis_stabilized_v1`  
Preregistration: `docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_preregistration_20260521.md`

## Runs inspected

| Arm | Run ID | Config |
| --- | --- | --- |
| GPT guardrail | `exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_gpt4_1_mini_20260521T095259Z` | `exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_gpt4_1_mini.json` |
| Qwen treatment | `exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_qwen35b_ollama_20260521T095620Z` | `exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_qwen35b_ollama.json` |

## Cap-25 metrics (same 25-record slice)

| Arm | Micro F1 | Diagnosis F1 | Seizure F1 | Medication F1 |
| --- | ---: | ---: | ---: | ---: |
| Qwen v4_10 H1 cap-25 (`…210432Z`) | 80.7% | 95.2% | 66.7% | 87.3% |
| Qwen v4_11 cap-25 (`…214425Z`) | 85.4% | 92.7% | 78.3% | 88.9% |
| **Qwen v4_12 cap-25** | **83.8%** | **97.6%** | **66.7%** | **94.7%** |
| GPT v4_12 guardrail | 93.8% | 97.6% | 92.3% | 92.9% |

## Gate assessment

| Stage | Gate | Result |
| --- | --- | --- |
| GPT cap-25 | No material S1 regression vs v4_10/v4_11 GPT cap anchors | **Pass** — micro 93.8% (−2.0pp vs v4_10 cap-25 95.8%; within guardrail noise) |
| Qwen cap-25 | Seizure F1 ≥ +8pp vs v4_10 cap; diagnosis not −2pp vs v4_10 cap | **Fail** — seizure **+0.0pp** (66.7% vs 66.7%; required ≥74.7%); diagnosis **+2.4pp** (97.6% vs 95.2%) |

## Read

v4_12 restored diagnosis stability at cap-25 (+4.9pp vs v4_11 cap-25, +2.4pp vs v4_10 cap-25) but **fully gave back** the v4_11 seizure lift (−11.6pp vs v4_11 cap-25). Seizure F1 tied the frozen v4_10 cap anchor exactly, so the preregistered +8pp seizure gate did not clear.

Residual seizure errors on the cap slice still include absence-seizure false positives (`EA0029`, `EA0050`, `EA0125`), plural/singular mismatches (`EA0016`, `EA0026`), and secondary-generalisation confusion (`EA0072`, `EA0090`) — the same families v4_11 targeted.

## Decision

**Reject (arm)** at cap-25. **Do not run** Qwen full validation (`exect_s1_qwen_v4_12_diagnosis_stabilized_full_qwen35b_ollama`). Frozen Qwen S1 operational default remains v4_10 H1 full; held v4_11 full stays blocked on diagnosis drift.

`decision_scope: arm` — prompt-policy tradeoff failure, not mechanism closure.

## Runtime notes

Qwen cap-25: 79%/21% CPU/GPU offload, ~420 s/record, ~2.9 h total. Detached launcher completed cleanly (exit 0).

## Next

No further v4_12 runs without a new preregistered prompt variant. Gan F0 Qwen cap-25 **done** (2026-05-22); next Ollama pull is **Gan F0 Qwen full validation** (`scripts/start_gan_s0_expanded_builders_prose_full_qwen35b_detached.ps1`).

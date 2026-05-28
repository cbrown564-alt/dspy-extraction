# Gan S0 Temporal/Date-Stage Ablation Decision Report (R11/R33)

Date: 2026-05-28  
Comparison Group: `gan_s0_temporal_date_stage_gpt_cap25_v1`  
Status: Completed & Evaluated (GPT 4.1-mini and Qwen 3.6:35b)

## Executive Summary

The R11 temporal/date-stage ablation grid compared four executor configurations (D0-D3) to evaluate if isolating a specialist date/event stage improves Gan S0 monthly seizure-frequency extraction. 

**Decision:** **PASS** the deterministic date/event stage (**D1**) to integration. Reject the LLM-only date/events stage (**D2**) due to severe schema/validation regressions, and hold the Hybrid merge stage (**D3**) as it does not outperform the cleaner D1 baseline.

---

## Taxonomy Block

```json
{
  "dataset": "gan_2026",
  "schema_complexity": "gan_s0",
  "clinical_task_family": "frequency",
  "comparison_group": "gan_s0_temporal_date_stage_gpt_cap25_v1",
  "stage_graph_id": "g3_date_events_candidates_adjudicate",
  "varied_factor": "date_event_stage_executor",
  "decision_scope": "arm",
  "intended_decision": "promote_d1"
}
```

---

## Run Metadata & Configs

| Arm | Model Config | Run Directory |
| --- | --- | --- |
| **D0** (GPT-4) | `configs/models/gan_s0_gpt4_1_mini.json` | `runs/gan_s0_date_stage_d0_baseline_det_candidates_cap25_gpt4_1_mini_20260527T234953Z` |
| **D0** (Qwen) | `configs/models/gan_s0_qwen35b_ollama.json` | `runs/gan_s0_date_stage_d0_baseline_det_candidates_cap25_qwen35b_20260528T000407Z` |
| **D1** (GPT-4) | `configs/models/gan_s0_gpt4_1_mini.json` | `runs/gan_s0_date_stage_d1_det_events_cap25_gpt4_1_mini_20260527T234958Z` |
| **D1** (Qwen) | `configs/models/gan_s0_qwen35b_ollama.json` | `runs/gan_s0_date_stage_d1_det_events_cap25_qwen35b_20260528T000532Z` |
| **D2** (GPT-4) | `configs/models/gan_s0_gpt4_1_mini.json` | `runs/gan_s0_date_stage_d2_llm_events_cap25_gpt4_1_mini_20260527T235033Z` |
| **D2** (Qwen) | `configs/models/gan_s0_qwen35b_ollama.json` | `runs/gan_s0_date_stage_d2_llm_events_cap25_qwen35b_20260528T001149Z` |
| **D3** (GPT-4) | `configs/models/gan_s0_gpt4_1_mini.json` | `runs/gan_s0_date_stage_d3_hybrid_events_cap25_gpt4_1_mini_20260527T235436Z` |
| **D3** (Qwen) | `configs/models/gan_s0_qwen35b_ollama.json` | `runs/gan_s0_date_stage_d3_hybrid_events_cap25_qwen35b_20260528T003527Z` |

---

## Metrics Matrix

| Model | Arm | Monthly Acc | Purist Acc | Pragmatic Acc | Schema Valid | Evidence Support | Call Count |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **GPT 4.1-mini** | **D0 (Control)** | 92.0% | 92.0% | 92.0% | 100.0% | 100.0% | 1 |
| | **D1 (Det Events)** | **96.0%** | **100.0%** | **100.0%** | 100.0% | 100.0% | 1 |
| | **D2 (LLM Events)** | 24.0% | 40.0% | 48.0% | 100.0% | 100.0% | 2 |
| | **D3 (Hybrid)** | 92.0% | 92.0% | 96.0% | 100.0% | 100.0% | 2 |
| **Qwen 3.6:35b** | **D0 (Control)** | 84.0% | 84.0% | 92.0% | 100.0% | 100.0% | 1 |
| | **D1 (Det Events)** | **92.0%** | **92.0%** | **96.0%** | 100.0% | 100.0% | 1 |
| | **D2 (LLM Events)** | 19.0% | 38.1% | 38.1% | 84.0% | 100.0% | 2 |
| | **D3 (Hybrid)** | 92.0% | 92.0% | 96.0% | 100.0% | 100.0% | 2 |

---

## Error Analysis & Prediction Overlap

### 1. D1 (Deterministic Events) Winner Profile
- On **GPT 4.1-mini**, **D1** corrected a critical temporal/baseline error in `gan_13058` (Gold: `2 per 7 month` [0.286], baseline D0 Pred: `1 per 7 month` [0.143]). By isolating deterministic date/event structures, the adjudicator successfully parsed the denominator.
- The single remaining error for D1 on GPT 4.1-mini was `gan_15193` (Gold: `multiple per 13 month` [0.231], Pred: `multiple per year` [0.250]), which is a subtle math window discrepancy.
- On **Qwen 3.6:35b**, **D1** also showed a strong +8.0pp absolute accuracy improvement over the D0 baseline (rising to **92.0%**). It resolved the baseline errors on `gan_13123` and `gan_15442`.

### 2. D2 (LLM Specialist) Regression
- **D2** suffered catastrophic failure across both models (falling to 24.0% on GPT and 19.0% on Qwen). 
- **Cause:** When the LLM was tasked with extracting the intermediate `DateEventPayload` directly, it hallucinated non-compliant keys, outputted unhashable structures (nested dicts inside lists), or omitted required clinical anchors. The downstream adjudicator failed to resolve these, resulting in a flood of `no seizure frequency reference` and `unknown` predictions.

### 3. D3 (Hybrid Merge)
- D3 recovered the stability of D0/D1 by merging deterministic and LLM outputs, but the additional LLM call yielded no extra accuracy over D1 and added latency and API cost.

---

## Decision & Gates

- **Gate Rule Evaluation (GPT-4 D1 vs D0):**
  - Beat D0 by >= 3pp? **Yes** (+4.0pp)
  - Schema validity >= 95%? **Yes** (100.0%)
  - Evidence support >= 95%? **Yes** (100.0%)
  - No increase in unknown/no-reference confusion? **Yes** (remained 0)
- **Action:** **PASS** D1 to integration. Re-run D1 on full validation to confirm the signal.
- **Qwen Port Transferability:** Confirmed. Qwen showed a matched +8.0pp improvement on D1 over D0, indicating high architectural transferability.

## Open Cells

- **Untested presentation variants:** Sweeping the format of the deterministic candidates presented to the downstream adjudicator (e.g., bulleted vs JSON).
- **R12 Integration:** Recommend that the R12 entity tagger feeds into the **D1 deterministic date/event pipeline** rather than trying to feed into D2.

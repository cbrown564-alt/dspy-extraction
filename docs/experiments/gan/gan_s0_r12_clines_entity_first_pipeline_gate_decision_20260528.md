# Gan S0 CLINES Entity-First Stage Graph Decision Report (R12/R35)

Date: 2026-05-28  
Comparison Group: `gan_s0_entity_first_stage_graph_gpt_cap25_v1`  
Status: Completed & Evaluated (GPT 4.1-mini and Qwen 3.6:35b)

## Executive Summary

The R12 stage-graph gate compared an entity-first decomposition pipeline (C1) against the matched deterministic date/event baseline control (C0) to evaluate if tagging clinically relevant entities and offsets/context first improves downstream adjudication.

**Decision:** **REJECT** the C1 entity-first treatment arm. The C1 pipeline introduced severe context-loss and parsing degradation, leading to a catastrophic accuracy drop to **20.8%** on GPT 4.1-mini and **12.0%** on Qwen 3.6:35b. Proceed with direct note date/event extraction (the R11 D1 winning pattern).

---

## Taxonomy Block

```json
{
  "dataset": "gan_2026",
  "schema_complexity": "gan_s0",
  "clinical_task_family": "frequency",
  "comparison_group": "gan_s0_entity_first_stage_graph_gpt_cap25_v1",
  "stage_graph_id": "g4_entity_tags_date_events_candidates_adjudicate",
  "varied_factor": "entity_first_decomposition",
  "decision_scope": "arm",
  "intended_decision": "reject_c1"
}
```

---

## Run Metadata & Configs

| Arm | Model Config | Run Directory |
| --- | --- | --- |
| **C0** (GPT-4) | `configs/models/gan_s0_gpt4_1_mini.json` | `runs/gan_s0_entity_first_c0_date_events_cap25_gpt4_1_mini_20260527T235508Z` |
| **C0** (Qwen) | `configs/models/gan_s0_qwen35b_ollama.json` | `runs/gan_s0_entity_first_c0_date_events_cap25_qwen35b_20260528T003532Z` |
| **C1** (GPT-4) | `configs/models/gan_s0_gpt4_1_mini.json` | `runs/gan_s0_entity_first_c1_llm_tags_date_events_cap25_gpt4_1_mini_20260527T235513Z` |
| **C1** (Qwen) | `configs/models/gan_s0_qwen35b_ollama.json` | `runs/gan_s0_entity_first_c1_llm_tags_date_events_cap25_qwen35b_20260528T003538Z` |

---

## Metrics Matrix

| Model | Arm | Monthly Acc | Purist Acc | Pragmatic Acc | Schema Valid | Evidence Support |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| **GPT 4.1-mini** | **C0 (Control)** | **96.0%** | **100.0%** | **100.0%** | 100.0% | 100.0% |
| | **C1 (Treatment)** | 20.8% | 41.7% | 54.2% | 96.0% | 100.0% |
| **Qwen 3.6:35b** | **C0 (Control)** | **92.0%** | **92.0%** | **96.0%** | 100.0% | 100.0% |
| | **C1 (Treatment)** | 12.0% | 24.0% | 28.0% | 100.0% | 100.0% |

---

## Error Analysis & Failures

### 1. Rejection Rationale
- **C1** regressed by **75.2pp** on GPT-4 and **80.0pp** on Qwen.
- **Cause:** Pre-tagging entities with an LLM and feeding only the tagged spans and local context into the downstream normalizer strips away critical global cues (e.g. temporality anchors, medication changes, planned status, or letter dates).
- For example, in records like `gan_13149`, `gan_14214`, and `gan_14792`, the downstream adjudicator responded with `unknown` or `no seizure frequency reference` because the pre-tagged inputs lacked the context necessary to ground the extraction.

### 2. Implementation Interface Rejection
- Forcing a rigid "tag first, normalize second" architecture introduces multiple points of compounding errors (tagging omission + normalizer schema misalignment).
- Direct extraction of candidate date/events (R11 D1) preserves global context and is significantly more robust.

---

## Decision & Gates

- **Gate Rule Evaluation (C1 vs C0):**
  - C1 beats C0 by at least 3pp monthly? **No** (severely regressed).
  - Schema validity >= 95%? **Yes** (96.0% on GPT-4).
- **Action:** **REJECT** the C1 entity-first stage graph. Do not proceed to full validation or targeted replay for this arm. 
- **Integration Recommendation:** R11 date/events should be extracted directly from the raw clinical note.

## Open Cells
- None for this axis. Entity-first decomposition is rejected for Gan S0.

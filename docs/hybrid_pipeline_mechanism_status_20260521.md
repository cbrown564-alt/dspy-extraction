# Hybrid Pipeline Mechanism Status

Date: 2026-05-21  
Maintained under: `docs/hybrid_pipeline_research_pivot_20260521.md`  
Update when an inspection doc with `decision_scope: mechanism` closes a class, or when a new arm reject is recorded.

**Legend:** `open` | `arm-reject` | `operational-freeze` | `mechanism-reject` (rare)

---

## Operational defaults (not mechanism-closed)

| ID | Config / program | decision_scope | Notes |
| --- | --- | --- | --- |
| gan-default | temporal-candidates + verify-repair v1.1 | operational | Best known Gan arm; Phase 2 may supersede |
| exect-s1-gpt | v4_10 + inline bridges | operational | Ladder + freeze anchor 92.3% micro full |
| exect-ladder-gpt | S2–S4 frozen full runs | operational | Schema complexity series |

---

## Axis 1 — Pipeline stage count / decomposition

| Mechanism class | Status | Evidence |
| --- | --- | --- |
| Optimal stage count for Gan S0 | **open** | Cap-25 grid complete; A3 (`g2_candidates_adjudicate`) leads at 52% monthly — see `docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md` |
| Optimal stage count for ExECT S1 | **open** | D1→L0→L1→L1+policy confounds stages with policy |
| Single-stage sufficient for Gan | **open** | — |
| Three-stage (candidates+VR) necessary for Gan | **open** | Promoted arm is 2–3 stage; Phase 2 isolates stage graph while holding candidate source deterministic |

---

## Axis 2 — Deterministic vs LLM per stage

| Mechanism class | Status | Evidence |
| --- | --- | --- |
| Det temporal candidate generation (Gan) | **operational-freeze** | In promoted arm; **not mechanism-closed** |
| LLM temporal candidate generation (Gan) | **open** | Cap-25 JSON path rejected as arm (E2/E5 29.2% vs E1 52%); presentation not swept — `docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md` |
| LLM vs det for candidate stage (Gan) | **open** | Directional det > hybrid > LLM on cap-25; mechanism not closed (one LLM format) |
| Verify-repair as second stage (Gan) | **open** | Cap-25 null on monthly; temporal+VR ≡ direct on labels in Lane A |
| Verify-repair (ExECT S1) | **arm-reject** | `exect_s1_verification_verify_repair_cap25` −9.4pp micro |
| Tool-during temporal (Gan H3) | **arm-reject** | `gan_s0_qwen35b_react_temporal_tools` slice — one tool surface |
| Tool-during (general) | **open** | Second tool implementation not tested |
| Pre section-aware context (ExECT) | **arm-reject** | Section-aware cap-25 fail — short-note caveat |
| Pre static vocab lists (ExECT S1/S4) | **arm-reject** | Slice/cap-25 configs in negative-probe synthesis |
| Pre context/candidate (general ExECT) | **open** | Other presentations and tasks not swept |
| Post benchmark bridges (ExECT S1) | **operational-freeze** | Inline bridges in production; diagnostic bridge-free measured |
| Post bridge as only intervention | **open** | Not same as bridge + policy decomposition |

---

## Axis 3 — Implementation variants

| Mechanism class | Status | Evidence |
| --- | --- | --- |
| Prompt v4_11 (GPT S1) | **arm-reject** | cap-25 seizure −1.5pp |
| Prompt v4_11 (Qwen S1) | **operational-freeze** | Hold promote blocked; seizure +18.5pp full |
| Evidence soft (ExECT S1) | **arm-reject** | cap-25 |
| Evidence span-check (Gan) | **arm-reject** | confounded cap-25 |
| Bootstrap optimizer (ExECT S1) | **arm-reject** | cap-25 −5.1pp |
| DSPy optimizers (general) | **open** | Ladder rungs 4–5 not run |
| GEPA (Gan) | **arm-reject** | historical full |
| ReAct interface (Gan) | **arm-reject** | one implementation |
| Candidate table vs JSON vs prose (Gan) | **open** | Cap-25: table/JSON/bullets 56% vs prose 52% (+4pp); tied formats — `docs/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md` |

---

## Repeat guardrail (arm configs — do not rerun without new prereg)

See `docs/exect_negative_probe_synthesis_20260520.md` for ExECT probe **config IDs**.  
These are **arm-reject**, not mechanism-reject for the rows in that doc.

---

## Next status updates expected

- After ExECT S1 stage-graph cap-25 → stage-count mechanism rows for ExECT S1
- Optional 50-record Gan presentation confirmation before operational default format change

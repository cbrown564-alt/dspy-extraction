# Gan S0 Stage-Executor GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_stage_executor_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 2 — per-stage executor (candidate source) |
| Comparison group | `gan_s0_stage_executor_gpt_cap25_v1` |
| Primary varied factor | `stage_executor` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No (directional mechanism review below; class not closed) |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` cap-25, scorer `gan_frequency_deterministic_v1`, single-pass adjudication v1.1 downstream, required model-quote evidence.

## Arms

| arm_id | stage_executor | run_id | monthly | purist | pragmatic | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| E1 | `det_candidates_llm_adjudicate` | `gan_s0_stage_executor_e1_det_candidates_cap25_gpt4_1_mini_20260521T013003Z` | **52.0%** | 60.0% | 76.0% | 100% | 100% | 25 |
| E3 | `hybrid_candidates_llm_adjudicate` | `gan_s0_stage_executor_e3_hybrid_candidates_cap25_gpt4_1_mini_20260521T013205Z` | 41.7% | 58.3% | 79.2% | 96% | 100% | 24 |
| E4 | `det_candidates_llm_adjudicate_llm_vr` | `gan_s0_stage_executor_e4_det_vr_cap25_gpt4_1_mini_20260521T013234Z` | **52.0%** | 60.0% | 76.0% | 100% | 100% | 25 |
| E2 | `llm_candidates_llm_adjudicate` | `gan_s0_stage_executor_e2_llm_candidates_cap25_gpt4_1_mini_20260521T013007Z` | 29.2% | 50.0% | 70.8% | 96% | 100% | 24 |
| E5 | `llm_candidates_llm_adjudicate_llm_vr` | `gan_s0_stage_executor_e5_llm_vr_cap25_gpt4_1_mini_20260521T013313Z` | 29.2% | 50.0% | 70.8% | 96% | 100% | 24 |

Rank order (monthly): **E1 = E4 (52%)** > E3 (41.7%) > E2 = E5 (29.2%).

Phase 2 A3 reproduction: E1 matches A3 (`…T012204Z`) at **52.0%** monthly on the same 25 records.

## Prediction overlap

| Pair | Identical `raw_value` / 25 | Notes |
| --- | ---: | --- |
| E1 vs E4 | 25/25 | Adjudicate-then-VR is label-neutral vs adjudicate-only on this slice |
| E2 vs E5 | 22/25 | VR does not rescue LLM-candidate path |
| E2 vs E3 | 12/25 | Hybrid partially diverges from LLM-only |
| E1 vs E3 | 7/25 | Det candidates drive most E1 gains vs hybrid |
| E1 vs E2 | 6/25 | LLM candidate stage reshapes most labels |
| E1 vs E5 | 6/25 | — |
| E3 vs E4 | 7/25 | — |
| E4 vs E5 | 6/25 | — |

Contrast with Phase 2: A3 vs A5 (extract→VR skeleton) shared 15/25 labels and **lost 8pp** monthly. Here E1 vs E4 is **25/25** — VR **after adjudication** does not erase det-candidate gains.

## Gates (prereg)

| arm_id | monthly vs best (52%) | schema ≥ 95% | outcome | decision_scope |
| --- | --- | --- | --- | --- |
| E1 | best (tie) | pass | **hold** — det-candidate anchor confirmed | arm |
| E4 | best (tie) | pass | hold (diagnostic); VR placement after adjudicate is neutral | arm |
| E3 | −10.3pp | pass (96%) | reject arm; hybrid does not beat det | arm |
| E2 | −22.8pp | pass (96%) | reject arm | arm |
| E5 | −22.8pp | pass (96%) | reject arm (diagnostic) | arm |

E2/E3 each had **1 invalid** prediction (schema 96%). No full-validation spend from this group.

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| E1 | hold | arm | Reproduces Phase 2 A3; det candidates + LLM adjudicate remains cap-25 winner |
| E4 | hold | arm | Label-identical to E1; adjudicate→VR ≠ extract→VR (Phase 2 A5 failure mode) |
| E3 | reject | arm | +12.5pp vs LLM-only but −10.3pp vs det; merge adds cost without beating det |
| E2 | reject | arm | LLM JSON candidate generation underperforms det on matched downstream |
| E5 | reject | arm | VR cannot recover LLM-candidate deficit |

## Mechanism review (directional — not mechanism reject)

- **Arms cited:** E1, E2, E3 (primary); E4, E5 (VR diagnostic).
- **Implementations tested:** deterministic `temporal_candidates.py` vs LLM JSON candidate generation vs merged hybrid; shared adjudication signature and v1.1 policy.
- **Conclusion:** All three primary cells agree **det > hybrid > LLM** on monthly frequency (−10pp hybrid, −23pp LLM vs det). Operational default should **retain deterministic candidate generation** for `g2_candidates_adjudicate`. Mechanism class **LLM temporal candidate generation** stays **open** — only one LLM presentation (JSON list) tested; cap-25 search only; no full validation.

## Phase 4 recommendation

Proceed **Axis 3 implementation sweep** on **`g2_candidates_adjudicate` + `det_candidates_llm_adjudicate`** (E1/E4 skeleton):

- Candidate presentation variants (`cand_table_v1`, `cand_json_v1`, `cand_bullets_v1`) if testing det presentation — or skip if det primitive is frozen.
- Do **not** spend Axis 3 budget replaying LLM-only candidate generation without a new `implementation_variant` in prereg.
- Optional: promote E4 adjudicate→VR path only after full validation confirms E1 band; cap-25 shows VR-neutral, not VR-helpful.

## Open cells (explicit)

- LLM candidate **presentation** variants (table vs prose vs structured tool).
- Full validation of E1 on 50-record slice or full split.
- Qwen port of winning det-candidate cell only.
- Whether hybrid merge helps under a different LLM candidate prompt or presentation.
- ExECT S1 stage-graph grid remains blocked until Gan Axis 3 or full-validation gate on E1.

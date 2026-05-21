# Gan S0 Stage-Executor GPT Cap-25 v1 Preregistration

Date: 2026-05-21  
Status: Cap-25 complete — see `docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md`  
Comparison group: `gan_s0_stage_executor_gpt_cap25_v1`  
Related: `docs/hybrid_pipeline_exploration_implementation_plan_20260521.md`, `docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`, `docs/hybrid_pipeline_mechanism_status_20260521.md`

## Research Question

On the Phase 2 winning graph `g2_candidates_adjudicate`, who should build temporal candidates — deterministic rules, LLM extraction, or a merged hybrid — when downstream adjudication stays LLM single-pass?

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 2 — per-stage executor (det vs LLM vs hybrid) |
| Comparison group | `gan_s0_stage_executor_gpt_cap25_v1` |
| Primary varied factor | `stage_executor` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No (mechanism review only if ≥2 candidate implementations agree directionally) |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records, same order as Phase 2 / Lane A cap-25 |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Primary metric | Monthly frequency accuracy |
| Diagnostics | Purist category, Pragmatic category, schema-valid prediction rate, evidence support, valid/invalid count |
| Downstream adjudication | Single-pass LLM adjudicate (`temporal_candidates_single_pass_v1_1` policy) |
| Evidence policy | Required model quote |
| Stage graph | `g2_candidates_adjudicate` for E1–E3; E4–E5 add LLM verify-repair after adjudication (diagnostic VR cells) |

## Prompt / call budget (documented confound)

| Executor cell | LLM calls per record | Candidate context |
| --- | ---: | --- |
| E1 det candidates | 1 (adjudicate only) | Deterministic `temporal_candidates.py` injected pre-adjudicate |
| E2 LLM candidates | 2 (generate candidates → adjudicate) | Model-generated candidate JSON, note-filtered to contiguous spans |
| E3 hybrid merge | 2 (generate candidates → adjudicate) | Deterministic + LLM candidates merged and deduped pre-adjudicate |
| E4 det + VR | 2 (adjudicate → temporal VR) | Same deterministic candidate injection as E1 |
| E5 LLM + VR | 3 (generate → adjudicate → temporal VR) | Same LLM candidate stage as E2 |

Det-candidate arms receive the same adjudication signature and v1.1 policy as Phase 2 arm A3. LLM-candidate arms add one upstream generation pass; this is the isolation target, not a hidden confound to erase in code.

## Arms

| Arm | stage_executor | Candidate stage | Adjudication | Repair | program_variant | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| E1 | `det_candidates_llm_adjudicate` | deterministic | LLM | none | `gan_frequency_s0_temporal_candidates_single_pass` | Required — A3 reproduction |
| E2 | `llm_candidates_llm_adjudicate` | LLM | LLM | none | `gan_frequency_s0_llm_temporal_candidates_single_pass` | Required |
| E3 | `hybrid_candidates_llm_adjudicate` | det + LLM merge | LLM | none | `gan_frequency_s0_hybrid_temporal_candidates_single_pass` | Required |
| E4 | `det_candidates_llm_adjudicate_llm_vr` | deterministic | LLM | LLM VR | `gan_frequency_s0_temporal_candidates_adjudicate_verify_repair` | Optional diagnostic |
| E5 | `llm_candidates_llm_adjudicate_llm_vr` | LLM | LLM | LLM VR | `gan_frequency_s0_llm_temporal_candidates_verify_repair` | Optional diagnostic |

Phase 2 baseline for E1: A3 monthly **52.0%** (`gan_s0_stage_graph_g2_candidates_adjudicate_cap25_gpt4_1_mini_20260521T012204Z`).

## Explicit Non-Goals

- Do not vary stage graph among E1–E3 (all `g2_candidates_adjudicate`).
- Do not test candidate presentation variants (table vs JSON vs prose).
- Do not change scorer, split, model, or evidence policy.
- Do not claim mechanism reject for deterministic vs LLM candidate generation from cap-25 alone.
- Do not start ExECT S1 stage-graph grid until this inspection lands.

## Gates

| Decision | Rule |
| --- | --- |
| Rank arms | Order by monthly frequency; use Purist/Pragmatic, schema validity, evidence support as diagnostics |
| Hold | Within 3pp of best monthly, or qualitatively distinct failure modes |
| Reject arm | >3pp below best without diagnostic benefit, or schema-valid rate < 95% |
| Mechanism review | Only if E1/E2/E3 (or E4/E5 pair) agree directionally on candidate-source effect |
| Full validation | Deferred until cap-25 winner confirmed |

## Inspection Requirements

- Run IDs for all arms.
- Taxonomy block with `decision_scope: arm`.
- Metrics table vs E1 (A3 reproduction) and Phase 2 A3 run.
- Prediction overlap E1 vs E2/E3/E4/E5.
- Prompt-call budget noted per arm.
- Open cells: candidate presentation, Qwen port, full validation.

## Open Cells

- `implementation_variant`: candidate presentation format for LLM generation output.
- Axis 3 sweeps on winning executor assignment.
- Qwen confirmation of cap-25 winner.
- Full validation on 50-record slice or full split.

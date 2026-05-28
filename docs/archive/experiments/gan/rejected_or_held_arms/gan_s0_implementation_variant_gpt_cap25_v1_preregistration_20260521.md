# Gan S0 Implementation-Variant GPT Cap-25 v1 Preregistration

Date: 2026-05-21  
Status: Cap-25 complete — see `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md`  
Comparison group: `gan_s0_implementation_variant_gpt_cap25_v1`  
Related: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`, `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md`

## Research Question

Does deterministic temporal-candidate **presentation** (prose vs table vs JSON vs bullets) change Gan S0 monthly frequency when stage graph and executor are fixed at the Phase 2–3 winners?

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation variant |
| Comparison group | `gan_s0_implementation_variant_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records (Lane A order) |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Primary metric | Monthly frequency accuracy |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` |
| Candidate source | Deterministic `temporal_candidates.py` (unchanged) |
| Evidence policy | Required model quote |
| LLM calls | One adjudication pass per record |

## Arms

| Arm | implementation_variant | Presentation | Config |
| --- | --- | --- | --- |
| I0 | `cand_prose_v1` | Numbered prose (E1 reproduction control) | `gan_s0_impl_i0_cand_prose_cap25_gpt4_1_mini.json` |
| I1 | `cand_table_v1` | Markdown table | `gan_s0_impl_i1_cand_table_cap25_gpt4_1_mini.json` |
| I2 | `cand_json_v1` | JSON object with `candidates` array | `gan_s0_impl_i2_cand_json_cap25_gpt4_1_mini.json` |
| I3 | `cand_bullets_v1` | Bullet list | `gan_s0_impl_i3_cand_bullets_cap25_gpt4_1_mini.json` |

## Explicit Non-Goals

- Do not vary stage graph, candidate source, prompt policy, evidence policy, or model.
- Do not replay LLM-only or hybrid candidate generation (Phase 3 arm rejects).
- Do not add verify-repair after adjudication in this group.
- Do not claim mechanism reject for “candidate presentation” from fewer than two distinct presentation families with directional agreement.

## Gates

| Decision | Rule |
| --- | --- |
| Rank arms | Order by monthly frequency; diagnostics: Purist/Pragmatic, schema validity, evidence support |
| Hold | Within 3pp of best monthly, or qualitatively distinct failure mode |
| Reject arm | >3pp below best without diagnostic benefit, or schema-valid rate <95% |
| Full validation | None by default; only if an arm beats I0 by preregistered margin and passes mechanism review prerequisites |

## Inspection Requirements

- Taxonomy block with `decision_scope: arm`
- Run IDs for all four arms
- Prediction overlap I0 vs I1/I2/I3
- Open cells: LLM candidate presentation, tool surface, evidence policy on this skeleton

## Open Cells

- LLM temporal candidate presentation (not in scope)
- Token/context budget differences across formats (document in inspection if material)
- Qwen port of any winning presentation

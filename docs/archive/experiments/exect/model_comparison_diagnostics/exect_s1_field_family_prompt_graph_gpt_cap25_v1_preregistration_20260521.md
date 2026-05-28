# ExECT S1 Field-Family Prompt Graph GPT Cap-25 v1 Preregistration

Date: 2026-05-21  
Status: **Cap-25 complete** — see `docs/experiments/exect/exect_s1_field_family_prompt_graph_gpt_cap25_v1_inspection_20260521.md`  
Comparison group: `exect_s1_field_family_prompt_graph_gpt_cap25_v1`  
Related: `docs/planning/multi_stage_llm_clinical_extraction_literature_review_20260521.md` (Literature Card 3), `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`

## Research Question

On the Phase 5a winning skeleton `g1_l1_policy_bridges`, does field-family prompt-graph decomposition (parallel full-note per-family stages vs sequential prior-context chaining) improve S1 micro F1 versus single-pass v4_10 extraction when bridges, model, split, and scorer are fixed?

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S1 field-family (diagnosis, seizure_type, annotated_medication) |
| Research axis | 1 — decomposition on winning skeleton (literature-informed prompt graph) |
| Comparison group | `exect_s1_field_family_prompt_graph_gpt_cap25_v1` |
| Primary varied factor | `pipeline_stage_graph` |
| Anchor skeleton | `g1_l1_policy_bridges` (PG0 baseline) |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` |
| Cap | First 25 validation records (Lane A order) |
| Model | GPT 4.1-mini |
| Scorer | `exect_field_family_deterministic_v1` |
| Primary metric | Pooled micro F1 |
| Diagnostics | Per-family F1, evidence quote support, schema validity, merge-error notes |
| Prompt family | `exect_s0_s1_field_family_v4_10_label_policy` |
| Few-shot | embedded benchmark-facing label-policy examples (per-family filtered in PG1/PG2) |
| Evidence policy | Standard v4_10 quote requirement |

## Bridge Mode (all arms)

| `bridge_mode` | `repair_policy` | Meaning |
| --- | --- | --- |
| `inline` | `none` | Inline benchmark bridges after multi-family merge (same as S1/S5) |

Bridge policy is explicit and identical across arms so merge/bridge confounds do not explain arm deltas.

## Arms

| Arm | `stage_graph_id` | Program variant | Context | LLM calls/record | Config |
| --- | --- | --- | --- | ---: | --- |
| PG0 | `g1_l1_policy_bridges` | `exect_s0_s1_field_family_single_pass` | full note | 1 | `exect_s1_prompt_graph_pg0_single_pass_cap25_gpt4_1_mini.json` |
| PG1 | `g2_field_family_parallel` | `exect_s0_s1_field_family_prompt_graph_parallel` | full note per family | 3 | `exect_s1_prompt_graph_pg1_parallel_cap25_gpt4_1_mini.json` |
| PG2 | `g2_field_family_prompt_graph` | `exect_s0_s1_field_family_prompt_graph_sequential` | prior-context chain | 3 | `exect_s1_prompt_graph_pg2_sequential_cap25_gpt4_1_mini.json` |

**PG1 vs Phase 5a S5:** S5 used section-aware routing with bare per-family signatures (83.3% micro). PG1 uses **full-note** context with **v4_10 label-policy examples** per family — tests whether decomposition helps when context and policy are controlled.

**PG2:** Sequential prompt graph per Spaanderman et al. — diagnosis → seizure (with diagnosis context) → medication (with diagnosis + seizure context).

## Explicit Non-Goals

- Do not vary bridge placement, prompt policy version, model, or scorer.
- Do not re-run section-aware S5 under this group (already arm-rejected in Phase 5a).
- Do not claim mechanism reject for field-family decomposition from this cap-25 grid alone.
- Do not proceed to full validation unless an arm beats PG0 by preregistered margin.

## Gates

| Decision | Rule |
| --- | --- |
| Rank arms | Order by pooled micro F1; per-family F1 and evidence support as diagnostics |
| Hold | Within 2pp of PG0 micro F1, or distinct failure mode worth documenting |
| Reject arm | >2pp below PG0 without diagnostic benefit, or evidence support <95% |
| Full validation | None by default |

## Inspection Requirements

- Taxonomy block with `decision_scope: arm`
- Run IDs for PG0–PG2
- Bridge_mode column (all `inline`)
- Per-family F1 table and merge-error notes
- Prediction overlap PG0 vs PG1/PG2
- Comparison note vs Phase 5a S5 (section-aware, −12.5pp)
- Open cells: Qwen port, section-aware + label policy combo, det pre-candidates on prompt graph

## Frozen References

| Role | Run ID | Micro F1 |
| --- | --- | ---: |
| Phase 5a S1 (PG0 expect match) | `exect_s1_stage_graph_g1_l1_policy_bridges_cap25_gpt4_1_mini_20260521T014619Z` | 95.8% |
| Phase 5a S5 section-aware | `exect_s1_stage_graph_g3_family_split_merge_cap25_gpt4_1_mini_20260521T014634Z` | 83.3% |
| Phase 5b E1 inline repro | `exect_s1_stage_executor_e1_inline_bridges_cap25_gpt4_1_mini_20260521T014707Z` | 95.8% |

## Open Cells

- Section-aware + v4_10 per-family policy (PG1 context routing variant)
- Per-family det pre-candidates on prompt graph skeleton
- Qwen confirmation on any hold arm
- Full validation deferred

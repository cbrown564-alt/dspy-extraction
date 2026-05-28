# ExECT S1 Field-Family Prompt Graph GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/exect/exect_s1_field_family_prompt_graph_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `exect_s1_field_family_prompt_graph_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S1 field-family |
| Research axis | 1 — decomposition on winning skeleton (literature prompt graph) |
| Comparison group | `exect_s1_field_family_prompt_graph_gpt_cap25_v1` |
| Primary varied factor | `pipeline_stage_graph` |
| Anchor skeleton | `g1_l1_policy_bridges` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `exectv2_fixed_v1:validation` cap-25, v4_10 label policy, inline benchmark bridges (`repair_policy=none`), scorer `exect_field_family_deterministic_v1`.

## Arms

| arm_id | `stage_graph_id` | run_id | micro F1 | diagnosis | seizure | medication | evidence |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| PG0 | `g1_l1_policy_bridges` | `exect_s1_prompt_graph_pg0_single_pass_cap25_gpt4_1_mini_20260521T021533Z` | **95.8%** | 97.6% | 95.4% | 94.9% | 97.3% |
| PG1 | `g2_field_family_parallel` | `exect_s1_prompt_graph_pg1_parallel_cap25_gpt4_1_mini_20260521T021536Z` | 86.5% | 86.4% | 82.9% | 91.2% | 92.8% |
| PG2 | `g2_field_family_prompt_graph` | `exect_s1_prompt_graph_pg2_sequential_cap25_gpt4_1_mini_20260521T021905Z` | 87.1% | 86.4% | 84.1% | 91.2% | 91.6% |

Best micro F1: **95.8%** (PG0 single-pass baseline).

## Bridge contribution

All arms use `bridge_mode=inline` with identical post-merge bridge path. Arm deltas are attributable to extraction decomposition, not bridge placement.

## Prediction overlap

| Comparison | Identical label sets | Notes |
| --- | ---: | --- |
| PG0 vs PG1 | 14/25 | 11 records regress vs single-pass |
| PG0 vs PG2 | 14/25 | Same diff set as PG0 vs PG1 |
| PG1 vs PG2 | **24/25** | Sequential prior-context chain null vs parallel (only `EA0072` differs) |

Prior-context chaining (PG2) does **not** materially change outcomes versus parallel full-note per-family stages (PG1) on this slice.

## Comparison vs Phase 5a S5

| Arm | Micro F1 | Context | Policy per family |
| --- | ---: | --- | --- |
| S5 section-aware (Phase 5a) | 83.3% | section routing | bare signatures |
| PG1 parallel full-note | 86.5% | full note | v4_10 examples |
| PG2 sequential chain | 87.1% | full note + prior context | v4_10 examples |

Full-note + label policy per family recovers **+3.2pp to +3.8pp** vs S5, but remains **−8.7pp to −9.3pp** below single-pass PG0.

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| PG0 | **Hold** | arm | Matches Phase 5a S1/E1 (95.8%); anchor confirmed |
| PG1 | **Reject (arm)** | arm | −9.3pp vs PG0; seizure F1 −12.5pp |
| PG2 | **Reject (arm)** | arm | −8.7pp vs PG0; null vs PG1 (24/25 identical) |

## Gates applied

| Rule | Result |
| --- | --- |
| Rank by micro F1 | PG0 leads; PG2 slightly above PG1 |
| Hold within 2pp of PG0 | PG0 only |
| Reject >2pp below PG0 | PG1, PG2 reject |
| Evidence support ≥95% | PG0 pass; PG1/PG2 fail (92.8%, 91.6%) |

## Mechanism review

Not applicable — `decision_scope: arm` only. Do **not** mechanism-close field-family decomposition or prompt-graph chaining from this grid.

Directional read:

- Single-pass monolithic extraction with inline bridges remains best on GPT cap-25.
- Per-family decomposition hurts seizure-type F1 most (95.4% → 82.9–84.1%), consistent with co-list / secondary-generalisation merge errors in multi-call paths.
- Sequential prior-context chaining adds no measurable gain over parallel per-family calls.

## Operational recommendation

- **Do not** promote prompt-graph or parallel per-family decomposition for ExECT S1 operational default.
- Keep `g1_l1_policy_bridges` single-pass as the winning skeleton for Axis 2–3 work.
- Literature Card 3 question answered at arm level: decomposition does not beat single-pass under controlled bridges on this slice.

## Open cells

- Section-aware + v4_10 per-family policy (combine S5 routing with PG1 policy)
- Per-family det pre-candidates on prompt-graph skeleton
- Qwen port of PG1/PG2 (literature hypothesized weaker-model gains — not tested)
- Full validation deferred (both decomposition arms reject cap-25 gate)

## Registry

Run `scripts/backfill_hybrid_cap25_registry.py` to append PG0–PG2 rows with `decision_scope: arm`.

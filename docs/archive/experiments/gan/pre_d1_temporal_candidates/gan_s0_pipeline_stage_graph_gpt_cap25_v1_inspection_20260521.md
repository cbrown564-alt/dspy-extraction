# Gan S0 Pipeline Stage-Graph GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_pipeline_stage_graph_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Comparison group | `gan_s0_pipeline_stage_graph_gpt_cap25_v1` |
| Research axis | 1 — pipeline stage graph / decomposition |
| Primary varied factor | `pipeline_stage_graph` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` cap-25 (same order as Lane A), scorer `gan_frequency_deterministic_v1`, deterministic `temporal_candidates.py` only where a candidate stage exists, v1.1 prompt family on temporal arms.

## Arms

| arm_id | stage_graph_id | run_id | monthly | purist | pragmatic | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A1 | `g1_direct` | `gan_s0_stage_graph_g1_direct_cap25_gpt4_1_mini_20260521T012156Z` | 44.0% | 64.0% | 72.0% | 100% | 100% | 25 |
| A2 | `g2_extract_repair` | `gan_s0_stage_graph_g2_extract_repair_cap25_gpt4_1_mini_20260521T012200Z` | 44.0% | 56.0% | 68.0% | 100% | 100% | 25 |
| A3 | `g2_candidates_adjudicate` | `gan_s0_stage_graph_g2_candidates_adjudicate_cap25_gpt4_1_mini_20260521T012204Z` | **52.0%** | 60.0% | 76.0% | 100% | 100% | 25 |
| A4 | `g3_extract_verify_repair` | `gan_s0_stage_graph_g3_extract_verify_repair_cap25_gpt4_1_mini_20260521T012239Z` | 44.0% | 56.0% | 68.0% | 100% | 100% | 25 |
| A5 | `g3_candidates_extract_repair` | `gan_s0_stage_graph_g3_candidates_extract_repair_cap25_gpt4_1_mini_20260521T012243Z` | 44.0% | 64.0% | 72.0% | 100% | 100% | 25 |

Rank order (monthly): **A3 (52%)** > A1/A2/A4/A5 (44% tie band).

## Prediction overlap

| Pair | Identical `raw_value` / 25 | Notes |
| --- | ---: | --- |
| A1 vs A5 | 25/25 | Direct ≡ promoted temporal+VR skeleton on labels |
| A2 vs A4 | 25/25 | Same verify-repair implementation; stage_graph_id metadata only |
| A1 vs A3 | 15/25 | A3 differs on 10 records; +8pp monthly |
| A3 vs A5 | 15/25 | Same 10 diffs as A1 vs A3 — verify-repair reverses A3 gains on this slice |
| A1 vs A2 | 17/25 | Verify-repair perturbs labels without monthly lift vs direct |

Sample A3-only wins (vs A1/A5): `gan_1794`, `gan_4113`, `gan_16825`, `gan_9566`, `gan_16772`.

## Gates (prereg)

| arm_id | monthly vs best (52%) | schema ≥ 95% | outcome | decision_scope |
| --- | --- | --- | --- | --- |
| A3 | best | pass | **hold for Axis 2** | arm |
| A1 | −8pp | pass | reject arm (no diagnostic benefit vs A3) | arm |
| A2 | −8pp | pass | reject arm | arm |
| A4 | −8pp | pass | reject arm (duplicate of A2) | arm |
| A5 | −8pp | pass | reject arm on cap-25 search | arm |

All arms pass schema and evidence diagnostics. No full-validation spend from this group (per prereg).

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| A3 | hold | arm | Best monthly on cap-25; candidates→adjudicate without repair beats full promoted skeleton |
| A1 | reject | arm | Tied 44%; byte-identical to A5 |
| A2 | reject | arm | Verify-repair regresses purist/pragmatic vs direct |
| A4 | reject | arm | Label duplicate of A2 |
| A5 | reject | arm | Operational skeleton unchanged on cap-25; VR stage removes A3 monthly lift |

## Mechanism review

Not applicable — no mechanism reject or promote claims from this cap-25 grid.

## Phase 3 recommendation

Proceed **`gan_s0_stage_executor_gpt_cap25_v1`** on:

1. **`g2_candidates_adjudicate`** (A3 winner) — test det vs LLM vs hybrid candidate generation with single-pass adjudication downstream.
2. **`g3_candidates_extract_repair`** (operational skeleton) — optional executor cells if Axis 2 needs to explain why VR negates A3 gains on this slice.

Do **not** spend Axis 2 budget on `g1_direct` or verify-repair-only graphs from this draw.

## Open cells (explicit)

- `stage_executor`: LLM temporal candidate generation; det+LLM merge.
- `implementation_variant`: candidate presentation (table vs JSON vs prose).
- Model transfer: Qwen confirmation deferred.
- Full validation: deferred until Axis 2 winner.
- Mechanism classes (verify-repair necessity, optimal stage count): **remain open** — cap-25 search only.

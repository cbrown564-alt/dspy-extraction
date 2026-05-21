# Gan S0 Implementation-Variant GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_implementation_variant_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation variant (candidate presentation) |
| Comparison group | `gan_s0_implementation_variant_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` cap-25, scorer `gan_frequency_deterministic_v1`, deterministic `temporal_candidates.py`, v1.1 adjudication prompt, required model-quote evidence.

## Arms

| arm_id | implementation_variant | run_id | monthly | purist | pragmatic | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| I1 | `cand_table_v1` | `gan_s0_impl_i1_cand_table_cap25_gpt4_1_mini_20260521T013745Z` | **56.0%** | 64.0% | 80.0% | 100% | 100% | 25 |
| I2 | `cand_json_v1` | `gan_s0_impl_i2_cand_json_cap25_gpt4_1_mini_20260521T013756Z` | **56.0%** | 64.0% | 80.0% | 100% | 100% | 25 |
| I3 | `cand_bullets_v1` | `gan_s0_impl_i3_cand_bullets_cap25_gpt4_1_mini_20260521T013808Z` | **56.0%** | 64.0% | 80.0% | 100% | 100% | 25 |
| I0 | `cand_prose_v1` | `gan_s0_impl_i0_cand_prose_cap25_gpt4_1_mini_20260521T013740Z` | 52.0% | 60.0% | 76.0% | 100% | 100% | 25 |

Rank order (monthly): **I1 = I2 = I3 (56%)** > I0 (52%, E1 reproduction control).

## Prediction overlap

| Pair | Identical `raw_value` / 25 | Notes |
| --- | ---: | --- |
| I0 vs I1 | 23/25 | +4pp monthly; diffs on `gan_14485`, `gan_14881` |
| I0 vs I2 | 22/25 | Same headline as I1; one additional diff vs I1 |
| I0 vs I3 | 22/25 | Same headline as I1 |
| I1 vs I2 | 22/25 | Table and JSON not label-identical |
| I1 vs I3 | 22/25 | Table and bullets not label-identical |

Presentation change is **mostly label-neutral** but not fully — alternate formats shift 2–3 labels on this slice.

## Gates (prereg)

| arm_id | monthly vs best (56%) | schema ≥ 95% | outcome | decision_scope |
| --- | --- | --- | --- | --- |
| I1 | best (tie) | pass | **hold** — table presentation | arm |
| I2 | best (tie) | pass | **hold** — JSON presentation | arm |
| I3 | best (tie) | pass | **hold** — bullet presentation | arm |
| I0 | −4.0pp | pass | reject arm (repro control; prose not best on cap-25) | arm |

No full-validation spend from this group unless a single presentation is chosen after tie-break (e.g. table for readability).

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| I1 | hold | arm | +4pp vs prose; 23/25 label match with I0 |
| I2 | hold | arm | Tied best; not identical to I1 labels |
| I3 | hold | arm | Tied best; not identical to I1 labels |
| I0 | reject | arm | Reproduces Phase 3 E1 at 52%; prose underperforms alt formats here |

## Mechanism review (directional — not mechanism reject)

- **Arms cited:** I0, I1, I2, I3 (four presentation families).
- **Implementations tested:** deterministic candidate payload formatted as numbered prose, markdown table, JSON blob, or bullets — same primitive output, same adjudication signature.
- **Conclusion:** Three non-prose presentations agree **+4pp monthly** vs prose on cap-25 (56% vs 52%) with high but incomplete label overlap. Mechanism class **candidate table vs JSON vs prose (Gan)** stays **open** — cap-25 search only; no full validation; tied arms need tie-break before operational update.

## Phase 5 recommendation

Unblock **ExECT S1 stage-graph grid** (`exect_s1_pipeline_stage_graph_gpt_cap25_v1`) per implementation plan. Optional Gan follow-up: pick one presentation (e.g. `cand_table_v1`) for 50-record slice confirmation before changing operational default formatting.

## Open cells (explicit)

- Full validation of winning presentation vs prose control.
- Token/latency cost of table vs JSON vs bullets (not measured here).
- LLM candidate presentation (Phase 3 reject path — separate mechanism).
- Qwen port of presentation winner only after Gan Axis 3 confirmation.

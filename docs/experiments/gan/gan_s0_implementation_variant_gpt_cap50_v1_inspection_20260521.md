# Gan S0 Implementation-Variant GPT Cap-50 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_preregistration_20260521.md`  
Parent cap-25: `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md`  
Comparison group: `gan_s0_implementation_variant_gpt_cap50_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation variant (50-record confirmation) |
| Comparison group | `gan_s0_implementation_variant_gpt_cap50_v1` |
| Primary varied factor | `implementation_variant` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` first 50 IDs (cap-25 strict prefix), deterministic temporal candidates, adjudication v1.1, scorer `gan_frequency_deterministic_v1`.

## Arms

| arm_id | implementation_variant | run_id | monthly | purist | pragmatic | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| I0 | `cand_prose_v1` | `gan_s0_impl_i0_cand_prose_cap50_gpt4_1_mini_20260521T021111Z` | **62.0%** | 70.0% | 80.0% | 100% | 100% | 50 |
| I1 | `cand_table_v1` | `gan_s0_impl_i1_cand_table_cap50_gpt4_1_mini_20260521T021149Z` | **62.0%** | 70.0% | 80.0% | 100% | 100% | 50 |

**Monthly delta (I1 − I0):** **0.0pp** on 50 records.

Cap-25 reference (same arms, 25 records): I1 56.0% vs I0 52.0% (**+4.0pp**).

## Prediction overlap

| Slice | Identical `raw_value` | Diff record IDs |
| --- | ---: | --- |
| Full cap-50 | **45/50** | `gan_14485`, `gan_14881`, `gan_10047`, `gan_12810`, `gan_12130` |
| Cap-25 prefix (records 1–25) | **23/25** | `gan_14485`, `gan_14881` (same as cap-25 grid) |

Records 26–50 add three label disagreements (`gan_10047`, `gan_12810`, `gan_12130`) but **net monthly accuracy is unchanged** — errors on those IDs are symmetric (table and prose miss or hit gold the same way on monthly metric).

## Confirmation gates (prereg)

| Gate | Rule | Result |
| --- | --- | --- |
| Confirm | I1 monthly ≥ I0 + **2.0pp**, schema ≥ 95% both | **Fail** — 0.0pp delta |
| Hold (inconclusive) | I1 > I0 but < +2pp, or within 1pp | **Pass** — exact tie |
| Reject confirm | I1 ≤ I0 | **Fail** — tie, not reject |
| Schema | ≥ 95% | **Pass** — 100% both |

**Confirmation outcome:** **hold (inconclusive)** — cap-25 **+4pp** advantage for table does **not** replicate on the 50-record prefix superset.

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| I1 | hold (inconclusive) | arm | Tied prose on cap-50; do not promote operational format change from this draw |
| I0 | hold | arm | 62% monthly on 50 (vs 52% on cap-25 — records 26–50 lift both arms equally) |

## Mechanism review

Not applicable for mechanism closure.

Directional read:

- Presentation format remains **mostly label-neutral** (45/50 identical) but cap-25 **+4pp** was **not stable** when extending to 50 records.
- The two cap-25 disagreeing IDs persist; three additional diffs appear in records 26–50 without separating monthly accuracy.
- Mechanism class **candidate presentation (Gan)** stays **open** — cap-50 null does not confirm table > prose for operational default.

## Operational recommendation

- **Do not** change default `format_temporal_candidates_for_prompt` to table based on cap-50 alone.
- **Optional follow-up:** full validation on one format only if cap-25 +4pp is revisited with tie-break (e.g. readability/latency); or re-run cap-50 with fixed seed / cost logging.
- Keep promoted extraction path (`g3_candidates_extract_repair` operational) unchanged; presentation sweep was on `g2_candidates_adjudicate` skeleton only.

## Open cells

- Full 299-record validation for presentation
- I2 JSON / I3 bullets on cap-50 (not run — only needed if tie-break required)
- Qwen port
- Code change to operational default formatter

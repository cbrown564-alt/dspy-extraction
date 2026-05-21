# Gan S0 Implementation-Variant GPT Cap-50 v1 — Pre-Registration

Date: 2026-05-21  
Status: **Complete** — `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_inspection_20260521.md`  
Comparison group: `gan_s0_implementation_variant_gpt_cap50_v1`  
Parent cap-25: `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_preregistration_20260521.md`  
Cap-25 inspection: `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap25_v1_inspection_20260521.md`

## Research question

On the first **50** validation records (superset of the cap-25 Lane A prefix), does `cand_table_v1` presentation maintain the **+4pp monthly** advantage over `cand_prose_v1` observed on cap-25, supporting a candidate operational change to table formatting in deterministic temporal-candidate prompts?

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation variant (confirmation) |
| Comparison group | `gan_s0_implementation_variant_gpt_cap50_v1` |
| Primary varied factor | `implementation_variant` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope target | `arm` (operational note only if confirm gate passes) |
| Mechanism closure allowed? | No |

## Fixed controls

Same as cap-25 group except **cap = 50** (first 50 IDs in `gan_2026_fixed_v1:validation`, preserving cap-25 as strict prefix).

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | 50 records |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` |
| Candidate source | Deterministic `temporal_candidates.py` |
| Evidence | Required model quote |
| LLM calls | One adjudication pass per record |

## Arms (paired confirmation only)

| Arm | implementation_variant | Config |
| --- | --- | --- |
| I0 | `cand_prose_v1` | `gan_s0_impl_i0_cand_prose_cap50_gpt4_1_mini.json` |
| I1 | `cand_table_v1` | `gan_s0_impl_i1_cand_table_cap50_gpt4_1_mini.json` |

JSON and bullets arms (I2/I3) are **not** re-run on cap-50 unless I1 fails confirm and tie-break is needed.

## Confirmation gates

| Outcome | Rule |
| --- | --- |
| **Confirm** | I1 monthly ≥ I0 monthly **+ 2.0pp** on 50 records, and both arms schema-valid rate ≥ 95% |
| **Hold (inconclusive)** | I1 monthly > I0 but delta < 2.0pp, or within 1.0pp (null band) |
| **Reject confirm** | I1 monthly ≤ I0 monthly |
| **Operational note** | Confirm does **not** mechanism-close presentation; it only unlocks *considering* default format change pending mechanism review |
| **Full validation** | Not triggered from cap-50 alone |

Cap-25 reference: I1 56.0% vs I0 52.0% (+4.0pp), 23/25 label overlap.

## Inspection requirements

- Taxonomy with `decision_scope: arm`
- Monthly, Purist/Pragmatic, schema validity, evidence support
- Label overlap on cap-25 prefix (records 1–25) vs cap-50 full slice
- Explicit: no mechanism reject for presentation class

## Open cells

- Full 299-record validation
- I2/I3 tie-break if I1 fails confirm
- Qwen port
- Operational default change in `gan_frequency_s0` prompt formatter (code change separate from this run)

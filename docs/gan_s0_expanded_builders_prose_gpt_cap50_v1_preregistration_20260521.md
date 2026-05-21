# Gan S0 Expanded Builders Prose GPT Cap-50 v1 — Pre-Registration

Date: 2026-05-21  
Status: **Complete** — `docs/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md`  
Comparison group: `gan_s0_expanded_builders_prose_gpt_cap50_v1`  
Parent plan: `docs/hybrid_pipeline_exploration_implementation_plan_20260521.md` (item 15)  
Builder expansion: `docs/gan_s0_residual_candidate_builder_expansion_20260521.md`  
Residual replay: `docs/gan_s0_exact_frequency_slot_payload_residual_slice_replay_v2_20260521.md`

## Research question

On the first **50** validation records (Lane A prefix, same draw as `gan_s0_implementation_variant_gpt_cap50_v1`), does the **post-2026-05-21 expanded** deterministic temporal-candidate builder surface improve **monthly-frequency accuracy** versus the **pre-expansion** prose adjudication baseline, without schema or evidence regressions?

This is a **confirmatory re-run** (single arm), not a presentation sweep. Presentation stays `cand_prose_v1`; slot-payload is out of scope.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation (deterministic candidate surface) |
| Comparison group | `gan_s0_expanded_builders_prose_gpt_cap50_v1` |
| Primary varied factor | `implementation_variant` (`cand_prose_expanded_builders_v1`) |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | 50 records (strict prefix of validation order; superset of cap-25) |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` |
| Presentation | `cand_prose_v1` (prose candidate list) |
| Candidate source | Deterministic `temporal_candidates.py` (**expanded builders**, commit after 2026-05-21) |
| Evidence | Required model quote |
| LLM calls | One adjudication pass per record |
| Repair / verifier | None |

## Arms

| Arm | implementation_variant | Config |
| --- | --- | --- |
| B0 | `cand_prose_expanded_builders_v1` | `gan_s0_expanded_builders_prose_cap50_gpt4_1_mini.json` |

No simultaneous in-session control arm. **Historical baseline** for paired read:

| Baseline | Run ID | Monthly | Builders |
| --- | --- | ---: | --- |
| Pre-expansion I0 prose cap-50 | `gan_s0_impl_i0_cand_prose_cap50_gpt4_1_mini_20260521T021111Z` | 62.0% | Pre-expansion |

Cap-25 Lane-A anchors (same presentation, pre-expansion builders):

| Reference | Run ID | Monthly |
| --- | --- | ---: |
| E1 / I0 prose cap-25 | `gan_s0_stage_executor_e1_det_candidates_cap25_gpt4_1_mini_20260521T012204Z` (or I0 `…T013740Z`) | 52.0% |

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| Monthly frequency accuracy | **Primary** |
| Normalized-label exact | Secondary |
| Purist / Pragmatic category | Guardrail |
| Schema-valid prediction rate | Gate ≥ 95% |
| Evidence quote support | Gate ≥ 96% |

## Confirmation gates (vs pre-expansion cap-50 baseline)

| Outcome | Rule |
| --- | --- |
| **Confirm (arm)** | B0 monthly ≥ baseline **+ 3.0pp** (≥ 65.0% if baseline 62.0%), and both gates pass |
| **Hold (inconclusive)** | B0 monthly > baseline but delta < 3.0pp, or within 1.0pp null band |
| **Reject confirm** | B0 monthly ≤ baseline monthly |
| **Operational note** | Confirm unlocks *considering* promoting expanded builders as default det surface; does **not** mechanism-close det-candidate generation |
| **Full validation** | Not triggered from cap-50 alone |

Residual-queue reference (not a gate for this run): v2 replay S0 prose **63.3%** on 30 hard records (`docs/gan_s0_exact_frequency_slot_payload_residual_slice_replay_v2_20260521.md`).

## Inspection requirements

- Taxonomy with `decision_scope: arm`
- Label delta vs pre-expansion cap-50 baseline on shared 50 IDs
- Cap-25 prefix (records 1–25) delta vs cap-25 E1/I0 prose
- Stratum note if ≥5 records flip wrong→right on arithmetic/unknown/cluster tags from residual read
- Explicit: no mechanism reject for det-candidate class

## Open cells

- Full 299-record validation
- Table presentation + expanded builders (only if prose confirm passes)
- Qwen port
- Slot-payload v1 with expanded builders (deprioritized after residual v2)

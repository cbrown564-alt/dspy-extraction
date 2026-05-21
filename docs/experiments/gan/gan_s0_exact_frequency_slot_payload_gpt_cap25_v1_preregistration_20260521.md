# Gan S0 Exact-Frequency Slot Payload GPT Cap-25 v1 — Preregistration

Date: 2026-05-21  
Status: Complete — `docs/experiments/gan/gan_s0_exact_frequency_slot_payload_gpt_cap25_v1_inspection_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (Phase 8 — residual mechanism follow-up)  
Parent synthesis: `docs/experiments/gan/gan_s0_exact_frequency_residual_manual_read_20260521.md`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation variant (structured candidate slot payload) |
| Comparison group | `gan_s0_exact_frequency_slot_payload_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Hypothesis

Exposing deterministic temporal candidates as a **structured slot payload** (event count, seizure type, denominator provenance, cluster slots, unknown-policy cues) improves **monthly-frequency accuracy** on cap-25 versus the current prose candidate presentation, without increasing unknown/no-reference confusions or schema/evidence regressions.

## Motivation

Residual manual read (`docs/experiments/gan/gan_s0_exact_frequency_residual_manual_read_20260521.md`) identified five recurring mechanisms on the 30-record error queue:

- highest-frequency seizure-type selection failure (5 records)
- calendar/window aggregation failure (5)
- unknown denominator hallucination (6)
- cluster slot omission/spacing swap (8 combined)
- long-window residual-count compression (4)

The current candidate primitive lists canonical labels but does not expose denominator provenance, target-priority cues, or cluster slot separation. Canonical-format prompt examples (`docs/experiments/gan/gan_s0_canonical_format_port_gpt_cap25_v1_inspection_20260521.md`) improved normalized exact on cap-25 (+4pp) but **residual-slice replay was null** — prompt examples alone do not address the slot mechanisms above.

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records (Lane A order) |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Candidate source | Deterministic `temporal_candidates.py` (unchanged builders) |
| Evidence policy | Required model quote |
| LLM calls | One adjudication pass per record |
| Repair / verifier | None |

## Arms

| Arm | implementation_variant | Prompt version | Config |
| --- | --- | --- | --- |
| S0 | `cand_prose_v1` | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` | `gan_s0_slot_s0_prose_control_cap25_gpt4_1_mini.json` |
| S1 | `slot_payload_v1` | `gan_frequency_s0_temporal_candidates_single_pass_v1_3_slot_payload` | `gan_s0_slot_s1_payload_cap25_gpt4_1_mini.json` |

### S1 implementation note

S1 adds:

- `src/clinical_extraction/gan/slot_payload.py` — structured slot enrichment from existing temporal candidates
- Table + JSON slot presentation via `format_slot_payload_candidates_for_prompt`
- v1.3 adjudication addendum covering seizure-type priority, denominator abstention, calendar aggregation, and cluster slot handling

Do **not** change candidate regex builders, stage graph, scorer, evidence policy, or split in this group.

## Primary and Secondary Metrics

| Metric | Role |
| --- | --- |
| Monthly frequency accuracy | **Primary** for promotion |
| Normalized-label exact | Secondary / diagnostic |
| Purist / Pragmatic category | Guardrail |
| Schema-valid prediction rate | Gate >= 95% |
| Evidence quote support | Gate >= 96% |

## Gates

| Decision | Rule |
| --- | --- |
| **Hold / promote to residual replay** | S1 monthly ≥ S0 + **3.0pp** on cap-25, schema/evidence gates pass, and no pragmatic overcall > 1 record vs S0 on cap-25 |
| **Hold (inconclusive)** | S1 monthly delta within ±2pp of S0, or lift < 3pp |
| **Reject arm** | S1 monthly < S0 − 2pp, or schema/evidence gate failure, or pragmatic regression > 2pp |
| **Mechanism closure** | Forbidden from this group alone |
| **Full validation / Qwen** | Deferred until cap-25 + residual-slice gates pass |

## Residual-Slice Plan

After cap-25 runs, replay the fixed 30-record queue from `data/fixtures/gan_s0_exact_frequency_residual_slice.json` using `scripts/replay_gan_canonical_format_residual_slice.py` (adapted or reused for S0 vs S1). Report per-group recovery on:

- `arithmetic_window_precision`
- `unknown_vs_quantified`
- `cluster_composition`
- `infrequent_long_denominator_or_boundary`

Promotion requires monthly wins concentrated in the residual groups targeted by the manual read, not only cap-25 luck.

## Required Diagnostic Readouts

- Gold-in-candidate rate (unchanged builders)
- Denominator-status distribution in slot payloads
- Per-stratum monthly accuracy: infrequent gold, unknown gold, cluster-label gold
- Residual-slice monthly recovery S1 vs S0

## Reference Runs

| Reference | Run ID suffix | Monthly | Notes |
| --- | --- | ---: | --- |
| GPT E1 executor | `…T013003Z` | 52.0% | Same skeleton as S0 |
| GPT I1 table | `…T013745Z` | 56.0% | Presentation only; different comparison group |
| GPT canonical C1 | `…T065651Z` | 52.0% | Normalized exact +4pp; monthly null vs C0 |

## Inspection Requirements

- Taxonomy block with `decision_scope: arm`
- Run IDs for S0 and S1
- Monthly (primary), normalized exact, Purist, Pragmatic, schema, evidence tables
- Residual-slice replay on shared record IDs
- Open cells: verify-repair skeleton, Qwen port, expanded candidate builders

## Open Cells

- Candidate regex builders not expanded in this group (slot enrichment only)
- Verify-repair skeleton (`g3_candidates_extract_repair`) not tested
- Qwen port deferred until GPT cap-25 + residual gates pass
- Mechanism classes “seizure-type selection”, “calendar aggregation”, “unknown denominator”, and “cluster slots” stay **open** unless ≥2 implementations agree directionally

## Explicit Non-Goals

- Do not vary stage graph, candidate source, evidence policy, or model
- Do not add verify-repair in this group
- Do not claim mechanism reject for slot payload from one presentation variant
- Do not describe results as published Gan benchmark reproduction

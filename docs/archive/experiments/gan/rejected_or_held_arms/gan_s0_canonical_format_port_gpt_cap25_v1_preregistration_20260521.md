# Gan S0 Canonical-Format Port GPT Cap-25 v1 — Preregistration

Date: 2026-05-21  
Status: Complete — `docs/experiments/gan/gan_s0_canonical_format_port_gpt_cap25_v1_inspection_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (post Phase 4; prior-best follow-up)  
Parent synthesis: `docs/experiments/synthesis/prior_best_vs_current_best_reanalysis_20260521.md`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation variant (canonical label-surface discipline) |
| Comparison group | `gan_s0_canonical_format_port_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Hypothesis

Reintroducing the prior v3/v5 canonical-format worked examples and guardrails onto the current temporal-candidates adjudicator improves **normalized-label exact** accuracy without reducing monthly, Purist, Pragmatic, schema-valid, or evidence-support metrics.

## Motivation

The promoted temporal-candidates pipeline reaches strong category metrics (GPT full validation: 65.1% monthly, 76.5% Purist, 84.2% Pragmatic) but normalized-label exact remains ~52–55%. Residual analysis (`docs/experiments/gan/gan_s0_residual_exact_frequency_error_analysis_20260521.md`) shows many misses are surface-format or cluster-assembly errors, not absence of temporal candidates. The prior v3 condition (`docs/experiments/synthesis/prior_best_config_pipeline_report.md`) carried explicit canonical-format examples that the current v1.1 adjudication prompt does not replicate in full.

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records (Lane A order) |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Candidate source | Deterministic `temporal_candidates.py` (unchanged) |
| Candidate presentation | `cand_prose_v1` (E1 reproduction control) |
| Evidence policy | Required model quote |
| LLM calls | One adjudication pass per record |
| Repair / verifier | None |

## Arms

| Arm | implementation_variant | Prompt version | Config (planned) |
| --- | --- | --- | --- |
| C0 | `canonical_format_control_v1_1` | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` | `gan_s0_canonical_c0_control_cap25_gpt4_1_mini.json` |
| C1 | `canonical_format_v3_examples_v1` | `gan_frequency_s0_temporal_candidates_single_pass_v1_2_canonical_examples` | `gan_s0_canonical_c1_v3_examples_cap25_gpt4_1_mini.json` |

### C1 implementation note (pre-run)

C1 adds a signature addendum with the v3/v5 canonical-format worked examples from `docs/experiments/synthesis/prior_best_config_pipeline_report.md` § `gan_frequency_v3_qwen35` (17 examples covering clusters, SF threshold, YTD, quarter windows, adjective rates, and `or`→`to` conversion). Do **not** change candidate generation, stage graph, scorer, evidence policy, or split.

Optional follow-up (not in this group): repeat C0/C1 on `gan_frequency_s0_temporal_candidates_verify_repair` only if C1 wins on adjudicate-only and a VR confirmation is needed.

## Primary and Secondary Metrics

| Metric | Role |
| --- | --- |
| Normalized-label exact | **Primary** for promotion |
| Monthly frequency accuracy | Guardrail — no regression > 2pp vs C0 |
| Purist / Pragmatic category | Guardrail |
| Schema-valid prediction rate | Gate >= 95% |
| Evidence quote support | Gate >= 96% |

## Gates

| Decision | Rule |
| --- | --- |
| **Hold / promote to full validation** | C1 normalized-label exact ≥ C0 + **3.0pp** on cap-25, and monthly within 2pp of C0, and both arms pass schema/evidence gates |
| **Hold (inconclusive)** | C1 improves exact but delta < 3.0pp, or monthly delta within 1pp null band |
| **Reject arm** | C1 normalized exact ≤ C0, or monthly regression > 2pp, or schema/evidence gate failure |
| **Mechanism closure** | Forbidden from this group alone |
| **Full validation** | Only if hold/promote gate passes |

## Residual-Slice Plan

After cap-25 runs, replay the fixed 30-record error-read queue from `docs/experiments/gan/gan_s0_exact_frequency_residual_slice_error_read_20260521.md` (exported via `scripts/export_gan_exact_frequency_residual_slice.py`) on C0 vs C1 predictions. Report per-group recovery on:

- `arithmetic_window_precision`
- `unknown_vs_quantified`
- `cluster_composition`
- `infrequent_long_denominator_or_boundary`

Promotion requires wins concentrated in exact-label residuals, not only broad category luck.

## Reference Runs

| Reference | Run ID suffix | Monthly | Normalized exact | Notes |
| --- | --- | ---: | ---: | --- |
| GPT E1 executor (C0 repro) | `…T013003Z` | 52.0% | — | Same skeleton as C0 |
| GPT I0 prose (C0 repro) | `…T013740Z` | 52.0% | — | Same presentation |
| GPT temporal+VR full | `…T130933Z` | 65.1% | 52.3% | Operational default; different stage graph |

## Inspection Requirements

- Taxonomy block with `decision_scope: arm`
- Run IDs for C0 and C1
- Normalized-label exact, monthly, Purist, Pragmatic, schema, evidence tables
- Residual-slice replay on shared record IDs
- Open cells: VR skeleton confirmation, Qwen port, table presentation interaction

## Open Cells

- Verify-repair skeleton (`g3_candidates_extract_repair`) not tested in this group
- Candidate presentation format (table vs prose) held at prose control
- Qwen port deferred until GPT cap-25 gate passes
- Mechanism class “canonical format examples” stays open unless ≥2 implementations agree directionally

## Explicit Non-Goals

- Do not vary stage graph, candidate source, evidence policy, or model
- Do not add verify-repair in this group
- Do not claim mechanism reject for “prompt examples” from one addendum variant
- Do not describe results as published Gan benchmark reproduction

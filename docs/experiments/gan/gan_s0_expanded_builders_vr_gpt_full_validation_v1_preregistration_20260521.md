# Gan S0 Expanded Builders VR GPT Full Validation v1 — Pre-Registration

Date: 2026-05-21  
Status: **Done** — inspection `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_20260521.md`  
Comparison group: `gan_s0_expanded_builders_vr_gpt_full_validation_v1`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`  
Trigger: F0 adjudicate-only **promote operational (arm)** at 68.1% monthly — `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_20260521.md`  
Builder expansion: `docs/experiments/gan/gan_s0_residual_candidate_builder_expansion_20260521.md`

## Research question

On the full Gan 2026 fixed validation split (299 records), does **expanded deterministic temporal-candidate builders** bundled into the promoted **`g3_candidates_extract_repair`** verify-repair skeleton (`gan_frequency_s0_temporal_candidates_verify_repair` v1.1):

1. Beat the **pre-expansion VR operational anchor** (65.1% monthly), and  
2. Match or beat **F0 adjudicate-only** expanded builders (68.1% monthly),

without schema or evidence regressions?

This tests whether verify-repair **adds or subtracts** versus single-pass adjudication when both arms share the expanded builder surface.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation (expanded builders × stage graph bundle) |
| Comparison group | `gan_s0_expanded_builders_vr_gpt_full_validation_v1` |
| Primary varied factor | `implementation_variant` (`cand_prose_expanded_builders_vr_v1`) |
| Anchor `stage_graph_id` | `g3_candidates_extract_repair` |
| Anchor `stage_executor` | n/a (g3 combined extract+VR program; no Axis-2 executor slot tag) |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` (full, no cap) |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Program | `gan_frequency_s0_temporal_candidates_verify_repair` |
| Prompt | `gan_frequency_s0_temporal_candidates_verify_repair_v1_1` |
| Candidate source | Deterministic `temporal_candidates.py` (**expanded builders**, post-2026-05-21 code) |
| Verifier | v1.1 candidate-gated confirm-first verify/repair (same policy as frozen VR anchor) |
| Evidence | Required model quote |
| LLM calls | Two per record (verify-repair) |
| Presentation | Prose candidate surface (inherited from VR prompt; not a separate formatter sweep) |

**Code note:** Expanded builders are activated in `temporal_candidates.py`, not via a separate config flag. V1 uses the **same program and prompt IDs** as the frozen VR anchor; only the deterministic candidate surface differs from the pre-2026-05-21 anchor run.

## Arms

| Arm | implementation_variant | Config |
| --- | --- | --- |
| V1 | `cand_prose_expanded_builders_vr_v1` | `gan_s0_expanded_builders_vr_full_validation_gpt4_1_mini.json` |

No in-session control arm. **External anchors** for paired read:

| Anchor | Run ID | Monthly | Stage graph | LLM calls/rec | Builders |
| --- | --- | ---: | --- | ---: | --- |
| F0 adjudicate-only (expanded) | `gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini_20260521T073432Z` | **68.1%** | `g2_candidates_adjudicate` | 1 | Expanded |
| Promoted VR (pre-expansion) | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` | 65.1% | `g3_candidates_extract_repair` | ~2 | Pre-expansion |
| Axis 1 A5 cap-25 (pre-expansion VR) | `gan_s0_stage_graph_g3_candidates_extract_repair_cap25_gpt4_1_mini_20260521T012243Z` | 44.0% | `g3_candidates_extract_repair` | ~2 | Pre-expansion; cap-25 only |

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| Monthly frequency accuracy | **Primary** |
| Normalized-label exact | Secondary |
| Purist / Pragmatic category | Guardrail |
| Schema-valid prediction rate | Gate ≥ 95% |
| Evidence quote support | Gate ≥ 95% |

## Confirmation gates

| Outcome | Rule |
| --- | --- |
| **Promote VR operational (arm)** | V1 monthly ≥ **F0 − 1.0pp** (≥ **67.1%**) **and** ≥ pre-expansion VR − 1.0pp (≥ 64.1%) **and** schema ≥ 95% **and** evidence ≥ 95% |
| **Hold — keep F0 as best monthly arm** | V1 beats pre-expansion VR by ≥ 1.0pp with gates pass, but V1 monthly **< F0 − 1.0pp** (VR bundle helps vs old anchor but loses to adjudicate-only) |
| **Hold (inconclusive)** | V1 within ±1.0pp of F0 with gates pass |
| **Reject VR bundle (arm)** | V1 monthly < **F0 − 3.0pp** **or** schema < 95% **or** evidence < 90% |
| **Mechanism** | Not closable from one arm; does not mechanism-close verify-repair placement |

### Sub-analyses (inspection)

- Monthly label delta V1 vs F0 and vs pre-expansion VR on shared record IDs
- Stratum table: unknown abstention, cluster, arithmetic/window, seizure-type-priority (from F0 residual read)
- Latency/cost vs F0 (~2× LLM calls expected)
- Whether VR repairs or worsens F0 regressions (`gan_12218`, `gan_12438`, `gan_12871`, etc.)

## Run order

1. Dry-run config (`uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_expanded_builders_vr_full_validation_gpt4_1_mini.json --env-file .env --dry-run`)
2. Full validation run (299 records; budget ~598 LLM calls)
3. Inspection `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_inspection_<date>.md`
4. Registry row with `decision_scope: arm`
5. If promote VR: update Kanban operational default **explicitly** (do not silently retag frozen anchor)

## Open cells

- Adjudicate-then-VR (`temporal_candidates_adjudicate_verify_repair`, E4-style) with expanded builders if g3 bundle null vs F0
- Qwen port of winning full-validation skeleton
- Table presentation + expanded builders (deprioritized)
- Targeted builder gaps (seizure-type priority, long-window cluster phrasing)
- LLM temporal candidates (Phase 3 E2)

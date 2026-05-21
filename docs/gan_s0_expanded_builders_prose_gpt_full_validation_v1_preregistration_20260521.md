# Gan S0 Expanded Builders Prose GPT Full Validation v1 — Pre-Registration

Date: 2026-05-21  
Status: **Ready to run**  
Comparison group: `gan_s0_expanded_builders_prose_gpt_full_validation_v1`  
Parent plan: `docs/hybrid_pipeline_exploration_implementation_plan_20260521.md` (item 17)  
Cap-50 confirm: `docs/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md` (+6pp monthly, confirm arm)  
Builder expansion: `docs/gan_s0_residual_candidate_builder_expansion_20260521.md`

## Research question

On the full Gan 2026 fixed validation split (299 records), does **prose adjudication** with **post-2026-05-21 expanded deterministic temporal-candidate builders** on `g2_candidates_adjudicate` match or beat the promoted **temporal-candidates verify-repair** operational anchor on **monthly-frequency accuracy**, without schema or evidence regressions?

This is a **confirmatory full-validation** run (single arm), triggered only after cap-50 confirm passed (+6pp vs pre-expansion prose cap-50).

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation (deterministic candidate surface) |
| Comparison group | `gan_s0_expanded_builders_prose_gpt_full_validation_v1` |
| Primary varied factor | `implementation_variant` (`cand_prose_expanded_builders_v1`) |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` (full, no cap) |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` |
| Presentation | `cand_prose_v1` |
| Candidate source | Deterministic `temporal_candidates.py` (**expanded builders**) |
| Evidence | Required model quote |
| LLM calls | One adjudication pass per record (no verify-repair) |
| Repair / verifier | None |

## Arms

| Arm | implementation_variant | Config |
| --- | --- | --- |
| F0 | `cand_prose_expanded_builders_v1` | `gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini.json` |

No in-session control arm. **External anchors** for paired read:

| Anchor | Run ID | Monthly | Stage graph | Notes |
| --- | --- | ---: | --- | --- |
| Promoted operational (VR) | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` | **65.1%** | `g3_candidates_extract_repair` | Two LLM calls; verify-repair |
| Verify-repair v2 full | `gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z` | 65.4% | direct + VR | Historical hosted anchor |
| Pre-expansion prose cap-50 | `gan_s0_impl_i0_cand_prose_cap50_gpt4_1_mini_20260521T021111Z` | 62.0% | `g2_candidates_adjudicate` | 50-record prefix only |
| Expanded builders cap-50 | `gan_s0_expanded_builders_prose_cap50_gpt4_1_mini_20260521T072655Z` | **68.0%** | `g2_candidates_adjudicate` | Confirm trigger (+6pp) |

**Important:** F0 tests a **different stage graph** than the promoted VR default (adjudicate-only vs candidates+VR). Full-validation outcome informs whether to (a) promote expanded builders inside VR, (b) promote adjudicate-only as operational, or (c) hold expanded builders as code default without changing frozen full-validation anchor.

## Primary and guardrail metrics

| Metric | Role |
| --- | --- |
| Monthly frequency accuracy | **Primary** |
| Normalized-label exact | Secondary |
| Purist / Pragmatic category | Guardrail |
| Schema-valid prediction rate | Gate ≥ 95% |
| Evidence quote support | Gate ≥ 95% (match promoted VR anchor band) |

## Confirmation gates

| Outcome | Rule |
| --- | --- |
| **Promote operational (arm)** | F0 monthly ≥ promoted VR anchor **−1.0pp** (≥ 64.1% if anchor 65.1%) **and** both gates pass **and** evidence ≥ 95% |
| **Hold (inconclusive)** | F0 monthly within ±1.0pp of VR anchor with gates pass |
| **Reject confirm** | F0 monthly < VR anchor −3.0pp **or** schema < 95% **or** evidence < 90% |
| **Operational note** | Promote does **not** mechanism-close det-candidate generation; requires inspection + optional VR-bundle follow-up |
| **Mechanism** | Not closable from one full-validation arm |

### Sub-analyses (inspection)

- Label delta vs promoted VR run on shared record IDs (expect partial overlap on validation split)
- Stratum table: arithmetic/window, unknown, cluster, seizure-type-priority residuals from `docs/gan_s0_residual_candidate_builder_expansion_20260521.md`
- Latency/cost: single-pass vs VR (diagnostic only)

## Run order

1. Dry-run config (`uv run python -m clinical_extraction.experiments.run --config configs/experiments/gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini.json --dry-run`)
2. Full validation run (299 records; budget ~299 LLM calls)
3. Inspection `docs/gan_s0_expanded_builders_prose_gpt_full_validation_v1_inspection_<date>.md`
4. Registry row with `decision_scope: arm`

## Open cells

- Bundle expanded builders into `g3_candidates_extract_repair` (VR) — separate prereg if F0 wins
- Table presentation + expanded builders full validation
- Qwen port of winning skeleton
- Targeted builder gaps (seizure-type priority, long-window cluster phrasing)
- LLM temporal candidates (Phase 3 E2)

# Gan S0 Expanded Builders Prose GPT Full Validation v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_expanded_builders_prose_gpt_full_validation_v1`  
Cap-50 confirm: `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_cap50_v1_inspection_20260521.md`

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
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` full (299 records), prose presentation, adjudication v1.1, scorer `gan_frequency_deterministic_v1`, expanded `temporal_candidates.py` builders, single LLM pass (no verify-repair).

## Arms

| arm_id | implementation_variant | run_id | monthly | purist | pragmatic | norm exact | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F0 | `cand_prose_expanded_builders_v1` | `gan_s0_expanded_builders_prose_full_validation_gpt4_1_mini_20260521T073432Z` | **68.1%** | 75.5% | 81.5% | 56.0% | 99.7% | 100% | 298/299 |

**External anchor (promoted operational VR default):**

| Reference | run_id | monthly | stage graph | LLM calls/rec |
| --- | --- | ---: | --- | ---: |
| Promoted VR + guardrails | `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` | 65.1% | `g3_candidates_extract_repair` | ~2 |
| Cap-50 expanded builders | `gan_s0_expanded_builders_prose_cap50_gpt4_1_mini_20260521T072655Z` | 68.0% | `g2_candidates_adjudicate` | 1 |

**Monthly delta (F0 − VR anchor):** **+3.0pp** (203/298 vs 194/298 correct).  
95 monthly misses vs 104 on VR (−9 misses).  
Normalized-label exact **+3.7pp** (56.0% vs 52.3%).

## Confirmation gates (prereg)

| Gate | Rule | Result |
| --- | --- | --- |
| Promote operational (arm) | F0 monthly ≥ VR − **1.0pp** (≥ 64.1%), schema ≥ 95%, evidence ≥ 95% | **Pass** — 68.1% vs 65.1%; schema 99.7%; evidence 100% |
| Hold (inconclusive) | Within ±1.0pp of VR with gates pass | N/A — clear win |
| Reject confirm | F0 < VR − 3.0pp or schema < 95% or evidence < 90% | **Fail** — not triggered |

**Confirmation outcome:** **promote operational (arm)** — expanded builders on adjudicate-only skeleton beats promoted VR monthly anchor on full validation with gates pass.

## Diagnostics

| Metric | F0 | VR anchor | Notes |
| --- | ---: | ---: | --- |
| Pragmatic category | 81.5% | 84.2% | −2.7pp; not primary gate |
| Purist category | 75.5% | 76.5% | −1.0pp |
| Missing evidence spans | 15 records | 4 records | Quote support still 100% on scored evidence rows |
| Invalid predictions | 1 (`gan_338`) | 1 (`gan_338`) | Shared `"many per month"` normalization failure |
| Prediction latency | 0.91 s/rec | 3.73 s/rec | Single-pass vs verify-repair (~4× faster) |

## Label delta vs VR anchor (monthly)

Sampled from exported monthly-mismatch IDs (partial lists in metrics JSON):

| Category | Count | Example IDs |
| --- | ---: | --- |
| Recovered (VR wrong → F0 right) | **13** | `gan_10993`, `gan_10618`, `gan_1070`, `gan_12130`, `gan_12145`, … |
| Regressed (VR right → F0 wrong) | **13** | `gan_12218`, `gan_12438`, `gan_12871`, `gan_13190`, `gan_14214`, … |
| Shared monthly misses | **7** | e.g. `gan_10074`, `gan_10434`, `gan_12667`, `gan_12679` |

Aggregate net on full split: **+9** monthly correct vs VR (matches +3.0pp). Tradeoff is not one-sided on individual IDs — expanded builders shift errors rather than uniformly fixing the VR failure set.

Recovered IDs include builder-expansion targets (`gan_10993` cluster spacing, calendar/window cases). Regressions concentrate on unknown abstention and seizure-type-adjacent frequency selection (`gan_12218`, `gan_12438`, `gan_12871`, `gan_14214`).

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| F0 | **promote operational (arm)** | arm | +3.0pp monthly vs VR anchor; gates pass; different stage graph |

## Mechanism review

Not applicable for mechanism closure.

Directional read:

- Expanded deterministic candidate surface **helps at full validation** on the primary monthly metric, confirming cap-50 (+6pp) directionally.
- **Does not** prove adjudicate-only is universally better than verify-repair — different stage graphs, pragmatic regressed, and 13/13 paired tradeoff on sampled IDs.
- Mechanism classes **det temporal candidate generation** and **verify-repair placement (Gan)** remain **open**.

## Operational recommendation

- **Record F0 as the best known full-validation monthly arm** under `g2_candidates_adjudicate` + expanded builders (68.1%).
- **Keep VR anchor frozen** for reproducibility until a preregistered **expanded-builders + VR bundle** arm is run; do not silently swap operational default without that follow-up.
- **Treat expanded builders as code default** for new Gan S0 runs (already deployed).
- **Optional next:** preregister `g3_candidates_extract_repair` with expanded builders — **Done** `docs/experiments/gan/gan_s0_expanded_builders_vr_gpt_full_validation_v1_preregistration_20260521.md`; execute V1 full validation.

## Open cells

- Bundle expanded builders into verify-repair (`g3_candidates_extract_repair`)
- Table presentation + expanded builders full validation
- Qwen port of F0 skeleton
- Targeted builder gaps (seizure-type priority, long-window cluster phrasing)
- LLM temporal candidates (Phase 3 E2)

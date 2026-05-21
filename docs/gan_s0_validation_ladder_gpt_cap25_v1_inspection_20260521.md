# Gan S0 Validation Ladder GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/gan_s0_validation_ladder_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_validation_ladder_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | Post-adjudicate validation stack |
| Comparison group | `gan_s0_validation_ladder_gpt_cap25_v1` |
| Primary varied factor | `validation_ladder_rung` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` cap-25, scorer `gan_frequency_deterministic_v1`, deterministic temporal candidates, adjudication v1.1.

## Arms

| rung | run_id | monthly | purist | pragmatic | schema | evidence | valid | invalid |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| V0 adjudicate_only | `gan_s0_validation_ladder_v0_cap25_gpt4_1_mini_20260521T014725Z` | **52.0%** | 60.0% | 76.0% | 100% | 100% | 25 | 0 |
| V2 det_plausibility | `gan_s0_validation_ladder_v2_cap25_gpt4_1_mini_20260521T014734Z` | **52.0%** | 60.0% | 76.0% | 100% | 100% | 25 | 0 |
| V3 det_evidence_grounding | `gan_s0_validation_ladder_v3_cap25_gpt4_1_mini_20260521T014738Z` | 58.3% | 66.7% | 75.0% | 48% | 100% | 12 | 13 |
| V4 llm_confirm_only | `gan_s0_validation_ladder_v4_cap25_gpt4_1_mini_20260521T014742Z` | 58.3% | 66.7% | 75.0% | 48% | 100% | 12 | 13 |
| V5 llm_verify_repair | `gan_s0_validation_ladder_v5_cap25_gpt4_1_mini_20260521T014746Z` | 58.3% | 66.7% | 75.0% | 48% | 100% | 12 | 13 |
| V6 llm_vr_det_guards | `gan_s0_validation_ladder_v6_cap25_gpt4_1_mini_20260521T014750Z` | **52.0%** | 60.0% | 76.0% | 100% | 100% | 25 | 0 |
| V7 llm_vr_det_guards_span_check | `gan_s0_validation_ladder_v7_cap25_gpt4_1_mini_20260521T014804Z` | 50.0% | 62.5% | 75.0% | 64% | 100% | 16 | 9 |

Rank order (monthly on **valid** predictions): V3/V4/V5 (58.3% on 12 valid) > V0/V2/V6 (52% on 25) > V7 (50% on 16).

## Prediction overlap (valid records only)

| Pair | Identical `raw_value` on shared valid IDs | Notes |
| --- | ---: | --- |
| V0 vs V2 | 25/25 | Det plausibility guards are label-neutral on this slice |
| V0 vs V6 | 25/25 | Reproduces Phase 3 E4 (adjudicate + VR + guards) |
| V3 vs V4 | 12/12 | Confirm-only LLM pass does not change labels vs det-evidence stack |
| V3 vs V5 | 12/12 | LLM VR without post-guards does not change labels given det-evidence front-end |
| V6 vs V7 | 16/16 on shared valid | Span-check abstains 9 records that V6 keeps |

## Gates (prereg)

| rung | monthly vs V0 (52%) | schema ≥ 95% | valid ≥ 23 | outcome | decision_scope |
| --- | --- | --- | --- | --- | --- |
| V0 | anchor | pass | pass | **hold** (baseline) | arm |
| V2 | tie | pass | pass | **hold (null)** — det guards add nothing on cap-25 | arm |
| V3 | +6.3pp on 12 valid only | **fail (48%)** | **fail (12)** | **reject** — abstention confound | arm |
| V4 | same as V3 | fail | fail | **reject** — confirm-only null vs V3 | arm |
| V5 | same as V3 | fail | fail | **reject** — VR after det-evidence null | arm |
| V6 | tie | pass | pass | **hold** — matches V0/E4 | arm |
| V7 | −2pp on 16 valid | fail (64%) | fail (16) | **reject** — span-check abstentions | arm |

No full-validation spend recommended from this draw.

## Outcomes

| rung | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| V0 | hold | arm | 52% monthly reproduction control |
| V2 | hold (null) | arm | Det guards alone do not move monthly or labels |
| V3 | reject | arm | 13/25 abstentions from det evidence grounding; inflated monthly on reduced denominator |
| V4 | reject | arm | Second LLM call redundant after V3 abstention filter |
| V5 | reject | arm | LLM VR does not recover valid count vs V3 |
| V6 | hold | arm | Full VR + guards neutral vs adjudicate-only (confirms E4) |
| V7 | reject | arm | Span-check after VR: 9 abstentions, 50% monthly on 16 valid |

## Mechanism review

Not applicable for mechanism closure. Directional read:

- **Deterministic plausibility guards** after adjudicate are **neutral** on this cap-25 slice when no LLM verifier runs (V2 ≡ V0).
- **Deterministic evidence grounding** before guards is **harmful** under strict in-note quote enforcement: half the cap-25 records abstain, failing schema and valid-count gates.
- **LLM verify-repair after adjudicate** is **neutral** when det guards are on and det-evidence is off (V6 ≡ V0 ≡ E4).
- **Evidence span-check after VR** reproduces Lane A-style abstention pressure (9/25) on the g2 skeleton; **reject** for operational use.

## Open cells (explicit)

- V3/V4/V5 monthly lift on 12 valid records — needs error-read before interpreting as true gain.
- Det evidence policy tuned to diagnostic-only vs prediction-affecting abstain.
- Judge escalation (V8) not run.
- Qwen port deferred.

## Phase recommendation

1. Keep **adjudicate-only** or **adjudicate + VR + det guards** (V0/V6) as cap-25 search cells; do not add det-evidence abstention to the default path without a revised policy.
2. Do not spend full validation on V3–V5 or V7.
3. Optional error-read on the 13 records where V3 abstained vs V0 scored — tag `unsupported-quote` vs model quote formatting.
4. Registry rows + matrix refresh when backfill script is next run.

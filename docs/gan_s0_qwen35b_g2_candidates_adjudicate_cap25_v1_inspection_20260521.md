# Gan S0 Qwen35b G2 Candidates-Adjudicate Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | Phase 7 — Qwen port of winning GPT cap-25 cell |
| Comparison group | `gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1` |
| Primary varied factor | `model_track` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| `implementation_variant` | `cand_prose_v1` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: Qwen3.6:35b via Ollama, `gan_2026_fixed_v1:validation` cap-25, scorer `gan_frequency_deterministic_v1`, program `gan_frequency_s0_temporal_candidates_single_pass`, prompt `gan_frequency_s0_temporal_candidates_single_pass_v1_1`, deterministic temporal candidates, no verify-repair.

## Arms

| arm_id | model | run_id | monthly | purist | pragmatic | norm exact | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Q1 | Qwen3.6:35b | `gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_20260521T065534Z` | **40.0%** | 56.0% | 72.0% | 32.0% | 100% | 100% | 25 |

Reference (same cell, GPT):

| Reference | run_id | monthly | schema | evidence |
| --- | --- | ---: | ---: | ---: |
| GPT E1 | `gan_s0_stage_executor_e1_det_candidates_cap25_gpt4_1_mini_20260521T013003Z` | 52.0% | 100% | 100% |

## Runtime caveat

Total prediction time was **1.4s** for 25 records (~0.06s/record), indicating **DSPy disk-cache hits** rather than fresh Ollama inference. Metrics are valid for the compiled program/prompt path but should be treated as a **fast replay**; re-run without cache if a latency or fresh-inference audit is needed.

## Gates (prereg)

| Check | Result | Gate | Outcome |
| --- | --- | --- | --- |
| Valid predictions | 25/25 | pass | pass |
| Schema validity | 100% | ≥ 95% | pass |
| Evidence support | 100% | ≥ 96% | pass |
| Monthly vs GPT E1 | 40.0% vs 52.0% (−12.0pp) | ≥ 47% promote / ≥ 44% hold | **fail reject** |
| Systemic abstention | none observed | — | pass |

**Outcome: reject (arm).** Qwen does not port the GPT E1 winner on this cap-25 slice. Do not promote to full validation or update operational default.

## Error profile (headline)

Dominant failure modes vs GPT E1 on the same records:

- **Unknown overcall:** 6/15 monthly misses predicted `unknown` where gold is quantified infrequent/frequent (`gan_13123`, `gan_14485`, `gan_14881`, `gan_16825`, `gan_4709`).
- **Cluster/per-cluster collapse:** `multiple per cluster` substitutions (`gan_10434`, `gan_3246`).
- **Window arithmetic:** `10 per 3 month` → `8 per 3 month`; `9 per 5 month` → `9 per 3 month`; `8 per 2 month` → `6 per 2 month`.
- **Unknown vs quantified:** gold `unknown` → `1 to 2 per week` (`gan_9566`).

Pattern aligns with residual-slice groups (`unknown_vs_quantified`, `cluster_composition`, `arithmetic_window_precision`) but at higher severity than GPT on this prefix.

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| Q1 | reject | arm | −12pp monthly vs GPT E1; schema/evidence pass; no full-validation spend |

## Mechanism review

Not applicable — arm reject only. Do **not** claim Qwen cannot run det-candidate adjudication globally; this is one model × one prompt × cap-25 portability test.

## Open cells

- Fresh-inference rerun without DSPy cache
- Qwen port of operational `g3_candidates_extract_repair` (different stage graph)
- Qwen with table candidate presentation (not promoted on GPT cap-50)
- Full validation (gated off by reject)

## Phase 7 recommendation

- **Do not** promote Qwen `g2_candidates_adjudicate` to full validation.
- **Proceed** to Phase 7b Gan canonical-format port on **GPT** (prereg ready) — exact-label surface discipline is the higher-value next test for the residual error profile.
- Keep Qwen operational default on temporal-candidates + verify-repair until a Qwen cell clears a preregistered port gate.

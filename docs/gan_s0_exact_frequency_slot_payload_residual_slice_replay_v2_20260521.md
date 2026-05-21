# Gan S0 Exact-Frequency Slot Payload — Residual Slice Replay v2

Date: 2026-05-21  
Parent: `docs/gan_s0_exact_frequency_slot_payload_gpt_cap25_v1_inspection_20260521.md`  
Builder expansion: `docs/gan_s0_residual_candidate_builder_expansion_20260521.md`  
Comparison group: `gan_s0_exact_frequency_slot_payload_residual_slice_gpt_v1` (same configs; code change only)

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema | S0 seizure frequency |
| Research axis | 3 — implementation variant + expanded deterministic builders |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed: GPT 4.1-mini, 30-record residual queue, `g2_candidates_adjudicate`, scorer `gan_frequency_deterministic_v1`, no verify-repair.

Varied: `implementation_variant` — S0 `cand_prose_v1` vs S1 `slot_payload_v1`, with **expanded** `temporal_candidates.py` builders (post-2026-05-21).

## Runs

| arm | implementation_variant | run_id | monthly | norm exact | schema | evidence |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| S0 | `cand_prose_v1` | `gan_s0_slot_s0_residual_slice_gpt4_1_mini_20260521T071756Z` | **63.3%** (19/30) | 60.0% | 100% | 100% |
| S1 | `slot_payload_v1` | `gan_s0_slot_s1_residual_slice_gpt4_1_mini_20260521T071836Z` | 60.0% (18/30) | 56.7% | 100% | 100% |

Replay artifact: `artifacts/gan_slot_payload_residual_replay_v2_20260521/summary.json`

## v1 vs v2 (builder expansion effect)

| Replay | S0 monthly | S1 monthly | S1 − S0 | Headline |
| --- | ---: | ---: | ---: | --- |
| v1 (sparse builders) | 13.3% (4/30) | 13.3% (4/30) | 0 | null — 1 recovery, 1 regression |
| **v2 (expanded builders)** | **63.3%** (19/30) | **60.0%** (18/30) | **−3.3pp** | builders dominate; S1 does not beat S0 on hard queue |

Builder expansion alone moved the residual queue from **4/30 → 19/30** monthly-correct for S0 (+50pp on this slice). Slot-payload formatting does **not** add lift on the hard queue once builders are rich; S1 is slightly worse overall.

## Per-group monthly correct (v2)

| Residual group | records | S0 monthly | S1 monthly | v1 S0/S1 (ref) |
| --- | ---: | ---: | ---: | ---: |
| `arithmetic_window_precision` | 10 | **5/10** | **5/10** | 0/10 |
| `unknown_vs_quantified` | 8 | **6/8** | **6/8** | ~4/8 (v1 had mixed) |
| `cluster_composition` | 8 | **5/8** | 4/8 | 1/8 |
| `infrequent_long_denominator_or_boundary` | 4 | **3/4** | **3/4** | 1/4 |

Arithmetic/window and infrequent strata show the largest builder-driven gains. Unknown strata mostly recover when gold is plain `unknown` and candidates emit `unknown`; `gan_14081` / `gan_14092` still invent denominators on both arms.

## S1 vs S0 paired deltas (v2)

| Metric | Value |
| --- | ---: |
| Monthly recovery (S1 vs S0) | 1 (`gan_10434`: `multiple cluster per week, 2 to 3 per cluster`) |
| Monthly regression (S1 vs S0) | 2 (`gan_10031`, `gan_10673`: S0 correct cluster → S1 `unknown`) |
| Normalized exact recovery | 1 |
| Normalized exact regression | 2 |
| Pragmatic overcall (S1 vs S0) | 2 |

S1 helps one cluster-composition record where prose under-specified `multiple cluster`; S1 hurts two records where slot table/json may over-emphasize `unknown_policy_cue` and the model abstains despite prose candidates carrying the gold cluster label.

## Gates (preregistered residual)

| Check | Outcome |
| --- | --- |
| Concentrated recovery in arithmetic + unknown target groups | **partial pass** — arithmetic 5/10 monthly (was 0/10 in v1); unknown 6/8 monthly |
| S1 beats S0 on residual monthly | **fail** — S0 63.3% vs S1 60.0% |
| Net null S1 vs S0 (v1 criterion) | **fail** — 1 recovery, 2 regressions monthly |
| Promote slot_payload to cap-50 / full | **no** — hard-queue lift is builder-driven; presentation arm loses on residual |

## Outcomes

| arm | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| S0 | hold | arm | Prose + expanded builders: 63.3% monthly on hard queue |
| S1 | reject (arm) vs S0 on residual | arm | 60.0% monthly; regresses cluster records vs prose with same builders |

Cap-25 S1 hold (+8pp vs 52% Lane-A) **unchanged in interpretation** — Lane-A and hard-queue criteria diverge once builders cover gold labels. Next Axis-3 work should default to **prose or table** presentation with expanded builders, not slot-payload v1 on this queue.

## Open cells

- Seizure-type selection failures (`gan_12562`–`gan_12679`, `gan_16947`/`gan_16964`) — builders do not address concurrent-type priority
- Long-window `multiple cluster per N month` (`gan_15240`, `gan_15255`)
- `gan_13290` gold `4 per 6 month` vs candidate `2 per 6 month`
- Cap-50 confirm deferred; no full-validation promotion from residual v2

## Mechanism review

Not applicable for mechanism closure. Directional evidence: **deterministic candidate coverage** is the dominant lever on the residual queue; slot-payload presentation is not uniformly helpful and can increase cluster abstention.

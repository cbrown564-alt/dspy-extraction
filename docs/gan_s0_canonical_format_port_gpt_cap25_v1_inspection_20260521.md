# Gan S0 Canonical-Format Port GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/gan_s0_canonical_format_port_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_canonical_format_port_gpt_cap25_v1`

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
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` cap-25, scorer `gan_frequency_deterministic_v1`, program `gan_frequency_s0_temporal_candidates_single_pass`, deterministic temporal candidates, prose presentation, no verify-repair.

## Arms

| arm_id | implementation_variant | run_id | monthly | purist | pragmatic | norm exact | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | `canonical_format_control_v1_1` | `gan_s0_canonical_c0_control_cap25_gpt4_1_mini_20260521T065641Z` | 52.0% | 60.0% | 76.0% | 40.0% | 100% | 100% | 25 |
| C1 | `canonical_format_v3_examples_v1` | `gan_s0_canonical_c1_v3_examples_cap25_gpt4_1_mini_20260521T065651Z` | **56.0%** | 64.0% | 72.0% | **44.0%** | 100% | 100% | 25 |

Delta C1 − C0: **+4.0pp monthly**, **+4.0pp normalized exact**, +4.0pp Purist, **−4.0pp Pragmatic**.

C0 reproduces E1/I0 at 52% monthly on the same 25 records.

## Prediction overlap

Identical normalized labels: **17/25**.

Notable C1 fixes vs C0:

- `gan_14881`: `unknown` → `1 per month` (infrequent quantified rate recovered)
- `gan_1794`: `2 per month` → `2 per 2 month` (window arithmetic)
- `gan_16772`: `7 per month` → `9 per 5 month` (denominator correction)

Notable C1 regressions vs C0:

- `gan_4113`: `1 per 1 to 2 day` → `unknown`
- Pragmatic category −4pp (7/25 mismatches vs prior control)

## Gates (prereg)

| Check | C1 vs C0 | Gate | Outcome |
| --- | --- | --- | --- |
| Normalized exact | +4.0pp (44% vs 40%) | ≥ +3.0pp | **pass** |
| Monthly | +4.0pp (56% vs 52%) | no regression > 2pp | **pass** (improved) |
| Pragmatic | −4.0pp | not preregistered hard gate | **caveat** |
| Schema | 100% | ≥ 95% | pass |
| Evidence | 100% | ≥ 96% | pass |

**Outcome: hold (arm) on cap-25 only.** C1 clears the preregistered normalized-exact promotion threshold on cap-25 and improves monthly frequency. Pragmatic regression and cap-25 size warranted residual-slice replay.

**Residual replay (2026-05-21):** `docs/gan_s0_canonical_format_residual_slice_replay_20260521.md` — on the fixed 30-record VR monthly-miss queue, C0/C1 tie at 10% normalized exact; 1 recovery vs 1 regression; **no cap-50 or full-validation promotion** from residual evidence.

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| C0 | hold | arm | Reproduces E1/I0 control |
| C1 | hold | arm | +4pp normalized exact and monthly; pragmatic −4pp; 17/25 label overlap |

## Mechanism review

Not applicable — single addendum variant; mechanism class stays **open**.

## Open cells

- ~~Residual-slice replay~~ Done — null on 30-record queue; see `docs/gan_s0_canonical_format_residual_slice_replay_20260521.md`
- VR skeleton confirmation (`g3_candidates_extract_repair`)
- Cap-50 / full validation deferred (residual gate not met)
- Qwen port deferred

## Recommendation

- Treat cap-25 hold as **search evidence only**; do not operationalize C1 without a new confirmatory prereg.
- Do **not** mechanism-close “canonical format examples” from cap-25 + residual replay.
- Prefer next work on residual mechanisms (seizure-type selection, calendar aggregation) over cap-50 prompt-example confirm.

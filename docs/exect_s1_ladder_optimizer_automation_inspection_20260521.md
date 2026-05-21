# ExECT S1 Ladder Optimizer Automation — Inspection

Date: 2026-05-21  
Thesis: `docs/exect_s1_ladder_optimizer_automation_thesis_20260521.md`  
Comparison group: `exect_s1_ladder_optimizer_automation_v1`  
Ladder context: `docs/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S1 field-family |
| Research axis | 3 — implementation (DSPy compile on stripped L0/L1) |
| Comparison group | `exect_s1_ladder_optimizer_automation_v1` |
| Primary varied factor | `ladder_rung` (optimizer base prompt + method) |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `exectv2_fixed_v1:validation` cap-25 eval, train compile on first 40 `exectv2_fixed_v1:train`, scorer `exect_field_family_deterministic_v1`, `repair_policy=raw_no_benchmark_bridges` (no v4_10 policy or inline bridges in prediction path).

## Arms

| Rung | Config | Run ID | Micro F1 | Diagnosis | Seizure | Medication | Evidence support |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 4a | L0 + LabeledFewShot | `exect_s1_full_ladder_l0_labeled_cap25_gpt4_1_mini_20260521T020735Z` | **65.3%** | 52.6% | 60.3% | 80.6% | 80.7% |
| 4b | L0 + BootstrapFewShot | `exect_s1_full_ladder_l0_bootstrap_cap25_gpt4_1_mini_20260521T020742Z` | **60.0%** | 41.4% | 59.5% | 74.4% | 84.6% |
| 4c | L1 + LabeledFewShot | `exect_s1_full_ladder_l1_labeled_cap25_gpt4_1_mini_20260521T020751Z` | **71.7%** | 57.7% | 63.9% | 93.3% | 82.1% |

Reference anchors (not re-run):

| Anchor | Micro F1 | Notes |
| --- | ---: | --- |
| L0 zero-shot | 60.0% | `exect_s1_full_ladder_l0_cap25_20260521T003707Z` |
| L1 zero-shot | 67.7% | `exect_s1_full_ladder_l1_cap25_20260521T003924Z` |
| Hand-crafted v4_10 + bridges | 95.8% | `exect_s1_optimizer_baseline_cap25_20260521T000602Z` |
| v4_10 + bootstrap (prior pilot) | 90.7% | Reject — stacked on hand craft |

## Gates (thesis prereg)

| Outcome rule | Result |
| --- | --- |
| Thesis supported (≥ 93.0% micro, families within 3 pp of policy ref) | **Fail** — best arm 71.7% |
| Partial automation (≥ L1 + 10 pp but < 93%) | **Borderline** — 4c +4.0 pp vs L1 zero-shot (67.7%), below +10 pp bar |
| Thesis rejected (≤ 75% plateau) | **Fail for 4a/4b** — 4c exceeds 75% |
| Schema / evidence regression vs paired baseline | **Pass** — all arms Pydantic-valid on 25/25; evidence support ≥ 80% |

## Outcomes

| Rung | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| 4a | hold (partial) | arm | +5.3 pp vs L0 zero-shot; still below L1 zero-shot (67.7%) |
| 4b | reject | arm | 60.0% micro — ties L0 zero-shot; bootstrap traces do not lift extraction |
| 4c | hold (partial) | arm | Best optimizer arm; +4.0 pp vs L1 zero-shot; medication strong (93.3%) but diagnosis/seizure << policy ref |

**Group conclusion (arm scope):** DSPy compile on stripped L0/L1 **does not substitute** for hand-authored v4_10 policy + bridges on cap-25. Demos help modestly (especially L1+labeled); bootstrap on L0 with raw compile metric adds no lift over zero-shot.

## Mechanism review

Not applicable for mechanism closure. Directional read:

- **LabeledFewShot > BootstrapFewShot** on L0 (+5.3 pp) — consistent with Gan ladder pattern.
- **Schema descriptions + demos (4c)** beat **minimal prompt + demos (4a)** by +6.4 pp — schema helps compile ceiling but remains ~24 pp below hand-crafted cap-25.
- **Medication** is the easiest family for demo-only automation (93.3% on 4c); **diagnosis** remains the bottleneck (57.7% best).

## Open cells

- BootstrapRS / GEPA rungs 6–7 (deferred).
- Full validation or test holdout for any arm (none cleared promotion gate).
- Compile with benchmark-normalized train demos (known asymmetry in thesis).
- Optimizer on winning Gan `g2_candidates_adjudicate` skeleton (Phase 6 Gan attachment).

## Operational implications

- Keep **v4_10 + inline bridges** as ExECT S1 operational default; do not replace with L0/L1+compile from this draw.
- Next optimizer work, if any: fix train-demo surface alignment, then re-run **one** labeled arm before expanding rungs 6–7.

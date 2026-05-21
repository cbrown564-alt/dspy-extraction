# ExECT S4 Medication Precision Guard GPT Full Validation v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_full_validation_v1_preregistration_20260521.md`  
Cap-25 inspection: `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_cap25_v1_inspection_20260521.md`  
Design: `docs/experiments/exect/exect_s4_medication_precision_guard_design_20260521.md`  
Comparison group: `exect_s4_medication_precision_guard_gpt_full_validation_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s4_field_family` |
| Research axis | 3 |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

## Arms

| arm_id | implementation_variant | run_id | MT precision | MT F1 | MT recall | Micro F1 |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| L1 | `mt_guard_l1_control` | `exect_s4_mt_guard_l1_baseline_full_gpt4_1_mini_20260521T074448Z` | **46.4%** | 62.5% | 95.7% | 66.2% |
| G0 | `mt_guard_non_asm_only_v1` | `exect_s4_mt_guard_g0_non_asm_full_gpt4_1_mini_20260521T074459Z` | **57.7%** | **72.0%** | 95.7% | 67.9% |

**Delta (G0 − L1):** MT precision **+11.3pp**; MT F1 **+9.5pp**; micro F1 **+1.7pp**; MT recall unchanged.

L1 reproduces the frozen S4 v1.2 full anchor (`runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`) on all headline metrics.

## Confirmation gates (full validation)

| Gate | Rule | Result |
| --- | --- | --- |
| Precision | G0 ≥ L1 + 3pp | **Pass** (+11.3pp) |
| F1 guard | G0 F1 not below L1 by ≥2pp | **Pass** (+9.5pp) |
| Regression guard | Frozen S3/S4 families | **Pass** — diagnosis, seizure_type, annotated_medication, investigation, seizure_frequency F1 identical |

## Frozen-family check

| Family | L1 F1 | G0 F1 |
| --- | ---: | ---: |
| diagnosis | 91.1% | 91.1% |
| seizure_type | 84.0% | 84.0% |
| annotated_medication | 71.3% | 71.3% |
| investigation | 96.7% | 96.7% |
| seizure_frequency | 50.6% | 50.6% |

Evidence support: L1 87.6% → G0 87.5% (negligible).

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (reference) | arm | Matches S4 v1.2 full anchor |
| G0 | **hold (operational candidate)** | arm | Full-validation confirm; wire G0 into S4 default only after Kanban/registry update |

## Mechanism review

Not applicable for mechanism closure.

Directional read:

- Non-ASM post-guard gain **generalizes** from cap-25 (+11.2pp precision) to full validation (+11.3pp) with **no recall loss** (unlike H1 post-classifier full reject).
- Remaining MT burden is predominantly **planned/previous ASM over-tag** and brand/surface mismatches — G0 does not address ~54% of full-val FP bucket per residual analysis.
- Mechanism class **medication temporality precision guard** stays **open** until G1/G2 or second implementation tier confirms.

## Operational recommendation

- **Promote (arm):** use `exect_s4_field_family_mt_guard_non_asm_single_pass` as the GPT S4 operational default for medication-temporality scoring runs, replacing bare `exect_s4_field_family_single_pass` for new ExECT S4 GPT configs.
- **Do not** mechanism-close precision-guard class from G0 alone.
- **Next:** G0+G2 dose-current fallback cap-25, then G1 planned/previous evidence gate if G0+G2 passes F1 guard.
- **Do not** rerun H1 post-classifier.

## Open cells

- G0+G2 dose-current fallback
- G1 planned/previous evidence gate
- G3 brand alias map
- Annotated-medication coupled guard
- Qwen port of G0 skeleton

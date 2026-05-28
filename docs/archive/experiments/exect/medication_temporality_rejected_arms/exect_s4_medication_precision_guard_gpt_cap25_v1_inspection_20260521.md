# ExECT S4 Medication Precision Guard GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_cap25_v1_preregistration_20260521.md`  
Design: `docs/experiments/exect/exect_s4_medication_precision_guard_design_20260521.md`  
Comparison group: `exect_s4_medication_precision_guard_gpt_cap25_v1`

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
| L1 | `mt_guard_l1_control` | `exect_s4_mt_guard_l1_baseline_cap25_gpt4_1_mini_20260521T073717Z` | **46.8%** | 63.7% | 100.0% | 69.5% |
| G0 | `mt_guard_non_asm_only_v1` | `exect_s4_mt_guard_g0_non_asm_cap25_gpt4_1_mini_20260521T073727Z` | **58.0%** | **73.4%** | 100.0% | 71.4% |

**Delta (G0 − L1):** MT precision **+11.2pp**; MT F1 **+9.7pp**; micro F1 **+1.9pp**; MT recall unchanged (100%).

## Promotion gates (cap-25)

| Gate | Rule | Result |
| --- | --- | --- |
| Precision | G0 ≥ L1 + 3pp | **Pass** (+11.2pp) |
| F1 guard | G0 F1 not below L1 by ≥2pp | **Pass** (+9.7pp) |
| Regression guard | Frozen S3/S4 families | **Pass** — diagnosis, seizure_type, annotated_medication, investigation, seizure_frequency F1 identical |

## Frozen-family check

| Family | L1 F1 | G0 F1 |
| --- | ---: | ---: |
| diagnosis | 95.2% | 95.2% |
| seizure_type | 90.9% | 90.9% |
| annotated_medication | 69.0% | 69.0% |
| investigation | 93.8% | 93.8% |
| seizure_frequency | 51.0% | 51.0% |

Evidence support: L1 87.9% → G0 87.2% (negligible).

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| L1 | hold (reference) | arm | Matches prior temporality L1 cap-25 band (~46.8% MT precision) |
| G0 | **hold (cap-25 proceed)** | arm | Beats prereg precision gate without recall loss; eligible for full-validation pair |

## Mechanism review

Not applicable for mechanism closure.

Directional read:

- Non-ASM-only post-guard removes precision FPs **and** improves F1 on cap-25 because recall stays at 100% (unlike H1 unknown-abstention).
- Single implementation tier; mechanism class **medication temporality precision guard** stays **open** until G0+G2 or full-validation confirms.
- Does **not** address planned/previous ASM over-tagging (54% of full-val FP bucket) — G1/G2 still queued.

## Operational recommendation

- **Do not** wire G0 into production S4 default without full-validation (40 records).
- **Next:** ~~full-validation L1/G0 pair~~ **Done** — `docs/experiments/exect/exect_s4_medication_precision_guard_gpt_full_validation_v1_inspection_20260521.md` (G0 hold operational candidate).
- **Do not** rerun H1 post-classifier.

## Open cells

- Full validation (40)
- G0+G2 dose-current fallback
- G1 planned/previous evidence gate
- Brand alias G3
- Annotated-medication coupled guard

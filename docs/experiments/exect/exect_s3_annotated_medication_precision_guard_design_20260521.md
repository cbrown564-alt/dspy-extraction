# ExECT S3 Annotated Medication Precision Guard — Design

Date: 2026-05-21  
Status: Design ready for preregistration (coupled read with S4 MT track)  
Parent: `exect_s1_s3_residual_targeted_actions_20260521.md` (P1)  
S4 sibling: `exect_s4_medication_precision_guard_design_20260521.md`  
Anchor: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` (annotated_medication **81.4%** F1, 20 FP / 1 FN)

## Question

Can shared **non-ASM and brand-surface guards** reduce S3 annotated-medication false positives introduced by the nine-family pass without reopening S1 medication pre-vocabulary (rejected: 98.3% → 95.1% on Rx slice)?

## No-model FP taxonomy (GPT full validation)

| Bucket | Count | Tag | Examples |
| --- | ---: | --- | --- |
| Non-ASM / comorbidity-drug leakage | ~12 | over-extraction | aspirin, omeprazole, insulin, ramipril, simvastatin, thyroxine |
| Duplicate ASM extras | ~6 | over-extraction | carbamazepine, lamotrigine, levetiracetam (overlap with S4 MT planned/previous) |
| Brand / spelling | ~2 | scorer-surface | `eplim` vs `epilim chrono` (EA0136) |
| Recall | 1 FN | scorer-surface | isolated miss |

**Primary problem is precision (20 FP, 1 FN),** same shape as S4 annotated_medication coupling in MT design doc.

## Design constraint

- S1 medication pre-vocab: **reject (arm)** — do not port H2.
- S4 MT H1 broad post-classifier: **reject (arm)** — unknown abstention recall collapse.
- Guards must be **tiered** and **family-scoped** unless preregistered cross-family coupling.

## Proposed tiers (shared primitive logic, S3-scoped variant IDs)

| Tier | ID | Action | Source |
| --- | --- | --- | --- |
| **M0** | `am_guard_non_asm_only_v1` | Drop labels where canonical ∉ ASM allowlist (reuse S4 G0 logic) | `exect_s4_medication_precision_guard_design` G0 |
| **M1** | `am_guard_brand_alias_v1` | Map `eplim` → `epilim chrono`, `lamictal` surface repair | S4 G3 + `_BRAND_SURFACES` in primitives |
| **M2** | `am_guard_duplicate_asm_v1` | Dedupe identical ASM within pass when no distinct evidence | Optional; only if M0 insufficient |

**Do not** apply MT planned/previous rules to `annotated_medication` — temporality is out of scope for S3 medication family.

## Cap-25 prereg gates

| Metric | Gate |
| --- | --- |
| Primary | `annotated_medication` precision vs S3 v1.2 cap-25 baseline |
| F1 guard | Family F1 no regression ≥2pp vs L1 |
| Regression | investigation ≥93%, seizure_type ≥78%, comorbidity no ≥3pp drop |
| Cross-track | If S4 MT G0 promotes, run S3 M0 in same inspection batch for coupled read |

Comparison group: `exect_s3_annotated_medication_guard_gpt_cap25_v1`

## Fixture documents

| Doc | Tests |
| --- | --- |
| EA0136 | M1 brand repair; M0 does not drop affirmed ASM |
| EA0143 | M0 drops extra lamotrigine only if non-gold scope |
| EA0016 | M0 drops aspirin/omeprazole class FPs |

Exclude EA0078 (`missing_gold`) from guard evaluation.

## Open cells

- Whether M0 uses same `_NON_ASM_MEDICATIONS` set as S4 G0 (recommended: single source in `exect/primitives.py`)
- Coupled inspection with S4 MT G0 full-validation
- S2 annotated medication (90% F1) — optional S2 cap-25 regression check when promoting S3 M0

## Next steps

1. Extract shared `drop_non_asm_medication_labels()` for S3/S4 programs.
2. Implement M0 + tests on S3 artifact path.
3. Prereg + cap-25 vs `…235439Z` prefix.
4. Full validation only if cap-25 passes F1 guard.

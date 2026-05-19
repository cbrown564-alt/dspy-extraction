# ExECT S0/S1 Full Validation Inspection (v4.1)

Date: 2026-05-19

Run artifact:

- `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T201721Z`

Config:

- `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`
- `prompt_version`: `exect_s0_s1_field_family_v4_1_label_policy`
- `scorer`: `exect_field_family_deterministic_v1`

Comparison anchors:

| Run | Prompt | Micro F1 | Diagnosis F1 | Seizure F1 | Med F1 | Evidence |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Full v3 | `…_v3_seizure_evidence_policy` | 67.8% | 50.6% | 61.4% | 87.4% | 87.6% |
| Cap-25 v4.1 | `…_v4_1_label_policy` | 81.4% | 84.2% | 72.0% | 90.6% | 89.4% |
| **Full v4.1** | `…_v4_1_label_policy` | **75.3%** | **74.3%** | 68.6% | 82.7% | 84.7% |

Prior docs: `docs/exect_s0_s1_validation_full_inspection.md` (v3), `docs/exect_s0_label_policy_regression_slice_comparison_20260519.md`

## Scope

Full fixed ExECTv2 validation split (`exectv2_fixed_v1:validation`, 40 records). Not published ExECTv2 benchmark reproduction.

Runtime: ~84s, 40 model calls (~2.1s/record).

## Interpretation

- **+7.5pp micro F1** vs v3 full validation (67.8% → 75.3%). Label-policy v4.1 is a material improvement on the full split.
- **Diagnosis F1 +23.7pp** (50.6% → 74.3%) — unsupported-diagnosis rejection, uncertainty stripping, and symptomatic structural focal restoration dominate the gain.
- **Cap-25 was optimistic** for the full split: cap-25 micro F1 was 81.4% vs full 75.3% (−6.1pp), same pattern as v3 (73.7% cap vs 67.8% full).
- **Seizure-type F1** improved vs v3 (+7.2pp) but trails cap-25 (68.6% vs 72.0%) on the harder tail records.
- **Medication F1 regressed** vs v3 full (87.4% → 82.7%) and cap-25 (90.6%); common FPs: `lamotrigine`, `carbamazepine`, `sodium valproate` on gold-limited or historical mentions.
- **Evidence support** 84.7% (vs 87.6% v3); still secondary to label F1 gaps.

## Error read (40 records)

31 documents with at least one field-family mismatch (vs 35 on v3 full).

Dominant remaining failure modes:

1. **Granular seizure descriptors** — `myoclonic jerks`, `absences`, `jerks` as false positives where gold uses coarser surfaces (`generalized seizures`, etc.).
2. **Seizure-type recall** — missing labels on tail records; precision 62.1% vs diagnosis 92.9%.
3. **Medication scope** — extra ASM on `missing_gold` or historical rows (EA0078 pattern persists).
4. **Diagnosis recall** — 62.0% recall despite high precision; missed co-listed lobe/syndrome diagnoses on tail records.

## Recommended next pull

1. Treat **v4.1 full validation as the new monolithic anchor** for ExECT S0/S1 (replace v3 headline in Kanban).
2. Do **not** reopen section-aware architecture without a new hypothesis.
3. Next improvement lever: **seizure-type coarse-surface policy** and **medication false-positive guardrails** (prompt or narrow bridge), not scorer changes.
4. Defer verify-repair until label F1 plateaus; evidence at 84.7% remains secondary.

## Audit guidance

Grounded in `docs/exect_gold_label_audit.md`: benchmark-facing fields only; deterministic bridges tagged in prediction `quality_flags`; v3 full run retained as historical comparison anchor.

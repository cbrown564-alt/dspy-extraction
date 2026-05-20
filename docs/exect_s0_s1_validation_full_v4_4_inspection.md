# ExECT S0/S1 Full Validation — v4.4 Post-Anchor Read

Date: 2026-05-19

Run artifact:

- `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T210602Z`

Config:

- `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`
- `prompt_version`: `exect_s0_s1_field_family_v4_4_label_policy`
- `scorer`: `exect_field_family_deterministic_v1` (unchanged)

Comparison anchors:

| Run | Micro F1 | Diagnosis F1 | Seizure F1 | Med F1 | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| **v4.4 full (this run)** | **82.0%** | **79.5%** | **76.8%** | 89.4% | 94.1% |
| v4.3 full | 79.8% | 74.3% | 74.7% | 89.4% | 94.1% |
| v4.2 full | 78.5% | 74.3% | 74.7% | 85.1% | 84.0% |

Prior reads: `docs/exect_s0_label_policy_v4_4_implementation.md`, `docs/exect_s0_s1_validation_full_v4_2_medication_evidence_inspection.md`

## Headline

v4.4 co-list bridges lifted diagnosis F1 (+5.2pp vs v4.3) and seizure F1 (+2.1pp) without medication or evidence regression. **26 of 40** validation records still have at least one field-family mismatch (down from 27 on v4.3). **EA0045** (planned lamotrigine FP) cleared on full validation.

Remaining pain clusters: **JME / myoclonic seizure surfaces**, **generic `epilepsy` diagnosis recall** despite co-list policy, **dissociative vs epileptic seizure routing**, and **medication/evidence** on a smaller tail.

## What improved vs v4.3 (full validation)

| Record | v4.3 issue | v4.4 status |
| --- | --- | --- |
| EA0045 | Medication FP (planned lamotrigine) | **Cleared** |
| Multiple diagnosis co-list targets | Missing `epilepsy` / focal pairs | Partially fixed cluster-wide (+5.2pp diagnosis F1) |

## Residual errors not in the 23-record slice (pre-expansion)

These records failed on v4.4 full validation but were outside `exect_s0_label_policy_error_regression_slice.json` before this read:

| Record | Family | Pattern | v4.5 hypothesis |
| --- | --- | --- | --- |
| EA0048 | seizure | FN `tonic clonic seizures`; FP `myoclonic seizures`, `generalized tonic clonic seizures` | JME coarse surface: prefer GTCS label over myoclonic jerks when both in note |
| EA0069 | seizure | FN `generalized tonic clonic seizure`; FP `myoclonic seizures` | Same JME cluster; evidence header quote drift |
| EA0050 | seizure | FP `myoclonic seizures` (`specificity_collapsed`) | Do not emit myoclonic when gold collapses to jerks-only surface |
| EA0125 | diagnosis + seizure | FN `jme`; FP `myoclonic seizures` | Abbreviation + JME seizure coarsening |
| EA0026, EA0029 | seizure | FP `myoclonic seizures` / extra JME diagnosis | Already on slice; still failing |
| EA0131, EA0148, EA0170, EA0173 | diagnosis | FN `epilepsy` only | Tighten note-gated generic epilepsy co-list (avoid recall-probe overreach) |
| EA0116 | diagnosis | FN `epilepsy with generalized tonic clonic seizures on awakening` | On slice; still failing — awakening syndrome phrasing |
| EA0135 | seizure | FN `epileptic seizures`; FP `focal seizures` | Dissociative vs focal routing in seizure slot |
| EA0174 | seizure | FN `epileptic seizures`; FP descriptive bilateral shaking phrase | Do not promote narrative descriptors to benchmark seizure types |
| EA0179 | seizure | FP `complex partial seizures` from `?complex partial` differential | Question-mark / differential guard |
| EA0072 | seizure | FN `focal motor seizure` | Independent focal-motor surface |
| EA0008 | medication | FN `lamotrigine` | Prescription “to reduce” vs planned-medication exclusion |
| EA0188 | diagnosis + seizure | FN collapsed tokens `focal`, `drug`, `occipital`; FP granular focal labels | Specificity-collapse co-list (diagnosis), not ILAE remapping |

## Slice records now green on v4.4 (retained as anchors)

Keep in fixture for regression governance even when temporarily passing:

EA0018, EA0045, EA0047, EA0053, EA0059, EA0068, EA0090, EA0124, EA0142, EA0153

See `docs/exect_label_policy_prior_error_analysis_traceability_20260519.md` for canonical-case rationale (e.g. EA0016 single-event null diagnosis).

## Evidence errors (diagnostic)

17 evidence support failures on 40 records — unchanged rate vs v4.3 (94.1%). Mix:

| Reason | Representative records |
| --- | --- |
| Missing evidence spans | EA0026, EA0072, EA0150, EA0125 |
| Header / formatting quote mismatch | EA0069, EA0098, EA0135, EA0142, EA0143, EA0179 |

Evidence is not the primary blocker for the next label-policy iteration; medication temporality and quote repair were addressed in v4.3 without F1 gain on full validation.

## Tagged clusters for v4.5 (bounded)

1. **JME / myoclonic coarse surface** — EA0048, EA0069, EA0050, EA0125 (+ slice EA0026, EA0029, EA0053).
2. **Generic epilepsy co-list recall** — EA0131, EA0148, EA0170, EA0173 (note-gated; do not repeat add-only recall probe).
3. **Dissociative vs epileptic seizure slot** — EA0135.
4. **Differential / descriptive seizure guards** — EA0179, EA0174.
5. **EA0008 medication** — reconcile prescription markup with planned-medication policy.
6. **EA0188 specificity collapse** — diagnosis token co-list, not seizure remapping.

**Closed paths (unchanged):** verify-repair promotion; add-only diagnosis-recall v1; section-aware architecture.

## Slice expansion

Added **14 records** (+ canonical EA0016) from this read to `data/fixtures/exect_s0_label_policy_error_regression_slice.json` (**23 → 37 records**, fixture name `exect_s0_label_policy_regression_v3`).

Re-run `configs/experiments/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini.json` before v4.5 prompt/bridge work. Do not compare 23-record slice metrics directly to the expanded 37-record gate.

## Expanded slice gate (37 records, v4.4 anchor)

Run: `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T211558Z`

| Metric | 37-record (v4.4) | 23-record (v4.4, prior) |
| --- | ---: | ---: |
| Micro F1 | **81.4%** | 83.3% |
| Diagnosis F1 | 78.9% | 80.9% |
| Seizure F1 | 76.3% | 84.8% |
| Medication F1 | 88.9% | 83.6% |
| Evidence support | 93.9% | 95.9% |

The lower headline micro F1 is expected: the fixture now includes residual full-validation failures and canonical anchors, not only the pre-v4.4 error cluster. Use this run as the **v4.5 baseline gate**, not as a regression vs the 23-record number.

## Audit guidance

Grounded in `docs/exect_gold_label_audit.md` and `exect-label-policy-alignment`: benchmark-facing field families only; `specificity_collapsed` and `missing_gold` flags preserved in reports; scorer unchanged.

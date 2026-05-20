# ExECT S2 Full Validation (40) — Family Breakdown

Date: 2026-05-20

Run artifact:

- `runs/exect_s2_validation_full_gpt4_1_mini_20260519T230407Z`

Config:

- `configs/experiments/exect_s2_validation_full_gpt4_1_mini.json`
- `prompt_version`: `exect_s2_field_family_v1_2_label_policy`
- `scorer`: `exect_s2_field_family_deterministic_v1`
- S1 bridges: frozen v4.10 (unchanged in `exect_s0_s1.py`)

Comparison anchors:

| Run | Records | Scope |
| --- | ---: | --- |
| S2 cap-25 v1.2 | 25 | `…225836Z` |
| S2 cap-25 v1.1 | 25 | `…225159Z` |
| S1 v4.10 full (frozen) | 40 | `…221944Z` — 92.3% micro F1 (3 fam) |

Design context: `docs/exect_s2_field_expansion_design.md`, `docs/exect_s2_label_policy_v1_2_implementation.md`

## Headline metrics

| Metric | Full v1.2 (40) | Cap-25 v1.2 (25) | Δ (full − cap) | S1 v4.10 full (40, 3 fam) |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 (5 fam) | **80.6%** | 84.1% | −3.5pp | 92.3% (not comparable scope) |
| Diagnosis F1 | **86.4%** | 83.7% | +2.7pp | 93.8% |
| Seizure F1 | **76.6%** | 83.1% | −6.5pp | 90.5% |
| Medication F1 | **91.8%** | 93.3% | −1.5pp | 92.8% |
| Investigation F1 | **91.5%** | 90.9% | +0.6pp | n/a |
| Comorbidity F1 | **63.6%** | 74.3% | **−10.7pp** | n/a |
| Micro recall | 82.7% | 89.8% | −7.1pp | 92.6% |
| Evidence support | 89.3% | 89.3% | 0 | — |

**Records with any field-family mismatch:** 31 / 40.

Cap-25 optimism shows up mainly on **comorbidity** and **seizure** when scaling to the full split; diagnosis and investigation held or improved. This matches the S1 precedent (~7–9pp cap vs full on micro) but the family-level gap is not uniform.

## Mismatch mix (51 family-level mismatch entries)

| Family | Mismatch entries |
| --- | ---: |
| Comorbidity | 20 |
| Seizure type | 13 |
| Diagnosis | 8 |
| Annotated medication | 6 |
| Investigation | 4 |

## Comorbidity — still the main gap

Recall 70.8% vs 92.9% on cap-25; precision 57.6% vs 61.9%. The v1.2 bridges lifted cap-25 comorbidity but **full-split recall did not hold**.

Top false-positive labels (comorbidity):

| Label | Count |
| --- | ---: |
| jerk | 7 |
| meningioma resection | 1 |
| hysterectomy | 1 |
| depression / agitation | 2 |
| headaches / hypertension / meningitis | 3 |
| migraine, family history of epilepsy, GERD, smoking | 1 each |

**jerk** remains the dominant FP cluster (myoclonic jerk surface → comorbidity label). Several cap-25-only fixes (affirmed history recall) do not generalize to the 15 additional validation records.

## Seizure — cap optimism + persistent multi-family drift

Seizure F1 dropped 6.5pp full vs cap-25 while still above the v1 cap-25 disaster (40.0% at v1). Full validation adds records where ILAE modernization, plural loss, and absence FP patterns seen in the v1 inspection still appear on a subset of the **non-overlapping** 15 records.

Do **not** compare 76.6% seizure F1 to S1 full 90.5% as a bridge regression signal without record-level replay; root cause remains model output drift in the 5-family pass (documented for cap-25).

## Investigation and medication

Investigation stable (~91% F1). Medication aligned with S1 full (~92%). No gate blocker for S2 breadth on these families.

## Evidence

Evidence quote support **89.3%** on full — same as cap-25 v1.2. Evidence is not the binding constraint for promotion.

## Decision read

| Gate | Result |
| --- | --- |
| Full validation executed | **Pass** — 40/40 records, schema valid |
| S1 families not catastrophically worse than S1 full | **Mixed** — diagnosis/medication OK; seizure below S1 full |
| New families useful signal | **Pass** — investigation strong; comorbidity needs work |
| Cap-25 as promotion proxy | **Caveat** — comorbidity and seizure optimistic by ~7–11pp |

**Recommended next pull (Thread C):**

1. Treat v1.2 as the **full-validation baseline** for S2 (do not retune S1 on validation).
2. If iterating comorbidity: target **jerk FP suppression** and affirmed-history precision on the 15 records outside cap-25 — v1.3 S2-only, cap-25 regate then full replay.
3. Proceed to **S2→S4 schema ladder** planning only if comorbidity full F1 is acceptable for research goals (~64% may be sufficient for ladder design; not for benchmark reproduction).
4. Architecture ablation (monolithic vs field-group) remains **blocked until** this baseline is recorded in Kanban (now done).

**Do not:** compare 80.6% micro F1 to S1-only 92.3% full as a single headline; field-family scope differs.

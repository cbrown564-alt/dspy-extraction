# ExECT S4 Medication-Temporality Post-Classifier — Inspection (GPT cap-25)

Date: 2026-05-20  
Comparison group: `exect_s4_temporality_deterministic_v1`  
Pre-registration: `docs/exect_s4_temporality_deterministic_preregistration_20260520.md`

## Run artifacts

| Arm | Run ID | Config |
| --- | --- | --- |
| **L1 baseline** | `exect_s4_temporality_l1_baseline_cap25_gpt4_1_mini_20260520T203755Z` | `exect_s4_temporality_l1_baseline_cap25_gpt4_1_mini.json` |
| **H1 post classifier** | `exect_s4_temporality_h1_post_classifier_cap25_gpt4_1_mini_20260520T203803Z` | `exect_s4_temporality_h1_post_classifier_cap25_gpt4_1_mini.json` |

Fixed controls: cap-25 ExECTv2 validation, `exect_s4_field_family`, `exect_s4_field_family_deterministic_v1`, GPT 4.1-mini, prompt `exect_s4_field_family_v1_2_label_policy`.

Varied factor: medication-temporality-only `H1_post_deterministic` post classification (`exect.medication_temporality.post_classifier.v1`) vs L1 single-pass.

## Headline metrics

| Arm | **MT precision** | MT F1 | MT recall | Micro F1 | Diagnosis | Seizure_type | Medication |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| L1 baseline | **46.8%** | 63.7% | 100.0% | 69.5% | 95.2% | 90.9% | 69.0% |
| H1 post classifier | **61.3%** | 63.3% | 65.5% | 69.9% | 95.2% | 90.9% | 69.0% |

Primary delta (H1 − L1): **+14.5pp medication_temporality precision** (passes ≥2pp promotion gate).

F1 guard: **−0.4pp medication_temporality F1** (does not regress ≥2pp).

H1 dropped 31 of 62 raw MT predictions (non-ASM removals, unknown abstention, and evidence-aligned reclassification). Recall fell 100% → 65.5% while F1 held; gain is not empty-abstention on sparse support.

Frozen S3-family regression guard: diagnosis, seizure_type, annotated_medication, investigation, and comorbidity unchanged between arms.

## Decisions

| Arm | Outcome | Rationale |
| --- | --- | --- |
| **L1 baseline** | **Hold (cap-25 reference)** | 46.8% MT precision; 100% recall reflects over-extraction of non-ASM and wrong-status tags. |
| **H1 post classifier** | **Hold (cap-25 gate passed)** | +14.5pp MT precision with stable F1; eligible for full validation (40). Do not port to Qwen until full gate clears. |

## Interpretation

Post-position deterministic classification is the first ExECT S4 family probe to pass its cap-25 gate. Unlike rejected H2 pre-vocab paths (S1, medication slice, S4 frequency), post-hoc evidence-aligned filtering targets the known precision-collapse mode without changing LLM extraction inputs.

The mechanism matches the support-map hypothesis: L1 over-extracts temporality tags (non-ASM, planned/previous confusion); H1 post classifier prunes FPs while preserving most true positives.

## Recommended next work

1. ~~Run full-validation (40) L1/H1 pair under the same comparison group.~~ **Done — H1 rejected at full validation (see below).**
2. Keep L1 frozen as S4 GPT default; do not enable H1 post classifier in production paths.
3. Optional: planned/taper phrase slice error-read to diagnose full-validation recall collapse before any classifier retune. **Done:** `docs/exect_s4_temporality_planned_taper_error_read_20260520.md`

---

# Full validation addendum (40 records)

Date: 2026-05-20  
Runs: `exect_s4_temporality_l1_baseline_full_gpt4_1_mini_20260520T204207Z`, `exect_s4_temporality_h1_post_classifier_full_gpt4_1_mini_20260520T204216Z`

## Headline metrics (full validation)

| Arm | **MT precision** | MT F1 | MT recall | Micro F1 |
| --- | ---: | ---: | ---: | ---: |
| L1 baseline | **46.4%** | 62.5% | 95.7% | 66.2% |
| H1 post classifier | **56.5%** | 55.9% | 55.3% | 65.6% |

Primary delta (H1 − L1): **+10.1pp medication_temporality precision** (passes ≥2pp gate).

F1 guard: **−6.6pp medication_temporality F1** (fails ≥2pp regression guard — recall collapse 95.7% → 55.3%).

H1 dropped 51 of 97 raw MT predictions on full validation (vs 31/62 on cap-25).

Frozen S3-family regression guard: all non-MT families identical between arms.

## Full-validation decisions

| Arm | Outcome | Rationale |
| --- | --- | --- |
| **L1 baseline** | **Hold (full-validation reference)** | 46.4% MT precision; aligns with cap-25 over-extraction pattern at scale. |
| **H1 post classifier** | **Reject** | Precision gain (+10.1pp) with −6.6pp F1 regression; cap-25 gate was optimistic. Do not port to Qwen or promote. |

## Interpretation

Cap-25 precision-primary success did not generalize to full validation under the preregistered F1 guard. The post classifier's aggressive FP pruning that helped cap-25 (+14.5pp precision, stable F1 on 25 records) removed too many true positives on the broader 40-record split. This matches the preregistration reject path: precision gain with ≥2pp F1 regression.

Keep `exect.medication_temporality.post_classifier.v1` as a tested primitive; do not wire into default S4 recovery without a retuned abstention policy or narrower trigger slice.

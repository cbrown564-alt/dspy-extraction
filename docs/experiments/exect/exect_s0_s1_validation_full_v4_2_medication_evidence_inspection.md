# ExECT S0/S1 Full Validation — Medication & Evidence Read (v4.2)

Date: 2026-05-19

Run artifact:

- `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T202626Z`

Config:

- `configs/experiments/exect_s0_s1_validation_full_gpt4_1_mini.json`
- `prompt_version`: `exect_s0_s1_field_family_v4_2_label_policy`
- `program_variant`: `exect_s0_s1_field_family_single_pass`
- `scorer`: `exect_field_family_deterministic_v1` (unchanged)

Comparison anchors:

| Run | Micro F1 | Med F1 | Evidence support |
| --- | ---: | ---: | ---: |
| v4.2 full (this run) | **78.5%** | 85.1% | 84.0% |
| v4.1 full | 75.3% | 82.7% | 84.7% |
| v4.2 cap-25 | 86.4% | 93.5% | — |

Prior reads: `docs/experiments/exect/exect_s0_s1_validation_full_v4_1_inspection.md`, `docs/experiments/exect/exect_s0_label_policy_v4_2_implementation.md`

## Headline

v4.2 improved seizure F1 (+6.1pp vs v4.1 full) but **medication F1 (+2.4pp) and evidence support (−0.7pp) lag**. Medication remains the best target for v4.3 prompt/bridge work; evidence errors are mostly **header-style or non-contiguous quotes**, not the primary label-policy blocker.

## Medication errors (40 records)

**False positives (11):**

| Record | Predicted | Gold | Tag | Note pattern |
| --- | --- | --- | --- | --- |
| EA0045 | lamotrigine | [] | planned_rx | Prescription request, not current ASM list |
| EA0052 | eslicarbazepine | carbamazepine, zonisamide | planned_switch | “to change to eslicarbazine as below” |
| EA0078 | carbamazepine, levetiracetam | [] | taper_stop / missing_gold | Taper/stop levetiracetam; increase carbamazepine |
| EA0136 | carbamazepine, sodium valproate | epilim chrono | wrong_surface | No carbamazepine/valproate in current list |
| EA0142 | lamotrigine | lamictal | brand_fn | Brand vs canonical mismatch |
| EA0143 | lamotrigine | [] | historical_after_stop | Patient stopped meds; lamotrigine discussed as advice |
| EA0153 | lamotrigine | [] | planned_to_start | “Medications: to start lamotrigine” |
| EA0188 | brivitiracetam, zonismaide | brivaracetam, zonisamide | typo / specificity | Surface typos; gold uses brand spellings |

**False negatives (4):** EA0136 (`epilim chrono`), EA0142 (`lamictal`), EA0188 (`brivaracetam`, `zonisamide`) — mostly **surface/brand** mismatches, not absent medications.

**Precision 79.6% / recall 91.5%** — over-prediction dominates (11 FP vs 4 FN).

## Evidence errors

**17 medication-related evidence support failures** (of ~25 total evidence errors on the split):

| Reason | Count |
| --- | ---: |
| Quote not supported by document text (header prefixes, wrong spacing) | 13 |
| Missing evidence spans | 4 |

Common pattern: model quotes `"Medication: …"` or `"Current anti epileptic medication: …"` lines that do not exactly match note text (spacing, punctuation, tab characters). Ellipsis repair rate is 0% on this run — bridges do not fix these.

Examples: EA0048, EA0050, EA0069, EA0072, EA0142 — medication lines with label prefixes or formatting drift.

## Tagged failure clusters for v4.3

1. **planned_rx / planned_to_start / planned_switch** — EA0045, EA0153, EA0052 (extend `_MEDICATION_EVIDENCE_EXCLUSION_PHRASES` and prompt examples).
2. **taper_stop / missing_gold** — EA0078 (strengthen “no ASM from taper instructions” policy).
3. **historical_after_stop** — EA0143 (exclude advice to restart after self-discontinuation).
4. **brand_fn / typo** — EA0142, EA0188 (deterministic surface repairs: `brivitiracetam`→`brivaracetam`, `zonismaide`→`zonisamide`; audit whether `lamictal` should map to `lamotrigine` for scorer).
5. **evidence_header_quotes** — strip `Medication:` / `Current medication:` prefixes in verifier or bridge when substring search fails.

## Slice expansion

Added 8 records from v4.2 full-validation medication FPs (+ EA0026 granular seizure) to `data/fixtures/exect_s0_label_policy_error_regression_slice.json` (15 → **23 records**). Re-run slice config before v4.3 prompt/bridge changes.

## Verify-repair probe (bounded)

Following diagnosis-recall negative read, implemented **confirm-first verify-repair** (no add-only diagnosis recall):

- Program: `exect_s0_s1_field_family_verify_repair`
- Config: `configs/experiments/exect_s0_s1_verify_repair_cap25_gpt4_1_mini.json`
- Deterministic guards: block add-only diagnosis/medication; drop planned/historical medication evidence; require note-contained quotes.

**Cap-25 probe result** (`runs/exect_s0_s1_verify_repair_cap25_gpt4_1_mini_20260519T205419Z`, ~87s, 50 model calls):

| Metric | v4.2 cap-25 (`…202537Z`) | Verify-repair cap-25 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **86.4%** | 83.8% | −2.6pp |
| Medication F1 | **93.5%** | 83.6% | −9.9pp |
| Seizure F1 | 81.2% | **83.6%** | +2.4pp |
| Diagnosis F1 | 84.2% | 84.2% | 0 |
| Evidence support | 88.8% | **97.4%** | +8.6pp |

**Decision:** Verify-repair **fixes evidence quotes** but **regresses medication F1** on the cap-25 slice (likely over-removal or confirm-first blocking valid ASM). **Do not promote** to full validation. Keep v4.2 monolithic as anchor; pursue v4.3 **prompt/bridge** medication guardrails from the tagged clusters above. Optional: bounded verifier pass on **evidence only** (future hypothesis).

## Audit guidance

Grounded in `docs/datasets/exect/exect_gold_label_audit.md` and `exect-label-policy-alignment`: benchmark-facing annotated medication only; temporality not scored; `missing_gold` flags preserved; scorer unchanged.

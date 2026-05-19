# ExECT Diagnosis-Recall Probe Inspection

Date: 2026-05-19

Run artifact:

- `runs/exect_s0_s1_diagnosis_recall_regression_slice_gpt4_1_mini_20260519T202910Z`

Config:

- `configs/experiments/exect_s0_s1_diagnosis_recall_regression_slice_gpt4_1_mini.json`
- `program_variant`: `exect_s0_s1_field_family_diagnosis_recall`
- `prompt_version`: `exect_s0_s1_diagnosis_recall_v1`
- Slice fixture: `data/fixtures/exect_s0_diagnosis_recall_regression_slice.json` (14 records)

Comparison anchor (same 14 records, rescored from full validation):

- `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T202626Z` (v4.2 monolithic)

Scorer: `exect_field_family_deterministic_v1` (unchanged)

## Hypothesis

After v4.2 plateau (78.5% micro F1 full; diagnosis recall 62%), a bounded add-only diagnosis-recall pass would recover missed co-listed lobe/syndrome or generic epilepsy labels without touching seizure-type or medication fields.

## Headline metrics (14-record slice)

| Variant | Micro F1 | Diagnosis F1 | Diagnosis recall | Diagnosis precision | Seizure F1 | Med F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v4.2 monolithic (subset) | **66.0%** | **51.4%** | 36.0% | **90.0%** | 66.7% | 81.2% |
| Diagnosis-recall probe | 61.8% | 42.9% | 36.0% | 52.9% | 66.7% | 81.2% |

Runtime: ~25s, 28 model calls (~2/record).

## Interpretation

**Negative probe.** Diagnosis recall did not improve on this hard slice; precision dropped sharply because the recall pass added unsupported or wrong diagnoses.

1. **Recall flat** — diagnosis recall stayed at 36% (9/25 gold labels). Misses such as generic `epilepsy` alongside specific labels, `parietal lobe epilepsy` (EA0061), and `epilepsy with generalized tonic clonic seizures on awakening` (EA0116) were not recovered.
2. **Precision regression** — recall pass introduced false positives on EA0116 (`focal epilepsy`, `frontal lobe epilepsy`), EA0137/EA0150/EA0170 (`focal epilepsy`), EA0143 (`symptomatic structural focal epilepsy`, `temporal lobe epilepsy`), EA0188 (`drug refractory epilepsy`).
3. **Seizure/medication unchanged** — as designed; F1 identical to v4.2 subset for those families.
4. **Evidence support improved slightly** — 89.8% vs ~84% on overlapping records, but label F1 is the gating metric.

## Failure read

Dominant recall-pass failure modes:

| Pattern | Example | Notes |
| --- | --- | --- |
| Generic epilepsy co-list not added | EA0098, EA0131, EA0148, EA0173, EA0174 | Note may state epilepsy; model keeps only specific label |
| Co-listed lobe diagnosis missed | EA0061 | `parietal lobe epilepsy` still absent |
| Syndrome surface missed | EA0116 | On-awakening phrasing not emitted; recall added wrong lobe labels |
| Specificity-collapse gold | EA0188 | Gold wants `focal`, `drug`, `occipital`; recall added `drug refractory epilepsy` instead |
| Over-specific recall FP | EA0143, EA0150 | Recall pass inferred focal/temporal labels not in gold |

Many slice records have gold `specificity_collapsed` flags where the benchmark expects both a specific and a generic label (e.g. `epilepsy` plus `focal`). The add-only recall prompt did not reliably surface those co-listed generic labels and instead hallucinated adjacent lobe/syndrome diagnoses.

## Decision

**Do not promote** diagnosis-recall v1 to cap-25 or full validation. v4.2 monolithic remains the ExECT anchor.

## Recommended next pull

1. Keep v4.2 monolithic as headline anchor; do not scale this recall variant.
2. If revisiting diagnosis recall, tighten the recall pass with:
   - confirm-first guards (empty additional list when initial labels are note-supported)
   - explicit generic-epilepsy co-list policy tied to gold audit examples
   - deterministic rejection of recall additions not in `ALLOWED_DIAGNOSIS_LABELS` with note substring evidence check
3. Alternatively probe **full verify-repair** with confirm-first on all three field families — higher cost, but may catch diagnosis without unbounded add-only FPs.
4. Investigate **specificity-collapse co-list** (`epilepsy` + specific label) as a prompt/bridge target rather than a blind second pass.

## Audit guidance

Grounded in `docs/exect_gold_label_audit.md` and `exect-label-policy-alignment` skill: benchmark-facing labels only; add-only merge tagged via program variant metadata; scorer unchanged.

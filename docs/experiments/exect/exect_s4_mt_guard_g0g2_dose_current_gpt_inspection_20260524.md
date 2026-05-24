# ExECT S4 Medication Temporality G0G2 Guard GPT Inspection

Date: 2026-05-24  
Status: **Promote arm to full-validation winner; mechanism open**  
Decision scope: `arm`  
Comparison groups: `exect_s4_medication_precision_guard_gpt_cap25_v1`, `exect_s4_medication_precision_guard_gpt_full_validation_v1`

## Research Question

Does the narrow G0G2 medication-temporality post guard improve ExECT S4 `medication_temporality` precision over L1 without the recall collapse seen in the broad H1 post-classifier?

## Method

| Field | Value |
| --- | --- |
| Dataset / split | ExECTv2, `exectv2_fixed_v1:validation` |
| Model / provider | GPT 4.1-mini / OpenAI |
| Schema | `exect_s4_field_family` |
| Program variant | `exect_s4_field_family_mt_guard_non_asm_dose_current_single_pass` |
| Primitive | `exect.medication_temporality.non_asm_dose_current_guard.v1` |
| Interleaving | `during`, `post` |
| Scorer | `exect_s4_field_family_deterministic_v1` |
| Structured output | provider JSON schema with Pydantic validation |
| Optimizer | none |
| Evidence policy | diagnostic only; empty lists for no supported field values |

The G0G2 guard keeps the G0 non-ASM removal, preserves current ASM labels on prescription-style dose evidence, and prunes planned/previous labels when aligned evidence lacks matching planned/previous cues.

## Run Artifacts

| Scope | Arm | Run ID |
| --- | --- | --- |
| cap-25 | L1 | `exect_s4_mt_guard_l1_baseline_cap25_gpt4_1_mini_20260521T073717Z` |
| cap-25 | G0 | `exect_s4_mt_guard_g0_non_asm_cap25_gpt4_1_mini_20260521T073727Z` |
| cap-25 | G0G2 | `exect_s4_mt_guard_g0g2_dose_current_cap25_gpt4_1_mini_20260524T133106Z` |
| full validation | L1 | `exect_s4_mt_guard_l1_baseline_full_gpt4_1_mini_20260521T074448Z` |
| full validation | G0 | `exect_s4_mt_guard_g0_non_asm_full_gpt4_1_mini_20260521T074459Z` |
| full validation | G0G2 | `exect_s4_mt_guard_g0g2_dose_current_full_gpt4_1_mini_20260524T133253Z` |

The first attempted G0G2 cap-25 run, `exect_s4_mt_guard_g0g2_dose_current_cap25_gpt4_1_mini_20260524T133003Z`, failed before model calls because the ExECT backend had not registered the new S4 variant. The backend routing registration was fixed before the successful runs.

## Results

### Cap-25 Gate

| Arm | MT precision | MT recall | MT F1 | Micro F1 |
| --- | ---: | ---: | ---: | ---: |
| L1 | 46.8% | 100.0% | 63.7% | 69.5% |
| G0 | 58.0% | 100.0% | 73.4% | 71.4% |
| G0G2 | 70.7% | 100.0% | 82.9% | 71.5% |

G0G2 clears the cap-25 gate: `medication_temporality` precision improves by +24.0pp versus L1 and F1 improves by +19.1pp, with no recall loss on the cap-25 slice.

### Full Validation

| Arm | MT precision | MT recall | MT F1 | Micro F1 |
| --- | ---: | ---: | ---: | ---: |
| L1 | 46.4% | 95.7% | 62.5% | 66.2% |
| broad H1 post-classifier | 56.5% | 55.3% | 55.9% | 65.6% |
| G0 | 57.7% | 95.7% | 72.0% | 67.9% |
| G0G2 | 69.4% | 91.5% | 78.9% | 67.7% |

G0G2 clears the full-validation gate: `medication_temporality` precision improves by +23.0pp versus L1 and F1 improves by +16.4pp. Unlike the broad H1 post-classifier, G0G2 does not collapse recall, though it does drop recall by -4.3pp versus L1/G0.

### Frozen-Family Regression Guards

| Family | L1 full F1 | G0G2 full F1 | Delta |
| --- | ---: | ---: | ---: |
| diagnosis | 91.1% | 91.1% | 0.0pp |
| seizure_type | 84.0% | 84.0% | 0.0pp |
| annotated_medication | 71.3% | 71.3% | 0.0pp |
| investigation | 96.7% | 96.7% | 0.0pp |

The configured post guard only moves `medication_temporality`; frozen guard families remain stable.

## Error Read

G0G2 removes the main non-ASM leakage and much of the unsupported planned/previous over-tagging seen in L1. Full-validation residual `medication_temporality` errors are now concentrated in:

- remaining planned/previous ASM false positives such as `levetiracetam|planned`, `carbamazepine|previous`, and `lamotrigine|planned`
- missing brand/generic current rows (`epilim chrono|current`, `lamictal|current`, `clobazam|current`, `sodium valproate|current`)
- a small number of current ASM false positives in missing-gold or conflicting-span documents

This matches the design expectation that G0G2 is a narrow precision arm, not a complete medication-temporality solution.

## Decision

Promote G0G2 as the best tested medication-temporality precision guard arm for ExECT S4 under GPT 4.1-mini validation. Do not close the mechanism class: G1/G3 and an annotated-medication coupled guard remain open design cells, and this result does not replace the broader S4 operational default without a separate integration decision.

## Caveats

- Medication-temporality gold is span-inferred from ExECT `Prescription` annotations; the JSON source has no explicit temporality column.
- Planned medications mentioned in letters but not tagged as `Prescription` remain absent from gold.
- The result is validation-split evidence only, not test reporting or published ExECT Table 1 reproduction.
- Evidence support metrics are diagnostic and were not part of the benchmark-facing gate.
- The G0G2 full run slightly lowers `medication_temporality` recall versus L1/G0, so follow-up should inspect the brand/current-row false negatives before any broader default promotion.

## Next Steps

1. Keep G0G2 available as the promoted medication-temporality guard arm.
2. Add a small G3 brand/generic alias follow-up if medication temporality remains paper-relevant.
3. Consider an annotated-medication coupled guard separately; do not mix it into G0G2 retrospectively.

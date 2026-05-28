# ExECT S3 Residual Error Analysis

Date: 2026-05-21  
Status: Research synthesis from frozen S3 full-validation run artifacts  
Primary run: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z`  
Comparison runs: `runs/exect_s3_validation_full_gpt4_1_mini_20260519T233810Z`, `runs/exect_s3_validation_full_gpt4_1_mini_20260519T234907Z`, `runs/exect_s3_validation_full_qwen35b_ollama_20260520T092244Z`, `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z`  
Dataset / split: `exectv2_fixed_v1:validation`  
Schema: `exect_s3_field_family`  
Scorer: `exect_s3_field_family_deterministic_v1`  
Program: `exect_s3_field_family_single_pass`  
Prompt: `exect_s3_field_family_v1_2_label_policy`  
S1 anchor: `exect_s0_s1_field_family_v4_10_label_policy`  
S2 anchor: `exect_s2_field_family_v1_3_label_policy`

## Question

What still limits ExECT S3 after the v1.2 full-validation freeze, and which residual errors are worth targeting next?

## Audit And Scorer Assumptions

This analysis follows `docs/datasets/exect/exect_gold_label_audit.md`, `docs/policies/deterministic_scorer_semantics.md`, `docs/experiments/exect/exect_s3_phase1_overlap_policy.md`, and `docs/experiments/exect/exect_s3_label_policy_v1_2_implementation.md`.

- S3 is a **nine-family local diagnostic view**: S2 plus birth history, onset, epilepsy cause, and when diagnosed.
- It is not published ExECTv2 Table 1 reproduction.
- S1 and S2 label-policy bridges are reused from frozen v4.10 and v1.3.
- S3-only gold uses affirmed JSON `BirthHistory`, `Onset`, `EpilepsyCause`, and `WhenDiagnosed` entities.
- S3-only labels are canonical CUIPhrase surfaces; age, year, and temporal attributes are not benchmark labels in Phase 1.
- Overlapping phrases can score independently across families, especially cause, comorbidity, birth history, onset, and when diagnosed.
- Pooled S3 micro F1 is not directly comparable to S1, S2, or S4 pooled micro because schema breadth changes.

No scorer semantics were changed for this analysis.

## Metrics Snapshot

| Run | Model | Micro F1 | Precision | Recall | Evidence support | Mismatch entries |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| GPT S3 v1.2 full | GPT 4.1-mini | **72.1%** | 66.4% | 78.8% | 90.1% | 93 |
| GPT S3 v1.1 full | GPT 4.1-mini | 65.1% | - | - | 86.1% | - |
| GPT S3 v1.0 full | GPT 4.1-mini | 56.1% | - | - | 87.8% | 123 |
| Qwen S3 v1.2 full | Qwen3.6:35b | **72.2%** | 67.9% | 77.1% | 94.7% | - |
| GPT S2 v1.3 full | GPT 4.1-mini | 80.9% | 79.6% | 82.2% | 92.7% | 49 |

The v1.2 freeze repaired the two large earlier failures: v1.0 investigation collapse and v1.1 seizure collapse. The remaining S3 problem is broader: comorbidity remains weak, medication precision degrades in the nine-family pass, and S3-only families are sparse and annotation-surface-bound.

Qwen matches GPT on pooled S3 micro but with a different profile: Qwen is stronger on investigation, comorbidity, and sparse S3 slots, while GPT is stronger on diagnosis, seizure type, and annotated medication. Treat them as separate model tracks.

## GPT Residual Family Burden

| Family | F1 | Support | FP | FN | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| `comorbidity` | 59.8% | 48 | 20 | 19 | Main high-support residual burden; surface/atomization and scope drift. |
| `annotated_medication` | 81.4% | 47 | 20 | 1 | Precision problem from wider-pass medication over-extraction. |
| `seizure_type` | 78.1% | 47 | 17 | 6 | Recovered from v1.1 but still emits generic/modernized or misplaced timing surfaces. |
| `epilepsy_cause` | 11.1% | 7 | 10 | 6 | Sparse, overlap-heavy cause/comorbidity/birth-history confusion. |
| `onset` | 13.3% | 3 | 11 | 2 | Very sparse; model over-emits `epilepsy` and ages/timing phrases. |
| `when_diagnosed` | 28.6% | 4 | 8 | 2 | Sparse; many `epilepsy` timing-slot false positives. |
| `birth_history` | 25.0% | 8 | 6 | 6 | Sparse surface mismatch: normal/premature/perinatal variants. |
| `diagnosis` | 92.5% | 42 | 1 | 5 | Strong; residual recall/specificity misses. |
| `investigation` | 93.1% | 30 | 1 | 3 | Strong after v1.2; keep as regression guard. |

The biggest residual count is not in the S3-only families. It is still concentrated in high-support inherited families, especially comorbidity and medication, with sparse S3 families adding noisy low-support errors.

## S2 Families Inside S3

### Comorbidity

GPT comorbidity: **59.8% F1**, 20 FP / 19 FN.  
Qwen comorbidity: **65.3% F1**.

Representative GPT mismatches:

| Document | False positives | False negatives | Gold flags | Read |
| --- | --- | --- | --- | --- |
| EA0016 | `cerebrovascular accident`, `right hemiparesis` | `cva`, `hemiparesis`, `stroke`, `infarct` | - | Semantically close but gold is atomized / abbreviation-heavy. |
| EA0078 | `depression`, `agitation` | - | `missing_gold` | Gold-quality caveat, not clean over-extraction evidence. |
| EA0150 | `flashbacks`, `low mood` | `skull fracture`, `traumatic`, `brain injury`, `subarachnoid hemorrhage` | - | Missed trauma atomization; emits psychiatric symptoms. |
| EA0170 | `recurrent right hemisphere intracerebral haemorrhage`, `previous cerebrovascular events` | `cerebral vascular events`, `intracerebral hemorrhages` | - | British/American and modifier mismatch. |
| EA0179 | `mild learning disabilities` | `learning disabilities`, `episodes`, `syncope`, `episodes of loss of consciousness`, `febrile convulsions` | - | Large recall block plus specificity mismatch. |

Interpretation: comorbidity remains the main high-support S3 weakness. The S2 v1.3 `jerk` fix is not the issue; this is broader surface, specificity, and family-boundary drift in the nine-family pass.

### Annotated Medication

GPT annotated medication: **81.4% F1**, 20 FP / 1 FN.  
Qwen annotated medication: **77.6% F1**.

Top GPT false positives include `carbamazepine` x3, `lamotrigine` x3, `levetiracetam` x2, and singletons such as `aspirin`, `brivaracetam`, `insulin`, `omeprazole`, `ramipril`, `simvastatin`, and `thyroxine`.

Residual shape:

- The problem is precision, not recall.
- Non-ASM and comorbidity-medication leakage appears in the broader pass.
- Brand/spelling issues persist (`eplim`, `eplim chrono`, missed `epilim chrono`).

Interpretation: medication is not a good S3-only optimization target unless the mechanism is a narrow precision guard. It is also a warning that adding S3 fields increases medication over-extraction despite the frozen S1/S2 medication policy.

### Seizure Type

GPT seizure type: **78.1% F1**, 17 FP / 6 FN.  
Qwen seizure type: **72.3% F1**.

Representative GPT mismatches:

| Document | False positives | False negatives | Read |
| --- | --- | --- | --- |
| EA0016 | `focal seizures with altered awareness` | `focal seizure` | Specific model label versus coarse gold. |
| EA0072 | `secondary` | `focal motor seizure` | Generic modifier leakage persists. |
| EA0109 | - | `temporal lobe seizures` | Isolated recall miss. |
| EA0143 | `focal seizures with altered awareness`, `seizures started at the age of 19` | `focal` | Specific seizure label plus onset phrase leakage. |
| EA0174 | `bilateral episodes of limb shaking with retained awareness` | `epileptic seizures` | Descriptive clinical span versus broad gold. |
| EA0179 | `complex partial seizures`, `childhood seizures` | - | Differential/history leakage. |

Interpretation: v1.2 repaired the v1.1 seizure collapse, but seizure still shows the same recurring ExECT surface problem: legacy/coarse gold labels, modernized model terms, generic `secondary`, and timing phrases that belong outside seizure type.

### Diagnosis

GPT diagnosis: **92.5% F1**, 1 FP / 5 FN.  
Qwen diagnosis: **86.1% F1**.

Residual GPT mismatches:

| Document | False positives | False negatives | Gold flags | Read |
| --- | --- | --- | --- | --- |
| EA0116 | `epilepsy` | - | - | Extra generic diagnosis. |
| EA0125 | - | `jme` | `specificity_collapsed` | Specific diagnosis miss. |
| EA0135 | - | `focal onset epilepsy` | - | Recall miss. |
| EA0137 | - | `epilepsy` | - | Generic diagnosis omitted. |
| EA0150 | - | `epilepsy` | - | Generic diagnosis omitted. |
| EA0188 | - | `occipital lobe epilepsy` | `specificity_collapsed` | Specific diagnosis miss. |

Interpretation: diagnosis remains one of the reliable families. Its residuals are the same specificity and generic-label boundary cases seen at S1/S2.

### Investigation

GPT investigation: **93.1% F1**, 1 FP / 3 FN.  
Qwen investigation: **96.6% F1**.

Residual GPT mismatches:

| Document | False positives | False negatives | Read |
| --- | --- | --- | --- |
| EA0102 | `eeg abnormal` | `eeg normal` | Result polarity conflict. |
| EA0142 | - | `mri abnormal` | Recall miss. |
| EA0179 | - | `eeg unknown` | Unknown-result miss. |

Interpretation: v1.2 successfully fixed the v1.0 investigation format collapse. This family should now function mainly as a regression guard for S4 and staged architectures.

## S3-Only Families

### Birth History

GPT birth history: **25.0% F1**, 6 FP / 6 FN.  
Qwen birth history: **37.5% F1**.

Representative residuals:

| Document | False positives | False negatives | Read |
| --- | --- | --- | --- |
| EA0045 | - | `normal birth` | Missed surface. |
| EA0137 | `perinatal insult` | `perinatal injury`, `hypoxia during birth` | Overlap with cause and surface specificity. |
| EA0153 | `premature birth` | `late preterm birth` | Granularity mismatch. |
| EA0185 | `born normally` | `birth was normal` | Paraphrase mismatch. |
| EA0188 | `born slightly prematurely` | `born prematurely` | Modifier mismatch. |

Interpretation: birth history is a sparse surface-matching problem. The model often captures the clinical idea but not the audited CUIPhrase surface.

### Onset

GPT onset: **13.3% F1**, 11 FP / 2 FN.  
Qwen onset: **11.8% F1**.

Top GPT false positive: `epilepsy` x9. Residual false negatives are `epilepsy` and `generalized tonic clonic seizures`.

Interpretation: onset is not stable enough for broad model optimization. Gold support is only 3 labels on the validation split, and the annotation surfaces are often diagnosis/seizure phrases rather than natural onset ages or dates.

### Epilepsy Cause

GPT epilepsy cause: **11.1% F1**, 10 FP / 6 FN.  
Qwen epilepsy cause: **22.2% F1**.

Representative residuals:

| Document | False positives | False negatives | Read |
| --- | --- | --- | --- |
| EA0059 | `early life meningitis` | `meningitis` | Surface expansion mismatch. |
| EA0124 | `secondary to measles` | `measles` | Template/prose mismatch. |
| EA0137 | - | `hypoxia during birth` | Missed birth/cause overlap label. |
| EA0150 | `traumatic brain injury` | `traumatic` | Composite versus atomized gold. |
| EA0170 | `recurrent right hemisphere intracerebral haemorrhage` | `intracerebral haemorrhage` | Modifier specificity mismatch. |

Interpretation: cause has the hardest overlap policy in S3. Some phrases can be clinically valid in both comorbidity and cause, but the scorer expects family-specific annotation surfaces. This should not be tuned with pooled S3 micro as the primary objective.

### When Diagnosed

GPT when diagnosed: **28.6% F1**, 8 FP / 2 FN.  
Qwen when diagnosed: **72.7% F1**, but support is only 4.

Top GPT false positive: `epilepsy` x6. False negatives are both `epilepsy`.

Interpretation: this slot is unstable because the gold often uses `epilepsy` as the annotation-facing CUIPhrase rather than the natural date/age phrase. Qwen's much higher F1 is interesting but too low-support to treat as a stable model conclusion without record-level inspection.

## Document Burden

The heaviest GPT residual documents expose cross-family scope failures:

| Document | FP + FN | Families | Read |
| --- | ---: | --- | --- |
| EA0016 | 12 | seizure_type, medication, comorbidity, cause | Stroke/CVA surface variants plus medication and seizure specificity. |
| EA0150 | 13 | diagnosis, seizure_type, medication, comorbidity, cause, when_diagnosed | Broad cross-family burden; trauma/cause/comorbidity atomization plus timing leakage. |
| EA0179 | 9 | seizure_type, investigation, comorbidity | Comorbidity recall block plus differential/history seizure labels. |
| EA0137 | 9 | birth, diagnosis, seizure_type, comorbidity, cause, onset | Birth/cause overlap plus generic `secondary` and diagnosis miss. |
| EA0143 | 6 | seizure_type, medication, cause, when_diagnosed | Seizure-onset leakage and timing-surface mismatch. |
| EA0188 | 6 | birth, diagnosis, medication, comorbidity, onset | Specificity-collapsed caveats plus birth/onset surface mismatch. |
| EA0136 | 6 | seizure_type, medication, comorbidity | Same S2 medication/seizure surface issues. |

EA0150 is the best full S3 qualitative read candidate. EA0016 is best for comorbidity/cause overlap. EA0137 is best for birth/cause/onset family-boundary behavior. EA0179 is best for comorbidity recall and investigation `unknown`.

## Evidence Diagnostics

GPT has 62 evidence-support errors:

| Field | Evidence errors | No evidence spans | Unsupported quote / offsets |
| --- | ---: | ---: | ---: |
| `comorbidity` | 19 | 14 | 5 |
| `diagnosis` | 17 | 8 | 9 |
| `seizure_type` | 16 | 12 | 4 |
| `annotated_medication` | 4 | 4 | 0 |
| `epilepsy_cause` | 3 | 0 | 3 |
| `birth_history` | 1 | 0 | 1 |
| `investigation` | 1 | 0 | 1 |
| `when_diagnosed` | 1 | 0 | 1 |

Evidence errors are concentrated in the high-support families, especially comorbidity, diagnosis, and seizure type. Evidence support is diagnostic only; it should guide residual review but not become a global prediction filter.

## Interpretation

S3 v1.2 is a reasonable frozen ladder baseline, but it is not a solved nine-family extractor. It succeeded at restoring the two critical S2-family gates: investigation and seizure. The remaining limitations are:

1. **High-support family drift:** comorbidity and medication degrade materially versus S2 inside the nine-family pass.
2. **Sparse annotation-surface families:** birth history, onset, epilepsy cause, and when diagnosed have very low validation support and gold surfaces that often differ from clinically natural outputs.
3. **Cross-family overlap:** cause, comorbidity, birth history, onset, and when diagnosed legitimately share phrases, but the model often places or normalizes them differently from the audited family view.

This makes S3 useful for schema-ladder traceability and for identifying failure modes, but poor as a target for broad prompt churn. Any improvement work should be family-specific and preregistered.

## Recommended Next Work

**Targeted actions (2026-05-21):** `docs/experiments/exect/exect_s1_s3_residual_targeted_actions_20260521.md` — cause bridge `exect_s3_epilepsy_cause_cui_phrase_bridge_design_20260521.md` (P0), medication guard `exect_s3_annotated_medication_precision_guard_design_20260521.md` (P1).

1. **S3 residual qualitative queue** — **Done (2026-05-21)**
   - Tagged queue: `docs/experiments/exect/exect_s1_s3_residual_qualitative_queue_and_taxonomy_20260521.md` § S3 queue.
   - Primary docs: EA0150, EA0016, EA0137, EA0179, EA0143, EA0188, EA0136.

2. **Comorbidity and medication precision guard design**
   - Fixed baseline: GPT `...235439Z`.
   - Target: reduce high-support family burden without regressing investigation or seizure.
   - Avoid broad S3 retuning on validation; start with no-model residual classification.

3. **Sparse-family policy decision**
   - Decide whether birth/onset/cause/when-diagnosed should remain annotation-faithful CUIPhrase extraction, be clinically normalized, or be deferred to CUI-aware reproduction.
   - Do not optimize these families using pooled S3 micro as the primary objective.

4. **Use investigation as a regression guard**
   - v1.2 investigation is strong after the v1.0 collapse.
   - Wider S4 or staged architectures should protect `modality+result` labels and `unknown` behavior.

5. **Keep GPT and Qwen separate**
   - Qwen matches pooled micro but has a different family profile.
   - Qwen's stronger sparse-slot performance should be inspected before turning into a model-ranking claim.

## Caveats

- This analysis uses the current local S3 field-family scorer and fixed validation split. It is not a published ExECTv2 benchmark reproduction.
- S3-only family support is tiny on validation: onset 3, when diagnosed 4, cause 7, birth history 8.
- Some residuals are clinically plausible outputs that conflict with annotation-facing surfaces.
- Overlapping phrases can correctly belong to multiple families in gold; cross-family deduplication would change scorer semantics.
- Pooled S3 micro F1 should not be compared directly to S1, S2, or S4 pooled micro without family-scope caveats.

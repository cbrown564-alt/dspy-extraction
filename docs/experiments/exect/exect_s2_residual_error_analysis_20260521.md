# ExECT S2 Residual Error Analysis

Date: 2026-05-21  
Status: Research synthesis from frozen S2 full-validation run artifacts  
Primary run: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z`  
Comparison runs: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T230407Z`, `runs/exect_s2_validation_full_qwen35b_ollama_20260520T073552Z`, `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`  
Dataset / split: `exectv2_fixed_v1:validation`  
Schema: `exect_s2_field_family`  
Scorer: `exect_s2_field_family_deterministic_v1`  
Program: `exect_s2_field_family_single_pass`  
Prompt: `exect_s2_field_family_v1_3_label_policy`  
S1 anchor: `exect_s0_s1_field_family_v4_10_label_policy`

## Question

What still limits ExECT S2 after the v1.3 full-validation freeze, and which residual errors are worth targeting next?

## Audit And Scorer Assumptions

This analysis follows `docs/datasets/exect/exect_gold_label_audit.md`, `docs/policies/deterministic_scorer_semantics.md`, `docs/experiments/exect/exect_s2_label_policy_v1_3_implementation.md`, and the S2 full-validation inspection.

- S2 is a **five-family local diagnostic view**: diagnosis, seizure type, annotated medication, investigation, and comorbidity.
- It is not published ExECTv2 Table 1 reproduction.
- S1 diagnosis, seizure-type, and annotated-medication bridges are reused from frozen v4.10.
- Investigation labels use canonical modality+result strings such as `eeg normal`, `mri abnormal`, or `eeg unknown`.
- Comorbidity labels come from affirmed `PatientHistory` annotations, excluding seizure-history phrases.
- Medication temporality remains out of scope; S2 medication scoring is annotated prescription name extraction only.
- Pooled S2 micro F1 is not directly comparable to S1, S3, or S4 pooled micro because schema breadth changes.

No scorer semantics were changed for this analysis.

## Metrics Snapshot

| Run | Model | Micro F1 | Precision | Recall | Evidence support | Mismatch entries |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| GPT S2 v1.3 full | GPT 4.1-mini | **80.9%** | 79.6% | 82.2% | 92.7% | 49 |
| GPT S2 v1.2 full | GPT 4.1-mini | 80.6% | - | - | 89.3% | 51 |
| Qwen S2 v1.3 full | Qwen3.6:35b | **82.6%** | 81.1% | 84.1% | 96.4% | - |
| GPT S1 v4.10 full | GPT 4.1-mini | 92.3% | 92.0% | 92.6% | 95.8% | 15 |

The v1.3 S2 freeze is only a small pooled-micro improvement over v1.2 (+0.3pp), but it changes the residual shape: the dominant `jerk` comorbidity FP cluster was removed (7 to 0), while seizure type regressed in the replay. Qwen slightly exceeds GPT on pooled S2 micro, but the family profile differs and should be treated as a separate model track.

## GPT Residual Family Burden

| Family | F1 | Support | FP | FN | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| `comorbidity` | 69.3% | 48 | 18 | 13 | Main S2-specific gap; no longer a `jerk` problem, now broad surface/scope mismatch. |
| `seizure_type` | 71.0% | 47 | 13 | 14 | Biggest inherited-family degradation inside the five-family pass. |
| `annotated_medication` | 90.0% | 47 | 8 | 2 | Mostly over-extraction and brand/generic edge cases. |
| `diagnosis` | 88.9% | 42 | 3 | 6 | Still strong, but lower recall than S1. |
| `investigation` | 90.0% | 30 | 3 | 3 | Strong; residuals are modality/result and `unknown` edge cases. |

S2's main limitation is not field-family coverage in general. It is the interaction between added comorbidity/investigation context and the older S1 families, especially seizure type.

## Comorbidity

GPT comorbidity: **69.3% F1**, 18 FP / 13 FN.  
Qwen comorbidity: **71.6% F1**.

v1.3 fixed the previous dominant FP cluster: `jerk` false positives fell from 7 to 0. The remaining errors are more diffuse.

Representative GPT mismatches:

| Document | False positives | False negatives | Gold flags | Read |
| --- | --- | --- | --- | --- |
| EA0078 | `depression`, `agitation` | - | `missing_gold` | Gold-quality caveat; model emits plausible history labels against empty S1/S2 gold. |
| EA0100 | `hypertension`, `meningitis` | - | `missing_gold` | Same missing-gold caveat. |
| EA0148 | `gastroesophageal reflux`, `smoking` | `head injuries` | - | Scope and annotation-surface mismatch. |
| EA0150 | `traumatic brain injury`, `traumatic subarachnoid haemorrhage`, `low mood`, `flashbacks` | `traumatic`, `brain injury`, `subarachnoid hemorrhage` | - | Semantically close but atomized gold labels differ from model composites. |
| EA0170 | `intracerebral haemorrhage`, `cerebrovascular events` | `cerebral vascular events`, `intracerebral hemorrhages` | - | British/American and surface-number mismatch. |
| EA0179 | - | `episodes`, `syncope`, `episodes of loss of consciousness`, `febrile convulsions` | - | Large comorbidity recall block missed. |

Interpretation: comorbidity is now a surface-policy and annotation-scope problem rather than a single obvious FP cluster. Several errors are clinically close, but exact-family scoring rewards the audited annotation surfaces. A broad comorbidity prompt is unlikely to be clean unless it separates atomized PatientHistory labels from clinically natural composites.

## Seizure Type

GPT seizure type: **71.0% F1**, 13 FP / 14 FN.  
Qwen seizure type: **70.5% F1**.

Top GPT FP pattern: `focal seizures with altered awareness` appears 5 times. Other recurrent shapes include generic `secondary`, modernized seizure names, and umbrella labels.

Representative GPT mismatches:

| Document | False positives | False negatives | Read |
| --- | --- | --- | --- |
| EA0016 | `focal seizures with altered awareness` | `focal seizure` | Specific model label versus coarse gold. |
| EA0072 | `secondary` | `focal motor seizure` | Same generic modifier leakage seen in S1. |
| EA0090 | `generalized tonic clonic seizures` | `focal seizures`, `secondary generalisation`, `generalized tonic clonic seizure` | Plural/surface plus multi-label miss. |
| EA0136 | `generalized convulsions` | `generalized seizures` | Legacy surface mismatch. |
| EA0150 | `focal seizures with altered awareness`, `focal to bilateral convulsive seizures` | `complex partial seizures`, `secondary generalized seizures`, `secondary` | Modernized labels do not match older gold surfaces. |
| EA0185 | `focal seizures with altered awareness` | `focal seizures` | Specificity mismatch. |

Interpretation: seizure type is the biggest inherited-family warning in S2. The S1 scorer/bridges are unchanged, so this is not a pure scorer regression. The wider five-family prompt changes model output behavior, with more specific or modernized seizure terminology and persistent generic-modifier leakage. Static seizure pre-vocab was already rejected at S1; S2 needs either stronger label-policy priority or a staged architecture, not more static candidate hints.

## Diagnosis

GPT diagnosis: **88.9% F1**, 3 FP / 6 FN.  
Qwen diagnosis: **93.8% F1**.

Residual GPT mismatches:

| Document | False positives | False negatives | Gold flags | Read |
| --- | --- | --- | --- | --- |
| EA0098 | `focal epilepsy` | `epilepsy` | - | Specific output versus generic gold. |
| EA0116 | `epilepsy` | - | - | Extra diagnosis. |
| EA0125 | - | `jme` | `specificity_collapsed` | Specific diagnosis miss under collapsed view. |
| EA0135 | - | `focal onset epilepsy` | - | Recall miss. |
| EA0137 | - | `epilepsy` | - | Generic diagnosis omitted. |
| EA0150 | - | `epilepsy` | - | Generic diagnosis omitted. |
| EA0185 | `focal epilepsy` | - | - | Extra diagnosis from suggestive language. |
| EA0188 | - | `occipital lobe epilepsy` | `specificity_collapsed` | Specific diagnosis miss. |

Interpretation: diagnosis remains strong but inherits the same specificity and certainty-boundary issues as S1. The broader S2 prompt does reduce GPT diagnosis F1 versus S1, but diagnosis is not the main S2 bottleneck.

## Annotated Medication

GPT annotated medication: **90.0% F1**, 8 FP / 2 FN.  
Qwen annotated medication: **90.7% F1**.

Residual GPT mismatches:

| Document | False positives | False negatives | Gold flags | Read |
| --- | --- | --- | --- | --- |
| EA0018 | `lamotrigine` | - | - | Extra medication. |
| EA0052 | `eslicarbazepine` | `carbamazepine` | - | Medication substitution or prior/current scope confusion. |
| EA0053 | `levetiracetam` | - | - | Extra medication. |
| EA0078 | `carbamazepine` | - | `missing_gold` | Missing-gold caveat. |
| EA0131 | `carbamazepine` | - | - | Extra medication. |
| EA0136 | `carbamazepine`, `eplim chrono` | `epilim chrono` | - | Brand typo/surface issue plus extra carbamazepine. |
| EA0143 | `lamotrigine` | - | - | Extra medication. |

Interpretation: medication is stable enough for S2. Most errors are annotation-scope and brand/surface issues, not a reason to reopen S1 medication policy. The `epilim` / `eplim` case may be a narrow deterministic spelling repair candidate if it recurs outside this run.

## Investigation

GPT investigation: **90.0% F1**, 3 FP / 3 FN.  
Qwen investigation: **93.1% F1**.

Residual GPT mismatches:

| Document | False positives | False negatives | Gold flags | Read |
| --- | --- | --- | --- | --- |
| EA0016 | `ecg normal` | - | - | ECG is outside the intended EEG/MRI/CT-style S2 investigation view. |
| EA0100 | `ecg normal` | - | `missing_gold` | Missing-gold plus out-of-scope modality. |
| EA0102 | `eeg abnormal` | `eeg normal` | - | Result polarity conflict. |
| EA0179 | - | `eeg unknown` | - | Unknown-result label missed. |
| EA0188 | - | `eeg abnormal` | `specificity_collapsed` | Recall miss on EEG abnormal. |

Interpretation: investigation is strong and its residuals are policy-like: suppress out-of-scope ECG, preserve polarity, and handle `unknown` without over-emitting it. Later S3/S4 experience shows investigation can collapse when the prompt widens, so this family should be protected as a regression guard rather than aggressively retuned in S2.

## Document Burden

The heaviest GPT residual documents combine seizure and comorbidity errors:

| Document | FP + FN | Families | Read |
| --- | ---: | --- | --- |
| EA0150 | 13 | diagnosis, seizure_type, comorbidity | Cross-family modernized seizure labels plus atomized comorbidity mismatch. |
| EA0179 | 6 | seizure_type, investigation, comorbidity | Differential seizure output plus missed comorbidity block and `eeg unknown`. |
| EA0090 | 5 | seizure_type, comorbidity | Multi-label seizure surface mismatch plus headache FP. |
| EA0170 | 6 | seizure_type, comorbidity | Seizure specificity plus cerebrovascular surface variants. |
| EA0136 | 6 | seizure_type, medication, comorbidity | Medication surface typo plus seizure and comorbidity drift. |
| EA0148 | 3 | comorbidity | Scope/surface problem in PatientHistory labels. |
| EA0188 | 3 | diagnosis, investigation, comorbidity | Specificity-collapsed gold caveat plus EEG recall. |

EA0150 is the best S2 qualitative read candidate. EA0179 is the best example of comorbidity recall plus investigation unknown behavior. EA0170 is the best surface-canonicalization example.

## Evidence Diagnostics

GPT has 44 evidence-support errors:

| Field | Evidence errors | No evidence spans | Unsupported quote / offsets |
| --- | ---: | ---: | ---: |
| `comorbidity` | 18 | 13 | 5 |
| `diagnosis` | 13 | 8 | 5 |
| `seizure_type` | 9 | 6 | 3 |
| `annotated_medication` | 3 | 3 | 0 |
| `investigation` | 1 | 0 | 1 |

Evidence errors concentrate in the same families as field mismatches, especially comorbidity. But evidence is still diagnostic, not benchmark-facing. Prior verification and section-aware probes show that evidence-focused changes can reduce field F1, so evidence should guide residual selection rather than act as a global filter.

## Interpretation

S2 is useful but not clean enough to treat as a solved benchmark-facing layer. The v1.3 freeze removed the most obvious comorbidity bug (`jerk`), but the remaining residuals have three different causes:

1. **Comorbidity surface and atomization mismatch:** model composites such as `traumatic brain injury` collide with atomized gold labels such as `traumatic` and `brain injury`.
2. **Multi-family prompt drift in S1 families:** seizure type, diagnosis, and medication all degrade versus S1 even though S1 bridges are reused.
3. **Investigation policy edges:** out-of-scope ECG, polarity, and `unknown` handling are small but important regression guards for wider schemas.

This means S2 should remain frozen as a ladder baseline, but not as a target for broad validation retuning. The next useful work is either a fixed residual qualitative queue or an architecture experiment that protects S1/S2 family priority as schemas widen.

## Recommended Next Work

**Targeted actions (2026-05-21):** `docs/experiments/exect/exect_s1_s3_residual_targeted_actions_20260521.md` — comorbidity `exect_s2_comorbidity_surface_policy_design_20260521.md` (P0), investigation `exect_ladder_investigation_regression_guard_design_20260521.md` (P0).

1. **S2 residual qualitative queue** — **Done (2026-05-21)**
   - Tagged queue: `docs/experiments/exect/exect_s1_s3_residual_qualitative_queue_and_taxonomy_20260521.md` § S2 queue.
   - Primary docs: EA0150, EA0179, EA0170, EA0136, EA0090, EA0148, EA0188.

2. **Comorbidity surface-policy preregistration**
   - Fixed baseline: GPT `...231223Z`.
   - Target: improve comorbidity F1 without regressing seizure type or investigation.
   - Mechanism candidates: post surface canonicalization for narrow spelling/variant cases, or explicit atomized-label policy. Avoid broad semantic repair unless the scorer contract changes.

3. **S2 priority guard for wider schemas**
   - Use S2 residuals as regression guards when running S3/S4 or staged architectures.
   - Protect investigation modality/result and S1 seizure surfaces in any wider prompt.

4. **Do not reopen S1 medication or diagnosis because of S2 alone**
   - Medication and diagnosis residuals are real but secondary.
   - Their S2 errors are mostly scope/surface effects introduced by the wider pass.

5. **Keep GPT and Qwen separate**
   - Qwen S2 slightly exceeds GPT pooled micro and has better evidence support, but this does not erase the known Qwen S1 seizure weakness.
   - Report per-family profiles rather than a single model ranking.

## Caveats

- This analysis uses the current local S2 field-family scorer and fixed validation split. It is not a published ExECTv2 benchmark reproduction.
- Some residuals are clinically plausible outputs that conflict with annotation-facing surfaces.
- Missing-gold documents such as EA0078 and EA0100 should not be used as straightforward over-extraction evidence.
- Cap-25 S2 runs were optimistic on some families; full-validation family breakdown is the safer planning anchor.
- Pooled S2 micro F1 should not be compared directly to S1, S3, or S4 pooled micro without family-scope caveats.

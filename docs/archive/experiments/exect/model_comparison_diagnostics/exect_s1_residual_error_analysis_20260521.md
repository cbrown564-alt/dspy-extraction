# ExECT S1 Residual Error Analysis

Date: 2026-05-21  
Status: Research synthesis from frozen S1 full-validation run artifacts  
Primary run: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`  
Comparison runs: `runs/exect_s1_interleaving_l1_raw_no_bridges_gpt4_1_mini_20260520T190804Z`, `runs/exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z`, `runs/exect_s1_interleaving_h1_post_bridge_qwen35b_ollama_20260520T210722Z`  
Dataset / split: `exectv2_fixed_v1:validation`  
Schema: `exect_s0_s1_field_family`  
Scorer: `exect_field_family_deterministic_v1`  
Program: `exect_s0_s1_field_family_single_pass`  
Prompt: `exect_s0_s1_field_family_v4_10_label_policy`

## Question

What still limits ExECT S1 after the v4.10 full-validation freeze, and which residual errors are worth targeting next?

## Audit And Scorer Assumptions

This analysis follows `docs/datasets/exect/exect_gold_label_audit.md`, `docs/policies/deterministic_scorer_semantics.md`, and the S1 interleaving inspections.

- S1 is a **three-family benchmark-facing view**: diagnosis, seizure type, and annotated medication.
- It is not published ExECTv2 Table 1 reproduction.
- Diagnosis gold uses affirmed JSON `Diagnosis` rows with `DiagCategory == Epilepsy` and `Certainty >= 4`.
- Seizure type gold uses affirmed JSON `Diagnosis` rows with `DiagCategory` `MultipleSeizures` or `SingleSeizure`; seizure-frequency rows are not a seizure-type registry.
- Medication gold uses annotated JSON `Prescription` entities; planned/current/previous temporality is not benchmark-facing in S1.
- Raw diagnoses and gold quality flags are diagnostic context, not extra scored labels.
- Evidence support is diagnostic and is not part of benchmark-facing field-family F1.

No scorer semantics were changed for this analysis.

## Metrics Snapshot

| Run | Model | Micro F1 | Precision | Recall | Evidence support | Mismatch entries |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| GPT S1 v4.10 full | GPT 4.1-mini | **92.3%** | 92.0% | 92.6% | 95.8% | 15 |
| GPT bridge-free raw full | GPT 4.1-mini | 68.6% | - | - | 93.8% | - |
| GPT post-bridge full | GPT 4.1-mini | **92.3%** | - | - | 95.8% | - |
| Qwen post-bridge full | Qwen3.6:35b | 79.0% | - | - | 95.8% | - |

The frozen GPT v4.10 run and the later GPT H1 post-bridge run are metric-identical. The bridge-free comparison shows that benchmark bridges account for a large share of scored S1 performance: +23.7pp pooled micro, with the largest gains in diagnosis and seizure type.

Qwen is a separate model track. Its post-bridge S1 anchor remains much weaker than GPT, mainly because seizure type F1 is 55.7% versus GPT 90.5%.

## GPT Residual Family Burden

| Family | F1 | Support | FP | FN | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| `seizure_type` | 90.5% | 47 | 5 | 4 | Largest residual entry count; mostly coarse/specificity and generic `secondary` surfaces. |
| `diagnosis` | 93.8% | 42 | 1 | 4 | High precision, remaining recall/specificity misses. |
| `annotated_medication` | 92.8% | 47 | 5 | 2 | Small residual burden, mostly annotation scope and brand/generic surface issues. |

S1 is near ceiling on GPT under the current scorer. The residual count is small enough that broad prompt or architecture changes are more likely to trade errors around than produce a stable full-validation gain.

## Diagnosis

GPT diagnosis: **93.8% F1**, 1 FP / 4 FN.  
Qwen post-bridge diagnosis: **95.1% F1**.

Residual GPT mismatches:

| Document | False positives | False negatives | Gold flags | Read |
| --- | --- | --- | --- | --- |
| EA0125 | - | `jme` | `specificity_collapsed` | Specific diagnosis missed under collapsed benchmark-facing view. |
| EA0135 | - | `focal onset epilepsy` | - | Recall miss on a specific epilepsy diagnosis. |
| EA0137 | - | `epilepsy` | - | Generic diagnosis omitted. |
| EA0143 | `symptomatic structural focal epilepsy` | - | - | Clinically richer/specific output exceeds current gold. |
| EA0150 | - | `epilepsy` | - | Generic diagnosis omitted. |

Interpretation: diagnosis is not primarily a precision problem. The remaining errors are boundary cases around specificity, generic epilepsy labels, and annotation-facing certainty/scope. Because the field is already high precision, a broad recall-boosting prompt risks adding clinically plausible but non-gold diagnoses like the EA0143 false positive.

## Seizure Type

GPT seizure type: **90.5% F1**, 5 FP / 4 FN.  
Qwen post-bridge seizure type: **55.7% F1**.

Residual GPT mismatches:

| Document | False positives | False negatives | Read |
| --- | --- | --- | --- |
| EA0072 | `secondary` | `focal motor seizure` | Generic secondary-generalization surface replaces the gold motor seizure label. |
| EA0109 | - | `temporal lobe seizures` | Recall miss. |
| EA0137 | `secondary` | - | Spurious generic modifier. |
| EA0143 | `focal seizures with altered awareness` | `focal` | Specific clinical phrase does not match the sparse gold surface. |
| EA0174 | `prolonged bilateral episodes of limb shaking with retained awareness` | `epileptic seizures` | Clinically descriptive span versus broad gold label. |
| EA0179 | `complex partial seizures` | - | Plausible differential/uncertain seizure-type output absent from gold. |

Interpretation: the key residual pattern is not missing bridge coverage alone. Static seizure pre-vocabulary was tested and rejected on a seizure-heavy slice: seizure F1 fell from 91.5% to 83.3%. The remaining GPT errors mix three causes:

- generic modifier leakage, especially `secondary`;
- annotation-surface mismatch, such as broad `focal` or `epileptic seizures` gold labels;
- clinically plausible outputs from uncertain or differential language.

For GPT, the next seizure work should be a narrow negative guard around generic modifiers and uncertain differential contexts, not another candidate-list or pre-vocab arm. For Qwen, the problem is larger and model-track-specific; bridges recover far less seizure performance than they do for GPT.

## Annotated Medication

GPT annotated medication: **92.8% F1**, 5 FP / 2 FN.  
Qwen post-bridge annotated medication: **89.1% F1**.

Residual GPT mismatches:

| Document | False positives | False negatives | Gold flags | Read |
| --- | --- | --- | --- | --- |
| EA0052 | - | `carbamazepine` | - | Medication recall miss. |
| EA0078 | `levetiracetam`, `carbamazepine` | - | `missing_gold` | Gold has no scored S1 labels; model outputs clinically present medications. |
| EA0136 | `carbamazepine`, `sodium valproate` | `epilim chrono` | - | Brand/generic and medication-history scope conflict. |
| EA0143 | `lamotrigine` | - | - | Extra annotated-medication scope error. |

Interpretation: medication is not the highest-value S1 target. A medication-only pre-vocab slice already regressed medication F1 from 98.3% to 95.1% on Rx-heavy records, and the remaining full-validation residuals are mostly gold-scope or brand/generic edge cases. EA0078 should be treated as a gold-quality caveat rather than model over-extraction evidence.

## Document Burden

Most residual documents have only one or two family mismatches:

| Document | FP + FN | Families | Read |
| --- | ---: | --- | --- |
| EA0136 | 3 | medication | Brand/generic plus scope conflict. |
| EA0143 | 4 | diagnosis, seizure_type, medication | Cross-family specificity/scope boundary case. |
| EA0072 | 2 | seizure_type | Generic `secondary` plus missed focal motor label. |
| EA0078 | 2 | medication | Missing-gold caveat. |
| EA0174 | 2 | seizure_type | Descriptive clinical span versus broad gold label. |
| EA0052 | 1 | medication | Isolated medication recall miss. |
| EA0109 | 1 | seizure_type | Isolated seizure-type recall miss. |
| EA0125 | 1 | diagnosis | Specificity-collapsed diagnosis caveat. |
| EA0135 | 1 | diagnosis | Isolated diagnosis recall miss. |
| EA0137 | 2 | diagnosis, seizure_type | Generic diagnosis miss plus generic `secondary` FP. |
| EA0150 | 1 | diagnosis | Isolated diagnosis recall miss. |
| EA0179 | 1 | seizure_type | Uncertain/differential seizure-type FP. |

EA0143 is the best qualitative read candidate because it touches all three S1 families. EA0136 is the best medication-specific read. EA0072 and EA0174 are the best seizure-surface reads.

## Evidence Diagnostics

GPT has 24 evidence-support errors:

| Field | Evidence errors | No evidence spans | Unsupported quote / offsets |
| --- | ---: | ---: | ---: |
| `diagnosis` | 10 | 7 | 3 |
| `seizure_type` | 10 | 8 | 2 |
| `annotated_medication` | 4 | 4 | 0 |

Evidence errors are broader than benchmark mismatches: some correct benchmark labels still lack accepted evidence spans. Prior section-aware and verification-style probes warn that evidence improvements can come with field F1 regressions. Evidence should therefore remain a diagnostic selector for targeted review, not a global prediction filter.

## Interpretation

S1 is no longer failing as an extraction task on GPT. The current v4.10 baseline is mostly limited by small, annotation-facing boundary cases:

1. **Seizure modifier and uncertainty leakage:** especially generic `secondary` and plausible seizure labels from differential language.
2. **Diagnosis specificity and certainty boundaries:** recall misses on benchmark labels plus occasional clinically richer false positive output.
3. **Medication annotation scope:** brand/generic and missing-gold cases, with little evidence that pre-vocab hints help.

The main mechanism lesson is already clear: v4.10 label policy plus benchmark bridges are doing the heavy lifting. Removing bridges drops GPT full-validation micro F1 from 92.3% to 68.6%. Repackaging those bridges as a new H1 arm is null against production, and static pre-vocabulary arms have been negative.

## Recommended Next Work

**Targeted actions (2026-05-21):** `docs/experiments/exect/exect_s1_s3_residual_targeted_actions_20260521.md` — seizure modifier guard `exect_s1_seizure_modifier_negative_guard_design_20260521.md` (P2).

1. **Do not run broad S1 prompt churn on validation**
   - The residual set is too small for unconstrained prompt iteration.
   - Any new S1 full-validation run should be preregistered and tied to a narrow mechanism.

2. **S1 residual qualitative queue** — **Done (2026-05-21)**
   - Tagged queue: `docs/experiments/exect/exect_s1_s3_residual_qualitative_queue_and_taxonomy_20260521.md` § S1 queue.
   - Primary docs: EA0143, EA0136, EA0072, EA0174, EA0179, EA0125.

3. **Consider a narrow seizure negative guard**
   - Target: suppress generic `secondary` and uncertain/differential seizure-type outputs without reducing recall.
   - Baseline: GPT `...221944Z`; compare on a fixed residual slice before any full validation.
   - Do not reuse rejected static seizure pre-vocab.

4. **Keep medication work out of S1 unless tied to brand/generic repair**
   - Medication-only pre-vocab is rejected.
   - EA0078 should be documented as gold-quality context, not used as a precision-guard training signal.

5. **Separate GPT and Qwen tracks**
   - GPT S1 is near ceiling under current scorer.
   - Qwen S1 remains seizure-limited and likely needs model/prompt-policy work rather than additional post bridges.

## Caveats

- This analysis uses the current local S1 field-family scorer and fixed validation split. It is not a published ExECTv2 benchmark reproduction.
- The split has only 40 validation records; at 92.3% micro F1, a few examples can move family scores noticeably.
- Medication temporality is intentionally out of scope for S1.
- Evidence support is diagnostic only; unsupported evidence should not be converted into a global abstention rule without a preregistered experiment.
- Some residuals are gold-policy or annotation-surface disagreements rather than clearly wrong clinical extraction.

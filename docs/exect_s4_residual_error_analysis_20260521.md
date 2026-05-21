# ExECT S4 Residual Error Analysis

Date: 2026-05-21  
Status: Research synthesis from S4 full-validation run artifacts  
Primary run: `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`  
Comparison run: `runs/exect_s4_validation_full_qwen35b_ollama_20260520T160914Z`  
Dataset / split: `exectv2_fixed_v1:validation`  
Schema: `exect_s4_field_family`  
Scorer: `exect_s4_field_family_deterministic_v1`  
Program: `exect_s4_field_family_single_pass`  
Prompt: `exect_s4_field_family_v1_2_label_policy`

## Question

What still limits ExECT S4 after the v1.2 full-validation freeze, and which residual errors are worth targeting next?

## Audit And Scorer Assumptions

This analysis follows `docs/exect_gold_label_audit.md`, `docs/exect_s4_gold_policy.md`, and `docs/deterministic_scorer_semantics.md`.

- S4 is an **11-family local diagnostic view**, not published ExECTv2 Table 1 reproduction.
- Seizure frequency gold comes from JSON `SeizureFrequency` entities; these rows are **not** seizure-type gold.
- Medication temporality is inferred from annotated `Prescription` span text because the source annotation has no temporality column.
- Planned medications mentioned in note prose but absent from `Prescription` annotations are absent from gold.
- Families are scored independently; overlapping phrases can legitimately score in more than one family.
- Pooled S4 micro F1 is not directly comparable to S1/S2/S3 pooled micro because schema breadth changes.

No scorer semantics were changed for this analysis.

## Metrics Snapshot

| Run | Micro F1 | Precision | Recall | Evidence support | Mismatch entries |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT S4 v1.2 full | 65.5% | 57.0% | 77.0% | 87.7% | 156 |
| Qwen S4 full | 67.5% | 61.3% | 75.2% | 93.4% | 148 |

Qwen is slightly better on pooled S4 micro, but the family profile diverges. GPT is stronger on diagnosis and seizure type; Qwen is stronger on medication, medication temporality, seizure frequency, comorbidity, and sparse S3/S4 extensions. Treat them as separate model tracks.

## GPT Residual Family Burden

| Family | F1 | Support | FP | FN | Read |
| --- | ---: | ---: | ---: | ---: | --- |
| `medication_temporality` | 62.5% | 47 | **52** | 2 | Main FP burden; high recall, low precision. |
| `seizure_frequency` | 45.7% | 43 | 28 | **22** | Main S4-only benchmark gap. |
| `comorbidity` | 59.8% | 48 | 20 | 19 | Surface/synonym and overlap errors. |
| `annotated_medication` | 71.3% | 47 | 36 | 1 | Mostly extra non-gold or non-current medications. |
| `seizure_type` | 84.0% | 47 | 11 | 5 | Good but still emits generic/history-like seizure surfaces. |
| `diagnosis` | 91.1% | 42 | 1 | 6 | Near ceiling; residual recall misses. |
| `investigation` | 96.7% | 30 | 1 | 1 | v1.2 guard basically solved this family. |
| `birth_history` | 23.5% | 8 | 7 | 6 | Sparse support; surface mismatch. |
| `epilepsy_cause` | 10.5% | 7 | 11 | 6 | Sparse, overlap-heavy cause/comorbidity surfaces. |
| `onset` | 0.0% | 3 | 12 | 3 | Sparse slot; model emits plausible dates/ages but not gold surfaces. |
| `when_diagnosed` | 0.0% | 4 | 10 | 4 | Same: plausible timing, wrong annotation slot/surface. |

The biggest residual count is not the lowest-F1 family. The immediate high-value work is concentrated in **medication scope/temporality** and **seizure frequency**, not onset/when-diagnosed, because the latter are sparse and annotation-surface-bound.

## S4-Only Families

### Seizure Frequency

GPT S4 frequency: **45.7% F1**, 28 FP / 22 FN.  
Qwen S4 frequency: **50.0% F1**, 20 FP / 22 FN.

Common residual shapes:

- **Qualitative co-label misses:** `frequency increased`, `frequency decreased`, and `infrequent`.
- **Seizure-free surface mismatch:** gold may be `seizure free`, `seizure free since 2015`, or zero-rate labels like `0 per 3 year`; models often emit a prose-equivalent that does not match.
- **Multi-label frequency blocks:** documents can have rate plus qualitative change labels; partial extraction scores as both TP and FN.
- **Prose-to-template failures:** examples include `several per day`-style prose versus gold `2 per 1 day`, or `1 per 1 week` versus `2 per 1 week`.
- **Spurious frequency on no-frequency docs:** GPT adds `seizure free` on EA0179 despite no gold frequency.

Representative GPT mismatches:

| Document | False positives | False negatives | Read |
| --- | --- | --- | --- |
| EA0008 | — | `frequency increased` | Gold change label not supported by a clear note cue; bridge cannot safely infer. |
| EA0050 | — | `1 per 1 week`, `infrequent`, `frequency decreased` | Multi-label block miss. |
| EA0059 | `0 per 1 year` | `seizure free since 2015`, `seizure free since 2017`, `infrequent` | Multiple seizure-free / qualitative labels collapsed. |
| EA0136 | `a few per year` | `frequency same`, `0 per 3 year` | Prose surface not bridged to gold template. |
| EA0143 | `1 per 1 week`, `seizure free since 2013` | `seizure free`, `0 per 5 year` | Multi-surface conflict. |

Interpretation: this is **not** Gan-style monthly normalization. ExECT S4 wants annotation-facing template surfaces and co-label retention. The next frequency intervention should be an ExECT-specific post-template repair or structured frequency-slot output, not a direct port of Gan temporal candidates.

### Medication Temporality

GPT medication temporality: **62.5% F1**, 52 FP / 2 FN.  
Qwen medication temporality: **69.3% F1**, 36 FP / 3 FN.

The problem is precision, not recall. GPT recall is 95.7%; Qwen recall is 93.6%.

Top GPT false positives:

- `lamotrigine|planned` x5
- `levetiracetam|previous` x5
- `levetiracetam|planned` x4
- `aspirin|current` x3
- `carbamazepine|previous` x3
- `lamotrigine|previous` x3
- `omeprazole|current`, `citalopram|current`, `carbamazepine|current`, `carbamazepine|planned` x2 each

Residual shape:

- **Non-ASM leakage:** aspirin, omeprazole, citalopram, insulin, pravastatin, thyroxine, sertraline, sumitriptan.
- **Plan/previous over-tagging:** the model often emits planned/previous rows when gold only contains annotated prescription spans and conservative temporality inference.
- **Brand/generic misses:** GPT misses `epilim chrono|current` and `lamictal|current` while predicting related canonical forms elsewhere.

Interpretation: broad post-classification already failed as an H1 arm because it improved precision at the cost of recall. The next useful mechanism should be a **narrow precision guard** for obvious non-ASM leakage and duplicate planned/previous rows, with a dose/current fallback that avoids the prior recall collapse.

## S1/S2/S3 Families Inside S4

### Annotated Medication

GPT has 36 FP and only 1 FN. Qwen reduces FP to 20 with 2 FN. This family is mostly an **over-extraction / scope** problem in S4: the model pulls non-gold drugs or planned/previous drugs into annotated medication.

Top GPT FPs include levetiracetam, lamotrigine, aspirin, carbamazepine, omeprazole, ramipril, and midazolam.

### Comorbidity

GPT has 20 FP / 19 FN; Qwen has 20 FP / 16 FN. Many errors are semantically close but surface-misaligned:

- `cerebrovascular accident` vs `cva`
- `right hemiparesis` vs `hemiparesis`
- `stroke` / `infarct` / `lobe damage`
- British/American or specificity variants such as `intracerebral haemorrhage` vs `intracerebral hemorrhages`

This looks like a candidate for **post surface canonicalization**, but overlap with epilepsy cause must be protected because the same clinical phrase can score independently in both families.

### Sparse Surface Families

Onset, when-diagnosed, epilepsy cause, and birth history remain poor, but they are not equally valuable next targets.

| Family | Support | Residual read |
| --- | ---: | --- |
| `onset` | 3 | Model emits plausible ages/dates (`teenage years`, `10 months ago`) while gold uses sparse CUIPhrase-like labels (`epilepsy`, `generalized tonic clonic seizures`). |
| `when_diagnosed` | 4 | Model emits dates/ages/clinic-visit phrases; gold labels are often just `epilepsy`. |
| `epilepsy_cause` | 7 | Semantically close surface mismatches (`stroke` vs `strokes`, `early life meningitis` vs `meningitis`, `traumatic brain injury` vs `traumatic`). |
| `birth_history` | 8 | Negation and surface granularity issues (`his birth was normal` vs `birth was normal`, `prematurity at 34 weeks` vs `late preterm birth`). |

These families need an annotation-surface decision before model work. A few-shot prompt may improve them, but a scorer/bridge policy could also move metrics dramatically. Do not spend broad S4 model budget here until the desired annotation-faithful surface is clearer.

### Strong Families

Investigation is effectively solved under v1.2: 1 FP / 1 FN, both EA0102 polarity (`eeg abnormal` vs `eeg normal`). Diagnosis remains near ceiling. Seizure type is acceptable on GPT but weaker on Qwen, consistent with the earlier Qwen S1 seizure gap.

## Document Burden

The heaviest GPT residual documents combine multiple family errors:

| Document | FP + FN | Families |
| --- | ---: | --- |
| EA0150 | 17 | diagnosis, seizure_type, medication, comorbidity, cause, when_diagnosed, frequency, temporality |
| EA0016 | 15 | medication, comorbidity, onset, cause, frequency, temporality |
| EA0137 | 13 | diagnosis, seizure_type, comorbidity, birth, onset, cause, when_diagnosed, frequency, temporality |
| EA0143 | 13 | seizure_type, medication, cause, when_diagnosed, frequency, temporality |
| EA0059 | 12 | medication, cause, frequency, temporality |

These are good candidates for a qualitative error-read queue because they expose cross-family scope failures. They are poor candidates for isolated single-family metric claims unless each family decision is separated.

## Evidence Diagnostics

GPT has 98 evidence-support errors; Qwen has 60. For GPT:

| Field | Evidence errors |
| --- | ---: |
| comorbidity | 23 |
| medication_temporality | 23 |
| seizure_type | 18 |
| diagnosis | 17 |
| seizure_frequency | 6 |
| annotated_medication | 5 |
| birth_history | 3 |
| epilepsy_cause | 2 |
| when_diagnosed | 1 |

The two main reasons are evenly split:

- 50 predictions have no evidence spans.
- 48 have quotes/offsets not supported by document text.

Evidence is not the primary S4 benchmark metric, but unsupported/missing evidence is concentrated in the same over-extracted families. A prediction-affecting evidence guard might improve precision, but prior evidence/abstention work warns that broad guards can over-prune. Treat evidence as a diagnostic selector for targeted precision guards, not as a global filter.

## Interpretation

S4 is not failing because the model cannot produce broad JSON. It is failing because the broad schema mixes three different problem types:

1. **High-support scope/precision problems:** medication and medication temporality. These are abundant, measurable, and probably actionable with narrow guards.
2. **S4 frequency template problems:** seizure frequency needs ExECT-specific template repair and multi-label retention, not Gan monthly normalization.
3. **Sparse annotation-surface problems:** onset, when-diagnosed, cause, and birth history have low support and gold surfaces that often do not match clinically natural model outputs.

This means a single "better S4 prompt" is unlikely to be the best next move. The next useful work should be family-specific and preregistered.

## Recommended Next Work

1. **S4 frequency surface-repair preregistration**
   - Fixed baseline: GPT `...071248Z`, optionally Qwen `...160914Z`.
   - Varied factor: ExECT-specific frequency `implementation_variant`.
   - Target: improve `seizure_frequency` F1 by at least 3pp without regressing investigation, seizure type, or annotated medication.
   - Mechanism: post-template repair or structured slots for rate, change cue, seizure-free cue, and multi-label retention.

2. **Medication precision guard design**
   - Start with no-model analysis of medication and medication-temporality FPs.
   - Separate non-ASM leakage from planned/previous over-tagging and brand/generic misses.
   - Avoid rerunning the broad H1 post-classifier; it already failed by over-pruning recall.

3. **Sparse-family policy decision**
   - Decide whether onset/when-diagnosed/cause/birth should be annotation-faithful, clinically normalized, or deferred until CUI-aware reproduction.
   - Do not optimize these with pooled S4 micro as the primary objective; support is too small and surface policy is unstable.

4. **Representative S4 residual queue**
   - Use documents EA0150, EA0016, EA0137, EA0143, EA0059, EA0052, EA0136, EA0153, EA0109, and EA0179 for a qualitative cross-family read.
   - Tag each error by family and by whether it is scorer-surface, clinical semantics, over-extraction, or missing evidence.

## Caveats

- This analysis uses the current local field-family scorer. It is not a published ExECT benchmark reproduction.
- Medication temporality gold is span-inferred and incomplete by design; some clinically reasonable planned/current outputs are false positives because the source annotation lacks a temporality field.
- Sparse-family F1 values are unstable on 3-8 gold labels.
- Qwen/GPT pooled micro comparisons hide family divergence and should not be turned into a single model-ranking claim.

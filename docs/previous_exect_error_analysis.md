# Primary Sweep Error Analysis: Seizure Type and Diagnosis

Date: 2026-05-16
Runs analysed: `full_exect_qwen35_best_config__validation__v1`, `full_exect_gemini_flash_best_config__validation__v1`, `hardening_full_frequency_qwen35_no_evidence__validation__v2` (ladder step 4 minimal-config reference)
Past examples reference: `docs/past_examples/`

---

## Summary

Seizure type F1 (0.404 qwen35, 0.511 gemini) and diagnosis exact_match (0.526 qwen35, 0.632 gemini) are the two fields below acceptable reporting standard. This analysis identifies the root causes, quantifies their contribution, and provides concrete fixes for Round 2.

The dominant source of seizure type errors is not a comprehension failure — it is a label granularity mismatch between the ILAE-aligned clinical labels the model has been instructed to use and the coarser benchmark labels in the gold annotation. Correcting this mismatch alone is projected to raise qwen35 seizure type F1 from 0.404 to 0.549 and gemini from 0.511 to 0.653. The remaining errors after that correction are a separable second problem.

Diagnosis errors are driven by two distinct patterns: a `symptomatic` extraction failure and a false-positive inference failure, each with a targeted fix.

---

## 1. Seizure Type: Quantitative Breakdown

### 1.1 Raw counts

| Model | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| qwen35 (best_config) | 19 | 32 | 23 | 0.373 | 0.452 | 0.409 |
| gemini (best_config) | 28 | 31 | 14 | 0.475 | 0.667 | 0.554 |
| qwen35 (ladder minimal) | 20 | 30 | 22 | 0.400 | 0.476 | 0.435 |

FPs substantially exceed TPs for qwen35. Gemini has better recall but high FPs.

### 1.2 Document-level failure distribution (qwen35)

Of 40 documents:
- F1 = 1.0 (perfect): 8
- F1 = 0.0 (complete failure): 22
- FP-only errors (extracts wrong types, no misses): 9
- FN-only errors (misses types, no hallucinations): 4
- Both FP and FN: 13

**55% of documents score zero on seizure type.** The bimodal distribution (either perfect or zero) is a signal that these are label selection failures rather than comprehension failures — the model either picks the right label or picks a systematically wrong one for the same clinical content.

### 1.3 Most common error types

**False positives (spurious extractions), qwen35:**

| Label spuriously extracted | Count |
|---|---|
| focal impaired awareness seizure | 7 |
| generalized myoclonic seizure | 6 |
| focal aware seizure | 5 |
| generalized absence seizure | 4 |
| focal to bilateral tonic clonic seizure | 4 |
| complex | 2 |
| others (1 each) | 4 |

**False negatives (missed gold labels), qwen35:**

| Label missed | Count |
|---|---|
| focal seizure | 12 |
| temporal lobe seizure | 2 |
| epileptic seizures | 2 |
| secondary | 2 |
| others (1 each) | 4 |

**The most prominent pattern: `focal seizure` missed 12 times; `focal impaired awareness seizure` generated 7 times.** These are the same documents — the model extracts the correct clinical event but uses the ILAE-2017 specific label instead of the coarser gold label.

---

## 2. Root Cause A: Label Granularity Mismatch

### 2.1 The problem

The ExECT gold annotation uses coarser, pre-2017 labels for focal seizures:
- `focal seizure` — the benchmark gold label for any focal seizure

The ILAE 2017 classification introduced more specific terms now in the allowed label list and used by the current models:
- `focal impaired awareness seizure` — ILAE 2017 for focal seizure with alteration of awareness
- `focal aware seizure` — ILAE 2017 for simple focal seizure

When a letter says "focal seizures with altered awareness," the model correctly identifies the seizure type and correctly applies the ILAE 2017 label. The benchmark gold says `focal seizure`. The scorer sees a FP (`focal impaired awareness seizure`) and a FN (`focal seizure`) from the same extraction.

**Case EA0008** (the worked example in `docs/past_examples/med-full-evidence/raw_response.txt`):
- Letter: `"Seizure type and frequency: focal seizures with altered awareness every 3 weeks"`
- Gold: `['focal seizure']`
- qwen35 prediction: `['focal impaired awareness seizure']`
- Score: FP=1, FN=1, F1=0.0
- The past example response for this same letter correctly used `"focal seizures with altered awareness"` as the raw value — it did not normalise to an ILAE label at all.

### 2.2 Quantified impact

If `focal impaired awareness seizure` and `focal aware seizure` are remapped to `focal seizure` (the coarse benchmark label), the simulated F1 improvement is:

| Model | Raw F1 | Coarse-remapped F1 | Gain |
|---|---|---|---|
| qwen35 (best_config) | 0.409 | 0.549 | **+0.140** |
| gemini (best_config) | 0.554 | 0.653 | **+0.099** |
| qwen35 (ladder minimal) | 0.435 | 0.565 | **+0.130** |

This is a label instruction problem, not a model capability problem, and it affects the minimal-config baseline as well as the best_config. The ILAE guideline amplifies it (qwen35 best_config shows more ILAE-specific labels than ladder minimal) but does not cause it alone — `focal impaired awareness seizure` is in the allowed list presented to every model.

### 2.3 How the past prompts handled this

`docs/past_examples/med-full-no-evidence/prompt.txt` (the `e3` full extraction prompt, which achieved better seizure results) included this example:

> Example 1: "She continues to have focal impaired awareness seizures approximately twice a month. EEG showed left temporal spikes."
> → `"seizure_types":["focal seizure"]`

The example explicitly showed that the description "focal impaired awareness seizures" maps to the coarse benchmark label `focal seizure`. The model learned the mapping from the example, not from the label name alone.

The current system provides the same letter description, includes `focal impaired awareness seizure` in the allowed label list, and adds ILAE guidance to "use clinically natural epilepsy reasoning." Without the anchoring example, the model naturally uses the more specific label.

### 2.4 The ILAE guideline amplification

The `ilae_clinical_rich` guideline inserts:

> "Use clinically natural epilepsy reasoning. Distinguish focal, generalized, combined, and uncertain epilepsy descriptions."

This instruction, combined with `focal impaired awareness seizure` being in the allowed list, actively encourages the ILAE-specific label over the coarser benchmark label. The guideline was designed for clinical use but is operating in a benchmark evaluation setting where the gold was annotated before ILAE 2017 terminology was standard.

---

## 3. Root Cause B: Spurious Specific-Type Extractions

After remapping `focal impaired awareness seizure` and `focal aware seizure`, substantial FPs remain:

| Remaining spurious labels | qwen35 | gemini |
|---|---|---|
| generalized myoclonic seizure | 6 | 7 |
| generalized absence seizure | 4 | 5 |
| focal to bilateral tonic clonic seizure | 4 | 3 |
| nocturnal seizures | 0 | 2 |
| convulsive seizure | 0 | 2 |

These are different from the label granularity issue — the model is generating specific seizure subtypes that are not in the gold at all.

**Case EA0052** — letter header says "Diagnosis: temporal lobe epilepsy." The patient's current seizure types are not explicitly named in the narrative, only that "he has had 4 more attacks." Gold: `[]` (no explicit seizure type stated). Prediction: `['temporal lobe seizures']`. The model infers a seizure type from the diagnosis line. Gold annotation policy excludes inferred types; only types explicitly stated in the letter are gold.

**Case EA0148** — gold seizure type is `focal seizure`. qwen35 predicts `['focal aware seizure', 'focal impaired awareness seizure', 'focal to bilateral tonic clonic seizure']` — three labels for what the gold treats as a single focal seizure. The secondary generalisation (tonic clonic) is mentioned in the letter but the gold does not include it as a separate type.

The pattern: models extract multiple seizure types from a letter that contains a single seizure semiology description with a secondary component (e.g., secondary generalisation). Gold annotates the index type only; models extract both the index type and secondary event as separate seizure types.

**Fix**: Explicit instruction that when a letter describes a single focal seizure that may secondarily generalise, extract only the primary type. The past `stage2b_seizure_prompt.txt` handled this implicitly through the segmentation pipeline, which separated CURRENT from HISTORICAL quotes before the extraction step. Without pre-segmentation, the model needs an explicit rule.

---

## 4. Diagnosis: Quantitative Breakdown

| Model | Correct | Wrong | Exact_match |
|---|---|---|---|
| qwen35 | 20/40 | 18/40 + 2 ambiguous | 0.526 |
| gemini | 24/40 | 14/40 + 2 ambiguous | 0.632 |

### 4.1 Substitution error taxonomy (qwen35)

| Gold | Prediction | Count | Category |
|---|---|---|---|
| `['focal epilepsy']` | `symptomatic` | 5 | **Modifier capture** |
| `[]` | `focal epilepsy` | 4 | **False positive inference** |
| `[]` | `''` or `None` | 4 | Scoring artifact (both agree no diagnosis) |
| `['epilepsy']` | `focal epilepsy` | 3 | **Over-specification** |
| `['epilepsy']` | `symptomatic` | 2 | Modifier capture |
| `['drug', 'focal', 'focal epilepsy', 'occipital']` | `drug refractory epilepsies` | 1 | Multi-label collapse |
| `[]` | `juvenile myoclonic epilepsy` | 1 | False positive inference |

**The `[] → ''` cases** are likely scoring artifacts: both gold and prediction agree there is no diagnosis but one is represented as empty list and the other as empty string/null. These 4 cases are scoring as wrong but are substantively correct extractions. This should be investigated as a potential scoring bug before reporting.

### 4.2 Root Cause 1: Modifier capture (5+2 = 7 cases)

**Case EA0008**: letter says `"Diagnosis: symptomatic structural focal epilepsy"`. Gold collapses to `focal epilepsy`. Both qwen35 and gemini predict `symptomatic`. The model correctly reads the first word of the diagnosis line and outputs it as the label value. `symptomatic` is a valid label in the benchmark list, so no schema error is triggered — it is simply the wrong normalisation.

This pattern affects every letter whose diagnosis line begins with "symptomatic" (a common clinical prefix for structural/lesional epilepsies). The past `stage2d_diagnosis_prompt.txt` prevented this by providing only 5 constrained labels (`epilepsy`, `focal epilepsy`, `generalized epilepsy`, `juvenile myoclonic epilepsy`, `status epilepticus`) and the strict instruction "Do not invent a diagnosis if the letter does not clearly support one." The `symptomatic` label was not in the allowed set, so the model had to map `symptomatic structural focal epilepsy` to `focal epilepsy`.

The current allowed label list includes `symptomatic` as a standalone label. Without an example showing the normalisation, models capture the surface modifier rather than the type.

### 4.3 Root Cause 2: False positive diagnosis inference (4+1 = 5 cases)

**Case EA0016**: letter says `"Diagnosis: single focal seizure"` — a first presentation, not yet classified as epilepsy. Gold: `[]` (no epilepsy diagnosis established). Prediction: `focal epilepsy`. The clinician's diagnosis line says "single focal seizure," which the model correctly interprets as indicating focal pathophysiology and emits `focal epilepsy`. But the gold annotation policy excludes single-event diagnoses.

**Case EA0052**: similar — patient has had attacks but the formal diagnosis in the header is `temporal lobe epilepsy` (used as the diag label) while gold only considers the free-text diagnosis section. Prediction `focal epilepsy` extracts from the header.

The past `stage2d_diagnosis_prompt.txt` addressed this with its strict null policy: "Do not invent a diagnosis if the letter does not clearly support one." But the key gap is that neither the past prompt nor the current system includes an example showing what to do with a provisional or single-event diagnosis header. Without that example, the instruction is insufficient.

### 4.4 Root Cause 3: Over-specification (3 cases)

Letters say "epilepsy" without subtype specification; model emits `focal epilepsy` based on the seizure type evidence in the letter. Gold uses `epilepsy` because the annotator used only the explicitly stated diagnosis. Fix: guideline instruction that the diagnosis label should reflect the explicit diagnosis statement, not the inferred subtype from seizure type evidence.

---

## 5. Comparison to Past Example Prompts

### 5.1 What the past prompts did differently

**`docs/past_examples/med-full-no-evidence/prompt.txt`** (the `e3` constrained extraction prompt with four seizure examples):

1. **Explicit label-mapping examples for seizure types**: Example 1 showed `"focal impaired awareness seizures"` → `"seizure_types":["focal seizure"]`. Example 2 showed `"two episodes per month"` without type specification → `"unknown seizure type"`. Example 3 showed seizure-free status. Example 4 showed historical seizure types explicitly excluded.

2. **Restricted diagnosis label set (5 labels only)**: No `symptomatic`, no `focal`, no `drug refractory epilepsies` — only the five canonical labels plus null. Models could not output `symptomatic` because it wasn't in the allowed set presented in the prompt.

3. **No clinical reasoning instruction**: The prompt said nothing about "clinically natural epilepsy reasoning." It was task-directive: map the letter to the allowed labels using the provided examples.

4. **Explicit null instruction for diagnosis**: "Do not invent a diagnosis if the letter does not clearly support one" — same wording as the past `stage2d_diagnosis_prompt.txt`.

**`docs/past_examples/multi-agent-pipeline/stage2b_seizure_prompt.txt`**: operated on pre-segmented CURRENT seizure quotes, not the full letter. This structural difference matters — by the time this prompt ran, HISTORICAL quotes were explicitly excluded by the segmentation stage. The current single-agent implementation must handle that disambiguation within the same prompt.

**`docs/past_examples/multi-agent-pipeline/stage2d_diagnosis_prompt.txt`**: minimal, five-label diagnosis extraction with a single instruction. Its simplicity was its strength — no label surface variation could leak through.

### 5.2 What the current system does differently

| Dimension | Past (best-performing) | Current |
|---|---|---|
| Seizure type examples | 4 examples showing label mapping explicitly | 2 examples about temporality boundaries only |
| ILAE guidance | None | `ilae_clinical_rich`: "Use clinically natural epilepsy reasoning" |
| Allowed seizure labels | Benchmark coarse set (no `focal impaired awareness seizure`) | Clinical label set including ILAE-specific terms |
| Diagnosis label set | 5 constrained labels, no `symptomatic` | Full benchmark set including `symptomatic`, `drug`, `focal`, etc. |
| Diagnosis null policy | Explicit: "Do not invent a diagnosis" | Stated in evidence rules; no example reinforcing it |
| Task scope | Pre-segmented input (current quotes only) | Full letter (model handles temporality itself) |

The two most impactful differences for benchmark performance are (1) the absence of label-mapping examples and (2) the expanded allowed label set containing ILAE-specific terms.

---

## 6. Projected Impact of Fixes

The following projections are based on the simulated coarse-remapping analysis and the pattern counts above. They represent a ceiling on the achievable gain, not a guaranteed result, since other residual errors remain.

| Fix | Projected seizure F1 gain (qwen35) | Projected seizure F1 gain (gemini) |
|---|---|---|
| Remove ILAE-specific focal labels from allowed list OR add mapping example | +0.140 | +0.099 |
| Add rule/example for single seizure-type per episode (no secondary as separate type) | +0.03–0.05 est. | +0.03–0.05 est. |
| **Seizure type total (conservative)** | **~0.55** | **~0.65** |

| Fix | Projected diagnosis gain (qwen35) | Projected diagnosis gain (gemini) |
|---|---|---|
| Add `symptomatic → focal epilepsy` mapping example | +0.125 | +0.100 |
| Add null example for provisional/single-event diagnoses | +0.075 | +0.075 |
| Fix `[] → ''` scoring artifact | +0.100 | +0.100 |
| **Diagnosis total (conservative)** | **~0.75–0.80** | **~0.80–0.85** |

---

## 7. Recommended Round 2 Changes

### 7.1 Seizure type

**Change 1 — Remove `focal impaired awareness seizure` and `focal aware seizure` from the benchmark label list.** These ILAE-2017 specific terms are in `CLINICAL_SEIZURE_LABELS` but should be removed from `BENCHMARK_SEIZURE_LABELS`. The benchmark gold was annotated using the coarser pre-2017 labels; presenting ILAE-specific alternatives in the allowed list creates a label selection conflict.

> File: `src/clinical_extraction/labels.py`, `BENCHMARK_SEIZURE_LABELS` — add explicit exclusions for `focal impaired awareness seizure` and `focal aware seizure`.

**Change 2 — Add seizure-type label-mapping examples** to `_examples_block` for a new `seizure_type_mapping_examples` policy, or incorporate into `boundary_counterexamples`:

```
- "focal seizures with altered/impaired awareness" → focal seizure  (not focal impaired awareness seizure)
- "absence episodes with EEG spike-wave" → generalized absence seizure  (only if explicitly named)
- If a focal seizure occasionally secondarily generalises, extract the primary type only; do not add secondary generalised tonic clonic as a separate seizure type unless the letter separately names both as current seizure types.
```

**Change 3 — Revise the ILAE guideline insert** to explicitly re-anchor to the benchmark label set:

> "Use clinically natural epilepsy reasoning for diagnosis and seizure-type reasoning. For seizure-type labels, use only the terms in the provided allowed list; do not introduce ILAE-2017 specific terminology not in that list."

### 7.2 Diagnosis

**Change 4 — Add a `symptomatic → focal epilepsy` example** to the examples block:

```
- "symptomatic focal epilepsy" or "symptomatic structural focal epilepsy" → focal epilepsy
- "idiopathic generalised epilepsy" → generalized epilepsy
```

**Change 5 — Add a null-policy example for provisional diagnoses**:

```
- "Diagnosis: first focal seizure" (single event, no established epilepsy diagnosis) → epilepsy_diagnosis_type: null
- Diagnosis must be stated as an established epilepsy diagnosis, not inferred from the seizure type alone.
```

**Change 6 — Restrict the benchmark epilepsy diagnosis allowed list.** The current `BENCHMARK_EPILEPSY_LABELS` includes `symptomatic`, `focal`, `drug`, `refractory epilepsies` and other partial labels that are valid clinically but are FP attractors in benchmark scoring. The five-label constrained set from the past prompts (`epilepsy`, `focal epilepsy`, `generalized epilepsy`, `juvenile myoclonic epilepsy`, `status epilepticus`) achieved cleaner extraction. Consider a new `benchmark_diagnosis_constrained` label set in `labels.py` for use in the primary sweep.

**Change 7 — Investigate the `[] → ''` scoring artifact.** Four qwen35 cases and four gemini cases show gold=`[]` and prediction=null/empty, scored as wrong. If both parties agree there is no diagnosis, this should be a true negative. Check the scoring path in `src/clinical_extraction/scoring/field_scorers.py` for how empty list vs. null is handled in `diagnosis/exact_match_any_gold`.

### 7.3 New conditions for Round 2

These changes require two new conditions per model (qwen35, gemini):

| Condition | Changes from best_config |
|---|---|
| `full_exect_qwen35_sz_diag_tuned` | Remove ILAE-specific labels from list; add mapping examples; add diagnosis null example; add symptomatic fix |
| `full_exect_gemini_sz_diag_tuned` | Same |

A third condition testing label-list change alone (without new examples) would isolate the contribution of the label set change vs. the example change. This is optional if runtime budget is tight.

---

## 8. Appendix: Key Case Examples

### EA0008 — Label granularity (both seizure and diagnosis)
- Letter: `"Diagnosis: symptomatic structural focal epilepsy ... focal seizures with altered awareness every 3 weeks"`
- Gold: `sz=['focal seizure']`, `diag=['focal epilepsy']`
- qwen35: `sz=['focal impaired awareness seizure']`, `diag='symptomatic'`
- Failures: seizure label granularity mismatch; diagnosis modifier capture
- Present in `docs/past_examples/` as the demo letter; past extraction correctly produced `focal seizure` and `focal epilepsy`

### EA0016 — Diagnosis false positive
- Letter: `"Diagnosis: single focal seizure / CVA with right hemiparesis 2017"`
- Gold: `sz=['focal seizure']`, `diag=[]` (single event, not established epilepsy)
- qwen35: `sz=['focal seizure']` (correct), `diag='focal epilepsy'` (false positive)
- The model correctly extracts the seizure type but infers an epilepsy diagnosis that the annotation policy excludes for single-event presentations

### EA0045 — Secondary generalisation as separate type
- Letter: `"episode of altered awareness"` + `"he seemed to go into a day dream"` (focal) with secondary spread implied
- Gold: `sz=['focal seizure']`
- qwen35: `sz=['focal impaired awareness seizure', 'focal to bilateral tonic clonic seizure']`
- Two FPs from one extraction: ILAE-specific label for the focal type; secondary generalisation extracted as a separate type

### EA0052 — Type inferred from diagnosis header
- Letter: `"Diagnosis: temporal lobe epilepsy"` — narrative does not explicitly name seizure type
- Gold: `sz=[]`, `diag=['focal epilepsy']`
- qwen35: `sz=['temporal lobe seizures']`, `diag='focal epilepsy'`
- Diagnosis correct; seizure type inferred from diagnosis line (not from seizure description)

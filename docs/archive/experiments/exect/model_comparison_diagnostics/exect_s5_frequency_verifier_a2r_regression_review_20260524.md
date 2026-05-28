# ExECT S5 Frequency Verifier A2R Regression / Critic Review

Date: 2026-05-24
Kanban card: A2R - A2 regression/critic review
Status: Completed critic review
Decision scope: Actionable recommendations for Pathway A3 prompt/policy refinement

## Executive Summary

The Pathway A2 Candidate-Constrained Frequency Verifier pilot originally suffered a severe 20.0pp recall drop (down to 72.0% recall from 92.0% baseline). Following targeted implementation fixes (case-insensitive evidence substring matching, exact casing recovery, and relaxed medication-control guards), the repaired verifier was evaluated on the cap-25 validation subset.

The repaired verifier successfully recovered a portion of the recall loss while increasing precision further, reaching:
* **71.7% Seizure Frequency F1** (+11.2pp vs. baseline, +3.8pp vs. buggy verifier)
* **67.9% Precision** (+22.8pp vs. baseline, +3.6pp vs. buggy verifier)
* **76.0% Recall** (-16.0pp vs. baseline, +4.0pp vs. buggy verifier)

All other S5 field-family metrics remained stable. While the repaired verifier is a substantial improvement, the recall drop (16.0pp) still exceeds the allowed 3.0pp threshold for direct promotion. This review documents the forensic findings of the resolved bugs, conducts error analysis on the remaining recall loss, and details the prompt/policy refinements needed in Pathway A3 to unlock full-validation readiness.

---

## Metric Comparison (Cap-25 Validation)

All runs evaluated using `exect_s5_core_field_family_deterministic_v1` scorer mode.

| Run / Model Variant | Run ID | Frequency F1 | Frequency Precision | Frequency Recall | Micro F1 |
| --- | --- | ---: | ---: | ---: | ---: |
| **Baseline** (Pre-Vocab AM Guard) | `exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini_20260524T182134Z` | 60.5% | 45.1% | **92.0%** (23/25) | 83.1% |
| **Buggy Verifier** (Initial A2 Pilot) | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T193119Z` | 67.9% | 64.3% | 72.0% (18/25) | 86.6% |
| **Repaired Verifier** (A2 Bug Fixes) | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T194925Z` | **71.7%** | **67.9%** | 76.0% (19/25) | **87.4%** |

---

## Forensic Analysis of Resolved Bugs

### 1. Case-Sensitivity & Casing Recovery
* **Issue**: The initial verifier dropped correct labels in `EA0069` (e.g. `1 per 1 week` and `4 per 3 week`) because the LLM returned evidence with lowercase letters (e.g. "she thinks that...") that failed the case-sensitive `in note_text` check.
* **Fix**: Case-insensitive substring check `.lower() in .lower()` and exact casing recovery from the clinical note text.
* **Result**: `EA0069` rates are now correctly retained.

### 2. Medication Control Guard Relaxation
* **Issue**: In `EA0050` (and `EA0029` in baseline), the phrase "seizures have improved since reducing the lamotrigine" was blocked because "improved" was a medication-control marker, rejecting the valid `frequency decreased` label.
* **Fix**: Removed `"improved"` and `"better"` from the medication-control markers.
* **Result**: Dynamic frequency decreases are now correctly permitted unless explicit static control language (e.g. "controlled", "seizures under control") is present.

---

## Remaining Recall Loss Analysis

A deep dive into the remaining false negatives (recall misses) in the repaired verifier run reveals two main categories of failure: **Over-Logical Verifier reasoning** and **Extractor omission**.

### 1. Over-Logical Verifier Reasoning (Dropped Labels)

The LLM verifier rejected valid initial extraction labels due to overly strict logical reasoning on synonyms and clinical contexts.

#### A. Document [EA0048](file:///c:/Users/cbrow/Code/dspy-extraction/runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T194925Z/predictions.json#L1561-L1570)
* **Initial Extracted Label**: `0 per 3 week`
* **Evidence**: "The last one of these happened around three weeks ago."
* **Gold Label**: `0 per 3 week`
* **Verifier Action**: **Dropped** (`repair` decision)
* **Verifier Reason**: *"The label "0 per 3 week" is not supported because the note states "The last one of these happened around three weeks ago," indicating a seizure occurred within the last three weeks, so zero seizures in three weeks is inaccurate."*
* **Criticism**: In clinical NLP and the ExECT annotation guidelines, "last seizure was 3 weeks ago" indicates the patient has had a seizure-free interval of 3 weeks, which directly maps to `0 per 3 week`. The verifier's strict temporal interpretation (that a seizure occurring exactly 3 weeks ago makes the 3-week rate non-zero) is clinically pedantic and incorrect under benchmark semantics.

#### B. Document [EA0068](file:///c:/Users/cbrow/Code/dspy-extraction/runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T194925Z/predictions.json#L3364-L3372)
* **Initial Extracted Label**: `seizure free`
* **Evidence**: "no further seizures"
* **Gold Label**: `seizure free`
* **Verifier Action**: **Dropped** (`repair` decision)
* **Verifier Reason**: *"The note states "no further seizures" indicating seizure freedom currently, but the diagnosis explicitly states "Infrequent focal seizures," which is the formal diagnosis and more reliable for seizure frequency labeling. The phrase "no further seizures" is not definitive enough to confirm "seizure free" as a label without a specified time frame... Therefore, "seizure free" is dropped."*
* **Criticism**: The verifier over-indexed on the historical diagnosis phrase ("Infrequent focal seizures") to reject the patient's current clinical status ("no further seizures" since the last visit). Under ExECT guidelines, current status (seizure-free since last review) dictates the `seizure free` label. The verifier must treat current status as primary and allow qualitative diagnosis modifiers to coexist or be subordinated.

---

### 2. Extractor Omission (Failed Initial Extraction)

In some cases, the verifier did not get a chance to confirm/reject the label because the first-pass extractor failed to emit it, despite candidates being available.

#### A. Document [EA0069](file:///c:/Users/cbrow/Code/dspy-extraction/runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T194925Z/predictions.json#L3448-L3470)
* **Precomputed Candidates**: Contains `frequency increased` and `seizure free`.
* **Initial Extraction**: Emitted `1 per 1 week`, `4 per 3 week`, and `seizure free`. Missed `frequency increased`.
* **Gold Labels**: `1 per 1 week`, `4 per 3 week`, and `frequency increased`. (Missed `frequency increased` and added FP `seizure free`).
* **Note Text**: *"she is having more generalised tonic clinic seizures. She has had four in the last three weeks... has had up to five weeks seizure free"*
* **Criticism**: The extractor was biased by the phrase "up to five weeks seizure free" and failed to reconcile it with the primary statement "having more generalised tonic clonic seizures." Because it chose `seizure free`, it likely omitted `frequency increased` due to a perceived logical conflict.

---

## Actionable Recommendations for Pathway A3 (Prompt/Policy Refinement)

To resolve the remaining 16.0pp recall gap and prepare the verifier for full validation, we must inject specific **Verification Policy Rules** into the LLM verifier's instructions and prompt context:

1. **Reconcile Seizure-Free Synonyms**:
   * Explicitly instruct the verifier that phrases indicating no seizures since a specific event or visit (e.g., "no further seizures", "seizure free since last review", "remains clear") are valid and sufficient support for the `seizure free` label.
2. **Accept Zero-Rate Boundaries**:
   * Clarify that statements specifying the timing of the last seizure (e.g. "last event was 3 weeks ago", "last seizure in April") support a zero-rate label for that duration (e.g. `0 per 3 week` or `0 per 1 month` respectively). The verifier must not drop zero-rate labels due to pedantic boundary interpretation.
3. **Separate Current Status from Historical/Diagnosis Labels**:
   * Instruct the verifier that the patient's current status (e.g., "seizure free") can coexist with a general diagnostic history (e.g., "Infrequent focal seizures") or other qualifiers. If a label is supported by current clinical note sentences, it must be confirmed even if it seemingly conflicts with a diagnostic category.
4. **Tighten Extractor Reconciliations**:
   * In the extractor stage prompt, remind the model that patients can experience temporary seizure freedom in the past but have increased frequency currently. It must extract *both* if supported, rather than choosing one to satisfy a false logical consistency.

## Conclusion & Promotion Advice

**`proceed_to_a3_with_repaired_verifier_baseline`**

The A2R review confirms that the verifier's mechanism is sound and the major case-sensitive and medication-control bugs have been successfully repaired. The remaining recall loss is not a structural failure of the verifier architecture, but rather a set of addressable prompt-guidance gaps around clinical reasoning semantics. 

We recommend proceeding directly to **Pathway A3 (Frequency prompt/policy refinement)** to implement these refined rules in the verifier and extractor prompts, running cap-25 evaluations to verify recall recovery before performing a full-validation run.

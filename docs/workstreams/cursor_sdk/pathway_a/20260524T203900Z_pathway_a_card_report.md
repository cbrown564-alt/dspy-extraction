# Cursor SDK Pathway A Card Report

## Card

| Field | Value |
| --- | --- |
| **Card ID** | A2R |
| **Title** | A2 regression/critic review |
| **Lane** | review / critic |
| **Mode** | review-only (no source edits, analysis only) |

## Sources Read

**Primary Run & Error Artifacts:**
* `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T193119Z/predictions.json` (verifier predictions)
* `runs/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T193119Z/errors.json` (verifier errors)
* `runs/exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini_20260524T182134Z/predictions.json` (baseline predictions)
* `runs/exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini_20260524T182134Z/errors.json` (baseline errors)

**Source Code & Configs:**
* [exect_s4.py](../../../../src/clinical_extraction/programs/exect_s4.py) — Specifically verifier modules and `_apply_exect_s5_frequency_verifier_guards`
* [kanban_plan.md](../../../planning/kanban_plan.md) — Card requirements and baseline details
* [exect_s5_frequency_verifier_cap25_inspection_20260524.md](../../../archive/experiments/exect/model_comparison_diagnostics/exect_s5_frequency_verifier_cap25_inspection_20260524.md)

---

## Findings: Forensics of the 20.0pp Recall Drop

The A2 verifier cap-25 run achieved a precision lift (from 45.1% to 64.3%, **+19.2pp**) but triggered a severe recall collapse (from 92.0% to 72.0%, **-20.0pp**). A deep-dive analysis of the four target documents (`EA0008`, `EA0050`, `EA0059`, and `EA0069`) reveals three clear failure mechanisms:

### 1. Case-Sensitivity Substring Bug (Primary Technical Defect)
In [exect_s4.py](../../../../src/clinical_extraction/programs/exect_s4.py#L983), the verifier guard performs a case-sensitive substring match:
```python
if evidence_text not in note_text:
    flags.append("evidence_not_in_note")
    continue
```
* **EA0069 Failure:** The first-pass extractor predicted `1 per 1 week` and `4 per 3 week` with lowercased initial evidence fragments (e.g. `she thinks that she has about one a week` and `she has had four in the last three weeks`). However, the actual note starts these sentences with capitalized "She". 
* **Outcome:** The verifier LLM confirmed these correct labels, but the case-sensitive guard rejected them because of the capitalization mismatch. This single bug dropped **two correct gold labels** on `EA0069` and caused a false negative. The run ledger shows 4 documents total (`EA0045`, `EA0069`, `EA0090`, `EA0116`) had labels discarded due to `evidence_not_in_note` flags.

### 2. LLM Quote Paraphrasing (Primary LLM Defect)
Because the verifier requires the LLM to output `seizure_frequency_evidence`, the verifier LLM (`gpt-4.1-mini`) sometimes paraphrases the note or pulls from its reasoning instead of copy-pasting an exact substring.
* **EA0090 Failure:** The verifier decided to keep `1 per 1 year` but generated an evidence quote of `the father cannot recall a seizure before the recent one`. This exact string did not appear in the note body.
* **EA0116 & EA0045 Failure:** The verifier dropped all frequency labels because its proposed evidence quotes did not exactly match the note text, causing `evidence_not_in_note` flags.

### 3. Overly Strict Medication Control Guard (Annotation-Policy Alignment Defect)
The deterministic verifier guard `_frequency_change_from_medication_control` is designed to reject qualitative frequency changes derived solely from ASM control statements:
```python
def _frequency_change_from_medication_control(raw_value: str, evidence_text: str) -> bool:
    # returns True if lamotrigine/improved/etc are present without frequency words
```
* **EA0050 Failure:** The baseline correctly predicted `frequency decreased` with the evidence `I was pleased to hear that his seizures have improved since reducing the lamotrigine.` 
* **Outcome:** The guard flagged this as `medication_control_not_frequency_change` and dropped it. However, the ExECT gold standard *does* consider "seizures have improved since reducing lamotrigine" as a valid indicator of `frequency decreased`. The guard was too restrictive, translating a true prediction into an FN.

### 4. Empty-Evidence Drop on Pass 1 (Recall Ceiling Defect)
* **EA0008 Failure:** The baseline predicted `frequency increased` with no evidence span (`"evidence": []`). The verifier's P1 qualitative evidence gate correctly rejected it because evidence was missing. However, `frequency increased` is a valid gold label. Since the verifier is **reject-only**, it has no mechanism to recover the missing evidence quote or fix the first pass's evidence omission.

---

## Changes Proposed Or Made

No source changes were made during this review-only lane. 

We propose the following targeted code fixes to resolve the recall drop for the next implementation pilot:

### 1. Make Substring Matching Case-Insensitive
Modify [exect_s4.py](../../../../src/clinical_extraction/programs/exect_s4.py#L983) to check lowercased strings:
```diff
-        if evidence_text not in note_text:
+        if evidence_text.lower() not in note_text.lower():
             flags.append("evidence_not_in_note")
             continue
```

### 2. Relax the Medication Control Guard
Soften `_frequency_change_from_medication_control` or bypass it when the raw note explicitly links medication change to general seizure improvement without a negative control context. Alternatively, allow "improved" or "better" to stand for `frequency decreased` unless it is explicitly comorbid-only.

### 3. Evict Paraphrased Quotes in Verifier Instruction
Tighten the prompt description for `ExectS5SeizureFrequencyVerifierSignature.seizure_frequency_evidence` to explicitly forbid paraphrasing, forcing the model to select *only* exact substrings from `note_text`.

---

## Tests / Runs

No new runs were executed. The metrics are derived from:
* **Baseline Run:** `exect_s5_frequency_pre_vocab_am_guard_cap25_gpt4_1_mini_20260524T182134Z`
* **Verifier Run:** `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_cap25_gpt4_1_mini_20260524T193119Z`

We verified the case-sensitivity theory using a Python audit script on the baseline predictions, confirming that the case mismatches in `EA0069` are exactly repaired when evaluated case-insensitively.

---

## Metric Claims

All claims are based on ExECTv2 `validation` split (cap-25) using `exect_s5_core_field_family_deterministic_v1` scorer mode.

* **Baseline (Pre-Vocab AM Guard):** 60.5% F1, 45.1% Precision, 92.0% Recall.
* **A2 Verifier:** 67.9% F1, 64.3% Precision, 72.0% Recall.
* **Delta:** F1 **+7.4pp**, Precision **+19.2pp**, Recall **-20.0pp**.

---

## Scorer / Dataset Semantics Check

* **Raw Data & Splits:** Unchanged.
* **Scorer Mode:** Unchanged (`exect_s5_core_field_family_deterministic_v1`).
* **Verifier Reject-Only Contract:** Verified. The verifier successfully blocked all candidate additions (0 instances of `verifier_added_label_blocked`).
* **Scorer Preservation:** Verified. The verifier did not alter the scoring logic or denominator semantics.

---

## Risks

1. **Precision Decay upon Bug-Fix:** Fixing the case-insensitivity substring check and relaxing the medication control guard will restore recall, but it may allow some false positives to slip through. The net F1 is expected to rise since the recall gain (+20pp) is substantially larger than any potential precision decay.
2. **LLM Paraphrasing Persistence:** Even with prompt instructions, the LLM may occasionally paraphrase quotes. If this remains a problem, we should implement a fallback fuzzy matching algorithm (e.g. Gestalt pattern matching or token-level Jaccard distance) in the deterministic guard rather than rejecting outright.

---

## Promotion Recommendation

**`keep_on_hold_pending_fixes`**

The A2 verifier is NOT ready for full-validation promotion due to the recall collapse. However, the mechanism is validated: the precision lift is substantial (+19.2pp), and the recall drop is primarily driven by clear, addressable engineering bugs (case-sensitive matching and LLM quote-generation mismatch) rather than a failed hypothesis. 

We recommend proceeding to a revised A2I pilot incorporating the case-insensitive matching and quote instructions before moving to prompt-policy refinement (A3).

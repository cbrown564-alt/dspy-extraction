# E12 - Investigation Isolated Ceiling Confirmation

Date: 2026-05-29
Status: complete; isolated ceiling confirmed
Kanban card: E12 - Investigation Isolated Ceiling Confirmation
Dataset/splits: ExECTv2 `validation` and frozen `test` holdout
Model/provider: GPT 4.1-mini / OpenAI and Qwen3.6:35b / Ollama stored S5 runs
Scorer mode: `exect_s5_core_field_family_deterministic_v1`

## Abstract

This note isolates and evaluates the `investigation` family from the S5 validation and test holdout runs. Our results show that investigation performance is near ceiling, reaching F1 scores of **90.4% - 96.7%** on GPT-4.1-mini and **94.9% - 97.2%** on Qwen-35B. The small number of remaining errors are driven by gold annotation omissions and complex clinical modifier/reasoning logic (such as EEGs confirming psychogenic non-epileptic seizures) rather than model extraction capacity. We classify the component as **near ceiling** and unblock downstream pairwise interaction tasks.

## Metric Summary

| Run / Model | Split | F1 | Precision | Recall | Support | TP | FP | FN |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **GPT-4.1-mini Validation** | validation | **96.7%** | 96.7% | 96.7% | 30 | 29 | 1 | 1 |
| **GPT-4.1-mini Test** | test (holdout) | **90.4%** | 89.2% | 91.7% | 36 | 33 | 4 | 3 |
| **Qwen-35B Validation** | validation | **94.9%** | 96.6% | 93.3% | 30 | 28 | 1 | 2 |
| **Qwen-35B Test** | test (holdout) | **97.2%** | 97.2% | 97.2% | 36 | 35 | 1 | 1 |

*Note: S5 runs are `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` (validation) and `test_holdout_exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260527T055059Z` (test/holdout).*

## Modality & Result Normalization Policy

The investigation family maps raw mentions to a structured format of `modality` + `result`:
- **Modalities:** `eeg`, `mri`, `ct`
- **Results:** `normal`, `abnormal`, `unknown`

Example: `"MRI scan around 5 years ago which was normal"` normalizes to `"mri normal"`.
If a scan is mentioned but no result is stated, it normalizes to `unknown` (e.g. `"ct unknown"`).

## Mismatch Analysis & Clinical Context

Across all 4 evaluated runs, only a small number of mismatches (FP/FN) occur:

### 1. Clinical Reasoning & Modifier Gaps (EEGs in psychogenic seizures)
- **Document `EA0102` (Both GPT and Qwen Validation):**
  - *Text:* `"She has been diagnosed with non epileptic psychogenic seizures which is confirmed on EEG."`
  - *Gold:* `['eeg normal', 'mri normal']`
  - *Predicted:* `['eeg abnormal', 'mri normal']`
  - *Clinical logic:* An EEG that confirms non-epileptic seizures is one that is *normal* (meaning it shows no epileptic discharges during events). However, both LLMs extracted `eeg abnormal`, misinterpreting the word "confirmed" as implying a positive (abnormal) finding.
- **Document `EA0056` (GPT Test):**
  - *Text:* `"Last year he had an EEG which captured one of these events and with no EEG changes confirmed..."`
  - *Gold:* `['eeg normal']`
  - *Predicted:* `['eeg abnormal']`
  - *Clinical logic:* GPT failed to resolve the modifier `"no EEG changes"`, extracting `eeg abnormal` instead.

### 2. Incidental/Minor Findings
- **Document `EA0193` (GPT Test):**
  - *Text:* `"MRI 2006, essentially normal apart from tiny scattered hyperintensities"`
  - *Gold:* `['mri normal']`
  - *Predicted:* `['mri abnormal']`
  - *Clinical logic:* The text specifies `"essentially normal"` but notes tiny hyperintensities. The annotation standard codes this as `normal` (incidental findings ignored), while the model is overly conservative and codes it as `abnormal`.

### 3. Scan Mentioned with Unspecified Result
- **Document `EA0062` (GPT and Qwen Test):**
  - *Text:* `"She had a CT head in 2013..."`
  - *Gold:* `['ct unknown']`
  - *Predicted:* GPT `['ct normal']`, Qwen `[]` (FN)
  - *Clinical logic:* No result is specified in the text. GPT defaulted/hallucinated `normal`, while Qwen omitted it.

### 4. Gold Standard Omissions
- **Document `EA0015` (GPT and Qwen Test):**
  - *Text:* `"She continues to get a combination of epileptic and nonepileptic events which was confirmed with an EEG recording."`
  - *Gold:* `[]`
  - *Predicted:* `['eeg abnormal']`
  - *Clinical logic:* The annotation JSON has no `Investigations` entity, representing an annotator omission. The model correctly extracted it, but scored a false positive.

## Holdout Residual Caveats

The holdout split results are presented as diagnostic evidence for ceiling characterization only. Holdout metrics must not be used to tune models, prompts, scorers, or loaders. 

## Conclusion & Action

We confirm that **investigation performance is near ceiling**. The component does not require separate optimization runs. The remaining errors are minor and belong to clinical negation/modifier reasoning and annotation standard/omission bounds.

This confirms the investigation ceiling and unblocks:
1. **Pair 4 (Investigation + Comorbidity)** interaction tests defined under the X2 plan (`docs/experiments/exect/exect_pairwise_interaction_plan_x2_20260529.md`).
2. The component registry status change.

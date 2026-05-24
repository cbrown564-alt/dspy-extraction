# ExECT S5 Seizure Frequency Candidate Precision vs Recall Cap-25 — Inspection

Date: 2026-05-24  
Comparison group: `exect_s5_frequency_candidate_precision_vs_recall_v1`  
decision_scope: **arm** (candidate-density evidence only; not program default swap)

## Purpose

Evaluate whether narrowing injected seizure-frequency candidate lists to high-precision quantified/date templates (excluding common qualitative and generic non-dated seizure-free cues) improves `seizure_frequency` precision and overall F1 on ExECT S5 validation (cap-25).

## Run Artifacts

| Arm | Run ID | Records | Config |
| --- | --- | ---: | --- |
| Monolithic Baseline | `exect_s5_validation_cap25_gpt4_1_mini_20260524T094748Z` | 25 | `exect_s5_validation_cap25_gpt4_1_mini.json` |
| High-Recall Pre-Vocab (H2_pre) | `exect_s5_frequency_pre_vocab_cap25_gpt4_1_mini_20260524T094756Z` | 25 | `exect_s5_frequency_pre_vocab_cap25_gpt4_1_mini.json` |
| High-Precision Pre-Vocab (HP) | `exect_s5_frequency_pre_vocab_high_precision_cap25_gpt4_1_mini_20260524T141503Z` | 25 | `exect_s5_frequency_pre_vocab_high_precision_cap25_gpt4_1_mini.json` |

**Model:** `configs/models/gan_s0_gpt4_1_mini.json` (`gpt-4o-mini-2024-07-18`)  
**Split:** `exectv2_fixed_v1:validation`

## Metrics Comparison (Cap-25)

| Metric | Monolithic Baseline | High-Recall Pre-Vocab | High-Precision Pre-Vocab | Δ HP − High-Recall |
| --- | ---: | ---: | ---: | ---: |
| **seizure_frequency F1** | 47.1% | **60.5%** | 56.3% | −4.2pp |
| Precision | 37.2% | **45.1%** | 43.5% | −1.6pp |
| Recall | 64.0% | **92.0%** | 80.0% | −12.0pp |
| **diagnosis F1** (Guard) | **95.2%** | 93.0% | 93.0% | 0 |
| **seizure_type F1** (Guard) | 90.9% | **92.5%** | 88.2% | −4.3pp |
| **annotated_medication F1** (Guard) | 69.0% | 70.7% | **71.6%** | +0.9pp |
| **investigation F1** (Guard) | **93.8%** | **93.8%** | **93.8%** | 0 |
| **Micro F1** (5 fam pooled) | 75.3% | **78.7%** | 77.3% | −1.4pp |
| Micro Precision | 65.5% | **67.0%** | 66.7% | −0.3pp |
| Micro Recall | 88.7% | **95.2%** | 91.9% | −3.3pp |
| **Evidence quote support** | **93.1%** | 91.0% | 89.4% | −1.6pp |

## Research Analysis & Error Forensics

1. **Recall Deficit**:
   Omiting qualitative cues (e.g. `well controlled`, `stable`, `increasing`) from the candidate list led to a substantial **12.0pp drop in seizure frequency recall** (from 92.0% to 80.0%). The ExECT gold standard contains qualitative labels. By not injecting qualitative candidates, the model lacks pre-computed hints for these concepts and fails to extract them from the note.
   
2. **No Precision Payoff**:
   We hypothesized that filtering out common qualitative cues from the candidate list would reduce false-positive qualitative extractions and boost precision. Instead, precision **dropped slightly** from 45.1% to 43.5%. The model still falsely predicted qualitative labels (like `infrequent` or `frequency same`) even when they were absent from the candidate list, demonstrating that candidate list pruning does not prevent LLM hallucination of qualitative concepts.

3. **Impact on Seizure Type**:
   Interestingly, the high-precision candidate injection also saw a slight regression on the `seizure_type` guard family (88.2% vs 92.5%), suggesting that prompt context/density changes can cross-contaminate extraction performance in related field families.

## Contract Gates

| Gate | Monolithic Baseline | High-Recall | High-Precision |
| --- | --- | --- | --- |
| 25/25 predictions + scorer | Pass | Pass | Pass |
| Schema / validation errors | 0 | 0 | 0 |

## Taxonomy Mapping

| Field | Value |
| --- | --- |
| varied_factor | candidate_density (high-precision vs high-recall) |
| comparison_group | `exect_s5_frequency_candidate_precision_vs_recall_v1` |
| outcome | **reject** (narrowing to high-precision candidates harms recall and overall F1) |
| hybrid_balance_class | `H2_pre_deterministic` |

## Decision

**Reject candidate-list narrowing in favor of high-recall candidates**:

1. **Retain High-Recall Candidate List**: The high-recall candidate generator remains the operational choice for pre-vocab injection runs on ExECT S5.
2. **No Mechanism Closure**: This experiment confirms that pre-computed candidate lists act as a critical memory jogger for qualitative concepts, and filtering them harms performance. Future optimizations should focus on post-processing verifiers or post-classifiers rather than restricting the pre-computed candidate list.

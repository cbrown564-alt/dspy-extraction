# Gan Multi-Event Flag Validation Stratification

Date: 2026-05-21  
Status: Diagnostic stratification of promoted Gan S0 validation run  
Run: `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`  
Dataset / split: `gan_2026_fixed_v1:validation`  
Scorer: `gan_frequency_deterministic_v1`  
Source audit: `docs/datasets/gan/gan_multi_event_single_label_audit_20260521.md`  
Generated artifacts:

- `artifacts/gan_multi_event_flags_20260521/flags.jsonl`
- `artifacts/gan_multi_event_flags_20260521/summary.json`

## Question

Do the multi-event/single-label audit flags explain where the promoted Gan S0 pipeline still misses exact monthly frequency?

## Method

I exported per-record diagnostic flags over all 1,500 Gan JSON records, preserving the Gan audit assumptions:

- `seizure_frequency_number[0]` remains gold.
- `reference[0]` remains a secondary difficulty signal.
- `unknown` and `no seizure frequency reference` remain distinct.
- The flags are diagnostic only and do not change scorer semantics.

The flag exporter uses two kinds of signal:

- Broad note-text frequency mention counts, treated as upper-bound screens.
- Analysis-field language, treated as a more conservative audit-trail signal.

The exported flags were joined to the 299-record promoted GPT validation analysis in `analysis/records.jsonl`.

## Dataset Flag Counts

Clinical records: 1,446.

| Flag / signal | Count | Share |
| --- | ---: | ---: |
| Broad frequency mentions >= 2 | 1,392 | 96.3% |
| Broad frequency mentions >= 3 | 1,285 | 88.9% |
| Analysis highest-frequency language | 515 | 35.6% |
| Analysis multiple-frequency language | 163 | 11.3% |
| Multi-or-highest analysis signal | 551 | 38.1% |
| Label/reference disagreement | 197 | 13.6% |
| Gold evidence multi-span | 102 | 7.1% |
| Cluster adjudication required | 754 | 52.1% |
| Seizure-free conflict | 643 | 44.5% |
| Unknown with event mentions | 179 | 12.4% |

These operational counts are close to, but not identical with, the earlier audit counts because the exporter is a reusable regex implementation rather than the one-off exploratory notebook used for the prose audit. The intended use is stratification, not gold relabeling.

## Validation Stratification

| Stratum | Records | Monthly accuracy | Operational failure rate |
| --- | ---: | ---: | ---: |
| Overall joined validation | 299 | 65.1% | 35.1% |
| Multi-or-highest analysis signal | 109 | 60.2% | 40.4% |
| No multi-or-highest analysis signal | 190 | 67.9% | 32.1% |
| Highest-frequency policy required | 105 | 60.6% | 40.0% |
| Highest-frequency policy not required | 194 | 67.5% | 32.5% |
| Cluster adjudication required | 141 | 61.7% | 38.3% |
| Cluster adjudication not required | 158 | 68.2% | 32.3% |
| Seizure-free conflict | 136 | 58.8% | 41.2% |
| No seizure-free conflict | 163 | 70.4% | 30.1% |
| Unknown with event mentions | 35 | 51.4% | 48.6% |
| Not unknown with event mentions | 264 | 66.9% | 33.3% |
| Gold evidence multi-span | 19 | 36.8% | 63.2% |
| Gold evidence not multi-span | 280 | 67.0% | 33.2% |
| Label/reference disagreement | 39 | 71.8% | 28.2% |
| Label/reference agreement | 260 | 64.1% | 36.2% |

## Monthly Miss Concentration

The validation run has 104 benchmark-severe monthly misses.

| Flag among monthly misses | Count |
| --- | ---: |
| Multiple candidate frequencies | 101 |
| Seizure-free conflict | 56 |
| Cluster adjudication required | 54 |
| Multi-or-highest analysis signal | 43 |
| Highest-frequency policy required | 41 |
| Unknown with event mentions | 17 |
| Gold evidence multi-span | 12 |
| Label/reference disagreement | 11 |
| Historical/current conflict | 6 |

Strict multi/highest analysis signal accounts for 43/104 monthly misses. The broader text-screen multi-candidate flag accounts for 101/104, but that flag is intentionally high-recall and should not be interpreted as a causal label.

## Interpretation

The audit flags support the residual manual read, but with nuance:

1. **Single-label adjudication is real and measurable.** Strict multi/highest records are harder than their complement: 60.2% monthly accuracy versus 67.9%.
2. **The largest practical risk is not only highest-frequency selection.** Gold multi-span evidence, unknown-with-event-mentions, seizure-free conflict, and cluster adjudication produce larger accuracy gaps in this run.
3. **Gold/reference disagreement is not the main residual driver.** Disagreement records are actually easier on monthly accuracy here, matching the earlier residual analysis.
4. **A generic multi-candidate detector is too broad for intervention design.** Almost all monthly misses have multiple broad note-text mentions, so the useful intervention needs typed slots: target priority, denominator provenance, unknown policy, and cluster components.

## Consequence for the Next Primitive

The proposed `gan_s0_exact_frequency_slot_payload_gpt_cap25_v1` should include diagnostic fields that directly map to the high-risk flags:

- `target_priority_cue` for highest/current single-label adjudication.
- `window_source` and `denominator_status` for seizure-free and long-window conflicts.
- `unknown_policy_cue` for unknown-with-event-mentions.
- `cluster_count_or_range`, `cluster_window_count`, `cluster_window_unit`, and `per_cluster_count_or_range` for cluster adjudication.
- `supporting_quote` per slot, not only for the final label, because quote validity alone did not guarantee benchmark-policy correctness.

The next experiment should stratify results by these flags and require improvement on at least the strict multi/highest, seizure-free-conflict, unknown-with-event-mentions, and cluster-adjudication strata before any full-validation promotion.

## Caveats

- These flags are diagnostic regex screens, not human annotations.
- Broad note-text mention counts are upper bounds and include repeated history/plan mentions.
- Analysis-field flags depend on the generator's audit trail and may miss true multi-candidate cases.
- This stratification used the synthetic validation split only; it is not a Gan Real(300)/Real(150) reproduction.

# ExECT Qwen S1 Seizure-Gap Error Analysis - Phase 2 Preregistration

Date: 2026-05-20  
Status: Preregistered no-model Phase 2 first step  
Decision source: `docs/planning/kanban_plan.md`, `docs/experiments/exect/exect_field_family_deterministic_support_map_20260520.md`, `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md`, `docs/taxonomy/taxonomy_primitive_catalog.md`  
Comparison group context: `exect_s1_interleaving_qwen_validation_v1`

## Research Question

Why does Qwen3.6:35b remain far below GPT 4.1-mini on ExECT S1 `seizure_type` after the same benchmark-facing post bridges are applied?

This is an error-analysis preregistration, not a model-backed run preregistration. The Phase 2 decision is to start with frozen-artifact diagnosis because completed ExECT H1/H2 probes show no promoted deterministic intervention to rerun.

## Hypothesis

The Qwen S1 seizure gap is more likely a model-side or prompt-policy failure than a missing deterministic bridge. Error analysis should distinguish plural/singular scorer surfaces, unsupported over-specific labels, secondary-generalisation wording, absence/myoclonic overcalls, and evidence-support failures before any new model-backed prompt or repair arm is proposed.

## Fixed Artifacts

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2 `exectv2_fixed_v1:validation` |
| Records | Frozen validation 40 |
| Schema | `exect_s0_s1_field_family` |
| Field family | Primary: `seizure_type`; context: diagnosis, annotated_medication |
| Scorer | `exect_field_family_deterministic_v1` |
| Qwen run | `runs/exect_s1_interleaving_h1_post_bridge_qwen35b_ollama_20260520T210722Z` |
| GPT reference | `runs/exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z` |
| Qwen raw reference | `runs/exect_s1_interleaving_l1_raw_no_bridges_qwen35b_ollama_20260520T210719Z` |
| Inspection context | `docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md` |

## Non-Goals

- No model calls.
- No prompt edits.
- No new deterministic bridge behavior.
- No H2 pre-vocabulary rerun.
- No published ExECT Table 1 reproduction claim.

## Analysis Plan

1. Extract all `seizure_type` mismatches from Qwen H1 post-bridge full validation.
2. Compare the same documents against GPT H1 post-bridge mismatches.
3. Classify Qwen seizure errors into these preregistered categories:
   - surface inflection mismatch, such as singular/plural.
   - unsupported overcall, such as absence or myoclonic labels absent from gold.
   - under-specific or over-specific focal label.
   - secondary-generalisation label-policy mismatch.
   - missed gold label with no corresponding prediction.
   - evidence quote absent or unsupported.
   - audit/scorer caveat requiring manual review.
4. Summarize counts by category and list record IDs for each class.
5. Recommend exactly one next action: prompt-policy preregistration, narrow post-template repair preregistration, deterministic no-op/synthesis pause, or manual audit review.

## Initial Frozen-Artifact Snapshot

From `errors.json` in the frozen H1 post-bridge runs:

| Track | Seizure mismatch docs | FP count | FN count | Notable pattern |
| --- | ---: | ---: | ---: | --- |
| Qwen H1 | 19 | 23 | 20 | Frequent singular/plural GTCS mismatches, absence overcalls, focal-surface substitutions, and secondary-generalisation misses. |
| GPT H1 | 6 | 5 | 4 | Smaller residual set, overlapping partly with hard label-policy cases. |

Qwen mismatch records: EA0016, EA0029, EA0047, EA0050, EA0069, EA0072, EA0090, EA0098, EA0109, EA0116, EA0124, EA0125, EA0131, EA0136, EA0137, EA0143, EA0150, EA0170, EA0174.

## Decision Gates

| Outcome | Criterion |
| --- | --- |
| Prompt-policy preregistration | Most Qwen errors are unsupported overcalls or model wording choices that GPT avoids under the same bridge path. |
| Narrow post-template repair preregistration | Most residual errors are deterministic surface mismatches not already handled by `exect.seizure_type.benchmark_bridge.v1`, with low risk of adding false positives. |
| Synthesis pause | Errors are heterogeneous and no single-factor intervention can be stated cleanly. |
| Manual audit review | Errors concentrate in gold ambiguity, scorer caveats, or unsupported audit assumptions. |

## Reporting Artifact

Write the completed analysis as:

`docs/experiments/exect/exect_qwen_s1_seizure_gap_error_analysis_20260520.md`

The report must cite run IDs, frozen metrics, scorer mode, category counts, representative record IDs, and the recommended next card before any model-backed ExECT execution resumes.

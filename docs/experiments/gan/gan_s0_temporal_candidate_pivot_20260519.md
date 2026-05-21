# Gan S0 Temporal-Candidate Pivot

Date: 2026-05-19

## Research Question

Why did today's Gan S0 optimization loop stall, and what should replace further prompt-only iteration?

## Source Artifacts

- `docs/datasets/gan/gan_2026_label_audit.md`
- `docs/policies/deterministic_scorer_semantics.md`
- `docs/experiments/gan/gan_s0_qwen35b_regression_slice_inspection_20260519.md`
- `docs/experiments/gan/gan_s0_qwen_regression_slice_three_way_walkthrough_20260519.md`
- `docs/experiments/gan/gan_s0_qwen35b_direct_cap25_guardrails_validation_error_analysis.md`
- `docs/experiments/gan/gan_s0_qwen35b_verify_repair_regression_slice_guardrails_error_analysis.md`
- `docs/experiments/gan/gan_s0_qwen35b_labeled_fewshot_regression_slice_guardrails_error_analysis.md`
- `docs/experiments/gan/gan_s0_qwen35b_labeled_fewshot_verify_repair_regression_slice_guardrails_error_analysis.md`
- `docs/experiments/gan/gan_s0_verify_repair_full_validation_v2_20260519.md`
- `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md`
- `docs/experiments/gan/gan_s0_few_shot_ladder_cap25_inspection_20260519.md`
- `docs/experiments/gan/gan_s0_semantic_optimizer_cap25_followup_20260519.md`
- `docs/experiments/gan/gan_s0_gemini31_flash_lite_full_validation_inspection_20260519.md`
- `docs/planning/kanban_plan.md`

## Summary

Today's work tested several plausible levers for Gan S0 seizure-frequency extraction: larger Qwen output budgets, stronger direct guardrails, GEPA and semantic optimizer variants, LabeledFewShot and BootstrapFewShot ladders, hosted GPT verify-repair, Gemini Flash-Lite comparison, and local-Qwen verify-repair/few-shot hybrids. These experiments improved infrastructure and clarified model behavior, but the active Qwen path remains blocked on the same failure family: infrequent quantified rates that require temporal event aggregation across several note spans.

The strongest conclusion is negative but useful. We are no longer mostly fighting schema validity, evidence support, or deterministic surface normalization. The remaining blocker is semantic window selection: deciding which seizure events belong together, which time interval should be the denominator, and when a short seizure-free interval should not become a canonical seizure-free label.

## What Was Tested

### Qwen output budget and runtime

Hypothesis: Qwen3.6:35b direct extraction might be starved by a low completion budget.

Outcome: Raising direct `max_tokens` from 256 to 1024 did not improve monthly-frequency, Purist, Pragmatic, schema-validity, normalized-label, or invalid-count metrics. It slowed prediction and introduced prompt-footer evidence leakage in at least one long-evidence case. Later verify-repair runs used a larger 4096-token budget to remove verifier truncation as a confound, but this did not unlock the remaining infrequent cases.

Interpretation: Qwen's bottleneck is not broad output-budget starvation.

### Direct Qwen guardrails

Hypothesis: clearer final-label policy could fix unknown/no-reference confusion, YTD denominators, cluster surfaces, and infrequent over-`unknown`.

Key artifacts:

- `runs/gan_s0_qwen35b_direct_regression_slice_guardrails_20260519T151933Z`
- `runs/gan_s0_qwen35b_direct_cap25_guardrails_validation_20260519T154228Z`

Outcome: Direct v2.2 fixed the original 10-record regression slice: 10/10 original targets, 14/14 schema valid, 100% evidence support. It still failed all four infrequent quantified records by predicting `unknown`.

On cap-25, the same prompt regressed to 27.3% monthly on valid predictions, with 3 invalid labels and 0/4 monthly accuracy for gold-pragmatic infrequent records.

Interpretation: text guardrails can stabilize known policy boundaries, but they do not force Qwen to aggregate sparse temporal event histories into quantified infrequent labels.

### GEPA and semantic optimizer paths

Hypothesis: richer optimizer feedback might learn compact benchmark-contract guidance for temporal and label-policy errors.

Key artifacts:

- `runs/gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z`
- `runs/gan_s0_gepa_direct_cap5_qwen35b_ollama_20260519T060700Z`
- `runs/gan_s0_semantic_bootstrap_cap25_gpt4_1_mini_20260519T100255Z`
- `runs/gan_s0_semantic_gepa_cap25_gpt4_1_mini_20260519T100648Z`

Outcome: GEPA became operational, but did not become a reliable quality lever. Hosted GEPA improved schema/evidence behavior on a tiny cap but produced longer instructions and weaker label metrics than the synthesis baseline. Local Qwen GEPA was slow, selected very long instructions, and still drifted into non-canonical labels. Semantic BootstrapFewShot and under-budget semantic GEPA did not clear the cap-25 promotion gate.

Interpretation: optimizer feedback is not the next best lever for this blockage. It tends to add text rather than change the decomposition of the task.

### Few-shot ladders

Hypothesis: demonstration choice might improve direct extraction more than bootstrapped teacher traces.

Key artifacts:

- `runs/gan_s0_ladder_labeled_fewshot_cap25_gpt4_1_mini_20260519T091940Z`
- `runs/gan_s0_ladder_bootstrap_cap25_gpt4_1_mini_20260519T092020Z`
- `runs/gan_s0_ladder_bootstrap_rs_cap25_gpt4_1_mini_20260519T092117Z`

Outcome: On hosted GPT direct cap-25, LabeledFewShot outperformed plain BootstrapFewShot and BootstrapRS on all benchmark-facing label metrics while using much less compile time and token budget. But the local-Qwen LabeledFewShot slice did not unlock infrequent quantification: it stayed at 0/4 infrequent and introduced one abstention.

Interpretation: demonstrations help direct-path stability, but generic fixed demos are not enough. The missing behavior is specific multi-span temporal aggregation, not ordinary format learning.

### Hosted verify-repair

Hypothesis: a second model pass can improve semantic precision and evidence support without hiding scorer changes.

Key artifact:

- `runs/gan_s0_verify_repair_full_validation_gpt4_1_mini_20260519T084732Z`

Outcome: GPT 4.1-mini verify-repair v2 is the current hosted quality anchor: schema 96.7%, monthly 65.4%, Purist 72.7%, Pragmatic 79.2%, evidence 92.7%. It beat the synthesis BootstrapFewShot full-validation baseline on label and evidence metrics, though with two model calls per record and slightly lower schema validity.

Interpretation: verify-repair is viable for hosted GPT, but its success does not transfer automatically to local Qwen, where the verifier damaged correct YTD and cluster outputs.

### Gemini Flash-Lite comparison

Hypothesis: Gemini 3.1 Flash-Lite might offer a cheaper/faster hosted path with comparable label quality.

Key artifact:

- `runs/gan_s0_direct_full_validation_gemini31_flash_lite_20260519T101710Z`

Outcome: Gemini direct full validation was fast and label-competitive: monthly 63.9%, Purist 71.8%, Pragmatic 81.4%, schema 97.3%. Evidence support trailed GPT verify-repair v2: 84.9% versus 92.7%.

Interpretation: Gemini is a latency/cost candidate, not the quality anchor. It does not explain or solve the local-Qwen temporal aggregation blockage.

## The Stuck Point

The 14-record Qwen regression slice isolates the problem.

Direct v2.2 solved the original ten targets but predicted `unknown` for all four infrequent quantified records:

| Record | Gold | Direct v2.2 |
| --- | --- | --- |
| `gan_13123` | `1 per year` | `unknown` |
| `gan_14485` | `2 per 3 month` | `unknown` |
| `gan_14881` | `1 per month` | `unknown` |
| `gan_15306` | `2 to 3 per 15 month` | `unknown` |

Verify-repair v2.3 moved all four off `unknown`, but only one became gold-correct. It also broke previously correct records:

| Record | Gold | Verify-repair failure |
| --- | --- | --- |
| `gan_10751` | `unknown` | repaired to `no seizure frequency reference` |
| `gan_11221` | `unknown` | repaired to `seizure free for 4 month` |
| `gan_12823` | `9 per month` | repaired to `9 per 12 month` |
| `gan_10052` | `4 cluster per 3 month, multiple per cluster` | stripped required per-cluster clause |
| `gan_10003` | `1 cluster per week, multiple per cluster` | collapsed to `1 per week` |
| `gan_13123` | `1 per year` | repaired to the wrong window |
| `gan_14485` | `2 per 3 month` | repaired to short seizure-free |
| `gan_14881` | `1 per month` | repaired to no-reference |

The later v2.4 and LabeledFewShot+verify-repair hybrid recovered stability on original targets, but both stayed at only 1/4 infrequent correct.

## Failure Interpretation

The infrequent records expose two distinct tasks that our current program collapses into one final-label prediction.

1. Easy contiguous aggregation: count and window appear together. `gan_15306` is the successful template: "No further tonic-clonic seizures since 12/2020, although two to three single jerks remain" can become `2 to 3 per 15 month`.

2. Hard multi-span aggregation: the count, dates, and denominator are distributed across the note, often with a tempting recent seizure-free clause. `gan_13123`, `gan_14485`, and `gan_14881` require selecting the annotation-relevant observation window instead of the nearest temporal phrase.

For these hard cases, the model must infer an event table before it can safely emit a Gan label. Direct extraction avoids overclaiming and says `unknown`. Verify-repair tries to force a label but often picks the wrong span.

## Competing Explanations

### Guidelines are unclear

This is partly true. The label scheme defines valid surfaces and conversion rules, but it does not fully operationalize how to choose a denominator when the letter contains a single breakthrough event after a long quiet period, sparse dated events, or a recent short seizure-free interval.

### Gold labels are ambiguous

This is also partly true. The gold labels may be annotation-faithful, but some are not locally obvious from a single evidence span. They appear to depend on the construction-time interpretation and on using the whole generated scenario rather than just the nearest quote. This does not mean they should be rewritten, but it does mean they should be flagged as high-complexity examples.

### The bar is too high

Monthly-frequency exact is intentionally strict and clinically meaningful. Pragmatic category can hide wrong denominators. The bar is high, but lowering it would obscure the exact failure we need to understand.

### We need a radically new approach

For this slice, yes. More final-label prompt text is unlikely to solve it. The next approach should expose intermediate temporal candidates: seizure events, dates, counts, seizure-free intervals, candidate windows, and the selected Gan label. That gives the verifier something structured to check instead of asking it to invent a final label from prose.

## Recommended Pivot

Implement a named experimental bridge, not a scorer change:

`gan_frequency_s0_temporal_candidates`

The first version should be conservative and auditable:

- Extract candidate seizure events with raw phrase, count/range, date/window phrase, seizure type if present, and evidence.
- Extract candidate seizure-free intervals separately from seizure event counts.
- Generate candidate Gan labels only when the event count and denominator window are explicit or derivable from dated events.
- Preserve `unknown` when the candidate table cannot justify a denominator.
- Never turn short seizure-free intervals under six months into `seizure free for N unit`.
- Preserve the existing `gan_frequency_deterministic_v1` scorer unchanged.
- Report candidate-table diagnostics separately from benchmark-facing label metrics.

The immediate gate should remain the 14-record slice:

- original regression targets: 10/10
- infrequent quantified targets: at least 3/4
- schema validity: 100%
- evidence support: 100%

## First Implementation Slice

Start without model calls by adding deterministic temporal-candidate utilities and tests around the four infrequent regression records. This is not intended to solve the whole task deterministically. It is a scaffold for the next DSPy program variant and a way to make the missing reasoning explicit.

The first implementation should:

1. Define a small candidate schema for event mentions and selected windows.
2. Add tests for `gan_13123`, `gan_14485`, `gan_14881`, and `gan_15306` that assert candidate extraction can represent the gold-relevant event/window ingredients.
3. Keep final Gan scoring untouched.
4. Use the candidate structure later as input to a bounded model verifier or ReAct-style temporal tool probe.

## Research Caveats

This report concerns the synthetic Gan validation split, not published Gan real-letter benchmark reproduction. The primary gold remains `seizure_frequency_number[0]`; `reference[0]` remains a secondary cross-check and difficulty signal. Evidence quote support is diagnostic unless explicitly used by an optimizer objective. No scorer semantics should change as part of this pivot.

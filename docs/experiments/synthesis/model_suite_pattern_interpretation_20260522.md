# Model Suite Pattern Interpretation

Date: 2026-05-22; refreshed 2026-05-23 after Qwen3.6:27b completion
Status: Complete frozen-suite synthesis
Comparison group: `model_suite_frozen_architecture_v1`
Decision scope: `arm` - model-comparison evidence only; no mechanism closure or operational promotion

## Research Question

The frozen model suite does not produce a simple leaderboard: different models win on different extraction surfaces. The useful question is therefore not "which model is best?", but:

> What do the cross-model patterns reveal about the bottlenecks in each extraction surface, and how should those bottlenecks guide future model choice and pipeline design?

## Motivation

The project currently compares models on three frozen surfaces:

| Surface | Dataset / split | Program | Scorer | GPT 4.1-mini anchor |
| --- | --- | --- | --- | ---: |
| ExECT S1 | `exectv2_fixed_v1:validation` (40) | `exect_s0_s1_field_family_single_pass` + v4_10 policy | `exect_field_family_deterministic_v1` | 92.3% micro |
| ExECT S4 | `exectv2_fixed_v1:validation` (40) | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | `exect_s4_field_family_deterministic_v1` | 65.5% micro |
| Gan S0 F0 | `gan_2026_fixed_v1:validation` (299) | `g2_candidates_adjudicate` + `cand_prose_expanded_builders_v1` | `gan_frequency_deterministic_v1` | 68.1% monthly |

The surfaces intentionally vary task shape: S1 is narrow and policy-sensitive, S4 is broader and family-mixed, and Gan F0 is temporal seizure-frequency adjudication from structured candidates. This makes the suite useful for building model profiles rather than choosing a universal champion.

## Results

### Frozen suite summary

| Model | ExECT S1 micro | ExECT S4 micro | Gan F0 monthly | Main read |
| --- | ---: | ---: | ---: | --- |
| GPT 4.1-mini | **92.3%** | 65.5% | 68.1% | Search and reproducibility anchor; strongest S1 alignment. |
| Gemini 3.1 Flash-Lite | 90.3% | 66.8% | 72.6% | Most balanced Gemini track across ExECT; strong Gan; fast. |
| Gemini 3 Flash | 89.9% | 63.2% | **75.3%** | Best Gan F0 monthly; weaker S4 pooled micro. |
| Claude Sonnet 4.6 | 81.8% | 65.1% | 73.0% | Weak S1 seizure-type profile; S4 near anchor; Gan strong but slower and less schema-stable. |
| GPT 5.5 | 85.7% | **68.7%** | 74.9% | Best hosted S4; near-top Gan; S1 below anchor because of seizure-type gap. |
| Qwen 3.6:35b | 79.0% | 67.5% | 64.4% | Local contrast: S4 competitive, S1 and Gan F0 below hosted leaders. |
| Qwen 3.5:9b | 79.4% | 64.0% | 65.9% | Local latency-floor track; Gan faster than 35b but schema validity lower. |
| Qwen 3.6:27b | 85.7% | **69.3%** | 74.9% | Strongest local track; best S4 pooled micro and near-top Gan, but very slow under partial CPU offload. |

### Family-level signals that explain the pooled scores

| Surface | Observed pattern | Interpretation |
| --- | --- | --- |
| ExECT S1 | GPT 5.5 and Claude preserve diagnosis/medication reasonably but lose heavily on `seizure_type`; Gemini 3.1 remains close to GPT. | S1 rewards benchmark label-policy alignment, especially seizure-type policy, more than general extraction strength. |
| ExECT S4 | Qwen 27b leads pooled micro at 69.3%; GPT 5.5 gains in `seizure_frequency`, `epilepsy_cause`, and `annotated_medication`; Claude gains medication but loses diagnosis/seizure; Gemini 3 Flash has a precision-heavy FP profile. | S4 pooled micro hides divergent family tradeoffs. Per-family reporting is essential. |
| Gan F0 | All hosted tracks beat GPT 4.1-mini monthly; Gemini 3 Flash and GPT 5.5 are near-tied at the top, with perfect schema/evidence. | The F0 architecture converts the task into candidate adjudication, where newer hosted models appear stronger. |

## Interpretation

### 1. The suite is exposing bottlenecks, not ranking raw intelligence

The result pattern is best explained as an interaction among:

- model behavior;
- task surface;
- schema breadth;
- deterministic scaffolding;
- benchmark scoring policy.

No model dominates because the three surfaces ask the LLM to do different kinds of work. ExECT S1 asks for tight policy obedience on a small set of benchmark-facing families. ExECT S4 asks for broad, mixed-family extraction with sparse labels and uneven precision/recall tradeoffs. Gan F0 asks the model to adjudicate temporal seizure-frequency candidates rather than perform unconstrained extraction.

This supports the project's larger hybrid-pipeline thesis: model choice matters, but only after the pipeline has exposed the right bottleneck to the model.

### 2. ExECT S1 is a policy-alignment test

ExECT S1 looks simple because it has only three field families, but the project history shows that S1 performance is not explained by raw model extraction alone. The high GPT 4.1-mini anchor depends on v4_10 benchmark label policy and inline bridges. Prior ladder work showed that schema alone is not enough; the large jump comes from benchmark-facing policy plus bridge behavior.

The model-suite pattern fits that story:

- GPT 4.1-mini remains best at 92.3%.
- Gemini 3.1 Flash-Lite is close at 90.3%, suggesting good compatibility with the S1 policy surface.
- Gemini 3 Flash is also close at 89.9%.
- GPT 5.5 falls to 85.7%, mainly from `seizure_type`.
- Claude falls to 81.8%, with a larger `seizure_type` deficit.

The important conclusion is not that GPT 5.5 or Claude are generally weaker. It is that the S1 prompt/policy/bridge surface is tuned to a failure profile where GPT 4.1-mini and Gemini 3.1 behave better. A stronger general model can still be worse if it chooses a different seizure-type interpretation than the benchmark scorer expects.

### 3. ExECT S4 is a family-profile test, not a pooled leaderboard

S4 contains 11 field families, including sparse and difficult families. Pooled micro F1 compresses several distinct behaviors:

- Qwen 3.6:27b leads at 69.3%, with strong recall and a high but still mixed family profile.
- GPT 5.5 leads hosted tracks at 68.7%, with gains in `seizure_frequency`, `epilepsy_cause`, and `annotated_medication`.
- Qwen 3.6:35b and Gemini 3.1 Flash-Lite are competitive at 67.5% and 66.8%.
- Claude is near the GPT 4.1-mini anchor at 65.1%, but with a different profile: better medication, weaker diagnosis and seizure type.
- Gemini 3 Flash drops to 63.2%, with the inspection noting a precision-driven false-positive profile.

This suggests that S4 is not measuring one uniform capability. It mixes family-specific extraction skills, abstention behavior, and benchmark alignment. A model can improve the pooled score by doing better on hard sparse families while still getting worse on clinically central dense families such as seizure type.

For paper-facing reporting, S4 should be discussed as a profile table, not as a single ranking.

### 4. Gan F0 rewards temporal adjudication over policy mimicry

Gan F0 is structurally different. The expanded-builders F0 path gives the model prose candidate structure and asks it to adjudicate seizure frequency under the deterministic Gan scorer. Here, all hosted models beat the GPT 4.1-mini anchor:

- Gemini 3 Flash: 75.3% monthly
- GPT 5.5: 74.9% monthly
- Claude Sonnet 4.6: 73.0% monthly
- Gemini 3.1 Flash-Lite: 72.6% monthly
- GPT 4.1-mini: 68.1% monthly

This looks like a task where newer hosted models benefit from the scaffold. They do not need to discover all temporal structure from scratch; they need to reason over candidate windows and choose the benchmark-facing monthly label. Gemini 3 Flash and GPT 5.5 are especially strong in that setting.

The Gan result should not be read as "Gemini/GPT 5.5 are better extraction models overall." It is more specific: they are strong adjudicators once temporal candidate structure has been placed before the LLM.

### 5. Gemini 3 Flash vs Gemini 3.1 Flash-Lite is the clearest within-provider clue

The Gemini pair is especially useful because provider family is partly controlled:

| Model | S1 | S4 | Gan F0 |
| --- | ---: | ---: | ---: |
| Gemini 3.1 Flash-Lite | 90.3% | 66.8% | 72.6% |
| Gemini 3 Flash | 89.9% | 63.2% | 75.3% |

Gemini 3.1 Flash-Lite is more stable on ExECT, especially S4. Gemini 3 Flash is stronger on Gan F0. This argues against provider-level explanations such as "Gemini is good at this project" or "Gemini is bad at benchmark policy." The model ID itself changes the precision/recall and temporal-adjudication profile.

### 6. Claude is not simply weak; it is mismatched to S1

Claude's headline looks poor because S1 is low at 81.8%. But S4 is near the GPT anchor and Gan F0 is strong at 73.0%. The inspection shows the S1 deficit is concentrated in seizure type, while diagnosis and medication are closer to parity.

The better read is that Claude's extraction style is mismatched to the narrow S1 seizure-type benchmark policy. On broader S4 and temporal Gan adjudication, it remains viable, though its Gan F0 run had 98.0% schema validity, 99.3% evidence support, and materially higher latency than Gemini/GPT tracks. That makes it a model-profile hold, not an operational favorite.

### 7. GPT 5.5 is strong where S4/Gan require broader reasoning, but not where S1 demands local policy alignment

GPT 5.5 is the clearest case where "newer model" does not mean universal improvement:

- S1: 85.7%, below GPT 4.1-mini by 6.6pp.
- S4: 68.7%, above GPT 4.1-mini by 3.2pp.
- Gan F0: 74.9%, above GPT 4.1-mini by 6.8pp and near Gemini 3 Flash.

This suggests GPT 5.5 may be better at broader cross-family extraction and temporal adjudication, but less aligned with the frozen S1 policy/bridge path. Its S1 seizure-type gap should be treated as a prompt-policy mismatch hypothesis before any broad conclusion about model quality.

## What This Teaches

The model suite supports four practical lessons.

1. Model choice should follow bottleneck diagnosis. Use GPT 4.1-mini or Gemini 3.1 Flash-Lite as stronger S1 policy-alignment tracks; consider GPT 5.5 for S4 profiling; consider Gemini 3 Flash or GPT 5.5 for Gan F0.

2. Frozen architecture matters. Gan F0 hosted gains appear after temporal candidate structure is placed before the model. Older direct/verify-repair Gan rows are not comparable without architecture caveats.

3. Pooled micro is not enough for ExECT S4. S4 must be reported with per-family F1, evidence support, and precision/recall caveats, because models trade off diagnosis, seizure type, medication, cause, frequency, and temporality differently.

4. The suite should produce model profiles, not an operational winner. GPT 4.1-mini remains the search/reproducibility anchor unless a separate promotion decision changes that. Hosted wins are useful evidence, but their decision scope is `arm`, not `operational`.

## Model Profiles

### GPT 4.1-mini

Best current search/reproducibility anchor. Strongest S1 policy alignment and stable operational baseline. Its weakness is Gan F0, where all hosted suite models beat the 68.1% monthly anchor under the same F0 architecture.

### Gemini 3.1 Flash-Lite

Most balanced Gemini track. Close to GPT on S1, above GPT on S4, and strong on Gan F0 with excellent latency and evidence support. Good candidate for paper-facing comparison as a low-latency hosted alternative, but still model-comparison only.

### Gemini 3 Flash

Best Gan F0 monthly result in the suite. However, it underperforms Gemini 3.1 Flash-Lite and GPT 5.5 on S4, with a precision-heavy false-positive profile. Best described as a strong temporal-adjudication model, not a uniformly better Gemini successor.

### Claude Sonnet 4.6

Weak S1 due to seizure-type behavior, near-anchor S4 with different family tradeoffs, and strong Gan F0. Higher latency and Gan schema invalidity make it less attractive operationally, but its S4/Gan performance prevents a simple "Claude failed" interpretation.

### GPT 5.5

Strongest hosted S4 result and nearly tied with Gemini 3 Flash on Gan F0. S1 underperformance is concentrated in seizure type. Best current hypothesis: GPT 5.5 is strong on broad extraction and temporal adjudication, but needs S1-specific policy tuning before it can compete with the GPT 4.1-mini anchor.

### Qwen 3.6:35b

Useful local contrast. S4 is competitive, S1 lags substantially, and Gan F0 is below hosted tracks. This suggests local-model scaling is not enough by itself; model-side policy alignment and runtime-specific prompt behavior remain major factors.

### Qwen 3.5:9b

Useful local latency-floor track. It roughly matches 35b on S1, trails the stronger S4 rows, and improves slightly over 35b on Gan F0 while running faster. Its Gan schema validity is lower than 27b/35b, so it is a comparison point rather than a promotion candidate.

### Qwen 3.6:27b

Strongest local model-suite track. It reaches 85.7% on S1, leads S4 pooled micro at 69.3%, and reaches 74.9% Gan F0 monthly with 100% schema/evidence. The caveat is throughput: ExECT runs took roughly 578-743 seconds per record with 71%/29% CPU/GPU residency, so the result is methodologically valuable but operationally expensive.

## Limitations

- These are validation-suite diagnostics, not published benchmark reproduction.
- ExECT results depend on deterministic scorer semantics and benchmark-facing label policy.
- Gan results depend on the fixed synthetic validation set and the F0 expanded-builders architecture.
- S4 pooled micro can mislead if read without family breakdown.
- The model suite varies only `model_track`; it does not identify whether prompt rewrites could close a model-specific gap.
- Local Qwen results are confounded by Ollama residency, context settings, and quantized runtime behavior; 27b outperforming 35b should not be read as a pure parameter-scaling claim.
- Hosted latency, billing, schema validity, and evidence support differ across tracks and should be included in any operational decision.
- `decision_scope: arm` means no model should be operationally promoted from this report alone.

## Next Steps

1. Use this completed table as the model-profile source for paper-facing claims; do not promote operational defaults from the suite alone.
2. Decide explicitly whether the paper needs an S2/S3 extension. If not, freeze the suite at S1/S4/Gan F0 and move effort back to Gan builder-gap validation.
3. For GPT 5.5 and Qwen 27b, inspect S1 `seizure_type` failures against GPT 4.1-mini if a model-specific prompt adaptation workstream is opened.
4. For S4, report per-family F1 alongside pooled micro because the top rows win through different family tradeoffs.
5. Keep GPT 4.1-mini as the search and reproducibility anchor until a separate promotion review considers cost, latency, schema validity, evidence support, and cross-surface behavior.

## Artifact References

| Artifact | Role |
| --- | --- |
| `docs/planning/kanban_plan.md` | Active coverage matrix, operational defaults, and "what we know now" tables. |
| `docs/experiments/synthesis/model_suite_frozen_architecture_v1_preregistration_20260522.md` | Frozen-suite research question, controls, comparison surfaces, and interpretation rules. |
| `docs/experiments/exect/exect_gemini_ladder_replay_v1_inspection_20260521.md` | Gemini 3.1 Flash-Lite ExECT S1/S4 results and interpretation. |
| `docs/experiments/gan/gan_s0_expanded_builders_prose_gemini_full_validation_v1_inspection_20260521.md` | Gemini 3.1 Flash-Lite Gan F0 results. |
| `docs/experiments/synthesis/model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md` | Gemini 3 Flash S1/S4/Gan results and family-level read. |
| `docs/experiments/synthesis/model_suite_claude_sonnet_4_6_full_validation_v1_inspection_20260522.md` | Claude Sonnet 4.6 S1/S4/Gan results and latency/schema caveats. |
| `docs/experiments/synthesis/model_suite_gpt5_5_full_validation_v1_inspection_20260522.md` | GPT 5.5 S1/S4/Gan results and billing/latency details. |
| `docs/experiments/synthesis/model_suite_qwen9b_full_validation_v1_inspection_20260522.md` | Qwen 3.5:9b S1/S4/Gan local latency-floor results. |
| `docs/experiments/synthesis/model_suite_qwen27b_full_validation_v1_inspection_20260523.md` | Qwen 3.6:27b S1/S4/Gan completion report and local latency caveats. |
| `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md` | Doctrine separating model-comparison arms from mechanism closure and operational promotion. |
| `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md` | Background synthesis on deterministic placement and task-specific bottlenecks. |

# Gan S0 GEPA vs Synthesis Baseline Comparison and Decision

Date: 2026-05-19

## Purpose

Compare the hosted-path Gan S0 GEPA capped runs against the current synthesis-backed BootstrapFewShot baseline on prompt length, label metrics, evidence support, and runtime. Use the comparison to decide whether to scale GEPA on GPT 4.1-mini or pivot to a verifier/repair architecture.

## Taxonomy

- **Dataset:** gan_2026
- **Schema complexity:** gan_s0
- **Clinical task family:** frequency
- **Hybrid balance class:** L1_llm_constrained
- **Interleaving positions:** during, eval_only
- **Varied factor:** optimizer_strategy
- **Comparison group:** gan_s0_architecture_gpt_validation_v1
- **Outcome:** reject

## Baseline: Synthesis-Backed BootstrapFewShot

Artifact: `runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z`  
Config: `configs/experiments/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini.json`  
Program variant: `gan_frequency_s0_single_pass` (ChainOfThought)  
Optimizer: `BootstrapFewShot` with `synthesis_exact_with_evidence` metric  
Prompt version: `gan_frequency_s0_synthesis_v1`

Full-validation metrics on 299 records:

| Metric | Value |
|---|---:|
| Schema-valid prediction rate | 97.3% |
| Normalized-label accuracy | 51.5% |
| Monthly-frequency accuracy | 62.9% |
| Purist category accuracy | 70.1% |
| Pragmatic category accuracy | 73.9% |
| Evidence quote support rate | 89.9% |

Post-repair replay (`runs/gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_surface_replay_20260518T000000Z`) improved schema validity to 98.3% and normalized-label to 52.0% via deterministic surface repair of quoted special labels and matching-count denominator ranges. Remaining failures are semantic, not surface-repairable.

## Comparison: GEPA Rich-Feedback Run

Artifact: `runs/gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T054057Z`  
Config: `configs/experiments/gan_s0_gepa_direct_cap5_gpt4_1_mini.json`  
Program variant: `gan_frequency_s0_direct_single_pass`  
Optimizer: `GEPA` with `synthesis_exact_with_evidence_feedback` metric  
Prompt version: `gan_frequency_s0_synthesis_v1_gepa_harness`

Capped metrics on 5 records:

| Metric | Synthesis baseline (full, 299) | GEPA rich-feedback (cap5) |
|---|---:|---:|
| Schema-valid prediction rate | 97.3% | **100.0%** |
| Normalized-label accuracy | 51.5% | 40.0% |
| Monthly-frequency accuracy | 62.9% | 60.0% |
| Pragmatic category accuracy | 73.9% | 60.0% |
| Evidence quote support rate | 89.9% | **80.0%** |

Runtime:
- Compile: 20.05s
- Prediction: 8.26s (1.65s/record)
- Estimated model calls: 9

### Prompt Bloat

The selected GEPA instruction in `artifacts/compiled_state.json` is **3,249 characters / 508 words**. This is substantially longer than the synthesis signature instructions (~800 characters / ~120 words) and longer than the full `GAN_FREQUENCY_SYNTHESIS_GUIDANCE` constant (~600 characters). On a 5-record cap with only 4 training examples, the instruction already covers:

- Full label vocabulary enumeration
- Unit rules
- Normalization rules (daily, every N, or ranges, clusters, year-to-date, quarters)
- Seizure-free threshold (6 months)
- Evidence requirements

The earlier harness run (`runs/gan_s0_gepa_direct_cap5_gpt4_1_mini_20260519T052124Z`) had a shorter instruction but worse metrics. The richer-feedback run traded prompt length for schema validity and evidence support.

### Qwen GEPA Probe Corroboration

Local Qwen3.6:35b GEPA probes (`runs/gan_s0_gepa_direct_cap5_qwen35b_ollama_20260519T055049Z` and `runs/gan_s0_gepa_direct_cap5_qwen35b_ollama_20260519T060700Z`) confirmed the same pattern:

- Larger reflection/output budget (`max_tokens=10000`) improved some five-record metrics
- Compile time expanded from 267.81s to **535.80s**
- Selected instruction ballooned from 3,936 chars / 664 words to **10,562 chars / 1,819 words**
- Still introduced a non-canonical label (`several per week`)

This confirms prompt bloat is a real GEPA behavior, not an artifact of the small cap.

## Qwen Direct-Path Evidence Finding

The post-guardrail Qwen3.6:35b direct cap-25 run (`runs/gan_s0_qwen35b_direct_cap25_guardrails_validation_20260519T071524Z`) reached **100.0% evidence quote support on valid predictions**, with zero evidence-support errors. All four invalid predictions were semantic failures outside deterministic repair:

- Incomplete cluster (`4 cluster per 3 month` missing per-cluster count)
- Quoted numeric label (`"6 per 2 month"`)
- Forbidden units (`4 per hour`, `6 per hour`)

This demonstrates that evidence support is now a solved problem for the direct path. The remaining gap is **semantic label validity**, not evidence grounding.

## Decision

**Do not scale GEPA on GPT 4.1-mini as the next Gan S0 optimization path.**

Rationale:
1. **Prompt bloat**: GEPA instructions grow quickly and exceed the compact benchmark-contract guidance that the synthesis baseline demonstrated as effective.
2. **Label metric regression**: On the available comparison, GEPA underperforms the synthesis baseline on normalized-label, monthly-frequency, and pragmatic accuracy.
3. **Evidence is solved**: The Qwen direct path already reaches 100% evidence support on valid predictions. GEPA's evidence improvement is marginal relative to the baseline.
4. **Semantic failures remain**: The failures that matter (clusters, temporal windows, seizure-free thresholds, unknown/no-reference confusion) are exactly the semantic failures that deterministic postprocessing should not handle silently.
5. **Qwen transfer is poor**: Local GEPA is slow, bloated, and introduces drift. It should remain an explicitly scheduled stress test only.

## Recommended Next Implementation

Pivot to an **explicit Gan S0 extract-verify-repair program variant** with the following properties:

- **First pass**: Direct extraction (unchanged current behavior)
- **Second pass**: A narrow DSPy verifier module that receives the note text, initial prediction, and initial evidence
- **Verifier decisions**: `confirm`, `repair`, or `abstain`
- **Verifier targets**: cluster completeness, temporal-window/denominator correctness, seizure-free threshold validity, unknown vs no-reference discrimination, and evidence quote support
- **Auditability**: Every verifier decision is tagged with `verifier_decision`, `verifier_reason`, and `repair_type` in the prediction metadata
- **Metrics**: Report extraction-only metrics alongside verify-repair metrics, plus repair rate and abstention rate

This satisfies the kanban requirement that semantic repair be an explicit named variant rather than hidden deterministic postprocessing.

## Optional Follow-Up

A Qwen3.6:35b direct full-validation rerun with the post-guardrail bridge remains useful for quantifying invalid-label and evidence deltas against `runs/gan_s0_overnight_qwen35b_direct_full_validation_20260518T223713Z`, but it is not a blocker for starting the verifier/repair module.

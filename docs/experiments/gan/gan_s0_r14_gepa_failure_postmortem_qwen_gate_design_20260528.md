# Gan S0 R14 GEPA Failure Postmortem And Qwen Gate Design

Date: 2026-05-28
Status: Complete; no new model run launched
Decision scope: arm-level postmortem plus conditional optimizer-gate design
Primary board: `docs/planning/kanban_plan.md`

## Research Question

Did the completed Gan S0 GEPA arms fail because GEPA is the wrong mechanism, because the
objective/artifact contract was poorly matched to Gan's benchmark semantics, or because the
project has not yet tested a sufficiently compact optimizer target? Is a Qwen3.6:35b GEPA gate
justified now?

## Source Artifacts

- Workstream: `docs/workstreams/optimizer/gan_s0_multistage_gepa_workstream_20260524.md`
- GPT G0-G2 inspection: `docs/experiments/gan/gan_s0_multistage_gepa_gpt_cap25_v1_inspection_20260524.md`
- Direct GEPA decision: `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md`
- Optimizer synthesis: `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`
- Latency policy: `docs/policies/qwen_dspy_latency_policy.md`
- Gan audit: `docs/datasets/gan/gan_2026_label_audit.md`

Key run artifacts inspected:

| Arm | Run ID | Artifact focus |
| --- | --- | --- |
| G1 | `gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini_20260524T131719Z` | `metrics.json`, `artifacts/compiled_state.json`, `artifacts/optimizer/summary.json` |
| G2 | `gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini_20260524T131744Z` | `metrics.json`, `artifacts/compiled_state.json`, `artifacts/optimizer/summary.json` |

## Fixed Controls

| Control | Value |
| --- | --- |
| Dataset | Gan 2026 synthetic validation |
| Split | `gan_2026_fixed_v1:validation`, cap-25 |
| Schema level | `gan_frequency_s0` |
| Model/provider | GPT 4.1-mini for G0-G2 |
| Scorer mode | `gan_frequency_deterministic_v1` |
| Gold label | `seizure_frequency_number[0]`; `reference` diagnostic only |
| Optimizer metric | `gan_s0_stage_attributed_frequency_feedback`, optimizer-facing only |
| Candidate surface | `gan_s0_candidate_builder_gap_v1` held fixed for multistage GEPA |

## Results Recap

| Arm | Monthly | Purist | Pragmatic | Normalized label | Schema | Evidence | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| G0 cap control | 76.0% | 84.0% | 96.0% | 64.0% | 100.0% | 100.0% | hold as matched control |
| G1 GEPA adjudicator | 60.0% | 80.0% | 88.0% | 48.0% | 100.0% | 100.0% | reject arm |
| G2 GEPA verify-repair | 48.0% | 68.0% | 76.0% | 40.0% | 100.0% | 100.0% | reject arm |

The failed arms did not fail by malformed JSON or missing evidence. They failed by worse
benchmark-facing semantic label selection: denominator/window mistakes, quantified labels
collapsed to unknown, unknown/cluster confusions, and category flips.

## Failure Modes

### 1. GEPA Recreated Long Manual Policy Instead Of A Compact Delta

The selected compiled instructions were too large to qualify as a compact optimizer result:

| Arm | Predictor | Selected instruction size |
| --- | --- | ---: |
| G1 | `adjudicate` | 4,829 chars / 766 words |
| G2 | `extractor.extract` | 4,742 chars / 768 words |
| G2 | `verifier.verify` | 1,286 chars / 182 words |

This repeats the historical direct-GEPA pattern from 2026-05-19, where GPT selected a
3,249-character instruction and Qwen expanded as far as 10,562 characters / 1,819 words under a
larger completion budget. GEPA is finding policy walls, not short transferable corrections.

### 2. The Objective Rewarded Contract Cleanliness More Reliably Than Label Semantics

G1/G2 preserved 100.0% schema validity and 100.0% quote support. That is useful, but those
properties were already strong in the candidate-builder control. The optimizer-facing feedback
did not sufficiently penalize the residual errors that matter most for Gan S0: current temporal
window choice, denominator preservation, cluster spacing versus count-per-cluster, and
unknown/no-reference discrimination.

### 3. Stage Attribution Did Not Prevent Wrong-Stage Policy Inflation

The G1/G2 metric emitted stage tags, but the selected instructions still expanded into broad
global guidance. G2 was especially revealing: adding a verifier did not localize the improvement.
It increased severe residuals from 6 monthly mismatches in G0 to 13 in G2 while consuming more
runtime and tokens.

### 4. Qwen GEPA Is Not The Right Immediate Stress Test

The project's Qwen latency policy already warns that Qwen3.6:35b should avoid optimizer-expanded
prompts unless the run is an explicit overnight optimizer experiment. The historical Qwen direct
GEPA probes were slow, bloated, and produced non-canonical labels. The newer GPT G1/G2 evidence
does not create a positive transfer candidate; it creates another reason to avoid Qwen GEPA until
a compact hosted-model candidate exists.

## Interpretation

The result rejects the completed G1/G2 configurations as arms. It does not close GEPA as a
mechanism class. The mechanism remains open only under a narrower hypothesis:

> GEPA may be useful if it is constrained to discover a short, stage-local instruction delta over
> a stripped prompt and if the optimizer feedback directly targets benchmark-contract semantic
> failures rather than rewarding already-solved schema/evidence behavior.

That hypothesis has not yet produced a promotable artifact in this repo.

## Qwen Gate Decision

A compact Qwen GEPA gate is **not justified now**.

Do not run Qwen3.6:35b GEPA until all of the following are true:

1. A hosted GPT compact-delta gate is preregistered and passes on a cap slice.
2. The selected instruction delta is capped at <= 1,200 characters per optimized predictor, or the
   report explicitly justifies a larger budget with a benchmark-facing lift.
3. The GPT arm beats its matched cap control on monthly accuracy by >= 4 percentage points or
   removes a predeclared severe residual slice without category regression.
4. The optimizer metric separately reports semantic labels, schema validity, evidence support,
   instruction length, and estimated prediction prompt tokens.
5. The Qwen gate is run as a one-record smoke followed by a very small cap only, with no overlap
   with other Ollama jobs.

If these conditions are met, the smallest Qwen gate should be a **portability probe**, not an
optimizer search:

| Arm | Purpose |
| --- | --- |
| Q0 | Current non-compiled Qwen candidate-builder/adjudicator control on the same cap slice |
| Q1 | Distilled compact GPT-derived instruction delta inserted manually, no GEPA compile |
| Q2 | Optional Qwen GEPA compile only if Q1 improves and latency remains acceptable |

Q2 should stay blocked unless Q1 first shows that Qwen benefits from the compact instruction
content without paying compile-time search cost.

## Next Experiments

1. Prioritize R11/R12/R13 implementation follow-up over optimizer work: temporal/date stages,
   entity-first staging, and self-consistency map more directly to the residual Gan failure modes.
2. If optimizer work reopens, preregister a GPT compact-delta gate over a stripped prompt or
   verifier-only target. The varied factor should be compact instruction mutation, not broad
   policy restatement.
3. Keep G1/G2 as arm rejects in the experiment registry/workstream memory. Do not describe GEPA
   or DSPy optimizers as mechanism-rejected.

## Validation

No model run was launched for R14. Validation was artifact inspection only:

- `metrics.json` for G1/G2 benchmark-facing and diagnostic metrics
- `compiled_state.json` for selected instruction sizes and predictor targets
- `optimizer/summary.json` for budget settings and GEPA contract
- prior Gan audit and Qwen latency policy for scorer/gold and local-model constraints

The scorer semantics remain unchanged.

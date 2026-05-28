# Gan S0 Targeted Example Families Plan

Date: 2026-05-22  
Status: Design complete; not yet model-tested  
Related card: G4  

## Taxonomy

Dataset: Gan 2026 synthetic validation  
Schema complexity: Gan S0 seizure frequency  
Research axis: 3  
stage_graph_id: `g2_candidates_adjudicate`  
varied_factor: `example_strategy`  
decision_scope: arm  

## Purpose

The policy-density mini-grid suggests that compact rules alone do not stabilize hard temporal and cluster cases. The next example-backed run should test whether small, targeted demonstrations can move the exact ambiguity families seen in GPT/Qwen residuals without broad prompt bloat.

This plan records example families before model spend. Examples should be hand-authored synthetic snippets or drawn only from non-evaluation/training material with leakage checked; do not use the 25-record enriched validation slice as few-shot demonstrations.

## Fixed Controls For First Test

- Model/provider: GPT 4.1-mini
- Program: `gan_frequency_s0_temporal_candidates_single_pass`
- Prompt control: v1.4 full policy, no examples
- Candidate source: deterministic temporal candidates
- Scorer: `gan_frequency_deterministic_v1`
- Split: validation slice first for regression gating; broader validation only if a slice arm is clearly useful
- Evidence: exact quote support remains diagnostic, not the benchmark-facing objective

## Example Families

| Family | Failure mode targeted | Demo should teach | Acceptance signal |
| --- | --- | --- | --- |
| Grouped recent events | Multiple dated/recent events are treated as separate or unknown | Sum/group events under a shared observation window when the note supports one denominator | Fewer quantified-to-unknown misses; no rise in unsupported evidence |
| Counted events plus short stability | Later "stable", "well since", or "no further events" cancels counted events | Keep counted-window label unless seizure-free/no-event duration is at least 6 months | Rescue `gan_13190`-like cases without converting true seizure-free cases to rates |
| Highest current frequency | Model chooses severe or recent type rather than most frequent current epileptic events | Pick highest note-supported current frequency across concurrent seizure types | Fewer frequent/infrequent category flips |
| Year-to-date denominator | YTD counts are expanded to full year or collapsed to per-month | Use months elapsed since January through note date | Monthly accuracy improves on YTD-like records without changing non-YTD annual rates |
| Trigger-conditioned unknown | Trigger-linked events without calendar denominator are over-quantified | Output `unknown` when the note lacks event frequency across calendar time | True unknown precision improves; no broad quantified-to-unknown regression |
| Cluster ambiguity | Cluster spacing/per-cluster count is omitted, invented, or collapsed | Preserve full cluster syntax; use `unknown, N per cluster` when spacing is missing | Fewer cluster pragmatic regressions and no malformed cluster labels |
| No-reference boundary | Administrative or no clinical seizure-frequency content drifts to `unknown` | Use `no seizure frequency reference` only when frequency content is absent | No-reference precision preserved on abstention cases |

## First Example Pack Shape

Use a small fixed pack, not retrieval yet:

- One short positive demo per family above.
- One contrastive demo for `unknown` vs `no seizure frequency reference`.
- Keep each note snippet short enough that examples do not dominate the full note.
- Include the canonical label and an exact evidence quote for each demo.
- Avoid examples that encode full validation-record wording.

Suggested initial arm IDs:

| arm_id | Description |
| --- | --- |
| `targeted_examples_min7_v1` | Seven family demos, one per family, added to v1.4 adjudication prompt |
| `targeted_examples_temporal4_v1` | Only grouped events, short stability, highest current frequency, YTD |
| `targeted_examples_abstention3_v1` | Trigger-conditioned unknown, cluster ambiguity, no-reference boundary |

Run order should start with `targeted_examples_min7_v1` only if token cost is acceptable; otherwise run the two smaller packs against the v1.4 no-example control.

## Gates

Slice promotion signal:

- Pragmatic accuracy at least matches v1.4 control: 56.0%.
- Monthly accuracy improves over v1.4 control: 36.0%, or holds within one record while reducing a named failure family.
- Schema validity remains 100.0%.
- Evidence quote support remains 100.0%.
- No new broad quantified-to-unknown regression cluster.

## Caveats

This is an example-strategy arm, not a mechanism claim about few-shot prompting generally. A failed pack rejects only that example selection and placement. If the pack succeeds, it should still be tested on a broader validation slice before any Qwen transfer.

# Gan S0 G14 Temporal Anchoring Report

Date: 2026-05-29
Status: current synthesis / no-model temporal anchoring evaluation
Kanban card: G14 - Gan Temporal Anchoring Evaluation and Optimization
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Standard surface: `gan_s0_g6_standard50_v1`
Temporal challenge set: `gan_s0_g6_temporal_anchoring`
Candidate source: `current deterministic temporal candidate substrate`
Fixed controls: no model calls; no scorer, loader, split, bridge, prompt, candidate-builder, target-selection, or prediction-repair changes.

## Summary

Standard50: exact candidate coverage is **41/50** (82.0%); temporal-slot coverage is **36/40** (90.0%) on temporally applicable rows; gate-clean slot coverage is **31/35** (88.6%).
Temporal challenge: exact candidate coverage is **13/15** (86.7%); temporal-slot coverage is **13/15** (86.7%) on temporally applicable rows; gate-clean slot coverage is **13/15** (86.7%).

Gate-caveated view: rows where G13 already misclassified the source-level content state are carried as upstream caveats, not pure temporal-anchoring failures.

## Failure Classes

| Surface | Failure class | Records |
| --- | --- | ---: |
| `standard50` | `exact_temporal_candidate_present` | 41 |
| `standard50` | `temporal_slot_miss` | 4 |
| `standard50` | `upstream_g13_gate_caveat` | 5 |
| `temporal_challenge` | `exact_temporal_candidate_present` | 13 |
| `temporal_challenge` | `temporal_slot_miss` | 2 |

## Temporal Challenge Rows

| Record | Gold | Exact candidate | Slot match | Gate caveat | Failure class | Candidate labels |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `gan_14485` | `2 per 3 month` | yes | yes | no | `exact_temporal_candidate_present` | `2 per 3 month`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for 1 month` |
| `gan_13123` | `1 per year` | yes | yes | no | `exact_temporal_candidate_present` | `1 per year`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`2 per day` |
| `gan_4702` | `multiple per day` | yes | yes | no | `exact_temporal_candidate_present` | `seizure free for multiple month`<br>`multiple per day` |
| `gan_2609` | `1 per day` | yes | yes | no | `exact_temporal_candidate_present` | `seizure free for multiple month`<br>`2 per day`<br>`1 per day`<br>`1 per month`<br>`1 per day`<br>`4 per month`<br>`1 per day` |
| `gan_1794` | `8 per 2 month` | yes | yes | no | `exact_temporal_candidate_present` | `8 per 2 month` |
| `gan_12679` | `1 per day` | yes | yes | no | `exact_temporal_candidate_present` | `1 per day`<br>`seizure free for 6 month`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`1 to 2 per month`<br>`1 per 3 to 4 week`<br>`1 per day`<br>`1 to 2 per 6 month` |
| `gan_1584` | `11 per month` | yes | yes | no | `exact_temporal_candidate_present` | `seizure free for multiple month`<br>`11 per month` |
| `gan_17287` | `1 per 1 to 2 day` | yes | yes | no | `exact_temporal_candidate_present` | `1 per 1 to 2 day`<br>`1 per day`<br>`1 per 9 month`<br>`0.111 per month` |
| `gan_16772` | `9 per 5 month` | no | no | no | `temporal_slot_miss` | `seizure free for multiple month`<br>`8 per 2 month`<br>`11 per 3 month`<br>`11 per 10 month`<br>`11 per month`<br>`unknown, 1 per cluster` |
| `gan_16825` | `10 per 6 month` | no | no | no | `temporal_slot_miss` | `12 per 2 month`<br>`12 per 3 month`<br>`8 per 3 month`<br>`8 per 10 month`<br>`8 per month`<br>`unknown, 3 per cluster` |
| `gan_12950` | `7 per 3 month` | yes | yes | no | `exact_temporal_candidate_present` | `7 per 3 month`<br>`1 per 2 to 3 week`<br>`7 per 3 month`<br>`7 per year` |
| `gan_714` | `2 per day` | yes | yes | no | `exact_temporal_candidate_present` | `2 per day` |
| `gan_12465` | `1 per day` | yes | yes | no | `exact_temporal_candidate_present` | `2 per year`<br>`1 per day` |
| `gan_804` | `1 per month` | yes | yes | no | `exact_temporal_candidate_present` | `seizure free for multiple month`<br>`1 per month`<br>`1 per month`<br>`1 per month`<br>`2 per month`<br>`unknown, 2 per cluster` |
| `gan_22` | `3 per day` | yes | yes | no | `exact_temporal_candidate_present` | `seizure free for multiple month`<br>`3 per day`<br>`3 per day` |

## Decision

- Classification: **diagnostic_temporal_component_measured**.
- Mechanism status: **open**.
- Temporal challenge exact coverage is 13/15; slot coverage is 13/15 on temporally applicable rows.
- Optimization decision: Do not expand fragile arithmetic or broad relative-anchor guards from this pass. Preserve the current candidate builder as support, and route the remaining exact misses to aggregation-aware answer construction plus LLM target selection.

## Interpretation

- The temporal challenge surface is mostly covered by the current deterministic substrate, but two exact misses remain as true temporal-slot misses; both still have category-equivalent candidates rather than clean exact answer options.
- This supports G12's conclusion that exact closed answer-option construction needs temporal anchoring plus aggregation policy; it does not justify another broad prompt loop or a fragile arithmetic expansion.
- G13 gate errors remain visible in row-level JSON so G15 target-selection work does not blame source-level content confusions on temporal anchoring.

## Companion Artifact

`docs/experiments/gan/gan_s0_g14_temporal_anchoring_report_20260529.json` contains standard50 rows, temporal challenge rows, candidate records, slot diagnostics, G13 caveats, and failure classes.

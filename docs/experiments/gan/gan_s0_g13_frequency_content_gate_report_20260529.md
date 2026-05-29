# Gan S0 G13 Frequency-Content Gate Report

Date: 2026-05-29
Status: current synthesis / no-model isolated gate evaluation
Kanban card: G13 - Gan Isolated Frequency-Content Gate Evaluation and Refinement
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Gate source: `current deterministic temporal candidate substrate`
Gold source: `check__Seizure Frequency Number.seizure_frequency_number[0]`
Fixed controls: no model calls; no scorer, loader, split, bridge, prompt, target-selection, or prediction-repair changes.

## Summary

Overall gate accuracy is **244/299** (81.6%).

## Per-Class Metrics

| Gate class | Support | Predicted | Precision | Recall | F1 | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `no_reference` | 11 | 10 | 100.0% | 90.9% | 95.2% | 0 | 1 |
| `unknown_unclear_frequency` | 40 | 11 | 90.9% | 25.0% | 39.2% | 1 | 30 |
| `seizure_free` | 45 | 35 | 65.7% | 51.1% | 57.5% | 12 | 22 |
| `quantified_frequency_presence` | 203 | 243 | 82.7% | 99.0% | 90.1% | 42 | 2 |

## Confusion Matrix

| Gold \ predicted | no_reference | unknown_unclear_frequency | seizure_free | quantified_frequency_presence |
| --- | ---: | ---: | ---: | ---: |
| `no_reference` | 10 | 1 | 0 | 0 |
| `unknown_unclear_frequency` | 0 | 10 | 10 | 20 |
| `seizure_free` | 0 | 0 | 23 | 22 |
| `quantified_frequency_presence` | 0 | 0 | 2 | 201 |

## Error Routing

- `no_reference -> unknown_unclear_frequency`: 1
- `quantified_frequency_presence -> seizure_free`: 2
- `seizure_free -> quantified_frequency_presence`: 22
- `unknown_unclear_frequency -> quantified_frequency_presence`: 20
- `unknown_unclear_frequency -> seizure_free`: 10

## Gate Policy

- `unknown` and `no seizure frequency reference` remain distinct under the canonical project policy.
- `unknown, N per cluster` is counted with unclear-frequency labels for this gate because cluster spacing is unknown, while row-level JSON keeps the per-cluster burden visible.
- Quantified-rate and explicit cluster-spacing candidates are counted as frequency-presence signals; final target selection remains out of scope.
- Seizure-free labels are separated because later selector work needs to know whether the gate itself can identify remission evidence before adjudicating it against current quantified events.

## Decision

- The isolated deterministic gate is strong enough to use as a diagnostic baseline, but errors should be routed by class before G14/G15 so temporal anchoring and target selection are not blamed for source-level gate mistakes.
- The row-level JSON lists false positives and false negatives for no-reference, unclear-frequency, and quantified-frequency-presence classes for follow-up inspection.

## Companion Artifact

`docs/experiments/gan/gan_s0_g13_frequency_content_gate_report_20260529.json` contains row-level candidate labels, candidate records, confusion counts, and false-positive/false-negative lists.

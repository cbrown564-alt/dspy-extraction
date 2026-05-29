# Gan S0 G21 Aggregation Constructor Report

Date: 2026-05-29
Status: current synthesis / fixture-tested no-model constructor
Kanban card: G21 - Gan Deterministic Aggregation Constructor Fixture Implementation
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
Primitive ID: `gan.frequency.aggregation_constructor.v1`
Model calls: none
Scorer, loader, split, bridge, prompt, model, candidate-builder, target-selection, and prediction-repair semantics: unchanged.

## Summary

Standard50: raw exact **41/50**, constructed exact **4/50**, combined exact **45/50**.
G11 exact-miss challenge: raw exact **0/21**, constructed exact **12/21**, combined exact **12/21**.
Negative/deferred control constructions: **0** on G11 and **0** on Standard50.

## Decision

- Standard50 gate passed: **yes**.
- G11 gate passed: **yes**.
- Classification: **deterministic_quantified_rate_constructor_gate_passed**.
- Next authorization: A later selector card may compare closed-option target selection with a row-level before/after ledger; this report itself is not selector performance.

## G11 Fixture Rows

| Record | Gold | Policy class | Raw exact | Constructed exact | Constructed labels |
| --- | --- | --- | ---: | ---: | --- |
| `gan_15997` | `10 per 3 month` | `aggregation_required_temporal_slot_missing` | no | yes | `10 per 3 month` |
| `gan_16772` | `9 per 5 month` | `aggregation_required_temporal_slot_missing` | no | yes | `9 per 5 month` |
| `gan_16825` | `10 per 6 month` | `aggregation_required_temporal_slot_missing` | no | yes | `10 per 6 month`<br>`5 per 3 month` |
| `gan_16335` | `7 per 3 month` | `aggregation_required_temporal_slot_missing` | no | yes | `7 per 3 month` |
| `gan_10583` | `unknown, 2 to 3 per cluster` | `outside_rate_duration_aggregation_policy` | no | no | `none` |
| `gan_1463` | `3 per month` | `aggregation_required_temporal_slot_missing` | no | yes | `3 per month` |
| `gan_9424` | `10 per 9 month` | `aggregation_required_temporal_slot_missing` | no | yes | `10 per 9 month` |
| `gan_6094` | `3 per month` | `aggregation_required_temporal_slot_missing` | no | no | `none` |
| `gan_1486` | `3 per month` | `candidate_inventory_gap_before_aggregation` | no | no | `none` |
| `gan_7431` | `1 per month` | `aggregation_required_temporal_slot_missing` | no | yes | `1 per month` |
| `gan_16883` | `4 per 3 month` | `aggregation_required_temporal_slot_missing` | no | yes | `4 per 3 month` |
| `gan_4996` | `seizure free for 16 month` | `duration_aggregation_policy_required` | no | no | `none` |
| `gan_3355` | `1 per 3 month` | `aggregation_required_temporal_slot_missing` | no | yes | `2 per 6 month`<br>`1 per 3 month` |
| `gan_15129` | `4 per 15 month` | `candidate_inventory_gap_before_aggregation` | no | no | `none` |
| `gan_9063` | `seizure free for 8 month` | `duration_aggregation_policy_required` | no | no | `none` |
| `gan_13290` | `4 per 6 month` | `aggregation_required_temporal_slot_missing` | no | no | `none` |
| `gan_6509` | `1 per week` | `aggregation_required_temporal_slot_missing` | no | yes | `1 per week` |
| `gan_4378` | `3 per 2 month` | `aggregation_required_temporal_slot_missing` | no | yes | `3 per 2 month` |
| `gan_6296` | `3 per 4 month` | `candidate_inventory_gap_before_aggregation` | no | no | `none` |
| `gan_13019` | `9 per 3 month` | `candidate_inventory_gap_before_aggregation` | no | no | `none` |
| `gan_9526` | `4 per 8 month` | `aggregation_required_temporal_slot_missing` | no | yes | `4 per 8 month`<br>`1 per 2 month` |

## Interpretation

- G21 creates a separate constructed answer-option surface; raw temporal candidates are preserved unchanged.
- Coverage gains are answer-option coverage only, not selector, Purist, Pragmatic, canonical monthly, or paper-reproduction performance.
- Duration rows, inventory gaps, special labels, unknown clusters, and final target selection remain outside this constructor.

## Companion Artifact

`docs/experiments/gan/gan_s0_g21_aggregation_constructor_report_20260529.json` contains row-level constructor diagnostics, raw candidate snapshots, constructed options, and fixed-control metadata.

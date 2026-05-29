# Gan S0 G16 Rate/Duration Aggregation Policy

Date: 2026-05-29
Status: current synthesis / no-model aggregation policy
Kanban card: G16 - Gan Rate/Duration Aggregation Policy
Dataset/split: Gan 2026 synthetic (`gan_2026_fixed_v1:validation`)
G11 challenge set: `gan_s0_g6_candidate_coverage_exact_miss`
Standard surface: `gan_s0_g6_standard50_v1`
Model calls: none
Scorer, loader, split, bridge, prompt, model, candidate-builder, target-selection, and prediction-repair semantics: unchanged.

## Summary

G11 exact-miss challenge: **21** rows; **16** rows are blocked on aggregation or duration policy before exact closed-answer options.
Standard50: **50** rows; **4** rows are blocked on aggregation or duration policy before exact closed-answer options.

## Policy

- `closed_option_already_available`: The current candidate surface already contains the exact gold label; aggregation is not the bottleneck for that row.
- `aggregation_required_temporal_slot_missing`: A quantified-frequency row has category-equivalent candidates but lacks the exact event/window slot; an exact claim requires an explicit aggregation constructor or preregistered model mechanism.
- `aggregation_constructor_required`: The row is category-equivalent but exact-incomplete; aggregation may be needed, but the existing temporal slot is not the primary recorded miss.
- `duration_aggregation_policy_required`: The row is seizure-free duration rather than quantified rate; do not fold it into rate aggregation without a duration-specific rule.
- `upstream_gate_caveat_before_aggregation`: G13 already misclassified the content state, so aggregation should not be blamed as the first failure stage.
- `outside_rate_duration_aggregation_policy`: The row is an unknown/no-reference/unknown-cluster special case and routes to G17 or cluster policy, not G16 rate/duration aggregation.
- `candidate_inventory_gap_before_aggregation`: No exact or category-equivalent candidate support exists; inventory or temporal anchoring must improve before aggregation can be evaluated.

## Policy Class Counts

| Surface | Policy class | Records |
| --- | --- | ---: |
| `g11_exact_miss_challenge` | `aggregation_required_temporal_slot_missing` | 14 |
| `g11_exact_miss_challenge` | `candidate_inventory_gap_before_aggregation` | 4 |
| `g11_exact_miss_challenge` | `duration_aggregation_policy_required` | 2 |
| `g11_exact_miss_challenge` | `outside_rate_duration_aggregation_policy` | 1 |
| `standard50` | `aggregation_required_temporal_slot_missing` | 4 |
| `standard50` | `closed_option_already_available` | 41 |
| `standard50` | `outside_rate_duration_aggregation_policy` | 5 |

## G11 Policy Rows

| Record | Gold | Policy class | Exact | Slot | Purist/Pragmatic | Candidate labels |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `gan_15997` | `10 per 3 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `seizure free for multiple month`<br>`3 per week`<br>`4 per month`<br>`3 per month`<br>`unknown, multiple per cluster` |
| `gan_16772` | `9 per 5 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `seizure free for multiple month`<br>`8 per 2 month`<br>`11 per 3 month`<br>`11 per 10 month`<br>`11 per month`<br>`unknown, 1 per cluster` |
| `gan_16825` | `10 per 6 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `12 per 2 month`<br>`12 per 3 month`<br>`8 per 3 month`<br>`8 per 10 month`<br>`8 per month`<br>`unknown, 3 per cluster` |
| `gan_16335` | `7 per 3 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `1 per month`<br>`4 per 3 month` |
| `gan_10583` | `unknown, 2 to 3 per cluster` | `outside_rate_duration_aggregation_policy` | no | n/a | yes/yes | `no seizure frequency reference`<br>`unknown` |
| `gan_1463` | `3 per month` | `aggregation_required_temporal_slot_missing` | no | no | no/yes | `seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for 6 month`<br>`seizure free for multiple month`<br>`4 per month`<br>`1 per month` |
| `gan_9424` | `10 per 9 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `5 per 3 month` |
| `gan_6094` | `3 per month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `seizure free for multiple month`<br>`2 per month`<br>`1 per month` |
| `gan_1486` | `3 per month` | `candidate_inventory_gap_before_aggregation` | no | no | no/no | `1 per month` |
| `gan_7431` | `1 per month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `2 per 8 week`<br>`0.25 per week` |
| `gan_16883` | `4 per 3 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `seizure free for multiple month`<br>`3 per 2 month`<br>`3 per 3 month`<br>`5 per 3 month` |
| `gan_4996` | `seizure free for 16 month` | `duration_aggregation_policy_required` | no | no | yes/yes | `seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for multiple month`<br>`seizure free for multiple month` |
| `gan_3355` | `1 per 3 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `seizure free for multiple month`<br>`seizure free for multiple month`<br>`5 per day`<br>`3 per 6 month`<br>`0.5 per month`<br>`2 per 2 month`<br>`2 per 4 month`<br>`2 per 5 month` |
| `gan_15129` | `4 per 15 month` | `candidate_inventory_gap_before_aggregation` | no | no | no/no | `seizure free for multiple month`<br>`2 per day` |
| `gan_9063` | `seizure free for 8 month` | `duration_aggregation_policy_required` | no | no | yes/yes | `seizure free for multiple month`<br>`2017 per 8 month` |
| `gan_13290` | `4 per 6 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `2 per 6 month`<br>`0.333 per month` |
| `gan_6509` | `1 per week` | `aggregation_required_temporal_slot_missing` | no | no | no/yes | `seizure free for multiple month`<br>`2 per day`<br>`1 per day`<br>`1 per 2 week`<br>`0.5 per week` |
| `gan_4378` | `3 per 2 month` | `aggregation_required_temporal_slot_missing` | no | no | no/yes | `seizure free for multiple month`<br>`2 per day` |
| `gan_6296` | `3 per 4 month` | `candidate_inventory_gap_before_aggregation` | no | no | no/no | `seizure free for multiple month` |
| `gan_13019` | `9 per 3 month` | `candidate_inventory_gap_before_aggregation` | no | no | no/no | `seizure free for multiple month` |
| `gan_9526` | `4 per 8 month` | `aggregation_required_temporal_slot_missing` | no | no | yes/yes | `seizure free for multiple month`<br>`seizure free for multiple month`<br>`5 per 4 month`<br>`5 per 6 month` |

## Decision

- Classification: **aggregation_policy_defined_exact_constructor_blocked**.
- Next selector authorization: **blocked_until_constructor_or_preregistered_model_mechanism**.
- Constructor decision: Do not mutate the current candidate builder from this policy pass. A follow-up constructor must be independently fixture-tested and reported before an exact closed-answer-option claim.
- Reporting rule: Until that constructor exists, report exact-label and monthly-frequency selector results as unsupported diagnostics when exact candidates are absent; category-equivalent coverage may be reported separately.

## Interpretation

- Rate aggregation is policy-ready only as a named mechanism: sum explicitly supported events over an explicitly supported observation window, preserve the source candidates and evidence, and report exact labels separately from category-equivalent diagnostics.
- Seizure-free duration aggregation is not the same as rate aggregation; it needs a duration-specific policy before being mixed with quantified-frequency answer construction.
- Unknown and no-reference rows remain outside this G16 rate/duration policy and route to G17.
- G16 does not promote another exact-label selector. It defines the boundary a deterministic constructor or preregistered model mechanism must satisfy before exact closed answer options can be claimed.

## Companion Artifact

`docs/experiments/gan/gan_s0_g16_aggregation_policy_20260529.json` contains policy classes for the G11 exact-miss challenge and G14 standard50 surface.

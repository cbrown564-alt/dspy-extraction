# Gan S0 Canonical-Format Residual-Slice Replay — Inspection

Date: 2026-05-21  
Parent: `docs/experiments/gan/gan_s0_canonical_format_port_gpt_cap25_v1_inspection_20260521.md`  
Comparison group: `gan_s0_canonical_format_residual_slice_gpt_v1`  
Fixture: `data/fixtures/gan_s0_exact_frequency_residual_slice.json` (30 records from VR full-validation monthly misses)

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | 3 — implementation variant (canonical-format port confirmation) |
| Comparison group | `gan_s0_canonical_format_residual_slice_gpt_v1` |
| Primary varied factor | `implementation_variant` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation`, scorer `gan_frequency_deterministic_v1`, adjudicate-only skeleton (no VR), prose presentation, deterministic temporal candidates.

Reference queue: monthly misses from `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` (VR operational default), exported in `docs/experiments/gan/gan_s0_exact_frequency_residual_slice_error_read_20260521.md`.

## Arms

| arm_id | implementation_variant | run_id | norm exact (30) | monthly (30) | pragmatic (30) |
| --- | --- | --- | ---: | ---: | ---: |
| C0 | `canonical_format_control_v1_1` | `gan_s0_canonical_c0_residual_slice_gpt4_1_mini_20260521T070103Z` | 10.0% (3/30) | 13.3% (4/30) | 46.7% |
| C1 | `canonical_format_v3_examples_v1` | `gan_s0_canonical_c1_residual_slice_gpt4_1_mini_20260521T070140Z` | 10.0% (3/30) | 13.3% (4/30) | 43.3% |

Cap-25 port (prefix) for contrast: C0 40% / 52% monthly; C1 44% / 56% monthly (`docs/experiments/gan/gan_s0_canonical_format_port_gpt_cap25_v1_inspection_20260521.md`).

## C1 vs C0 paired deltas (30-record queue)

| Metric | Recoveries | Regressions | Net |
| --- | ---: | ---: | ---: |
| Normalized exact | 1 | 1 | 0 |
| Monthly frequency | 1 | 1 | 0 |
| Pragmatic overcall (C1 worse, C0 correct) | — | 1 | — |

Replay artifact: `artifacts/gan_canonical_format_residual_replay_20260521/summary.json`  
Script: `scripts/replay_gan_canonical_format_residual_slice.py`

## Per-group recovery (normalized exact)

| Residual group | n | C0 exact | C1 exact | C1 recoveries | C1 regressions |
| --- | ---: | ---: | ---: | ---: | ---: |
| `arithmetic_window_precision` | 10 | 0 | 0 | 0 | 0 |
| `unknown_vs_quantified` | 8 | 2 | 1 | 0 | 1 |
| `cluster_composition` | 8 | 0 | 1 | 1 | 0 |
| `infrequent_long_denominator_or_boundary` | 4 | 1 | 1 | 0 | 0 |

Wins are **not** concentrated in the exact-label residual groups targeted by the manual read (`arithmetic_window_precision`, `unknown_vs_quantified`). The single recovery is `gan_10993` (cluster spacing: `1 cluster per 2 week` → gold `2 cluster per month`). The single regression is `gan_13993` (C0 `unknown` correct → C1 invents `2 to 3 per 2 month`).

## Notable records

| record_id | C0 | C1 | Outcome |
| --- | --- | --- | --- |
| `gan_10993` | `1 cluster per 2 week, 2 to 4 per cluster` | `2 cluster per month, 2 to 4 per cluster` | **recovery** (exact + monthly) |
| `gan_13993` | `unknown` | `2 to 3 per 2 month` | **regression** (pragmatic overcall) |
| `gan_12562`–`gan_16964` (10 arithmetic) | All monthly miss | Same wrong seizure-type/window pattern as VR | No C1 movement |
| `gan_10031`–`gan_15240` (5 cluster abstains) | `unknown` | `unknown` | No movement |

## Gates (prereg residual plan)

| Check | Result | Gate |
| --- | --- | --- |
| Residual wins concentrate in target groups | **fail** — 0/10 arithmetic, 0/8 unknown recoveries | Promotion requires concentrated exact-label recovery |
| Net paired recovery > regressions on exact | **null** (1 vs 1) | Need clear net win on hard queue |
| Pragmatic overcall on residuals | 1 regression (`gan_13993`) | Caveat — do not promote if overcall on hard unknowns |

**Outcome: hold inconclusive (arm) on residual queue; do not promote to cap-50 or full validation from residual evidence alone.**

Cap-25 +4pp normalized exact is **not confirmed** on the fixed 30-record monthly-miss queue. Treat cap-25 port hold as **prefix/search evidence only** until a broader confirmatory run is explicitly preregistered.

## Mechanism review

Not applicable — residual replay does not add a second implementation variant; mechanism class “canonical format examples” stays **open**.

## Open cells

- Cap-50 confirm **deferred** (residual gate not met)
- Full validation promotion **deferred**
- VR skeleton interaction (adjudicate-only vs VR) still untested for C1
- Table presentation × canonical examples interaction untested

## Recommendation

1. **Do not** run cap-50 canonical-format confirmation until a new prereg defines a confirmatory slice (e.g. full validation prefix or stratified sample), not only VR-hard misses.
2. Keep C1 as **arm hold** from cap-25; downgrade promotion readiness based on residual null.
3. Next Gan S0 work should target **mechanism classes** visible on the residual queue (seizure-type selection, calendar aggregation, unknown denominator) via new primitives or stage executors — not additional prompt-example sweeps alone.

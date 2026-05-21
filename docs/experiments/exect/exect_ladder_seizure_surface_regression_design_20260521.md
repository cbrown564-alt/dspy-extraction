# ExECT Ladder Seizure Surface Regression — Design

Date: 2026-05-21  
Status: Design ready for cap-25 / residual-slice evaluation  
Parent: `exect_s1_s3_residual_targeted_actions_20260521.md` (P1)  
Related: `exect_s1_seizure_modifier_negative_guard_design_20260521.md` (S1-only N0/N1)  
Prior reject: S1 seizure H2 pre-vocab; S1 static pre-vocab on cap-25 executor grid (E3–E5)

## Question

How do we **prevent inherited S1 seizure families from degrading** when S2/S3/S4 prompts widen — without rerunning static pre-vocabulary or broad prompt churn?

## Problem statement (cross-level)

| Level | seizure_type F1 | Δ vs S1 | Dominant tag |
| --- | ---: | --- | --- |
| S1 | 90.5% | — | uncertainty-leakage, scorer-surface |
| S2 | 71.0% | −19.5pp | scorer-surface (modernized labels) |
| S3 | 78.1% | −12.4pp | recovered from v1.1 collapse; leakage persists |
| S4 | ~acceptable | — | regression guard per S4 residual read |

The S1→S2 drop is **not** a scorer regression (bridges unchanged). It is **prompt/schema drift**: five- and nine-family passes emit modernized terms (`focal seizures with altered awareness` ×5) and generic `secondary`.

## Action split (two mechanisms)

| Mechanism | Scope | Doc |
| --- | --- | --- |
| Negative guard (drop bad labels) | S1 primary; optional S2+ | `exect_s1_seizure_modifier_negative_guard_design_20260521.md` |
| Positive bridge (map surfaces) | S1–S4 | This doc — reuse `exect_seizure_type_benchmark_bridge` |

**Do not** add new H2 pre-vocab candidate lists.

## Proposed `implementation_variant` arms (wider schemas)

| Tier | ID | Action | When |
| --- | --- | --- | --- |
| **R0** | `sz_regression_bridge_only_v1` | Ensure post-bridge calls `exect_seizure_type_benchmark_bridge` on every seizure label in S2/S3 artifact paths (parity with S1) | Baseline audit |
| **R1** | `sz_regression_coarsen_modernized_v1` | Extend `_GRANULAR_SEIZURE_TYPE_COARSENING` with cap-25 frequent FPs: `focal seizures with altered awareness` → audited gold surfaces where policy allows | S2 cap-25 |
| **R2** | `sz_regression_priority_prompt_v1` | Prompt policy block: “preserve S1 seizure surfaces; do not emit standalone secondary” | New prompt variant ID only |
| **R3** | `sz_guard_drop_standalone_secondary_v1` | Port S1 N0 to S2/S3 recovery | Coupled with N0 slice pass |

**Order:** Audit R0 → R3 on S1 residual slice → R1 cap-25 on S2 → R2 only if bridges insufficient.

## Regression gates (mandatory for any S2/S3/S4 prereg)

| Family | Floor vs frozen baseline |
| --- | --- |
| seizure_type | No ≥3pp F1 drop vs same-level prior full run |
| investigation | No ≥2pp drop |
| diagnosis | No ≥2pp drop |

Embed in every `exect_s3_*` and `exect_s4_*` comparison group template.

## Qualitative queue (shared)

EA0150, EA0016, EA0090, EA0072, EA0143, EA0137 — tag `scorer-surface` vs `uncertainty-leakage` before choosing R1 vs R3.

## Open cells

- Whether R1 coarsening belongs in bridge primitive or S2-specific recovery
- Staged architecture (S5 family-split) — separate Axis 1 question; not this design
- Qwen seizure gap — `exect_qwen_s1_seizure_gap_error_analysis` track

## Next steps

1. Code audit: confirm S2 `_recover_s2_seizure_raw_values` applies same bridge stack as S1.
2. Run S1 N0 residual slice (see seizure modifier design).
3. Cap-25 S2: L1 vs R0+R3 vs R0+R1.
4. Document outcome in inspection; do not mechanism-close “wider prompt safe” without S3 confirmation.

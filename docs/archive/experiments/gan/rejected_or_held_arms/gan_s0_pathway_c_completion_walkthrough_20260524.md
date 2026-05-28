# Gan S0 Pathway C Completion Walkthrough

Date: 2026-05-24  
Pathway: C — Gan Frequency Residuals  
Status: **Complete**  
decision_scope: pathway closure (no scorer or gold change)

## Pathway Outcome

Pathway C aimed for a prioritized residual map and at most one tightly scoped next arm with a preregistered hypothesis. That outcome is met:

| Card | Status | Artifact |
| --- | --- | --- |
| C1. Residual taxonomy | Completed | [gan_s0_residual_taxonomy_consolidation_20260524.md](gan_s0_residual_taxonomy_consolidation_20260524.md) |
| C2. Unknown-overuse arm | Rejected | [gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_rejection_20260524.md](gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_rejection_20260524.md) |
| C3. Pragmatic monthly divergence | Completed | [gan_s0_pragmatic_monthly_divergence_analysis_20260524.md](gan_s0_pragmatic_monthly_divergence_analysis_20260524.md) |
| C4. Compact optimizer hypothesis | Closed (no hypothesis) | [gan_s0_multistage_gepa_gpt_cap25_v1_inspection_20260524.md](gan_s0_multistage_gepa_gpt_cap25_v1_inspection_20260524.md) |

## Operational Default (Unchanged)

| Field | Value |
| --- | --- |
| Program | `gan_s0_candidate_builder_gap_v1` |
| Model | GPT 4.1-mini |
| Split | `gan_2026_fixed_v1:validation` (299 records) |
| Scorer | `gan_frequency_deterministic_v1` |
| Gold | `seizure_frequency_number[0]` |
| Full-validation monthly accuracy | **80.6%** |
| Pragmatic category accuracy | **88.6%** |
| Run ID | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` |

No arm from Pathway C clears the cap-25 gate (≥84% monthly) or improves full-validation monthly accuracy. The operational default stands.

## Consolidated Residual Map

After C1–C3, benchmark-severe misses on the operational default cluster as follows:

| Residual class | Approx. count (GPT full-val) | Pathway C action | Status |
| --- | ---: | --- | --- |
| `other_semantic_mismatch` | 17 | C2 targeted subset | C2 rejected; builder gap remains root cause for no-candidate records |
| `pragmatic_match_monthly_divergence` | 16 | C3 analysis | Partially fixable; documented for paper attribution |
| `frequent_undercalled` | 7 | Not in C2 scope | Deferred |
| `purist_bin_boundary_within_pragmatic` | 7 | C3: accept as scorer boundary | Document only |
| `unknown_as_quantified_rate` | 3 | C2 Rule 1 | C2 over-corrected opposite direction |
| `cluster_collapsed_to_rate` | 2 | Not tested | Deferred |
| `unknown_as_high_rate` | 2 | C2 partial target | C2 rejected |
| `unknown_vs_seizure_free` | 2 | C2 target | C2 rejected |
| Other singleton classes | ≤2 each | — | Low priority |

## C2 Arm Summary (Rejected)

| Field | Value |
| --- | --- |
| Arm | `gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini` |
| Run ID | `gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_20260524T201746Z` |
| Gate | cap-25 monthly ≥ 84% |
| Result | **16.0%** monthly (−64.6pp vs baseline on enriched slice) |
| decision_scope | **arm** |

**Root causes (not resolved):**

1. **RC1 — Rule 1 over-fires:** Quantified-window preservation hallucinates specific rates where `unknown` is correct.
2. **RC2 — No-candidate records:** Rule 4 is inert when the deterministic builder produces no candidates (7/25 enriched-slice failures).

## C3 Key Decisions

1. **Pragmatic monthly divergence is partially fixable** via count-underestimation repair and multi-type highest-frequency examples; window-selection mismatch is moderate fixability.
2. **Range-to-point and vague-multiple cases are scorer-surface artifacts** — do not alter gold or scorer semantics.
3. **Paper reporting:** Monthly accuracy is primary; pragmatic category (88.6%) is supporting with documented attribution for the 16-record divergence class.

## C4 Closure

GEPA G1/G2 were already rejected on cap-25 (60.0% and 48.0% monthly vs 76.0% G0 control). No compact-instruction or submodule-freezing hypothesis was formulated for a C4 preregistration. Pathway C closes C4 as **not needed** until a new optimizer design exists.

G3/G4 remain globally blocked per kanban guardrails (prompt-length gate, new prereg required).

## Rejected Arms (Pathway C)

| Arm | Varied factor | Run ID | Reason | decision_scope |
| --- | --- | --- | --- | --- |
| Unknown-overuse guard v1.5 | prompt_policy | `gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_20260524T201746Z` | 16.0% monthly; Rule 1 over-extraction + no-candidate inertness | arm |
| GEPA G1 adjudicator | optimizer | `gan_s0_multistage_gepa_g1_adjudicator_cap25_gpt4_1_mini_20260524T131719Z` | −16.0pp monthly vs G0; long instructions | arm |
| GEPA G2 verify-repair | optimizer | `gan_s0_multistage_gepa_g2_verify_repair_cap25_gpt4_1_mini_20260524T131744Z` | −28.0pp monthly vs G0 | arm |

## Deferred Follow-Ons (Outside Pathway C)

These are documented recommendations, not Pathway C cards. Each requires a new preregistration and cap-25 gate:

1. **Builder extension for `other_semantic_mismatch` no-candidate records** — highest upside; addresses RC2 for C2 and general pipeline.
2. **Multi-type highest-frequency prompt arm** — targets `frequent_undercalled` (~7 records) and multi-type pragmatic divergence.
3. **Window-priority policy arm** — targets window-selection mismatch (~3–5 records).
4. **Softened C2b unknown-overuse retry** — only after RC1 fix (explicit calendar-window phrasing or hedging clause).

Do not retry C2 prompt variants or run broad optimizer arms without resolving RC1/RC2 or a new compact GEPA design.

## Paper-Facing Claims Supported

- Gan S0 operational default: 80.6% monthly, 88.6% pragmatic on synthetic validation (not Gan Real reproduction).
- Residual errors are categorized; unknown-overuse prompt guard and multi-stage GEPA are **rejected arms**, not mechanism closure.
- Monthly–pragmatic gap (8.0pp) is attributable primarily to pragmatic-monthly-divergence sub-patterns documented in C3.

## Validation Performed

- C1 taxonomy consolidation from builder-gap audit, Qwen forensics, and GEPA inspection
- C2 cap-25 model run with preregistered gate
- C3 full-validation error analysis (no model calls)
- C4 closure from existing GEPA G0–G2 cap-25 inspection
- Scorer semantics and gold labels unchanged throughout

## Files Referenced

- `docs/experiments/gan/gan_s0_residual_taxonomy_consolidation_20260524.md`
- `docs/experiments/gan/gan_s0_unknown_overuse_arm_preregistration_20260524.md`
- `docs/experiments/gan/gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini_rejection_20260524.md`
- `docs/experiments/gan/gan_s0_pragmatic_monthly_divergence_analysis_20260524.md`
- `docs/experiments/gan/gan_s0_multistage_gepa_gpt_cap25_v1_inspection_20260524.md`
- `docs/planning/kanban_plan.md`

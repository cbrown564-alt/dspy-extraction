# Pathway D — Paper Evidence Freeze Completion Walkthrough

Date: 2026-05-24  
Pathway: D — Paper Evidence Freeze  
Status: **Complete**  
decision_scope: pathway closure (documentation only; no scorer, loader, or model-output changes)

## Pathway Outcome

Pathway D froze manuscript-ready evidence from primary run artifacts: operational defaults (D1), rejected arms (D2), and a results narrative (D3). No new model budget was spent.

| Card | Status | Artifact |
| --- | --- | --- |
| D1. Operational-default table | **Done** (pre-existing) | [paper_frozen_operational_defaults_20260524.md](paper_frozen_operational_defaults_20260524.md) |
| D2. Negative/arm-reject table | **Done** | [paper_frozen_arm_reject_table_20260524.md](paper_frozen_arm_reject_table_20260524.md) |
| D3. Results narrative | **Done** | [paper_frozen_results_narrative_20260524.md](paper_frozen_results_narrative_20260524.md) |
| D4. Test/benchmark protocol | Backlog | Unchanged; activate only if holdout reporting is explicitly needed |

## D2 Summary

Compiled **25 rejected arms** across four tiers after the C-track per-family parallel ceiling row was added:

| Tier | Scope | Row count |
| --- | --- | --- |
| 1 | 2026-05-24 Pathway A/C closures + S5 v2 combined reject + C-track per-family ceiling | 7 |
| 2 | ExECT S5 frequency/medication arms | 4 |
| 3 | Gan S0 mechanism search | 6 |
| 4 | ExECT S1/S4 historical probes | 8 |

Every row includes `comparison_group`, `varied_factor`, reject reason, primary run ID or inspection doc, and `decision_scope: arm`. Holds and workspace-best outcomes are documented separately to avoid conflating reject with promote.

## D3 Summary

Drafted manuscript-facing narrative inheriting D1 metrics:

- **Gan:** 80.6% monthly operational default; Qwen transfer at 70.7%; negative C2/GEPA arms.
- **ExECT ladder:** S1 92.3% → S4 65.5% breadth-pressure story; Qwen surface-dependent transfer.
- **ExECT S5:** Paper-frozen **85.8% micro / 73.9% freq** (v2b verifier stack, promoted 2026-05-24); superseded v1 at 85.5% / 72.3%; combined v2 rejected (D2 Tier 1).
- **Cross-dataset:** Task-dependent hybrid placement thesis with claim-readiness matrix.

Companion table pack ([paper_result_table_pack_20260524.md](paper_result_table_pack_20260524.md)) remains the compact numeric source; D3 is the prose layer.

## Validation Performed

- Tier 1 ExECT metrics verified against local `runs/*/metrics.json` (A4 cap-25, high-precision cap-25, freq verifier full validation).
- D1 headline numbers cross-checked with paper_result_table_pack verification notes.
- Gan C2 and GEPA rows traced to cap-25 inspection docs and run IDs from Pathway C walkthrough.
- No scorer semantics, gold labels, or registry edits.

## Paper-Facing Claims Now Supported

1. Operational defaults cite primary artifacts with split/scorer/run ID (D1).
2. Negative results are tabled with explicit `decision_scope: arm` (D2).
3. Results prose distinguishes supported, workspace-best, and blocked claims (D3).
4. Model budget gate satisfied: tables cite existing runs only.

## Post-Pathway Update (2026-05-24)

ExECT S5 verifier + A3 stack promoted to D1 after human review. See [exect_s5_frequency_verifier_full_validation_promotion_review_20260524.md](../exect/exect_s5_frequency_verifier_full_validation_promotion_review_20260524.md).

## Deferred (Outside Pathway D)

| Item | Condition |
| --- | --- |
| D4 test/holdout protocol | Explicit manuscript need |
| Published benchmark reproduction | Real Gan + CUI-aware ExECT gates |

## Files Created

- `docs/experiments/synthesis/paper_frozen_arm_reject_table_20260524.md`
- `docs/experiments/synthesis/paper_frozen_results_narrative_20260524.md`
- `docs/experiments/synthesis/pathway_d_paper_evidence_freeze_walkthrough_20260524.md`

## Files Updated

- `docs/planning/kanban_plan.md`

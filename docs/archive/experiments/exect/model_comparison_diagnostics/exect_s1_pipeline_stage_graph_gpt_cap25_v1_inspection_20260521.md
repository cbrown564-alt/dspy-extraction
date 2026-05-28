# ExECT S1 Pipeline Stage-Graph GPT Cap-25 v1 Inspection

Date: 2026-05-21  
Scope: cap-25 (25 records), GPT 4.1-mini, Axis 1 stage-graph grid  
Preregistration: `docs/experiments/exect/exect_s1_pipeline_stage_graph_gpt_cap25_v1_preregistration_20260521.md`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S1 field-family |
| Comparison group | `exect_s1_pipeline_stage_graph_gpt_cap25_v1` |
| Research axis | 1 |
| Primary varied factor | `pipeline_stage_graph` |
| decision_scope | `arm` |

## Run artifacts

| Arm | `stage_graph_id` | `bridge_mode` | Run ID |
| --- | --- | --- | --- |
| S1 | `g1_l1_policy_bridges` | inline | `exect_s1_stage_graph_g1_l1_policy_bridges_cap25_gpt4_1_mini_20260521T014619Z` |
| S2 | `g1_l1_policy_no_bridges` | none_diagnostic | `exect_s1_stage_graph_g1_l1_policy_no_bridges_cap25_gpt4_1_mini_20260521T014623Z` |
| S3 | `g2_extract_verify` | none_diagnostic | `exect_s1_stage_graph_g2_extract_verify_cap25_gpt4_1_mini_20260521T014626Z` |
| S4 | `g2_raw_post_bridge` | post_module | `exect_s1_stage_graph_g2_raw_post_bridge_cap25_gpt4_1_mini_20260521T014630Z` |
| S5 | `g3_family_split_merge` | inline | `exect_s1_stage_graph_g3_family_split_merge_cap25_gpt4_1_mini_20260521T014634Z` |

## Headline metrics

| Arm | Micro F1 | Diagnosis | Seizure | Medication | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| S1 | **95.8%** | 97.6% | **95.4%** | 94.9% | 97.3% |
| S2 | 72.8% | 71.4% | 56.3% | 93.3% | 97.5% |
| S3 | 72.8% | 71.4% | 62.5% | 85.7% | 97.4% |
| S4 | **95.8%** | 97.6% | **95.4%** | 94.9% | 97.3% |
| S5 | 83.3% | 84.2% | 76.1% | 91.5% | 88.9% |

Best micro F1: **95.8%** (S1, S4 tied).

## Bridge contribution analysis

| Comparison | Micro F1 Δ | Interpretation |
| --- | ---: | --- |
| S1 vs S2 (inline vs none) | **+23.0pp** | Inline benchmark bridges dominate S1 performance |
| S4 vs S2 (post vs none) | **+23.0pp** | Post-module bridges recover full bridge gain |
| S1 vs S4 (inline vs post) | **0.0pp** | Bridge placement null on cap-25 — identical metrics |
| S2 vs S3 (single-pass vs verify-repair, both bridge-free) | **0.0pp** | Two-stage verify null when bridges off |

S1 and S4 produce metric-identical outputs on this slice (matches prior interleaving v2 H1 vs production L1 finding). Bridge-free arms (S2, S3) cluster at 72.8% micro.

## Prediction overlap notes

- S1 and S4: expect high label overlap (same bridge outcome, different stage metadata).
- S2 and S3: tied micro F1; verify-repair shifts seizure (+6.2pp vs S2) and medication (−7.6pp) without net micro gain.
- S5: section-aware decomposition underperforms monolithic S1 by **−12.5pp** micro; evidence support drops to 88.9%.

## Outcomes

| Arm | Outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| S1 | **Hold** | arm | Production-shaped anchor; ties best micro F1 |
| S2 | **Hold (diagnostic)** | arm | Bridge-free reference — not a deployment candidate |
| S3 | **Reject (arm)** | arm | Null vs S2 bridge-free; no cap-25 gain from verify stage |
| S4 | **Hold** | arm | Ties S1 — post bridges sufficient on this slice |
| S5 | **Reject (arm)** | arm | −12.5pp vs S1; evidence regression |

## Gates applied

| Rule | Result |
| --- | --- |
| Rank by micro F1 | S1/S4 lead (95.8%); S5 third (83.3%); S2/S3 tied (72.8%) |
| Hold within 2pp of best | S1, S4 hold; S5 reject (>2pp below best) |
| Reject >2pp below best without diagnostic benefit | S3, S5 reject |

## Mechanism review

Not applicable — `decision_scope: arm` only. Do **not** mechanism-close verify-repair, family decomposition, or bridge placement from this grid.

## Recommendation for Phase 5b (`exect_s1_stage_executor_gpt_cap25_v1`)

Fix **`g1_l1_policy_bridges`** (or equivalently `g2_raw_post_bridge`) as the Axis 2 skeleton:

1. **Bridge placement:** inline vs post on matched extraction (S1 vs S4 showed null — still worth executor-grid confirmation with explicit `bridge_mode` tags).
2. **Per-family executor:** LLM vs det-assisted pre-candidates on diagnosis/seizure/medication — new shapes, not replay of rejected H2 slice configs.
3. **Do not** advance S3 verify-repair or S5 section-aware to Axis 2 without new `implementation_variant` IDs.

## Open cells

- Bridge inline vs post mechanism class (cap-25 null between S1/S4 — executor grid may add tie-break diagnostics).
- Verify-repair with bridges on (Lane A: −9.4pp vs single-pass) vs bridge-free null (S2 vs S3).
- Section-aware with v4_10 vs legacy v3 prompt (S5 uses v4_10; still loses to S1).
- Full validation deferred for all arms per prereg.
- Qwen port deferred.

## Cross-reference

| Prior artifact | Relationship |
| --- | --- |
| `exect_s1_verification_single_pass_cap25_gpt4_1_mini_20260520T232837Z` | S1 metric match (95.8%) |
| interleaving L1 raw cap-25 | S2 match (72.8% full was 68.6%; cap-25 72.8%) |
| `exect_s1_verification_verify_repair_cap25_gpt4_1_mini_20260520T232841Z` | Distinct from S3 (86.4% with bridges on) |
| interleaving H1 post-bridge cap-25 | S4 match (95.8%) |

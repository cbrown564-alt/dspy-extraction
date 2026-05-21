# ExECT S4 Frequency Surface Repair GPT Cap-25 v1 — Preregistration

Date: 2026-05-21  
Status: Complete — `docs/exect_s4_frequency_surface_repair_gpt_cap25_v1_inspection_20260521.md`  
Parent plan: `docs/hybrid_pipeline_exploration_implementation_plan_20260521.md`  
Parent synthesis: `docs/prior_best_vs_current_best_reanalysis_20260521.md`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | S4 field-family (11 families) |
| Research axis | 3 — post-bridge surface repair (`implementation_variant`) |
| Comparison group | `exect_s4_frequency_surface_repair_gpt_cap25_v1` |
| Primary varied factor | `implementation_variant` |
| `stage_graph_id` | `g1_l1_policy_bridges` (frozen S4 single-pass) |
| `bridge_mode` | inline S3 bridges unchanged; frequency bridge varies post-merge policy |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Hypothesis

A **post-extraction** frequency surface repair (`H1_post_deterministic` on `seizure_frequency` only) improves `seizure_frequency` F1 on cap-25 versus frozen v1.2 inline bridge recovery, without regressing frozen S3 families.

This differs from the rejected H2 pre-vocab arm (`exect_s4_frequency_deterministic_v1`): H2 injected candidates **before** LLM extraction and regressed −2.0pp; R1 merges note-anchored audited surfaces **after** extraction and abstains when the note supports no frequency templates.

## Motivation

S4 v1.2 full validation (`…071248Z`) holds **45.7%** seizure-frequency F1 (+19.6pp vs v1.0) but residual gaps remain:

| Pattern | Example docs | v1.2 bridge behavior |
| --- | --- | --- |
| Dual-cardinal near-miss | `1 per month` → `1 per 1 month` | Partial — inline repair only on model outputs |
| Zero-rate surfaces | `0 per 3 year` | Prompt examples only; model often misses |
| Multi-label blocks | EA0050 rate + change + infrequent | Model collapse; co-label bridge requires quantified rate in model output |
| Spurious frequency | EA0179 `seizure free` FP on no-gold doc | No note-absence guard |
| Note-supported misses | Model omits rate present in note | No post-merge fill |

Error read: `docs/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md`.

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` |
| Cap | 25 (Lane A order) |
| Model | GPT 4.1-mini |
| Scorer | `exect_s4_field_family_deterministic_v1` |
| Program architecture | `single_pass` (eleven-family) |
| Prompt | `exect_s4_field_family_v1_2_label_policy` (unchanged) |
| S3 bridges | Frozen v1.2 inline bridges for nine S3 families |
| Investigation guard | v1.2 S4-only guard retained in both arms |
| LLM calls | One pass per record |
| Pre-vocab / candidate injection | None |

## Arms

| Arm | implementation_variant | Program variant | Config |
| --- | --- | --- | --- |
| R0 | `frequency_bridge_v1_2_control` | `exect_s4_field_family_single_pass` | `exect_s4_frequency_surface_r0_control_cap25_gpt4_1_mini.json` |
| R1 | `frequency_post_merge_v1_3` | `exect_s4_field_family_frequency_post_merge_single_pass` | `exect_s4_frequency_surface_r1_post_merge_cap25_gpt4_1_mini.json` |

### R1 implementation (pre-run spec)

R1 applies `exect.frequency.benchmark_bridge.v1` with post-merge policy on `seizure_frequency` only:

1. Run v1.2 inline bridge recovery on model outputs (unchanged repair, co-label augmentation, non-audited block).
2. **Note-anchored merge:** union audited labels from note regex/Gan-filtered hints not already present (`s4_bridge:note_anchored_frequency_merged`).
3. **Spurious seizure-free guard:** drop `seizure free` / `seizure free since YEAR` when note lacks matching cues (`s4_bridge:spurious_seizure_free_removed`).

Do **not** clear all frequency predictions when note regex finds no templates.

## Primary and Secondary Metrics

| Metric | Role |
| --- | --- |
| `seizure_frequency` field-family F1 | **Primary** |
| Pooled micro F1 (11 fam) | Diagnostic — not comparable to S1–S3 |
| Frozen S3 family F1 (diagnosis, seizure_type, medication, investigation, comorbidity, birth/onset/cause/when) | Regression guard |
| Evidence quote support | Gate >= 85% |
| Bridge flags per arm | Diagnostic |

## Gates

| Decision | Rule |
| --- | --- |
| **Hold / promote to full validation** | R1 seizure_frequency F1 ≥ R0 + **3.0pp** on cap-25, and no frozen S3 family regresses **≥2pp** vs R0, and both arms pass evidence gate |
| **Hold (inconclusive)** | R1 improves frequency but delta < 3.0pp, or S3 regression < 2pp on sparse families only |
| **Reject arm** | R1 seizure_frequency F1 ≤ R0, or any frozen S3 family regresses ≥2pp, or evidence gate failure |
| **Mechanism closure** | Forbidden from this group alone |
| **Full validation (40)** | Only if hold/promote gate passes |

## Frequency-Heavy Residual Slice (optional confirm)

If cap-25 hold passes, replay the 29 frequency-mismatch document-family entries from full v1.2 (`docs/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md` § mismatch mix) on R0 vs R1 predictions. Report recovery on:

- dual-cardinal near-miss
- zero-rate omission
- multi-label collapse
- spurious frequency on note-absent docs
- qualitative co-label (where note cue exists)

Do not promote from slice alone without cap-25 gate.

## Reference Runs

| Reference | Run suffix | seizure_frequency F1 | Notes |
| --- | --- | ---: | --- |
| S4 v1.2 cap-25 (R0 repro) | `…070616Z` | **49.1%** | Primary control |
| S4 v1.2 full anchor | `…071248Z` | 45.7% | Full validation |
| H2 pre-vocab (rejected) | `…191951Z` | 47.1% | Different varied factor — not R0 |
| Qwen S4 full | `…160914Z` | 50.0% | Confirmatory port deferred |

## Inspection Requirements

- Taxonomy block with `decision_scope: arm`
- Run IDs for R0 and R1
- Primary `seizure_frequency` F1 table + frozen S3 regression table
- Bridge flag counts (`note_absent_frequency_abstained`, `note_anchored_frequency_merged`, co-label, near-miss)
- Explicit contrast with rejected H2 pre-vocab arm
- Open cells listed

## Open Cells

- Prompt-policy or example-strategy changes not tested
- Medication temporality post-classifier not retested
- Qwen port deferred until GPT cap-25 gate passes
- Mechanism class “ExECT frequency post-merge” stays open unless ≥2 implementations agree directionally
- Full ExECTv2 Table 1 reproduction not claimed

## Explicit Non-Goals

- Do not reopen S3 v1.2, S2 v1.3, or S1 v4.10 label policy
- Do not rerun H2 pre-vocab as R1 control
- Do not vary stage graph or add verify-repair second pass
- Do not mechanism-reject “post-bridge repair” from one cap-25 null

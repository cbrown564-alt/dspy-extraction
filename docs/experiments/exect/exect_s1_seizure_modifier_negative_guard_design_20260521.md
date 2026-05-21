# ExECT S1 Seizure Modifier Negative Guard — Design

Date: 2026-05-21  
Status: Design ready for residual-slice validation, then cap-25 prereg  
Parent: `exect_s1_s3_residual_targeted_actions_20260521.md` (P2)  
Residual queue: `exect_s1_s3_residual_qualitative_queue_and_taxonomy_20260521.md` § S1  
Prior reject: S1 seizure H2 pre-vocab (`exect_s1_seizure_pre_vocab_slice_gpt_inspection_20260520.md`) — −8.2pp seizure F1  
Anchor: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` (seizure_type 90.5% F1)

## Question

Can a **narrow post-extraction guard** suppress generic `secondary` and differential-context seizure-type labels without the recall loss seen from static pre-vocabulary injection?

## No-model error taxonomy (GPT full validation, seizure_type)

| Bucket | Docs | Count | Tag | Example |
| --- | --- | ---: | --- | --- |
| Standalone `secondary` FP | EA0072, EA0137 | 2 | uncertainty-leakage | Gold wants `focal motor seizure`; model emits `secondary` |
| Differential / historical seizure FP | EA0179 | 1 | uncertainty-leakage | `complex partial seizures` from differential wording |
| Modernized vs sparse gold | EA0143 | 1 | scorer-surface | `focal seizures with altered awareness` vs gold `focal` |
| Descriptive span vs broad gold | EA0174 | 1 | scorer-surface | Long clinical phrase vs `epileptic seizures` |
| Recall misses | EA0109, EA0072, EA0143, … | 4 FN | scorer-surface / gold | Not primary guard target |

**Design constraint:** Fixing scorer-surface FNs via broad recall prompts risks new over-specificity FPs (EA0143 diagnosis pattern). Guards target **precision leakage** only.

## Existing infrastructure (reuse, do not rerun H2)

- `exect_seizure_type_benchmark_bridge` already coarsens modern surfaces and splits fused phrases (`src/clinical_extraction/exect/primitives.py`).
- `_SECONDARY_COLLAPSED_SEIZURE_TOKEN` and `_should_co_list_secondary_token` only **add** `secondary` when note supports secondary-generalized seizures — they do not remove spurious standalone `secondary`.
- S3 `_should_reroute_misplaced_seizure_phrase` removes onset leakage — different failure mode.

## Proposed tiers (`implementation_variant`)

| Tier | ID | Action | Expected effect | Recall risk |
| --- | --- | --- | --- | --- |
| **N0** | `sz_guard_drop_standalone_secondary_v1` | Drop seizure_type label if canonical == `secondary` and note lacks `_SECONDARY_GENERALISED_SEIZURE_NOTE_RE` | −2 FP (EA0072, EA0137) | Low if co-list rule unchanged |
| **N1** | `sz_guard_differential_context_v1` | Drop label if evidence window matches differential markers (`differential`, `?`, `vs`, `exclude`, `query`) without affirmed seizure-type header | −1 FP (EA0179) | Medium — preregister allowed seizure headers |
| **N2** | `sz_guard_modernized_coarsen_only_v1` | Apply existing `_GRANULAR_SEIZURE_TYPE_COARSENING` map only (no new surfaces) | scorer-surface FPs | Low — bridge-only |

**Do not combine N0+N1+N2 in first arm.** Run N0 alone on residual slice.

### N1 differential markers (draft)

Reuse patterns from `_note_has_dissociative_epileptic_seizure_contrast` neighborhood in `exect_s0_s1.py`:

- Window: ±120 chars around evidence quote or label mention
- Drop if: `differential diagnosis`, `?`, `possible`, `query`, `exclude`, `rule out` **and** no `seizure type:` / `diagnosis:` affirmed header in same section

## Validation ladder

| Step | Split | Gate |
| --- | --- | --- |
| 1 | Fixed 6-doc S1 queue (EA0143, EA0136, EA0072, EA0174, EA0179, EA0125) | N0 must not add FP/FN vs baseline on queue |
| 2 | Cap-25 validation | `seizure_type` F1 ≥ baseline −1pp; micro F1 ≥ −1pp |
| 3 | Full validation (40) | Only if cap-25 passes; expect ≤1–2 label moves total |

**Low priority:** S1 micro is 92.3%; full-validation spend is optional after slice + cap-25.

## Planned arms

| Arm | Variant | Description |
| --- | --- | --- |
| L1 | control | Frozen `exect_s0_s1_field_family_v4_10` |
| N0 | `sz_guard_drop_standalone_secondary_v1` | Tier N0 only |

Hook: post-bridge in `exect_s0_s1_field_family` artifact path (same lane as inline bridges), new function beside `_apply_specificity_collapse_seizure_policy`.

## Open cells

- Whether N1 belongs in S1 or only in S2+ wider-schema guards
- Qwen S1 track (seizure 55.7% post-bridge) — separate prereg, not this guard port

## Next steps

1. Fixture tests on EA0072, EA0137, EA0179 (N0/N1).
2. Residual-slice replay script or manual score on 6-doc subset.
3. Prereg `exect_s1_seizure_modifier_guard_gpt_cap25_v1` only if slice passes.

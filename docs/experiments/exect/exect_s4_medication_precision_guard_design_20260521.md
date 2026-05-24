# ExECT S4 Medication Precision Guard — Design (No-Model FP Taxonomy)

Date: 2026-05-21  
Status: Design ready for preregistration / implementation  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (item 18)  
Residual synthesis: `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`  
Prior H1 arm (reject): `docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md`  
Analysis anchor: `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`

## Question

Can a **narrow** deterministic post-guard improve `medication_temporality` precision on S4 without repeating the H1 recall collapse (−6.6pp F1 at full validation)?

**Do not** rerun broad `exect.medication_temporality.post_classifier.v1` (H1). Start from no-model false-positive taxonomy, then preregister tiered guards.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s4_field_family` |
| Research axis | 3 — `implementation_variant` (post-guard tiers) |
| Comparison group | `exect_s4_medication_precision_guard_gpt_cap25_v1` (planned) |
| Baseline anchor | GPT S4 v1.2 full `…071248Z` |
| decision_scope | `arm` (per tier); mechanism class stays **open** until ≥2 implementations agree |

## No-model FP taxonomy (GPT full validation, 40 records)

Source: `score_exect_s4_prediction_set` on `…071248Z` predictions; gold/scorer unchanged.

### Medication temporality (52 FP, 2 FN)

| Bucket | Count | Share | Examples | Mechanism hypothesis |
| --- | ---: | ---: | --- | --- |
| **ASM planned/previous over-tag** | 28 | 54% | `lamotrigine\|planned`×5, `levetiracetam\|previous`×5, `levetiracetam\|planned`×4 | Model emits planned/previous without gold Prescription temporality; span-inferred gold is conservative |
| **Non-ASM leakage** | 19 | 37% | `aspirin\|current`, `omeprazole\|current`, `citalopram\|current`, `thyroxine\|current` | L1 over-extracts non-epilepsy drugs into MT family |
| **ASM current over-tag** | 5 | 10% | `levetiracetam\|current`, `carbamazepine\|current` (duplicate/conflict rows) | Extra current rows when gold has different status or no span |
| **Brand/generic FN** | 2 | — | `epilim chrono\|current`, `lamictal\|current` | Canonicalization gap (model uses `eplim\|current`) |

**Recall is not the primary problem:** 95.7% MT recall, 2 FN. Precision 46.4% drives F1.

### Annotated medication (36 FP, 1 FN) — coupled scope read

| Bucket | Count | Notes |
| --- | ---: | --- |
| Unlisted / brand surfaces | 20 | Overlap with MT non-ASM and brand gaps |
| Listed ASM extras | 16 | Same drugs as MT planned/previous FPs (levetiracetam, lamotrigine, carbamazepine) |

Many errors are **cross-family over-extraction** of the same drug surfaces. A guard that only touches `medication_temporality` should not silently change `annotated_medication` unless preregistered.

## Why H1 failed (design constraint)

`recover_exect_medication_temporality_with_post_classifier` applies three aggressive rules:

1. Drop non-ASM — **safe** (19 FP removable; minimal FN risk).
2. Reclassify status from evidence cues — **mixed** (fixes some FPs, misclassifies “started” as previous).
3. **Drop `unknown`** when evidence lacks explicit temporality markers — **recall killer** (17/19 H1 new FNs were dose-only ASM lines).

Full-validation result: +10.1pp precision, −6.6pp F1 → **reject (arm)**.

See `docs/experiments/exect/exect_s4_temporality_planned_taper_error_read_20260520.md`: taper-on-current policy is not the main failure mode.

## Proposed tiered guards (new primitive IDs)

Each tier is a **separate** `implementation_variant` for cap-25 search before any full-validation spend.

| Tier | ID (proposed) | Action | Expected FP reduction | Recall risk |
| --- | --- | --- | --- | --- |
| **G0** | `mt_guard_non_asm_only_v1` | Drop labels where canonical medication ∈ `_NON_ASM_MEDICATIONS` or ∉ `_ASM_CANONICAL_MEDICATIONS` | ~19 FPs | Low (0 dose-only ASM drops) |
| **G1** | `mt_guard_planned_previous_evidence_v1` | Drop `planned`/`previous` **only when** aligned evidence quote lacks planned/previous markers **and** infer returns `unknown` | ~10–15 FPs (subset of 28) | Medium — must not drop dose-only current |
| **G2** | `mt_guard_dose_current_fallback_v1` | If infer=`unknown` **and** model_status=`current` **and** quote matches dose-line pattern → **keep** `current` | Recovers H1 FNs | Low if scoped to ASM + dose regex |
| **G3** | `mt_guard_brand_alias_v1` | Map `eplim`→`epilim chrono`, `lamictal`→`lamictal` before scoring | 2 FN | None |

**Do not combine G0–G3 in one arm** for the first grid; run G0 alone, then G0+G2, then add G1 only if cap-25 F1 guard passes.

### G1 evidence markers (reuse existing policy)

From `infer_exect_medication_temporality` / planned-taper read:

- Planned: `to start`, `plan to`, `recommend starting`, `could prescribe`, …
- Previous: `was on`, `previously`, `stopped`, …
- Current: `currently taking`, dose-line without planned/previous markers

**Explicit exclusion:** Do not treat bare `started` as previous when dose line is present (EA0179 failure mode).

## Cap-25 prereg gates (draft)

| Metric | Gate |
| --- | --- |
| Primary | `medication_temporality` precision vs L1 baseline (`…071248Z` cap-25 prefix or dedicated L1 cap-25 run) |
| F1 guard | MT F1 must not regress **≥2pp** vs L1 on same 25 records |
| Regression guard | No ≥2pp micro-F1 drop on investigation, seizure_type, annotated_medication |
| Proceed to full | Only if precision ≥ +3pp **and** F1 guard passes on cap-25 |

Full validation (40): same gates; H1 showed cap-25 can be optimistic.

## Arms (planned comparison group)

| Arm | implementation_variant | Description |
| --- | --- | --- |
| L1 | control | Frozen `exect_s4_field_family_v1_2` single-pass (no new guard) |
| G0 | `mt_guard_non_asm_only_v1` | Tier G0 only |
| G0G2 | `mt_guard_non_asm_dose_current_v1` | G0 + dose-current fallback |
| G0G1 | `mt_guard_non_asm_planned_previous_v1` | G0 + G1 (only if G0G2 passes F1 guard) |

Configs and program hook: post-bridge in `exect_s4_field_family` artifact path (same position as H1), new function beside `recover_exect_medication_temporality_with_post_classifier`.

Implementation note (2026-05-24): G0 exists as `exect.medication_temporality.non_asm_guard.v1`. The next cap-25 arm is scaffolded as `exect.medication_temporality.non_asm_dose_current_guard.v1` / `mt_guard_non_asm_dose_current_v1`; it keeps the G0 non-ASM removal, preserves `current` ASM labels on dose-line evidence, and prunes planned/previous labels when aligned evidence lacks the corresponding cue. Config: `configs/experiments/exect_s4_mt_guard_g0g2_dose_current_cap25_gpt4_1_mini.json`.

## Open cells

- Annotated-medication coupled guard (separate prereg)
- Qwen port (only after GPT cap-25 + full pass)
- Evidence-span guard as precision selector (diagnostic only; broad abstention arm-rejects)
- Sparse families (onset, when_diagnosed) — deferred per residual synthesis

## Recommended next steps

1. G0 implemented and full-validation promoted as an arm; keep it as the current medication-temporality guard reference.
2. Run the G0G2 cap-25 scaffold only under the existing `exect_s4_medication_precision_guard_gpt_cap25_v1` gates.
3. Inspect with `decision_scope: arm`; do not infer mechanism closure from a single guard variant.
4. Full validation only for a cap-25 winner that improves precision and passes the F1 guard.

**Do not** rerun H1 or broad post-classifier configs.

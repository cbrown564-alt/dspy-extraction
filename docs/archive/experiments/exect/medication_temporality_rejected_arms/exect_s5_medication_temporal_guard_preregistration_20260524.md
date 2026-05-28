# ExECT S5 Medication Temporal Guard GPT Validation v1 — Pre-Registration

Date: 2026-05-24  
Status: **Rejected (cap-25 gate)**  
Comparison group: `exect_s5_axis1_axis2_decomposition_gpt_full_validation_v1`  
Parent plan: `docs/planning/kanban_plan.md` (Pathway A4)

## Research Question

On the ExECTv2 fixed validation split (cap-25 and full), does a post-prediction temporal evidence guard (**A4**) improve S5 `annotated_medication` **precision** versus the promoted **AM guard** baseline (`exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1`) without causing a recall drop of >3.0pp?

## Hypothesis

By checking the temporality of model-aligned medication evidence and cross-referencing it with note candidates, we can prune planned, historical, previous, and future-hypothetical anti-seizure medication (ASM) leaks. This should resolve precision failures in S5 medication extraction without losing recall on true current prescriptions.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema | `exect_s5_core_field_family` |
| Research axis | 3 |
| Comparison group | `exect_s5_axis1_axis2_decomposition_gpt_full_validation_v1` |
| Primary varied factor | `implementation_variant` |
| decision_scope | `arm` |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` (cap-25 first, then full if gates clear) |
| Model | GPT 4.1-mini |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |
| Prompt | `exect_s4_field_family_v1_2_label_policy` |
| Program architecture | `extract_verify` (ExECT S5 core module) |

## Arms

| Arm | medication_guard_strategy | Program variant | Config |
| --- | --- | --- | --- |
| Baseline | `am_guard_non_asm_brand_alias_v1` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini.json` |
| A4 | `am_guard_temporal_evidence_v1` | `exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_v1` | `exect_s5_frequency_pre_vocab_am_guard_temporal_frequency_verify_full_gpt4_1_mini.json` |

## Primary and Guardrail Metrics

| Metric | Role | Target |
| --- | --- | --- |
| `annotated_medication` precision | **Primary** | Increase vs. Baseline (baseline: 79.7% full, 78.4% cap-25) |
| `annotated_medication` recall | **Recall guard** | Regress ≤ 3.0pp (baseline: 100.0% full, 100.0% cap-25) |
| `annotated_medication` F1 | Guardrail | Net positive delta vs. Baseline |
| `seizure_frequency` F1 | Guardrail | Stable vs. Baseline (baseline: 72.3% full, 71.7% cap-25) |
| Other families (diagnosis, seizure type, investigation) | Regression guard | No F1 regression > 1.0pp vs. Baseline |

## Confirmation Gates (Cap-25 / Full Validation)

| Outcome | Rule |
| --- | --- |
| **Promote (arm)** | `annotated_medication` precision increases (e.g. >85%) AND recall drop ≤ 3.0pp AND other families stable |
| **Reject (arm)** | `annotated_medication` recall drops > 3.0pp OR precision does not improve OR other families regress |

## Run Order

1. Implement `recover_exect_annotated_medication_temporal_evidence_guard` and register program variant.
2. Run unit tests on the new primitive.
3. Run the cap-25 experiment and evaluate metrics.
4. If cap-25 confirmation gates are passed, run the full validation experiment.
5. Record metrics and decisions in walkthrough, Kanban, and paper defaults documents.

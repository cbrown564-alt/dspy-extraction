# ExECT S5 Frequency Verifier v2 Preregistration

Date: 2026-05-24
Parent plan: `docs/planning/kanban_plan.md` (S5 frequency residual iteration)
Decision scope: arm

## Hypothesis

Stacking **v1.3 qualitative evidence-gate extractor prompt** with **v2 residual-tuned verifier policy** (temporal/current scope + strict qualitative evidence) will reduce precision-dominated qualitative false positives from the paper-frozen v1 stack without recall collapse beyond the 3.0pp cap-25 gate.

## Fixed Controls

| Dimension | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `exectv2_fixed_v1:validation`; cap-25 before full validation |
| Surface | S5 core families |
| Baseline | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v1` (paper freeze, 72.3% full-val freq F1) |
| Model/provider | `gpt-4.1-mini`, OpenAI |
| Scorer mode | `exect_s5_core_field_family_deterministic_v1` |
| Candidate policy | High-recall pre-vocab unchanged |
| Medication guard | `am_guard_non_asm_brand_alias.v1` unchanged |

## Varied Factor

| Component | Treatment |
| --- | --- |
| Extractor prompt | `exect_s4_field_family_v1_3_qualitative_evidence_gate` |
| Verifier policy | `frequency_evidence_verify_reject_only_v2` (rules 7–9 + strict qualitative guard) |
| Program variant | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2` |

## Cap-25 Gate

| Gate | Criterion |
| --- | --- |
| Primary | `seizure_frequency` F1 ≥ v1 cap-25 F1 **or** precision +≥3pp with recall drop ≤3pp vs v1 cap-25 |
| Guard families | diagnosis, seizure_type, annotated_medication, investigation F1 each within −2pp of v1 cap-25 |
| Recall floor | `seizure_frequency` recall ≥ v1 cap-25 −3pp |
| Full validation | Only if cap-25 clears all gates |

## Config

| Arm | Config |
| --- | --- |
| v2 cap-25 | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2_cap25_gpt4_1_mini.json` |

## Forbidden Changes

- Scorer, loader, split, candidate-builder output, gold labels
- High-precision candidate pruning (rejected arm)
- Medication temporal guard (rejected A4 arm)

## Stop Rules

- Stop if candidate list contents or count change for the same note
- Stop if cap-25 recall drops >3pp without compensating precision gain
- Stop if guard families regress beyond threshold

# ExECT S1 Prompt Policy — Clean GPT Ablation Pre-Registration

Date: 2026-05-21  
Status: **Cap-25 configs ready — runs pending**  
Comparison group: `exect_s1_prompt_policy_gpt_validation_v1`  
Kanban: `docs/planning/kanban_plan.md` (Lane A, Phase 2)

## Research question

On ExECT S1 with **GPT 4.1-mini**, how much does **prompt policy** (`v4_10` production vs `v4_11` seizure-focused vs broader benchmark-policy language) affect pooled micro F1 and per-family F1, when bridges, verification, split, model, and scorer are fixed?

This is **separate** from the Qwen port group `exect_s1_seizure_prompt_policy_qwen_v1`. Do not mix Qwen runs or H1 post-bridge repair paths into this GPT comparison group.

## Hypothesis

`v4_11` improves `seizure_type` F1 versus `v4_10` without regressing diagnosis or medication on GPT, mirroring the Qwen cap-25 signal. A broader benchmark-policy prompt (if added) is expected to help medication recall at possible seizure precision cost.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `exect_v2` |
| Split | `exectv2_fixed_v1:validation` |
| Schema | `exect_s0_s1_field_family` (`exect_s1`) |
| Scorer | `exect_field_family_deterministic_v1` |
| Field families | diagnosis, seizure_type, annotated_medication |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Program | `exect_s0_s1_field_family_single_pass` |
| `repair_policy` | `none` (inline benchmark bridges — GPT production path) |
| `hybrid_balance_class` | `L1_llm_constrained` |
| Verification | `none` |
| Structured output | `provider_json_schema_with_pydantic_validation` |

## Varied factor

`prompt_policy`

## Arms

| Arm | `prompt_version` | Config (planned) |
| --- | --- | --- |
| **v4_10 production** | `exect_s0_s1_field_family_v4_10_label_policy` | `exect_s1_prompt_policy_v4_10_cap25_gpt4_1_mini.json` |
| **v4_11 seizure-focused** | `exect_s0_s1_field_family_v4_11_label_policy` | `exect_s1_prompt_policy_v4_11_cap25_gpt4_1_mini.json` |
| **Broader benchmark-policy** *(optional third arm)* | `exect_s0_s1_field_family_v4_9_label_policy` | `exect_s1_prompt_policy_v4_9_cap25_gpt4_1_mini.json` |

The optional v4_9 arm runs only if v4_10 vs v4_11 cap-25 shows a seizure-specific delta worth contextualizing. Skip if v4_11 is null on GPT (guardrail already passed at −1.5pp seizure F1 in Qwen group).

## Frozen baselines (historical — re-run under this group for clean evidence)

| Role | Run ID | Prompt | Micro F1 | Seizure F1 |
| --- | --- | --- | ---: | ---: |
| GPT production full | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | v4_10 | 92.3% | — |
| GPT H1 post-bridge full | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z` | v4_10 | 92.3% | 90.5% |
| GPT v4_11 guardrail cap-25 | `exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini_20260520T214222Z` | v4_11 | 94.7% | 93.9% |

## Run order

1. Cap-25 configs for v4_10 and v4_11 (reuse v4_11 config pattern from Qwen group, change comparison_group).
2. Dry-run → cap-25 both arms on matched 25 records.
3. Optional v4_9 cap-25 if justified.
4. Full validation (40) for arms passing cap-25 gate.
5. Inspection `docs/exect_s1_prompt_policy_gpt_validation_v1_inspection_<date>.md`.
6. Registry rows.

## Primary metrics

- **Pooled micro F1** (3 families)
- **`seizure_type` field-family F1**

## Diagnostic metrics

- `diagnosis` and `annotated_medication` F1 (cross-family guardrails)
- Evidence quote support rate
- Schema-valid prediction rate
- Mismatch document count per family

## Cap-25 gate

| Outcome | Rule |
| --- | --- |
| **Proceed to full** | v4_11 seizure F1 ≥ v4_10 − 2pp **and** diagnosis/medication each ≥ −2pp |
| **Promote v4_11 on GPT** | Full seizure F1 ≥ v4_10 + 2pp **or** micro F1 ≥ v4_10 + 1pp with no family regression > 2pp |
| **Reject v4_11** | Seizure F1 < v4_10 − 2pp on cap-25 or full |
| **Hold** | Seizure gain with medication/diagnosis noise within −2pp |

## Cross-track note

Qwen v4_11 cap-25 showed +11.6pp seizure F1 vs v4_10 H1 anchor. GPT guardrail already passed at −1.5pp. This group establishes **GPT-native** clean single-factor evidence.

## Artifacts checklist

- [ ] Cap-25 (+ full) configs with `comparison_group: exect_s1_prompt_policy_gpt_validation_v1`
- [ ] Inspection doc
- [ ] Registry rows with `varied_factor: prompt_policy`

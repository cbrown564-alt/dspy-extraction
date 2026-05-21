# Gan S0 Prompt Policy — Clean GPT Ablation Pre-Registration

Date: 2026-05-21  
Status: **Cap-25 complete — hold guardrails port; reject synthesis** — `docs/gan_s0_lane_a_gpt_cap25_inspection_20260521.md`  
Comparison group: `gan_s0_prompt_policy_gpt_validation_v1`  
Kanban: `docs/kanban_plan.md` (Lane A, Phase 2)

## Research question

On Gan S0 with **GPT 4.1-mini**, how much does **prompt policy** (baseline synthesis vs guardrails vs temporal benchmark-policy language) contribute to monthly-frequency accuracy when program architecture, evidence policy, split, model, and scorer are held fixed?

## Hypothesis

Guardrails and temporal benchmark-policy prompt language each improve monthly-frequency and category accuracy versus the original synthesis-backed policy, even on the same temporal-candidates verify-repair architecture.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `gan_2026` |
| Split | `gan_2026_fixed_v1:validation` |
| Model | GPT 4.1-mini |
| Scorer | `gan_frequency_deterministic_v1` |
| Architecture | `gan_frequency_s0_temporal_candidates_verify_repair` |
| Verification | `verify_repair` with deterministic temporal candidates (pre) |
| Evidence strategy | `model_quote` |
| Few-shot | `none` |
| `context_policy` | `full_note_plus_deterministic_temporal_candidates` |

## Varied factor

`prompt_policy` / `normalization_strategy` (prompt-supplied benchmark policy)

## Arms

| Arm | Policy label | `prompt_version` (planned) | Source policy |
| --- | --- | --- | --- |
| **Baseline synthesis** | `benchmark_policy_prompt` (legacy) | `gan_frequency_s0_synthesis_v1_port_temporal_v1` *(new)* | `GAN_FREQUENCY_SYNTHESIS_GUIDANCE` ported to temporal signatures |
| **Guardrails** | `benchmark_policy_prompt` (guardrails) | `gan_frequency_s0_guardrails_v2_2_port_temporal_v1` *(new)* | Arithmetic/temporal guardrails from direct guardrails v2.2 |
| **Temporal benchmark-policy** | `benchmark_policy_prompt` (temporal v1.1) | `gan_frequency_s0_temporal_candidates_verify_repair_v1_1` | Current promoted default |

### Implementation note

Historical prompt families were developed on **different** architectures (synthesis on direct, guardrails on direct, v1.1 on temporal+VR). Clean factor isolation requires **porting** baseline and guardrails policy text onto the temporal-candidates verify-repair signatures without changing primitive IDs, candidate builder, or scorer.

Do **not** compare raw historical runs across architectures as the evidence base for this group.

## Frozen reference (promoted arm only)

`gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z` — 65.1% monthly, 76.5% Purist, 84.2% Pragmatic, 100% evidence. The v1.1 arm should match this band on cap-25 before interpreting ported prompts.

## Run order

1. Implement two ported prompt versions (`synthesis_v1_port`, `guardrails_v2_2_port`) on temporal+VR modules.
2. Add cap-25 configs for three arms.
3. Dry-run → cap-25 → full validation for arms passing gate.
4. Inspection `docs/gan_s0_prompt_policy_gpt_validation_v1_inspection_<date>.md`.
5. Registry rows.

## Primary metric

**Monthly-frequency accuracy**

## Diagnostic metrics

- Purist and Pragmatic category accuracy
- Schema-valid rate
- Evidence quote support
- Infrequent-stratum monthly (known residual bucket)
- Invalid-label and abstention counts

## Cap-25 gate

| Outcome | Rule |
| --- | --- |
| **Proceed to full** | Monthly ≥ v1.1 cap-25 − 2pp **and** schema ≥ 95% |
| **Promote prompt policy** (full) | Monthly ≥ v1.1 full − 1pp **or** Purist ≥ +3pp with monthly within 1pp |
| **Reject** | Monthly > 2pp below v1.1 cap-25 |

## Expected outcomes

- Guardrails port ≥ synthesis port on monthly (prior from direct-path history).
- v1.1 temporal policy ≥ both ports (current promoted default).

## Artifacts checklist

- [x] Ported prompt versions in `gan_frequency_s0.py` (`synthesis_v1_port`, `guardrails_v2_2_port`)
- [x] Three cap-25 configs
- [ ] Implementation note `docs/gan_s0_prompt_policy_port_implementation_<date>.md` (after first dry-run)
- [ ] Inspection doc
- [ ] Registry rows with `varied_factor: prompt_policy`

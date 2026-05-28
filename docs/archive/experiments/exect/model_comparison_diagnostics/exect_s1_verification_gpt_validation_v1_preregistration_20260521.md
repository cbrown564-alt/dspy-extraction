# ExECT S1 Verification Strategy — Clean GPT Ablation Pre-Registration

Date: 2026-05-21  
Status: **Cap-25 configs ready — runs pending**  
Comparison group: `exect_s1_verification_gpt_validation_v1`  
Kanban: `docs/planning/kanban_plan.md` (Lane A, Phase 2)

## Research question

On ExECT S1 with **GPT 4.1-mini**, does a **confirm-first verify-repair pass** improve benchmark-facing micro F1 or evidence quality versus single-pass extraction, when prompt policy, benchmark bridges, split, model, and scorer are fixed?

Distinct from interleaving H1 (artifact-only post bridges) and from rejected H2 pre-vocab shapes.

## Hypothesis

Verify-repair reduces medication false positives and unsupported evidence quotes without reopening add-only diagnosis recall. Net micro F1 gain is modest (≤ 3pp) given v4_10 single-pass already strong on GPT.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `exect_v2` |
| Split | `exectv2_fixed_v1:validation` |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Model | GPT 4.1-mini |
| Prompt (extraction) | `exect_s0_s1_field_family_v4_10_label_policy` |
| `repair_policy` | `none` on single-pass; `confirm_first_verifier_with_deterministic_guards` on verify-repair |
| Benchmark bridges | Inline on single-pass; unchanged deterministic guards on verify-repair |
| Few-shot | embedded benchmark-facing label-policy examples |

## Varied factor

`verification_strategy`

## Arms

| Arm | `verification_strategy` | `program_variant` | `prompt_version` | Config (planned) |
| --- | --- | --- | --- | --- |
| **Single-pass** | `none` | `exect_s0_s1_field_family_single_pass` | `exect_s0_s1_field_family_v4_10_label_policy` | `exect_s1_verification_single_pass_cap25_gpt4_1_mini.json` |
| **Verify-repair** | `verify_repair` | `exect_s0_s1_field_family_verify_repair` | `exect_s0_s1_field_family_verify_repair_v1` | `exect_s1_verification_verify_repair_cap25_gpt4_1_mini.json` |

Verify-repair extraction uses v4_10 via `resolve_exect_s0_s1_extraction_prompt_version`.

## Frozen references

| Role | Run / config | Notes |
| --- | --- | --- |
| Single-pass full | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | 92.3% micro, freeze |
| Legacy verify-repair cap-25 | `exect_s0_s1_verify_repair_cap25_gpt4_1_mini` | v4_2 era — **not** clean baseline for this group |

## Run order

1. Refresh verify-repair config for v4_10 alignment.
2. Dry-run → cap-25 both arms.
3. Full validation (40) if cap-25 gate passes.
4. Inspection `docs/exect_s1_verification_gpt_validation_v1_inspection_<date>.md`.
5. Registry rows.

## Primary metric

**Pooled micro F1**

## Diagnostic metrics

- Per-family F1 (diagnosis, seizure_type, annotated_medication)
- Evidence quote support rate
- Verifier confirm / repair / abstain counts
- Latency (verify-repair ≈ 2× model calls)

## Cap-25 gate

| Outcome | Rule |
| --- | --- |
| **Proceed to full** | Micro F1 ≥ single-pass − 1pp **and** evidence support ≥ +3pp |
| **Promote verify-repair** | Full micro F1 ≥ single-pass + 1pp with no family regression > 2pp |
| **Reject** | Micro F1 < single-pass − 2pp **or** seizure_type regression > 3pp |

## Expected outcomes

- Medication FP reduction (prior v4_2 verify-repair motivation).
- Possible seizure recall tradeoff — reject if seizure_type regresses.

## Artifacts checklist

- [ ] Updated cap-25 + full configs
- [ ] v4_10 verify-repair alignment note if signature changes needed
- [ ] Inspection doc
- [ ] Registry rows with `varied_factor: verification_strategy`

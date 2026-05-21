# ExECT S1 GPT Factor-Isolation — Cap-25 Inspection

Date: 2026-05-21  
Scope: cap-25 (25 records), GPT 4.1-mini, clean comparison groups  
Preregistrations: `docs/exect_s1_prompt_policy_gpt_validation_v1_preregistration_20260521.md`, `docs/exect_s1_verification_gpt_validation_v1_preregistration_20260521.md`, `docs/exect_s1_evidence_policy_gpt_validation_v1_preregistration_20260521.md`

## Taxonomy (shared fixed controls)

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2 `exectv2_fixed_v1:validation` (cap-25) |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Model | GPT 4.1-mini |
| Base prompt | v4_10 label policy (except prompt-policy v4_11 arm) |
| `repair_policy` | `none` (inline bridges) except verify-repair arm |

## Run artifacts

| Group | Arm | Run ID |
| --- | --- | --- |
| Prompt policy | v4_10 baseline | `exect_s1_prompt_policy_v4_10_cap25_gpt4_1_mini_20260520T232829Z` |
| Prompt policy | v4_11 treatment | `exect_s1_prompt_policy_v4_11_cap25_gpt4_1_mini_20260520T232833Z` |
| Verification | single-pass | `exect_s1_verification_single_pass_cap25_gpt4_1_mini_20260520T232837Z` |
| Verification | verify-repair | `exect_s1_verification_verify_repair_cap25_gpt4_1_mini_20260520T232841Z` |
| Evidence | standard (v4_10) | `exect_s1_evidence_standard_cap25_gpt4_1_mini_20260520T232844Z` |
| Evidence | strict addendum | `exect_s1_evidence_strict_cap25_gpt4_1_mini_20260520T232848Z` |
| Evidence | soft addendum | `exect_s1_evidence_soft_cap25_gpt4_1_mini_20260520T233326Z` |

## Headline metrics

| Group | Arm | Micro F1 | Diagnosis | Seizure | Medication | Evidence support | Mismatch docs |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prompt | v4_10 | **95.8%** | 97.6% | **95.4%** | 94.9% | 97.3% | 5 |
| Prompt | v4_11 | 95.1% | 97.6% | 93.9% | 94.7% | 97.4% | 7 |
| Verification | single-pass | **95.8%** | 97.6% | **95.4%** | 94.9% | 97.3% | 5 |
| Verification | verify-repair | 86.4% | 87.2% | 86.6% | 85.7% | 97.4% | 18 |
| Evidence | standard | **95.8%** | 97.6% | **95.4%** | 94.9% | 97.3% | 5 |
| Evidence | strict | 96.3% | 97.6% | 95.4% | 96.6% | 97.3% | 5 |
| Evidence | soft | 95.1% | 97.6% | 92.3% | 96.6% | 93.0% | 7 |

v4_10 baseline, verification single-pass, and evidence standard are metric-identical (same program + prompt on the same 25 records).

## Group 1 — Prompt policy (`exect_s1_prompt_policy_gpt_validation_v1`)

**Varied factor:** `prompt_policy` (v4_10 vs v4_11)

| Check | Result |
| --- | --- |
| Seizure F1 vs v4_10 | **−1.5pp** (93.9% vs 95.4%) — within −2pp guardrail |
| Micro F1 vs v4_10 | **−0.7pp** |
| Cross-family guardrail | Diagnosis flat; medication −0.2pp |
| Promote bar (+2pp seizure or +1pp micro) | **Fail** |

Notable v4_11 regressions: EA0029 spurious `absence seizures` FP; EA0116 medication FN (levetiracetam).

| Decision | Outcome |
| --- | --- |
| v4_10 | **Hold (GPT cap-25 anchor)** — matches historical cap-25 reference (`…221936Z`) |
| v4_11 | **Reject for GPT production** — null cap-25 signal; do **not** run GPT full validation |

**Interpretation:** v4_11 seizure-focused addendum helps Qwen (separate group) but does not improve GPT on this slice. Keep GPT production prompt at **v4_10**.

## Group 2 — Verification (`exect_s1_verification_gpt_validation_v1`)

**Varied factor:** `verification_strategy` (none vs verify-repair)

| Check | Result |
| --- | --- |
| Micro F1 vs single-pass | **−9.4pp** (86.4% vs 95.8%) |
| Evidence support delta | **+0.1pp** (97.4% vs 97.3%) |
| Seizure F1 regression | **−8.8pp** |
| Cap-25 proceed gate | **Fail** |

Verify-repair errors cluster on EA0026 (JME diagnosis FP, myoclonic overcall), EA0048 (seizure-type collapse), EA0045/EA0061/EA0069 (diagnosis/medication FNs). Confirm-first guards strip valid labels without compensating precision gain on benchmark F1.

| Decision | Outcome |
| --- | --- |
| single-pass | **Hold (anchor)** |
| verify-repair | **Reject** — do **not** run full validation |

**Interpretation:** LLM verify-repair under v4_10 is harmful on GPT cap-25. Distinct from interleaving H1 (artifact bridges), which add ~24pp via deterministic mapping — not a second LLM pass.

## Group 3 — Evidence policy (`exect_s1_evidence_policy_gpt_validation_v1`)

**Varied factor:** `evidence_strategy` (standard vs strict vs soft signature addenda)

| Check | Result |
| --- | --- |
| Strict micro vs standard | **+0.6pp** (96.3% vs 95.8%) |
| Strict evidence vs standard | **0.0pp** (97.3%) |
| Soft micro vs standard | **−0.7pp** |
| Soft evidence vs standard | **−4.4pp** (93.0% vs 97.3%) |
| Soft seizure vs standard | **−3.1pp** |
| Promote bar (evidence ≥ +5pp vs soft, micro within −1pp) | Strict evidence +4.3pp vs soft — **below +5pp bar** |

| Decision | Outcome |
| --- | --- |
| standard | **Hold (anchor)** — no change to production evidence policy |
| strict | **Hold (null)** — marginal micro bump, no evidence diagnostic gain |
| soft | **Reject** — worse seizure F1 and evidence support |

**Interpretation:** Evidence-only prompt addenda do not isolate a promotable mechanism on GPT cap-25. Standard v4_10 quote policy remains the default.

## Cross-group conclusions

| Factor | Clean cap-25 signal | Full validation? |
| --- | --- | --- |
| Prompt policy (v4_11) | Null / slight negative on GPT | **No** |
| Verification (verify-repair) | Strong negative | **No** |
| Evidence (strict/soft) | Null / negative | **No** |

These are the first **clean single-factor** GPT rows for the research-atlas evidence matrix. Historical bundled rows remain priors only.

## Recommended next pull

1. Lane Q: if not done, complete Qwen v4_11 full validation (`exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama.json`) — separate from these GPT groups.
2. Lane A (Gan): proceed with Gan verification/evidence/prompt-policy cap-25 configs (GPT).

Registry rows added under `exect_s1_prompt_policy_gpt_validation_v1`, `exect_s1_verification_gpt_validation_v1`, and `exect_s1_evidence_policy_gpt_validation_v1`; atlas and matrix regenerated 2026-05-21.
5. Do **not** port verify-repair or v4_11 to GPT production without new evidence.

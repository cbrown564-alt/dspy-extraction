# ExECT S1 Optimizer Pilot — Cap-25 Inspection

Date: 2026-05-21  
Scope: cap-25 (25 records), GPT 4.1-mini, clean comparison group  
Preregistration: `docs/exect_s1_optimizer_gpt_cap25_v1_preregistration_20260521.md`

## Taxonomy (shared fixed controls)

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2 `exectv2_fixed_v1:validation` (cap-25) |
| Train split (bootstrap only) | `exectv2_fixed_v1:train` (first 40 of 120 train IDs) |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Model | GPT 4.1-mini |
| Prompt | v4_10 label policy |
| Program | `exect_s0_s1_field_family_single_pass` |
| `repair_policy` | `none` (inline benchmark bridges) |

## Run artifacts

| Arm | `optimizer_strategy` | Run ID |
| --- | --- | --- |
| Frozen baseline | `zero_shot_or_prompt_only` | `exect_s1_optimizer_baseline_cap25_gpt4_1_mini_20260521T000602Z` |
| Bootstrap compiled | `bootstrapped` | `exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini_20260521T000608Z` |

Compiled state: `runs/exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini_20260521T000608Z/artifacts/compiled_state.json` (4 bootstrapped demos).

## Headline metrics

| Arm | Micro F1 | Δ vs baseline | Diagnosis | Seizure | Medication | Evidence support | Mismatch docs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen baseline | **95.8%** | — | 97.6% | **95.4%** | 94.9% | 97.3% | 5 |
| Bootstrap compiled | 90.7% | **−5.1pp** | 95.0% | 86.2% | 92.9% | 92.9% | 12 |

The frozen baseline is metric-identical to the clean prompt-policy v4_10 cap-25 row (`…232829Z`), confirming the in-group reference is stable.

## Optimizer diagnostics (bootstrap arm)

| Diagnostic | Value |
| --- | --- |
| Optimizer | BootstrapFewShot |
| Optimizer metric | `exect_field_family_micro_f1` (dev-only; not benchmark claim) |
| Trainset size | 40 dev records |
| Compiled demos | 4 |
| Compile duration | 17.7 s |
| Estimated model calls | 65 (40 compile + 25 eval) |
| Token usage | 118,922 total (111,619 prompt / 7,303 completion) |
| Schema-valid predictions | 25/25 (100%) |
| Prediction latency | 3.6 s/record vs 0.02 s/record baseline |

## Cap-25 gate

| Check | Result |
| --- | --- |
| Micro F1 ≥ baseline + 2pp | **Fail** (−5.1pp) |
| Schema ≥ 95% | Pass (100%) |
| No family regression > 3pp | **Fail** (seizure −9.2pp) |
| Proceed to full-validation design | **No** |

Per preregistration: **reject** bootstrap on null/negative micro delta.

## Error analysis

Shared mismatches (both arms): EA0052 (medication FN), EA0072 (secondary overcall), EA0078 (medication FP on missing-gold doc), EA0109 (temporal lobe seizures FN), EA0125 (JME abbreviation FN).

Bootstrap-only regressions:

| Doc | Mode | Detail |
| --- | --- | --- |
| EA0018 | diagnosis/seizure FN | Missed co-listed `epilepsy` and `focal seizures` |
| EA0026 | medication FN | Missed `sodium valproate` |
| EA0047 | seizure FP | `myoclonic seizures` overcall |
| EA0090 | seizure surface | `secondary generalized seizures` vs gold `secondary generalisation` + GTCS split |
| EA0102 | medication FN | Missed `sodium valproate` |
| EA0124 | seizure FP | `absence seizures` overcall |

These overlap familiar GPT failure modes (granular/myoclonic overcall, secondary surface mismatch, medication recall) rather than introducing a new promotable mechanism.

## Decisions

| Arm | Outcome | Rationale |
| --- | --- | --- |
| Frozen baseline | **Hold (in-group anchor)** | 95.8% micro; matches prior clean v4_10 cap-25 reference |
| Bootstrap compiled | **Reject** | −5.1pp micro, −9.2pp seizure F1; no full validation |

## Interpretation

BootstrapFewShot with dev micro-F1 metric **does not** improve ExECT S1 on GPT cap-25. Compiled demos appear to steer the model toward dev-set label surfaces that hurt seizure normalization and medication recall on the held-out cap-25 slice. Manual v4_10 policy examples remain the production path.

Optimizer metric note: the dev-set `exect_field_family_micro_f1` reward uses the same bridge path as benchmark scoring, but bootstrap selection on 40 dev records did not transfer to validation micro F1. Do not treat optimizer metric scores as benchmark evidence.

## Recommended next pull

1. **Do not** run bootstrap full validation or Qwen compile for this arm.
2. Lane Q: Qwen v4_11 full validation if still open (`exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama.json`).
3. Lane A (Gan): optional guardrails-port error-read or registry/atlas refresh from prior Gan cap-25 groups.

Registry rows added under `exect_s1_optimizer_gpt_cap25_v1` with `varied_factor: optimizer_strategy`.

# Gan S0 R9 Recovery And Exact-Policy Summary

Date: 2026-05-26
Decision scope: mechanism and validation-candidate hygiene
Dataset/split: Gan 2026 synthetic, `gan_2026_fixed_v1:validation`
Scorer: `gan_frequency_deterministic_v1`

## Purpose

This note separates the late R9 recovery artifacts from earlier R1.1 schema-guard
replays so the registry can cite the correct current evidence. It does not
authorize a Gan test-holdout run by itself; a separate promotion or holdout
selection review remains required before any test config is created or run.

## Current Evidence

| Arm | Run ID | Model | Scope | Monthly | Purist | Pragmatic | Schema valid | Evidence support | Decision |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| R9 recovery candidate | `gan_s0_l2_qwen_exact_policy_full_qwen35b_ollama_20260526T122351Z` | Qwen3.6:35b / Ollama | full validation, 299 records | 69.1% | 76.5% | 81.2% | 99.7% | 99.0% | Hold as final Gan Qwen validation candidate pending promotion review. |
| GPT exact-policy comparison | `gan_s0_l2_exact_policy_full_gpt4_1_mini_20260526T123247Z` | GPT 4.1-mini | full validation, 299 records | 78.5% | 86.9% | 90.3% | 99.7% | 100.0% | Freeze as comparison evidence, not a new Gan operational default. |
| Hybrid-resolution cap gate | `gan_s0_l2_qwen_hybrid_resolution_cap25_qwen35b_ollama_20260526T093907Z` | Qwen3.6:35b / Ollama | cap-25 | 60.0% | 64.0% | 76.0% | 100.0% | 100.0% | Superseded by the later full-validation recovery candidate. |

## Interpretation

The late R9 recovery candidate restores near-complete schema validity with only
one invalid abstention while keeping benchmark-facing monthly accuracy in the
same band as the earlier exact-policy family. It should be treated as the
current Gan Qwen validation candidate for review, not as an automatic replacement
for the GPT 4.1-mini builder-gap v1 operational default.

The GPT exact-policy run is useful as a same-policy closed-model comparison. It
does not change the current Gan operational default because the default was
already established by the builder-gap v1 promotion review.

## Caveats

- Gan gold is `seizure_frequency_number[0]`; `reference[0]` remains diagnostic.
- Raw exact and normalized-label exact metrics are diagnostic, not the primary
  benchmark-facing metrics.
- Evidence support is deterministic quote/source grounding, not clinical
  adjudication.
- Gan holdout remains blocked until a promotion/hold note selects the final test
  candidate explicitly.

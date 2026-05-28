# ExECT S4 Seizure-Frequency Pre-Candidate — Pre-Registration

Date: 2026-05-20  
Comparison group: `exect_s4_frequency_deterministic_v1`

## Hypothesis

Note-anchored **seizure-frequency-only** pre-candidate injection (`H2_pre_deterministic`) improves `seizure_frequency` F1 on the cap-25 ExECTv2 validation gate versus frozen S4 single-pass (`L1_llm_constrained`), without changing schema breadth, scorer, or prompt policy version.

## Fixed controls

| Control | Value |
| --- | --- |
| Dataset / split | ExECTv2 `exectv2_fixed_v1:validation` |
| Record cap | 25 |
| Schema | `exect_s4_field_family` (11 families) |
| Scorer | `exect_s4_field_family_deterministic_v1` |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Prompt | `exect_s4_field_family_v1_2_label_policy` |
| Program architecture | `single_pass` |

## Varied factor

`interleaving_position` — L1 (`during` only) vs H2 (`pre` + `during`).

H2 injects only `seizure_frequency` candidates built from:

- Note-anchored quantified/qualitative ExECT surfaces
- Filtered Gan temporal-candidate hints when `canonical_label` maps to audited ExECT frequency templates (not Gan monthly scorer semantics)

## Arms

| Arm | Config | Program variant |
| --- | --- | --- |
| L1 baseline | `exect_s4_frequency_l1_baseline_cap25_gpt4_1_mini.json` | `exect_s4_field_family_single_pass` |
| H2 pre-vocab | `exect_s4_frequency_h2_pre_vocab_cap25_gpt4_1_mini.json` | `exect_s4_field_family_frequency_pre_vocab_single_pass` |

## Primary metric

`seizure_frequency` field-family F1 (benchmark-facing).

## Diagnostic metrics

- Pooled micro F1 across eleven families (not comparable to S1–S3 headlines)
- Per-family F1 for frozen S3 families (regression guard)
- Evidence quote support rate

## Promotion gate

- Cap-25: require **≥2pp** `seizure_frequency` F1 vs L1 **and** no ≥2pp regression on any frozen S3 family F1 vs L1 on the same 25 records
- Full validation (40): only if cap-25 gate passes

## Expected reject paths

- H2 anchors non-audited Gan monthly labels → reject (scorer mismatch)
- H2 improves frequency but regresses seizure_type/diagnosis on cap-25 → reject (S1 H2 lesson)
- Null or negative frequency delta → reject; do not port to Qwen

## Artifacts

Inspection doc after runs: `docs/experiments/exect/exect_s4_frequency_deterministic_gpt_inspection_20260520.md` (post-run).

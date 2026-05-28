# ExECT Family-Span Prompt Comparison E8 Preregistration

Date: 2026-05-28
Status: mechanism open; preregistered cap-slice comparison
Kanban card: E8 - Family-Span Cap-Slice Prompt Comparison

## Hypothesis

E4 `exect.sections.family_spans.v1` context can preserve S1 family recall while reducing false-family context exposure or prompt substrate size relative to matched full-note prompting.

## Fixed Controls

- Dataset/split: ExECTv2 `exectv2_fixed_v1:validation`.
- Cap: first 25 validation documents.
- Model/provider: GPT 4.1-mini / OpenAI via `configs/models/gan_s0_gpt4_1_mini.json`.
- Schema level: `exect_s0_s1_field_family`.
- Prompt: `exect_s0_s1_field_family_v4_10_label_policy`.
- Scorer: `exect_field_family_deterministic_v1`.
- Repair policy: `post_prediction_clean_ladder_v1`.
- Holdout: not used; no loader, split, scorer, bridge, or prompt tuning from test.

## Arms

| Arm | Config | Context policy | Varied factor |
| --- | --- | --- | --- |
| Full-note baseline | `configs/experiments/exect_s1_full_note_e8_cap25_gpt4_1_mini.json` | full note | control |
| Family-span probe | `configs/experiments/exect_s1_family_span_e8_cap25_gpt4_1_mini.json` | E4 family spans for diagnosis/problem, seizure, medication, and investigation-bearing lines | context selection |

## Metrics And Diagnostics

- Primary: S1 micro F1 and per-family diagnosis, seizure type, and annotated medication precision/recall/F1.
- Substrate diagnostics: E4 cap-slice gold evidence coverage, false-family span counts, full-note character count, family-span character count, and family-span/full-note ratio.
- Evidence diagnostics: evidence quote support, exact support, ellipsis repair rate, and missing-evidence flags from the unchanged S1 scorer.
- Decision rule: family-span prompting is not promoted unless recall is preserved and the comparison shows a precision, evidence, or cost benefit. A regression rejects this arm shape only, not typed document geometry as a mechanism.

## Label-Policy Caveats

- Outputs are benchmark-facing S1 labels, not clinically rich extraction.
- Investigation spans are included only as context substrate for disambiguation; investigation is not scored in this S1 comparison.
- Medication temporality remains outside benchmark-facing S1 medication scoring.
- This cap slice is internal component evidence, not ExECT Table 1 reproduction.

# ExECT Family-Span Prompt Comparison E8 Results

Date: 2026-05-28
Status: rejected arm; mechanism open
Preregistration: `docs/experiments/exect/exect_family_span_prompt_comparison_e8_preregistration_20260528.md`
Kanban card: E8 - Family-Span Cap-Slice Prompt Comparison

## Research Question

Does the E4 `exect.sections.family_spans.v1` document-geometry substrate preserve S1 benchmark-facing extraction quality when it replaces full-note prompting on a matched cap-25 ExECT validation slice?

## Method

- Dataset/split: ExECTv2 `exectv2_fixed_v1:validation`.
- Cap: first 25 validation documents.
- Model/provider: GPT 4.1-mini / OpenAI.
- Schema level: `exect_s0_s1_field_family`.
- Scorer: `exect_field_family_deterministic_v1`.
- Prompt: `exect_s0_s1_field_family_v4_10_label_policy`.
- Repair policy: `post_prediction_clean_ladder_v1`.
- Varied factor: context selection only.

| Arm | Config | Run ID | Context |
| --- | --- | --- | --- |
| Full-note control | `configs/experiments/exect_s1_full_note_e8_cap25_gpt4_1_mini.json` | `exect_s1_full_note_e8_cap25_gpt4_1_mini_20260528T225300Z` | full note |
| Family-span probe | `configs/experiments/exect_s1_family_span_e8_cap25_gpt4_1_mini.json` | `exect_s1_family_span_e8_cap25_gpt4_1_mini_20260528T225330Z` | E4 spans for diagnosis/problem, seizure, medication, and investigation-bearing lines |

## Results

| Arm | Micro P | Micro R | Micro F1 | Diagnosis F1 | Seizure-type F1 | Medication F1 | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full note | 96.3% | 95.2% | 95.8% | 97.6% | 95.4% | 94.9% | 97.3% |
| Family span | 91.4% | 89.2% | 90.2% | 97.6% | 81.8% | 94.7% | 95.8% |

The E4 cap-slice substrate covered 116/116 gold annotations for the selected families. It used 29,319 characters versus 33,029 full-note characters, or 88.8% of the full-note substrate. False-family span counts in the full E4 validation audit remain measurable, especially seizure (59), plan/follow-up (55), frequency (36), diagnosis/problem (26), investigation (24), medication (23), and history/background (12).

## Interpretation

This family-span arm should not be promoted. The context substrate has perfect cap-slice gold evidence coverage, but the model-backed comparison loses 5.5pp micro F1 and the main failure is seizure type, dropping from 95.4% to 81.8% F1. Diagnosis and medication are essentially preserved, so the result is not a blanket rejection of typed document geometry. It rejects this single-pass S1 family-span prompt shape as a replacement for full-note prompting.

The likely mechanism is not evidence absence. The stronger explanation is that span rendering and false-family context alter the model's seizure-type adjudication surface despite covering the gold offsets. The character reduction is also modest, so this arm does not buy enough prompt-cost benefit to justify the quality loss.

## Caveats

- This is a cap-25 validation result, not full validation, test reporting, or ExECT Table 1 reproduction.
- Investigation spans were included as context only; investigation was not scored in this S1 comparison.
- Medication temporality remains outside benchmark-facing S1 medication scoring.
- The full-note control appears to have been served from DSPy/provider cache in this run, so runtime and token-use comparisons are not reliable. Quality metrics are still tied to the generated artifact outputs.
- Holdout was not used, and no scorer, loader, split, bridge, or prompt semantics changed.

## Next Steps

- E9 now records the rejection/diagnostic-substrate decision for this specific family-span prompting arm.
- If family spans are revisited, test a more targeted one-family or candidate-adjudication surface rather than replacing the whole S1 note context.
- Keep `exect.sections.family_spans.v1` as a document-geometry substrate and diagnostic coverage tool, not a promoted prompt-routing default.

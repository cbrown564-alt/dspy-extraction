# ExECT Section-Aware Versus Monolithic Ablation Design

Date: 2026-05-18

## Goal

Define the first ExECT architecture ablation after the 25-record S0/S1 validation cap: compare the current monolithic single-pass field-family extractor against a section-aware field-family variant while keeping the audited scorer, schema level, dataset split, and label-policy contract fixed.

This design is grounded in:

- `docs/exect_gold_label_audit.md`
- `docs/exect_s0_s1_baseline_design.md`
- `docs/exect_s0_s1_validation_cap25_inspection.md`
- `src/clinical_extraction/pipeline/sectioning.py`
- `tests/test_sectioning_context.py`

## Why This Is The Next Chunk

The cap-25 ExECT inspection changed the risk picture:

- evidence quote support is already strong enough for a first architecture comparison
- annotated-medication performance is no longer the dominant blocker
- the remaining ExECT errors are a mix of benchmark label-policy drift and cross-family leakage inside one monolithic extraction pass

The clearest architecture-shaped failures in the cap-25 note were:

- `EA0068`: diagnosis drift into non-diagnosis content
- `EA0090`: one rich seizure phrase leaking across diagnosis and seizure-type families
- `EA0109`: seizure-type content emitted as diagnosis while the benchmark seizure type was missed

These are plausible targets for a section-aware or field-family-disentangled variant. They do not justify changing scorer semantics.

## Hypothesis

Keeping the same benchmark-facing ExECT S0/S1 contract but restricting each field family to deterministic, section-aware context will reduce cross-family leakage and improve diagnosis and seizure-type precision relative to the current monolithic single-pass baseline, without materially hurting evidence quote support.

## Fixed Controls

The ablation should hold the following constant:

- dataset: `exect_v2`
- split: `exectv2_fixed_v1:validation`
- model/provider: `gpt-4.1-mini` via the existing OpenAI model config for the first comparison
- schema level: `exect_s0_s1_field_family`
- scorer mode: `exect_field_family_deterministic_v1`
- benchmark-facing field families: `diagnosis`, `seizure_type`, `annotated_medication`
- prompt guidance: current v3 ExECT label-policy and evidence policy
- deterministic bridges: fused seizure-type split and ellipsis evidence repair
- structured output strategy: provider JSON schema with Pydantic validation

This keeps architecture as the primary experimental factor.

## Existing Reusable Infrastructure

The repo already has deterministic note segmentation and lightweight context selection:

- `section_note(note_text)` produces offset-preserving sections with canonical titles such as `diagnosis`, `seizures`, and `medication`
- `select_context(note_text, target_field=..., max_sections=...)` returns ranked `EvidenceSpan` context snippets for a target field

The current tests already cover the basic contract:

- headings preserve offsets and canonical section titles
- section-aware selection prefers relevant sections when headings exist
- selection falls back to whole-document context when the note is unheaded

This is enough to open a first ExECT section-aware architecture variant without inventing a new retrieval subsystem.

## Proposed Variants

### Variant A: Monolithic Baseline

Keep the current program as the comparison anchor:

- program variant: `exect_s0_s1_field_family_single_pass`
- input: full note
- output: one joint response covering diagnosis, seizure type, and annotated medication

Use the existing cap-25 run as the baseline artifact and re-run only when a direct paired comparison is needed under the same command path.

### Variant B: Section-Aware Field-Family Extraction

Add a new program variant that keeps the same output schema but splits extraction by field family:

- diagnosis call: use deterministic section-aware context for diagnosis
- seizure-type call: use deterministic section-aware context for seizure type
- annotated-medication call: use deterministic section-aware context for medication
- merge the three family outputs back into the shared `DocumentPrediction` contract

Recommended first-pass context policy:

- diagnosis: up to 2 top sections from `select_context(..., target_field="diagnosis")`
- seizure type: up to 3 top sections from `select_context(..., target_field="seizure_type")`
- annotated medication: up to 2 top sections from `select_context(..., target_field="medication")`

If no headed sections score positively, fall back to the whole note so the architecture remains robust on unstructured letters.

## Module Boundary Recommendation

The first implementation should stay close to the current ExECT program rather than creating a second parallel framework.

Recommended implementation shape:

1. Keep shared normalization, bridge, and artifact logic in `src/clinical_extraction/programs/exect_s0_s1.py`.
2. Add a new DSPy signature or thin module wrapper for single-family extraction under the same prompt-policy regime.
3. Add a new program variant constant for the section-aware path.
4. Use `select_context` from `src/clinical_extraction/pipeline/sectioning.py` before each family call.
5. Merge family outputs through the same `ExtractedValue` construction path so scorer semantics remain identical.

This should avoid duplicating the ExECT bridge behavior in a second file.

## Prompt And Evidence Policy

The section-aware variant should not loosen benchmark-facing policy. It should carry forward the same constraints:

- no diagnosis inference from a single seizure event
- no seizure-type inference from diagnosis alone
- no planned or historical medication mentions in benchmark-facing medication outputs
- exact contiguous evidence quotes when possible

The section-aware variant may prepend a short context label such as `Section: diagnosis` or `Section: medication` to the selected text, but it should not change the benchmark label examples or allowed output families.

## Evaluation Plan

The first architecture comparison should remain capped and diagnostic:

1. Add mocked-LM tests for section-aware routing and merged output behavior.
2. Add a sibling experiment config for the section-aware ExECT variant on the same validation cap.
3. Dry-run the config before any model call.
4. Run a capped validation comparison, preferably on the same 25-record slice first.
5. Compare:
   - micro precision, recall, F1
   - per-family precision, recall, F1
   - evidence quote support overall and split by exact vs repaired quotes
   - bounded mismatch examples for diagnosis/seizure-type leakage

The report should explicitly state that this is an architecture ablation under fixed scorer semantics, not benchmark reproduction.

## Success Criteria

The section-aware variant is worth keeping if it shows one or both of:

- fewer diagnosis and seizure-type false positives caused by cross-family leakage
- equal or better benchmark-facing F1 without a meaningful evidence-support drop

It is not automatically a win if it only shifts the same label-policy errors into smaller context windows.

## First Implementation Slice

The next coding pull after this design should be:

1. Add a section-aware ExECT field-family module variant that reuses the existing artifact bridge.
2. Add focused tests for context selection, per-family call routing, and merged prediction output.
3. Add a capped section-aware experiment config on the same ExECT validation slice.
4. Run dry-run validation and one capped comparison run before considering broader section-aware or field-group variants.

## Risks And Boundaries

- The deterministic sectioner is intentionally simple; some notes may use header styles that do not map cleanly into the current alias set.
- Section-aware context may help cross-family leakage while hurting recall if relevant evidence is spread across multiple headings.
- Some remaining cap-25 failures are still label-policy normalization failures; architecture alone will not solve those.
- Keep this ablation on S0/S1 only. Do not widen schema breadth and architecture complexity in the same step.

## Audit Guidance Used

The design follows `docs/exect_gold_label_audit.md` by keeping seizure types tied to audited diagnosis-style labels, preserving diagnosis certainty/specificity behavior, and treating medication temporality and missing-gold limits as caveats rather than scorer changes.

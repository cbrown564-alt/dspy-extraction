# ExECT Section-Aware Cap-25 Inspection

Date: 2026-05-18

## Goal

Inspect the first capped ExECT S0/S1 section-aware architecture run against the existing monolithic cap-25 baseline while keeping scorer semantics, schema level, prompt version, and deterministic bridges fixed.

Compared runs:

- Monolithic baseline: `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260518T172431Z`
- Section-aware variant: `runs/exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z`

Shared controls:

- dataset: `exect_v2`
- split: `exectv2_fixed_v1:validation`
- max records: 25
- model/provider: `gpt-4.1-mini` via the existing OpenAI config
- schema level: `exect_s0_s1_field_family`
- scorer mode: `exect_field_family_deterministic_v1`
- prompt version: `exect_s0_s1_field_family_v3_seizure_evidence_policy`
- benchmark bridge behavior: fused seizure-type split and ellipsis evidence repair unchanged

Changed factor only:

- program variant: `exect_s0_s1_field_family_single_pass` -> `exect_s0_s1_field_family_section_aware`

## Validation

Commands run:

```bash
uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py tests/test_sectioning_context.py
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_section_aware_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_section_aware_cap25_gpt4_1_mini.json --env-file .env
```

The first section-aware run at `runs/exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174251Z` used the correct module but wrote stale `single_pass` metadata into `predictions.json`. The wiring bug was fixed in `scripts/run_experiment.py`, and the canonical section-aware artifact for comparison is:

- `runs/exect_s0_s1_section_aware_cap25_gpt4_1_mini_20260518T174714Z`

## Result

The section-aware variant underperformed the monolithic baseline on the same capped validation slice.

Metric comparison:

- micro precision: `68.8% -> 58.5%`
- micro recall: `79.5% -> 74.7%`
- micro F1: `73.7% -> 65.6%`
- diagnosis F1: `60.5% -> 44.9%`
- seizure-type F1: `65.8% -> 59.7%`
- annotated-medication F1: `92.1% -> 88.9%`
- evidence quote support: `92.1% -> 75.5%`
- evidence quote support on exact model quotes: `92.0% -> 75.0%`
- evidence quote repair rate: `unchanged low`, but too small to offset the broader evidence drop

This is not a promotion candidate. The first section-aware attempt does not beat the current monolithic cap-25 baseline.

## Failure Shape

### 1. Section-aware context did not remove the key architecture-shaped false positives

Several previously motivating documents still failed in the same general way:

- `EA0090`: diagnosis still absorbs the richer seizure phrase `focal seizures with secondary generalisation` instead of keeping the benchmark seizure labels separated.
- `EA0109`: diagnosis still receives seizure content (`focal seizures, probably temporal lobe`), while seizure-type output remains partially mis-normalized (`temporal lobe` rather than the audited seizure labels).
- `EA0068`: diagnosis still picks up non-diagnosis seizure content (`infrequent focal seizures`).

This means the first section-aware split is not yet sufficient to disentangle label policy from field-family routing.

### 2. Evidence quality regressed sharply

The biggest unexpected regression is evidence support:

- many outputs now use heading-shaped synthetic evidence such as `Diagnosis: Focal epilepsy` or `Medication: Keppra 1000 milligrams twice a day`
- these strings are often not exact contiguous source quotes in the underlying note text, so offsets are missing and evidence support fails

Representative evidence-support failures:

- `EA0045` diagnosis: `Diagnosis: Focal epilepsy`
- `EA0029` medication: `Medication: Keppra 1000 milligrams twice a day`
- `EA0102` diagnosis: `Diagnosis: anxiety`

This suggests the section-aware prompt framing makes the model echo normalized heading-style summaries instead of verbatim note spans.

### 3. Medication scope and single-event diagnosis mistakes remain

The section-aware split did not preserve the current monolithic strengths:

- `EA0008`: medication false positive `levetiracetam` remains while gold `lamotrigine` is missed
- `EA0016` and `EA0100`: diagnosis still turns single-seizure content into unsupported diagnosis labels
- `EA0102`: diagnosis still emits unsupported non-epileptic and anxiety labels

So the family-specific calls did not solve the benchmark-boundary problems and may have weakened the note-level policy grounding that helped the monolithic prompt.

## Interpretation

The first section-aware implementation is still a useful negative result:

- it proves the current deterministic section selection and thin per-family prompting are not enough by themselves
- it shows that section-aware decomposition can worsen evidence grounding even when field-family metrics only degrade moderately
- it supports keeping the monolithic ExECT S0/S1 baseline as the active comparison anchor

The likely reasons are:

1. The family-specific signatures are too thin relative to the monolithic v3 policy text, so each call has weaker benchmark-boundary guidance.
2. The selected section text encourages the model to restate heading-plus-summary evidence rather than quote the raw note exactly.
3. Some benchmark decisions still require note-global context, especially to avoid turning seizure descriptions or differentials into diagnosis labels.

## Recommendation

Do not promote the section-aware variant as the new ExECT baseline.

If this architecture line continues, the next bounded improvement should be to keep the same section-aware routing but strengthen the per-family instruction surface before widening architecture complexity further:

1. carry the full benchmark-boundary policy into each family-specific signature rather than a shortened field-only prompt
2. reduce heading-echo evidence errors, possibly by asking for quote-only evidence without synthetic `Diagnosis:` / `Medication:` prefixes
3. consider tighter section filtering for diagnosis so seizure-history sections are less likely to drive diagnosis outputs

## Audit Guidance Used

This inspection follows `docs/exect_gold_label_audit.md` by:

- keeping diagnosis specificity and seizure-type benchmark surfaces fixed
- preserving the existing medication temporality boundary
- treating unsupported or missing evidence as diagnostic regression rather than a scorer change

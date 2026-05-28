# ExECT S5 Core Surface Design

Date: 2026-05-24  
Status: Design scaffold plus scorer entry point implemented  
Kanban card: `E4 - Define and scaffold ExECT S5 core surface`  
Decision scope: reporting/experiment surface; no loader, gold, normalization, or model prompt semantics changed

## Purpose

S5 is a focused reporting surface for ExECT core clinical extraction. It is not a
new broader schema than S4. It selects the families with enough benchmark value,
gold support, and scorer stability to sustain a research claim after the S1
pipeline-decomposition reconciliation.

S5 includes:

- `diagnosis`
- `seizure_type`
- `annotated_medication`
- `investigation`
- `seizure_frequency`

S5 excludes:

- `medication_temporality`
- `comorbidity`
- sparse S3 families: `birth_history`, `onset`, `epilepsy_cause`, `when_diagnosed`

## Field Support

Support counts were computed with the current ExECT JSON loader and
`data/splits/exectv2_splits.json`.

| Family | Corpus support | Corpus docs with label | Validation support | Validation docs with label | S5 status |
| --- | ---: | ---: | ---: | ---: | --- |
| `diagnosis` | 225 | 164 | 42 | 31 | Include |
| `seizure_type` | 229 | 141 | 47 | 32 | Include |
| `annotated_medication` | 268 | 166 | 47 | 29 | Include |
| `investigation` | 172 | 108 | 30 | 19 | Include |
| `seizure_frequency` | 207 | 129 | 43 | 24 | Include |
| `comorbidity` | 234 | 112 | 48 | 25 | Exclude from S5 core because overlap/surface policy remains noisy |
| `medication_temporality` | 268 | 166 | 47 | 29 | Exclude from S5 core because temporality is inferred from prescription span text |
| `birth_history` | 44 | 36 | 8 | 7 | Exclude as sparse diagnostic family |
| `onset` | 22 | 19 | 3 | 2 | Exclude as sparse diagnostic family |
| `epilepsy_cause` | 31 | 27 | 7 | 6 | Exclude as sparse diagnostic family |
| `when_diagnosed` | 17 | 17 | 4 | 4 | Exclude as sparse diagnostic family |

The included set meets the proposed support rule from
`docs/experiments/exect/exect_post_gan_s0_experiment_structure_20260524.md`:
each included family has at least 20 validation gold labels and a documented
gold source.

## Scorer Composition

Implemented scorer entry point:

- `score_exect_s5_document`
- `score_exect_s5_prediction_set`
- scorer string: `exect_s5_core_field_family_deterministic_v1`

The scorer composes existing family semantics:

| S5 family | Reused semantics |
| --- | --- |
| `diagnosis` | S1 audited diagnosis, certainty >= 4, affirmed, specificity-collapsed |
| `seizure_type` | S1 audited seizure-type Diagnosis rows, not frequency rows |
| `annotated_medication` | S1 annotated prescription names; no temporality status |
| `investigation` | S2/S4 modality+result canonical labels |
| `seizure_frequency` | S4 ExECT annotation-facing frequency surfaces |

No new normalization, bridge behavior, or gold interpretation is introduced.

## Caveats To Carry In Reports

- S5 is a partial ExECTv2 diagnostic view, not published Table 1 reproduction.
- S5 pooled micro F1 is not comparable to S1/S2/S3/S4 pooled micro F1 without
  stating that the family set changed.
- Seizure frequency uses ExECT annotation-facing labels such as `1 per 1 week`,
  `frequency increased`, and `seizure free since YEAR`; it does not use Gan
  monthly-frequency normalization.
- Medication temporality is deliberately excluded. The JSON prescription source
  has no native temporality column, and S4 temporality labels are span-inferred.
- Evidence support remains diagnostic and does not replace benchmark-facing
  field-family F1.

## Regression Guard Expectations

Future S5 model-backed runs should report:

- S5 pooled micro F1 and per-family F1.
- S1 guard families: diagnosis, seizure type, annotated medication.
- Investigation guard from S2/S4.
- Seizure-frequency F1 with ExECT-specific frequency caveats.
- Evidence quote support as a diagnostic.
- Gold quality flag rate.

Do not promote an S5 arm if it improves pooled S5 micro by trading away a
material S1 family regression unless the inspection explicitly chooses that
tradeoff.

## Next Pull

The next ExECT card should be a no-model S4/S5 frequency gold-template audit.
It should ask whether current ExECT seizure-frequency gold labels can be
represented by deterministic, note-anchored candidate surfaces before testing
candidate adjudication or structured-slot model arms.

# ExECT S0/S1 Validation Cap-25 Inspection

Date: 2026-05-18

Run artifact:
- `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260518T172431Z`

Config:
- `configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json`

Validation commands:

```bash
uv run --extra dev pytest tests/test_exect_s0_s1_program.py tests/test_experiment_configs.py tests/test_exect_scoring.py
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s0_s1_validation_cap25_gpt4_1_mini.json --env-file .env
```

## Scope

This is a 25-record diagnostic validation cap for the ExECT S0/S1 field-family baseline using:

- dataset: `exect_v2`
- split: `exectv2_fixed_v1:validation`
- model/provider: `gpt-4.1-mini` via OpenAI
- schema level: `exect_s0_s1_field_family`
- program variant: `exect_s0_s1_field_family_single_pass`
- scorer mode: `exect_field_family_deterministic_v1`
- prompt version: `exect_s0_s1_field_family_v3_seizure_evidence_policy`

This is not a published-benchmark reproduction or a full-validation estimate.

## Artifact Check

The standard run bundle is present and internally consistent:

- `metadata.json`: dataset, split, model, prompt version, scorer, and caveats match the intended cap-25 contract.
- `config.json`: preserves the v3 ExECT field-family single-pass contract and caps the validation slice at 25 records.
- `prompts.json`: records the embedded benchmark-facing label-policy guidance and examples used in the run.
- `predictions.json`: 25 predictions written successfully with the shared `PredictionSet` artifact contract.
- `metrics.json` and `errors.json`: scorer output present with field-family metrics and diagnostic evidence errors.

Note: `counts.missing_predictions = 175` reflects the intentional validation cap against the full 200-document gold pool, not a failed run on the selected 25 records.

## Metrics

Field-family metrics on the 25-record cap:

| Metric | Value |
|---|---:|
| Micro precision | 68.8% |
| Micro recall | 79.5% |
| Micro F1 | 73.7% |
| Diagnosis F1 | 60.5% |
| Seizure-type F1 | 65.8% |
| Annotated-medication F1 | 92.1% |

Diagnostic evidence metrics:

| Metric | Value |
|---|---:|
| Evidence quote support rate | 92.1% |
| Evidence quote support rate, exact model quotes only | 92.0% |
| Evidence quote support rate, ellipsis repairs only | 100.0% |
| Evidence quote repair rate | 1.1% |
| Evidence offsets present rate | 92.1% |
| Evidence offsets valid rate | 100.0% |

Gold-quality context:

- 28.0% of the capped records carried gold quality flags.
- 8 mismatch rows involved `specificity_collapsed` gold.
- 1 mismatch row involved `missing_gold`.

## Error Read

The capped run produced 29 field-family mismatch rows across 19 documents:

- 14 seizure-type mismatch rows
- 11 diagnosis mismatch rows
- 4 annotated-medication mismatch rows

It also produced 14 evidence-support errors:

- 8 seizure-type evidence errors
- 4 annotated-medication evidence errors
- 2 diagnosis evidence errors

### 1. Label-policy and normalization failures are still the main blocker

Most remaining mismatches are still label-policy or surface-normalization issues rather than broad medication failure:

- Diagnosis specificity or uncertainty leakage:
  - `EA0047`: predicted `probable juvenile myoclonic epilepsy`; gold expects `juvenile myoclonic epilepsy`.
  - `EA0059`: predicted `symptomatic structural epilepsy`; gold expects `symptomatic structural focal epilepsy`.
  - `EA0116`: predicted `... from sleep`; gold expects `... on awakening`.
- Seizure-type surface drift:
  - `EA0061`: predicted `focal to bilateral seizures`; gold expects `focal to bilateral convulsive seizures`.
  - `EA0098`: predicted `focal onset convulsive seizure`; gold expects `focal to bilateral convulsive seizure`.
  - `EA0124`: predicted `absence events`; gold expects a benchmark-facing seizure-type label.
- Rich combined surfaces still bleed across benchmark labels:
  - `EA0090`: one fused seizure phrase is emitted where the gold expects `focal seizures`, `secondary generalisation`, and `generalized tonic clonic seizure` as separate benchmark-facing outputs.

### 2. Evidence-grounding is improved enough that it no longer looks like the main gate

Evidence quality remains worth tracking, but it does not look like the primary failure driver on this cap:

- Overall evidence quote support is 92.1%.
- The new split metrics show only one ellipsis repair in the capped run:
  - `EA0018` annotated medication `levetiracetam`
  - repaired quote: `Currently she is taking sodium valproate 500 mg twice a day and levetiracetam 1000 mg twice today`
- The remaining evidence failures are mostly missing or non-exact quoted support, especially for seizure types:
  - missing evidence: `EA0026`, `EA0029`, `EA0047`, `EA0072`, `EA0125`
  - non-contiguous or header-style quote text: `EA0048`, `EA0068`, `EA0069`, `EA0072`, `EA0098`, `EA0124`

This suggests the narrow ellipsis bridge is behaving as intended and should remain diagnostic bridge behavior, not scorer behavior.

### 3. Medication-scope and gold-limitation failures are narrower than in the first smoke

Annotated-medication F1 reached 92.1%, so medication scope is no longer the main weakness on this slice. The remaining errors are narrow:

- `EA0078`: `levetiracetam` and `carbamazepine` are false positives against a `missing_gold` record, which is consistent with the ExECT audit warning that some letters remain gold-limited.
- `EA0053` and `EA0109`: predicted non-benchmark or likely historical medication mentions (`citalopram`, `carbamazepine`).
- `EA0045`: extra `lamotrigine` prediction likely reflects medication-scope ambiguity rather than broad failure.

### 4. Some errors do point toward architecture or field-family disentangling limits

A smaller subset now looks more architectural than purely prompt-boundary related:

- `EA0068`: diagnosis output drifted into non-diagnosis content (`hydrocephalus`, `infrequent focal seizures`).
- `EA0090`: one rich seizure phrase was used in both diagnosis and seizure-type slots rather than decomposing into benchmark-facing family outputs.
- `EA0109`: `focal seizures` appeared as diagnosis while `temporal lobe seizure` was missed in seizure type.

These failures are consistent with cross-family leakage in a monolithic single-pass extractor and are the clearest evidence in this cap for trying a field-group or section-aware follow-up.

## Interpretation

The cap-25 run changes the risk picture in a useful way:

- Evidence quote support is strong enough that evidence repair is not the next main research bottleneck.
- Medication scope is much less problematic than in the earlier ExECT smoke cycle.
- The dominant remaining failures are benchmark label-policy alignment and seizure-type surface normalization.
- A smaller but real subset of failures now looks like cross-family leakage that a section-aware or field-group architecture could plausibly reduce.

## Recommended Next Pull

The next reasonable chunk after this cap is no longer "fix evidence first." It should be:

1. Design the section-aware versus monolithic ExECT ablation around the current S0/S1 field-family contract.
2. Keep the scorer unchanged and treat architecture as the experimental factor.
3. Carry forward the new evidence split metrics so later reports can separate exact model quotes from deterministic bridge repairs.

## Audit Guidance Used

This read was grounded in `docs/exect_gold_label_audit.md`, especially:

- seizure types must come from audited diagnosis-style labels, not richer clinical paraphrases
- diagnosis specificity and certainty handling matter for benchmark-facing scoring
- medication temporality and missing-gold limitations should be surfaced as caveats, not silently folded into scorer changes

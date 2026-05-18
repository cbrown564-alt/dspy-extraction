# ExECT S0/S1 Baseline Design

Date: 2026-05-18

## Goal

Define the first model-backed ExECT baseline as a combined audited S0/S1 field-family extraction task covering diagnosis, seizure type, and annotated medications only.

This baseline opens the broader ExECT path while keeping benchmark-facing scoring aligned with the current audited loader and `exect_field_family_deterministic_v1` scorer.

## Hypothesis

A benchmark-facing, label-policy-constrained ExECT S0/S1 DSPy program will outperform an unconstrained clinically rich extraction surface on the audited diagnosis, seizure-type, and annotated-medication field families, especially for seizure-type granularity and diagnosis false positives.

## Dataset And Split

- Dataset: `exect_v2`
- Source text: `data/ExECTv2 (2025)/Gold1-200_corrected_spelling`
- Primary gold: per-document JSON annotations under `data/ExECTv2 (2025)/Json`
- Existing split source: `data/splits/exectv2_splits.json`
- Initial run policy: dry run, then capped validation smoke, then full validation only after schema validity and evidence diagnostics are inspected

The test split should remain untouched until an explicit test-reporting config exists.

## Benchmark-Facing Field Families

The first baseline should emit three repeated field families:

| Family | Output field name | Gold source | Normalization/scoring view |
|---|---|---|---|
| Diagnosis | `diagnosis` | JSON `Diagnosis` where `DiagCategory == Epilepsy`, `Negation == Affirmed`, `Certainty >= 4` | `canonical_clinical_phrase`; specificity collapse already applied in gold |
| Seizure type | `seizure_type` | JSON `Diagnosis` where `DiagCategory` is `MultipleSeizures` or `SingleSeizure`, `Negation == Affirmed`, `Certainty >= 4` | `canonical_clinical_phrase`; no seizure-frequency rows as seizure types |
| Annotated medication | `annotated_medication` | JSON `Prescription` entities | `canonical_medication_name`; no benchmark-facing medication temporality |

Do not include investigation, patient history, birth history, aetiology, onset, diagnosis date, seizure frequency, or medication temporality in benchmark-facing metrics for this baseline.

## Output Shape

Use the existing shared artifact contract:

- `PredictionSet.dataset = "exect_v2"`
- `PredictionSet.schema_level = "exect_s0_s1_field_family"`
- `DocumentPrediction.values[*].field_name` in `diagnosis`, `seizure_type`, `annotated_medication`
- each `ExtractedValue` keeps:
  - `raw_value`: source-facing model phrase
  - `normalized_value`: canonical benchmark-facing label when deterministically normalized
  - `evidence`: at least one source quote for present clinical facts
  - `temporality`: `unknown` or `not_applicable` for benchmark-facing metrics unless a later schema level audits temporality
  - `negation`: `affirmed` for emitted benchmark-facing facts
  - `quality_flags`: policy or validation flags such as `unsupported_label`, `inferred_from_diagnosis`, or `missing_evidence`

The first implementation can use a single DSPy module that returns structured JSON lists for the three families, then bridges them into `DocumentPrediction`. A later ablation can split this into family-specific modules.

## Label-Policy Constraints

Diagnosis constraints:

- Allowed benchmark-facing diagnosis labels should initially be constrained to the current canonical diagnosis surface, including `epilepsy`, `focal epilepsy`, `generalized epilepsy`, `juvenile myoclonic epilepsy`, and `status epilepticus` when present in the audited scorer view.
- Do not infer established epilepsy diagnosis from a single seizure event.
- Do not infer epilepsy subtype from seizure-type evidence alone.
- Preserve the gold policy that certainty below 4 is excluded from the flat benchmark-facing diagnosis set.
- Preserve specificity collapse: if `juvenile myoclonic epilepsy` is emitted, do not also emit parent labels unless the scorer contract changes.

Seizure-type constraints:

- Emit the benchmark-facing canonical seizure-type surface, not an unrestricted ILAE-rich surface.
- Map focal-aware, focal impaired-awareness, focal with altered-awareness, and similar finer mentions to the canonical scorer label expected by `canonical_clinical_phrase` only through an explicit, tested normalization path.
- Do not infer seizure type from diagnosis alone.
- Do not treat secondary generalisation as a separate current seizure type unless it is independently named as a seizure type in the text.
- Do not source seizure types from seizure-frequency rows.

Medication constraints:

- Emit medications only when they are annotated prescription-style mentions under the current S0/S1 scorer view.
- Normalize brand/spelling variants through the existing medication normalizer.
- Do not score current, planned, stopped, previous, refused, or adverse-effect status as benchmark-facing medication labels in this baseline.
- Preserve raw medication text separately from canonical names so later medication-temporality work can audit disagreements.

## Context And Evidence Strategy

The baseline should start with full-note input for capped experiments because ExECT letters are short enough for the initial closed-provider path. The prompt should still ask the model to quote exact contiguous source text for every emitted diagnosis, seizure type, and medication.

Evidence diagnostics should report source-quote support separately from benchmark-facing label metrics. A label can be correct while evidence is missing or unsupported, and unsupported evidence should not silently alter field-family precision/recall.

Section-aware or context-then-extract modules should be a named later ablation, not part of this first baseline.

## Scorer And Report

Use `exect_field_family_deterministic_v1`.

The first report should include:

- dataset and split
- model/provider and model config path
- schema level: `exect_s0_s1_field_family`
- program variant
- prompt version and constrained label policy
- scorer mode and normalization rules
- micro precision, recall, and F1 across the three field families
- per-family precision, recall, F1, and support
- schema-valid prediction rate
- evidence quote support diagnostics
- documents with gold quality flags, especially `missing_gold` and `specificity_collapsed`
- bounded error samples grouped by diagnosis, seizure type, medication, schema validity, evidence support, and label-policy failure

The report must state that these metrics are partial ExECT S0/S1 diagnostics, not published ExECTv2 benchmark reproduction.

## Initial Implementation Cards

1. Add an ExECT S0/S1 DSPy signature and module with constrained output lists for diagnosis, seizure type, and annotated medication.
2. Add an artifact bridge from module output into the shared `PredictionSet` schema.
3. Add config validation for an `exect_s0_s1_field_family` experiment using a capped validation split.
4. Add mocked-LM tests for null lists, diagnosis specificity, seizure-type granularity, no seizure-type inference from diagnosis, medication alias normalization, and evidence spans.
5. Add a capped GPT 4.1-mini validation smoke run; inspect artifacts before scaling.

## Known Risks

- The existing ExECT scorer does not yet expose schema-validity or evidence-support metrics as richly as the Gan evaluator.
- Empty-list/null behavior should be explicitly tested before reporting diagnosis exact-match-style metrics.
- Medication temporality is clinically important but remains excluded from benchmark-facing metrics because the audited prescription gold does not reliably encode it.
- Clinically rich labels may be reasonable but should not be scored against this benchmark-facing view without a tested bridge.

# Deterministic Scorer Semantics

Date: 2026-05-17

This note fixes the current deterministic gold-source, normalization, and scorer meanings before DSPy programs or model calls are added.

## ExECTv2

Gold source:

- Primary structured gold is the per-document JSON under `data/ExECTv2 (2025)/Json`.
- Source letters are loaded from `data/ExECTv2 (2025)/Gold1-200_corrected_spelling`.
- BRAT `.ann` files and Markup CSVs are retained as references, but are not the current primary diagnosis, seizure-type, or prescription source.

Current scoring view:

- Diagnosis rows are included only when `entity == "Diagnosis"`, `Negation == "Affirmed"`, and `Certainty >= 4`.
- Epilepsy diagnoses use `DiagCategory == "Epilepsy"`.
- Seizure types use `DiagCategory` values `MultipleSeizures` and `SingleSeizure`; seizure frequency rows are not used as a seizure-type registry.
- Prescription rows are loaded from JSON `Prescription` entities. The loader prefers `CUIPhrase` and falls back to `DrugName` or span text.
- Raw diagnoses are preserved in `raw_diagnoses`; the canonical `diagnoses` scoring view collapses generic parent diagnoses when a more specific descendant is present.

Normalization:

- Clinical phrases are lowercased, hyphen/underscore separated, CamelCase split, and whitespace collapsed.
- British `generalised` normalizes to `generalized`.
- Known spelling noise such as `tonic chronic` normalizes to `tonic clonic`.
- Medication aliases include common brand and spelling variants such as `Keppra -> levetiracetam`, `Epilim -> sodium valproate`, `SodiumValproate -> sodium valproate`, and `EslicarbazepineAcetate -> eslicarbazepine`.

Quality flags:

- `missing_gold`: no diagnosis, seizure type, or medication remains after loading.
- `gold_noise`: generic seizure terms such as `seizure` or `seizures` appear in the seizure-type view.
- `specificity_collapsed`: one or more generic diagnoses were removed from the benchmark-facing diagnosis view.

Benchmark-facing metrics should use the canonical scoring views. Raw annotations, raw diagnoses, and quality flags are diagnostic context and should be reported separately.

## Gan 2026

Gold source:

- Primary gold is `check__Seizure Frequency Number.seizure_frequency_number[0]` from `data/Gan (2026)/synthetic_data_subset_1500.json`.
- `reference[0]` is a secondary cross-check and difficulty signal, not benchmark gold.
- `label_reference_disagreement` and `hard_case` flag records where primary gold differs from the secondary reference label.

Normalization:

- Labels are lowercased and whitespace collapsed.
- Plural time units normalize to singular units.
- `multiple` maps to `3`.
- Numeric ranges map to their midpoint.
- Rates convert to seizures per month using day `30.0`, week `4.33`, month `1.0`, and year `1/12`.
- Cluster labels convert as `(clusters per month) * (seizures per cluster)`.
- `unknown` and `unknown, ... per cluster` map to `1000.0`.
- `no seizure frequency reference` and seizure-free labels map to `0.0`.

Benchmark-facing metrics:

- Monthly-frequency match compares deterministic seizures-per-month values.
- Purist category match uses the multi-bin Gan/Holgate category view.
- Pragmatic category match uses `infrequent`, `frequent`, `unknown`, and `no_seizure_information`.

Diagnostic metrics:

- Raw string exact match should remain diagnostic only.
- Normalized-label exact match is stricter than monthly-frequency or category matching and should be interpreted as a format-fidelity diagnostic unless an experiment explicitly targets label-scheme reproduction.
- Reference-label agreement is a difficulty/audit feature, not a gold-label alternative.

## Split And Reporting Caveats

- `data/splits/gan_2026_splits.json` is deterministic and salted with `gan-2026-fixed-splits-v1`.
- Gan split stratification includes pragmatic category, purist category, `row_ok`, and label-reference disagreement.
- Experiment reports should state dataset, split name, scorer mode, and whether metrics are benchmark-facing or diagnostic.

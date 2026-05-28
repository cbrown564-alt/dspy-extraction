# Published Benchmark Metrics And Alignment

Date: 2026-05-17
Last updated: 2026-05-28 for project-scorer versus published-benchmark distinction

This note records the published benchmark values and metric definitions that are relevant to this repo. Code-level references live in `clinical_extraction.evaluation.benchmarks`, but those constants are comparison aids only: they carry alignment labels and caveats, and must not be used to claim published benchmark reproduction unless the relevant scorer and dataset caveats are resolved.

## Local Sources

- ExECTv2 paper: `data/ExECTv2 (2025)/Annotation of Epilepsy Clinic Letters for NLP (Fonferko-Shadrach 2024).pdf`
- ExECTv2 annotation guideline: `data/ExECTv2 (2025)/ExECT V2 .1- What and How of annotating_v9.docx`
- Gan paper: `data/Gan (2026)/Synthetic Clinical Letters for Seizure Frequency.pdf`
- Current repo scorer note: `docs/policies/deterministic_scorer_semantics.md`
- Dataset audits: `docs/datasets/exect/exect_gold_label_audit.md`, `docs/datasets/gan/gan_2026_label_audit.md`

## ExECTv2

Published metric definition:

- The ExECTv2 paper reports F1, defined as the harmonic mean of precision and recall.
- Scores are reported per item, meaning every entity mention, and per letter, meaning at least one correct extraction of the entity with features in a letter.
- The validation comparator is the ExECTv2 pipeline against the consensus gold standard.
- For diagnosis per-letter validation, the paper uses epilepsy or multiple-seizure annotations with certainty level 4 or 5 and CUI matching; the paper also reports that ignoring epilepsy/seizure type detail gives F1 0.99.

Published values from Table 1:

| Annotation | Gold annotations | ExECTv2 per-item F1 | ExECTv2 per-letter F1 | Human IAA F1 |
|---|---:|---:|---:|---:|
| Birth History | 47 | 0.97 | 0.98 | 0.69 |
| Diagnosis | 572 | 0.85 | 0.94 | 0.83 |
| Epilepsy Cause | 36 | 0.90 | 0.92 | 0.67 |
| Investigations | 183 | 0.95 | 0.95 | 0.82 |
| Onset | 22 | 0.96 | 0.95 | 0.61 |
| Patient History | 620 | 0.78 | 0.89 | 0.57 |
| Prescription | 290 | 0.87 | 0.87 | 0.87 |
| Seizure Frequency | 260 | 0.66 | 0.68 | 0.47 |
| When Diagnosed | 17 | 0.91 | 0.91 | 0.45 |
| All | 2047 | 0.87 | 0.90 | 0.73 |

Current repo alignment:

- The repo now has project field-family scorers for S1-S4 and the S5 core surface, as documented in `docs/policies/deterministic_scorer_semantics.md`.
- These project scorers are not direct ExECTv2 Table 1 reproduction. They use normalized project label views and selected field-family surfaces rather than full CUI-plus-feature matching across every paper annotation family.
- The strongest audited alignment remains the S1 core families: diagnosis, seizure type, and annotated medication. Later family scorers are useful project diagnostics and stacked-surface metrics, but each needs its own benchmark-contract caveat.
- The repo deliberately excludes planned/current medication status from benchmark-facing S5 medication scoring until reliable temporality gold exists.
- Investigation, patient history/comorbidity, birth history, aetiology, onset, diagnosis-date, and seizure-frequency are no longer "not implemented" for project scoring, but they remain not sufficient for published ExECTv2 reproduction until CUI-aware, feature-aware Table 1 scoring is implemented.

## Gan 2026

Published metric definition:

- Gan et al. evaluate seizure-frequency outputs under Purist and Pragmatic category schemes.
- All output formats are aligned to a common seizure-frequency representation before evaluation.
- The paper reports micro, macro, and weighted F1, and treats micro-F1 as the primary comparison metric because Purist classes are imbalanced.
- Decoding temperature is set to 0 for evaluation.

Published values:

- Abstract headline: representative models trained on fully synthetic letters generalize to real clinic letters with micro-F1 up to 0.788 under the fine-grained Purist scheme and 0.847 under the Pragmatic scheme.
- Table 6, synthetic-only 1,797-letter training evaluated on Real(300): best reported Purist micro-F1 is 0.776 for Qwen2.5-14B with `Our COT`; best reported Pragmatic micro-F1 is 0.832 for Qwen2.5-14B with `Our COT` and Qwen2.5-7B with `Our label`.
- Table 7, training-set comparison: real-plus-synthetic training reaches Pragmatic micro-F1 up to 0.889 on the Synthetic(1,166) evaluation set for Qwen2.5-14B with `R+S(x per M)`, but those values are not the main real-letter benchmark.
- Table 8, synthetic CoT scaling: Qwen2.5-14B with `COT(15000)` reaches Purist micro-F1 0.788 and Pragmatic micro-F1 0.847 on Real(300), matching the abstract headline.

Current repo alignment:

- Scorer alignment now has two explicit modes. `gan2026_paper_reproduction` is
  the primary mode for direct Gan 2026 comparisons because it ports the
  author-provided evaluator supplied on 2026-05-27. `gan_frequency_deterministic_v1`
  remains a canonical clinical/project diagnostic scorer.
- Not directly comparable to the published real-letter benchmarks because the repo currently loads `synthetic_data_subset_1500.json`, not the Real(300) or Real(150) clinician-annotated evaluation sets.
- The repo reports category accuracy for deterministic stored predictions, not micro-F1 across model-predicted category labels. For single-label multiclass classification these can coincide when every evaluated record has exactly one valid prediction, but reports should not claim equivalence unless that condition is explicit.
- Evidence diagnostics in this repo are separate from benchmark-facing frequency/category metrics; the paper treats evidence-grounded outputs as clinically useful, but the benchmark tables above are frequency classification F1.

## Reproduction Implications

- ExECTv2 reproduction needs CUI/feature-aware scoring across all Table 1 annotation families before comparing to the published `All` F1 values.
- Gan reproduction needs the paper's real-letter evaluation sets or a clear statement that a synthetic-only subset is being used, and direct comparisons must use `gan2026_paper_reproduction` with its repair/range/tolerance options reported.
- Future reports should cite scorer mode, dataset split, schema level, and whether they are benchmark-aligned, partially aligned, or diagnostic-only.
- `clinical_extraction.evaluation.benchmarks` may be used to attach reference values and caveats to reports. Values labeled `partial` or `not_comparable` are not reproduction claims.

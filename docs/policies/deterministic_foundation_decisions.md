# Deterministic Foundation Decisions

Date: 2026-05-17

This note records the decisions from the `grill-with-docs` planning pass before implementing the first deterministic milestone.

## Scope

The first milestone will build deterministic infrastructure before any DSPy modules or model calls. The goal is to make dataset loading, gold-label representation, normalization, splitting, and scoring auditable before LLM behavior is introduced.

## Decisions

1. Use `clinical_extraction` as the Python package name.
2. Scaffold a minimal modern Python project with `pyproject.toml`, `pytest`, and `pydantic`.
3. Keep model/provider configuration minimal for now; do not implement LLM adapters in this milestone.
4. Treat ExECTv2 per-document JSON files as the primary structured gold source.
5. Load ExECTv2 `.txt` letters as source text and retain ExECT seizure-frequency CSV use only for future frequency-specific work.
6. Preserve raw ExECT diagnosis annotations, but expose a canonical scoring view that collapses generic diagnosis parents when a more specific diagnosis is present.
7. Record ExECT gold-quality flags such as `missing_gold`, `gold_noise`, and `specificity_collapsed`.
8. Treat Gan `check__Seizure Frequency Number.seizure_frequency_number[0]` as canonical gold.
9. Treat Gan `reference[0]` as a secondary cross-check and difficulty signal, not as gold.
10. Implement Gan label normalization and deterministic conversion to seizures/month before benchmark-facing scoring.
11. Expose Gan exact normalized-label matching, numeric seizures/month comparison, Purist category, and Pragmatic category semantics; keep raw exact string match as diagnostic only.
12. Generate a reproducible `data/splits/gan_2026_splits.json` with fixed salt and stratification metadata.
13. Include focused regression tests from the audits before adding DSPy modules.

## Audit Guidance Used

- `docs/datasets/exect/exect_gold_label_audit.md`: JSON primary source, certainty threshold, seizure types from `Diagnosis` rows, diagnosis specificity collapse, and warning flags.
- `docs/datasets/gan/gan_2026_label_audit.md`: Gan gold source, reference as cross-check, plural unit normalization, year/month equivalence, cluster conversion, hard-case flags, and special labels.
- [AGENTS.md](file:///c:/Users/cbrow/Code/dspy-extraction/AGENTS.md): deterministic loaders, validators, normalizers, and scorers around LLM components; no silent scorer semantic changes.

## Deferred

- DSPy modules, optimizers, and LLM provider adapters.
- Full model matrix configuration.
- ExECT seizure-frequency scoring.
- Excel parsing for Gan real-letter annotation examples.

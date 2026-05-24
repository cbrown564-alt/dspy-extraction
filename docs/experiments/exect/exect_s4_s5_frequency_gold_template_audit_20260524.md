# ExECT S4/S5 Frequency Gold-Template Audit

Date: 2026-05-24
Status: Completed no-model audit
Kanban card: `S4/S5 frequency gold-template audit`
Decision scope: pre-arm gate for ExECT S5/S4 frequency work

## Question

Can deterministic, note-anchored candidate surfaces represent ExECT validation
gold for the S4/S5 `seizure_frequency` family before spending on
candidate-adjudication or structured-slot model arms?

## Sources And Method

Primary sources:

- `docs/planning/kanban_plan.md`
- `docs/datasets/exect/exect_gold_label_audit.md`
- `docs/experiments/exect/exect_s4_gold_policy.md`
- `docs/experiments/exect/exect_s5_core_surface_design_20260524.md`
- `src/clinical_extraction/datasets/exect.py`
- `src/clinical_extraction/exect/primitives.py`
- `data/splits/exectv2_splits.json`

The audit used `load_exect_gold_documents()` to collect normalized
`seizure_frequencies` and `build_exect_frequency_candidate_payloads()` to
collect current deterministic note-anchored candidates. No model calls were
made.

The Cursor SDK was used as a review-only audit assistant first:
`docs/workstreams/cursor_sdk/archive/experiments_cursor_sdk_drafts/20260524T083058Z_inspection_draft.md`.
That SDK draft supplied a checklist and taxonomy, but it is not used as
benchmark evidence. The primary deterministic output was written to the ignored
local artifact:
`artifacts/audits/exect_s4_s5_frequency_gold_template_audit_20260524.json`.

## Validation Results

| Measure | Value |
| --- | ---: |
| Validation documents | 40 |
| Documents with frequency gold | 24 |
| Gold frequency labels | 43 |
| Candidate labels emitted | 11 |
| Matched gold labels | 5 |
| Missed gold labels | 38 |
| Extra candidate labels | 6 |
| Gold-label coverage | 11.6% |
| Candidate precision vs gold | 45.5% |
| Gold docs with all labels covered | 2 / 24 |

Coverage by gold-template type:

| Template type | Gold labels | Matched | Coverage |
| --- | ---: | ---: | ---: |
| Quantified rate | 15 | 1 | 6.7% |
| Qualitative change | 11 | 2 | 18.2% |
| Seizure free | 9 | 2 | 22.2% |
| Zero rate | 7 | 0 | 0.0% |
| Other qualitative | 1 | 0 | 0.0% |

The corpus-level result is similar: 34 / 207 gold labels covered (16.4%) and
15 / 129 gold-bearing documents fully covered. This is not a validation-only
accident.

## Missed-Template Taxonomy

Validation misses:

| Code | Definition | Count |
| --- | --- | ---: |
| `M3` | Gold present, current note parser emits no frequency candidate | 28 |
| `M1_quantified` | Quantified gold surface not detected from note prose | 6 |
| `M1_qualitative` | Qualitative gold cue not detected | 2 |
| `M1_seizure_free_or_zero_rate` | Seizure-free or zero-rate surface not detected | 1 |
| `M6_quantified_near_miss` | Candidate catches a nearby rate but misses another gold rate | 1 |

The dominant failure is not that the gold label is structurally impossible. It
is that the current deterministic note parser often fails to recover
annotation-derived templates from natural note phrasing. Examples include
abbreviated or section-list formats such as "weekly", "1 since previous
appointment", zero-rate year windows, and type-specific seizure-free history.

Validation extra candidates:

| Code | Definition | Count |
| --- | --- | ---: |
| `X2` | Candidate seizure-free / zero-rate label absent from gold | 3 |
| `X3` | Candidate quantified-rate label absent from gold | 2 |
| `X1` | Candidate qualitative label absent from gold | 1 |

The extra-candidate cases matter because a pre-vocab or post-merge arm could
trade recall attempts for false positives if candidates are promoted directly.
EA0008 is a useful warning: note prose contains "period of seizure freedom",
so the candidate primitive emits `seizure free`, while validation gold is
`1 per 3 week` plus `frequency increased`.

## Unmapped JSON Rows

Four validation `SeizureFrequency` JSON rows normalize to no scored gold label:

| Document | Span text | Attributes summary |
| --- | --- | --- |
| EA0050 | `generalised-tonic-clonic-seizures` | `NumberOfSeizures=1`, `PointInTime=LastClinic`, `Since` |
| EA0072 | `focal-motor-seizure` | `NumberOfSeizures=1`, `PointInTime=LastClinic`, `Since` |
| EA0090 | `generalised-tonic-clonic-seizur` | `NumberOfSeizures=1`, `PointInTime=Birthday`, `Since` |
| EA0098 | `seizur` | `NumberOfSeizures=1`, `MonthDate=9`, `During` |

These rows confirm the S4 gold policy caveat: some annotation rows carry
temporal information but do not map to benchmark labels because they lack the
count-period fields or qualitative-change field required by
`canonical_seizure_frequency_label()`.

## Evidence Availability

All 43 validation gold labels have at least one JSON span because every scored
label comes from a `SeizureFrequency` annotation. Only the 5 matched labels
have current candidate spans. Therefore candidate-span availability is exactly
11.6% on validation under the current deterministic candidate primitive.

This should not be read as evidence quality for model predictions. It is a
representability diagnostic: the candidate generator cannot yet provide
candidate evidence for most validation gold labels.

## Representative Validation Cases

| Document | Gold | Candidates | Read |
| --- | --- | --- | --- |
| EA0008 | `1 per 3 week`, `frequency increased` | `seizure free` | Current parser misses section frequency and returned-seizure cue, while adding historical seizure freedom. |
| EA0050 | `1 per 1 week`, `frequency decreased`, `infrequent` | none | Section-list phrasing such as "weekly" and "since previous appointment" is not represented. |
| EA0059 | `infrequent`, `seizure free since 2015`, `seizure free since 2017` | none | Multi-type historical seizure-free annotations are not recovered from note text. |
| EA0136 | `0 per 3 year`, `0 per 5 year`, `frequency same` | none | Zero-rate windows and `frequency same` are outside current candidate support. |
| EA0142 | `seizure free` | `3 per 1 month`, `seizure free` | Full gold coverage, but with one extra candidate. |
| EA0188 | `1 per 1 day`, `1 per 1 month` | `1 per 1 day` | Parser recovers current daily rate but misses secondary generalized monthly rate. |

## Interpretation

Current deterministic note-anchored candidates are not sufficient as the S5/S4
frequency graph input. They cover only 11.6% of validation gold labels and fully
cover only 2 of 24 validation documents with frequency gold.

The result argues against launching an S5 Axis 1 / Axis 2 grid that depends on
the current frequency candidate primitive as a recall-preserving pre-stage. It
also argues against treating post-merge note anchoring as a safe scorer-facing
repair without more targeted parser work.

The next useful work is E6-style deterministic implementation iteration before
E5 model-grid spend. The high-value parser gaps are:

- section-list rates such as "weekly", "monthly", and "1 since previous appointment"
- zero-rate windows such as `0 per N year`
- qualitative `frequency same`
- multi-type frequency blocks with separate current and historical rates
- guardrails for historical seizure-free prose that is not benchmark gold

## Scorer Caveats

- S4 and S5 use the same ExECT annotation-facing frequency labels.
- No scorer, loader, normalization, or S5 semantics changed during this audit.
- `seizure_frequency` remains separate from `seizure_type`; frequency rows must
  not be used as seizure-type gold.
- Gan monthly-frequency normalization does not transfer to ExECT.
- S5 pooled micro is not comparable to S1-S4 pooled micro without stating the
  family set.
- Test split remains holdout; primary decision here is validation-only.

## Decision

Status: **complete / hold E5 / pull E6**

Do not start the ExECT S5 Axis 1 / Axis 2 model grid on the current frequency
candidate primitive. Pull a narrow deterministic frequency candidate iteration
first, with validation gates on gold coverage and extra-candidate rate. After
candidate recall improves, rerun this audit before promoting a model-backed S5
frequency arm.

# ExECT S4 Gold Policy — Seizure Frequency and Medication Temporality

Date: 2026-05-20

## Scope

Phase 1 adds two JSON-backed field families to `load_exect_gold_document` and
`exect_s4_field_family_deterministic_v1`, extending frozen **S3 v1.2** (nine families) without
changing S1–S3 loader semantics for existing families.

| JSON entity | Field family | Benchmark label shape |
| --- | --- | --- |
| `SeizureFrequency` | `seizure_frequency` | Canonical frequency strings (see below) |
| `Prescription` | `medication_temporality` | `{medication}\|{current\|planned\|previous}` |

Program work (`exect_s4.py`, smoke/cap-25/full configs) is **out of scope** for this document;
see `docs/exect_s2_s4_schema_ladder_design.md` and `docs/kanban_plan.md` Thread E.

## Audit basis

- `docs/exect_gold_label_audit.md` — Bug 1 (frequency ≠ seizure type), Bug 2 (no Rx temporality column), Q4 (multi-type frequency)
- `docs/exect_s3_phase1_overlap_policy.md` — independent per-family scoring when phrases overlap
- Frozen baselines: S2 v1.3 `…231223Z`, S3 v1.2 `…235439Z`

## Seizure frequency

### Source

All `SeizureFrequency` JSON entities for the document. Unlike early loader bugs, these rows are
**not** used as seizure-type gold (`seizure_type` remains `Diagnosis` with
`MultipleSeizures` / `SingleSeizure` only).

### Normalization rules (`canonical_seizure_frequency_label`)

1. **Seizure-free** — `CUIPhrase` is `seizure-free`, or `NumberOfSeizures == 0` with CUIPhrase
   `seizure` / `seizures` / `seizure-free`:
   - `seizure free`
   - `seizure free since {YearDate}` when `YearDate` is present
   - `seizure free since {year}` when `NumberOfSeizures == 0` and `YearDate` is set (type-specific
     resolved frequency, e.g. EA0011 convulsive type since 2017)

2. **Frequency change (qualitative)** — non-null `FrequencyChange`:
   - `Increased` → `frequency increased`
   - `Decreased` → `frequency decreased`
   - `Infrequent` → `infrequent`
   - Other values → `frequency {normalized phrase}`

3. **Quantified rate** — `NumberOfTimePeriods` and `TimePeriod` present:
   - `{NumberOfSeizures or 1} per {NumberOfTimePeriods} {period}` with period lowercased and
     `generalised` → `generalized` (e.g. `1 per 3 week`, `1 per 2 month`)

4. **Unmapped** — entities that do not match the above return no label (not scored as gold).

Rows with only a seizure-type CUIPhrase and no quantified period (e.g. `During` without counts) are
excluded until a policy is added.

### Multi-row documents

All normalized labels are retained and deduplicated. Set-based field-family F1 allows multiple gold
values per document (e.g. EA0008: `1 per 3 week` + `frequency increased`).

**Extraction policy (planned S4 program):** prefer the clinically current quantified rate when
multiple types exist (audit Q4 simple approach). Gold lists all annotated surfaces until a
primary-frequency selection rule is validated on error reads.

### Overlap with `seizure_type`

`SeizureFrequency` CUIPhrases often match seizure-type wording. Families are scored independently;
duplicate predictions across families are expected until prompt policy is defined.

## Medication temporality

### Source and limitation

JSON `Prescription` entities only. The markup has **no temporality column** (audit Bug 2).
Medications mentioned in letters but not tagged as `Prescription` (e.g. planned levetiracetam on
EA0008) are **absent from gold**, not false negatives.

### Label shape

`format_medication_temporality_label(medication, temporality)` → `{canonical_medication}|{status}`

Medication names use the same `canonical_medication_name` / CUIPhrase preference as S1–S3
`annotated_medication`.

### Temporality inference (`infer_prescription_temporality`)

Applied to the prescription **span text** only (conservative, auditable):

| Status | Span cues |
| --- | --- |
| `current` | Default; also when span contains `current anti`, `current-antiepileptic`, or `current medication` |
| `previous` | `previously`, `had been on`, `had been taking`, `stopped`, `discontinued`, `weaned` |
| `planned` | `to start`, `plan to start`, `will start`, `due to start`, `commence` |

**Explicitly remain `current`:** dose-change wording on an existing prescription (`to reduce`,
`to increase`, `as detailed below`) — aligned with frozen S1 label-policy v4.x.

### Overlap with `annotated_medication`

Every prescription still populates `current_medications` (name only). `medication_temporality`
adds status. A prediction of `lamotrigine` alone does not match `lamotrigine|current`.

## Scorer

- Mode: `exect_s4_field_family_deterministic_v1`
- Families: S3 nine + `seizure_frequency` + `medication_temporality` (11 total)
- Micro F1 across 11 families is **not** comparable to S3 nine-family or S2 five-family headlines
- Report per-family F1 and frozen-family regression on each gate

## Corpus coverage (200 letters, Phase 1 loader)

| Entity | JSON rows | Documents with ≥1 label |
| --- | ---: | ---: |
| `SeizureFrequency` | 263 | (varies; multiple rows per document common) |
| `Prescription` | 294 | same as `current_medications` coverage |

Most prescription spans infer as `current`; `planned` / `previous` are rare in tagged spans.

## Regression guards

- `load_exect_gold_document` must preserve S1–S3 family outputs unchanged
- S3 frozen configs and scorer semantics are not modified
- Do not compare 11-family micro F1 to S3/S2/S1 pooled headlines without caveat

## Deferred (not Phase 1)

- Per-type frequency linked to `seizure_type` by CUI (audit Q4 complex schema)
- Temporality challenge set integration for planned/previous gold beyond JSON spans
- CUI-aware Table 1 reproduction scorer
- Gan-style monthly numeric normalization (ExECT labels are annotation surfaces, not Gan ordinals)

## References

- `docs/exect_s2_s4_schema_ladder_design.md`
- `docs/deterministic_scorer_semantics.md`
- `tests/test_exect_s4_gold_loader.py`, `tests/test_exect_s4_scoring.py`

# ExECT S3 Phase 1 — Gold Overlap Policy

Date: 2026-05-20

## Scope

Phase 1 adds four JSON entity families to `load_exect_gold_document` and `exect_s3_field_family_deterministic_v1`:

| JSON entity | Field family | Gold source |
| --- | --- | --- |
| `BirthHistory` | `birth_history` | Affirmed CUIPhrase (certainty ≥ 4) |
| `Onset` | `onset` | Affirmed CUIPhrase (certainty ≥ 4) |
| `EpilepsyCause` | `epilepsy_cause` | Affirmed CUIPhrase (certainty ≥ 4) |
| `WhenDiagnosed` | `when_diagnosed` | Affirmed CUIPhrase (certainty ≥ 4) |

Labels are `canonical_clinical_phrase` surfaces (hyphens → spaces, `generalised` → `generalized`). Age, year, and `TimePeriod` attributes are **not** benchmark labels in Phase 1.

## Overlap rules

### Cause vs comorbidity

`EpilepsyCause` and affirmed `PatientHistory` are **independent gold sources**. When both annotate the same phrase (for example `meningitis` on EA0058), each family receives the label. The scorer does not deduplicate across families.

**Extraction policy (planned S3 program):** prefer `epilepsy_cause` for aetiology framing and `comorbidity` for ongoing comorbid history; both may appear when the note supports each audited surface.

### Birth history vs epilepsy cause

Phrases such as `perinatal insult` may appear under both `BirthHistory` and `EpilepsyCause` in gold (for example EA0010). Each entity type is scored in its own family.

### Onset / when diagnosed vs diagnosis

`Onset` and `WhenDiagnosed` often use CUIPhrase `epilepsy`, overlapping `Diagnosis` gold. Families are scored independently. Duplicate predictions across `diagnosis` and `onset` are expected extraction noise until prompt policy is defined.

### Onset vs seizure type

Some `Onset` rows use seizure-type CUIPhrases (for example `generalized tonic clonic seizures` on EA0029). These remain in `onset` gold when annotated as `Onset`; they are not moved to `seizure_type` unless also annotated under `Diagnosis` / `MultipleSeizures`.

## Corpus coverage (200 letters)

| Entity | Annotated rows (JSON) | Documents with ≥1 label (affirmed, certainty ≥ 4) |
| --- | ---: | ---: |
| `BirthHistory` | 47 | 36 |
| `EpilepsyCause` | 36 | 27 |
| `Onset` | 24 | 19 |
| `WhenDiagnosed` | 17 | 17 |

## Regression guards

- `load_exect_gold_document` must preserve existing S1/S2 family outputs unchanged.
- S2 frozen configs and scorer semantics are not modified by Phase 1.
- Pooled micro F1 across 9 families is not comparable to S2-only (5 family) headlines.

## References

- `docs/exect_s2_s4_schema_ladder_design.md`
- `docs/exect_gold_label_audit.md` — entity inventory
- `docs/kanban_plan.md` — Thread D

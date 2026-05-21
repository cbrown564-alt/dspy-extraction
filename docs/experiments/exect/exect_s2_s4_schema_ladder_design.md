# ExECT S2→S4 Schema Ladder

Date: 2026-05-20

## Decision

Proceed with the **schema ladder** from frozen **S2 v1.3** (`runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z`) toward **S4**, per `docs/outline.md`. Do **not** reopen S1 bridges or S2 comorbidity micro-iteration on the validation split unless a ladder step regresses a frozen family.

## Frozen baselines

| Level | Status | Program / prompt | Full validation anchor (40) |
| --- | --- | --- | --- |
| S1 | Frozen | `exect_s0_s1` v4.10 | `…221944Z` — 92.3% micro (3 fam) |
| **S2** | **Frozen** | `exect_s2` v1.3 | `…231223Z` — **80.9%** micro (5 fam); comorbidity 69.3% |
| **S3** | **Frozen** | v1.2 `…235439Z` | 72.1% micro (9 fam); comorbidity gap vs S2 accepted |
| S4 | Planned | TBD | — |

Cap-25 v1.3 (`…230945Z`): 87.5% micro, comorbidity 85.7% — gate only.

## Schema levels (`docs/outline.md`)

| Level | Scope | ExECT JSON / audit basis |
| --- | --- | --- |
| **S0** | Core diagnostic fields | Done (early ExECT) |
| **S1** | Diagnosis + seizure + medication | Frozen v4.10 |
| **S2** | S1 + investigation + comorbidity | Frozen v1.3 — `docs/experiments/exect/exect_s2_field_expansion_design.md` |
| **S3** | S2 + birth / development / family / social / driving / pregnancy | **Phase 1:** auditable JSON entities; **Phase 2:** outline fields without dedicated gold |
| **S4** | Full ExECTv2-like schema | Seizure frequency, rich prescriptions, CUI-level reproduction — `docs/datasets/exect/exect_gold_label_audit.md` |

## S3 — auditable gold first (Phase 1)

Corpus entity counts (200 letters, JSON):

| Entity | Rows | Proposed field family | Notes |
| --- | ---: | --- | --- |
| `BirthHistory` | 47 | `birth_history` | Affirmed CUIPhrase surfaces (`born-normally`, `perinatal-insult`, …) |
| `Onset` | 24 | `onset` | Often overlaps `epilepsy` diagnosis wording — audit before scorer |
| `EpilepsyCause` | 36 | `epilepsy_cause` | Aetiology phrases; overlap with comorbidity (`meningitis`) — policy: cause vs history |
| `WhenDiagnosed` | 17 | `when_diagnosed` | Mostly `epilepsy` CUIPhrase — may be low signal; confirm utility |
| *(outline)* family / social / driving / pregnancy | — | deferred Phase 2 | No dedicated JSON entities; sparse PatientHistory keywords — spike before gold |

**Hypothesis:** Extend the S2 monolithic label-policy pass with S3 field families using the same pattern: deterministic loader → partial scorer → `exect_s3.py` reusing frozen S1+S2 bridges without editing `exect_s0_s1.py` / `exect_s2.py`.

**Do not:** mix S3 fields into S2 prompt version bumps; new `schema_level` + `exect_s3_field_family_*` contract.

## S4 — full schema (Phase 3+)

Targets after S3 baseline:

- `SeizureFrequency` (263 JSON rows) — quantified / qualitative frequency; separate normalization from Gan but shared audit discipline
- Prescription temporality (current vs planned) — JSON has no temporality column; align with audit §Bug 2
- CUI-aware or annotation-reproduction probe — `docs/datasets/exect/exect_gold_label_audit.md` “complex schema approach”
- Not Table 1 reproduction until CUI-aware all-family scorer exists (Kanban blocked card)

## Implementation sequence

```text
S2 frozen (v1.3)
    → S3 Phase 1: loader + scorer + tests (4 JSON families)  [done 2026-05-20]
    → S3 frozen v1.2 (…235439Z)  [done 2026-05-20]
    → S4 gold policy + Phase 1 scaffold  [done 2026-05-20]
    → S4 program + smoke/cap-25/full
    → S3 Phase 2 spike: outline-only fields (family/social/driving/pregnancy) [deferred]
```

## Experiment naming (planned)

| Config | Purpose |
| --- | --- |
| `exect_s3_smoke_gpt4_1_mini.json` | 3-record contract |
| `exect_s3_validation_cap25_gpt4_1_mini.json` | 25-record gate |
| `exect_s3_validation_full_gpt4_1_mini.json` | 40-record read |

Model: GPT 4.1-mini (hosted breadth track). Scorer: `exect_s3_field_family_deterministic_v1` (TBD families).

## Regression guards

- S2 regression slice: existing `tests/test_exect_s2_*` + frozen configs unchanged
- S1 regression: `data/fixtures/exect_s0_label_policy_error_regression_slice.json` when touching shared loaders only
- Any change to `load_exect_gold_document` must preserve S2 family outputs (dataset-audit-first)

## Metric caveats

- Pooled micro F1 across expanding families is **not** comparable to S2-only or S1-only headlines
- Report **per-family F1** and frozen-family regression (S1 + S2 families) on each S3/S4 gate
- Cap-25 remains optimistic vs full (~7–9pp on S1 precedent)

## References

- `docs/outline.md` — schema level definitions
- `docs/datasets/exect/exect_gold_label_audit.md` — entity sources, seizure-frequency warning
- `docs/experiments/exect/exect_s2_label_policy_v1_3_implementation.md` — S2 freeze artifact
- `docs/planning/kanban_plan.md` — Thread D active work

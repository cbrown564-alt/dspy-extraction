# ExECT S2 Field Expansion Design

Date: 2026-05-19

## Goal

Pivot ExECT breadth from frozen S1 (v4.10) to Schema S2: extend the monolithic label-policy program with **investigation** and **comorbidity** field families while reusing S1 deterministic bridges unchanged.

## Hypothesis

The S1 monolithic label-policy + bridge pattern extends to investigations and comorbidities with auditable gold loading and a new partial scorer, without reopening S1 validation-split tuning.

## Gold audit (new families)

### Investigations

- **Source:** JSON `Investigations` entities (`data/ExECTv2 (2025)/Json/EA*.json`)
- **Preferred attributes:** `{EEG,MRI,CT}_Performed == Yes` plus `{EEG,MRI,CT}_Results`
- **Fallback:** parse `CUIPhrase` tokens (`eeg-abnormal`, `normal-mri`, etc.)
- **Canonical label:** `{modality} {result}` where modality ∈ {eeg, mri, ct} and result ∈ {normal, abnormal, unknown}
- **Corpus:** 108/200 documents with ≥1 investigation label; 166 modality+result rows total

### Comorbidities

- **Source:** JSON `PatientHistory` entities with `Negation == Affirmed` and `Certainty >= 4`
- **Exclusion policy:** drop seizure-history phrases (seizures, febrile seizures, dissociative seizures, jerks, etc.) and epilepsy-adjacent event descriptors
- **Canonical label:** `canonical_clinical_phrase(CUIPhrase)` (hyphen → space, lowercased)
- **Examples:** diabetes, type 1 diabetes, learning difficulties, anxiety, depression, migraine, hypertension

## Scorer

- **Mode:** `exect_s2_field_family_deterministic_v1`
- **Families:** diagnosis, seizure_type, annotated_medication, investigation, comorbidity
- **Micro F1:** pooled TP/FP/FN across all five families
- **Caveats:** partial diagnostic view; not CUI-aware Table 1 reproduction; comorbidity filter is policy-defined not annotation-guideline verbatim

## Program

- **Module:** `src/clinical_extraction/programs/exect_s2.py`
- **Variant:** `exect_s2_field_family_single_pass`
- **Prompt:** `exect_s2_field_family_v1_2_label_policy` (v1.2 — comorbidity affirmed-history recall + S2-only bridges; see `docs/experiments/exect/exect_s2_label_policy_v1_2_implementation.md`)
- **S1 reuse:** frozen v4.10 diagnosis/seizure/medication bridges imported from `exect_s0_s1.py`
- **S2 fields:** investigation + comorbidity lists with aligned evidence quotes

## Experiment configs

| Config | Purpose |
| --- | --- |
| `configs/experiments/exect_s2_smoke_gpt4_1_mini.json` | 3-record contract / schema smoke |
| `configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json` | 25-record diagnostic cap (gate only; not promotion) |

## Validation runs

**Smoke (cleared 2026-05-19):** `runs/exect_s2_smoke_gpt4_1_mini_20260519T223951Z`

- 3/3 predictions evaluated; no schema/contract failures
- Evidence quote support: 87.5% (3-record smoke — not a performance gate)
- Early S2 confusions: comorbidity granularity (stroke vs cva/hemiparesis/infarct), seizure surface vs gold, investigation unknown modality

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_smoke_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json --env-file .env
```

## Cap-25 gate

**v1.2 (current):** `runs/exect_s2_validation_cap25_gpt4_1_mini_20260519T225836Z` — 84.1% micro F1, comorbidity 74.3%, seizure 83.1%. See `docs/experiments/exect/exect_s2_label_policy_v1_2_implementation.md`.

**v1.1:** `runs/exect_s2_validation_cap25_gpt4_1_mini_20260519T225159Z` — 79.7% micro F1, seizure 80.6%, comorbidity 53.8%. See `docs/experiments/exect/exect_s2_label_policy_v1_1_implementation.md`.

**v1 (superseded):** `runs/exect_s2_validation_cap25_gpt4_1_mini_20260519T224038Z`

| Family | S2 cap-25 F1 | S1 v4.10 cap-25 anchor (3-family micro context) |
| --- | ---: | ---: |
| Micro F1 (5 families) | **66.4%** | 95.8% micro (S1-only, same cap) |
| Diagnosis | 88.4% | ~94% (full v4.10 dev) |
| Seizure type | **40.0%** | 95.4% (v4.10 cap-25) |
| Medication | 81.7% | ~93% (full v4.10 dev) |
| Investigation | 85.7% | n/a |
| Comorbidity | 49.0% | n/a |
| Evidence support | 87.1% | ~96% (v4.10 cap-25) |

**Read:** Contract gate passed (25/25 evaluated). Full error analysis: `docs/experiments/exect/exect_s2_validation_cap25_gpt4_1_mini_inspection_20260519.md`.

- **Seizure regression:** 14/16 seizure-fail records pass S1 cap-25 with the same bridges — model raw outputs change (plural GTCS, altered→impaired, ILAE surfaces, absence FP) before bridges run.
- **Comorbidity:** atomization (stroke vs cva/hemiparesis/infarct), modifier granularity, plural migraine.
- **Investigation:** mostly strong; tighten unknown/abnormal guards.
- **Medication collateral:** 10 records FP-only (non-AED over-extraction when S2 fields added).

Next: S2 label-policy **v1.1** (prompt-first); do **not** retune S1 bridges on validation.

## Status (2026-05-20)

**S2 frozen at v1.3.** Full anchor: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` (80.9% micro, 69.3% comorbidity). Schema ladder continues in **`docs/experiments/exect/exect_s2_s4_schema_ladder_design.md`** and Thread D in `docs/planning/kanban_plan.md`.

## Next steps (historical)

1. ~~S2 label-policy iteration~~ — complete through v1.3
2. **S3 Phase 1** — auditable gold for `BirthHistory`, `Onset`, `EpilepsyCause`, `WhenDiagnosed`
3. Do **not** retune S1 bridges or S2 v1.3 on validation while climbing the ladder

## Files touched

- `src/clinical_extraction/datasets/exect.py` — gold loader extensions
- `src/clinical_extraction/schemas.py` — `ExectGoldDocument.investigations`, `.comorbidities`
- `src/clinical_extraction/evaluation/exect.py` — S2 scorer
- `src/clinical_extraction/programs/exect_s2.py` — DSPy program
- `src/clinical_extraction/experiments/config.py` — S2 experiment contract
- `scripts/run_experiment.py` — S2 routing
- `tests/test_exect_s2_*.py` — loader, scorer, program tests

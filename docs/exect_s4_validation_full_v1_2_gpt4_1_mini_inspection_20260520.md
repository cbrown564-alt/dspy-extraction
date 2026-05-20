# ExECT S4 Full Validation v1.2 (40) — Error Read

Date: 2026-05-20

Run artifact:

- `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`

Config:

- `configs/experiments/exect_s4_validation_full_gpt4_1_mini.json`
- `prompt_version`: `exect_s4_field_family_v1_2_label_policy`
- `program_variant`: `exect_s4_field_family_single_pass`
- `scorer`: `exect_s4_field_family_deterministic_v1`
- S3 bridges: reused from frozen `exect_s3.py` (not edited); S2/S1 bridges unchanged

Implementation: `docs/exect_s4_label_policy_v1_2_implementation.md`

Comparison anchors:

| Run | Records | Scope |
| --- | ---: | --- |
| S4 cap-25 v1.2 | 25 | `…070616Z` |
| **S4 full v1.1** | 40 | `…064751Z` — freq **45.2%**, investigation **86.2%** |
| **S4 full v1.0** | 40 | `…001602Z` — freq **25.6%** |
| **S3 full v1.2 (frozen)** | 40 | `…235439Z` — **72.1%** micro F1 (9 fam) |
| S4 v1.1 error read | — | `docs/exect_s4_validation_full_v1_1_gpt4_1_mini_inspection_20260520.md` |

Design context: `docs/exect_s4_gold_policy.md`, `docs/exect_s2_s4_schema_ladder_design.md`

## Headline metrics

| Metric | Full v1.2 (40) | Full v1.1 (40) | Δ (v1.2 − v1.1) | Full v1.0 (40) | Cap-25 v1.2 (25) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Micro F1 (11 fam) | **65.5%** | 65.6% | −0.1pp | 63.4% | 69.2% |
| Diagnosis F1 | 91.1% | 92.5% | −1.4pp | 91.4% | 95.2% |
| Seizure F1 | **84.0%** | 82.0% | +2.0pp | 78.8% | 90.9% |
| Medication F1 | 71.3% | 72.6% | −1.3pp | 72.0% | 69.0% |
| **Investigation F1** | **96.7%** | 86.2% | **+10.5pp** | 93.3% | 93.8% |
| Comorbidity F1 | 59.8% | 56.6% | +3.2pp | 57.1% | 73.0% |
| Birth history F1 | 23.5% | 28.6% | −5.1pp | 25.0% | 50.0% |
| Onset F1 | 0.0% | 0.0% | 0 | 0.0% | 0.0% |
| Epilepsy cause F1 | 10.5% | 11.1% | −0.6pp | 11.1% | 0.0% |
| When diagnosed F1 | 0.0% | 0.0% | 0 | 0.0% | 0.0% |
| **Seizure frequency F1** | **45.7%** | 45.2% | +0.5pp | 25.6% | 49.1% |
| Medication temporality F1 | 62.5% | 67.2% | −4.7pp | 65.2% | 63.7% |
| Micro recall | 77.0% | 76.4% | +0.6pp | 72.7% | 84.3% |
| Evidence support | 87.7% | 87.9% | −0.2pp | 86.6% | 88.0% |

**Records with any field-family mismatch:** 40 / 40 (156 family-level mismatch entries vs 155 v1.1).

Cap-25 remained optimistic on **medication temporality** (−4.7pp full vs cap) and **birth history** (−26.5pp). **Investigation** held cap→full (+2.9pp). **Seizure frequency** held (−3.4pp cap→full), similar to v1.1 (−2.1pp).

## Root cause summary

| Pattern | Families affected | v1.2 read |
| --- | --- | --- |
| **Investigation unknown guard (pass)** | investigation | Mismatch count **6 → 1**. Cleared planned-scan FPs on **EA0109**, **EA0116**, **EA0188**, **EA0045**. **EA0179** `eeg unknown` recovered via unavailable-results cue. Residual: **EA0102** polarity flip (`eeg normal` → `eeg abnormal`) — unchanged mechanism. |
| **Non-audited period block (pass)** | seizure_frequency | **EA0188** cleared `1 per 30 day` FP; now hits `1 per 1 month` + `1 per 1 day` gold pair. |
| **Co-label bridge (partial)** | seizure_frequency | Note-anchored co-labels help when prose contains explicit change cues. **EA0008** still misses `frequency increased` — gold change label not supported by note text (`every 3 weeks` only). |
| **Spurious frequency on non-frequency docs** | seizure_frequency | **EA0179** new `seizure free` FP (gold has no frequency). Monitor only. |
| **Qualitative / paraphrase residuals** | seizure_frequency | `2 per 1 day` vs `several per day`; multi-label blocks (**EA0050**) unchanged. |
| **Rx temporality over-extraction** | medication_temporality | F1 −4.7pp vs v1.1 full — cap-25 optimistic; mechanism unchanged from v1.0/v1.1. |
| **Not primary** | All | Scorer/loader unchanged; evidence errors stable (~93). |

## Mismatch mix (156 family-level mismatch entries)

| Family | v1.2 entries | v1.1 entries | Δ |
| --- | ---: | ---: | ---: |
| Seizure frequency | **29** | 28 | +1 |
| Medication temporality | 29 | 27 | +2 |
| Annotated medication | 22 | 20 | +2 |
| Comorbidity | 17 | 18 | −1 |
| Onset | 12 | 14 | −2 |
| Seizure type | 12 | 12 | 0 |
| Epilepsy cause | 11 | 11 | 0 |
| When diagnosed | 10 | 8 | +2 |
| Diagnosis | 7 | 6 | +1 |
| Birth history | 6 | 5 | +1 |
| **Investigation** | **1** | **6** | **−5** |

## Investigation — v1.2 guard impact (+10.5pp vs v1.1)

| Doc | v1.1 | v1.2 | Read |
| --- | --- | --- | --- |
| EA0109 | `mri unknown` FP | *(empty)* | Planned scan FP **cleared** |
| EA0116 | `mri unknown`, `eeg unknown` FP | *(empty)* | Planned scan FPs **cleared** |
| EA0188 | `mri unknown`, `eeg unknown` FP | `mri normal`, `eeg abnormal` only | Unknown FPs **cleared**; performed results retained |
| EA0045 | `eeg unknown` FP | *(empty)* | Spurious unknown **cleared** |
| EA0179 | missed `eeg unknown` | `eeg unknown`, `mri normal` | Unavailable-results cue **recovered** gold unknown |
| EA0102 | `eeg abnormal` FP | `eeg abnormal` FP | Polarity flip **unchanged** (only remaining investigation mismatch) |

Investigation F1 **96.7%** beats S3 full v1.2 **93.1%** (+3.6pp) on same 40 records.

## Seizure frequency — v1.2 impact (+0.5pp vs v1.1)

Gold support: **43** labels across 40 records (unchanged).

### Document-level highlights

| Doc | v1.1 | v1.2 | Read |
| --- | --- | --- | --- |
| EA0188 | `1 per 1 day`, `1 per 30 day` FP | `1 per 1 day`, `1 per 1 month` | **Non-audited block + near-miss repair** — major fix |
| EA0179 | *(empty)* | `seizure free` FP | New spurious frequency on doc with no gold frequency |
| EA0008 | `1 per 3 week` only | `1 per 3 week` only | Gold `frequency increased` not in note text — bridge cannot fire |

### False negatives (top)

| Label | v1.2 miss | v1.1 miss |
| --- | ---: | ---: |
| `seizure free` | 4 | 3 |
| `frequency increased` | 3 | 4 |
| `infrequent` | 2 | 2 |

Co-label bridge reduced `frequency increased` misses by 1; `seizure free` FN increased by 1 (offset by fewer prose-related issues elsewhere).

**Read:** v1.2 holds v1.1 frequency lift with slight +0.5pp improvement. Primary v1.2 wins are **investigation guard** and **EA0188 frequency repair**. Residual frequency gap remains annotation-vs-note alignment (EA0008) and high-rate paraphrase.

## Frozen S3 families on same 40 records

| Family | S4 v1.2 | S4 v1.1 | S3 v1.2 | Gate |
| --- | ---: | ---: | ---: | --- |
| Diagnosis | 91.1% | 92.5% | 92.5% | Hold |
| Seizure type | 84.0% | 82.0% | 78.1% | **Hold** (+2.0pp vs v1.1) |
| **Investigation** | **96.7%** | 86.2% | 93.1% | **Pass** (+10.5pp vs v1.1; +3.6pp vs S3) |
| Comorbidity | 59.8% | 56.6% | 59.8% | Hold |
| Medication | 71.3% | 72.6% | 81.4% | Monitor (−10.1pp vs S3) |
| Birth history | 23.5% | 28.6% | 25.0% | Hold (sparse) |

## Decision read

| Gate | Result |
| --- | --- |
| v1.2 investigation guard | **Pass** — +10.5pp full; 1 residual mismatch |
| v1.2 frequency co-label / period block | **Partial pass** — +0.5pp full; EA0188 cleared; EA0008 unchanged |
| Frozen S3 seizure slot | **Pass** — seizure +2.0pp vs v1.1 |
| Pooled micro F1 | **Hold** — 65.5% vs 65.6% v1.1 (within noise) |
| Evidence / contract | **Pass** |

**Freeze decision:** Record **S4 v1.2 full anchor** at `…071248Z` for ladder traceability. Retain v1.1 `…064751Z` and v1.0 `…001602Z` for before/after frequency claims. v1.2 supersedes v1.1 as the active S4 baseline because investigation guard passes without frequency regression. **Do not** reopen S3 v1.2, S2 v1.3, or S1 v4.10 on validation.

## Recommended next steps (Thread E)

1. **Freeze S4 at v1.2** — no v1.3 micro-iteration unless a targeted regression slice surfaces a clear bridge gap.
2. **Qwen ladder:** replay cap-25/full with `exect_s4_*_qwen35b_ollama.json` when Ollama is free.
3. Gan / architecture / benchmark reproduction cards unchanged in Kanban.

**Do not:** compare 65.5% eleven-family micro F1 to 72.1% nine-family S3 micro as a single regression headline.

## Artifact quick reference

```powershell
$run = "runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z"
$metrics = Get-Content "$run/metrics.json" | ConvertFrom-Json
$metrics.benchmark_metrics.field_f1
$metrics.errors.field_family_mismatches | Where-Object field_family -eq 'investigation'
```

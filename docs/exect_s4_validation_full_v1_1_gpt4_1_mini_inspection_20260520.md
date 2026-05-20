# ExECT S4 Full Validation v1.1 (40) — Error Read

Date: 2026-05-20

Run artifact:

- `runs/exect_s4_validation_full_gpt4_1_mini_20260520T064751Z`

Config:

- `configs/experiments/exect_s4_validation_full_gpt4_1_mini.json`
- `prompt_version`: `exect_s4_field_family_v1_1_label_policy`
- `program_variant`: `exect_s4_field_family_single_pass`
- `scorer`: `exect_s4_field_family_deterministic_v1`
- S3 bridges: reused from frozen `exect_s3.py` (not edited); S2/S1 bridges unchanged

Implementation: `docs/exect_s4_label_policy_v1_1_implementation.md`

Comparison anchors:

| Run | Records | Scope |
| --- | ---: | --- |
| S4 cap-25 v1.1 | 25 | `…064206Z` |
| **S4 full v1.0** | 40 | `…001602Z` — freq **25.6%** |
| **S3 full v1.2 (frozen)** | 40 | `…235439Z` — **72.1%** micro F1 (9 fam) |
| S4 v1.0 error read | — | `docs/exect_s4_validation_full_gpt4_1_mini_inspection_20260520.md` |

Design context: `docs/exect_s4_gold_policy.md`, `docs/exect_s2_s4_schema_ladder_design.md`

## Headline metrics

| Metric | Full v1.1 (40) | Full v1.0 (40) | Δ (v1.1 − v1.0) | Cap-25 v1.1 (25) | S3 full v1.2 (40, 9 fam) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Micro F1 (11 fam) | **65.6%** | 63.4% | +2.2pp | 68.3% | 72.1% (not comparable scope) |
| Diagnosis F1 | **92.5%** | 91.4% | +1.1pp | 95.2% | 92.5% |
| Seizure F1 | **82.0%** | 78.8% | +3.2pp | 86.6% | 78.1% |
| Medication F1 | **72.6%** | 72.0% | +0.6pp | 70.9% | 81.4% |
| Investigation F1 | **86.2%** | 93.3% | **−7.1pp** | 83.3% | 93.1% |
| Comorbidity F1 | 56.6% | 57.1% | −0.5pp | 67.7% | 59.8% |
| Birth history F1 | 28.6% | 25.0% | +3.6pp | 80.0% | 25.0% |
| Onset F1 | 0.0% | 0.0% | 0 | 0.0% | 13.3% |
| Epilepsy cause F1 | 11.1% | 11.1% | 0 | 0.0% | 11.1% |
| When diagnosed F1 | 0.0% | 0.0% | 0 | 0.0% | 28.6% |
| **Seizure frequency F1** | **45.2%** | 25.6% | **+19.6pp** | 47.3% | n/a |
| **Medication temporality F1** | **67.2%** | 65.2% | +2.0pp | 66.7% | n/a |
| Micro recall | 76.4% | 72.7% | +3.7pp | 82.7% | 78.8% |
| Evidence support | 87.9% | 86.6% | +1.3pp | 88.9% | 90.1% |

**Records with any field-family mismatch:** 40 / 40 (155 family-level mismatch entries vs 156 v1.0).

Cap-25 remained optimistic on **seizure type** (−5.7pp full vs cap) and **investigation** (−2.9pp). **Seizure frequency** held cap→full (−2.1pp), unlike v1.0 (−7.0pp) — v1.1 frequency policy generalizes better beyond the cap subset.

## Root cause summary

| Pattern | Families affected | v1.1 read |
| --- | --- | --- |
| **Near-miss quantified repair (partial)** | seizure_frequency | Bridges fix `1 per month` → `1 per 1 month` when model emits single-slot rates; **EA0188** still misses `1 per 1 day` (model emits `1 per 30 day`). `several per day` vs gold `2 per 1 day` unchanged. |
| **Zero-rate + multi-label recovery** | seizure_frequency | **EA0061** cleared (`0 per 3 year`, `0 per 10 year`); **EA0124** cleared. **EA0050** still abstains on `1 per 1 week` + qualitative block. |
| **Seizure-free prose collapse** | seizure_frequency | `seizure free` FN **5 → 3**; prose FPs reduced (**EA0102**, **EA0137**). Residual: `seizure free since YEAR` variants and spurious `seizure free` FPs (**EA0069**). |
| **Qualitative change still weak** | seizure_frequency | `frequency increased` FN **3 → 4**; **EA0008** still drops `frequency increased` when gold has rate + change. |
| **Investigation unknown over-extraction** | investigation | New FPs **`eeg unknown`**, **`mri unknown`** on **EA0109**, **EA0116**, **EA0188** — eleven-family pass tags planned/uncertain imaging as `unknown` where v1.0 abstained. Core misses on **EA0102** / **EA0179** unchanged. |
| **Rx temporality over-extraction** | medication_temporality | Same mechanism as v1.0: `lamotrigine|planned`, `levetiracetam|previous` FPs on dose-change/current spans. F1 +2.0pp from higher recall (97.9%). |
| **Eleven-family slot competition** | annotated_medication | Medication name F1 **72.6%** vs S3 **81.4%** (−8.8pp) — unchanged gap vs v1.0 (−9.4pp). |
| **Not primary** | All | Scorer/loader unchanged; evidence errors **93** (same count as v1.0). |

## Mismatch mix (155 family-level mismatch entries)

| Family | v1.1 entries | v1.0 entries | Δ |
| --- | ---: | ---: | ---: |
| Seizure frequency | **28** | 27 | +1 |
| Medication temporality | 27 | 30 | −3 |
| Annotated medication | 20 | 20 | 0 |
| Comorbidity | 18 | 18 | 0 |
| Onset | 14 | 13 | +1 |
| Seizure type | 12 | 11 | +1 |
| Investigation | **6** | 3 | **+3** |
| Epilepsy cause | 11 | 11 | 0 |
| When diagnosed | 8 | 10 | −2 |
| Diagnosis | 6 | 7 | −1 |
| Birth history | 5 | 6 | −1 |

Frequency mismatch *count* is flat, but **TPs increased** (recall 48.8% vs 34.9% v1.0) — fewer gross surface errors, more partial hits.

## Seizure frequency — v1.1 impact

Gold support: **43** labels across 40 records (unchanged).

### False negatives (missed gold) — v1.1 vs v1.0

| Label | v1.1 miss | v1.0 miss | Read |
| --- | ---: | ---: | --- |
| `frequency increased` | 4 | 3 | Still dropped when paired with quantified rate (**EA0008**) |
| `seizure free` | 3 | 5 | Prose collapse + zero-rate recovery helped |
| `infrequent` | 2 | 2 | Unchanged |
| `0 per 5 year` | 2 | 2 | Unchanged |
| `1 per 1 month` | 2 | 3 | Near-miss bridge helped some docs |
| `1 per 1 week` | 1 | 3 | **EA0047** recovered `1 per 1 week` |
| `0 per 3 year` | 0 | 3 | **Cleared** — **EA0061** |
| `2 per 1 day` | 1 | 1 | `several per day` / `several per 1 day` paraphrase persists |
| `frequency decreased` | 1 | 1 | **EA0050** block still weak |

### False positives (non-gold) — v1.1 vs v1.0

| Pattern | v1.1 | v1.0 | Read |
| --- | --- | --- | --- |
| `infrequent` | 3 | 4 | Slight reduction |
| Near-miss `1 per month` / `1 per day` | **0** | 2+ | **Bridge cleared** near-miss slot omission |
| Prose seizure-free | fewer | 5+ | Collapse to `seizure free` removes some FPs; new spurious `seizure free` on **EA0069** |
| Non-gold quantified (`1 per 30 day`, `5 per 5 week`, `1 per previous appointment`) | 4+ | rare | Model invents non-audited period templates |

### Document-level frequency delta (12 improved / 13 worse / 15 unchanged)

**Improved (error count ↓):**

| Doc | v1.0 errors | v1.1 errors | Read |
| --- | ---: | ---: | --- |
| EA0061 | 3 | 0 | Zero-rate gold recovered |
| EA0124 | 2 | 0 | `1 per 1 week` + `0 per 3 year` recovered |
| EA0047 | 4 | 2 | `1 per 1 week` hit; `2 per 1 day` still paraphrased as `several per 1 day` |
| EA0188 | 4 | 2 | `1 per month` → `1 per 1 month` via bridge; `1 per 1 day` still missed (`1 per 30 day` FP) |
| EA0137 | 3 | 1 | `seizure free` TP; `2 per year` near-miss reduced |
| EA0102 | 2 | 1 | Prose seizure-free FP removed; new `0 per 5 year` FP |

**Still binding:**

| Doc | Gold | Predicted | Read |
| --- | --- | --- | --- |
| EA0008 | `1 per 3 week`, `frequency increased` | `1 per 3 week` only | Qualitative change omission (unchanged) |
| EA0050 | `1 per 1 week`, `frequency decreased`, `infrequent` | rate FPs only | Multi-label abstention persists |
| EA0047 | `2 per 1 day` | `several per 1 day` | Cardinal paraphrase — no safe bridge |

**Read:** v1.1 delivered the intended **+19.6pp** frequency F1 via near-miss repair, zero-rate recovery, and seizure-free collapse. Residual gap is **qualitative co-labels**, **non-audited period inventiveness**, and **high-rate paraphrase** (`several per day`) — not missing dual-cardinal template alone.

## Investigation — regression monitor (−7.1pp vs v1.0)

Mismatches **3 → 6**. Shared failures with v1.0:

| Doc | Gold miss | Predicted FP | Read |
| --- | --- | --- | --- |
| EA0102 | `eeg normal` | `eeg abnormal` | Polarity flip (unchanged) |
| EA0179 | `eeg unknown` | *(empty)* | Gold unknown not emitted |
| EA0045 | — | `eeg unknown` | Spurious unknown |

**v1.1-only** investigation FPs (model now emits `unknown` for uncertain/planned imaging):

| Doc | FP surfaces |
| --- | --- |
| EA0109 | `mri unknown` |
| EA0116 | `mri unknown`, `eeg unknown` |
| EA0188 | `mri unknown`, `eeg unknown` |

**Read:** Not a bridge failure — S3 investigation bridges unchanged. The wider S4 pass encourages **`modality unknown`** when results are not clearly normal/abnormal. This correlates with **EA0188** frequency noise (same doc) but investigation regression is **independent** of frequency bridges. **Do not** fix by reopening S3; a v1.2 **S4-only** investigation guard (suppress `unknown` unless gold policy supports) would be scoped separately.

## Medication temporality — stable noise (+2.0pp F1)

Recall **97.9%** (near-saturated). Top FPs unchanged in mechanism:

| Label | v1.1 FP | v1.0 FP |
| --- | ---: | ---: |
| `lamotrigine|planned` | 5 | 4 |
| `levetiracetam|previous` | 4 | 5 |
| `levetiracetam|planned` | 3 | 3 |
| `aspirin|current` | 3 | 2 |

Gold FN: `epilim chrono|current` (1) — trade-name normalization gap persists.

## Frozen S3 families on same 40 records

| Family | S4 v1.1 | S4 v1.0 | S3 v1.2 | Gate |
| --- | ---: | ---: | ---: | --- |
| Diagnosis | 92.5% | 91.4% | 92.5% | Hold |
| Seizure type | 82.0% | 78.8% | 78.1% | **Hold** (+3.2pp vs v1.0) |
| Investigation | 86.2% | 93.3% | 93.1% | **Monitor** (−7.1pp vs v1.0) |
| Comorbidity | 56.6% | 57.1% | 59.8% | Hold (known S3 gap) |
| Medication | 72.6% | 72.0% | 81.4% | Monitor (−8.8pp vs S3) |
| Birth history | 28.6% | 25.0% | 25.0% | Hold (sparse) |

Seizure type **improved** under v1.1 — frequency policy did not collapse the S3 seizure slot. Investigation is the main frozen-family regression vs v1.0; vs S3 full it is **−6.9pp**.

## Evidence

| Metric | v1.1 | v1.0 |
| --- | ---: | ---: |
| Quote support | 87.9% | 86.6% |
| Offsets valid (when present) | 100% | 100% |
| Evidence support errors | 93 | 93 |

Frequency lift is not explained by evidence failure.

## Decision read

| Gate | Result |
| --- | --- |
| v1.1 frequency hypothesis | **Pass** — +19.6pp full F1; cap-25 +14.7pp |
| Frozen S3 seizure slot | **Pass** — seizure +3.2pp vs v1.0 |
| Frozen S3 investigation | **Monitor** — −7.1pp vs v1.0; `unknown` over-extraction |
| S4 new families | **Mixed** — frequency **usable** (45%); temporality **67%** |
| Evidence / contract | **Pass** |

**Freeze decision:** Record **S4 v1.1 full anchor** at `…064751Z` for ladder traceability. Retain v1.0 `…001602Z` for before/after frequency claims. **Do not** reopen S3 v1.2, S2 v1.3, or S1 v4.10 on validation.

## Recommended next steps (Thread E)

1. **Optional S4 v1.2** (S4-only, not S3):
   - Frequency: multi-label co-emission rule for rate + `frequency increased/decreased`; block non-audited period tokens (`30 day`, `previous appointment`); no bridge from `several per day` → `2 per 1 day` without note-anchored repair.
   - Investigation: suppress `eeg unknown` / `mri unknown` unless span explicitly encodes unknown result (reduce **EA0109**, **EA0116**, **EA0188** FPs).
2. **Do not** micro-tune S3 comorbidity or reopen S2/S1 bridges on validation.
3. **Qwen ladder:** replay cap-25/full with `exect_s4_*_qwen35b_ollama.json` when Ollama is free — compare frequency lift vs GPT v1.1.
4. Gan / architecture / benchmark reproduction cards remain unchanged in Kanban.

**Do not:** compare 65.6% eleven-family micro F1 to 72.1% nine-family S3 micro as a single regression headline.

## Artifact quick reference

```powershell
$run = "runs/exect_s4_validation_full_gpt4_1_mini_20260520T064751Z"
$metrics = Get-Content "$run/metrics.json" | ConvertFrom-Json
$metrics.benchmark_metrics.field_f1
$metrics.errors.field_family_mismatches | Where-Object field_family -eq 'seizure_frequency'
```

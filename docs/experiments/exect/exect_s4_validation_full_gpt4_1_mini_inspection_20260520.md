# ExECT S4 Full Validation (40) — Error Read

Date: 2026-05-20

Run artifact:

- `runs/exect_s4_validation_full_gpt4_1_mini_20260520T001602Z`

Config:

- `configs/experiments/exect_s4_validation_full_gpt4_1_mini.json`
- `prompt_version`: `exect_s4_field_family_v1_0_label_policy`
- `program_variant`: `exect_s4_field_family_single_pass`
- `scorer`: `exect_s4_field_family_deterministic_v1`
- S3 bridges: reused from frozen `exect_s3.py` (not edited); S2/S1 bridges unchanged

Comparison anchors:

| Run | Records | Scope |
| --- | ---: | --- |
| S4 smoke v1.0 | 3 | `…000944Z` |
| S4 cap-25 v1.0 | 25 | `…001157Z` |
| **S3 full v1.2 (frozen)** | 40 | `…235439Z` — **72.1%** micro F1 (9 fam) |
| S3 cap-25 v1.2 | 25 | `…235349Z` — 78.1% micro F1 (9 fam) |

Design context: `docs/experiments/exect/exect_s4_gold_policy.md`, `docs/experiments/exect/exect_s2_s4_schema_ladder_design.md`

## Headline metrics

| Metric | Full v1.0 (40) | Cap-25 v1.0 (25) | Δ (full − cap) | S3 full v1.2 (40, 9 fam) |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 (11 fam) | **63.4%** | 67.8% | −4.4pp | 72.1% (not comparable scope) |
| Diagnosis F1 | **91.4%** | 93.0% | −1.6pp | 92.5% |
| Seizure F1 | **78.8%** | 92.3% | **−13.5pp** | 78.1% |
| Medication F1 | **72.0%** | 70.0% | +2.0pp | 81.4% |
| Investigation F1 | **93.3%** | 90.9% | +2.4pp | 93.1% |
| Comorbidity F1 | **57.1%** | 68.8% | −11.7pp | 59.8% |
| Birth history F1 | **25.0%** | 57.1% | −32.1pp | 25.0% |
| Onset F1 | **0.0%** | 0.0% | 0 | 13.3% |
| Epilepsy cause F1 | **11.1%** | 0.0% | +11.1pp | 11.1% |
| When diagnosed F1 | **0.0%** | 0.0% | 0 | 28.6% |
| **Seizure frequency F1** | **25.6%** | 32.6% | −7.0pp | n/a |
| **Medication temporality F1** | **65.2%** | 65.9% | −0.7pp | n/a |
| Micro recall | 72.7% | 80.1% | −7.4pp | 78.8% |
| Evidence support | **86.6%** | 87.7% | −1.1pp | 90.1% |

**Records with any field-family mismatch:** 39 / 40.

Cap-25 was optimistic on **seizure type** and **comorbidity** when scaling to full; **seizure frequency** degraded further on full (−7.0pp). **Medication temporality** held (~65% F1).

## Root cause summary

| Pattern | Families affected | Mechanism |
| --- | --- | --- |
| **Benchmark surface mismatch** | seizure_frequency (primary) | Model emits clinical prose or near-miss quantified strings (`1 per month` vs gold `1 per 1 month`, `2 per week` vs `1 per 2 week`) instead of audited JSON-normalized surfaces. |
| **Qualitative frequency omission** | seizure_frequency | Misses `frequency increased/decreased`, `infrequent`, and bare `seizure free` when note uses richer phrasing (`seizure free for more than five years`, date ranges). |
| **Zero-rate / multi-row gold** | seizure_frequency | Gold uses `0 per N year/week` and multiple coexisting frequency rows; model often abstains or collapses to a single prose label. |
| **Rx temporality over-extraction** | medication_temporality, annotated_medication | Model tags **planned** or **previous** on drugs that gold marks **current** (dose-change spans); also emits temporality for non-antiepileptic drugs (`thyroxine|current`, `aspirin|current`). |
| **Eleven-family slot competition** | annotated_medication | Medication name-only F1 **72.0%** vs S3 full **81.4%** (−9.4pp) — temporality slot and wider pass increase drug-name FPs without improving temporality precision. |
| **Cap optimism on sparse S3 slots** | seizure_type, comorbidity, birth_history | Cap-25 subset overstates performance on families with high variance across the 15 non-cap records. |
| **Not primary** | All | Scorer/loader regression — Phase 1 gold policy unchanged; S3 full on same 40 records still scores investigation ~93%. |

## Mismatch mix (156 family-level mismatch entries)

| Family | Mismatch entries |
| --- | ---: |
| Medication temporality | 30 |
| Seizure frequency | 27 |
| Annotated medication | 20 |
| Comorbidity | 18 |
| Onset | 13 |
| Epilepsy cause | 11 |
| Seizure type | 11 |
| When diagnosed | 10 |
| Diagnosis | 7 |
| Birth history | 6 |
| Investigation | 3 |

## Seizure frequency — binding failure (v1.0 label policy)

Gold support: **43** labels across 40 records (19 records with frequency gold).

Top false negatives (missed gold surfaces):

| Label | Miss count |
| --- | ---: |
| `seizure free` | 5 |
| `frequency increased` | 3 |
| `1 per 1 week` | 3 |
| `0 per 3 year` | 3 |
| `1 per 1 month` | 3 |
| `infrequent` | 2 |
| `0 per 5 year` | 2 |

Top false positives (non-gold surfaces):

| Label | FP count |
| --- | ---: |
| `infrequent` | 4 |
| `1 per month` | 2 |
| Prose seizure-free variants (`seizure free >5 years`, date ranges) | 5+ |
| Near-miss rates (`2 per week`, `1 per week`, `3 per month`) | 4+ |

Representative record-level failures:

| Doc | Gold | Predicted | Read |
| --- | --- | --- | --- |
| EA0008 | `1 per 3 week`, `frequency increased` | `1 per 3 week` only | Qualitative change omitted |
| EA0047 | `1 per 1 week`, `2 per 1 day` | `1 per week`, `several per day` | Cardinal normalization mismatch |
| EA0050 | `1 per 1 week`, `frequency decreased`, `infrequent` | *(empty)* | Complete abstention on multi-label frequency block |
| EA0188 | `1 per 1 day`, `1 per 1 month` | `1 per day`, `1 per month` | Missing `1` in `N per N period` template |

**Read:** Deterministic bridges accept canonical `N per N period` only when the model emits exact surfaces; there is no prose→gold repair for frequency (unlike S3 investigation bridge). v1.1 must teach **gold-normalized frequency templates** and multi-label retention, not Gan-style monthly ordinals.

## Medication temporality — usable but noisy

Full F1 **65.2%** with **100% recall** on cap-25 and full — the model over-predicts status tags.

Top false positives:

| Label | FP count |
| --- | ---: |
| `levetiracetam|previous` | 5 |
| `lamotrigine|planned` | 4 |
| `levetiracetam|planned` | 3 |
| `carbamazepine|previous` | 3 |

Gold false negatives are rare (2): `epilim chrono|current`, `lamictal|current` — synonym/trade-name normalization gap vs `annotated_medication` bridges.

**Read:** Temporality policy needs tighter **current-by-default on dose-change spans** (aligned with gold policy) and restriction to **annotated antiepileptic prescriptions**; avoid tagging comorbidity medications unless they appear as `Prescription` entities.

## Frozen S3 families on same 40 records

| Family | S4 full | S3 full | Δ | Gate |
| --- | ---: | ---: | ---: | --- |
| Diagnosis | 91.4% | 92.5% | −1.1pp | Hold |
| Seizure type | 78.8% | 78.1% | +0.7pp | Hold |
| Investigation | 93.3% | 93.1% | +0.2pp | Hold |
| Comorbidity | 57.1% | 59.8% | −2.7pp | Monitor (known S3 gap) |
| Medication | 72.0% | 81.4% | **−9.4pp** | **Regression** — likely eleven-family competition |
| Birth history | 25.0% | 25.0% | 0 | Hold (sparse) |
| Onset / when diagnosed | 0% | 13% / 29% | worse | Low support; cap-25 n=3/1 |

Investigation and seizure **did not regress** vs frozen S3 full — the S3 v1.2 priority block largely held under S4 expansion.

## Evidence

| Metric | Value |
| --- | ---: |
| Quote support | 86.6% |
| Offsets valid (when present) | 100% |
| Evidence errors | (see `errors.json`) |

Evidence is adequate for contract gating; frequency F1 collapse is label-surface mismatch, not evidence failure.

## Decision read

| Gate | Result |
| --- | --- |
| Smoke / cap-25 / full executed | **Pass** — 3/3, 25/25, 40/40 |
| Eleven-family contract | **Pass** — schema valid, all families scored |
| Frozen S3 high-support families | **Mostly pass** — investigation/seizure held; medication −9.4pp |
| S4 new families baseline | **Mixed** — temporality **65%** usable; frequency **26%** weak |
| Evidence / contract | **Pass** |

**Freeze decision:** Record **S4 v1.0 full anchor** at `…001602Z` for ladder traceability. Do **not** reopen S3 v1.2, S2 v1.3, or S1 v4.10 on validation.

## Recommended next steps (Thread E)

1. Ship **S4 v1.1 label-policy** targeting **seizure frequency only**:
   - Explicit `N per N week/month/day/year` template with both cardinal slots.
   - Qualitative surfaces: `frequency increased/decreased`, `infrequent`, `seizure free`, `seizure free since YEAR`.
   - Forbid seizure-type names in `seizure_frequency`; retain multi-label lists when note states rate + change.
   - Optional deterministic bridge: map near-miss `1 per month` → `1 per 1 month` when note supports it (TDD against EA0188-style cases).
2. **Do not** micro-tune S3 comorbidity or medication name-only fields on validation unless medication regression persists after v1.1 frequency pass.
3. Cap-25 regate → full replay for v1.1; compare frequency canonical match rate and frozen investigation/seizure F1 vs `…001602Z`.
4. Update Kanban with frozen S4 v1.0 anchor and v1.1 as optional next pull.

**Do not:** compare 63.4% eleven-family micro F1 to 72.1% nine-family S3 micro as a single regression headline.

## Artifact quick reference

```powershell
$run = "runs/exect_s4_validation_full_gpt4_1_mini_20260520T001602Z"
Get-Content "$run/metrics.json" | ConvertFrom-Json | Select-Object -ExpandProperty benchmark_metrics
```

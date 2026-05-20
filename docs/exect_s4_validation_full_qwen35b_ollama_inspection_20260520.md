# ExECT S4 Full Validation (40) — Qwen3.6:35b Replication Read

Date: 2026-05-20

**Track:** local Qwen replication of frozen hosted GPT Thread E (S4 v1.2). **Not** the same experiment as GPT 4.1-mini; same split, scorer, prompt version, and program variant.

## Run artifacts

| Run | ID suffix | Records | Notes |
| --- | --- | ---: | --- |
| **Qwen full (this read)** | `…160914Z` | 40 | Live inference; ~91 min total |
| Qwen cap-25 gate | `…133930Z` | 25 | 72.4% micro; cap optimism vs full |
| **GPT v1.2 frozen anchor** | `…071248Z` | 40 | 65.5% micro (hosted) |
| GPT cap-25 v1.2 | `…070616Z` | 25 | 69.2% micro |

**Config:** `configs/experiments/exect_s4_validation_full_qwen35b_ollama.json`  
**Model:** `configs/models/exect_qwen35b_ollama.json` (`qwen3.6:35b`, Ollama)  
**Prompt:** `exect_s4_field_family_v1_2_label_policy`  
**Program:** `exect_s4_field_family_single_pass`  
**Scorer:** `exect_s4_field_family_deterministic_v1`  
**Ollama residency:** 79%/21% CPU/GPU, `num_ctx` 262144

Design context: `docs/exect_s4_gold_policy.md`, `docs/exect_s2_s4_schema_ladder_design.md`, GPT error read `docs/exect_s4_validation_full_v1_2_gpt4_1_mini_inspection_20260520.md`

## Headline metrics

| Metric | Qwen full | GPT v1.2 full | Δ (Qwen − GPT) | Qwen cap-25 |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 (11 fam) | **67.5%** | 65.5% | **+2.0pp** | 72.4% |
| Micro precision | 61.3% | 66.4% | −5.1pp | — |
| Micro recall | 75.2% | 77.0% | −1.8pp | — |
| Evidence quote support | **93.4%** | 87.7% | **+5.7pp** | — |
| Evidence errors | 60 | 93 | −33 | — |
| Schema / normalization errors | 0 / 0 | 0 / 0 | — | — |
| Records evaluated | 40/40 | 40/40 | — | 25/25 |
| Total runtime | 5452.8 s | — | — | — |
| Seconds / record | 136.3 | — | — | — |

**Cap-25 → full (Qwen):** micro F1 **−4.9pp** (72.4% → 67.5%). Same direction as GPT cap optimism on S4 (69.2% → 65.5%, −3.7pp).

## Per-family F1 (full 40, same gold supports)

| Family | Support | Qwen full | GPT v1.2 | Δ (Qwen − GPT) |
| --- | ---: | ---: | ---: | ---: |
| investigation | 30 | 94.7% | **96.7%** | −1.9pp |
| diagnosis | 42 | 88.3% | **91.1%** | −2.8pp |
| seizure_type | 47 | 76.3% | **84.0%** | −7.7pp |
| annotated_medication | 47 | **80.4%** | 71.3% | +9.0pp |
| comorbidity | 48 | **64.0%** | 59.8% | +4.2pp |
| birth_history | 8 | **31.6%** | 23.5% | +8.0pp |
| when_diagnosed | 4 | 0.0% | 0.0% | 0 |
| onset | 3 | 0.0% | 0.0% | 0 |
| epilepsy_cause | 7 | **19.0%** | 10.5% | +8.5pp |
| **seizure_frequency** | 43 | **50.0%** | 45.7% | +4.3pp |
| **medication_temporality** | 47 | **69.3%** | 62.5% | +6.8pp |

**Read:** Pooled micro F1 exceeds the frozen GPT S4 anchor by 2.0pp, but the **family profile diverges**. Qwen is weaker on **seizure type** and **diagnosis** (themes from prior Qwen S1/S3 reads) and stronger on **S4 extension families** (medication name, Rx temporality, seizure frequency) plus **comorbidity** and sparse S3 slots. Do **not** treat pooled micro as “Qwen beats GPT on ExECT” without per-family caveats — separate model tracks.

## Contract / schema gates

| Gate | Result |
| --- | --- |
| 40/40 predictions + scorer | **Pass** |
| Invalid JSON / schema errors | **Pass** (0) |
| Normalization errors | **Pass** (0) |
| Eleven-family emission | **Pass** — no empty-family collapse |
| Cap-25 gate row | Separate — `…133930Z` is not a full-validation substitute |

## Evidence (report separately from F1)

| Metric | Qwen full | GPT v1.2 |
| --- | ---: | ---: |
| Quote support | 93.4% | 87.7% |
| Quote support (exact only) | 93.3% | — |
| Quote support (with ellipsis repairs) | 100.0% | — |
| Quote repair rate | 1.1% | — |
| Offsets present | 93.4% | — |
| Offsets valid (when present) | 100.0% | 100.0% |

Shared gaps: missing evidence spans on comorbidity/medication (EA0008, EA0016, EA0053, …). Qwen adds **fewer** total evidence errors (60 vs 93) but still emits unsupported header-style quotes on some records (EA0069, EA0072, EA0135).

## Field-family caveats (S4 extensions)

### Seizure frequency (+4.3pp vs GPT)

Gold support: **43** labels / 19 records with frequency gold (unchanged).

| Pattern | Mechanism |
| --- | --- |
| Near-miss templates | `1 per week` vs `1 per 1 week`; `2 per 1 month` vs `1 per 1 month` |
| Qualitative change omission | `frequency increased/decreased` missed when rate surface partially correct (EA0008, EA0069) |
| Prose vs gold surface | `seizure free since 2020`, `4 to 5 per month` FPs (EA0100, EA0185) |
| Multi-label abstention | EA0050 still empty on multi-label frequency block |
| Collapsed seizure-free | EA0061: gold `0 per 3 year` + `0 per 10 year` → predicted `seizure free` only |

Qwen improves frequency F1 vs GPT v1.2 but the binding failure mode is the same: **no prose→gold frequency repair** beyond v1.2 co-label bridges. Gan monthly temporal scaffolding does **not** transfer directly.

### Medication temporality (+6.8pp vs GPT)

Recall remains high (93.6%); precision lower (55.0%). Top mechanism unchanged: **over-extraction** of `planned`/`previous` tags and non-antiepileptic drugs (`thyroxine|current`, `omeprazole|current`, `sertraline|current`). Qwen extracts more temporality rows than GPT on the same notes — helping recall on some records, hurting precision on others.

### Onset / when_diagnosed (0% both tracks)

Both models emit spurious age/date surfaces on records with gold `unknown` or different slot semantics (EA0153, EA0116, EA0143). Sparse gold support (n=3 onset, n=4 when_diagnosed) — inspect record-level before policy changes.

## Mismatch mix (148 family-level mismatch entries)

| Family | Entries |
| --- | ---: |
| Medication temporality | 30 |
| Seizure frequency | 27 |
| Annotated medication | 20 |
| Comorbidity | 18 |
| Onset | 13 |
| Seizure type | 11 |
| Epilepsy cause | 11 |
| When diagnosed | 10 |
| Diagnosis | 7 |
| Birth history | 6 |
| Investigation | 3 |

## Comparison to Qwen S3 full (separate scope)

| Run | Families | Micro F1 |
| --- | ---: | ---: |
| Qwen S3 full `…092244Z` | 9 | 72.2% |
| Qwen S4 full `…160914Z` | 11 | 67.5% |

Two-family S4 expansion costs ~4.7pp pooled micro vs Qwen S3 on the same validation split — expected breadth effect, not a scorer regression.

## Replication decision (Thread E local)

| Question | Answer |
| --- | --- |
| Complete Qwen schema ladder through S4? | **Yes** — contract clean; record `…160914Z` as Qwen S4 full anchor |
| Pooled micro exceeds GPT on S4? | **Yes** (+2.0pp) — report with per-family divergence |
| Promote Qwen as default over hosted GPT on S4? | **No** — separate tracks; seizure/diagnosis weaker |
| Safe to proceed to S1 interleaving experiment? | **Yes** — ladder replication closed; next causal test is fixed-schema interleaving |

## Artifact quick reference

```powershell
$qwen = "runs/exect_s4_validation_full_qwen35b_ollama_20260520T160914Z"
$gpt  = "runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z"
Get-Content "$qwen/metrics.json" | ConvertFrom-Json | Select-Object -ExpandProperty benchmark_metrics
Get-Content "$gpt/metrics.json"  | ConvertFrom-Json | Select-Object -ExpandProperty benchmark_metrics
```

# ExECT S3 Full Validation (40) — Qwen3.6:35b Replication Read

Date: 2026-05-20

**Track:** local Qwen replication of frozen hosted GPT Thread D (v1.2). **Not** the same experiment as GPT 4.1-mini; same split, scorer, prompt version, and program variant.

## Run artifacts

| Run | ID suffix | Records | Notes |
| --- | --- | ---: | --- |
| **Qwen full (this read)** | `…092244Z` | 40 | Live inference; detached launcher ~83 min |
| Qwen cap-25 | `…091642Z` | 25 | 77.1% micro; partial cache replay caveat |
| **GPT v1.2 frozen anchor** | `…235439Z` | 40 | 72.1% micro (hosted) |
| GPT cap-25 v1.2 | `…235349Z` | 25 | 78.1% micro |

**Config:** `configs/experiments/exect_s3_validation_full_qwen35b_ollama.json`  
**Model:** `configs/models/exect_qwen35b_ollama.json` (`qwen3.6:35b`, Ollama)  
**Prompt:** `exect_s3_field_family_v1_2_label_policy`  
**Program:** `exect_s3_field_family_single_pass`  
**Scorer:** `exect_s3_field_family_deterministic_v1`  
**Log:** `runs/overnight_logs/exect_s3_full_qwen35b_20260520_102242.log`  
**Ollama residency (start/end):** 79%/21% CPU/GPU, `num_ctx` 262144

## Headline metrics

| Metric | Qwen full | GPT v1.2 full | Δ (Qwen − GPT) | Qwen cap-25 |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 (9 fam) | **72.2%** | 72.1% | **+0.1pp** | 77.1% |
| Micro precision | 67.9% | 66.4% | +1.5pp | 69.8% |
| Micro recall | 77.1% | 78.8% | −1.7pp | 86.1% |
| Evidence quote support | **94.7%** | 90.1% | **+4.6pp** | 93.4% |
| Evidence errors | 37 | 62 | −25 | 27 |
| Schema / normalization errors | 0 / 0 | 0 / 0 | — | 0 / 0 |
| Records evaluated | 40/40 | 40/40 | — | 25/25 |

**Cap-25 → full (Qwen):** micro F1 **−4.9pp** (77.1% → 72.2%). Same direction as GPT cap optimism (78.1% → 72.1%, −6.0pp) but smaller gap on this slice.

## Per-family F1 (full 40, same gold supports)

| Family | Support | Qwen full | GPT v1.2 | Δ (Qwen − GPT) |
| --- | ---: | ---: | ---: | ---: |
| investigation | 30 | **96.6%** | 93.1% | +3.5pp |
| diagnosis | 42 | 86.1% | **92.5%** | −6.4pp |
| seizure_type | 47 | 72.3% | **78.1%** | −5.8pp |
| annotated_medication | 47 | 77.6% | **81.4%** | −3.8pp |
| comorbidity | 48 | **65.3%** | 59.8% | +5.5pp |
| when_diagnosed | 4 | **72.7%** | 28.6% | +44.1pp |
| birth_history | 8 | **37.5%** | 25.0% | +12.5pp |
| epilepsy_cause | 7 | **22.2%** | 11.1% | +11.1pp |
| onset | 3 | 11.8% | 13.3% | −1.5pp |

**Read:** Pooled micro F1 matches the frozen GPT anchor within 0.1pp, but the **family profile diverges**. Qwen does not replay GPT’s v1.0 investigation collapse (frozen v1.2 investigation policy holds on local model). Qwen is weaker on **diagnosis** and **seizure** (S1-priority / legacy-surface themes from prior Qwen reads) and stronger on **comorbidity**, **sparse S3 slots** (when_diagnosed, birth_history, cause), and **evidence grounding**.

Do **not** treat when_diagnosed +44.1pp as a stable “Qwen wins” claim — support n=4; inspect record-level slot assignment before any policy inference.

## Contract / schema gates (Phase 2)

| Gate | Result |
| --- | --- |
| 40/40 predictions + scorer | **Pass** |
| Invalid JSON / schema errors | **Pass** (0 schema errors) |
| Normalization errors | **Pass** (0) |
| Systematic empty-family collapse vs GPT | **Pass** — all nine families emitted on full split |
| Cap-25 schema validity ≥95% | **Pass** (prior `…091642Z`) |

## Evidence (report separately from F1)

| Metric | Qwen full | GPT v1.2 |
| --- | ---: | ---: |
| Quote support | 94.7% | 90.1% |
| Quote support (exact only) | 94.6% | 90.1% |
| Quote support (with ellipsis repairs) | 100.0% | — |
| Quote repair rate | 0.8% | 0.0% |
| Offsets present | 94.7% | 90.1% |
| Offsets valid (when present) | 100.0% | 100.0% |

Shared evidence gaps (both runs): EA0008 comorbidity missing spans; EA0016 medication/comorbidity missing spans. Qwen adds fewer total evidence errors (37 vs 62) but still has unsupported long quotes on some records (e.g. EA0045 diagnosis/seizure).

## Comparison to Qwen S2 full (separate scope)

| Run | Families | Micro F1 |
| --- | ---: | ---: |
| Qwen S2 full `…073552Z` | 5 | 82.6% |
| Qwen S3 full `…092244Z` | 9 | 72.2% |

Nine-family expansion costs ~10.4pp pooled micro vs Qwen S2 on the same validation split — expected breadth effect; not a scorer regression.

## Replication decision (Thread D local)

| Question | Answer |
| --- | --- |
| Replicate GPT v1.2 micro headline? | **Yes** — 72.2% vs 72.1% (+0.1pp) |
| Same failure mode as GPT S3 v1.0 (investigation collapse)? | **No** — investigation 96.6% |
| Safe to proceed to S4 replication? | **Yes** — contract clean; per-family deltas documented |
| Promote Qwen as “beats GPT” on S3? | **No** — separate track; mixed per-family profile |

Record `…092244Z` as the **Qwen Thread D full anchor** for ladder Phase 2. Next ladder step: **S4 cap-25** then **S4 full** vs GPT `…071248Z` (65.5% micro, 11 fam).

## Artifact quick reference

```powershell
$qwen = "runs/exect_s3_validation_full_qwen35b_ollama_20260520T092244Z"
$gpt  = "runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z"
Get-Content "$qwen/metrics.json" | ConvertFrom-Json | Select-Object -ExpandProperty benchmark_metrics
Get-Content "$gpt/metrics.json"  | ConvertFrom-Json | Select-Object -ExpandProperty benchmark_metrics
```

# ExECT S1 Interleaving Qwen Validation v1 — Inspection

Date: 2026-05-20  
Comparison group: `exect_s1_interleaving_qwen_validation_v1`  
Pre-registration: `docs/exect_s1_interleaving_qwen_validation_v1_preregistration_20260520.md`  
Cap-25 addendum: `docs/exect_s1_interleaving_qwen_validation_v1_cap25_inspection_20260520.md`  
GPT reference: `docs/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md`

## Run artifacts

| Arm | Scope | Run ID | Config |
| --- | --- | --- | --- |
| **L1 raw (bridge-free)** | cap-25 | `exect_s1_interleaving_l1_raw_no_bridges_cap25_qwen35b_ollama_20260520T210420Z` | `exect_s1_interleaving_l1_raw_no_bridges_cap25_qwen35b_ollama.json` |
| **H1 post bridge** | cap-25 | `exect_s1_interleaving_h1_post_bridge_cap25_qwen35b_ollama_20260520T210432Z` | `exect_s1_interleaving_h1_post_bridge_cap25_qwen35b_ollama.json` |
| **L1 raw (bridge-free)** | full (40) | `exect_s1_interleaving_l1_raw_no_bridges_qwen35b_ollama_20260520T210719Z` | `exect_s1_interleaving_l1_raw_no_bridges_qwen35b_ollama.json` |
| **H1 post bridge** | full (40) | `exect_s1_interleaving_h1_post_bridge_qwen35b_ollama_20260520T210722Z` | `exect_s1_interleaving_h1_post_bridge_qwen35b_ollama.json` |
| **Qwen production anchor** *(frozen)* | full (40) | `exect_s0_s1_validation_full_qwen35b_ollama_20260520T042117Z` | `exect_s0_s1_validation_full_qwen35b_ollama.json` |

Fixed controls: ExECTv2 validation (40), `exect_s0_s1_field_family`, `exect_field_family_deterministic_v1`, Qwen3.6:35b Ollama, prompt `exect_s0_s1_field_family_v4_10_label_policy`.

Varied factor: `repair_policy` — `raw_no_benchmark_bridges` vs `artifact_benchmark_bridge_only`.

## Headline metrics

| Arm | Scope | Micro F1 | Diagnosis | Seizure | Medication | Evidence support |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| L1 raw | cap-25 | **71.4%** | 78.0% | 57.5% | 85.2% | 97.6% |
| H1 post bridge | cap-25 | **80.7%** | 95.2% | 66.7% | 87.3% | 98.7% |
| L1 raw | full | **66.2%** | 70.1% | 45.5% | 85.7% | 94.6% |
| H1 post bridge | full | **79.0%** | 95.1% | 55.7% | 89.1% | 95.8% |
| Qwen production anchor | full | **79.0%** | 95.1% | 55.7% | 89.1% | ~96% |

**Full bridge delta (H1 − L1 raw):** **+12.8pp** micro; seizure **+10.2pp**; diagnosis **+25.0pp**; medication **+3.4pp**.

## Cross-track reference (GPT v2, full validation 40)

| Track | L1 raw micro | H1 post micro | Bridge Δ micro | Bridge Δ seizure | H1 seizure F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| GPT 4.1-mini | 68.6% | 92.3% | **+23.7pp** | **+33.1pp** | 90.5% |
| Qwen3.6:35b | 66.2% | 79.0% | **+12.8pp** | **+10.2pp** | 55.7% |

**Interpretation:** Qwen and GPT start from similar **raw** micro F1 (~66–69%), but GPT bridges recover **~24pp** pooled F1 versus Qwen **~13pp**. The model-track gap after bridging is driven mainly by **seizure_type** (GPT H1 90.5% vs Qwen H1 55.7%, **−34.8pp**).

## Production anchor check

H1 post-bridge full metrics are **identical** to frozen `exect_s0_s1_validation_full_qwen35b_ollama` (79.0% micro, per-family F1 match). Confirms `artifact_benchmark_bridge_only` reproduces inline production bridges (`repair_policy=none`).

## Decisions

| Arm / matrix | Outcome | Rationale |
| --- | --- | --- |
| **H1 post bridge (full)** | **Hold (null vs Qwen production L1)** | Same 79.0% micro as frozen anchor; not a new deployment path |
| **L1 raw (full)** | **Diagnostic anchor** | 66.2% micro quantifies bridge contribution on Qwen; not deployable |
| **Qwen v1 matrix** | **Complete — reject port narrative** | Bridges help Qwen (+12.8pp full micro) but **do not** close GPT gap; seizure H1 still **>25pp** below GPT H1; prereg “proceed” thresholds not met |
| **Cap-25 gate** | **Pass** | 25/25 records (see cap-25 addendum) |

## Research takeaway

Deterministic benchmark bridges are **necessary but not sufficient** for local Qwen on ExECT S1: they explain ~13pp of Qwen’s scored F1 on full validation, versus ~24pp on GPT, with most of the residual model-track gap concentrated in **seizure_type** normalization (fused-phrase split, coarse surfaces, specificity collapse). Further Qwen gains likely require **model-side** or **prompt/policy** changes, not additional post bridges alone.

## Recommended next work

1. ~~Full validation pair~~ — complete.
2. Add registry rows for full-validation configs; mark comparison group **complete**.
3. Do **not** open further S1 interleaving arms on Qwen without a new hypothesis (e.g. seizure-targeted prompt slice, not re-tested H2 pre-vocab).
4. Revisit support-map queue for non–S1-interleaving work (S4 sparse families, Gan confirmatory, benchmark reproduction blockers).

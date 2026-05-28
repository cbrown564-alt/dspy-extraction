# ExECT S1 Interleaving Qwen Validation v1 — Cap-25 Inspection

Date: 2026-05-20  
Comparison group: `exect_s1_interleaving_qwen_validation_v1`  
**Full inspection (authoritative):** `docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md`  
Pre-registration: `docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_preregistration_20260520.md`  
GPT reference: `docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md`

## Run artifacts

| Arm | Scope | Run ID | Config |
| --- | --- | --- | --- |
| **L1 raw (bridge-free)** | cap-25 | `exect_s1_interleaving_l1_raw_no_bridges_cap25_qwen35b_ollama_20260520T210420Z` | `exect_s1_interleaving_l1_raw_no_bridges_cap25_qwen35b_ollama.json` |
| **H1 post bridge** | cap-25 | `exect_s1_interleaving_h1_post_bridge_cap25_qwen35b_ollama_20260520T210432Z` | `exect_s1_interleaving_h1_post_bridge_cap25_qwen35b_ollama.json` |

Fixed controls: ExECTv2 validation cap-25 (25 records), `exect_s0_s1_field_family`, `exect_field_family_deterministic_v1`, Qwen3.6:35b Ollama, prompt `exect_s0_s1_field_family_v4_10_label_policy`.

Varied factor: `repair_policy` — `raw_no_benchmark_bridges` vs `artifact_benchmark_bridge_only` (same single-pass program; bridges applied or skipped at artifact build).

## Headline metrics

| Arm | Micro F1 | Diagnosis | Seizure | Medication | Evidence support |
| --- | ---: | ---: | ---: | ---: | ---: |
| L1 raw | **71.4%** | 78.0% | 57.5% | 85.2% | 97.6% |
| H1 post bridge | **80.7%** | 95.2% | 66.7% | 87.3% | 98.7% |

**Bridge delta (H1 − L1 raw):** **+9.3pp** micro; seizure **+9.2pp**; diagnosis **+17.2pp**; medication **+2.1pp**.

## Cross-track reference (GPT v2 cap-25, same 25 records)

| Track | L1 raw micro | H1 post micro | Bridge Δ micro | Bridge Δ seizure |
| --- | ---: | ---: | ---: | ---: |
| GPT 4.1-mini | 72.8% | 95.8% | **+23.0pp** | **+39.1pp** |
| Qwen3.6:35b | 71.4% | 80.7% | **+9.3pp** | **+9.2pp** |

Qwen raw F1 is similar to GPT raw on this cap (−1.4pp micro), but **post bridges recover far less** on Qwen, especially seizure_type (GPT +39pp vs Qwen +9pp).

Frozen anchors for context:

| Anchor | Micro F1 | Seizure F1 | Notes |
| --- | ---: | ---: | --- |
| GPT production L1 full (40) | 92.3% | 90.5% | `…221944Z` |
| Qwen production L1 full (40) | 79.0% | 55.7% | `…042117Z`, inline bridges |
| Qwen H1 cap-25 | 80.7% | 66.7% | This run |

## Operational notes

- Both arms evaluated **25/25** records with structured outputs (cap-25 **schema gate passed**).
- Evidence support stable (97.6% → 98.7%, no regression).
- Runtimes ~0.3s for 25 predictions suggest **DSPy disk cache hits** on the same validation records; bridge deltas remain valid because scoring applies different `repair_policy` to the same underlying extraction artifacts.

## Decisions

| Item | Outcome | Rationale |
| --- | --- | --- |
| **Cap-25 gate** | **Pass** | 25/25 records; evidence OK |
| **Research signal (cap-25)** | **Hold** | Bridges help Qwen (+9.3pp micro) but **much less than GPT** (+23pp); seizure bridge delta +9.2pp vs GPT +39.1pp — does not meet prereg “proceed” thresholds |
| **Full validation (40)** | **Recommend** | Gate passed; n=40 needed before closing comparison group — cap-25 may understate bridge lift (GPT full bridge Δ was +23.7pp vs +23.0pp cap-25) |

## Recommended next work

1. ~~Run full-validation pair~~ — complete; see `docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md`.
2. ~~Write full inspection + update registry~~ — complete.
3. Do **not** treat Qwen H1 as a new default — production Qwen anchor already uses inline bridges (`repair_policy=none`).

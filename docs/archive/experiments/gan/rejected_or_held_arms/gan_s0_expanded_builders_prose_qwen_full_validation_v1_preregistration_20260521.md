# Gan S0 Expanded Builders Prose Qwen Full Validation v1 — Pre-Registration

Date: 2026-05-21  
Status: **Cap-25 done — full validation (299) ready** — inspection `docs/experiments/gan/gan_s0_expanded_builders_prose_qwen_cap25_v1_inspection_20260522.md`  
Comparison group: `gan_s0_expanded_builders_prose_model_comparison_v1`  
Gemini port: `docs/experiments/gan/gan_s0_expanded_builders_prose_gemini_full_validation_v1_inspection_20260521.md`  
GPT F0 prereg: `docs/experiments/gan/gan_s0_expanded_builders_prose_gpt_full_validation_v1_preregistration_20260521.md`  
Kanban: `docs/planning/kanban_plan.md` (§ Next step — Qwen Gan F0)

## Research question

On the full Gan 2026 fixed validation split (299 records), does **Qwen3.6:35b** on the frozen **F0** skeleton (`cand_prose_expanded_builders_v1`, `g2_candidates_adjudicate`) complete the **three-provider model-comparison table** alongside GPT and Gemini F0 ports?

## Hypothesis

Qwen may trail hosted GPT/Gemini on monthly accuracy (prior Qwen g2 cap-25 was **40%** monthly vs GPT **52%** on pre-expansion builders) but full-validation F0 with expanded builders is untested. Outcome is model-comparison evidence only (`decision_scope: arm`).

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Comparison group | `gan_s0_expanded_builders_prose_model_comparison_v1` |
| Primary varied factor | `model_track` = `qwen35b` |
| implementation_variant | `cand_prose_expanded_builders_v1` (fixed) |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Model | Qwen3.6:35b via Ollama (`configs/models/gan_s0_qwen35b_ollama.json`) |
| Scorer | `gan_frequency_deterministic_v1` |
| Program | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` |
| Builders | Post-2026-05-21 expanded `temporal_candidates.py` |
| ChainOfThought / optimizers | **None** (per Qwen latency policy) |

## External anchors (F0 full validation, same skeleton)

| Provider | Run suffix | Monthly | Schema | Evidence |
| --- | --- | ---: | ---: | ---: |
| GPT F0 | `…073432Z` | 68.1% | 99.7% | 100% |
| Gemini F0 | `…094020Z` | **72.6%** | 100% | 100% |
| Qwen g2 cap-25 (pre-expansion builders) | `…065534Z` | 40% | — | — | *Different builder surface — not F0-comparable* |
| Qwen F0 cap-25 | **`…091442Z`** | **48.0%** | **100%** | **100%** | Gates cleared 2026-05-22 |

## Arms and configs

| Step | Scope | Config | Launcher |
| --- | --- | --- | --- |
| 0 | Smoke (3 records) | `gan_s0_expanded_builders_prose_smoke_qwen35b_ollama.json` | IDE / dry-run OK |
| 1 | Cap-25 gate | `gan_s0_expanded_builders_prose_cap25_qwen35b_ollama.json` | `scripts/start_gan_s0_expanded_builders_prose_cap25_qwen35b_detached.ps1` |
| 2 | Full validation (299) | `gan_s0_expanded_builders_prose_full_validation_qwen35b_ollama.json` | `scripts/start_gan_s0_expanded_builders_prose_full_qwen35b_detached.ps1` |

Promote to full validation only after smoke passes and cap-25 clears schema ≥ 90% and evidence ≥ 85% gates (Qwen historical band).

## Primary metrics

| Metric | Role |
| --- | --- |
| Monthly frequency accuracy | **Primary** |
| Purist / Pragmatic category | Secondary |
| Schema-valid prediction rate | Gate ≥ 90% |
| Evidence quote support | Gate ≥ 85%; report vs GPT/Gemini 100% |
| Normalized-label exact | Diagnostic |

## Run hygiene (Windows / Ollama)

- **Do not** run cap-25 or full validation in Cursor background terminals.
- Use detached launchers; monitor via `runs/overnight_logs/gan_s0_expanded_builders_prose_*_qwen35b_*.log`.
- Record Ollama GPU residency or RAM offload in inspection.
- Do not overlap with other long local Qwen jobs on the same machine.

## Interpretation rules

- Same F0 skeleton as GPT/Gemini; only `model_track` differs.
- Do not compare to stale Qwen g2 cap-25 (pre-expansion builders) without caveat.
- Do not mechanism-close det-candidate generation from one Qwen arm.
- Three-provider table is complete only after this full-validation run.

## Skills

`model-config-compatibility`, `experiment-run-lifecycle`, `dspy-experiment-design`, `windows-portability`.

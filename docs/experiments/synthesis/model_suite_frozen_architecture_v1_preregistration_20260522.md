# Model Suite Frozen Architecture v1 — Umbrella Pre-Registration

Date: 2026-05-22  
Status: **Active** — governs confirmatory model-comparison replays on frozen programs  
Comparison group: `model_suite_frozen_architecture_v1`  
Kanban: `docs/planning/kanban_plan.md` (§ Key workstream)  
Research doctrine: `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`

## Research question

On **three frozen comparison surfaces** (ExECT S1, ExECT S4, Gan S0 F0), how do hosted and local model tracks compare when only `model_track` varies — same programs, scorers, splits, and prompt policies?

This is **model-comparison evidence only** (`decision_scope: arm`). It does not mechanism-close hybrid placement, swap operational defaults, or promote hosted arms from leaderboard position alone.

## Hypothesis

- **Hosted tracks** (Gemini 3 Flash, Gemini 3.1 Flash-Lite, GPT 5.5, Claude Sonnet 4.6) may diverge from GPT 4.1-mini on evidence support, sparse families, and billing-adjusted cost.
- **Local Qwen scaling ladder** (3.5:9b, 3.6:27b, 3.6:35b) tests latency vs performance tradeoffs: 9b best latency; 27b dense best benchmark performance; 35b MoE best performance/latency mix on CPU-offloaded Windows runtime.
- Outcomes inform paper-facing model profiles; they do not alone change engineering defaults.

## Taxonomy

| Field | Value |
| --- | --- |
| Comparison group | `model_suite_frozen_architecture_v1` |
| Primary varied factor | `model_track` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |
| Operational promotion from suite? | No — separate decision doc required |

## Frozen comparison surfaces (3 only)

ExECT S2 and S3 are **excluded**. Mid-ladder Qwen vs GPT numbers remain contextual only; reopen under `model_suite_exect_s2_s3_extension_v1` only if phase-5 synthesis requires a validated hosted check on S2/S3.

| Surface | Schema level | Frozen program / variant | Prompt policy | Scorer | Split | GPT 4.1-mini anchor |
| --- | --- | --- | --- | --- | --- | --- |
| **ExECT S1** | `exect_s0_s1_field_family` | `exect_s0_s1_field_family_single_pass` | `exect_s0_s1_field_family_v4_10_label_policy` | `exect_field_family_deterministic_v1` | `exectv2_fixed_v1:validation` (40) | **92.3%** micro (`…221944Z`) |
| **ExECT S4** | `exect_s4_field_family` | `exect_s4_field_family_cause_bridge_k0_k1_single_pass` | `exect_s4_field_family_v1_2_label_policy` | `exect_s4_field_family_deterministic_v1` | same | **65.5%** micro (`…071248Z`) |
| **Gan S0 F0** | `gan_frequency_s0` | `gan_frequency_s0_temporal_candidates_single_pass` + `g2_candidates_adjudicate` | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` + `cand_prose_expanded_builders_v1` | `gan_frequency_deterministic_v1` | `gan_2026_fixed_v1:validation` (299) | **68.1%** monthly (`…073432Z`) |

**ExECT S1 policy (all tracks):** v4_10 only. Qwen S1 v4_12 follow-up is **outside** this comparison group — cap-25 **reject (arm)** 2026-05-21 (`exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_inspection_20260521.md`).

**Do not** compare stale Round-2 or pre-F0 arms without explicit architecture caveat.

## Target model tracks

**GPT 4.1-mini** is the **search and reproducibility anchor** — fixed baseline, not a missing suite row.

| model_track | Provider | Config (representative) | Suite role |
| --- | --- | --- | --- |
| `gpt41mini` | OpenAI | `configs/models/gan_s0_gpt4_1_mini.json` | Anchor (not varied) |
| `gpt55` | OpenAI | `configs/models/gan_s0_gpt5_5_openai.json` | Hosted replay |
| `gemini31flashlite` | Google | `configs/models/gan_s0_gemini31_flash_lite.json` | Early member — replay **done** |
| `gemini3flash` | Google | `configs/models/gan_s0_gemini3_flash.json` | Hosted replay |
| `claude_sonnet46` | Anthropic | `configs/models/gan_s0_claude_sonnet_4_6_anthropic.json` | Required track; smoke ready |
| `qwen35b` | Ollama | `configs/models/gan_s0_qwen35b_ollama.json` | Local scaling — partial |
| `qwen27b` | Ollama | `configs/models/gan_s0_qwen27b_ollama.json`, `configs/models/exect_qwen27b_ollama.json` | Local scaling — full ladder ready |
| `qwen9b` | Ollama | `configs/models/gan_s0_qwen9b_ollama.json` | Local scaling — latency floor |

## Sub-documents (existing arms aligned to this group)

| Arm | Comparison group / doc | Status |
| --- | --- | --- |
| Gemini 3.1 ExECT S1/S4 | `exect_gemini_ladder_replay_v1` — `docs/experiments/exect/exect_gemini_ladder_replay_v1_preregistration_20260521.md` | **Done** |
| Gemini 3.1 Gan F0 | `gan_s0_expanded_builders_prose_model_comparison_v1` — Gemini inspection | **Done** — 72.6% monthly |
| Qwen 35b Gan F0 | `gan_s0_expanded_builders_prose_model_comparison_v1` — `docs/experiments/gan/gan_s0_expanded_builders_prose_qwen_cap25_v1_inspection_20260522.md` | Cap-25 **done** (48.0% monthly); full **ready** |
| Qwen S1 v4.12 | `exect_s1_qwen_v4_12_diagnosis_stabilized_*` | **Reject (arm)** — not in suite |

## Coverage matrix (target)

| Model | ExECT S1 | ExECT S4 | Gan F0 | Notes |
| --- | --- | --- | --- | --- |
| GPT 4.1-mini | **92.3%** | **65.5%** | **68.1%** | Anchor |
| Gemini 3.1 Flash-Lite | **90.3%** | **66.8%** | **72.6%** | Done — Gan F0 model-comparison only |
| Gemini 3 Flash | **89.9%** | **63.2%** | **75.3%** | Done — `model_suite_gemini3_flash_full_validation_v1_inspection_20260522.md` |
| GPT 5.5 | — | — | — | After Claude smokes |
| Claude Sonnet 4.6 | — | — | — | Smoke ready |
| Qwen 3.6:35b | 79.0% (v4.10) | 67.5% | cap-25 **48.0%**; full **ready** | `gan_s0_expanded_builders_prose_qwen_cap25_v1_inspection_20260522.md` |
| Qwen 3.6:27b | **ready** | **ready** | **ready** | Full configs + `scripts/start_qwen27b_model_suite_ladder_detached.ps1`; after 35b Gan F0 full |
| Qwen 3.5:9b | — | — | — | After 27b column |

## Execution sequencing

All execution on **one Windows laptop** unless noted.

| Lane | Rule |
| --- | --- |
| **Ollama** | One long job at a time — never overlap cap-25/full local runs |
| **Hosted API** | May run in parallel with an active Ollama job |
| **Claude plumbing** | **Smoke ready** — config and adapter are present; use existing `.env` with `ANTHROPIC_API_KEY` for live smokes |
| **New full hosted replays** | **Halted** until Claude smokes pass (Gemini 3 Flash, GPT 5.5 full validation) |
| **Gan F0 Qwen 35b cap-25** | **Continues now** — does not wait on Claude |

### Phase order

| Phase | Scope |
| --- | --- |
| **0 — Provider plumbing** | Claude Sonnet 4.6 smokes; Qwen 3.6:27b configs and smokes; Qwen 3.5:9b smoke (config exists) |
| **1 — Complete 35b column** | Gan F0 Qwen cap-25 → full (S1/S4 already at v4.10 full) |
| **2 — Hosted full replays** | Gemini 3 Flash + GPT 5.5 on S1/S4/Gan F0 — **after Claude smokes pass** |
| **3 — Claude full replay** | S1/S4/Gan F0 after phase 0 |
| **4 — Local scaling** | Qwen **27b** full ladder (`start_qwen27b_model_suite_ladder_detached.ps1`), then Qwen **9b** full ladder |
| **5 — Synthesis** | Model-profile memo + provider tables; registry `comparison_group` alignment |

## Run lifecycle gates

| Gate | Rule |
| --- | --- |
| Smoke | Provider/runtime compatibility; standard artifacts; no performance claim |
| Cap-25 (local Qwen) | Schema ≥ 90%, evidence ≥ 85% before full (Gan F0); detached launchers only |
| Full validation | Same split/scorer as GPT anchor; write inspection before Kanban update |
| S4 reporting | **Per-family F1 required** — pooled micro alone insufficient |
| Local metrics | Record latency, wall-clock, and CPU/GPU residency (Ollama offload %) on every local run |
| Hosted metrics | Record latency, tokens, and billing where available |

## Interpretation rules

- **Gemini 3.1 Gan F0 lead (72.6% vs GPT 68.1%):** model-comparison hold only — **no operational promotion** from suite results.
- **GPT 4.1-mini** remains operational/search anchor for Gan F0 and ExECT S1 v4_10.
- Do not mechanism-close hybrid placement from any single model track.
- Do not compare pooled ExECT micro across schema levels (S1 ≠ S4 family count).
- Suite synthesis may proceed with Claude column as "—" only if live Claude smokes remain blocked at a declared milestone — **preferred path is run the smoke-ready Claude configs first**.

## Deferred extension

| Card | Trigger |
| --- | --- |
| `model_suite_exect_s2_s3_extension_v1` | Paper needs hosted validation of mid-ladder Qwen≈GPT claim on S2/S3 |

## Skills

`model-config-compatibility`, `experiment-run-lifecycle`, `dspy-experiment-design`, `windows-portability`, `hybrid-pipeline-exploration`.

## Reference links

- Kanban: `docs/planning/kanban_plan.md`
- Model smokes: `docs/policies/model_config_smoke_tests.md`
- Gemini ladder inspection: `docs/experiments/exect/exect_gemini_ladder_replay_v1_inspection_20260521.md`
- Gan F0 Gemini inspection: `docs/experiments/gan/gan_s0_expanded_builders_prose_gemini_full_validation_v1_inspection_20260521.md`
- v4_12 reject: `docs/experiments/exect/exect_s1_qwen_v4_12_diagnosis_stabilized_cap25_inspection_20260521.md`

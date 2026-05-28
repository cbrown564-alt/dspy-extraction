# Gan S0 Qwen35b G2 Candidates-Adjudicate Cap-25 v1 — Preregistration

Date: 2026-05-21  
Status: Complete — `docs/experiments/gan/gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_inspection_20260521.md`  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` Phase 7  
Parent inspections:

- `docs/experiments/gan/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md`
- `docs/experiments/gan/gan_s0_implementation_variant_gpt_cap50_v1_inspection_20260521.md`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | Phase 7 — Qwen port of winning GPT cap-25 cell |
| Comparison group | `gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1` |
| Primary varied factor | `model_track` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| `implementation_variant` | `cand_prose_v1` |
| decision_scope | `arm` |

## Hypothesis

Qwen3.6:35b can port the GPT-discovered Gan S0 winner, deterministic temporal candidates followed by single-pass LLM adjudication, without losing schema validity or evidence support on the fixed validation cap-25 slice.

## Fixed Controls

- Dataset/split: `gan_2026_fixed_v1:validation`, first 25 records from `data/splits/gan_2026_splits.json`
- Schema/scorer: `gan_frequency_s0`, `gan_frequency_deterministic_v1`
- Program variant: `gan_frequency_s0_temporal_candidates_single_pass`
- Prompt version: `gan_frequency_s0_temporal_candidates_single_pass_v1_1`
- Context policy: full note plus deterministic temporal candidates
- Candidate source: deterministic `temporal_candidates.py`
- Repair/verifier policy: none, aside from artifact bridge surface normalization
- Few-shot/optimizer policy: none
- Structured output: provider JSON schema with Pydantic validation
- Local-model policy: no ChainOfThought, no BootstrapFewShot, no GEPA

## Config

`configs/experiments/gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1.json`

Model config: `configs/models/gan_s0_qwen35b_ollama.json`

## Reference Runs

| Reference | Run ID | Monthly | Notes |
| --- | --- | ---: | --- |
| GPT A3 stage graph | `gan_s0_stage_graph_g2_candidates_adjudicate_cap25_gpt4_1_mini_20260521T012204Z` | 52.0% | Axis 1 winner |
| GPT E1 executor repro | `gan_s0_stage_executor_e1_det_candidates_cap25_gpt4_1_mini_20260521T013003Z` | 52.0% | Axis 2 det-candidate anchor |
| GPT I0 cap-50 prose | `gan_s0_impl_i0_cand_prose_cap50_gpt4_1_mini_20260521T021111Z` | 62.0% | Format control; not same cap size |
| Qwen direct full anchor | `gan_s0_qwen35b_direct_full_validation_guardrails_20260519T102249Z` | 55.9% | Different stage graph; full validation |
| Qwen temporal+VR full anchor | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails_20260519T230324Z` | 65.8% | Operational default; different stage graph |

## Gates

This is a **portability cap**, not a mechanism-closing validation.

Pass/hold gate:

- 25/25 records produce Pydantic-valid predictions.
- Evidence support remains >= 96%.
- No systemic abstention or invalid-label cluster appears in `errors.json`.
- Monthly accuracy is interpretable against GPT E1 and prior Qwen anchors, with model-transfer caveats.

Promote-to-full-validation gate:

- Schema validity >= 95%.
- Evidence support >= 96%.
- Monthly accuracy is within 5pp of GPT E1 (>= 47%) or shows a clinically interpretable failure mode worth confirming.
- Latency is feasible for unattended full validation under the Qwen DSPy latency policy.

Reject/hold gate:

- Reject arm if schema validity < 95%, evidence support < 96%, or monthly accuracy drops below 44% without a clear artifact/bridge explanation.
- Hold without full validation if quality is acceptable but latency or artifact inspection suggests the full run would not answer a current decision.

## Interpretation Rules

- `decision_scope: arm`; do not claim mechanism promotion or rejection from this cap-25 port.
- Compare primarily to GPT E1 as the same stage graph/executor shape.
- Compare to Qwen direct and temporal+VR anchors only as operational context; those are different stage graphs.
- Do not update the Gan operational default unless a later full-validation inspection supports it.
- Do not describe this as published Gan benchmark reproduction.

## Expected Artifacts

- Run directory under `runs/gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_<timestamp>`
- `metadata.json`
- `config.json`
- `prompts.json`
- `predictions.json`
- `metrics.json`
- `errors.json`

## Launch Plan

1. Dry run:

   ```powershell
   uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1.json --env-file .env --dry-run
   ```

2. Detached run from an external PowerShell process or the repo launcher:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_detached.ps1
   ```

3. Monitor log:

   ```powershell
   Get-Content runs\overnight_logs\gan_s0_qwen35b_g2_candidates_adjudicate_cap25_v1_*.log -Tail 20 -Wait
   ```

## Open Cells

- Full validation of the same Qwen cell, gated by this cap-25 run.
- Qwen port of table/JSON/bullets candidate presentations; not run here because cap-50 GPT did not promote an operational format change.
- Alternate LLM candidate generation presentations; excluded because this port preserves the winning det-candidate stage executor.

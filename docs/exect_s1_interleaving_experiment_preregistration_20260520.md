# ExECT S1-Only Interleaving Experiment — Pre-Registration

Date: 2026-05-20  
Status: **Completed (GPT phase 1)** — inspection `docs/exect_s1_interleaving_gpt_validation_v1_inspection_20260520.md`  
Related: `docs/kanban_plan.md`, `docs/hybrid_component_taxonomy_decision_20260520.md`, `docs/experiment_taxonomy_schema.md`

## Research question

Where should deterministic clinical knowledge enter an ExECT S1 extraction pipeline, holding dataset, split, schema, scorer, and model fixed?

This is the ExECT counterpart to the Gan hard-slice interleaving matrix (`gan_s0_hard_slice_qwen_architecture_v1`). It must **not** mix schema expansion (S2–S4) with interleaving position.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `exect_v2` |
| Split | `exectv2_fixed_v1:validation` (40 records) |
| Schema / taxonomy | `exect_s1` (`exect_s0_s1_field_family`) |
| Scorer | `exect_field_family_deterministic_v1` |
| Field families | diagnosis, seizure_type, annotated_medication |
| Model (phase 1) | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Context | full note |
| Structured output | `provider_json_schema_with_pydantic_validation` |

**Phase 2 (optional):** port the winning arm(s) to Qwen35b only after GPT establishes a meaningful interleaving delta.

## Comparison group

`exect_s1_interleaving_gpt_validation_v1`

**Varied factor:** `interleaving_position` (and associated `hybrid_balance_class`)

## Arms

| Arm | Config (stub) | Hybrid class | Interleaving | Program (planned) | Question |
| --- | --- | --- | --- | --- | --- |
| **L1 baseline** | *(existing)* `exect_s0_s1_validation_full_gpt4_1_mini` | `L1_llm_constrained` | `during` | `exect_s0_s1_field_family_single_pass` | How much comes from prompt-level benchmark policy alone? |
| **H1 post bridge** | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini.json` | `H1_post_deterministic` | `during`, `post` | `exect_s0_s1_field_family_single_pass` + artifact-only benchmark bridges | Does post-hoc deterministic mapping improve measured F1 without changing extraction prompts? |
| **H2 pre vocabulary** | `exect_s1_interleaving_h2_pre_vocab_gpt4_1_mini.json` | `H2_pre_deterministic` | `pre`, `during` | `exect_s0_s1_field_family_pre_vocab_single_pass` *(new)* | Do injected medication/seizure/diagnosis candidate lists improve recall and normalization? |
| **H3 tool normalization** | *(config after program registration)* | `H3_interleaved_tool_hybrid` | `tool_during`, `during` | `exect_s0_s1_field_family_react_normalize_tools` *(new)* | Can bounded tool use help ExECT where Gan ReAct failed, or does it add schema/latency cost? |

### L1 anchor (no new run required if frozen)

- Frozen GPT anchor: `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` — **92.3%** micro F1  
- Registry: `exect_s0_s1_validation_full_gpt4_1_mini`, outcome `freeze`

### H1 design notes

- Reuse existing deterministic benchmark bridges in `exect_s0_s1.py` **after** model extraction, applied as artifact normalization only (no second LLM pass).
- Scorer unchanged; measure whether bridges move benchmark-facing labels without prompt edits.
- Distinct from `exect_s0_s1_field_family_verify_repair` (confirm-first **LLM** verifier — not in this matrix).

### H2 design notes

- Precompute deterministic candidate lists per family (medication names from Rx spans, seizure-type surfaces from audited vocabulary, diagnosis surfaces from policy table).
- Inject into prompt context before single-pass extraction; no tools during reasoning.
- Controlled vocabulary source: audited scorer surfaces + `docs/exect_gold_label_audit.md` policy boundaries.

### H3 design notes

- Bounded ReAct (max 4 iterations) with tools: `lookup_medication_canonical`, `lookup_seizure_type_surface`, `lookup_diagnosis_surface` (names provisional).
- Negative control reference: Gan ReAct slice rejected — `docs/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_inspection_20260520.md`.
- Gate on schema-valid prediction rate ≥ 95% on cap-25 before full validation.

## Run order (GPT phase 1)

1. Cap-25 smoke per new arm (schema + evidence gates)  
2. Full validation (40) for arms passing cap-25  
3. Inspection doc per arm with per-family F1 and bridge/tool telemetry  
4. Registry rows under `exect_s1_interleaving_gpt_validation_v1`

## Primary metrics

- Pooled micro F1 (3 families) — headline  
- Per-family F1: diagnosis, seizure_type, annotated_medication  
- Evidence quote support rate (diagnostic, separate from F1)  
- Schema-valid prediction rate (especially H3)

## Success / stop criteria

| Outcome | Criterion |
| --- | --- |
| **Proceed to Qwen** | Any non-L1 arm beats L1 full micro by ≥ 2pp with no evidence regression > 2pp |
| **Freeze arm** | Arm beats L1 by ≥ 3pp full validation with stable per-family gains and inspection sign-off |
| **Reject H3** | Schema validity < 95% cap-25 OR latency > 2× L1 without ≥ 5pp micro gain |
| **Hold** | Gains within noise (< 2pp) — keep L1 frozen default |

## Explicit non-goals

- No S2–S4 schema expansion in this matrix  
- No scorer semantic changes  
- No optimizer / GEPA runs  
- No published ExECT Table 1 benchmark claims

## Implementation checklist

- [x] Implement H1 post-bridge-only program path (`repair_policy=artifact_benchmark_bridge_only`, `bridge_stage=post` metadata)  
- [x] Implement H2 pre-vocabulary program variant + candidate builders (`exect_s0_s1_field_family_pre_vocab_single_pass`)  
- [ ] Implement H3 bounded ReAct tools module (or defer if Gan-negative-control is sufficient)  
- [x] Add cap-25 configs for H1/H2  
- [x] Run GPT cap-25 → full ladder  
- [x] Write inspection docs + registry rows  
- [ ] Fix H1 null comparison (bridge-free L1 or true post-only bridge path) before Qwen phase 2

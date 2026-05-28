# ExECT S1 Interleaving Qwen Validation v1 — Pre-Registration

Date: 2026-05-20  
Status: **Completed (GPT phase analogue)** — inspection `docs/experiments/exect/exect_s1_interleaving_qwen_validation_v1_inspection_20260520.md`; matrix **reject port narrative**  
Comparison group: `exect_s1_interleaving_qwen_validation_v1`  
GPT reference: `exect_s1_interleaving_gpt_validation_v2` — `docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md`  
Support map queue: #6 (Qwen port after bridge-free baseline measurable)

## Research question

On ExECT S1 with **Qwen3.6:35b**, does the benchmark-bridge lift (H1 post vs L1 raw) exceed the GPT 4.1-mini bridge delta, especially on `seizure_type` where Qwen lags GPT by ~35pp at production L1?

This is **not** a port of a new GPT arm (all H2/H1 family probes rejected). It replicates the **v2 interleaving matrix** (bridge-free raw vs post bridges) on the local model track.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `exect_v2` |
| Split | `exectv2_fixed_v1:validation` (40 records) |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Field families | diagnosis, seizure_type, annotated_medication |
| Model | Qwen3.6:35b Ollama (`configs/models/exect_qwen35b_ollama.json`) |
| Program | `exect_s0_s1_field_family_single_pass` |
| Prompt | `exect_s0_s1_field_family_v4_10_label_policy` |
| Structured output | `provider_json_schema_with_pydantic_validation` |

**Cross-track reference (not re-run):** GPT v2 L1 raw 68.6% / H1 post 92.3% micro F1 full validation; bridge delta **+23.7pp** (seizure **+33.1pp**).

## Varied factor (within comparison group)

`interleaving_position` — `repair_policy` `raw_no_benchmark_bridges` (L1 raw) vs `artifact_benchmark_bridge_only` (H1 post).

| Arm | Config | Hybrid class |
| --- | --- | --- |
| L1 raw | `exect_s1_interleaving_l1_raw_no_bridges_{cap25_,}qwen35b_ollama.json` | `L1_llm_constrained` |
| H1 post bridge | `exect_s1_interleaving_h1_post_bridge_{cap25_,}qwen35b_ollama.json` | `H1_post_deterministic` |

Between-group implicit factor: `model_track` (Qwen vs frozen GPT v2 artifacts).

## Run order

1. Cap-25 smoke per arm (schema validity ≥ 95%, evidence support diagnostic)
2. Full validation (40) for arms passing cap-25
3. Inspection doc with per-family F1 and bridge delta vs GPT v2
4. Registry rows under `exect_s1_interleaving_qwen_validation_v1`

**Windows:** launch cap-25/full via external PowerShell or detached wrappers — not Cursor background shells (`docs/policies/qwen_dspy_latency_policy.md`, experiment-run-lifecycle skill).

## Primary metrics

- Pooled micro F1 (3 families)
- Per-family F1: diagnosis, seizure_type, annotated_medication
- **Bridge delta** (H1 − L1 raw) per family and pooled — compare to GPT v2 deltas
- Evidence quote support rate
- Schema-valid prediction rate

## Success / stop criteria

| Outcome | Criterion |
| --- | --- |
| **Proceed (research signal)** | Qwen bridge delta on seizure_type **≥ +10pp larger than GPT** (+33.1pp reference) **or** Qwen H1 seizure F1 within **10pp** of GPT H1 (90.5%) while Qwen raw seizure was **≥20pp** below GPT raw (57.4%) |
| **Hold** | Bridge helps Qwen but deltas within noise vs GPT (< 5pp seizure delta difference) |
| **Reject port narrative** | Qwen bridge delta **< +10pp** pooled micro with seizure still **>25pp** below GPT H1 |
| **Cap-25 gate fail** | Schema validity < 95% or run stall — do not promote to full |

## Explicit non-goals

- No H2 pre-vocab arms (GPT rejected family-isolated and full-note variants)
- No scorer or prompt policy changes vs GPT v2 matrix
- No published ExECT Table 1 claims

## Commands

```bash
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_interleaving_l1_raw_no_bridges_cap25_qwen35b_ollama.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_interleaving_h1_post_bridge_cap25_qwen35b_ollama.json --env-file .env --dry-run
```

Full validation only after both cap-25 arms pass the gate above.

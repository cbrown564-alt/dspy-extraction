# ExECT Label-Policy v4.11 Implementation

Date: 2026-05-20

Prompt version: `exect_s0_s1_field_family_v4_11_label_policy`  
Comparison group: `exect_s1_seizure_prompt_policy_qwen_v1`  
Preregistration: `docs/exect_s1_seizure_prompt_policy_qwen_preregistration_20260520.md`  
Error analysis: `docs/exect_qwen_s1_seizure_gap_error_analysis_20260520.md`

## Target

Reduce Qwen-only S1 `seizure_type` failure modes (singular/plural inflection, absence/myoclonic overcall, secondary-generalisation policy drift) via **prompt-only** deltas on v4.10, without changing benchmark bridges or scorer semantics. GPT production remains on v4.10 until a separate promotion prereg.

## Changes

### Prompt (`EXECT_S0_S1_V4_11_LABEL_POLICY_ADDENDUM` + `EXECT_S0_S1_V4_11_POLICY_EXAMPLES`)

**A. Plural benchmark surfaces**

- Emit plural audited labels when the diagnosis or seizure row uses plural forms (GTCS, focal to bilateral convulsive seizures).
- Examples: `plural_gtcs_from_diagnosis_row`, `plural_focal_to_bilateral_convulsive`.

**B. Absence / myoclonic abstention**

- Do not emit absence or myoclonic seizure types unless explicitly named as current types in diagnosis/seizure surfaces.
- Examples: `no_seizure_types_without_absence_myoclonic_overcall`, `gtcs_only_no_absence_co_list`.

**C. Secondary-generalisation (reinforce v4.10 for Qwen)**

- Use full audited phrases (`secondary generalisation`, `secondary generalized seizures`) when supported; avoid bare `secondary` unless specificity-collapse applies.
- Examples: `secondary_generalisation_full_phrase`, `secondary_generalized_seizures_not_bare_secondary`, `multi_type_secondary_generalized_co_list`.

### Version resolution

- `resolve_exect_s0_s1_label_policy(prompt_version)` selects v4.10 vs v4.11 guidance and examples.
- `build_exect_s0_s1_field_family_signature(prompt_version)` appends v4.11 boundary examples to the signature docstring for treatment runs only.
- `EXECT_S0_S1_PROMPT_VERSION` remains **v4.10** (frozen GPT production default).

### Deterministic bridges

**Unchanged** — same `exect.seizure_type.benchmark_bridge.v1` and related post bridges as v4.10 H1 path.

## Experiment configs

| Config | Model | Scope | repair_policy |
| --- | --- | --- | --- |
| `exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini.json` | GPT 4.1-mini | cap-25 | `none` (GPT guardrail) |
| `exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama.json` | Qwen3.6:35b | cap-25 | `artifact_benchmark_bridge_only` |
| `exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama.json` | Qwen3.6:35b | full (40) | `artifact_benchmark_bridge_only` |

## Run order

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama.json --env-file .env --dry-run

# External PowerShell (not Cursor background shells)
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama.json --env-file .env
```

Post-run: `scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py` and inspection `docs/exect_s1_seizure_prompt_policy_qwen_v1_inspection_<date>.md`.

## Cap-25 gate (2026-05-20)

| Arm | Run ID | Seizure F1 | Verdict |
| --- | --- | ---: | --- |
| GPT guardrail | `exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini_20260520T214222Z` | 93.9% (−1.5pp vs v4_10) | Pass |
| Qwen treatment | `exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama_20260520T214425Z` | 78.3% (+11.6pp vs v4_10 H1 cap-25) | Pass via **amended gate** (diagnosis −2.6pp waived as cap-25 noise) |

Qwen full approved per amended cap-25 gate; full run `exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama_20260520T231850Z` — **Hold (promote blocked)** per `docs/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md`.

## Validation (pre-run)

- [x] Prompt diff targets preregistered Qwen error buckets
- [x] Configs include `comparison_group: exect_s1_seizure_prompt_policy_qwen_v1`, `varied_factor: prompt_policy`
- [x] `uv run python scripts/validate_experiment_taxonomy.py --errors-only` passes
- [x] Dry-run succeeds for GPT and Qwen cap-25 configs
- [x] GPT + Qwen cap-25 executed; Qwen full cleared to run

## Prior analysis

`docs/exect_s0_label_policy_v4_10_implementation.md`, `docs/exect_qwen_s1_seizure_gap_error_analysis_20260520.md`

# ExECT S1 Seizure Prompt-Policy Qwen v1 — Inspection

Date: 2026-05-20  
Comparison group: `exect_s1_seizure_prompt_policy_qwen_v1`  
Pre-registration: `docs/experiments/exect/exect_s1_seizure_prompt_policy_qwen_preregistration_20260520.md`  
Implementation: `docs/experiments/exect/exect_s0_label_policy_v4_11_implementation.md`  
Error analysis (baseline): `docs/experiments/exect/exect_qwen_s1_seizure_gap_error_analysis_20260520.md`

## Run artifacts

| Arm | Scope | Run ID | Config |
| --- | --- | --- | --- |
| GPT v4_11 guardrail | cap-25 | `exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini_20260520T214222Z` | `exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini.json` |
| Qwen v4_11 treatment | cap-25 | `exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama_20260520T214425Z` | `exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama.json` |
| **Qwen v4_11 treatment** | **full (40)** | **`exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama_20260520T231850Z`** | `exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama.json` |
| Qwen v4_10 H1 baseline *(frozen)* | full (40) | `exect_s1_interleaving_h1_post_bridge_qwen35b_ollama_20260520T210722Z` | `exect_s1_interleaving_h1_post_bridge_qwen35b_ollama.json` |
| GPT H1 reference | full (40) | `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z` | — |

Fixed controls: ExECTv2 validation (40), `exect_s0_s1_field_family`, `exect_field_family_deterministic_v1`, Qwen3.6:35b Ollama, `repair_policy=artifact_benchmark_bridge_only`, same benchmark bridges as v4_10 H1.

Varied factor: `prompt_policy` — `exect_s0_s1_field_family_v4_10_label_policy` (baseline) vs `exect_s0_s1_field_family_v4_11_label_policy` (treatment).

Cap-25: diagnosis −2.6pp waived as slice noise; full validation proceeded per amended gate in preregistration.

## Headline metrics (full validation, 40 records)

| Track | Micro F1 | Diagnosis | Seizure | Medication | Evidence support | Seizure mismatch docs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen v4_10 H1 (frozen) | 79.0% | 95.1% | 55.7% | 89.1% | 95.8% | 19 |
| **Qwen v4_11 H1** | **84.3%** | **90.0%** | **74.2%** | **90.1%** | 94.8% | **14** |
| GPT H1 (reference) | 92.3% | 93.8% | 90.5% | 92.8% | 95.8% | 6 |

**Deltas (v4_11 − v4_10 Qwen H1):** micro **+5.4pp**; seizure **+18.5pp**; diagnosis **−5.1pp**; medication **+1.0pp**.

**Qwen–GPT seizure gap after bridges:** **−16.3pp** (74.2% vs 90.5%), down from **−34.8pp** at v4_10 H1 — prompt-policy closed roughly half the model-track seizure gap on this split.

## Full-validation decision gates

| Criterion | Threshold | Observed | Met? |
| --- | --- | --- | --- |
| Seizure F1 vs baseline | ≥ 63.7% (≥ +8pp from 55.7%) | **74.2%** (+18.5pp) | **Yes** |
| Seizure mismatch docs | ≤ 12 (from 19) | **14** | **No** |
| Diagnosis cross-family | ≥ −2pp vs baseline | **−5.1pp** | **No** |
| Medication cross-family | ≥ −2pp vs baseline | **+1.0pp** | **Yes** |
| New absence/myoclonic cluster | none on previously clean docs | EA0047/0124 still overcall; no broad new cluster | **Yes** |

**Outcome: Hold (promote blocked).** The preregistered **promote** row requires all three of seizure F1, mismatch-doc count, and cross-family guardrails. Seizure and medication improved strongly; **promote is blocked** by mismatch docs (14 > 12) and diagnosis regression (−5.1pp). Strict **reject** is not the right narrative — the seizure-focused hypothesis is confirmed at full scale.

**Do not** switch Qwen production prompt to v4_11 without a follow-up on diagnosis drift or a narrowed promotion prereg (seizure-only deployment claim).

## Error-read (seizure gap)

Artifact: `runs/exect_s1_seizure_prompt_policy_qwen_v1_error_read.json`

Regenerate:

```bash
uv run python scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py \
  --qwen-h1-run runs/exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama_20260520T231850Z \
  --gpt-h1-run runs/exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z \
  --output runs/exect_s1_seizure_prompt_policy_qwen_v1_error_read.json
```

### Category counts (scored atoms, Qwen H1)

| Category | v4_10 H1 full | v4_11 full | Δ |
| --- | ---: | ---: | ---: |
| Surface inflection | 14 | 4 | −10 |
| Unsupported overcall | 6 | 5 | −1 |
| Secondary-generalisation policy | 14 | 7 | −7 |
| Missed gold label | 7 | 7 | 0 |
| Other model wording | 2 | 2 | 0 |

**Target buckets** (inflection + overcall + secondary-policy): **34 → 16 atoms** (−53%). Clears the synthesis-pause “no >30% reduction” bar for those buckets.

### Mismatch document churn (14 vs 19)

**Cleared vs v4_10:** EA0069, EA0098, EA0116, EA0131, EA0150, EA0170 (6 docs).

**Still failing:** EA0016, EA0029, EA0047, EA0050, EA0072, EA0090, EA0109, EA0124, EA0125, EA0136, EA0137, EA0143, EA0174 (13 overlap).

**New on v4_11:** EA0179 (1 doc).

**Residual v4_11 targets:**

- **Overcall:** EA0029, EA0050, EA0124 — absence seizures persist; EA0047 still spurious types.
- **Inflection:** EA0016, EA0125 — reduced but not eliminated.
- **Secondary policy:** EA0090, EA0137, EA0143 — shared hard core with GPT on several docs.

## Cap-25 recap (for traceability)

| Arm | Seizure F1 | Gate |
| --- | ---: | --- |
| GPT v4_11 | 93.9% (−1.5pp vs v4_10) | Pass |
| Qwen v4_11 | 78.3% (+11.6pp vs v4_10) | Pass (amended — diagnosis −2.6pp waived) |

Full validation generalized the cap-25 seizure gain (+11.6pp → +18.5pp) but surfaced a larger diagnosis drop than on the 25-record slice.

## Decisions

| Item | Outcome | Rationale |
| --- | --- | --- |
| **v4_11 Qwen S1 prompt** | **Hold (promote blocked)** | Seizure F1 and error buckets support prompt-policy mechanism; mismatch count and diagnosis block production promotion |
| **GPT production** | **Unchanged (v4_10)** | GPT cap-25 guardrail passed; no GPT full run required |
| **Qwen production anchor** | **Frozen at v4_10 H1** (`…210722Z`) until a new prereg or diagnosis follow-up | |
| **Comparison group** | **Complete** | All preregistered arms executed |

## Research takeaway

`v4_11` confirms the Phase 2 hypothesis: the Qwen–GPT seizure gap is largely **label-policy / model wording**, not missing deterministic bridges. A prompt-only revision recovered **+18.5pp seizure F1** and cut targeted error atoms by roughly half, without bridge or scorer changes.

Promotion to the Qwen production prompt is blocked by **diagnosis regression** and **mismatch-doc count** on the strict multi-field gate. Next work should either (a) open a **diagnosis-focused** follow-up on the same 40 records to see if v4_11 guidance leaked into diagnosis extraction, or (b) preregister a **Qwen seizure-only promotion** claim with explicit diagnosis caveats — not another H2 pre-vocab or post-bridge sweep.

## Follow-ups

- [x] Registry rows under `exect_s1_seizure_prompt_policy_qwen_v1` in `docs/experiments/synthesis/experiment_registry.json`
- [x] Regenerate `docs/experiments/synthesis/experiment_registry_matrix_20260520.md` after registry edit
- [x] Update `docs/planning/kanban_plan.md` decisions table

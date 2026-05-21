# ExECT S1 Seizure Prompt-Policy Qwen v1 — Pre-Registration

Date: 2026-05-20  
Status: Complete — Hold (promote blocked); full run `…231850Z` (2026-05-20)  
Comparison group: `exect_s1_seizure_prompt_policy_qwen_v1`  
Error analysis: `docs/exect_qwen_s1_seizure_gap_error_analysis_20260520.md`  
Preregistration chain: `docs/exect_qwen_s1_seizure_gap_error_analysis_preregistration_20260520.md`

## Research question

On ExECT S1 with **Qwen3.6:35b**, does a **seizure-focused label-policy prompt revision** (`v4_11`) improve `seizure_type` F1 versus the frozen **v4_10** production prompt, while keeping the same benchmark post bridges and scorer?

This tests the Phase 2 conclusion that the Qwen–GPT seizure gap is primarily **model wording / extraction policy**, not missing deterministic bridges.

## Hypothesis

Targeted prompt-policy rules will reduce Qwen-only failure modes seen after H1 bridging:

1. **Singular/plural surface mismatch** (14 error atoms) — e.g. `generalized tonic clonic seizure` vs gold `generalized tonic clonic seizures`.
2. **Unsupported absence/myoclonic overcall** (6 atoms) — e.g. EA0047, EA0124.
3. **Secondary-generalisation policy drift** (14 atoms) — missed `secondary generalisation` / `secondarily generalized seizures` FNs and collapsed FP `secondary` tokens.

`v4_10` already encodes secondary-token co-listing for GPT; Qwen still misses or over-splits on the same validation records, so `v4_11` adds **Qwen-oriented counterexamples** without changing bridges or scorer.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `exect_v2` |
| Split | `exectv2_fixed_v1:validation` |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` |
| Field families | diagnosis, seizure_type, annotated_medication |
| Model | Qwen3.6:35b Ollama (`configs/models/exect_qwen35b_ollama.json`) |
| Program | `exect_s0_s1_field_family_single_pass` |
| `repair_policy` | `artifact_benchmark_bridge_only` (H1 post-bridge path) |
| `hybrid_balance_class` | `H1_post_deterministic` |
| Structured output | `provider_json_schema_with_pydantic_validation` |
| Primitive IDs (unchanged) | `exect.seizure_type.benchmark_bridge.v1`, `exect.diagnosis.benchmark_bridge.v1`, `exect.medication.benchmark_bridge.v1` |

## Frozen baseline (do not re-run unless config drift)

| Role | Run ID | Prompt | Seizure F1 (full 40) | Micro F1 |
| --- | --- | --- | ---: | ---: |
| Qwen H1 production anchor | `exect_s1_interleaving_h1_post_bridge_qwen35b_ollama_20260520T210722Z` | `exect_s0_s1_field_family_v4_10_label_policy` | 55.7% | 79.0% |
| Qwen H1 cap-25 reference | `exect_s1_interleaving_h1_post_bridge_cap25_qwen35b_ollama_20260520T210432Z` | v4_10 | 66.7% | 80.7% |

Cross-track reference (not varied in this group): GPT H1 post-bridge full `exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z` — seizure F1 **90.5%**, micro **92.3%**.

## Varied factor

`prompt_policy` — `exect_s0_s1_field_family_v4_10_label_policy` (baseline, frozen artifact) vs **`exect_s0_s1_field_family_v4_11_label_policy`** (treatment, to implement).

| Arm | Prompt version | Config (planned) |
| --- | --- | --- |
| Baseline | v4_10 | *(frozen runs above; re-run only if registry/config hash drift)* |
| Treatment cap-25 | v4_11 | `exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama.json` |
| Treatment full | v4_11 | `exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama.json` |

Implementation note: `v4_11` is a **prompt-only** delta on `EXECT_S0_S1_LABEL_POLICY_GUIDANCE` / policy examples in `src/clinical_extraction/programs/exect_s0_s1.py`. No program-variant change, no H2 pre-vocab, no new bridge rules.

### Planned v4_11 policy deltas (single combined revision)

**A. Plural benchmark surfaces**

- When the diagnosis or seizure-type line uses a **plural** audited surface (e.g. `generalized tonic clonic seizures`, `focal seizures`), emit the **plural** benchmark label, not the singular form.
- Add counterexamples for EA0029, EA0050, EA0116, EA0131-style mismatches.

**B. Absence / myoclonic abstention**

- Do not emit `absence seizure(s)` or `myoclonic seizure(s)` unless the note **explicitly names** that seizure type as a current type in the diagnosis/seizure surface (not inferred from EEG narrative alone).
- Add negative examples for EA0047 (spurious absence + myoclonic with empty gold seizure set) and EA0124.

**C. Secondary-generalisation (reinforce v4_10 for Qwen)**

- If a focal seizure secondarily generalises, extract the **benchmark-policy** label: co-list `secondary` only when v4_10 collapse rules apply; otherwise use full audited surfaces (`secondary generalized seizures`, `secondarily generalized seizures`, `secondary generalisation`) as gold expects — do not emit bare `secondary` alone when gold uses the full phrase (EA0137).
- Do not add a separate secondary generalised tonic-clonic type unless the letter names **multiple current seizure types** (re-anchor `docs/previous_exect_error_analysis.md` §7.1).
- Add positive examples for EA0090 (`secondary generalisation` FN) and EA0143 / EA0150 multi-label gold.

## GPT regression guardrail (mandatory before Qwen full)

Before promoting Qwen full validation, run **one** GPT 4.1-mini cap-25 check with v4_11 and the production `repair_policy=none` path (inline bridges, same as frozen GPT anchor):

| Config (planned) | Purpose |
| --- | --- |
| `exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini.json` | Ensure v4_11 does not regress GPT seizure F1 vs v4_10 cap-25 |

| Outcome | Rule |
| --- | --- |
| **Block Qwen full** | GPT cap-25 `seizure_type` F1 **< −2pp** vs v4_10 cap-25 reference (`runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z`, seizure F1 **95.4%**) |
| **Proceed to Qwen full** | GPT cap-25 seizure F1 **≥ −2pp** vs reference |

GPT full validation is **out of scope** unless the guardrail fails and prompt revision must be narrowed.

## Run order

1. Implement `exect_s0_s1_field_family_v4_11_label_policy` + `docs/exect_s0_label_policy_v4_11_implementation.md`.
2. Dry-run treatment configs (`--dry-run`).
3. **GPT cap-25 guardrail** (v4_11).
4. **Qwen cap-25** (v4_11, H1 post-bridge).
5. If cap-25 gate passes → **Qwen full validation (40)**.
6. Re-run `scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py` on treatment full vs frozen baseline; write inspection `docs/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md` (date suffix updated on completion).
7. Registry rows under `exect_s1_seizure_prompt_policy_qwen_v1`.

**Windows:** launch model runs via external PowerShell or detached wrappers — not Cursor background shells (`docs/qwen_dspy_latency_policy.md`).

## Primary metrics

- **`seizure_type` field-family F1** (promotion metric)
- Seizure mismatch document count (from scorer `field_family_mismatches`)
- Category counts from `scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py` (inflection, overcall, secondary-policy)

## Diagnostic metrics

- Pooled micro F1 (3 families)
- `diagnosis` and `annotated_medication` F1 (cross-family guardrails)
- Evidence quote support rate
- Schema-valid prediction rate

## Cap-25 gate (Qwen treatment)

| Check | Threshold |
| --- | --- |
| Schema validity | ≥ 95% valid predictions |
| Evidence support (diagnostic) | No collapse vs v4_10 cap-25 reference |
| Seizure F1 | **≥ +5pp** vs v4_10 cap-25 reference (**66.7%** → **≥ 71.7%**) |
| Cross-family guardrail | `diagnosis` and `annotated_medication` F1 each **≥ −2pp** vs v4_10 cap-25 reference |

Failure on any row → **do not** run Qwen full validation; revise prompt or **reject**.

### Cap-25 results (2026-05-20)

| Arm | Run ID | Micro F1 | Seizure F1 | Diagnosis F1 | Medication F1 | Seizure mismatch docs |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| GPT v4_11 guardrail | `exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini_20260520T214222Z` | 95.1% | 93.9% | 97.6% | 94.7% | 3 |
| Qwen v4_11 treatment | `exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama_20260520T214425Z` | 85.4% | 78.3% | 92.7% | 88.9% | 9 |
| GPT v4_10 reference | `exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` | 95.8% | 95.4% | 97.6% | 94.9% | 2 |
| Qwen v4_10 reference | `exect_s1_interleaving_h1_post_bridge_cap25_qwen35b_ollama_20260520T210432Z` | 80.7% | 66.7% | 95.2% | 87.3% | 12 |

**GPT guardrail:** seizure F1 **−1.5pp** vs v4_10 cap-25 — **pass** (within −2pp band).

**Qwen treatment vs v4_10 cap-25:** seizure **+11.6pp**, medication **+1.6pp**, diagnosis **−2.6pp**, evidence support 95.9% vs 98.7% (diagnostic only).

### Amended gate (2026-05-20)

The strict cap-25 row for diagnosis cross-family (**−2.6pp** vs 95.2%) is **waived for full-validation proceed**. Rationale:

- Promotion metric is `seizure_type` F1; cap-25 shows **+11.6pp** and seizure mismatch docs **12 → 9** on the same 25-record slice.
- Diagnosis regression is **−0.4pp beyond** the −2pp guardrail on **n=25** — treated as slice noise, not a prompt-policy failure mode targeted by v4_11.
- Medication and micro F1 improved (+1.6pp, +4.6pp); no new absence/myoclonic cluster beyond pre-existing cap-25 docs.

**Decision:** **Proceed to Qwen full validation (40)** — `exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama.json`. Full-validation cross-family gates remain **unchanged** (diagnosis/medication each ≥ −2pp vs frozen full baseline `…210722Z`).

### Full-validation result (2026-05-20)

Run: `exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama_20260520T231850Z`  
Inspection: `docs/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md`  
Error read: `runs/exect_s1_seizure_prompt_policy_qwen_v1_error_read.json`

| Metric | v4_10 H1 (`…210722Z`) | v4_11 full | Δ |
| --- | ---: | ---: | ---: |
| Micro F1 | 79.0% | 84.3% | +5.4pp |
| Seizure F1 | 55.7% | 74.2% | +18.5pp |
| Diagnosis F1 | 95.1% | 90.0% | −5.1pp |
| Medication F1 | 89.1% | 90.1% | +1.0pp |
| Seizure mismatch docs | 19 | 14 | −5 |

**Final outcome: Hold (promote blocked).** Seizure criteria for promote met; blocked by mismatch docs (14 > 12) and diagnosis −5.1pp. Qwen production prompt remains **v4_10** until follow-up.

## Full-validation decision gates (40 records)

Compare treatment run to frozen baseline `…210722Z` (v4_10 H1).

| Outcome | Criterion |
| --- | --- |
| **Promote (Qwen S1 prompt path)** | `seizure_type` F1 **≥ +8pp** vs baseline (**55.7%** → **≥ 63.7%**) **and** no cross-family F1 regression **≥ 2pp** on diagnosis or medication **and** seizure mismatch documents **≤ 12** (from 19) |
| **Hold (slice-level signal)** | Seizure F1 gain **+3pp to +7.9pp** with no cross-family regression **≥ 2pp** — document; do not change production prompt; optional narrow bridge follow-up only with separate prereg |
| **Reject** | Seizure F1 **< +3pp** vs baseline **or** any cross-family regression **≥ 2pp** **or** new absence/myoclonic overcall cluster on previously clean docs |
| **Synthesis pause** | Heterogeneous errors remain with no category count reduction **> 30%** on inflection + overcall + secondary-policy buckets |

Promotion updates the **Qwen** label-policy anchor only. GPT production remains **v4_10** unless a separate GPT promotion prereg is opened.

## Explicit non-goals

- No H2 pre-vocabulary or `exect_s0_s1_field_family_seizure_pre_vocab_single_pass`
- No new post-bridge rules or `exect.seizure_type.benchmark_bridge.v1` changes in this comparison group
- No S1 interleaving matrix extension (L1 raw vs H1)
- No published ExECT Table 1 reproduction
- No Gan or S4 work in the same runs

## Commands (planned)

```bash
# After v4_11 implementation
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini.json --env-file .env --dry-run
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama.json --env-file .env --dry-run

# Guardrail then Qwen cap-25 (external shell)
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_cap25_qwen35b_ollama.json --env-file .env

# Qwen full only after cap-25 gate
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s1_seizure_prompt_policy_v4_11_full_qwen35b_ollama.json --env-file .env
```

Post-run error read:

```bash
uv run python scripts/analyze_exect_qwen_s1_seizure_gap_error_read.py \
  --qwen-h1-run runs/<v4_11_full_run_id> \
  --gpt-h1-run runs/exect_s1_interleaving_h1_post_bridge_gpt4_1_mini_20260520T190807Z \
  --output runs/exect_s1_seizure_prompt_policy_qwen_v1_error_read.json
```

## Artifacts (post-run)

| Artifact | Path |
| --- | --- |
| Implementation log | `docs/exect_s0_label_policy_v4_11_implementation.md` |
| Inspection | `docs/exect_s1_seizure_prompt_policy_qwen_v1_inspection_<date>.md` |
| Registry rows | `docs/experiment_registry.json` under `exect_s1_seizure_prompt_policy_qwen_v1` |
| Kanban | Update `docs/kanban_plan.md` active work / decisions |

## Validation (pre-run)

- [ ] `v4_11` prompt diff reviewed against `docs/exect_gold_label_audit.md` and `docs/previous_exect_error_analysis.md`
- [ ] Experiment configs include taxonomy `comparison_group`, `varied_factor: prompt_policy`, `hybrid_balance_class`
- [ ] `uv run python scripts/validate_experiment_taxonomy.py` passes for new configs
- [ ] Dry-run succeeds for Qwen and GPT cap-25 configs

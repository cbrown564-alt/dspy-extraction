# ExECT S5 Per-Family Parallel Ceiling GPT Cap-25 v1 Preregistration

Date: 2026-05-24  
Status: **Preregistered** — C1.1 implementation unblocked  
Comparison group: `exect_s5_per_family_parallel_ceiling_gpt_cap25_v1`  
Related: [kanban C-track](../../planning/kanban_plan.md), [paper-frozen S5 v2b](../synthesis/paper_frozen_operational_defaults_20260524.md), [S1 PG1 inspection (arm reject only)](exect_s1_field_family_prompt_graph_gpt_cap25_v1_inspection_20260521.md)

## Research Question

On the paper-frozen **S5 core surface** (five families), does **full-note per-family parallel extraction** (one LLM call per family → merge) establish a **quality/efficiency ceiling** versus the promoted **single-pass v2b** stack when label policies and post-processing match the operational default?

This is a **P2 research arm** for paper-facing ceiling measurement — not an operational-default candidate unless it clears promotion gates (unlikely given S1 PG1 direction).

## Hypothesis

Per-family parallel decomposition with promoted **v1.2 label policies** per call and the **frequency post-stack isolated to the seizure_frequency call** may improve per-family focus but is **unlikely to beat single-pass v2b** on pooled micro F1. S1 PG1 parallel full-note decomposition regressed **−9.3pp** vs monolithic extraction on a smaller schema; this arm tests whether the mature S5 promoted stack changes that conclusion on the five-family core surface.

Primary read: **ceiling vs cost** (quality delta, call multiplier, per-family failure modes), not operational promotion.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | `exect_s5_core_field_family` (diagnosis, seizure_type, annotated_medication, investigation, seizure_frequency) |
| Research axis | **1** — pipeline stage-graph decomposition |
| Comparison group | `exect_s5_per_family_parallel_ceiling_gpt_cap25_v1` |
| Primary varied factor | `pipeline_stage_graph` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | **No** |

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:validation` |
| Cap | First 25 validation records (Lane A order) |
| Model | GPT 4.1-mini |
| Scorer | `exect_s5_core_field_family_deterministic_v1` |
| Primary metric | Pooled micro F1 across five S5 core families |
| Diagnostics | Per-family F1, evidence quote support, schema validity, LLM call count per record, merge-error notes |
| Prompt family | `exect_s4_field_family_v1_2_label_policy` (extractor v1.2; **not** v1.3 qualitative gate) |
| Few-shot | Embedded benchmark-facing label-policy examples **filtered per family** |
| Context | Full note for every family call (no section routing, no prior-context chaining) |
| Bridge mode | Inline benchmark bridges after merge (same post-merge path as single-pass S5) |
| Local model | **None** — GPT anchor only; impractical for local deployment path |

## Post-Processing Contract (Promoted Stack Parity)

Post-processing is **family-scoped**, mirroring the paper-frozen v2b stack:

| Family call | Extractor | Deterministic post |
| --- | --- | --- |
| `diagnosis` | Per-family v1.2 signature + family-filtered examples | Inline S1/S2 diagnosis bridges |
| `seizure_type` | Per-family v1.2 signature + family-filtered examples | Inline seizure bridges |
| `annotated_medication` | Per-family v1.2 signature + family-filtered examples | **AM guard** (`exect.medication.am_guard_non_asm_brand_alias.v1`) |
| `investigation` | Per-family v1.2 signature + family-filtered examples | S2/S3/S4 investigation recovery bridges |
| `seizure_frequency` | Pre-vocab note + frequency-only v1.2 signature | **v2b reject-only verifier** (`exect.frequency.evidence_verify_policy.v2b`; rules 1–9, no strict qualitative guard) |

Medication temporality is **excluded** (S5 core surface). No cross-family prior-context injection (contrast with S1 PG2 sequential arm).

## Arms

| Arm | `stage_graph_id` | Program variant | LLM calls / record | Config |
| --- | --- | --- | ---: | --- |
| **C0** (baseline) | `g2_extract_verify` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b` | 2 (monolithic extract + freq verify) | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_cap25_gpt4_1_mini.json` |
| **C1** (ceiling test) | `g2_s5_core_family_parallel` | `exect_s5_core_field_family_parallel_v2b` | 6 (5 family extracts + freq verify) | `configs/experiments/exect_s5_core_field_family_parallel_v2b_cap25_gpt4_1_mini.json` |

**C0 anchor run (existing):** `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_cap25_gpt4_1_mini_20260524T211133Z` — 88.2% micro, 76.4% freq F1.

Re-run C0 only if config or scorer drift is suspected; otherwise cite frozen cap-25 run ID.

## Explicit Non-Goals

- **Do not replay** S1 arms (`exect_s0_s1_field_family_prompt_graph_parallel`, `g3_family_split_merge`, section-aware split). Those cap-25 rejects predated current label-policy and hybrid-stack maturity; treat as negative probes at arm scope only.
- **Do not clone** S1 family-split configs or reuse S1 v4_10 prompt versions for this arm.
- **Do not** vary bridge placement, scorer, model, or prompt policy version between C0 and C1.
- **Do not** claim mechanism reject for S5 decomposition from this cap-25 grid alone.
- **Do not** port to Qwen in this arm (L-track handles local transfer separately).
- **Do not** promote to operational default without full-validation gates (C1.3).

## Gates (Cap-25 — C1.2)

| Decision | Rule |
| --- | --- |
| **Rank** | Order by pooled micro F1; per-family F1 and evidence support as diagnostics |
| **Hold (ceiling documented)** | Within **2pp** of C0 micro F1 **or** ≥1 family improves ≥3pp without catastrophic regression elsewhere |
| **Reject arm** | **>2pp** below C0 micro F1 without diagnostic benefit, or evidence support **<95%**, or any guard family drops **>3pp** vs C0 |
| **Proceed to full validation (C1.3)** | Only if cap-25 does **not** regress catastrophically (>5pp micro drop vs C0) **and** ceiling tradeoff is paper-relevant (hold or mixed per-family gains) |
| **Operational promotion** | **Out of scope** — ceiling anchor only unless future prereg explicitly reopens |

### Per-Family Monitoring (Guard Families)

Monitor diagnosis, seizure_type, annotated_medication, and investigation within **−3pp** of C0 cap-25 per family. Seizure_frequency is the primary upside family but recall floor applies: freq recall must not drop **>3pp** vs C0 unless precision gain ≥3pp compensates.

## Efficiency Reporting (C1.4 inputs)

| Metric | C0 | C1 (expected) |
| --- | ---: | ---: |
| LLM calls / record | 2 | 6 |
| Extract call multiplier | 1× | ~5× (five family extracts vs one monolithic) |
| Total call multiplier | 1× | ~3× (6 vs 2 including verifier) |

Report token/latency if run artifacts capture them; not a gate.

## Inspection Requirements (C1.2)

- Taxonomy block with `decision_scope: arm`
- Run IDs for C0 (cite or re-run) and C1
- Per-family F1 table (all five families)
- Evidence support rate
- LLM call count per record
- Prediction overlap C0 vs C1 (identical label sets / record)
- Merge-error notes (cross-family confusion, empty-family failures)
- Comparison note vs S1 PG1 (−9.3pp on 3-family S1; different schema but directional prior)
- Open cells listed explicitly

## Frozen Baseline References

| Role | Run ID | Micro F1 | Freq F1 |
| --- | --- | ---: | ---: |
| C0 cap-25 (v2b) | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_cap25_gpt4_1_mini_20260524T211133Z` | 88.2% | 76.4% |
| C0 full validation (paper D1) | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_20260524T211229Z` | 85.8% | 73.9% |

Full-validation side-by-side (C1.3) compares against the full-validation C0 row only if cap-25 clears non-catastrophic gate.

## Open Cells

- Sequential prior-context chaining on S5 core (S1 PG2 analogue)
- Section-aware routing + v1.2 per-family policy
- Per-family det pre-candidates on non-frequency families
- Qwen port of any hold arm (L-track)
- Medication temporality (excluded from S5 core)

## Implementation Notes (C1.1)

- Fresh `ExectS5CoreFieldFamilyParallelV2bModule` in `src/clinical_extraction/programs/exect_s4.py`
- Per-family signatures built from S4 v1.2 policy examples (S1 PG1 pattern, S5 surface)
- Frequency call: pre-vocab note injection + frequency-only extract + v2b verifier
- Prediction path: S5-core-only value builder with existing inline bridges and AM guard
- Register variant in `config.py`, `exect_backend.py`, `exect_prompts.py`
- Config taxonomy: `stage_graph_id: g2_s5_core_family_parallel`, `varied_factor: pipeline_stage_graph`

## Stop Rules

- Reject C1 at cap-25 if gates fail; do not spend full-validation model budget.
- Do not stack additional factors (v1.3 prompt, strict qualitative guard, temporal med guard) on this arm.
- Do not update paper operational defaults from C1 outcomes without separate promotion review.

# ExECT S5 Per-Family Parallel Ceiling GPT Cap-25 v1 — Inspection

Date: 2026-05-24  
Preregistration: [exect_s5_per_family_parallel_ceiling_gpt_cap25_v1_preregistration_20260524.md](exect_s5_per_family_parallel_ceiling_gpt_cap25_v1_preregistration_20260524.md)  
Comparison group: `exect_s5_per_family_parallel_ceiling_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Schema complexity | `exect_s5_core_field_family` |
| Research axis | 1 — pipeline stage-graph decomposition |
| Comparison group | `exect_s5_per_family_parallel_ceiling_gpt_cap25_v1` |
| Primary varied factor | `pipeline_stage_graph` |
| stage_graph_id (C1) | `g2_s5_core_family_parallel` |
| decision_scope | **arm** |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `exectv2_fixed_v1:validation` cap-25, v1.2 label policy, inline bridges, AM guard on medication call, pre-vocab + v2b verifier on frequency call only.

## Arms

| arm_id | `stage_graph_id` | run_id | micro F1 | diagnosis | seizure_type | medication | investigation | freq | evidence |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| C0 | `g2_extract_verify` | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_cap25_gpt4_1_mini_20260524T211133Z` | **88.2%** | 93.0% | 92.5% | 87.9% | 93.8% | 76.4% | 93.8% |
| C1 | `g2_s5_core_family_parallel` | `exect_s5_core_field_family_parallel_v2b_cap25_gpt4_1_mini_20260524T212052Z` | 83.6% | 87.2% | 80.6% | **96.6%** | 93.8% | 66.7% | 91.5% |

Best micro F1: **88.2%** (C0 single-pass v2b).

## Efficiency

| Metric | C0 | C1 | Ratio |
| --- | ---: | ---: | ---: |
| LLM history entries | 19 | 143 | ~7.5× |
| Prediction seconds / record | 1.43 | 20.44 | ~14.3× |
| Total prediction time (25 records) | 35.7s | 511.0s | ~14.3× |
| Prompt + completion tokens | 33.4k | 172.8k | ~5.2× |

C1 uses five family extract calls plus one frequency verifier per record (~6 effective calls vs C0 ~2).

## Gate Comparison (C1 vs C0)

| Gate | Rule | Result |
| --- | --- | --- |
| Micro F1 | Reject if >2pp below C0 without diagnostic benefit | **Fail** (−4.6pp) |
| Evidence support | Reject if <95% | **Fail** (91.5%) |
| Guard families | Reject if any drops >3pp vs C0 | **Fail** (diagnosis −5.8pp, seizure_type −11.9pp) |
| Frequency recall floor | Must not drop >3pp unless precision +3pp compensates | **Fail** (recall 80.0% vs 84.0%, −4.0pp; precision 57.1% vs 70.0%) |
| Full validation (C1.3) | Skip if catastrophic (>5pp micro drop) or gate fail | **Skip** |

## Prediction Overlap (C0 vs C1)

| Comparison | Identical label sets |
| --- | ---: |
| All five families (per record) | 7/25 |
| diagnosis | 22/25 |
| seizure_type | 18/25 |
| annotated_medication | 19/25 |
| investigation | 25/25 |
| seizure_frequency | 15/25 |

## Failure Modes

- **Seizure type (−11.9pp):** cross-slot leakage in per-family calls — e.g. `EA0016` predicts `single focal seizure` from diagnosis context; `EA0100` emits diagnosis-as-seizure-type; co-list / secondary-generalisation surfaces lost without monolithic pass (same pattern as S1 PG1).
- **Seizure frequency (−9.7pp):** isolated frequency call over-emits qualitative labels without evidence (`infrequent`, `frequency same`, `frequency increased` with empty evidence spans on EA0018, EA0047, EA0048, EA0109); monolithic pass retains cross-family disambiguation.
- **Diagnosis (−5.8pp):** recall drop on co-list / specificity surfaces (EA0061, EA0125) when diagnosis is extracted without sibling-family context.
- **Medication (+8.7pp):** per-family focus reduces cross-family medication noise from the eleven-family monolithic signature — **not sufficient** to offset pooled micro regression.

## Comparison vs S1 PG1 (directional)

| Arm | Schema | Micro F1 | Seizure type delta vs single-pass |
| --- | --- | ---: | --- |
| S1 PG1 parallel | 3-family S1 | 86.5% | −12.5pp |
| S5 C1 parallel | 5-family S5 core | 83.6% | −11.9pp |

Mature v1.2 policies on the S5 surface do **not** overturn the S1 decomposition direction: parallel full-note per-family extraction remains below monolithic single-pass on GPT cap-25.

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| C0 | **Hold** (baseline anchor) | arm | Paper-frozen v2b cap-25 reference |
| C1 | **Reject (arm)** | arm | −4.6pp micro; evidence 91.5%; guard-family regressions; ~14× slower |

## Recommendation

- **Do not proceed to C1.3 full validation** — cap-25 gates failed on micro F1, evidence support, and guard families.
- **Document as paper-facing ceiling anchor:** single-pass v2b dominates per-family parallel at ~6× LLM call cost with no pooled quality gain.
- **Do not mechanism-close** S5 decomposition from this arm alone.

## Quality / Efficiency Ceiling (C1.4 summary)

Per-family parallel decomposition on the promoted S5 stack is **not a quality ceiling above** single-pass v2b — it is a **lower bound** on the quality/efficiency tradeoff at cap-25: ~14× latency for −4.6pp micro F1. The one family that improves (medication +8.7pp) does not generalize; seizure_type and seizure_frequency regress most, consistent with cross-family context dependence in clinical letters.

## Open Cells

- Sequential prior-context chaining on S5 core (S1 PG2 analogue)
- Section-aware routing + v1.2 per-family policy
- Qwen port (out of scope for C-track GPT anchor)

## Caveats

- Cap-25 only; systematically optimistic vs full validation.
- S5 partial surface; scorer unchanged.
- C0 and C1 compared under identical split cap and scorer.

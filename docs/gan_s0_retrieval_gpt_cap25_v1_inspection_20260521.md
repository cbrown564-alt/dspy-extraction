# Gan S0 Evidence-First Retrieval GPT Cap-25 v1 — Inspection

Date: 2026-05-21  
Preregistration: `docs/gan_s0_retrieval_gpt_cap25_v1_preregistration_20260521.md`  
Comparison group: `gan_s0_retrieval_gpt_cap25_v1`

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Comparison group | `gan_s0_retrieval_gpt_cap25_v1` |
| Research axis | Context selection / evidence retrieval |
| Primary varied factor | `context_selection_policy` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| decision_scope | `arm` |
| Mechanism closure allowed? | No |

Fixed controls: GPT 4.1-mini, `gan_2026_fixed_v1:validation` cap-25 (Lane A order), scorer `gan_frequency_deterministic_v1`, single-pass adjudication (no verify-repair), required model-quote evidence.

## Arms

| arm_id | context_selection_policy | run_id | monthly | purist | pragmatic | schema | evidence | valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R1 | `full_note` | `gan_s0_retrieval_r1_full_note_cap25_gpt4_1_mini_20260521T014536Z` | 44.0% | 64.0% | 72.0% | 100% | 100% | 25 |
| R2 | `full_note_plus_deterministic_temporal_candidates` | `gan_s0_retrieval_r2_full_note_plus_candidates_cap25_gpt4_1_mini_20260521T014540Z` | **52.0%** | 60.0% | 76.0% | 100% | 100% | 25 |
| R3 | `deterministic_temporal_candidates_only` | `gan_s0_retrieval_r3_candidates_only_cap25_gpt4_1_mini_20260521T014545Z` | 28.0% | 28.0% | 28.0% | 100% | 100% | 25 |

Rank order (monthly): **R2 (52%)** > R1 (44%) > R3 (28%).

## Reproduction gate (R2)

R2 **reproduces** Phase 2 A3 / Phase 3 E1 at **52.0%** monthly on the same 25 records (`…T012204Z`, `…T013003Z`). Clean context-selection group confirms prior stage-graph/executor directional evidence was not a split artifact.

## Prediction overlap

| Pair | Identical `raw_value` / 25 | Notes |
| --- | ---: | --- |
| R1 vs R2 | 15/25 | Retrieval + candidates change 10 labels (+8pp monthly) |
| R1 vs R3 | 2/25 | Candidates-only reshapes almost entire slice |
| R2 vs R3 | 2/25 | Full-note visibility required for R2 gains |

Sample R2-only wins vs R1: `gan_1794`, `gan_4113`, `gan_16825`, `gan_9566`, `gan_16772`.

## Retrieval diagnostics (cap-25 mismatches)

Proxy counts from `monthly_frequency_mismatches` (not full failure-taxonomy pass):

| arm_id | missed → `no seizure frequency reference` | unknown ↔ no-ref swap | unsupported-positive proxy |
| --- | ---: | ---: | ---: |
| R1 | 0 | 0 | 0 |
| R2 | 0 | 0 | 0 |
| R3 | **18** | 3 | 0 |

R3 collapses to `no seizure frequency reference` on most errors — consistent with insufficient context when full-note body is hidden. Evidence support stays 100% on valid rows (quotes remain note substrings).

## Gates (prereg)

| arm_id | monthly vs best (52%) | schema ≥ 95% | outcome | decision_scope |
| --- | --- | --- | --- | --- |
| R2 | best | pass | **hold** — operational context default for adjudication skeleton | arm |
| R1 | −8pp | pass | **reject arm** — full-note without retrieval undermatches R2 | arm |
| R3 | −24pp | pass | **reject arm** — candidates-only insufficient on cap-25 | arm |

No full-validation spend from this group (per prereg).

## Outcomes

| arm_id | outcome | decision_scope | Notes |
| --- | --- | --- | --- |
| R2 | hold | arm | Best monthly; reproduces E1/A3; supports keeping det-candidate injection with full note |
| R1 | reject | arm | Matches prior full-note direct cap-25 band (44%) |
| R3 | reject | arm | CLEAR-style window-only context regresses sharply; high no-reference miss rate |

## Mechanism review

Not applicable — cap-25 search only; no mechanism promote/reject claims.

Directional read (arm-level): **full note plus deterministic temporal candidates** beats full-note-only and candidates-only on this slice. Does **not** close whether embedding/entity retrieval or alternate windowing would beat R2.

## Recommendations

1. **Freeze operational context** for Gan single-pass adjudication at R2 (`full_note_plus_deterministic_temporal_candidates`) pending Axis 2/3 work.
2. **Do not promote** candidates-only retrieval for Gan S0 without a new prereg and improved windowing primitive.
3. **Next pull:** ExECT S1 stage-graph grid (`exect_s1_pipeline_stage_graph_gpt_cap25_v1`) or Gan validation-ladder companion prereg.

## Open cells (explicit)

- Embedding / entity-index retrieval (CLEAR full analogue).
- LLM-generated evidence windows.
- Verify-repair layered on R2 skeleton.
- Qwen confirmation of R2.
- Full validation / 50-record slice on R2 vs R1 only if broader confirmation needed.

## Implementation notes

- R3 uses `_prompt_note_text_for_context_policy` in `gan_frequency_s0.py` — prompt-visible note is deduped candidate evidence spans; empty lists use preregistered stub.
- Run artifacts record `context_policy`, `prompt_note_text_is_full_note`, and char-count metadata per prediction.

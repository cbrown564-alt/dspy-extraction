# Gan S0 Evidence-First Retrieval GPT Cap-25 v1 Preregistration

Date: 2026-05-21  
Status: **Planned** — configs and optional R3 program support pending  
Comparison group: `gan_s0_retrieval_gpt_cap25_v1`  
Related: `docs/multi_stage_llm_clinical_extraction_literature_review_20260521.md`, `docs/hybrid_pipeline_research_pivot_20260521.md`, `docs/hybrid_pipeline_mechanism_status_20260521.md`, `docs/kanban_plan.md`, `docs/gan_2026_label_audit.md`

## Literature motivation

Lopez et al. (CLEAR, npj Digital Medicine 2025) show that **clinical entity augmented retrieval** before extraction can outperform full-note prompting and embedding RAG on clinical IE tasks while reducing tokens and latency. Reference: https://www.nature.com/articles/s41746-024-01377-1

Project synthesis: `docs/multi_stage_llm_clinical_extraction_literature_review_20260521.md` § Clinical entity augmented retrieval; Literature Card 1.

For Gan S0 seizure frequency, full-note prompting may invite confusion between historical and current frequency statements. Deterministic temporal candidates (`gan.frequency.temporal_candidates.v1`) are the local analogue of evidence-window retrieval — but prior stage-graph comparisons (A1 vs A3) **confounded** `pipeline_stage_graph` with context assembly. This group isolates **context selection** under a fixed single-pass adjudication skeleton.

## Research question

On Gan S0 with **GPT 4.1-mini**, does **evidence-first context selection** (full note vs full note plus retrieved candidate windows vs candidate windows only) change monthly-frequency accuracy, unsupported-positive rate, and `unknown` / `no seizure frequency reference` confusion when downstream adjudication, evidence policy, split, model, and scorer are fixed?

## Hypothesis

Injecting deterministic temporal-candidate evidence windows before LLM adjudication reduces historical/current confusion and unsupported frequency labels compared with full-note-only context. A candidate-window-only arm tests whether retrieval alone (without full-note visibility) can match or exceed full-note performance on this slice.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Clinical task family | frequency |
| Research axis | Context selection / evidence retrieval (literature-informed; pre-stage `section_context_selection`) |
| Comparison group | `gan_s0_retrieval_gpt_cap25_v1` |
| Primary varied factor | `context_selection_policy` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| `decision_scope` target | `arm` |
| Mechanism closure allowed? | No |

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `gan_2026` |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records, same order as Lane A / Phase 2–4 cap-25 groups |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Scorer | `gan_frequency_deterministic_v1` (unchanged — see `docs/gan_2026_label_audit.md`) |
| Verification | `none` — single-pass adjudication only (no verify-repair confound) |
| Evidence strategy | `model_quote` (required contiguous quote; evidence support is diagnostic) |
| Few-shot | `none` |
| Structured output | `provider_json_schema_with_pydantic_validation` |
| `repair_policy` | `artifact_bridge_surface_normalization_only` |
| Downstream program skeleton | Single LLM adjudication after optional pre retrieval |
| Primitive (retrieval arms) | `gan.frequency.temporal_candidates.v1` at `pre` (soft hint) |

## Varied factor

`context_selection_policy`

## Arms

| Arm | `context_selection_policy` | `context_policy` (config) | `program_variant` | `prompt_version` | Config (planned) | Priority |
| --- | --- | --- | --- | --- | --- | --- |
| **R1** | `full_note` | `full_note` | `gan_frequency_s0_direct_single_pass` | `gan_frequency_s0_direct_guardrails_v2_2` | `gan_s0_retrieval_r1_full_note_cap25_gpt4_1_mini.json` | Required |
| **R2** | `full_note_plus_deterministic_temporal_candidates` | `full_note_plus_deterministic_temporal_candidates` | `gan_frequency_s0_temporal_candidates_single_pass` | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` | `gan_s0_retrieval_r2_full_note_plus_candidates_cap25_gpt4_1_mini.json` | Required |
| **R3** | `deterministic_temporal_candidates_only` | `deterministic_temporal_candidates_only` | `gan_frequency_s0_temporal_candidates_single_pass` *(context mode)* | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` | `gan_s0_retrieval_r3_candidates_only_cap25_gpt4_1_mini.json` | Required if feasible |

### Arm semantics

| Arm | What the LLM sees | Retrieval stage | LLM calls / record |
| --- | --- | --- | ---: |
| R1 | Entire note text | none | 1 |
| R2 | Entire note + formatted deterministic temporal candidates | `gan.frequency.temporal_candidates.v1` | 1 |
| R3 | Formatted deterministic temporal candidates only (no full-note body in prompt) | `gan.frequency.temporal_candidates.v1` | 1 |

R3 retains the full note internally for quote validation and artifact-bridge substring checks; only the **prompt-visible context** changes. If empty candidate lists occur, R3 must fall back to a preregistered abstention or minimal note stub — document behavior in the inspection; do not silently switch to full-note mid-run.

### Prompt pairing (documented confound)

R1 uses the direct guardrails prompt family; R2/R3 use the temporal v1.1 adjudication prompt family. This mirrors the clean Lane A pattern (matched architecture per arm, explicit prompt pairing in inspection). **Do not** treat Phase 2 A1 vs A3 as paper-safe single-factor evidence for retrieval — those arms varied `pipeline_stage_graph` and are motivational priors only.

### Implementation prerequisites

1. **R1 / R2:** existing program variants and configs; no scorer or bridge changes.
2. **R3:** add a `context_selection_policy` / `context_policy` branch in `gan_frequency_s0.py` (or equivalent config hook) so `temporal_candidates_single_pass` can assemble candidate-only prompt input while preserving quote substring checks against the full note.
3. **Taxonomy:** `context_selection_policy` is added to `docs/experiment_taxonomy_schema.md` `varied_factor` allowed values before config validation.
4. Confirm empty-candidate and multi-candidate edge cases against `docs/gan_2026_label_audit.md` (`unknown` vs `no seizure frequency reference`).

If R3 cannot be implemented without changing scorer semantics or quote validation, **run R1/R2 only** and document R3 as deferred in the inspection (do not substitute a different arm without amending this prereg).

## Historical priors (motivation only — not clean single-factor evidence)

| Reference | Context | Monthly (cap-25) | Notes |
| --- | --- | ---: | --- |
| Phase 2 A1 `g1_direct` | full note, direct single-pass | 44.0% | `gan_s0_stage_graph_g1_direct_cap25_gpt4_1_mini_20260521T012156Z` — confounded by `pipeline_stage_graph` |
| Phase 2 A3 `g2_candidates_adjudicate` | full note + det candidates | 52.0% | `…T012204Z` — confounded by `pipeline_stage_graph` |
| Phase 3 E1 det candidates | same as A3 under executor grid | 52.0% | `gan_s0_stage_executor_e1_det_candidates_cap25_gpt4_1_mini_20260521T013003Z` — reproduction anchor for **R2** |
| Lane A verification direct | full note | 44.0% | `…T233555Z` |
| Lane A verification temporal + VR | full note + candidates + VR | 44.0% | `…T233701Z` — identical labels to direct on this slice |

**R2 reproduction gate:** R2 should match E1/A3 at **52.0%** monthly on the same 25 records before interpreting R1/R3 deltas.

## Primary metrics

- **Monthly-frequency accuracy** (benchmark-facing headline)
- **Purist category accuracy**
- **Pragmatic category accuracy**

## Diagnostic metrics (retrieval-specific)

Compute from cap-25 predictions using `clinical_extraction.evaluation.gan_failure_taxonomy.classify_gan_frequency_failure`:

| Diagnostic | Definition / failure classes |
| --- | --- |
| **Evidence support rate** | Scorer diagnostic — required model quotes supported in note |
| **Unsupported-positive rate** | Share of scored records with `false_positive_rate` (gold ≠ `no seizure frequency reference`, predicted = `no seizure frequency reference` inverted — use `false_positive_rate` class: predicted frequency when gold is no-reference) |
| **`unknown` / no-reference confusion** | Count of `unknown_vs_no_reference`, `unknown_cluster_vs_no_reference`, `missed_frequency_reference` |
| **Historical vs current proxy errors** | `seizure_free_to_no_reference_benchmark_severe`, `unknown_vs_seizure_free`, `frequent_undercalled`, `frequent_overcalled` |
| **Schema-valid prediction rate** | Valid predictions / 25 |
| **Token / latency diagnostics** | Optional — log if run metadata exposes prompt length or timing |

Per `docs/gan_2026_label_audit.md`: treat `unknown` and `no seizure frequency reference` as distinct gold semantics; do not collapse in error analysis.

## Explicit non-goals

- Do not vary verify-repair, stage graph, candidate source (deterministic only on R2/R3), or evidence policy.
- Do not test LLM-generated retrieval, embedding RAG, or hybrid candidate merge (deferred to `gan_s0_stage_executor_gpt_cap25_v1` follow-ups).
- Do not test candidate presentation variants (table/JSON/bullets).
- Do not claim mechanism reject for full-note vs retrieval from cap-25 alone.
- Do not compare to published Gan Real-set benchmarks; fixed synthetic validation only.

## Gates

| Decision | Rule |
| --- | --- |
| **Rank arms** | Order by monthly frequency; use diagnostics above for retrieval mechanism read |
| **Hold** | Within 3pp of best monthly **or** ≥2pp reduction in benchmark-severe unknown/no-reference confusion without monthly regression >2pp |
| **Reject arm** | >3pp below best monthly without diagnostic benefit, or schema-valid rate < 95% |
| **Promote context policy** | Cap-25 winner clears hold gate **and** R2 reproduces E1/A3 band; full validation deferred unless winner beats R1 by ≥5pp with stable diagnostics |
| **Mechanism review** | Only if R1/R2/R3 agree directionally across ≥2 context implementations (e.g. R3 plus an alternate windowing primitive) |
| **Full validation** | Not by default; spend only if R2 or R3 beats R1 by ≥5pp monthly with no evidence-support regression |

## Run order

1. Implement R3 context-only assembly (if not already present).
2. Emit three cap-25 configs with taxonomy `varied_factor: context_selection_policy`.
3. Dry-run configs (`experiment-run-lifecycle`).
4. Cap-25 all required arms on matched records.
5. Error-read: failure taxonomy counts per arm; overlap table R1 vs R2 vs R3 on `raw_value`.
6. Inspection `docs/gan_s0_retrieval_gpt_cap25_v1_inspection_<date>.md`.
7. Registry rows under `gan_s0_retrieval_gpt_cap25_v1`.

## Inspection requirements

- Run IDs for all executed arms.
- Taxonomy block with `decision_scope: arm`.
- Metrics table vs R2 reproduction anchor (E1/A3 52.0%).
- Prediction overlap R1 vs R2 vs R3.
- Failure-taxonomy table: unsupported-positive rate and unknown/no-reference confusion by arm.
- Prompt pairing and R3 empty-candidate behavior documented.
- Open cells: embedding RAG, LLM retrieval, verify-repair layered on winning context, Qwen port, full validation.

## Open cells

- LLM or hybrid candidate retrieval (executor grid tested source, not windowing policy).
- Embedding / entity-index retrieval beyond deterministic temporal spans.
- Validation ladder (schema → plausibility → evidence → repair → judge) — companion prereg `gan_s0_validation_ladder_gpt_cap25_v1` (not started).
- Qwen confirmation of cap-25 winner.
- Full validation / 50-record slice confirmation.

## Companion work (out of scope for this prereg)

**Gan S0 validation ladder:** layered ablation for schema validation, deterministic plausibility checks, evidence grounding, selective repair, and optional judge review. Depends on retrieval winner or current temporal-candidates default. Draft as separate prereg after this group's inspection.

## Artifacts checklist

- [ ] `context_selection_policy` in `docs/experiment_taxonomy_schema.md`
- [ ] R3 context-only program support (if required)
- [ ] Three cap-25 configs (`gan_s0_retrieval_r*_cap25_gpt4_1_mini.json`)
- [ ] Cap-25 runs
- [ ] Inspection doc
- [ ] Registry rows

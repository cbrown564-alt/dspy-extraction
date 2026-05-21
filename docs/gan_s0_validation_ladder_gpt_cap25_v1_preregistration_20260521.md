# Gan S0 Validation Ladder — GPT Cap-25 v1 Pre-Registration

Date: 2026-05-21  
Status: **Design complete — implementation pending**  
Comparison group: `gan_s0_validation_ladder_gpt_cap25_v1`  
Related: `docs/multi_stage_llm_clinical_extraction_literature_review_20260521.md` (Literature Card 2), `docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md`, `docs/gan_s0_lane_a_gpt_cap25_inspection_20260521.md`, `docs/gan_2026_label_audit.md`, `docs/hybrid_pipeline_mechanism_status_20260521.md`  
Kanban: `docs/kanban_plan.md` (Literature-informed follow-ups)

## Research question

On the Phase 2–3 winning skeleton (`g2_candidates_adjudicate` + deterministic temporal candidates + LLM adjudicate), which **validation layer** — schema/surface normalization, deterministic plausibility, deterministic evidence grounding, selective LLM verify-repair, bundled post-VR guards, or optional judge escalation — improves monthly-frequency accuracy and reduces unsupported positives **without** changing scorer semantics?

This group **decomposes validation** that is currently bundled in `gan_frequency_s0_temporal_candidates_adjudicate_verify_repair` and the operational `g3_candidates_extract_repair` path. It does **not** re-test stage-graph or candidate-source axes (closed for search at cap-25; see Phase 2–3 inspections).

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Research axis | **Post-extract validation stack** (orthogonal to Axes 1–3) |
| Comparison group | `gan_s0_validation_ladder_gpt_cap25_v1` |
| Primary varied factor | `validation_ladder_rung` |
| Anchor `stage_graph_id` | `g2_candidates_adjudicate` |
| Anchor `stage_executor` | `det_candidates_llm_adjudicate` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No |

## Hypothesis

Following the literature hierarchy (schema → deterministic plausibility → evidence grounding → selective repair → judge):

1. Deterministic plausibility and evidence checks remove unsupported or non-canonical labels **before** LLM repair spends a second call.
2. LLM verify-repair helps only when initial adjudication is `unknown`/abstain-heavy or candidate-gated repair is needed; confirm-first deterministic guards prevent over-repair on confident adjudications (E4 showed VR **neutral** vs adjudicate-only on cap-25 when guards are on).
3. Evidence span-check abstention trades monthly accuracy for stricter grounding (Lane A **reject** on bundled temporal+VR; ladder isolates the layer on the winning skeleton).
4. Judge review belongs only on uncertain/conflicting cases (deferred rung; not bundled into scorer).

## Fixed controls (all rungs)

| Control | Value |
| --- | --- |
| Dataset | `gan_2026` |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records (same order as Lane A / Phase 2–3) |
| Model | GPT 4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`) |
| Scorer | `gan_frequency_deterministic_v1` (**unchanged**) |
| Candidate source | Deterministic `temporal_candidates.py` only |
| Adjudication prompt | `gan_frequency_s0_temporal_candidates_single_pass_v1_1` |
| Few-shot | `none` |
| Structured output | `provider_json_schema_with_pydantic_validation` |
| `repair_policy` | `artifact_bridge_surface_normalization_only` (label surface repairs in bridge — not varied) |
| Evidence in signature | Required model quote (unless rung explicitly tests optional/span-check) |

## Varied factor

`validation_ladder_rung` — exactly **one** validation layer added per rung relative to the prior rung. No stacked prompt-policy or candidate-source changes.

## Validation layer map (code ↔ rung)

| Layer | Implementation (current) | Prediction-affecting? |
| --- | --- | --- |
| Schema validity | Provider JSON schema + Pydantic `ExtractedValue` | Yes (invalid → excluded from denominator) |
| Surface plausibility | `_normalize_predicted_label`, forbidden-hour/cluster repairs in `_predict_record` | Yes (via normalization) |
| Deterministic evidence | `_guard_evidence_text` in bridge | Usually diagnostic flags; can affect quality_flags |
| Det plausibility (pre-emit) | `_apply_temporal_verifier_guards` **without** upstream LLM verifier | Yes — **needs new program path** |
| LLM verify-repair | `GanFrequencyS0TemporalVerifierModule` | Yes |
| Det VR guards | `_apply_temporal_verifier_guards` after LLM verifier | Yes |
| Evidence span-check | `_apply_evidence_span_check_guard` | Yes (abstain unsupported) |
| Judge escalation | *(none)* | Deferred |

## Arms (rungs)

| Rung | `validation_ladder_rung` | What is added vs previous | LLM calls | Program variant (planned) | Exists? |
| ---: | --- | --- | ---: | --- | --- |
| V0 | `adjudicate_only` | Baseline: det candidates + single-pass adjudicate | 1 | `gan_frequency_s0_temporal_candidates_single_pass` | **Yes** (E1 `…T013003Z`, 52% monthly) |
| V1 | `schema_surface` | Document-only: schema + bridge surface normalization (same executable as V0) | 1 | same | **Yes** (implicit; rung for ladder bookkeeping) |
| V2 | `det_plausibility` | Deterministic confirm-first + candidate-gated + short seizure-free guards on adjudicate output **without** LLM verifier | 1 | `gan_frequency_s0_temporal_candidates_adjudicate_det_guards` | **No** |
| V3 | `det_evidence_grounding` | V2 + abstain when quote not contiguous in note (prediction-affecting span check pre-VR) | 1 | `…_adjudicate_det_evidence` | **No** |
| V4 | `llm_confirm_only` | V3 + LLM verifier restricted to `confirm` (no repair/abstain in policy) | 2 | `…_adjudicate_confirm_only` | **No** |
| V5 | `llm_verify_repair` | V3 + full LLM confirm/repair/abstain verifier **without** post-VR det guards | 2 | `…_adjudicate_verify_repair_no_guards` | **No** |
| V6 | `llm_verify_repair_det_guards` | V5 + `_apply_temporal_verifier_guards` after verifier | 2 | `gan_frequency_s0_temporal_candidates_adjudicate_verify_repair` | **Yes** (E4 `…T013234Z`, 52% monthly, 25/25 label match vs E1) |
| V7 | `llm_vr_det_guards_span_check` | V6 + `_apply_evidence_span_check_guard` | 2 | span-check prompt variant on adjudicate+VR path | **Partial** (Lane A evidence arm; 18 valid on cap-25) |
| V8 | `judge_escalation` | V6/V7 + second LLM judge on conflict/abstain only | 2–3 | TBD | **Deferred** |

### Diagnostic reference (not ladder arms)

| Label | Purpose | Run / note |
| --- | --- | --- |
| Operational default | `g3_candidates_extract_repair` + temporal VR v1.1 | Full validation `…130933Z` (65.1% monthly, N=299) — **different stage graph**; compare only as external anchor |
| Lane A verification null | direct / VR / temporal VR on mixed graphs | 44% monthly cap-25 — not comparable skeleton |
| Lane A evidence span-check | bundled on `g3` temporal+VR | **Reject** — 7/25 abstentions |

## Incremental hypotheses per transition

| Transition | Proceed if | Reject arm if |
| --- | --- | --- |
| V0 → V2 | Always run V2 after V0 scaffold | Monthly −3pp vs V0 with no unsupported-positive reduction |
| V2 → V3 | V2 does not regress monthly > 2pp | Evidence abstention > 10% of cap-25 without monthly gain |
| V3 → V4 | Always run (isolates LLM read vs repair) | Monthly −3pp vs V3 with confirm-only |
| V4 → V5 | V4 completed | V5 monthly −3pp vs V4 **and** repair rate > 30% with no Purist/pragmatic gain |
| V5 → V6 | Always run | V6 monthly −3pp vs V5 (guards hurt) |
| V6 → V7 | Optional — Lane A prior | V7 valid count < 23 or monthly −5pp vs V6 |
| V8 | Separate prereg after V0–V6 | — |

## Primary metrics

| Metric | Role |
| --- | --- |
| **Monthly-frequency accuracy** | Benchmark-facing primary |
| **Unsupported-positive rate** | Labels with `evidence.unsupported_quote` or missing in-note span |
| **Purist / Pragmatic category accuracy** | Coarse error mode |
| **Schema-valid prediction rate** | Contract health |
| **Evidence quote support rate** | Diagnostic (required unless rung varies evidence) |

## Validation-process metrics (required in inspection)

Log per rung from prediction metadata (`verifier_decision`, `verifier_reason`, `quality_flags`, `initial_label` vs final):

| Metric | Definition |
| --- | --- |
| `repair_rate` | Share of records where final label ≠ initial adjudication label |
| `abstention_rate` | Share with `abstained` quality flag or null `raw_value` |
| `verifier_confirm_rate` | `verifier_decision == confirm` |
| `verifier_repair_rate` | `verifier_decision == repair` |
| `verifier_abstain_rate` | `verifier_decision == abstain` |
| `det_guard_override_rate` | `verifier_reason` contains `Confirm-first guard` or `Candidate-gated` |
| `unsupported_positive_rate` | Predictions scored monthly-positive but failing in-note evidence check |
| `unknown_no_reference_confusion` | Cross-tab `unknown` vs `no seizure frequency reference` errors |
| `latency_seconds_per_record` | Wall-clock / record from run metadata |
| `llm_calls_per_record` | 1, 2, or 3 per prereg table |

## Cap-25 gate

| Outcome | Rule |
| --- | --- |
| **Hold rung** | Monthly within −1pp of V0 (52% band) **and** unsupported-positive ↓ ≥ 3pp **or** Purist/pragmatic ↑ ≥ 3pp |
| **Reject rung** | Monthly −3pp vs V0 without diagnostic gain **or** schema < 95% **or** valid count < 23 |
| **Proceed to full** | Only if a rung **beats V0 monthly by ≥ 3pp** on cap-25 **and** passes schema/evidence gates — max one arm per ladder wave |

No full-validation spend on null transitions (V4 confirm-only ≈ V3, V6 ≈ V0 per E4).

## Relationship to completed work

| Prior study | Implication for ladder |
| --- | --- |
| Phase 2 A3 vs A5 | VR on **extract** path erased +8pp monthly vs candidates→adjudicate — ladder uses **adjudicate-first** skeleton only |
| Phase 3 E1 vs E4 | VR **after adjudicate** neutral on labels (25/25 match) — V5 vs V6 tests whether **det guards** change outcomes when VR is enabled |
| Lane A verification | Null at 44% on different graphs — do not conflate with ladder |
| Lane A evidence span-check | Abstention confound on g3 path — V7 retests on g2 anchor only |
| Operational full VR | 65.1% monthly on N=299 — ladder cap-25 may not reproduce; full confirm only for cap-25 winner |

## Implementation prerequisites

Ordered before model-backed runs:

1. [ ] Add `validation_ladder_rung` to taxonomy allowlist (`taxonomy.py`, `registry_validation.py`, `docs/experiment_taxonomy_schema.md`).
2. [ ] **V2** — `GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule`: apply `_apply_temporal_verifier_guards` to adjudicate output with synthetic `decision=confirm` from adjudicate (no LLM verifier call).
3. [ ] **V3** — extend V2 with prediction-affecting `_evidence_policy_feedback` abstain before emit.
4. [ ] **V4** — `GanFrequencyS0TemporalVerifierModule` + confirm-only prompt variant (`decision` constrained to confirm; reject repair/abstain in signature).
5. [ ] **V5** — adjudicate → temporal verifier **without** `_apply_temporal_verifier_guards` (isolates raw LLM VR).
6. [ ] **V6** — wire existing `gan_frequency_s0_temporal_candidates_adjudicate_verify_repair` (E4 reproduction).
7. [ ] **V7** — span-check prompt version on V6 path (reuse `GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION` pattern).
8. [ ] Cap-25 configs `configs/experiments/gan_s0_validation_ladder_v{0,2,3,4,5,6,7}_cap25_gpt4_1_mini.json` with taxonomy block.
9. [ ] Extend run artifact summary or inspection script to aggregate validation-process metrics above.
10. [ ] **V8 judge** — separate prereg `gan_s0_validation_ladder_judge_gpt_cap25_v1` after V0–V6 inspection.

## Run order

1. Dry-run all implemented configs.
2. **V0** (reproduce E1) → **V2** → **V3** (deterministic-only rungs).
3. **V4** → **V5** → **V6** (LLM validation rungs).
4. **V7** optional if V6 holds.
5. Inspection `docs/gan_s0_validation_ladder_gpt_cap25_v1_inspection_<date>.md`.
6. Registry rows; regenerate matrix/atlas.

Skip V1 as a separate run (same executable as V0; documented as schema+surface floor).

## Commands (after implementation)

```powershell
# Reproduction control
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_validation_ladder_v0_cap25_gpt4_1_mini.json --env-file .env --dry-run

# Deterministic validation rungs
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_validation_ladder_v2_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_validation_ladder_v3_cap25_gpt4_1_mini.json --env-file .env

# LLM validation rungs
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_validation_ladder_v4_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_validation_ladder_v5_cap25_gpt4_1_mini.json --env-file .env
uv run python scripts/run_experiment.py --experiment configs/experiments/gan_s0_validation_ladder_v6_cap25_gpt4_1_mini.json --env-file .env
```

## Open cells (explicit)

- LLM judge (V8) and uncertainty routing policy.
- Whether det plausibility (V2) duplicates bridge normalization gains on cap-25.
- Interaction with evidence-first retrieval ablation (Literature Card 1) — run retrieval grid **before** or **in parallel** with validation ladder only if scorer and cap record order stay matched.
- Qwen port of winning rung only after GPT cap-25 inspection.

## Artifacts checklist

- [x] Ladder design + preregistration (this doc)
- [ ] Program variants V2–V5, V7
- [ ] Cap-25 configs (7–8 arms)
- [ ] Validation-process metric aggregation in inspection script
- [ ] Model-backed runs
- [ ] Inspection doc with `decision_scope: arm`
- [ ] Registry rows under `gan_s0_validation_ladder_gpt_cap25_v1`

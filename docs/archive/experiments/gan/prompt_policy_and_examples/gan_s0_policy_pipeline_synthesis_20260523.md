# Gan S0 Policy And Hybrid Pipeline Synthesis

Date: 2026-05-23  
Status: Decision note for next Gan S0 pull  
Dataset: Gan 2026 synthetic validation, enriched 25-record validation slice unless stated  
Primary gold: `check__Seizure Frequency Number.seizure_frequency_number[0]`  
Scorer: `gan_frequency_deterministic_v1`  

## Research Question

Which next Gan S0 work is justified after the GPT-first policy and pipeline runway: more prompt/example/verifier model calls, Qwen transfer, or deterministic candidate-builder engineering?

## Taxonomy

Dataset: Gan 2026  
Schema complexity: Gan S0 seizure-frequency label  
Comparison group: multiple GPT-first Axis 3 cells over the same enriched 25-record validation slice  
Research axis: 3  
stage_graph_id: `g2_candidates_adjudicate` unless noted  
varied_factor: `prompt_policy`, `example_strategy`, `implementation_variant`, `verification_strategy`  
decision_scope: operational / arm synthesis; no mechanism closure  

## Source Artifacts

- Audit and policy: `docs/datasets/gan/gan_2026_label_audit.md`, `docs/policies/deterministic_scorer_semantics.md`
- Primitive catalog: `docs/taxonomy/taxonomy_primitive_catalog.md`
- Learning log: `docs/experiments/gan/gan_s0_policy_pipeline_learning_log.md`
- Mechanism status: `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- Slice fixture: `data/fixtures/gan_s0_qwen35b_20260522_pragmatic_error_slice.json`
- Candidate implementation: `src/clinical_extraction/gan/temporal_candidates.py`
- Candidate tests: `tests/test_gan_temporal_candidates.py`

## Arm Outcomes

| Arm | Run | Monthly | Pragmatic | Schema / evidence | Decision |
| --- | --- | ---: | ---: | --- | --- |
| v1.1 baseline | `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_1_slice_20260522T215239Z` | 24.0% | 56.0% | 100% / 100% | superseded by v1.4 for this slice |
| v1.4 full policy | `gan_s0_gpt4_1_mini_error_taxonomy_policy_v1_4_slice_20260522T215246Z` | 36.0% | 56.0% | 100% / 100% | current no-example control |
| Compact hierarchy | `gan_s0_gpt4_1_mini_policy_density_compact_hierarchy_slice_20260522T221745Z` | 28.0% | 48.0% | 100% / 100% | reject as tested |
| G5 event table | `gan_s0_gpt4_1_mini_event_table_candidate_slice_20260522T222602Z` | 8.3% | 37.5% | 96% / 100% | reject as tested |
| G6 answer selector | `gan_s0_gpt4_1_mini_multiple_answer_det_selector_slice_20260522T223556Z` | 0.0% | 0.0% | 100% / 100% on 4 supported-evidence predictions | reject as tested |
| G7 constrained verifier | `gan_s0_gpt4_1_mini_constrained_verifier_slice_20260522T225947Z` | 36.0% | 56.0% | 100% / 100% | reject for promotion; ties v1.4 with second LLM pass |
| G9 targeted examples min7 | `gan_s0_gpt4_1_mini_targeted_examples_min7_slice_20260523T072443Z` | 36.0% | 56.0% | 100% / 100% | reject for promotion; mixed rescues/regressions |
| G6b seeded options | `gan_s0_gpt4_1_mini_seeded_answer_options_slice_20260523T074823Z` | 16.0% | 20.0% | 100% / 100% on 8 supported-evidence predictions | reject as tested |

## Error Analysis

Current deterministic candidate builders contain the exact gold label for only 5/25 enriched-slice records. Coverage by original Qwen failure mode:

| Failure mode | Gold label in deterministic candidates |
| --- | ---: |
| counted-window/no-further-events over unknown | 2/2 |
| infrequent quantified over unknown | 3/15 |
| frequent quantified over unknown | 0/3 |
| seizure-free over unknown | 0/2 |
| vague multiple over unknown | 0/2 |
| cluster frequency over unknown | 0/1 |

For the strongest control, v1.4, the 16 monthly misses were mostly not exact-candidate-selection failures; they were candidate absence plus raw-note inference failures. Examples include:

- `gan_13058`: gold `2 per 7 month`, v1.4 predicted `1 per 3 week`, no gold candidate.
- `gan_14792`, `gan_14821`, `gan_14965`, `gan_14973`, `gan_16750`: quantified gold labels predicted `unknown`, no gold candidate.
- `gan_15442`: cluster gold `1 cluster per 4 day, 2 per cluster`, predicted `unknown`, no gold candidate.
- `gan_16529`: gold `1 per 5 day`, predicted cluster syntax, no gold candidate.

G7 shows that a constrained verifier is safe but currently low-value: final labels matched v1.4 on 24/25 records and the second pass mostly confirmed the initial decision. This is expected when the verifier is forbidden to free-form repair and the candidate set is empty or incomplete.

G9 shows targeted examples can move individual records but are not stable as a mixed pack: `gan_16750` became an exact rescue, and `gan_15442`/`gan_16645` improved categorically, but `gan_14881`, `gan_15193`, and `gan_16529` regressed to `unknown`.

G6b is useful mainly as a negative implementation critique. Seeding prevented total collapse when deterministic candidates existed, but the LLM option layer introduced false `no seizure frequency reference` and zero-rate choices on quantified gold records, preserved 66 rejected LLM options, and still left 14/25 with no selected option.

## Hypothesis Evaluation

**H1: v1.4 policy text is a useful no-example control.** Supported at arm level. It improved monthly accuracy over v1.1 on the enriched slice without losing pragmatic accuracy.

**H2: compact policy prose can replace v1.4.** Rejected as tested. The compact hierarchy lost v1.4 wins and added pragmatic regressions.

**H3: a broad targeted example pack will unlock hard cases.** Rejected as tested for promotion. Examples have local signal but the seven-family pack confounds grouped-event gains with abstention and cluster regressions.

**H4: unconstrained LLM candidate stages should replace deterministic candidates.** Rejected for the tested event-table and answer-option implementations. Evidence localization was not enough; numeric slot fidelity, canonical surface validity, and final policy selection failed.

**H5: candidate-constrained verification should be promoted now.** Rejected as tested for promotion. It is safer than free-form repair but does not help without better candidate recall.

**H6: deterministic candidate-builder coverage is now the largest actionable bottleneck.** Supported. The best control can infer beyond candidates sometimes, but all failed pipeline arms point back to missing or incomplete candidate surfaces.

## Implementation Critique

The current candidate builder is appropriately conservative and auditable, but it is now doing research work beyond its original scaffold role. It is a sequence of narrow regex-style builders for high-value known patterns. That made sense for the temporal-candidate pivot, and it produced the current operational F0 strength, but the enriched slice shows the limits: common residual families still have no candidate at all.

The LLM option implementations failed for different reasons than the deterministic builder. G5 found evidence but lost required count/window slots; G6 was too strict and collapsed to `unknown`; G6b retained deterministic seeds but over-trusted poor LLM options. These are implementation failures, not mechanism closure, but they argue against another model call until the candidate contract is sharper.

The selector/verifier designs are currently downstream of bad inputs. If the candidate set is empty, a constrained verifier mostly confirms `unknown`; if the option set contains weak LLM no-reference or zero-rate labels, the deterministic selector can choose a bad but schema-valid answer. A better selector guard may help later, but first it needs candidate families worth selecting.

## Decision

Promote no new model-backed arm from G5/G6/G6b/G7/G9. Do not transfer these failed GPT-first cells to Qwen.

Keep `gan_frequency_s0_temporal_candidates_single_pass_v1_4_error_taxonomy_policy` as the strongest no-example GPT slice control for the current enriched slice. Keep F0 expanded builders + prose as the full-validation operational Gan S0 default until a tested arm beats it.

Next pull should be **deterministic candidate-builder gap analysis and implementation**, not another prompt, example, verifier, or Qwen run.

## Next Pull

1. Add a no-model inspection artifact over the 25-record slice that lists gold label, current candidate labels, v1.4 prediction, and failure family for every uncovered record.
2. Implement the smallest deterministic builder-gap variant with regression tests before code changes. First candidate families should be:
   - long-window quantified counts such as `2 per 7 month`, `5 per 13 month`, `multiple per 13/15 month`
   - grouped recent counts where the denominator is implied by elapsed months, not the local sentence
   - cluster spacing with per-cluster count such as `1 cluster per 4 day, 2 per cluster`
   - seizure-free multi-year/no-seizure-information cases that currently have no candidate
3. Run no-model validation first:
   - focused `tests/test_gan_temporal_candidates.py`
   - `uv run python scripts/validate_primitives.py --errors-only`
   - candidate coverage audit on the 25-record enriched slice
4. Only after candidate coverage improves, run one GPT 4.1-mini slice comparing v1.4 control against the new builder variant. Qwen transfer remains blocked until the GPT slice beats v1.4 or answers a clearly preregistered transferability question.

## Open Cells

- LLM candidate extraction remains open as a mechanism, but needs a stricter candidate schema with mandatory numeric slots and evidence-preserving artifacts.
- Candidate-constrained verification remains open after candidate recall improves.
- Targeted examples remain open only as narrower single-family packs, not another broad mixed pack.
- Selector guards for seeded options are open but lower priority than candidate coverage.

## Caveats

This synthesis is based on an enriched 25-record slice selected from Qwen 35B pragmatic misses. It is a search and diagnosis surface, not a full-validation estimate. Scorer semantics were not changed; evidence support remains diagnostic for these arms.

# Gan S0 Self-Consistency Variance Probe Preregistration

Date: 2026-05-28  
Status: Preregistered; no model runs launched  
Comparison group: `gan_s0_self_consistency_compute_allocation_gpt_cap25_v1`  
Related: `docs/planning/kanban_plan.md`, `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`, `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`, `docs/datasets/gan/gan_2026_label_audit.md`

## Research Question

Does spending extra inference on repeated sampling and deterministic aggregation improve Gan S0 seizure-frequency extraction, and does response variance identify records that are likely to be wrong?

## Motivation

The current Gan S0 operational surface is `gan_s0_candidate_builder_gap_v1` on GPT 4.1-mini. It improved candidate recall and is the strongest validated synthetic-validation surface, but remaining errors still include temporal-window ambiguity, cluster/range adjudication, unknown/no-reference confusion, and model-specific semantic misses. Self-consistency is a clean compute-allocation ablation: it keeps the prompt, deterministic candidates, schema, scorer, split, and model fixed while changing how many independent model samples are collected and how their canonical labels are aggregated.

This preregistration is intentionally smaller than a multi-agent design. It tests whether repeated samples expose useful disagreement before introducing new stage graphs, tools, optimizers, or prompt policies.

## Taxonomy

| Field | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Schema complexity | S0 seizure frequency |
| Clinical task family | frequency |
| Research axis | 3 - implementation variant / compute allocation |
| Comparison group | `gan_s0_self_consistency_compute_allocation_gpt_cap25_v1` |
| Primary varied factor | `compute_allocation_and_aggregation_policy` |
| Frozen stage graph | `g2_candidates_adjudicate` |
| Frozen implementation | `gan_s0_candidate_builder_gap_v1` |
| Frozen program architecture | `temporal_candidates_single_pass` |
| decision_scope target | `arm` |
| Mechanism closure allowed? | No. This cap-25 probe can justify a larger self-consistency gate or reject this exact aggregation arm only. |

## Hypothesis

Repeated stochastic samples over the frozen builder-gap v1 Gan S0 surface will improve monthly accuracy when deterministic aggregation preserves canonical-label validity, and high within-record disagreement will be enriched for baseline errors.

## Fixed Controls

| Control | Value |
| --- | --- |
| Split | `gan_2026_fixed_v1:validation` |
| Cap | First 25 validation records, same ordering used by existing Gan cap-25 grids |
| Model | GPT 4.1-mini |
| Provider config baseline | `configs/models/gan_s0_gpt4_1_mini.json` |
| Sampling config | New GPT 4.1-mini config with the same model/provider and a non-zero temperature fixed before the run |
| Scorer | `gan_frequency_deterministic_v1` |
| Gold label | `seizure_frequency_number[0]` only |
| Reference label | Diagnostic/hard-case flag only; never promotion gold |
| Program variant | `gan_frequency_s0_temporal_candidates_single_pass` |
| Prompt version | Builder-gap v1 prompt used by the promoted Gan S0 operational surface |
| Candidate builder | `gan_s0_candidate_builder_gap_v1`, unchanged |
| Structured output | Provider JSON schema with Pydantic validation |
| Few-shot policy | none |
| Verifier/repair policy | none beyond existing artifact bridge surface normalization |
| Primary metric | Monthly frequency accuracy |
| Required diagnostics | Purist category, Pragmatic category, schema-valid prediction rate, evidence support, valid/invalid count |
| Compute diagnostics | samples per record, successful samples per record, model-call count, estimated cost, wall-clock latency, mean and p95 latency |
| Variance diagnostics | unique canonical labels per record, vote entropy, top-vote margin, normalized-value spread, schema-invalid sample count |
| Test reporting | forbidden |

The sampling config must be named explicitly before execution. The temperature is part of the preregistered compute-allocation surface, not a prompt-tuning knob. Do not tune temperature from cap outcomes.

## Repeated-Sample Contract

Each sampled prediction must be stored as an individual record before aggregation. The aggregation layer consumes only validated prediction artifacts and scorer-normalized labels; it must not inspect the gold label except during evaluation.

Required per-sample fields:

| Slot | Meaning |
| --- | --- |
| `sample_id` | Stable within-record sample index, such as `s1` through `s5`. |
| `run_id` | Parent run or sample-batch identifier. |
| `record_id` | Gan record identifier from the fixed split. |
| `raw_prediction` | Model output before validation/repair. |
| `canonical_label` | Schema-valid canonical Gan label after existing artifact bridge normalization. |
| `monthly_value` | Deterministic scorer conversion for variance diagnostics. |
| `purist_category` | Diagnostic scorer category. |
| `pragmatic_category` | Diagnostic scorer category. |
| `evidence_text` | Model evidence quote for the sample. |
| `schema_valid` | Pydantic/schema validity flag. |
| `evidence_supported` | Existing evidence-support diagnostic. |
| `latency_seconds` | End-to-end sample latency if available. |

Invalid samples remain in the variance report. Aggregators may ignore invalid samples for label voting, but the invalid count is part of the decision gate.

## Arms

All treatment aggregation arms reuse the same five sampled predictions per record. This keeps the model-call budget fixed while comparing aggregation policies.

| Arm | Policy | Samples per record | Aggregation rule | Priority |
| --- | --- | ---: | --- | --- |
| S0 | matched single pass | 1 | First stochastic sample only; same prompt/config as repeated samples | Required control |
| S1 | majority vote | 5 | Choose the canonical label with the most valid votes | Required |
| S2 | confidence-weighted vote | 5 | Weight valid votes by model-reported confidence when present; fall back to equal weight when confidence is missing or invalid | Required diagnostic |
| S3 | majority plus deterministic tie-break | 5 | Majority vote, then tie-break by valid evidence support, then lower monthly-value spread, then first valid sample | Required |
| S4 | abstain-on-instability | 5 | Use S3 unless vote entropy or top-vote margin crosses a preregistered instability threshold; otherwise emit `unknown` only if `unknown` is among valid votes | Optional if aggregation code can preserve abstention metadata |

S2 must not let uncalibrated confidence override canonical-label validity. Confidence is diagnostic and may be reported as unreliable if it does not predict correctness.

## Config Plan

Create configs only after the sample-batch runner or aggregation adapter is available. Planned config IDs:

| Planned config | Purpose |
| --- | --- |
| `gan_s0_self_consistency_s0_single_sample_cap25_gpt4_1_mini` | Matched one-sample control under the stochastic sampling config. |
| `gan_s0_self_consistency_sample5_cap25_gpt4_1_mini` | Five repeated samples per record over the frozen builder-gap v1 surface. |
| `gan_s0_self_consistency_aggregate_s1_majority_cap25_gpt4_1_mini` | Offline aggregation view over the sample5 artifacts. |
| `gan_s0_self_consistency_aggregate_s2_confidence_weighted_cap25_gpt4_1_mini` | Offline aggregation view over the sample5 artifacts. |
| `gan_s0_self_consistency_aggregate_s3_tiebreak_cap25_gpt4_1_mini` | Offline aggregation view over the sample5 artifacts. |
| `gan_s0_self_consistency_aggregate_s4_abstain_instability_cap25_gpt4_1_mini` | Optional offline aggregation view over the sample5 artifacts. |

Minimum taxonomy block for model-call configs:

```json
{
  "dataset": "gan_2026",
  "schema_complexity": "gan_s0",
  "clinical_task_family": "frequency",
  "comparison_group": "gan_s0_self_consistency_compute_allocation_gpt_cap25_v1",
  "stage_graph_id": "g2_candidates_adjudicate",
  "varied_factor": "compute_allocation_and_aggregation_policy",
  "implementation_variant": "gan_s0_candidate_builder_gap_v1",
  "intended_decision": "pending"
}
```

Metric caveats must state: cap-25 search only, `decision_scope: arm`, Gan gold is `seizure_frequency_number[0]`, `reference` is diagnostic only, and repeated sampling changes compute budget rather than prompt, scorer, candidate builder, or split.

## Variance Reporting

The inspection must report record-level disagreement before interpreting aggregate accuracy.

| Diagnostic | Definition | Purpose |
| --- | --- | --- |
| `unique_label_count` | Number of distinct valid canonical labels among samples | Direct response variability. |
| `vote_entropy` | Entropy of the valid canonical-label vote distribution | Continuous instability score. |
| `top_vote_margin` | Top vote share minus second vote share | Tie-risk indicator. |
| `monthly_value_range` | Max minus min scorer-converted monthly values among valid samples | Severity of numerical disagreement. |
| `valid_sample_rate` | Valid samples divided by requested samples | Schema robustness under sampling. |
| `evidence_support_rate` | Supported samples divided by valid samples | Evidence stability. |
| `baseline_error_and_disagreement` | Whether S0 is wrong and `unique_label_count > 1` | Tests whether variance predicts errors. |

Report these diagnostics overall and on overlapping Gan slices: label/reference disagreement, seizure-free interval, bounded window/YTD, historical-prior window, cluster, and unknown/no-reference boundary.

## Gates

| Decision | Rule |
| --- | --- |
| Pass to cap-50 | Best aggregation arm improves over S0 by at least 2 correct records on cap-25, schema-valid aggregate rate >= 95%, evidence support >= 95%, and no increase greater than one record in unknown/no-reference confusion. |
| Hold for targeted residual replay | Accuracy is within one record of S0 but high disagreement is enriched among S0 errors, or a temporal slice shows a plausible rescue pattern without schema/evidence regression. |
| Reject arm | Aggregation trails S0 by more than one record, schema validity < 95%, evidence support < 95%, or tie-breaking creates unsupported/prose/noncanonical labels. |
| Qwen port | Deferred. Qwen repeated sampling is costly and must wait for a GPT cap-25 signal or a specific local-variance question. |
| Full validation | Deferred until cap-25 plus cap-50 or targeted residual replay supports the aggregation policy. |
| Mechanism closure | Forbidden from this preregistration alone. |

Cost and latency are first-class outcomes. An accuracy tie with 5x calls is not a promotion unless variance diagnostics are useful enough to justify selective deployment on hard records.

## Explicit Non-Goals

- Do not change the Gan loader, split, scorer, label normalization, evidence scorer, candidate builders, or prompt policy.
- Do not use `reference[0]` as gold or `reference[1]` as evidence.
- Do not tune sampling temperature, sample count, or aggregation thresholds from test-holdout outcomes.
- Do not combine self-consistency with R11 date/event stages, R12 entity-first stages, examples, GEPA, or tool-during arms in this comparison group.
- Do not claim self-consistency or multi-agent systems are rejected from a null cap-25 result.
- Do not report test-split results from this protocol.

## Inspection Requirements

The post-run inspection must include:

- Run IDs, config paths, model config paths, prompt versions, and sample count.
- Taxonomy block with `decision_scope: arm`.
- Metrics table for S0-S4: monthly, Purist, Pragmatic, schema validity, evidence support, valid/invalid count, cost, and latency.
- Variance table with `unique_label_count`, entropy, top-vote margin, monthly-value spread, and valid-sample rate.
- Error-prediction analysis: whether disagreement predicts S0 errors, with at least precision/recall or a 2x2 table.
- Temporal/hard-case slice table using the R11 slice definitions.
- At least five qualitative examples where aggregation changed the final label or exposed instability.
- Open cells explicitly listing ExECT S5 self-consistency, Qwen transfer, selective rerun-on-instability, R11/R12 stage-graph integration, and full-validation promotion.

## Open Cells

- ExECT S5 self-consistency over the promoted frequency verifier surface.
- Selective self-consistency only for records with high deterministic ambiguity or candidate conflict.
- Qwen repeated sampling under local latency constraints.
- Self-consistency over R11 date/event or R12 entity-first winners after those gates run.
- Confidence calibration if model-reported confidence proves predictive rather than decorative.

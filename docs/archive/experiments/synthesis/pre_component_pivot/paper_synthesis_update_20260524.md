# Paper Synthesis Update - Gan Builder-Gap and Post-Suite Priorities

Date: 2026-05-24  
Status: Source synthesis update for paper-facing results narrative  
Decision scope: results synthesis and prioritization; no scorer or benchmark semantics changed

## Current Read

The active research story has shifted from broad model-suite coverage to a cleaner Gan S0 mechanism result. The frozen model suite is complete for its planned S1/S4/Gan F0 surfaces, and the ExECT S2/S3 extension has been explicitly declined unless a manuscript later needs a middle-ladder claim. The newest paper-relevant result is the verified Gan S0 candidate-builder gap v1 surface: GPT 4.1-mini becomes the operational Gan S0 default, while Qwen3.6:35b clears the preregistered local transfer gate but remains below the hosted default.

## Source Artifacts

| Artifact | Role |
| --- | --- |
| `docs/planning/kanban_plan.md` | Active steering board and operational defaults |
| `docs/outline.md` | Project research aims and schema/model framing |
| `docs/datasets/gan/gan_2026_label_audit.md` | Gan gold-source and label-policy guidance |
| `docs/policies/deterministic_scorer_semantics.md` | Current Gan and ExECT scorer meanings |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_gpt_full_validation_rerun_inspection_20260523.md` | Verified GPT builder-gap full-validation result |
| `docs/experiments/gan/gan_s0_operational_default_promotion_review_20260523.md` | Promotion review for Gan S0 operational default |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_preregistration_20260523.md` | Preregistered Qwen transfer gates |
| `docs/experiments/gan/gan_s0_candidate_builder_gap_v1_qwen35b_full_validation_inspection_20260523.md` | Completed Qwen transfer validation result |
| `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md` | Completed frozen-suite model-profile synthesis |
| `docs/experiments/synthesis/model_suite_exect_s2_s3_extension_v1_decision_20260523.md` | Decision not to run S2/S3 model-suite extension |
| `docs/experiments/synthesis/experiment_registry.json` | Current registry rows and run IDs |

## Results Narrative Update

### Gan S0 Candidate-Builder Gap V1

The verified GPT rerun should replace stale G16 and older Gan F0 rows when describing the historical canonical Gan S0 surface. The task remains Gan 2026 synthetic validation, split `gan_2026_fixed_v1:validation`, scored here with `gan_frequency_deterministic_v1`. Direct benchmark-comparison claims should be rescored with `gan2026_paper_reproduction`; the primary gold remains `seizure_frequency_number[0]`, and `reference[0]` remains a secondary difficulty signal.

| Model / arm | Run ID | N | Monthly | Purist | Pragmatic | Schema | Evidence | Decision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| GPT 4.1-mini builder-gap v1 | `gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z` | 299 | **80.6%** | **86.0%** | **88.6%** | **100.0%** | **100.0%** | Operational default |
| Qwen3.6:35b builder-gap v1 | `gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z` | 299 predicted / 297 valid-scored | **70.7%** | **83.2%** | **90.6%** | **99.3%** | **99.7%** | Accepted transfer arm |
| GPT 4.1-mini F0 prior default | model-suite F0 anchor | 299 | 68.1% | not restated | not restated | 99.7% | 100.0% | Superseded operationally |
| Qwen3.6:35b F0 baseline | model-suite F0 anchor | 299 | 64.4% | not restated | not restated | 100.0% | 100.0% | Superseded as local comparison |

Paper-facing interpretation:

- The strongest current Gan S0 claim is no longer "temporal candidates reach roughly 65% monthly." It is that tightening deterministic candidate recall before LLM adjudication raises GPT 4.1-mini to 80.6% monthly accuracy without sacrificing schema validity or evidence support.
- The Qwen result is a transfer success, not a parity claim. Qwen3.6:35b improves materially over its F0 baseline and clears the preregistered 70% monthly gate, but it trails the GPT builder-gap default by about 9.9 percentage points on monthly accuracy.
- The mechanism claim should stay scoped: builder-gap v1 resolved a documented candidate-recall bottleneck and moved residual errors toward semantic adjudication, but it does not close Gan S0 broadly or reproduce the published Gan Real(300) benchmark.

### Frozen Model Suite

The frozen model suite remains useful as a model-profile section, not as the operational decision source for Gan S0. It covers ExECT S1, ExECT S4, and Gan F0 under fixed surfaces and should be reported as bottleneck diagnosis:

- ExECT S1 tests narrow benchmark-policy alignment, especially seizure-type policy.
- ExECT S4 tests broad multi-family extraction where pooled micro F1 hides divergent family profiles.
- Gan F0 tests temporal candidate adjudication before the candidate-builder gap v1 improvement.

The S2/S3 extension is not part of the next paper loop unless the manuscript makes a specific middle-ladder claim that S1/S4 cannot support.

## Claim Readiness

| Claim | Readiness | Guidance |
| --- | --- | --- |
| Deterministic candidate-builder gap v1 is the current best Gan S0 operational surface on synthetic validation | Supported | Cite GPT rerun inspection, promotion review, registry row, split, scorer, and synthetic-validation caveat |
| Qwen3.6:35b transfers the builder-gap v1 surface successfully | Supported | Cite preregistration and inspection; phrase as accepted local transfer, not hosted parity |
| Model choice depends on extraction surface rather than a universal leaderboard | Supported | Use the completed model-suite synthesis; keep decision scope as arm/model-profile |
| Qwen is generally equivalent to GPT for Gan | Risky | Older temporal-candidates parity language is superseded by builder-gap v1; current GPT default is clearly higher monthly |
| The project beats published Gan or ExECT benchmarks | Unsupported | Published Real(300) and CUI-aware ExECT reproduction remain blocked/deferred |
| Candidate-constrained verification or LLM candidate extraction should be next | Plausible but premature | Requires sharper candidate schemas and residual analysis before more model spend |

## Next Priorities After Current Kanban Completion

1. **Freeze paper result tables from primary artifacts.** Build a small table pack that cites run IDs, configs, splits, scorer modes, and caveats for: Gan builder-gap v1 GPT/Qwen, frozen model-suite S1/S4/Gan F0, ExECT schema ladder, and key negative ablations. This is the highest-value next step because it turns experiment sprawl into manuscript evidence.
2. **Run Gan builder-gap residual error forensics before new model arms.** Compare GPT and Qwen builder-gap mismatches by gold pragmatic stratum, candidate availability, invalid-label cases, and semantic mismatch type. The decision it should inform is whether the next mechanism work is deterministic candidate expansion, stricter candidate schema, or model-side adjudication.
3. **Keep provider adapter validation test-only.** The Cursor SDK compatibility report is review-only. Before provider config changes, run `uv run pytest tests/test_llm_adapters.py tests/test_model_comparison_configs.py` plus targeted provider smokes.
4. **Promote only source-backed paper prose.** Cursor SDK drafts can seed wording, but final claims should be copied only after checking registry rows, inspection docs, and run artifacts.
5. **Defer benchmark-reproduction claims.** Published Gan Real(300), CUI-aware ExECT Table 1, test holdout reporting, and optimizer rungs should stay deferred unless the manuscript explicitly needs them and the required scorer/data gates are reopened.

## Remaining Risks

- The registry currently contains some unrelated formatting churn from JSON reserialization; publication tables should verify headline rows against `metrics.json` or inspection docs before final copy.
- Qwen builder-gap scoring has 297 valid-scored records because two predictions were invalid labels; report the denominator when comparing to the GPT 299/299 row.
- Evidence quote support is diagnostic source grounding, not a human adjudicated evidence-quality metric.
- ExECT S4 pooled micro must always travel with per-family caveats; it should not become a simple model ranking.

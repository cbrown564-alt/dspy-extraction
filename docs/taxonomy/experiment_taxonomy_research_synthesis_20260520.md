# Experiment Taxonomy Implementation Synthesis

Date: 2026-05-20  
Status: Research log after taxonomy implementation (steps 1-7) and analysis pass (2026-05-20)  
Source decision: `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`

## Context

The hybrid component taxonomy was introduced to make the project's central design
question measurable: how much responsibility should sit in deterministic
components, how much should sit in LLM components, and where should those
components enter the extraction pipeline?

The immediate operational problem was that the repository had enough experiment
configs, run directories, metrics files, and decision notes that narrative
memory was no longer a reliable research instrument. Names such as "S4",
"v4.10", "temporal candidates", and "verify-repair" remained useful artifact
identifiers, but they did not consistently expose the scientific variables being
tested.

## Work Completed

Steps 1-7 of `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md` are now
implemented as repo artifacts:

- `docs/experiments/synthesis/experiment_registry.json` seeds the canonical experiment registry with
  82 experiment rows, one per distinct metric-bearing experiment ID from local
  run artifacts.
- `docs/taxonomy/experiment_taxonomy_schema.md` defines controlled values and usage rules
  for dataset, schema complexity, clinical task family, model track, program
  architecture, hybrid balance, interleaving position, knowledge source, control
  mode, evidence, normalization, verification, outcome, and comparison groups.
- `src/clinical_extraction/experiments/taxonomy.py` adds typed taxonomy metadata
  for new experiment configs.
- `src/clinical_extraction/experiments/registry_validation.py` validates registry
  controlled values, canonical run references, decision-document requirements,
  comparison-group compatibility, and config coverage.
- `scripts/validate_experiment_taxonomy.py` exposes the validation as a command
  line check.
- `tests/test_experiment_registry_validation.py` covers registry validation
  behavior, including controlled-value failures, missing canonical runs,
  decision-doc requirements, and comparison-group compatibility.
- `tests/test_experiment_configs.py` now requires each experiment config to have
  inline taxonomy, an explicit taxonomy exemption, or registry coverage.
- New Gan temporal-candidates and ReAct temporal-tools configs include inline
  taxonomy blocks, so the taxonomy is now part of experiment design rather than
  only retrospective cleanup.

The current registry outcome distribution is:

| Outcome | Rows |
| --- | ---: |
| exploratory | 62 |
| freeze | 4 |
| hold | 4 |
| promote | 2 |
| reject | 7 |
| superseded | 2 |

The current registry hybrid-balance tags are:

| Hybrid balance class | Tag count |
| --- | ---: |
| `L1_llm_constrained` | 67 |
| `H1_post_deterministic` | 7 |
| `H2_pre_deterministic` | 7 |
| `H4_deterministic_first_llm_adjudicates` | 6 |

These are tag counts, not mutually exclusive experiment counts, because a row
can carry more than one hybrid-balance class.

## Validation

Focused validation was run after implementation:

```text
uv run python scripts/validate_experiment_taxonomy.py --errors-only
uv run pytest tests/test_experiment_registry_validation.py -q
```

The taxonomy validator passes with no errors under `--errors-only`. It reports
one warning for a documented missing local run directory:
`gan_s0_synthesis_bootstrap_full_validation_gpt4_1_mini_20260518T065115Z`.
The row documents that the run artifact is referenced by docs but not present in
the current local `runs/` folder, so the missing run remains visible rather than
silently invalidating the registry.

The focused registry test suite passes: 10 tests passed. The only test warnings
observed were DSPy deprecation warnings from installed package code, not taxonomy
validation failures.

## Observations

The registry already makes several research patterns visible.

First, most historical rows remain `L1_llm_constrained`. This reflects the
project's origin in structured LLM extraction with JSON schema, Pydantic
validation, and benchmark-facing scorers. Hybrid interventions exist, but they
are concentrated in the newer Gan and ExECT bridge/repair families rather than
being evenly distributed across the whole experiment history.

Second, the two promoted systems are both Gan temporal-candidates variants:

| Experiment ID | Model track | Program architecture | Hybrid class | Comparison group |
| --- | --- | --- | --- | --- |
| `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails` | `gpt4_1_mini` | `temporal_candidates_verify_repair` | `H2_pre_deterministic`, `H4_deterministic_first_llm_adjudicates` | `gan_s0_architecture_gpt_validation_v1` |
| `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails` | `qwen35b` | `temporal_candidates_verify_repair` | `H2_pre_deterministic`, `H4_deterministic_first_llm_adjudicates` | `gan_s0_architecture_qwen_validation_v1` |

This strengthens the current working hypothesis that Gan seizure-frequency
performance improved through deterministic temporal scaffolding plus LLM
selection/verification, not through prompt wording alone.

Third, the pending Gan ReAct temporal-tools probe is now tagged as
`H3_interleaved_tool_hybrid` with `tool_during` and `during` interleaving
positions. That makes it a clean conceptual contrast against temporal-candidates
runs, which use deterministic preconditioning and deterministic-first
adjudication. A ReAct result can therefore be interpreted as a test of
interleaving position, not as a generic test of whether temporal rules help.

Fourth, ExECT S1-S4 full validation runs are now represented as schema
complexity values inside comparison groups rather than as unrelated branches.
This supports schema-ladder analysis while preserving the caveat that changing
schema breadth also changes field-family aggregation and scorer surface.

## Direct Answers To Near-Term Research Questions

### Which promoted systems are `H1`, `H2`, `H3`, or `H4`?

The current registry has two promoted systems. Both are Gan S0 temporal-candidates
verify-repair systems, and both are tagged as `H2_pre_deterministic` plus
`H4_deterministic_first_llm_adjudicates`.

| Experiment ID | Model | Hybrid class | Interpretation |
| --- | --- | --- | --- |
| `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails` | `gpt4_1_mini` | `H2_pre_deterministic`, `H4_deterministic_first_llm_adjudicates` | Deterministic temporal candidates enter before extraction; the LLM verifies/repairs around those candidates. |
| `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails` | `qwen35b` | `H2_pre_deterministic`, `H4_deterministic_first_llm_adjudicates` | Same architecture applied to the local model track. |

No promoted system is currently tagged as pure `H1_post_deterministic` or
`H3_interleaved_tool_hybrid`. The key `H1` Gan anchor,
`gan_s0_verify_repair_full_validation_gpt4_1_mini`, is superseded. The key `H3`
Gan probe, `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails`, is
pending rather than promoted.

### Did deterministic preconditioning outperform deterministic postprocessing on Gan?

Tentatively, yes for the promoted decision, but the evidence is cleaner for the
research conclusion than for a single headline metric.

Within the GPT Gan architecture comparison group, the superseded `H1` verify-repair
anchor reported monthly-frequency accuracy of 0.654, Purist category accuracy of
0.727, Pragmatic category accuracy of 0.792, evidence support of 0.927, and
schema validity of 0.967. The promoted GPT temporal-candidates `H2/H4` row
reported monthly-frequency accuracy of 0.651, Purist category accuracy of 0.765,
Pragmatic category accuracy of 0.842, evidence support of 1.000, and schema
validity of 0.997.

So deterministic preconditioning did not beat the GPT `H1` post-deterministic
anchor on monthly-frequency accuracy by point estimate; it was slightly lower.
It did improve Purist category accuracy, Pragmatic category accuracy, evidence
support, and schema validity, which explains why the promoted decision should be
read as a robustness/evidence-grounding promotion rather than a simple monthly
accuracy win.

For Qwen, the promoted temporal-candidates row reported monthly-frequency
accuracy of 0.658, Purist category accuracy of 0.755, Pragmatic category
accuracy of 0.826, evidence support of 1.000, and schema validity of 0.997. The
registry currently does not expose an equally clean Qwen full-validation `H1`
post-deterministic comparator, so the Qwen result supports promotion of the
preconditioned system but does not by itself isolate preconditioning versus
postprocessing.

### Did ExECT gains come from model capability, benchmark policy alignment, or deterministic bridge behavior?

The current registry does not yet identify a single cause. The best-supported
answer is: ExECT gains currently appear to come mainly from model capability plus
benchmark policy alignment during constrained extraction; deterministic bridge
behavior is present as scoring, validation, and policy scaffolding, but it has
not yet been isolated as the causal driver of the full-validation gains.

The frozen GPT ExECT schema-ladder rows are all tagged `L1_llm_constrained`, with
deterministic roles including benchmark label policy, field-family scoring, JSON
schema constraint, and Pydantic validation. Their headline micro F1 decreases as
schema breadth expands:

| Row | Model | Schema | Headline micro F1 | Status |
| --- | --- | --- | ---: | --- |
| `exect_s0_s1_validation_full_gpt4_1_mini` | `gpt4_1_mini` | `exect_s1` | 0.923 | freeze |
| `exect_s2_validation_full_gpt4_1_mini` | `gpt4_1_mini` | `exect_s2` | 0.809 | freeze |
| `exect_s3_validation_full_gpt4_1_mini` | `gpt4_1_mini` | `exect_s3` | 0.721 | freeze |
| `exect_s4_validation_full_gpt4_1_mini` | `gpt4_1_mini` | `exect_s4` | 0.655 | freeze |

The Qwen hold rows show lower S1 performance than GPT but comparable S2/S3 point
estimates under the current local scorer:

| Row | Model | Schema | Headline micro F1 | Status |
| --- | --- | --- | ---: | --- |
| `exect_s0_s1_validation_full_qwen35b_ollama` | `qwen35b` | `exect_s1` | 0.790 | hold |
| `exect_s2_validation_full_qwen35b_ollama` | `qwen35b` | `exect_s2` | 0.826 | hold |
| `exect_s3_validation_full_qwen35b_ollama` | `qwen35b` | `exect_s3` | 0.722 | hold |

The strongest causal claim available now is that ExECT performance is sensitive
to schema complexity and model track under benchmark-aligned constrained
extraction. The registry cannot yet cleanly separate prompt-level benchmark
policy alignment from deterministic bridge behavior because many historical
ExECT runs combine JSON/Pydantic constraints, benchmark policy instructions, and
field-family scoring in the same row.

### Which clinical task families still rely mostly on LLM judgment without deterministic support?

The broad ExECT families still rely most heavily on constrained LLM judgment.
Current `L1_llm_constrained` rows include frequency rows, but Gan frequency now
has promoted deterministic temporal support. The clearer support gap is in ExECT
multi-family extraction and the S1 families of diagnosis, seizure type, and
medication.

In the registry, `L1_llm_constrained` appears across:

| Clinical task family | `L1_llm_constrained` row count |
| --- | ---: |
| `frequency` | 41 |
| `multi_family` | 17 |
| `diagnosis` | 9 |
| `seizure_type` | 9 |
| `medication` | 9 |

The row counts should not be read as performance weights, because historical Gan
frequency runs dominate the archive. Interpreted as design coverage, the main
remaining gap is deterministic support for ExECT diagnosis, seizure type,
medication, and broader S2-S4 field families. Medication in particular is a good
candidate for controlled vocabulary or post-hoc normalization experiments, while
diagnosis and seizure type need careful benchmark-policy versus clinical-validity
separation.

### Which future experiments would most cleanly test interleaving position while holding dataset, schema, model, and scorer fixed?

The cleanest near-term test is Gan S0 on Qwen35b, fixed to
`gan_2026_fixed_v1:validation`, `gan_frequency_deterministic_v1`, schema
`gan_s0`, and the same guardrail record slice or full validation split:

| Interleaving condition | Candidate experiment | Fixed controls |
| --- | --- | --- |
| `pre` plus `post` / `H2-H4` | `gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails` or matched slice | Gan S0, Qwen35b, deterministic Gan scorer, same split/slice |
| `tool_during` / `H3` | `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails` | Same dataset, schema, model, scorer, and guardrail slice |
| `post` / `H1` | A matched Qwen35b verify-repair run without precomputed temporal candidates | Same dataset, schema, model, scorer, and split/slice |
| `during` / `L1` | A matched Qwen35b direct constrained run with no temporal candidates or tools | Same dataset, schema, model, scorer, and split/slice |

This would directly test whether temporal knowledge works best as precomputed
candidate context, a tool available during reasoning, post-hoc repair, or prompt
policy alone.

For ExECT, the cleanest later test would hold `exect_v2`, one schema level such
as `exect_s1`, one model such as GPT 4.1-mini or Qwen35b, and the same
field-family scorer fixed while comparing: benchmark policy only during
extraction, deterministic post-hoc benchmark bridge, pre-injected controlled
vocabularies for medication/seizure labels, and tool-mediated normalization.
That experiment should not mix schema expansion with interleaving position.

## Interpretation

The taxonomy implementation converts a loose experiment archive into a
research-facing design matrix. The most important shift is methodological:
future experiment claims can now be framed around controlled variables such as
`hybrid_balance_class`, `interleaving_positions`, `program_architecture`,
`model_track`, and `schema_complexity`, rather than around local version names.

For Gan, the registry is already strong enough to support architecture-level
questions within model tracks, especially direct or verify-repair baselines
versus temporal-candidates variants. For ExECT, it is strong enough to preserve
the schema complexity ladder and distinguish GPT frozen anchors from Qwen hold
rows, but less mature for isolating whether gains come from benchmark policy
prompting, deterministic bridges, or model capability.

The current balance of tags also suggests a research gap: deterministic support
has been operationalized most clearly for Gan temporal reasoning, while broad
ExECT field families still depend heavily on constrained LLM extraction and
post-hoc benchmark-facing policy alignment. That is not necessarily a weakness,
but it should become an explicit next experimental question.

## Caveats

A paper-ready curated matrix export lives at `docs/archive/experiments/synthesis/pre_component_pivot/experiment_registry_matrix_20260520.md`
(regenerate with `uv run python scripts/export_experiment_registry_matrix.py`). Retrospective
rows outside that export may still need clinical review.

Retrospective tagging is partly inferred from config and run metadata. Historical
experiments may have changed multiple factors at once, so comparison groups are
more reliable than raw row adjacency.

The `hybrid_balance_class` field is intentionally coarse. It should be used for
stratified analysis, not as a substitute for detailed fields such as
`deterministic_roles`, `llm_roles`, `normalization_strategy`, and
`verification_strategy`.

The current validation checks structural integrity, controlled vocabularies,
artifact references, decision-doc coverage, and obvious comparison-group
incompatibilities. It does not prove that every retrospective row has been
clinically interpreted correctly.

Benchmark-facing scorer outputs remain distinct from published benchmark
reproduction. Current rows generally refer to fixed synthetic validation/test
splits and deterministic local scorer modes, not final external benchmark
claims.

Evidence support remains a diagnostic based on model quotes and deterministic
span checks, not independent clinical adjudication.

## Taxonomy Analysis Pass (2026-05-20)

This section completes the recommended next pull from the taxonomy implementation
synthesis. Registry validation still passes under `--errors-only` after five
targeted `headline_metric` backfills.

### Registry summary (82 rows)

**By outcome**

| Outcome | Rows |
| --- | ---: |
| exploratory | 62 |
| freeze | 4 |
| hold | 4 |
| promote | 2 |
| reject | 7 |
| superseded | 2 |

**By dataset × outcome**

| Dataset | exploratory | freeze | hold | promote | reject | superseded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| exect_v2 | 20 | 4 | 4 | 0 | 1 | 0 |
| gan_2026 | 42 | 0 | 0 | 2 | 6 | 2 |

**Representative dimension tuples** (same dataset, schema, model, architecture, hybrid class, outcome)

| n | Dataset | Schema | Model | Architecture | Hybrid class | Outcome |
| ---: | --- | --- | --- | --- | --- | --- |
| 11 | gan_2026 | gan_s0 | qwen35b | direct_single_pass | L1 | exploratory |
| 8 | gan_2026 | gan_s0 | gpt4_1_mini | direct_single_pass | L1 | exploratory |
| 6 | gan_2026 | gan_s0 | qwen9b | direct_single_pass | L1 | exploratory |
| 4 | exect_v2 | exect_s1 | gpt4_1_mini | single_pass | L1 | exploratory |
| 3 | exect_v2 | exect_s1 | qwen35b | single_pass | L1 | exploratory |

Most historical rows remain `L1_llm_constrained` direct or single-pass extraction.
Promoted and superseded anchors cluster in named Gan architecture comparison groups
and ExECT schema-ladder freeze/hold rows.

### Gan architecture comparison (full validation)

#### `gan_s0_architecture_gpt_validation_v1`

Fixed: `gan_2026_fixed_v1:validation`, `gan_frequency_deterministic_v1`, schema `gan_s0`.
Headline: monthly-frequency accuracy (valid predictions); secondary metrics from registry.

| Architecture | Hybrid class | Outcome | Monthly | Purist | Pragmatic | Evidence | Schema valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| synthesis bootstrap | L1 | superseded | 62.9% | 70.1% | 73.9% | 89.9% | 97.3% |
| verify-repair v2 | H1 post | superseded | **65.4%** | 72.7% | 79.2% | 92.7% | 96.7% |
| temporal-candidates v1.1 | H2 pre + H4 adjudicate | **promote** | 65.1% | **76.5%** | **84.2%** | **100%** | **99.7%** |

**Interpretation (GPT):** Temporal-candidates does not win monthly frequency by point
estimate versus superseded verify-repair (−0.3 pp). Promotion is justified by Purist,
Pragmatic, evidence support, and schema validity — a robustness/evidence-grounding
decision, not a raw monthly-accuracy win. Synthesis bootstrap remains the weakest
hosted reference on category and evidence metrics.

#### `gan_s0_architecture_qwen_validation_v1`

| Architecture | Hybrid class | Outcome | Monthly | Purist | Pragmatic | Evidence | Schema valid |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| direct + guardrails | L1 during | exploratory (anchor) | 55.9% | 61.9% | 70.5% | 99.6% | 94.0% |
| temporal-candidates v1.1 | H2 pre + H4 adjudicate | **promote** | **65.8%** | **75.5%** | **82.6%** | **100%** | **99.7%** |

**Interpretation (Qwen):** Full-validation temporal-candidates clears the pre-registered
promotion gate (+9.9 pp monthly vs direct) while preserving near-perfect evidence support.
There is no equally clean Qwen full-validation `H1` verify-repair row in this group; slice
evidence below shows post-hoc verify-repair underperforms direct on hard cases.

### Gan interleaving-position probe (`gan_s0_hard_slice_qwen_architecture_v1`)

Same 14-record fixture (`data/fixtures/gan_s0_qwen_error_regression_slice.json`),
same scorer. Slice metrics are not extrapolated to full validation.

| Architecture | Hybrid / interleaving | Monthly (valid) | Notes |
| --- | --- | ---: | --- |
| direct v2.2 | L1 / during | 71.4% | Strong on original 10 targets; 0/4 infrequent quantified |
| verify-repair v2.3 | H1 / during+post | 46.2% | Forces infrequent quantification; breaks 5/10 originals |
| temporal-candidates v1.1 (B1) | H2+H4 / pre+during+post | **100%** | Canonical slice run `…232514Z` |
| temporal event table (B2) | H2+H4 / pre+during+post | **100%** | Extra model call vs B1; same slice score |
| ReAct temporal tools (H3) | H3 / tool_during+during | **42.9%** (7 valid) | Run `…173943Z`; **reject** |

**Interpretation (interleaving):** On hard infrequent cases, deterministic **pre**-injected
candidates (H2/H4) dominate both constrained direct extraction and **post** verify-repair.
ReAct (`H3`) is a clear **negative control**: 50% schema validity, 42.9% monthly on valid
predictions only, ~93 s/record. Tool-during temporal rules did not replace pre-conditioning;
6/14 trajectories hit `extract_temporal_anchors` arg errors; invalid labels are bare counts
(`5`, `9`, `3 to 4`). **Conclusion:** keep promoted temporal-candidates (H2/H4); do not scale
ReAct to full validation without structural fixes.

Inspection: `docs/experiments/gan/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_inspection_20260520.md`

### ExECT schema ladder vs model track

All rows: `L1_llm_constrained`, `exect_field_family_deterministic_v1`,
`exectv2_fixed_v1:validation` (40 records). Headline: pooled micro F1 (field-family scope
changes with schema — not a single learning curve).

**GPT frozen anchors (`exect_schema_complexity_gpt_validation_v1`)**

| Schema | Families (scope) | micro F1 | Δ vs prior step |
| --- | --- | ---: | ---: |
| exect_s1 | diagnosis, seizure type, medication | **92.3%** | — |
| exect_s2 | + demographics, comorbidities | 80.9% | −11.4 pp |
| exect_s3 | + procedures, investigations | 72.1% | −8.8 pp |
| exect_s4 | + seizure frequency, Rx temporality | 65.5% | −6.6 pp |

**Qwen hold rows (`exect_qwen_replication_validation_v1`, same prompts/policy where noted)**

| Schema | micro F1 | GPT counterpart | Model gap (Qwen − GPT) |
| --- | ---: | ---: | ---: |
| exect_s1 | 79.0% | 92.3% | **−13.3 pp** |
| exect_s2 | 82.6% | 80.9% | **+1.7 pp** |
| exect_s3 | 72.2% | 72.1% | ~0 pp |
| exect_s4 | 67.5% | 65.5% | **+2.0 pp** |

**Separating schema breadth from model capability**

1. **Schema breadth:** Within GPT, each schema step adds field families and drops micro F1
   monotonically. That is primarily **task surface expansion**, not proof that the model
   forgot S1 fields — pooled F1 is not comparable across steps without per-family tables.
2. **Model capability:** Qwen lags GPT sharply at S1 (−13.3 pp) under the same constrained
   extraction stack, then **matches or exceeds** GPT at S2–S3. The crossover suggests
   local-model limits bite hardest on the narrowest audited S1 policy surface, not on the
   full multi-family schemas where replication holds.
3. **Deterministic bridge vs model:** All ladder rows share JSON/Pydantic constraints and
   benchmark policy scaffolding (`L1`). The registry still cannot isolate bridge-only
   causality without a controlled interleaving experiment at fixed schema (e.g. S1 only).

Qwen S4 full-validation hold: `exect_s4_validation_full_qwen35b_ollama` (`…160914Z`, 67.5% micro).
Cap-25 gate row (`…133930Z`, 72.4% micro) remains exploratory only.

### Targeted registry backfill (completed)

Backfilled `headline_metric` (+ decision doc where missing) only for rows that unlock
concrete comparisons:

| experiment_id | Unlocks |
| --- | --- |
| `gan_s0_qwen35b_direct_full_validation_guardrails` | Qwen architecture group vs promoted temporal |
| `gan_s0_qwen35b_*_regression_slice_guardrails` (4 rows) | Hard-slice interleaving matrix |

Skipped: bulk `pending_backfill` on historical cap-25/smoke Gan direct rows (58 rows) that
do not change promote/freeze/hold decisions already recorded in decision docs.

### ReAct H3 probe (complete — reject)

| Item | Value |
| --- | --- |
| Outcome | **reject** (registry row 82) |
| Monthly (valid 7/14) | 42.9% vs direct 71.4% vs B1 100% |
| Schema valid | 50% (7 invalid: partial labels, abstains) |
| Evidence (valid) | 100% |
| Latency | ~93 s/record; ~3.7 tool calls/record (max 4) |
| Tool errors | 6/14 trajectories with `extract_temporal_anchors` arg failure |

## Next Steps

1. **Update kanban** — mark ReAct probe complete; default path remains temporal-candidates.
2. **Optional Qwen H1 full-validation** — matched verify-repair without temporal candidates
   to complete `gan_s0_architecture_qwen_validation_v1` post-deterministic arm (only if
   monthly/evidence decision requires it; slice already shows verify-repair regression).
3. **ExECT S1-only interleaving** — hold schema at `exect_s1`, vary bridge/policy/tool
   timing; do not mix with S2–S4 expansion.
4. **Defer** mass retrospective tagging of exploratory Gan direct history rows.

## Artifact References

- `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`
- `docs/taxonomy/experiment_inventory_for_taxonomy_20260520.md`
- `docs/experiments/synthesis/experiment_registry.json`
- `docs/taxonomy/experiment_taxonomy_schema.md`
- `src/clinical_extraction/experiments/taxonomy.py`
- `src/clinical_extraction/experiments/registry_validation.py`
- `scripts/validate_experiment_taxonomy.py`
- `tests/test_experiment_registry_validation.py`
- `tests/test_experiment_configs.py`
- `configs/experiments/gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails.json`
- `configs/experiments/gan_s0_qwen35b_temporal_candidates_verify_repair_full_validation_guardrails.json`
- `configs/experiments/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json`

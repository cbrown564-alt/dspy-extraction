# DSPy Optimizer Investigation

Date: 2026-05-21  
Status: Research report — informs next experiment design  
Type: Standalone investigation synthesizing code, runs, and prior audits  
Related:

- `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` (practice audit; partially superseded on ExECT compile path)
- `docs/hybrid_component_taxonomy_decision_20260520.md` (hybrid balance classes and intervention matrix)
- `docs/dspy_gepa_react_best_practices_deep_dive.md` (optimizer ladder guidance)
- `docs/exect_s1_optimizer_gpt_cap25_v1_inspection_20260521.md` (latest ExECT optimizer pilot)
- `docs/kanban_plan.md` (active tracker)

## Research Question

Have DSPy optimizers underperformed in this project because integration is wrong, because optimizers are a poor fit for clinical benchmark extraction, or because we have not run the right ablation ladder? What should the project do next?

## Motivation

DSPy is widely described as an optimization framework, not only an orchestration layer. `docs/outline.md` positions DSPy as the layer that orchestrates extraction **and** optimizes prompts, modules, and few-shot policy. In practice, the project converged on manual label-policy engineering, deterministic benchmark bridges, and architecture pivots (verify-repair, temporal-candidates) while optimizer paths were probed and mostly deprioritized.

That pattern raises three risks:

1. **False rejection** — optimizers might help if tested on the right ladder rung, split, and program architecture.
2. **False confidence** — manual prompt ladders may overfit validation without a clean reference axis.
3. **Incomparable experiments** — many historical runs changed multiple factors at once; without a shared baseline ladder, it is hard to interpret whether a new intervention genuinely adds value.

This report records the current optimizer status, interprets historical results, and proposes a **full ablation ladder** anchored in the hybrid component taxonomy so future experiments — optimizers and non-optimizers alike — can be compared against the same reference rungs.

## Method

Reviewed:

- Optimizer code: `src/clinical_extraction/experiments/config.py`, `src/clinical_extraction/programs/gan_frequency_s0.py`, `src/clinical_extraction/programs/exect_s0_s1.py`, `scripts/run_experiment.py`
- Experiment configs: 23 configs with `optimizer` blocks (22 Gan, 1 ExECT bootstrap)
- Run artifacts and metrics for ExECT S1 optimizer pilot (2026-05-21) and Gan optimizer ladder runs (2026-05-18–19)
- Decision and inspection docs listed in Related above
- Taxonomy schema: `docs/experiment_taxonomy_schema.md`, `hybrid_balance_class` definitions in `docs/hybrid_component_taxonomy_decision_20260520.md`
- Tests: `tests/test_gan_s0_program.py`, `tests/test_exect_s0_s1_program.py`, `tests/test_experiment_configs.py`

Comparison frame: DSPy documented optimizer progression (`LabeledFewShot` → `BootstrapFewShot` → `BootstrapRS` → GEPA → MIPRO) against project practice (manual policy + architecture + bounded Gan probes + one ExECT bootstrap pilot).

---

## Executive Verdict

**Mostly yes — optimizers have underperformed relative to the project's best paths, but the picture is more specific than "DSPy optimizers don't work."**

| Finding | Assessment |
| --- | --- |
| Integration wiring | **Sound** — compile paths, metrics, artifacts, and GEPA harness fixes are in place |
| Results vs best manual/architecture paths | **Poor** — bootstrap and GEPA usually lose to frozen prompts, verify-repair, or temporal-candidates |
| Partial successes | **Present** — Gan synthesis `BootstrapFewShot` was a usable hosted baseline; `LabeledFewShot` beats bootstrap on Gan direct cap-25 |
| Root cause | **Design and regime mismatch**, not broken plumbing — wrong failure mode, competing baselines, missing ladder rungs, optimizers never applied to winning multi-step architectures |
| Strategic posture | **Evidence-based deprioritization is justified** — but ablation debt remains, especially the full reference ladder and test-holdout confirmation |

The project has not abandoned DSPy. It has largely stopped treating compile-time search as the default improvement loop on the paths that matter most — often for documented reasons — while manual program engineering outran optimizer ROI on active blockers.

---

## Current Integration Status

### Implemented

| Component | Status |
| --- | --- |
| `OptimizerConfig` | `BootstrapFewShot`, `BootstrapRS`, `LabeledFewShot`, `GEPA` |
| Gan compile | `compile_gan_s0_module`, `compile_gan_s0_module_gepa` in `gan_frequency_s0.py` |
| ExECT compile | `compile_exect_s0_s1_module` in `exect_s0_s1.py` (added 2026-05-21) |
| Runner | `scripts/run_experiment.py` — dev split → compile → eval; writes `compiled_state.json`, `optimizer/summary.json` |
| Optimizer metrics | Dataset-specific; kept separate from benchmark scorers (good discipline) |
| Tests | Compile paths, config validation, artifact layout |

**Supported optimizer metrics:**

| Metric | Dataset / use |
| --- | --- |
| `pragmatic_category` | Gan (legacy) |
| `semantic_frequency_with_evidence` | Gan scalar |
| `semantic_frequency_with_evidence_feedback` | Gan GEPA |
| `synthesis_exact_with_evidence` | Gan synthesis bootstrap |
| `synthesis_exact_with_evidence_feedback` | Gan GEPA |
| `exect_field_family_micro_f1` | ExECT S1 bootstrap |

### Not implemented

| Component | Notes |
| --- | --- |
| MIPRO / MIPROv2 | Mentioned in `gan_frequency_s0.py` docstring only |
| SIMBA | Available in DSPy 3.2.1; never wired |
| GEPA on ExECT | Runner raises `SystemExit` |
| Optimizers on multi-step programs | verify-repair, temporal-candidates, ReAct never compiled |
| ExECT `LabeledFewShot` | Infrastructure exists; no experiment run yet |
| Full reference ladder | D1 and L0 baselines not yet run as a comparison group |

### May 2026 update vs prior audit

`docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` correctly noted that ExECT had no optimizer compile path. That gap was closed on 2026-05-21 with `compile_exect_s0_s1_module` and the ExECT S1 optimizer pilot. The audit's strategic conclusions otherwise remain largely valid.

---

## Historical Results

### ExECT S1 optimizer pilot (cap-25, GPT 4.1-mini, 2026-05-21)

Comparison group: `exect_s1_optimizer_gpt_cap25_v1`. Inspection: `docs/exect_s1_optimizer_gpt_cap25_v1_inspection_20260521.md`.

| Arm | Run ID | Micro F1 | Seizure F1 | Medication F1 | Evidence support | Outcome |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Frozen v4_10 baseline | `exect_s1_optimizer_baseline_cap25_gpt4_1_mini_20260521T000602Z` | **95.8%** | **95.4%** | 94.9% | 97.3% | Hold |
| BootstrapFewShot | `exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini_20260521T000608Z` | 90.7% | 86.2% | 92.9% | 92.9% | **Reject (−5.1pp)** |

Bootstrap compile: 40 dev records, 4 bootstrapped demos, 17.7 s compile, ~119k tokens. Prediction latency ~180× baseline (3.6 s vs 0.02 s per record) due to demo-inflated prompts.

**Critical confound:** the baseline was not zero-shot. It already embeds curated `EXECT_S0_S1_POLICY_EXAMPLES` (~10+ benchmark-facing boundary cases in the signature). Bootstrap stacked four full-document teacher traces on top, including surfaces such as `focal seizures with loss of awareness` that may not match audited gold normalization.

### Gan S0 — few-shot ladder (direct path, cap-25)

Inspection: `docs/gan_s0_few_shot_ladder_cap25_inspection_20260519.md`.

| Optimizer | Norm exact | Monthly | Purist | Compile (s) | Tokens |
| --- | ---: | ---: | ---: | ---: | ---: |
| **LabeledFewShot** | **34.8%** | **43.5%** | **56.5%** | 0.0 | 90k |
| BootstrapFewShot | 21.7% | 34.8% | 39.1% | 17.8 | 141k |
| BootstrapRS | 29.2% | 37.5% | 50.0% | 166.3 | 2.36M |

Demos help; bootstrapping does not on this slice. Search (BootstrapRS) recovers partially but still trails labeled-only at ~26× token cost.

**Program-variant caveat:** these results apply to `gan_frequency_s0_direct_single_pass`. The historical CoT synthesis bootstrap full-validation run remains stronger on labels and should not be conflated with the direct-path ladder.

### Gan S0 — full-validation anchors

| Approach | Run (suffix) | Monthly | Purist | Evidence | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| Synthesis BootstrapFewShot (CoT) | `…065115Z` | 62.9% | 70.1% | 89.9% | Valid DSPy use; historical reference |
| Verify-repair v2 | `…084732Z` | **65.4%** | **72.7%** | **92.7%** | Beat bootstrap |
| Temporal-candidates v1.1 (Qwen) | `…230324Z` | **65.8%** | — | **100%** | Current promoted architecture |

### GEPA — consistently rejected

Decision: `docs/gan_s0_gepa_vs_synthesis_decision_20260519.md`. Follow-up: `docs/gan_s0_semantic_optimizer_cap25_followup_20260519.md`.

| Failure mode | Evidence |
| --- | --- |
| Prompt bloat | 508 words → 1,819 words (Qwen); 3,249 chars on GPT cap-5 |
| Label regression | 51.5% → 40.0% norm exact vs synthesis baseline |
| Non-canonical labels | e.g. `several per week` |
| Under-budget runs | Semantic GEPA: 0 reflection iterations; evidence support 34.8% |
| Qwen viability | ~536 s compile; stress-test only per latency policy |

### Project decisions summary

| Domain | Optimizer tried | Outcome |
| --- | --- | --- |
| Gan direct cap-25 ladder | LabeledFewShot > Bootstrap > BootstrapRS | Do not promote bootstrap/RS on direct path |
| Gan full validation | Synthesis bootstrap vs verify-repair v2 | Verify-repair wins on labels |
| Gan GEPA | cap-5 / Qwen probes | Reject scale-up |
| ExECT S1 cap-25 | BootstrapFewShot vs frozen v4_10 | **Reject** bootstrap |
| Local Qwen | Bootstrap / GEPA / CoT | Avoid for routine work |

---

## Root Cause Analysis

### 1. Optimizing the wrong failure mode

Active blockers are **task decomposition and label-policy boundaries**, not missing few-shot demos:

- Gan: temporal window selection, cluster completeness, seizure-free thresholds
- ExECT: benchmark-facing granularity, diagnosis/seizure leakage, medication temporal status

`BootstrapFewShot` selects demonstrations; it does not decompose tasks. Verify-repair and temporal-candidates address the actual failure modes and win.

### 2. Competing against already-optimized baselines

ExECT v4_10 is the product of ~9 prompt-policy iterations tied to specific error IDs. The bootstrap pilot tested against that — not against a naive zero-shot or L0 program. This invalidates the comparison as a test of "does DSPy optimization help?" and instead tests "does bootstrap beat hand-tuned policy examples?" — a much harder bar.

### 3. Optimizers applied only to single-pass extractors

Winning architectures are multi-module (verify-repair, temporal-candidates). Optimizers were never compiled on these programs. DSPy guidance recommends MIPRO/GEPA when architecture needs multi-step behavior; that class remains untried.

### 4. Trainset and demo quality issues

ExECT trainset construction uses raw gold labels in `make_exect_s0_s1_dspy_examples`, not benchmark-normalized surfaces. The bootstrap config sets `max_labeled_demos: 4`, mixing labeled raw-gold demos with bootstrapped teacher traces. Gan synthesis trainsets are better engineered (priority sorting, locatable evidence filtering).

### 5. Dev-set selection without transfer

ExECT bootstrap: 40 dev records → 4 demos → −5.1 pp on cap-25 validation. Errors overlap familiar GPT failure modes rather than introducing a new promotable mechanism. This mirrors the broader S1 generalization gap (92.3% dev vs 77.8% test on frozen GPT).

### 6. GEPA misconfiguration and under-budget

Semantic GEPA with `max_metric_calls=16` consumed the budget on initial evaluation and ran zero reflection iterations. GEPA requires budget for instruction mutation; several runs effectively tested expensive bootstrap, not instruction search.

### 7. Local model path avoids optimizers by policy

`docs/qwen_dspy_latency_policy.md` excludes CoT + BootstrapFewShot + GEPA from routine Qwen work. Optimizer evidence is therefore concentrated on hosted GPT Gan paths and one ExECT pilot.

### 8. Incomplete optimizer ladder

The project often jumped to `BootstrapFewShot` without establishing:

- D1 deterministic feasibility bound
- L0 bare LLM baseline
- L1 schema-constrained extraction
- LabeledFewShot before bootstrap
- Test-holdout confirmation after dev exploration

---

## Automation thesis (2026-05-21)

**Question:** Can a stripped-back ladder base (L0 or L1) plus DSPy compile match hand-crafted v4_10 policy + inline bridges — a more durable path than manual tuning?

**What we already know:**

- Rungs 0–3 on validation: L0 **60.0%** → L1 **67.7%** → L1+policy **92.3%** full / **95.8%** cap-25 (`docs/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md`).
- Prior bootstrap on **v4_10** (hand-crafted already in prompt) **regressed** to 90.7% cap-25 — that experiment did **not** test automation from a stripped base.

**What to run next:** comparison group `exect_s1_ladder_optimizer_automation_v1` — configs `exect_s1_full_ladder_l0_labeled_cap25`, `l0_bootstrap_cap25` (compile metric `exect_field_family_micro_f1_raw`), `l1_labeled_cap25`. Full prereg: `docs/exect_s1_ladder_optimizer_automation_thesis_20260521.md`.

**Success bar:** cap-25 eval ≥ **93%** micro without v4_10 policy or `repair_policy=none` bridges in the prediction path.

---

## Proposed Full Ablation Ladder

`docs/hybrid_component_taxonomy_decision_20260520.md` defines `hybrid_balance_class` from `D1_deterministic_only` through `L0_llm_only`, `L1_llm_constrained`, and hybrid classes `H1`–`H4`. The optimizer investigation should not be a standalone DSPy ladder disconnected from that taxonomy. Instead, the project needs a **shared reference ladder** that every major experiment can be plotted against.

### Design principles

1. **Bottom rung is non-LLM.** `D1_deterministic_only` establishes feasibility bounds — what deterministic rules, regex, vocabulary lookup, or primitive-only pipelines can extract without any model call. This answers "how much of the task is structurally recoverable?"
2. **Next rung is the purest LLM.** `L0_llm_only` — minimal signature, no embedded policy examples, no normalization instructions, no benchmark bridges in the prediction path. Structured output may remain as the thinnest hard constraint (JSON shape) so outputs are scorable; document this explicitly as the boundary between D1 and L0.
3. **Each rung adds one intervention class.** Do not stack manual policy examples and bootstrap demos on the same rung. One primary varied factor per rung.
4. **Optimizer rungs come after example/policy rungs.** DSPy compile search is meaningless without knowing whether demos or instructions help at all.
5. **Architecture rungs are a parallel axis.** Hybrid classes `H1`–`H4` (post-processing, pre-conditioning, tool-during, deterministic-first adjudication) should be tested at fixed ladder positions — e.g. L1 + verify-repair vs L1 + temporal-candidates — not conflated with optimizer rungs.
6. **Dev first, test to confirm.** Run the full ladder on **development** split for exploration and error analysis. Promote only arms that clear pre-registered gates to **test holdout** for confirmation. Do not tune on test.

### Reference ladder (single dataset / schema / model / scorer)

Use one comparison group per ladder instantiation, e.g. `exect_s1_full_ladder_gpt_dev_v1` or `gan_s0_full_ladder_gpt_dev_v1`.

| Rung | ID | `hybrid_balance_class` | `example_strategy` | Primary addition | Purpose |
| ---: | --- | --- | --- | --- | --- |
| 0 | `D1` | `D1_deterministic_only` | `none` | Primitive-only / rule-only extraction; no LLM | Feasibility bound; scorer sanity |
| 1 | `L0` | `L0_llm_only` | `zero_shot_or_prompt_only` | Bare LLM: extract fields, no policy examples, no norm instructions, no bridges in prediction path | Purest probabilistic baseline |
| 2 | `L1` | `L1_llm_constrained` | `zero_shot_or_prompt_only` | Add JSON schema / Pydantic structured output only | Measure value of output constraints alone |
| 3 | `L1+policy` | `L1_llm_constrained` | `manual_few_shot_or_policy_examples` | Add benchmark label-policy guidance and curated policy examples (current v4_10-style) | Measure hand-authored instruction value |
| 4 | `L1+labeled` | `L1_llm_constrained` | `labeled_few_shot` | `LabeledFewShot` k≤4 from dev trainset; **strip embedded policy examples** | Measure dev gold demos vs policy text |
| 5 | `L1+bootstrap` | `L1_llm_constrained` | `bootstrapped` | `BootstrapFewShot` on dev; strip embedded policy examples | Measure teacher-trace demo selection |
| 6 | `L1+bootstrap_rs` | `L1_llm_constrained` | `optimizer_or_bootstrapped` | `BootstrapFewShotWithRandomSearch` | Measure demo search vs cheap bootstrap |
| 7 | `L1+gepa` | `L1_llm_constrained` | `gepa` | GEPA with feedback metric and adequate budget | Measure instruction mutation |
| 8 | `H1+verify` | `H1_post_deterministic` | varies | verify-repair architecture at best lower rung | Architecture axis |
| 9 | `H4+temporal` | `H4_deterministic_first_llm_adjudicates` | varies | temporal-candidates (Gan) or equivalent (ExECT) | Architecture axis |

**MIPRO (`mipro`)** adds as rung 7b or replaces GEPA when the program variant is genuinely multi-step (verify-repair, ReAct). Do not run MIPRO on single-pass L1 until lower rungs are complete.

### Taxonomy tags for ladder runs

Every ladder config must include:

```text
comparison_group: <dataset>_<schema>_full_ladder_<model>_dev_v1
varied_factor: ladder_rung  (or hybrid_balance_class where rung ID is insufficient)
fixed_controls: dataset, schema, scorer, model, split, bridge_policy_explicit
run_scope: development  (then test_holdout for confirmed arms only)
```

Record `knowledge_sources`, `interleaving_positions`, and `normalization_strategy` per rung so historical experiments (temporal-candidates, v4_10 policy, interleaving probes) can be positioned on the same axis retroactively.

### Why this helps compare other experiments

Many existing runs bundled multiple factors — e.g. v4_10 policy + inline bridges + embedded examples + GPT 4.1-mini on validation. Without rungs 0–3, it is unclear whether gains came from the LLM, the policy text, the bridges, or validation tuning. The ladder provides:

- A **shared y-axis** for plotting any new intervention ("+3.2 pp over L0, −1.1 pp vs L1+policy")
- A **sanity check** for overfitting (large dev gains that collapse on test)
- A **decision rule** for optimizers: only invest in rungs 5–7 if rung 4 shows demo sensitivity on dev **and** rung 3 is beaten by more than noise

### Implementation prerequisites

Before running the ladder:

1. **L0 prompt variant** — new `prompt_version` or program flag that strips `EXECT_S0_S1_POLICY_EXAMPLES` / `GAN_FREQUENCY_SYNTHESIS_GUIDANCE` and benchmark-bridge application from the prediction path (bridges may remain in scorer for eval-only comparison if explicitly tagged `eval_only`).
2. **D1 arm** — compose existing typed primitives for the target schema; no model config. Tag `D1_deterministic_only`, `eval_only` normalization if scorer bridges are applied only at score time.
3. **Ladder compile hygiene** — when running rungs 4–6, disable embedded policy examples in the signature so optimizers are not stacked on hand-tuned demos.
4. **ExECT labeled demo normalization** — consider benchmark-normalized gold in trainset examples, or document that labeled demos use raw gold and interpret rung 4 accordingly.
5. **Registry rows** — add one row per rung under a shared `comparison_group` in `docs/experiment_registry.json`.

---

## Dev-Then-Test Protocol

### Phase A — Development ladder (primary exploration)

| Control | Value |
| --- | --- |
| Split | `exectv2_fixed_v1:development` or `gan_2026_fixed_v1:development` |
| Scope | Full dev split, or capped slice (e.g. cap-50) for expensive rungs (GEPA, BootstrapRS) |
| Model | GPT 4.1-mini (default exploration track) |
| Scorer | Unchanged benchmark-facing scorer |
| Gates | Pre-register per rung: minimum delta vs previous rung, schema validity, evidence non-regression |

**Order:** rungs 0 → 3 sequentially before expensive optimizers. Skip rung 5+ if rung 4 does not beat rung 2 by a pre-registered margin (e.g. ≥ 2 pp on primary metric).

**Artifacts:** standard run layout plus `compiled_state.json` for optimizer rungs. Write inspection doc after each rung batch.

### Phase B — Validation cap (optional intermediate)

For arms that beat the prior rung on dev, run a **fixed cap-25 validation slice** using the same record cap as other factor-isolation groups. This matches current Lane A practice and allows comparison to existing cap-25 anchors (e.g. v4_10 95.8% micro).

Do not treat validation cap as the final promotion gate if the arm was selected after any validation-visible error analysis.

### Phase C — Test holdout (confirmation only)

| Control | Value |
| --- | --- |
| Split | test holdout (`report_on_test_split: true` where policy allows) |
| Arms | Only rungs that cleared dev + cap gates |
| Tuning | **Forbidden** — no prompt, demo, or bridge changes based on test results |
| Purpose | Confirm generalization; compare to frozen test anchors (e.g. ExECT S1 GPT test `…222615Z` at 77.8% micro) |

Qwen confirmation remains a separate track per `docs/kanban_plan.md`: port only dev+test-confirmed arms.

---

## Integration Assessment

### What is correct

- Optimizer dispatch in `run_experiment.py` loads dev records, compiles, writes artifacts
- Optimizer metrics separated from benchmark scorers
- GEPA harness fixes (reflection LM, cloudpickle, single budget control)
- Verify-repair compile pattern for Gan (LabeledFewShot on extractor only)
- ExECT compile path follows Gan patterns; pilot was reproducible

### What should change for the ladder

| Issue | Recommendation |
| --- | --- |
| Bootstrap tested vs embedded policy examples | Strip embedded examples on optimizer rungs |
| Raw gold in ExECT labeled demos | Normalize or document; prefer bridge-aligned train labels for rung 4 |
| No L0 / D1 configs | Add prompt variant and D1 primitive arm templates |
| GEPA under-budget | Pre-register `max_metric_calls` ≥ 50 or use `auto: light`; block promotion if zero reflection iterations |
| MIPRO absent | Implement only after rung 6 on dev; prioritize multi-step variants |
| Audit doc stale on ExECT | Cross-link this report; note ExECT compile path landed 2026-05-21 |

---

## Recommendations

### Do not resume by default

- Scaling GEPA or semantic bootstrap on Gan without ladder context
- BootstrapFewShot on ExECT against v4_10 embedded examples without L0/L1 ablation
- Bootstrap / GEPA on Qwen routine paths (latency policy stands)
- Optimizer tuning of benchmark bridges (belongs in deterministic code)
- Validation re-tuning of frozen hosted threads

### Do next (ordered)

1. **Preregister the full ladder** for ExECT S1 on GPT dev — comparison group, rung definitions, gates, and inspection template. Gan S0 ladder can follow the same template.
2. **Implement L0 prompt variant** and D1 primitive arm for ExECT S1 (and Gan S0 if not already available as diagnostic fixtures).
3. **Run rungs 0–3 on dev** before any optimizer compile. This establishes the reference axis.
4. **Run rungs 4–6 on dev** only if rung 3 beats rung 1 by a meaningful margin.
5. **GEPA (rung 7) on dev** only with feedback metric, adequate budget, and instruction-length guardrail.
6. **Cap-25 validation** for arms that clear dev gates; compare to existing factor-isolation anchors.
7. **Test holdout** for at most 1–2 arms that clear cap gates — confirm generalization, not explore.

### Policy restatement

1. **DSPy orchestration** remains the default framework (signatures, modules, artifacts).
2. **DSPy optimization** is a **bounded probe** on the reference ladder, not the default improvement loop.
3. **Program architecture** (verify-repair, temporal-candidates) counts as a valid DSPy-style win even without teleprompters.
4. **Promotion metrics** stay benchmark-facing scorers; optimizer metrics never replace them.
5. **Every major experiment** should declare its ladder rung so results remain comparable.

---

## Limitations

- This report is based on configs, code, and documented runs through 2026-05-21; no re-runs were executed for this writeup.
- Cap-25 slices are useful for fast comparison but can disagree with full validation (documented for ExECT S4 and Gan).
- MIPRO/SIMBA absence is a documented gap, not evidence they would fail.
- D1 rung feasibility depends on primitive coverage per schema; some ExECT field families may have no meaningful D1 extractor yet.
- L0 definition requires an explicit choice about minimal JSON schema constraint vs truly unstructured output; the ladder should fix this once per schema and hold it constant.

---

## Artifact References

### Code

- `src/clinical_extraction/experiments/config.py` — `OptimizerConfig`
- `src/clinical_extraction/programs/gan_frequency_s0.py` — `compile_gan_s0_module`, `compile_gan_s0_module_gepa`
- `src/clinical_extraction/programs/exect_s0_s1.py` — `compile_exect_s0_s1_module`, `make_exect_s0_s1_dspy_examples`
- `scripts/run_experiment.py` — optimizer dispatch

### Configs

- `configs/experiments/exect_s1_optimizer_baseline_cap25_gpt4_1_mini.json`
- `configs/experiments/exect_s1_optimizer_bootstrap_cap25_gpt4_1_mini.json`
- `configs/experiments/gan_s0_ladder_*_cap25_gpt4_1_mini.json`
- `configs/experiments/gan_s0_gepa_direct_cap5_gpt4_1_mini.json`

### Key runs

| Track | Run ID suffix | Headline |
| --- | --- | --- |
| ExECT bootstrap reject | `…000608Z` | 90.7% micro (−5.1 pp vs baseline) |
| ExECT optimizer baseline | `…000602Z` | 95.8% micro |
| Gan synthesis bootstrap full | `…065115Z` | 62.9% monthly |
| Gan verify-repair v2 full | `…084732Z` | 65.4% monthly |
| Gan temporal v1.1 Qwen full | `…230324Z` | 65.8% monthly |
| ExECT S1 GPT test holdout | `…222615Z` | 77.8% micro |

### Prior docs superseded or extended

| Doc | Relationship |
| --- | --- |
| `docs/dspy_optimizer_vs_manual_engineering_audit_20260520.md` | Extended; ExECT compile gap closed |
| `docs/hybrid_component_taxonomy_decision_20260520.md` | Ladder rungs instantiate `hybrid_balance_class` |
| `docs/dspy_gepa_react_best_practices_deep_dive.md` | Optimizer ordering guidance aligned with rungs 4–7 |

---

## Next Steps

See `docs/kanban_plan.md` for tracker updates. Immediate engineering pulls:

1. Add preregistration doc: `docs/exect_s1_full_ladder_gpt_dev_v1_preregistration.md` (or equivalent).
2. Implement L0 prompt variant and D1 diagnostic arm for ExECT S1.
3. Backfill ladder comparison group stub rows in `docs/experiment_registry.json`.
4. Run rungs 0–3 on dev before further optimizer probes.

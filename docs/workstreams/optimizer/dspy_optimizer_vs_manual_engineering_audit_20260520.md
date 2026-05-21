# DSPy Optimizer vs Manual Engineering Audit

Date: 2026-05-20  
Audit type: practice review against DSPy optimization norms and `docs/outline.md`  
Active tracker: `docs/planning/kanban_plan.md`  
Related: `docs/workstreams/optimizer/dspy_gepa_react_best_practices_deep_dive.md`, `docs/policies/qwen_dspy_latency_policy.md`, `docs/experiments/gan/gan_s0_temporal_candidate_pivot_20260519.md`, `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md`, `docs/planning/research_drift_audit_20260520.md`

## Research Question

Given rapid experimentation on Gan S0 and the hosted GPT ExECT schema ladder, have we veered away from DSPy best practices? Should we be using DSPy optimizers more — and if not, what did manual engineering buy or cost us relative to the overall research goals?

## Motivation

`docs/outline.md` positions DSPy as the layer that orchestrates extraction **and** optimizes prompts, modules, and few-shot policy. The project has invested heavily in manual label-policy ladders, deterministic benchmark bridges, and architecture pivots (verify-repair, temporal-candidates, bounded ReAct). Optimizer paths (BootstrapFewShot, LabeledFewShot, GEPA, BootstrapRS) were explored on Gan and mostly deprioritized. ExECT never received an optimizer compile path.

This audit records what was tweaked manually vs left to optimizers, the consequences, and a stepped-back view on research alignment — so future work does not confuse “DSPy orchestration” with “DSPy optimization already explored.”

## Method

Reviewed:

- `docs/planning/kanban_plan.md`, `docs/planning/kanban_frozen_threads_history.md`, `docs/outline.md`
- Experiment configs under `configs/experiments/` (91 total; 22 with `optimizer` blocks — all Gan)
- `scripts/run_experiment.py` optimizer wiring (Gan-only gate)
- Program modules: `gan_frequency_s0.py`, `exect_s0_s1.py`, `exect_s2.py`, `exect_s3.py`, `exect_s4.py`
- Optimizer decision docs and pivot notes (May 18–20)
- Qwen replication plan and latency policy

Comparison frame: DSPy documented optimizer ladder (`LabeledFewShot` → `BootstrapFewShot` → search/GEPA/MIPRO) vs project practice (manual policy + architecture + bounded Gan optimizer probes).

## Executive Verdict

**We have not abandoned DSPy; we have largely stopped using DSPy optimization on the paths that matter most — often for good reasons.**

| Layer | Practice | Assessment |
| --- | --- | --- |
| Signatures, modules, structured output | Strong | Aligned with DSPy “programs not prompts” |
| Run artifacts, scorer separation | Strong | Optimizer metrics kept distinct from benchmark scorers |
| Teleprompter / compile loops | Weak on ExECT; probed then deprioritized on Gan | Biggest gap vs outline and vs DSPy tutorials |
| Architecture search | Manual ablations (section-aware, verify-repair, temporal-candidates) | Spirit of DSPy; not optimizer-driven |
| MIPRO / multi-step compile | Never implemented | Mentioned in code comment only |

The project converged on **manual label-policy engineering + deterministic bridges + program architecture pivots** rather than compile-time search. That is defensible clinical-research engineering, not accidental neglect — but it leaves ablation debt (especially on ExECT) and generalization uncertainty (S1 dev vs test gap).

---

## What DSPy Best Practice Would Look Like Here

| DSPy norm | Project practice |
| --- | --- |
| Define `Signature` + `Module`, compile with optimizer | Signatures/modules: yes. Compile: **Gan only** |
| Optimizer ladder from simple demos to search/GEPA/MIPRO | Ladder tested on Gan; **never on ExECT** |
| Let optimizer find instructions and demonstrations | ExECT: human `*_LABEL_POLICY_GUIDANCE` + versioned bridges |
| Keep benchmark metric separate from optimizer metric | **Consistently enforced** |
| Architecture ablations at fixed compile state | Architecture tested; not at fixed optimizer state |
| MIPRO for multi-step / tool programs | **Not implemented** |

Hard constraint in the runner:

```python
# scripts/run_experiment.py — optimizer gate
if config.optimizer is not None:
    if config.dataset != "gan_2026":
        raise SystemExit("Only Gan S0 experiments currently support DSPy optimization.")
```

ExECT — the harder, broader task — has **zero optimizer infrastructure** despite being where prompt and bridge complexity grew fastest.

---

## Stage-by-Stage: Manual vs Optimizer

### 1. Gan S0 (narrow frequency task)

#### Left to optimizers (hosted GPT, early arc)

- `BootstrapFewShot` + `synthesis_exact_with_evidence` → full-validation reference (`…065115Z`: 62.9% monthly, 89.9% evidence)
- Ladder: `LabeledFewShot`, `BootstrapFewShot`, `BootstrapRS`, semantic metrics, GEPA (~22 optimizer configs)
- Human-curated `GAN_FREQUENCY_SYNTHESIS_GUIDANCE` fed into synthesis trainset **before** bootstrap — hybrid pattern

#### Manually engineered instead

- Direct-path guardrails, canonical label policy, deterministic surface repair
- Verify-repair v2 (second DSPy module) — `…084732Z`: 65.4% monthly, beat synthesis bootstrap on labels
- Temporal-candidates v1.1 (task decomposition) — Tier 1 `…230324Z`: 65.8% monthly, 100% evidence on Qwen

#### Optimizer outcomes

| Path | Result | Consequence |
| --- | --- | --- |
| Synthesis BootstrapFewShot | Strong hosted baseline | Valid DSPy use; demos helped format/evidence |
| GEPA | Prompt bloat (508→1,819 words on Qwen), label regression | Correctly deprioritized — see `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md` |
| Semantic BootstrapFewShot / semantic GEPA | Failed cap-25 vs verify-repair v2 | Pivot to architecture |
| LabeledFewShot on Qwen | 0/4 infrequent quantified cases | Demos ≠ temporal aggregation |
| Qwen GEPA | ~536s compile, non-canonical labels | Local optimizer path not viable for routine work |

**Interpretation:** Optimizers were run where DSPy recommends them. Evidence showed the blocker was **task decomposition** (temporal window selection), not missing few-shot demos. Verify-repair and temporal-candidates are DSPy-*aligned* in spirit (change the program, not the paragraph).

**Gap:** Optimizers were applied to **single-pass extractors only**. No GEPA/MIPRO compile on multi-module verify-repair or temporal-candidates programs.

---

### 2. ExECT S0–S4 (broad schema ladder)

#### Left to optimizers

Nothing. No `optimizer` block in any ExECT config. Qwen replication explicitly skips optimizers per `docs/policies/qwen_dspy_latency_policy.md` and `docs/experiments/exect/exect_qwen35b_ladder_replication_plan.md`.

#### Manually engineered (entire winning arc)

- **S1:** v3 → v4.10 label-policy ladder (~9 documented versions), tied to error IDs (EA0188, EA0150, …)
- **S2–S4:** v1.0 → v1.3 / v1.2 with family-specific guidance and `s4_bridge:*` / `benchmark_bridge:*` normalizers in program code
- Embedded policy examples in signatures (not bootstrapped demos)
- Section-aware ablation: **negative** (−8.1pp micro F1 cap-25) — closed

#### Consequences

| Benefit | Cost |
| --- | --- |
| Fast hosted GPT iteration on 40-record validation | **Validation overfitting risk** — S1 dev 92.3% vs test 77.8% (−14.5pp) |
| Auditable named bridges with quality flags | Bridges encode scorer quirks; may not transfer (Qwen S1 full 79.0% vs GPT 92.3%) |
| Frozen prompts enable Qwen replication track | Cannot answer outline ablation: “does few-shot help each field?” on ExECT |
| Clear freeze discipline (Threads B–E) | Prompt version metadata under-represents full program state (prompt + bridges + examples) |

**Interpretation:** ExECT was optimized like a **benchmark-reproduction engineering sprint**, not a DSPy compile loop. For policy-heavy clinical gold, that was often correct — optimizers should not silently learn “collapse to `secondary` under specificity-collapse context.” But the hardest task never got a fair optimizer baseline.

---

### 3. Qwen3.6:35b track

Per `docs/policies/qwen_dspy_latency_policy.md`:

- Routine runs: direct structured extraction, no CoT, no BootstrapFewShot, no GEPA
- Optimizers only as explicit overnight stress tests

**Observed:**

- Qwen S2 full **beat** frozen GPT S2 (+1.7pp micro F1) with zero optimization
- Qwen S1 full **lost** to GPT (−13.3pp) — manual GPT policy may be GPT-shaped

Local-model thesis is tested on **distilled hosted programs**, not DSPy-compiled local artifacts.

---

## Consequences Summary

### What manual tweaking bought

1. **Speed** — ExECT v4.x ladder in days, not compile sweeps
2. **Auditability** — bridges carry flags; GEPA instructions do not
3. **Scorer integrity** — rejected optimizer drift into non-canonical labels
4. **Documented negative results** — section-aware, GEPA bloat, semantic bootstrap

### What manual tweaking cost

1. **Generalization uncertainty** — S1 test holdout gap; repeated cap-25 optimism (e.g. S4 v1.2: 69.2% cap-25 vs 65.5% full)
2. **Optimizer infrastructure debt** — no ExECT compile path; MIPRO never built
3. **Incomplete ablation matrix** — outline Goal 3 (few-shot, verifier, sectioning) partially answered manually, not systematically
4. **Asymmetric learning** — Gan got the optimizer lab; ExECT got the hand-tuning lab

### Ironic parallel

GEPA’s failure mode (prompt bloat, label drift) mirrors ExECT’s success mode (incremental prompt growth + targeted bridges). Optimizer bloat was rejected; human bloat was accepted because it is traceable. That is research-integrity-friendly but not DSPy orthodoxy.

---

## Alignment with Research Goals (`docs/outline.md`)

| Goal | Optimizer-heavy path? | Project path | Assessment |
| --- | --- | --- | --- |
| Beat ExECTv2 / Gan benchmarks | Optimizers might help | Manual policy + partial families; Gan ~65.8% monthly | **Goal 1 open** — data/scorer scope matters more than missing optimizers |
| Modular specialization (Gan vs ExECT) | Shared compile pipeline | Different programs and optimization strategies | **Aligned** |
| Comprehensive ablations | Optimizer sweeps | Manual Gan ablations; ExECT incomplete | **Partially aligned** |
| Best deterministic + LLM mix | Rules + compiled LLM | Heavy deterministic bridges on ExECT | **Aligned**; watch bridge overfitting |
| Local vs closed models | Compile on hosted, transfer | Freeze hosted → replicate on Qwen | **Pragmatic** |

May 20 drift audit verdict still holds: project shifted from **optimize** to **freeze + replicate**. That shift reflects evidence that **manual program engineering outran optimizer ROI** on the active blockers.

---

## Recommendations

### Do not resume by default

- Scaling GEPA or semantic BootstrapFewShot on Gan (negative evidence documented)
- BootstrapFewShot / GEPA on Qwen3.6:35b routine paths (latency policy stands)
- Optimizer-tuning of ExECT benchmark bridges (belongs in deterministic code)
- Validation re-tuning on frozen hosted GPT threads

### Worth doing narrowly (see Kanban cards)

| Task | Rationale | Guardrails |
| --- | --- | --- |
| Wire ExECT optimizer compile path | Close infrastructure gap; enable one fair baseline | Hosted GPT only; `LabeledFewShot` k≤4; fixed frozen bridges |
| ExECT S1 LabeledFewShot vs zero-shot on **test holdout** | Answer outline few-shot ablation once | No validation tuning; compare to frozen v4.10 zero-shot test run |
| Gan ReAct MIPRO capped probe (hosted) | Only untried optimizer class for multi-step programs | After ReAct slice pass; cap-25; compare to uncompiled ReAct |
| Architecture ablation + optional compile | Phase 5 — monolithic vs verify-repair **with/without** cheap compile | Deferred until Gan port + Qwen S4 reads clear |

### Policy restatement

1. **DSPy orchestration** remains the default framework (signatures, modules, artifacts).
2. **DSPy optimization** is a **bounded probe**, not the default improvement loop, unless failure mode matches demo/instruction search (format, evidence) rather than task decomposition (temporal aggregation, label-policy collapse).
3. **Program changes** (verify-repair, temporal-candidates, ReAct tools) count as DSPy-best-practice wins even without teleprompters.
4. **Promotion metrics** stay benchmark-facing scorers; optimizer metrics never replace them.

---

## Artifact References

### Config / code

- Optimizer configs: `configs/experiments/gan_s0_*` (22 with `optimizer` block)
- Frozen ExECT configs: `exect_s0_s1_validation_full_gpt4_1_mini.json`, `exect_s2_validation_full_gpt4_1_mini.json`, etc. (no optimizer)
- Compile helpers: `src/clinical_extraction/programs/gan_frequency_s0.py` (`compile_gan_s0_module`, `compile_gan_s0_module_gepa`)
- Runner gate: `scripts/run_experiment.py`

### Key decision docs

- `docs/experiments/gan/gan_s0_gepa_vs_synthesis_decision_20260519.md`
- `docs/experiments/gan/gan_s0_temporal_candidate_pivot_20260519.md`
- `docs/experiments/gan/gan_s0_semantic_optimizer_cap25_followup_20260519.md`
- `docs/experiments/exect/exect_section_aware_cap25_inspection.md`
- `docs/experiments/exect/exect_s0_label_policy_v4_10_implementation.md`

### Anchor runs

| Track | Run | Headline |
| --- | --- | --- |
| Gan synthesis bootstrap (GPT) | `…065115Z` | 62.9% monthly |
| Gan verify-repair v2 (GPT) | `…084732Z` | 65.4% monthly |
| Gan temporal v1.1 (Qwen) | `…230324Z` | 65.8% monthly |
| ExECT S1 v4.10 dev (GPT) | `…221944Z` | 92.3% micro F1 |
| ExECT S1 v4.10 test (GPT) | `…222615Z` | 77.8% micro F1 |
| ExECT S1 full (Qwen) | `…042117Z` | 79.0% micro F1 |

---

## Limitations

- Audit based on configs, code, and documented runs as of 2026-05-20; no re-runs.
- Did not line-audit every `benchmark_bridge` for necessity vs overfit.
- MIPRO/SIMBA not evaluated — absence is a documented gap, not evidence they would fail.

## Next Steps

See Kanban cards added under Backlog / Ready in `docs/planning/kanban_plan.md` (2026-05-20 refresh):

1. Wire minimal ExECT compile path in `run_experiment.py`
2. ExECT S1 hosted LabeledFewShot test-holdout baseline
3. Gan ReAct MIPRO capped probe (hosted, after slice gate)
4. Extend architecture ablation design to include optional cheap compile factor

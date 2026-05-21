# Where Deterministic Clinical Knowledge Should Enter the DSPy Pipeline

Date: 2026-05-21  
Status: **Historical snapshot** — superseded for research doctrine by `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`  
Type: Research report (bets and artifacts as of 2026-05-21; **not** mechanism closure)  
Related:

- **Taxonomy north star:** `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`
- **Taxonomy implementation:** `docs/taxonomy/experiment_taxonomy_schema.md`, `docs/experiments/synthesis/experiment_registry.json`, `docs/taxonomy/experiment_taxonomy_research_synthesis_20260520.md`
- **Operating plan:** `docs/planning/kanban_plan.md`
- **Registry views:** `docs/research_atlas/evidence_matrix.md`
- **Closed ExECT probes:** `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md`
- **Latest measurements:** `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md`, `docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md`, `docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md`, `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`

---

## Research Question

**Where should deterministic clinical knowledge enter a DSPy extraction pipeline, and how does the answer differ by dataset, schema breadth, clinical task family, and model track?**

The project frames this through the hybrid component taxonomy (`L0`–`L1`, `H1`–`H4`, `D1`) and **interleaving positions** (`pre`, `during`, `tool_during`, `post`, `eval_only`). Implementation labels (`v4_10`, `temporal_candidates`, `ExECT S4`) are artifact IDs; the scientific variable is **allocation of responsibility** between deterministic code and the LLM, and **where** that responsibility is exercised.

---

## Motivation

Performance gains in this repo often came from moving *where* structure enters the pipeline, not from swapping models alone. Without a shared synthesis, recent work can feel like drift: Kanban cards name factor-isolation groups, optimizer ladders, and Qwen seizure ports, while the taxonomy decision doc still reads like a forward-looking standard.

This report states what the project **currently believes**, what it has **ruled out**, the **rationales**, what is **actively testing**, and what we **expect next** — all mapped to `hybrid_balance_class` and interleaving position.

---

## Document Map (Where To Look)

| Layer | Role | Primary docs |
| --- | --- | --- |
| **North star / ontology** | Defines `L0`–`D1`, intervention matrix, registry fields | `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`, `docs/taxonomy/experiment_taxonomy_schema.md` |
| **Evidence index** | Registry rows, comparison groups, outcomes | `docs/experiments/synthesis/experiment_registry.json`, `docs/experiments/synthesis/experiment_registry_matrix_20260520.md` |
| **First taxonomy answers** | Registry-backed answers to taxonomy “near-term questions” (2026-05-20) | `docs/taxonomy/experiment_taxonomy_research_synthesis_20260520.md` |
| **Execution tracker** | What ran, gates, next pull | `docs/planning/kanban_plan.md` |
| **Closed mechanisms** | ExECT probes that should not repeat | `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md` |
| **Decomposition (ExECT S1)** | How much each rung contributes | `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md` |
| **Single-factor isolation** | Prompt / verification / evidence on fixed arms | `docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md`, `docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md` |
| **Compile-time search** | Optimizer role vs manual engineering | `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md` |

**Perceived drift:** execution docs grew faster than a single taxonomy-facing narrative. The science did not abandon the hybrid question; it **operationalized** it (registry, preregistrations, clean comparison groups, reference ladder). This synthesis closes that gap as of 2026-05-21.

---

## Method

Evidence drawn from:

- Promoted/frozen/reject/hold registry outcomes and inspection docs cited above
- Cap-25 and full-validation runs on `exectv2_fixed_v1:validation` and `gan_2026_fixed_v1:validation`
- Scorer modes: `exect_field_family_deterministic_v1`, `gan_frequency_deterministic_v1`
- Models: GPT 4.1-mini (exploration default), Qwen3.5 35B Ollama (confirmatory / local track)

**Caveat (always):** ExECT numbers here are **local field-family diagnostics**, not published ExECTv2 Table 1 reproduction (blocked on CUI-aware all-family scoring). Gan numbers are **fixed synthetic validation**, not Real(300)/Real(150) (data access blocked). Post-hoc **benchmark bridges** can raise measured F1 without improving clinical validity; the registry’s `normalization_strategy` and `control_modes` fields exist to keep that visible.

---

## Results — Answers by Taxonomy Class

### Summary table (current working conclusions)

| Hybrid class | Interleaving (typical) | Gan S0 frequency | ExECT S1 (3-family) | ExECT S2–S4 |
| --- | --- | --- | --- | --- |
| **D1** deterministic only | `pre` / `post` | Not production path | Feasibility floor ~58% micro (cap-25) | Not explored as ceiling |
| **L0** LLM only | `during` | — | +1.6pp vs D1; rich labels hurt diagnosis | Dominated by schema breadth |
| **L1** LLM + schema | `during` + hard constraint | Direct / synthesis baselines superseded | +7.7pp vs L0; still far below production | Frozen ladder: micro falls 92→81→72→66% (GPT) |
| **H1** post-deterministic | `post` | Verify-repair **superseded** on GPT; S1 verify-repair **reject** (−9.4pp cap-25) | Bridges **explain** scores; interleaving H1 = diagnostic not new intervention | MT post-classifier **reject** (recall collapse) |
| **H2** pre-deterministic | `pre` | Section-aware **reject**; pre-vocab on ExECT **reject** | Medication/seizure H2 slices **reject** | S4 frequency H2 **reject** |
| **H3** tool during | `tool_during` | ReAct temporal tools **reject** (schema/evidence collapse) | Deferred (no H1/H2 signal) | — |
| **H4** pre + LLM adjudicates | `pre` + `during` + `post` | **Promoted** temporal-candidates + verify-repair | Production path is L1 + policy + **inline bridges** (not isolated H4 row) | — |
| **Optimizer / examples** | `during` (demos) | LabeledFewShot > Bootstrap on direct; GEPA **reject** | Bootstrap **reject** (−5.1pp); ladder rungs 4–7 **ready** | Not on winning architectures |

---

### D1 — deterministic only

**What we know:** On ExECT S1 cap-25, substring note-anchoring without LLM or benchmark bridges yields **58.4% micro F1** with high recall (~74%) and low precision (~48%) — many token-level false positives (`focal`, `secondary`, `epilepsy` fragments).

**Rationale:** Establishes a feasibility bound; deterministic matching alone is not a credible extraction ceiling for benchmark-facing S1.

**Ruled out:** Treating D1 as a target architecture for S1.

**Artifact:** `exect_s1_full_ladder_d1_cap25_gpt4_1_mini_20260521T003704Z` — `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md`

---

### L0 / L1 — LLM extraction with minimal vs schema constraint

**What we know (ExECT S1 ladder):**

| Rung | Micro F1 (cap-25 unless noted) | Δ vs prior |
| --- | ---: | ---: |
| L0 bare LLM | 60.0% | +1.6pp vs D1 |
| L1 schema-only | 67.7% | +7.7pp vs L0 |
| L1 + v4_10 policy + inline bridges (full 40) | **92.3%** | +24.6pp vs L1 cap-25* |

\*L1+policy on full validation; matches frozen GPT S1 anchor.

**Interpretation:** Under the current scorer, **most of the scored S1 gap** between “bare LLM” and “production” is **not** JSON schema alone (~8pp from L0→L1). The step to **92.3%** is dominated by **benchmark label policy during extraction plus inline post bridges** (`H1`/`during`/`post`, soft hint + posthoc correction on diagnosis, seizure_type, medication).

**Ruled out:** Claiming ExECT S1 success is “just the model” or “just schema.”

**Still uncertain:** Clean separation of **prompt policy** vs **bridge code** as causal drivers — historical runs bundled them; the full ladder partially decomposes rungs 0–3 but L1+policy still combines policy + bridges.

---

### H4 + H2 — deterministic preconditioning, LLM adjudication (Gan promoted path)

**What we know:**

| System | Model | Monthly freq. | Evidence support | Outcome |
| --- | --- | ---: | ---: | --- |
| Temporal-candidates + verify-repair | GPT 4.1-mini | 65.1% | 100% | **Promote** |
| Same architecture | Qwen35b | 65.8% | 100% | **Promote** |
| Verify-repair only (H1) | GPT | 65.4% (full) | 92.7% | **Superseded** |

**Rationale:** For **Gan seizure frequency**, temporal structure is the bottleneck. Precomputed candidates (`H2`, `pre`) plus LLM selection/verification (`H4`, `during`/`post`) improve **robustness, category tiers (Purist/Pragmatic), evidence support, and schema validity** more than a simple monthly-accuracy win over H1 on GPT. The promoted decision is an **architecture** claim, not a prompt tweak.

**Ruled out:**

- **H3** ReAct temporal tools on Gan: ~50% schema validity, ~43% monthly on valid preds (`H3_interleaved_tool_hybrid`, `tool_during`) — tool-during does not replace preconditioning.
- **H2** section-aware context on ExECT S0/S1 cap-25 (prior probes).

**Active / expected:** Gan Lane A verification cap-25 was **null** (44% monthly all arms) — does not overturn promotion but says **verification strategy alone** is not the driver on that slice; architecture + preconditioning remains the story.

---

### H1 — post-deterministic (bridges, verify-repair, classifiers)

**What we know — ExECT S1:**

- **Inline benchmark bridges** are load-bearing: bridge-free L1 raw **68.6%** full micro vs **92.3%** with bridges (~24pp), measured in interleaving v2 (`docs/experiments/exect/exect_s1_interleaving_gpt_validation_v2_inspection_20260520.md`).
- **S1 post-bridge H1 as a new intervention:** **Reject** — reproduces production path; diagnostic only (`docs/experiments/exect/exect_negative_probe_synthesis_20260520.md`).
- **Second-pass verify-repair on S1 (cap-25):** **Reject** — 86.4% vs 95.8% single-pass micro (−9.4pp) (`docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md`).

**What we know — ExECT S4:**

- Medication-temporality **post** classifier: precision +10.1pp, F1 −6.6pp (recall collapse) — **reject** broad abstention (`docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md`).

**Rationale:** Post-hoc deterministic layers help when they **align** to benchmark policy without destroying recall. Generic verify-repair and broad post-filters hurt S1/S4 under current policies.

**Ruled out:** Default S1 verify-repair; broad S4 MT post-classifier; treating interleaving H1 arms as new product features.

---

### H2 — pre-deterministic (candidates, vocab, pre-candidates)

**What we know:** Family-isolated **pre** injection **rejected** on:

- S1 medication slice (−3.2pp medication F1)
- S1 seizure_type slice (−8.2pp)
- S4 seizure_frequency cap-25 (−2.0pp)

**Rationale:** Static candidate lists anchor the model to coarse or unsupported surfaces; they do not substitute for benchmark label policy + bridges on ExECT. Gan is different: **temporal** pre-candidates match the task’s structural bottleneck.

**Ruled out (default):** Broad/static H2 pre-vocab on ExECT S1/S4 in tested shapes.

**Still plausible (preregistered only):** Redesigned frequency presentation or narrowed MT fallback (dose-only ASM), not repeat of catalog arm shapes.

---

### H3 — tool during reasoning

**What we know:** Gan ReAct temporal tools **reject** as default vs precomputed candidates.

**Rationale:** Same knowledge source, different **interleaving position** → different outcome. Failure of H3 does not invalidate H2/H4 on Gan.

**Ruled out:** Tool-during as default Gan path; S1 H3 deferred after null H1/H2 interleaving signal.

---

### Example / optimizer strategy (`during`, bootstrapped demos)

**What we know:**

| Context | Result |
| --- | --- |
| Gan GEPA | **Reject** (bloat, regression) |
| Gan cap-25 ladder | LabeledFewShot > Bootstrap > BootstrapRS on **direct** architecture |
| ExECT S1 bootstrap vs paired baseline | **Reject** −5.1pp micro, −9.2pp seizure (cap-25) |
| Manual verify-repair / temporal-candidates / label-policy | Outran compile-time search on active blockers |

**Rationale:** Optimizers are wired correctly; mismatch is **failure mode** (benchmark alignment, multi-step programs) and **missing ladder rungs**, not broken DSPy integration (`docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md`).

**Active / expected:** **Optimizer automation thesis** — rungs 4–5 on **train** (`exect_s1_ladder_optimizer_automation_v1`): can stripped L0/L1 + DSPy compile match **95.8%** hand-crafted cap-25 without v4_10 policy/bridges in the compile path?

---

## Cross-Cutting Findings (Thesis-Level)

### 1. Dataset and task family dominate the answer

| Setting | Best deterministic placement | Why |
| --- | --- | --- |
| **Gan S0 frequency** | **Pre** temporal candidates + **H4** LLM adjudication + light **post** evidence guard | Temporal structure is explicit; gold labels reward canonical frequency windows |
| **ExECT S1 diagnosis / seizure / medication** | **During** benchmark policy + **post** inline bridges on **L1** constrained LLM | Benchmark policy alignment matters more than extra pre-lists; bridges recover scored labels |
| **ExECT S2–S4 broad schema** | Mostly **L1** constrained extraction; targeted **H2/H1** probes **failed** | Schema breadth changes family mix; micro F1 is not a simple “learning curve” |

### 2. Interleaving position beats component label

The intervention matrix in `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md` is the right mental model: the same knowledge (temporal rules, vocab, evidence) must be compared at **pre / during / tool_during / post**, not as “we added normalization.”

**Strongest positive:** Gan temporal rules at **pre** (not tool_during).  
**Strongest ExECT signal:** Benchmark policy + bridges at **during/post**, not static **pre** lists.

### 3. Model track interacts with placement

| Observation | Implication |
| --- | --- |
| Qwen matches/exceeds GPT on S2–S4 micro | Broader schema does not always favor hosted GPT |
| Qwen lags GPT on S1 (79% vs 92%) | Narrow audited policy surface stresses local model |
| Qwen v4_11 prompt: seizure +18.5pp, diagnosis −5.1pp | **During** policy can help one family and hurt another; promote blocked |
| Qwen bridges contribute less than GPT in interleaving port | Local gap is not fixed by copying GPT **post** path alone |

### 4. What moved the needle vs what explained scores

| Mechanism | Role |
| --- | --- |
| Gan temporal-candidates + VR | **Causal improvement** (promoted architecture) |
| ExECT inline bridges | **Explain and recover** benchmark F1; also risk overfitting to audit policy |
| S1 verify-repair, H2 pre-vocab, S4 MT classifier | **Rejected interventions** |
| DSPy bootstrap on S1 | **Rejected** on cap-25; not default loop |
| Lane A Gan verification/evidence cap-25 | **Null or reject** for single-factor claims on promoted architecture |

---

## What We Have Ruled Out (Do Not Repeat Without New Hypothesis)

Consolidated from negative probes, Lane A, and ladder:

1. **S1 post-bridge H1** as a new product intervention (diagnostic only).
2. **S1/S4 H2** static pre-vocab / pre-candidates in tested shapes.
3. **S1 second-pass verify-repair** on GPT (and prior Gan ReAct H3 as default).
4. **S4 broad medication-temporality post-classifier** abstention policy.
5. **Qwen S1 interleaving port** without model-side or prompt-policy hypothesis.
6. **ExECT v4_11 prompt on GPT** for production (cap-25 reject); Qwen port **hold, promote blocked**.
7. **Gan evidence span-check / optional** arms as comparable factors (confounded).
8. **Ad hoc DSPy bootstrap** against embedded policy examples without L0/L1 ladder baselines.
9. **Recategorizing old bundled runs** as clean single-factor evidence (Lane A policy).

---

## What We Are Actively Testing (2026-05-21)

| Workstream | Taxonomy focus | Status | Expected outcome |
| --- | --- | --- | --- |
| **ExECT S1 optimizer automation thesis** | L0/L1 compile (`example_strategy`) without hand policy in prediction path | **Ready** — configs scaffolded | If compile ≈ 95.8% cap-25, optimizers may replace hand demos; if not, manual policy remains necessary |
| **Ladder rungs 6–7** (BootstrapRS, GEPA) | Same | **Deferred** after 4–5 | Likely low priority given bootstrap reject |
| **Lane Q optional** | `during` prompt policy (Qwen) | **Hold** — v4_11 full | Error-read or seizure-only promotion prereg before any promote |
| **Gan guardrails error-read** | `during` prompt on promoted arch | Optional | Clarify whether +4pp cap-25 port is label noise or real |
| **Registry matrix refresh** | Metadata | Maintenance | Keeps atlas aligned with ladder + Lane A rows |

**Not in flight:** No model-backed runs active per `docs/planning/kanban_plan.md`.

---

## What We Expect (Falsifiable)

1. **ExECT S1:** Further gains on GPT will come from **narrow, family-specific `during` policy** (e.g. Qwen seizure) or **bridge/policy refinements**, not from generic H2 pre-lists or verify-repair — unless a new preregistered mechanism changes candidate **presentation** or recall-safe post rules.

2. **Gan:** Architecture remains **H2+H4**; single-factor sweeps on verification/evidence will stay **null or secondary** on monthly frequency at cap-25 scale.

3. **Optimizers:** Compile may help **L0/L1 bare extraction** but is **unlikely** to beat production L1+policy+bridges without explicitly optimizing toward `exect_field_family_micro_f1` **and** accepting bridge surface — thesis run will clarify.

4. **Schema ladder:** Broader ExECT schemas will continue to show **family-specific** difficulty (seizure/diagnosis on S1 for Qwen; not a monotonic “harder = lower” story without per-family tables).

5. **Published benchmarks:** No paper-safe ExECT/Gan external claims until CUI scoring and real-set access unblock Phase 3 in `docs/planning/kanban_plan.md`.

---

## Interpretation — Are We Still On the Central Thesis?

**Yes.** The project has shifted from “find a better prompt” to **measuring placement of deterministic knowledge** via:

- factorial taxonomy and registry (`hybrid_balance_class`, `interleaving_positions`, `varied_factor`, `comparison_group`);
- clean GPT factor-isolation (Lane A);
- ExECT reference ladder (D1→L0→L1→L1+policy);
- negative-probe closure for misleading ExECT arms.

What felt like drift is **fragmentation of narrative**, not abandonment of the thesis. `docs/planning/kanban_plan.md` optimizes **execution**; `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md` optimizes **ontology**; this document optimizes **synthesis**.

**Partial answer today:**

> **Deterministic clinical knowledge should enter where the task’s bottleneck lives** — temporal structure **before** the LLM on Gan frequency (**H2+H4**); benchmark label alignment **during** extraction and **after** via bridges on ExECT S1 (**L1 + H1 post**), not via generic pre-vocab lists or second-pass repair on the current policy. **Tool-during** and **compile-time demo search** are secondary or rejected on the paths that matter most. **Dataset, schema breadth, and model track** change which placement is worth testing next.

That answer is **strong for Gan S0 frequency**, **decomposed but incomplete for ExECT S1** (policy vs bridges still coupled), and **weak for S2–S4** (few promotable deterministic arms; mostly frozen L1 ladder).

---

## Limitations

- Many historical rows changed multiple factors; clean evidence is **2026-05-20 onward** preregistered groups.
- `hybrid_balance_class` is coarse; rows can carry multiple tags.
- Bridge gains confound **clinical validity** vs **benchmark alignment** — scorer and audit caveats in `docs/datasets/exect/exect_gold_label_audit.md`.
- Cap-25 slices can miss full-validation effects (Gan verification null; some ExECT arms cap-only by design).
- Qwen and GPT runs are not always symmetric comparison groups.

---

## Next Experiments (Smallest Useful Set)

1. **Run** `exect_s1_ladder_optimizer_automation_v1` (rungs 4–5 on train, eval on validation) — tests whether `example_strategy` can substitute for hand-crafted policy at L0/L1.
2. **Optional:** Qwen diagnosis-drift error-read on v4_11 full vs `…210722Z` before any seizure-only promote.
3. **Do not run** closed shapes in `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md` without a new `varied_factor` and preregistration.
4. **Consolidation:** Add taxonomy blocks to any new inspection doc; update `docs/taxonomy/experiment_taxonomy_research_synthesis_20260520.md` § “Direct Answers” with ladder + Lane A citations (or supersede with this doc as the living synthesis).
5. **Phase 3 (blocked):** CUI-aware ExECT pack and Gan real-set — only when reproduction blockers clear.

---

## Artifact References Used

| Artifact | Use in this synthesis |
| --- | --- |
| `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md` | Ontology and intervention matrix |
| `docs/taxonomy/experiment_taxonomy_research_synthesis_20260520.md` | Registry-level answers (2026-05-20) |
| `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md` | Closed ExECT mechanisms |
| `docs/experiments/exect/exect_s1_full_ladder_gpt_validation_v1_inspection_20260521.md` | D1/L0/L1/L1+policy decomposition |
| `docs/experiments/exect/exect_s1_gpt_factor_isolation_cap25_inspection_20260521.md` | S1 prompt/verification/evidence |
| `docs/experiments/gan/gan_s0_lane_a_gpt_cap25_inspection_20260521.md` | Gan verification/evidence/prompt nulls |
| `docs/workstreams/optimizer/dspy_optimizer_investigation_20260521.md` | Optimizer ladder and rejects |
| `docs/experiments/exect/exect_s1_seizure_prompt_policy_qwen_v1_inspection_20260520.md` | Qwen v4_11 hold / promote blocked |
| `docs/planning/kanban_plan.md` | Active/complete status as of 2026-05-21 |

---

## Claims That Remain Tentative

- Exact split of ExECT **prompt policy** vs **bridge code** as causal drivers of 92.3% micro F1.
- Whether optimizer compile on L0/L1 can approach hand-crafted cap-25 without bridges in the metric path.
- Whether any Gan prompt-policy port (+4pp guardrails cap-25) matters at full validation on the promoted architecture.
- Generalization of all findings to **published** benchmarks and external datasets.

**Recommended maintainer action:** Link this doc from `docs/planning/kanban_plan.md` header as the **big-picture synthesis**; treat `docs/taxonomy/experiment_taxonomy_research_synthesis_20260520.md` as the implementation log unless updated.

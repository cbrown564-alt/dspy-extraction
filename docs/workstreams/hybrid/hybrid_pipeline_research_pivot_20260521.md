# Research Pivot: Three-Axis Hybrid Pipeline Exploration

Date: 2026-05-21  
Status: **Active research doctrine** — supersedes premature closure language in prior syntheses  
Type: Critical report and programmatic pivot  
Related:

- Ontology (unchanged): `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`
- Prior snapshot (historical bets, not closure): `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`
- Execution plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`
- Agent skill: `.agents/skills/hybrid-pipeline-exploration/SKILL.md`
- Operating board: `docs/planning/kanban_plan.md`

---

## Executive Summary

The project built strong **engineering defaults** and useful **taxonomy infrastructure**, but often stated **scientific conclusions** that the evidence does not support. We confused:

| What we often claimed | What we often had |
| --- | --- |
| “Mechanism X is rejected” | One **arm** (one config, one implementation, one slice) failed a gate |
| “Path Y is closed” | We will not rerun **that exact program** without a new hypothesis |
| “Hybrid placement is answered” | We have a **promoted default** on Gan and a **decomposed ladder** on ExECT S1 |

This document is a **research pivot**, not a repudiation of past work. Frozen anchors, registry rows, and inspection artifacts remain valuable. What changes is **how we decide what to run next** and **how we language outcomes**.

**New central program:** systematically explore three axes on **GPT 4.1-mini cap-25 grids** before narrowing again.

1. **Axis 1 — Pipeline depth:** How many stages should the pipeline have?
2. **Axis 2 — Placement:** At each stage, should work be deterministic, probabilistic (LLM), or hybrid?
3. **Axis 3 — Implementation:** Given a stage assignment, what concrete form should each stage take?

We have barely begun Axis 1. We have sampled Axis 2. We have **not** searched Axis 3.

---

## The Fundamental Error: Arm Reject vs Mechanism Reject

### Definitions

| Term | Meaning | When it is justified |
| --- | --- | --- |
| **Operational freeze** | Default config for reproducibility and comparison | Any time we need a stable baseline |
| **Reject (arm)** | This **specific** program config under these controls failed preregistered gates | One inspection doc, one comparison group, explicit `varied_factor` |
| **Reject (mechanism)** | The **hypothesis class** is unlikely to help across reasonable implementations | Multiple arms, multiple implementations or positions, same mechanism label |
| **Hold** | Evidence insufficient, confounded, or slice-only | Default for single cap-25 nulls |
| **Open** | Hypothesis class still live | Default for placement and implementation questions |

### How we violated this

**Gan S0 — temporal candidates**

- **Freeze (operational):** temporal-candidates + verify-repair is the current best default on validation.
- **Not proven:** deterministic candidate generation is the best **placement** for temporal structure.
- **Missing:** LLM-only candidate identification with the same downstream adjudication; temporal-candidates **without** repair (deferred in verification prereg); equal-budget “LLM does what `temporal_candidates.py` does” arms.

**Gan S0 — H3 ReAct**

- **Reject (arm):** one ReAct tool interface on a Qwen regression slice.
- **Not reject (mechanism):** tool-during temporal knowledge — only one tool surface was tested.

**ExECT — H2 pre-vocab / section-aware**

- **Reject (arm):** static list injection and section-aware context in tested shapes on S1/S0 cap-25/slices.
- **Not reject (mechanism):** all `pre` context selection or controlled vocabulary — e.g. section-aware may be wrong for short notes but right for long letters; different candidate **presentation** was not swept.

**ExECT S1 — verify-repair**

- **Reject (arm):** one verify-repair config on cap-25 (−9.4pp micro vs single-pass with inline bridges).
- **Not reject (mechanism):** verification or repair at **any** stage with **any** policy — stage count and repair target were not isolated.

**ExECT S1 — “closed probes”**

- Negative-probe synthesis correctly stops **repeat waste** on identical configs.
- It must **not** be read as closing **interleaving positions** or **hybrid balance classes** globally.

### Language we will use going forward

In inspection docs, registry `notes`, and Kanban:

```text
decision_scope: arm | mechanism | operational
outcome: freeze | reject | hold | open | promote
```

- Registry `outcome: reject` without `decision_scope` should be interpreted as **reject (arm)** until a mechanism review explicitly upgrades it.
- Kanban “Current Decisions” table lists **operational freezes** and **arm rejects** separately from **open mechanism classes**.

---

## Three Research Axes (Programmatic Frame)

### Axis 1 — How many stages?

**Question:** What decomposition of the end-to-end task (context → candidates → extract → normalize → verify → repair → evidence) maximizes benchmark-facing quality per unit complexity?

**What we did:** A few architectures (1-stage direct, 2-stage verify-repair, 2–3-stage temporal+VR, tool loop). ExECT D1→L0→L1→L1+policy is a **partial** decomposition but conflates stage count with policy and bridges.

**What we did not do:** Treat `pipeline_stage_count` or `stage_graph_id` as the **primary varied factor** with fixed scorer, model, and task.

**Axis 1 control:** Candidate stages in the first Gan grid use deterministic `temporal_candidates.py` only. LLM-only or hybrid candidate generation belongs to Axis 2, after a competitive stage graph exists.

**Examples of stage graphs to compare (Gan S0 first):**

| `stage_graph_id` | Stages (high level) |
| --- | --- |
| `g1_extract_only` | Single LLM extract+normalize |
| `g2_extract_repair` | Extract → repair/normalize |
| `g2_candidates_adjudicate` | Candidates → adjudicate label |
| `g3_candidates_extract_repair` | Candidates → window extract → repair |
| `g3_extract_verify_repair` | Extract → verify → repair |

Axis 1 must be explored **before** declaring an architecture “optimal.”

### Axis 2 — Deterministic vs probabilistic at each stage?

**Question:** For each stage in a fixed graph, should the executor be deterministic code, LLM, or hybrid?

**What we did:** Taxonomy tags (`H1`–`H4`, `L0`–`L1`) and a handful of probes; Gan promotion encodes det-pre + LLM-adjudicate without an LLM-pre candidate arm.

**What we did not do:** For a **fixed stage graph**, swap det/LLM/hybrid **per stage slot** (factorial or fractional factorial on GPT cap-25).

**Critical open cell (Gan):** **Candidate generation** — deterministic `temporal_candidates.py` vs LLM candidate ID vs hybrid merge — with **identical** downstream adjudication and scorer.

### Axis 3 — What should each implementation look like?

**Question:** Given stage count and det/LLM assignment, which concrete implementation wins?

**Design space (non-exhaustive):**

- Prompt policy variants (rules in prompt vs examples vs both)
- Tool interfaces (ReAct vs structured tool calls vs none)
- Candidate presentation (table, JSON, bullets, inline spans)
- Bridge placement (inline vs post module vs eval-only)
- Evidence (quote, span-check, optional, soft)
- Optimizer/demo strategy (zero-shot, labeled, bootstrap, GEPA)
- Control mode (soft hint vs hard constraint)

**Rule:** Axis 3 sweeps are **in scope only after** Axis 1–2 identify a competitive stage graph and per-stage assignment. Until then, a failed v4_11 prompt or one ReAct config is **arm reject**, not mechanism reject.

---

## What We Actually Know (Restated Conservatively)

### Strong enough to freeze operationally (not mechanism-closed)

| Default | Scope | Evidence |
| --- | --- | --- |
| Gan temporal-candidates + VR + v1.1 policy | Gan S0 validation, GPT/Qwen full | Promoted full-validation runs; best **known arm** |
| ExECT S1 GPT v4_10 + inline bridges | ExECT S1 validation | 92.3% micro full; ladder L1+policy match |
| ExECT S2–S4 GPT frozen ladder | Schema complexity series | Freeze for ladder comparisons |
| Taxonomy + registry + prereg discipline | Repo operations | Infrastructure, not science |

### Arm rejects (do not rerun without new hypothesis doc)

Listed in `docs/experiments/exect/exect_negative_probe_synthesis_20260520.md` and Lane A / ladder inspections — **specific configs and comparison groups only**.

### Open mechanism classes (explicitly not closed)

| Mechanism class | Why still open |
| --- | --- |
| Optimal **stage count** | Few graphs tried; no stage-count ladder |
| **LLM vs det** for temporal candidate ID (Gan) | Never cleanly isolated |
| **Pre** context/candidate strategies (ExECT) | One section-aware / static-list shape ≠ all `pre` |
| **Tool-during** hybrids | One ReAct arm |
| **Verify/repair** placement | One S1 arm; Gan verification cap-25 null but architecture confounded |
| **Compile-time** optimizers | One bootstrap arm; ladder rungs 4–5 not yet run |
| **Prompt-policy** at stage level | v4_11 arm reject on GPT; Qwen hold — not full policy space |

---

## Why This Happened

1. **Benchmark velocity** — needed defaults; freezes became conclusions.  
2. **Taxonomy outcomes** — `reject` read as scientific closure.  
3. **Negative-probe phase** — stopped reruns but over-generalized in prose.  
4. **Cheap GPT underused for grids** — cap-25 used to confirm nulls more than to **search** stage/assignment space.  
5. **Conflated axes** — architecture labels hid stage count and per-stage executor.  
6. **Single implementation generalization** — especially placement (H2/H3) and tools.

---

## Pivot Principles (Non-Negotiable)

1. **GPT 4.1-mini cap-25 grids first** — search wide, confirm narrow, then Qwen/full validation.  
2. **One primary varied factor per comparison group** — stage graph, stage executor, or implementation variant — not “new program name.”  
3. **Reject (arm) in inspection; reject (mechanism) only in mechanism review** with ≥2 implementations or positions.  
4. **Operational freeze ≠ epistemic closure** — Kanban separates “Default for runs” from “Mechanism status.”  
5. **Gan before ExECT for Axis 1–2** — cleaner task, fewer bridge confounds; ExECT follows with policy/bridge caveats documented.  
6. **Compose primitives** — new arms use `arm_templates` and catalog primitives; document `decision_scope` in every inspection.  
7. **No “closed probe” language without** `decision_scope: arm` and explicit comparison group ID.

---

## Relationship to Existing Docs

| Doc | Role after pivot |
| --- | --- |
| `hybrid_component_taxonomy_decision_20260520.md` | Ontology — still valid |
| `hybrid_deterministic_placement_research_synthesis_20260521.md` | **Historical snapshot** of bets; read pivot for doctrine |
| `exect_negative_probe_synthesis_20260520.md` | **Arm-repeat guardrail** — not global mechanism closure |
| `kanban_plan.md` | **Active queue** — three-axis grids replace “closed” narrative |
| `experiment_registry.json` | Add `decision_scope` in `notes` when updating rows |

---

## Success Criteria for the Pivot

We are “back on track” when:

1. Every new comparison group states **axis** (1/2/3), `stage_graph_id`, `varied_factor`, and `decision_scope` target.  
2. Gan has a completed **stage-graph** cap-25 matrix and a follow-up **candidate-source executor** grid with inspection docs.  
3. Kanban **Open mechanism classes** table is maintained alongside **Operational defaults**.  
4. No inspection doc claims **mechanism reject** without a mechanism review section citing ≥2 arms.  
5. Qwen/full validation runs only for cells that win cap-25 search.

---

## Immediate Next Step

Execute Phase 0–1 in `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`: doctrine embedded (this doc, skill, Kanban), then **Gan S0 Axis 1 stage-graph** preregistration and config batch. Axis 2 candidate-source arms follow only after the Axis 1 inspection ranks the skeletons.

Use skill: **`hybrid-pipeline-exploration`** for all new experiment design and decision writing.

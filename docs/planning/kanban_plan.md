# Clinical Extraction Kanban Plan

**Active steering doc** — what to work on next. Detailed card history, run IDs, and inspection notes live in pathway walkthroughs, experiment inspections, and [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md).

**Last refreshed:** 2026-05-24

## Steering References

| Purpose | Source |
| --- | --- |
| Research direction | [outline.md](../outline.md) |
| Hybrid doctrine | [hybrid_pipeline_research_pivot_20260521.md](../workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md) |
| Pipeline synthesis | [core_research_questions_pipeline_review_20260524.md](../experiments/synthesis/core_research_questions_pipeline_review_20260524.md) |
| ExECT / Gan audits | [exect_gold_label_audit.md](../datasets/exect/exect_gold_label_audit.md), [gan_2026_label_audit.md](../datasets/gan/gan_2026_label_audit.md) |
| Scorer guardrails | [deterministic_scorer_semantics.md](../policies/deterministic_scorer_semantics.md) |
| Frozen paper defaults | [paper_frozen_operational_defaults_20260524.md](../experiments/synthesis/paper_frozen_operational_defaults_20260524.md) |
| Experiment registry | [experiment_registry.json](../experiments/synthesis/experiment_registry.json) |

---

## Current Priorities

1. **ExECT S5 seizure frequency iteration.** Paper freeze is 72.3% freq F1 (verifier + A3 stack). High-precision candidate pruning and temporal medication guard are **rejected arms** (D2). Next mechanism work: residual-driven verifier/policy tuning — not candidate narrowing.
2. **Gan S0 — hold new arms.** Builder-gap v1 stays the default (80.6% monthly). Residual map is documented; unknown-overuse prompt and GEPA G1/G2 are rejected (D2). Any new Gan work needs preregistration (builder extension for no-candidate records is the highest-upside deferred item).

---

## Key Findings (Recent)

Condensed outcomes from completed pathways. Full detail in linked walkthroughs and inspections.

| Area | Finding | Implication |
| --- | --- | --- |
| **ExECT S5 frequency** | Pre-vocab injection + verifier + A3 policy raised freq F1 from 60.2% → **72.3%** (full validation). High-precision candidate pruning regressed recall. | Keep high-recall candidates; iterate verifier/policy, not narrowing. |
| **ExECT S5 medication** | AM guard (`am_guard_non_asm_brand_alias.v1`) → 88.7% F1. Temporal evidence guard → 100% precision but −20.7pp recall on cap-25. | Promoted guard is brand/non-ASM repair only; temporal pruning rejected. |
| **Gan S0** | Unknown-overuse prompt: **16.0%** monthly (rejected). GEPA G1/G2: 60.0% / 48.0% monthly (rejected). Pragmatic monthly divergence (16 records) partially fixable; monthly vs pragmatic gap (80.6% vs 88.6%) is paper-reportable. | No broad optimizer or prompt arms without new prereg and root-cause fixes. |
| **Explorer** | ExECT + Gan share `explorer_model_catalog` schema; Model panel uses dataset-specific metric labels. | Inspection surface ready for paper review — no new Explorer work required. |
| **Rejected mechanisms** | High-precision ExECT freq candidates, Gan unknown-overuse v1.5, GEPA multi-stage G1/G2, ExECT A4 temporal med guard, Gan C2 prompt variants. | Capture in D2 arm-reject table with `decision_scope: arm`. |

**Completed pathway walkthroughs:** [Pathway A (A4 rejected)](../experiments/exect/exect_s5_medication_temporal_guard_walkthrough_20260524.md) · [Pathway B](../experiments/exect/exect_explorer_pathway_b_completion_walkthrough_20260524.md) · [Pathway C](../experiments/gan/gan_s0_pathway_c_completion_walkthrough_20260524.md) · [Pathway D](../experiments/synthesis/pathway_d_paper_evidence_freeze_walkthrough_20260524.md) · [Pathway E](../experiments/synthesis/pathway_e_workflow_readiness_completion_walkthrough_20260524.md)

---

## Active Work

### Pathway D — Paper Evidence Freeze

| Card | Status | Artifact |
| --- | --- | --- |
| D1. Operational-default table | **Done** | [paper_frozen_operational_defaults_20260524.md](../experiments/synthesis/paper_frozen_operational_defaults_20260524.md) |
| D2. Negative/arm-reject table | **Done** | [paper_frozen_arm_reject_table_20260524.md](../experiments/synthesis/paper_frozen_arm_reject_table_20260524.md) |
| D3. Results narrative | **Done** | [paper_frozen_results_narrative_20260524.md](../experiments/synthesis/paper_frozen_results_narrative_20260524.md) |
| D4. Test/benchmark protocol | Backlog | Only after explicit need for holdout reporting |

### Pathway E — Workflow Readiness

| Card | Status | Next action |
| --- | --- | --- |
| E1. API key preflight | Done | — |
| E2. Qwen high-context warning | Done | — |
| E3. Provider smoke ledger | **Done** | [provider_smoke_ledger_20260524.md](../policies/provider_smoke_ledger_20260524.md) |
| E4. Cursor implementation workflow | Done | — |

---

## Operational Defaults

Authoritative numbers and run IDs: [paper_frozen_operational_defaults_20260524.md](../experiments/synthesis/paper_frozen_operational_defaults_20260524.md). Arm rejects and results narrative: [paper_frozen_arm_reject_table_20260524.md](../experiments/synthesis/paper_frozen_arm_reject_table_20260524.md), [paper_frozen_results_narrative_20260524.md](../experiments/synthesis/paper_frozen_results_narrative_20260524.md).

| Track | Default | Headline metric | Caveat |
| --- | --- | --- | --- |
| Gan S0 | `gan_s0_candidate_builder_gap_v1` / GPT 4.1-mini | 80.6% monthly | Synthetic validation only |
| Gan Qwen | Builder-gap v1 / Qwen3.6:35b | 70.7% monthly, 90.6% pragmatic | Local transfer |
| ExECT S1–S4 | Frozen GPT ladder | S1 92.3% → S4 65.5% micro | Comparison anchors |
| ExECT S5 (paper) | Pre-vocab + AM guard + freq verifier + A3 | **85.5%** micro; freq **72.3%** F1 | Paper-frozen 2026-05-24 |

---

## Blocked Or Gated

| Item | Release condition |
| --- | --- |
| Published ExECTv2 Table 1 reproduction | CUI-aware scorer + explicit reproduction workstream |
| Gan Real(300)/Real(150) | Dataset access + preregistered reporting plan |
| GEPA G3/G4 | New compact-instruction or submodule-freezing hypothesis + cap-25 prereg |
| Test/holdout reporting | Explicit protocol (D4); no accidental test spend |

---

## Optional Follow-Ons (Not Active)

Require new preregistration. Do not pull unless paper or benchmark gates justify model spend.

- Gan builder extension for no-candidate `other_semantic_mismatch` records
- Gan multi-type highest-frequency or window-priority prompt arms
---

## Standing Guardrails

- Do not silently change scorer semantics; update tests and document interpretation.
- Gan gold is `seizure_frequency_number[0]`; `reference[0]` is diagnostic only.
- Distinguish `unknown` from `no seizure frequency reference`.
- Keep arm rejection separate from mechanism rejection; name `decision_scope` in inspection docs.
- ExECT S5 families: diagnosis, seizure type, annotated medication, investigation, seizure frequency (medication temporality excluded unless reopened).
- High-recall ExECT frequency candidates remain baseline; high-precision pruning is rejected.
- Cursor SDK drafts are leads, not evidence, until manually promoted from primary artifacts.
- No broad Gan optimizer arms without preregistered hypothesis after residual forensics.

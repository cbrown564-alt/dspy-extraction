# 24-Hour Progress Review and Local-Model Gap Analysis

Date: 2026-05-24  
Status: Source-backed steering review  
Decision scope: synthesis only — no scorer, loader, registry, or model-output changes  
Companion: [kanban_plan.md](../../planning/kanban_plan.md)

## Executive Summary

The last 24 hours closed five Kanban pathways (A–E), froze paper-facing evidence (Pathway D), promoted ExECT S5 frequency verifier + A3 policy to operational default (72.3% freq F1 / 85.5% micro), and closed Gan S0 mechanism search (Pathway C). Rapid iteration used **GPT 4.1-mini** as the primary experimentation anchor because of fast turnaround and stable adapter behavior.

**Critical gap identified:** promoted implementations for **ExECT S5 and all post-S4 hybrid stacks have no Qwen3.6:35b transfer runs**. Gan S0 builder-gap v1 and ExECT S1–S4 have side-by-side Qwen comparisons, but **local parity is not achievable on every surface today** — and we cannot claim best local variant for S5 at all.

**Strategic goal:** best-performing implementation on a local model for every surface (G0/S1–S5), or at minimum a documented side-by-side with the best closed-model variant per surface.

---

## Part 1 — What Was Tested, Implemented, Evaluated, and Uncovered

### Pathway closures (2026-05-23 → 2026-05-24)

| Pathway | Outcome | Key artifacts |
| --- | --- | --- |
| **A — ExECT S5 medication temporality guard** | **Rejected (arm)** | [exect_s5_medication_temporal_guard_walkthrough_20260524.md](../exect/exect_s5_medication_temporal_guard_walkthrough_20260524.md) — 100% precision but −20.7pp recall on cap-25 |
| **B — Explorer catalog completion** | **Done** | [exect_explorer_pathway_b_completion_walkthrough_20260524.md](../exect/exect_explorer_pathway_b_completion_walkthrough_20260524.md) — shared model catalog schema for ExECT + Gan |
| **C — Gan S0 residual / mechanism search** | **Closed** | [gan_s0_pathway_c_completion_walkthrough_20260524.md](../gan/gan_s0_pathway_c_completion_walkthrough_20260524.md) — C2 unknown-overuse guard rejected (16% monthly); GEPA G1/G2 rejected |
| **D — Paper evidence freeze** | **Done** | D1 operational defaults, D2 arm-reject table (23 rows), D3 results narrative |
| **E — Workflow readiness** | **Done** | Provider smoke ledger, Qwen high-context policy, API preflight |

### ExECT S5 frequency iteration (active thread, GPT-only)

| Stage | Status | Headline | Run / config |
| --- | --- | --- | --- |
| A1 residual audit | Done | 17 qualitative FP docs mapped | [exect_s5_frequency_residual_audit_20260524.md](../exect/exect_s5_frequency_residual_audit_20260524.md) |
| A2 frequency verifier (buggy) | Rejected | Recall −20pp | cap-25 |
| A2R verifier repair | Cap-25 fail on recall gate | F1 +11.2pp but recall −16pp | led to A3 |
| A3 prompt policy + full validation | **Promoted** | Freq F1 60.2% → **72.3%**; micro 81.4% → **85.5%** | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_gpt4_1_mini_20260524T195813Z` |
| High-precision candidates | **Rejected** | Recall −12pp, no precision gain | cap-25 |
| Post-promotion residual audit | Done | Precision-dominated residuals for v2 | [exect_s5_frequency_post_promotion_residual_audit_20260524.md](../exect/exect_s5_frequency_post_promotion_residual_audit_20260524.md) |
| v2 preregistration + implementation | Done, **gate pending** | v1.3 qualitative gate + v2 verifier rules 7–9 | `exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2_cap25_gpt4_1_mini.json` (GPT only) |

**Uncovered S5 insights:**

1. Seizure frequency gains come from **reject-only verifier + prompt policy**, not candidate narrowing.
2. AM guard (`am_guard_non_asm_brand_alias.v1`) is a stable component — 88.7% medication F1 retained in promoted stack.
3. Residual frequency errors are **qualitative false positives** (`infrequent`, `frequency same`) and temporal-scope mismatches — v2 targets these explicitly.
4. Medication temporality remains **open** (A4 rejected; G0G2 dose-current guard passes arm gates but is not a full S4 solution).

### Gan S0 (frozen operational default)

| Item | Result |
| --- | --- |
| Operational default | `gan_s0_candidate_builder_gap_v1` / GPT 4.1-mini → **80.6%** monthly |
| Qwen transfer (same surface) | **70.7%** monthly — accepted local arm, not parity |
| C2 unknown-overuse guard | 16.0% monthly — rejected |
| GEPA G1/G2 | −16pp / −28pp vs G0 control — rejected |
| Residual map | `other_semantic_mismatch` (17), pragmatic-monthly divergence (16), builder coverage gaps on no-candidate records |

**Uncovered Gan insights:**

1. Deterministic candidate builders are the dominant mechanism — not prompt addenda or optimizers.
2. Qwen transfers the builder-gap surface (+6.3pp vs Qwen F0) but trails GPT by ~9.9pp monthly.
3. Pragmatic category (88.6% GPT / 90.6% Qwen) exceeds monthly accuracy — paper must attribute the 8pp gap.

### ExECT schema ladder (S1–S4, frozen GPT anchors)

Breadth-pressure story validated: S1 92.3% → S4 65.5% micro F1 (GPT 4.1-mini, 40-record validation). Negative probes consolidated: section split, verify-repair, static pre-vocab, BootstrapFewShot all rejected on S1/S4.

### Cross-cutting synthesis

| Deliverable | Role |
| --- | --- |
| [core_research_questions_pipeline_review_20260524.md](core_research_questions_pipeline_review_20260524.md) | Three-axis answers: Gan = pre-LLM candidates; ExECT = broad LLM + post bridges |
| [paper_frozen_operational_defaults_20260524.md](paper_frozen_operational_defaults_20260524.md) | Authoritative numbers for manuscript |
| [paper_frozen_arm_reject_table_20260524.md](paper_frozen_arm_reject_table_20260524.md) | 23 rejected arms with `decision_scope: arm` |
| [model_suite_pattern_interpretation_20260522.md](model_suite_pattern_interpretation_20260522.md) | Model profiles — no universal winner; surface-dependent |

### Engineering / infra (supporting experimentation velocity)

- Provider smoke ledger (E3): Qwen3.6:35b pass on F0 + S1 + S4; GPT 4.1-mini pass on S1 + S4
- Explorer model panel: dataset-specific metric labels ready for inspection
- ExECT S4 prompt v1.3 qualitative evidence gate scaffolded (feeds S5 v2)
- Frequency verifier v2 policy implemented in code; cap-25 config exists (GPT only)

---

## Part 2 — Local vs Closed Model: Surface-by-Surface Status

**Local model anchor:** Qwen3.6:35b via Ollama (project's primary local deployment target)  
**Closed anchor:** GPT 4.1-mini (experimentation default) plus best-known closed alternative where it beats GPT  
**Split/scorer:** synthetic validation only; frozen deterministic scorers per surface

### Summary matrix

| Surface | Best closed variant (program) | Closed headline | Best local variant (program) | Local headline | Qwen tested on promoted stack? | Local vs GPT Δ | Local viability |
| --- | --- | ---: | --- | ---: | --- | ---: | --- |
| **G0 (Gan S0)** | builder-gap v1 / GPT 4.1-mini | 80.6% monthly | builder-gap v1 / Qwen3.6:35b | 70.7% monthly | **Yes** | −9.9pp | Viable alternative; not best |
| **S1** | v4_10 + bridges / GPT 4.1-mini | 92.3% micro | same program / Qwen3.6:35b | 79.0% micro | **Yes** (same program) | −13.3pp | Weak on seizure_type (55.7% vs 90.5%) |
| **S2** | S2 v1.3 / GPT 4.1-mini | 80.9% micro | same / Qwen3.6:35b | 82.6% micro | **Yes** | +1.7pp | **Local leads pooled micro** |
| **S3** | S3 v1.2 / GPT 4.1-mini | 72.1% micro | same / Qwen3.6:35b | 72.2% micro | **Yes** | +0.1pp | **Near parity** |
| **S4** | S4 v1.2 + cause bridge / GPT 4.1-mini | 65.5% micro | same / Qwen3.6:35b | 67.5% micro | **Yes** | +2.0pp | **Local leads pooled micro**; family profile differs |
| **S5** | freq verifier v1 + A3 + AM guard / GPT 4.1-mini | 85.5% micro; 72.3% freq | — | — | **No** | unknown | **Gap — zero Qwen runs** |

### Best closed model is not always GPT 4.1-mini

From the frozen model suite ([model_suite_pattern_interpretation_20260522.md](model_suite_pattern_interpretation_20260522.md)):

| Surface | GPT 4.1-mini | Best closed (non-GPT) | Best local (any Qwen) |
| --- | ---: | ---: | ---: |
| S1 micro | **92.3%** | Gemini 3.1 Flash-Lite 90.3% | Qwen 3.6:27b 85.7% (not 35b) |
| S4 micro | 65.5% | GPT 5.5 **68.7%** | Qwen 3.6:27b **69.3%** |
| Gan F0 monthly | 68.1% | Gemini 3 Flash **75.3%** | Qwen 3.6:27b 74.9% (F0, not builder-gap) |

**Implication:** even when Qwen3.6:35b is the deployment target, **Qwen 3.6:27b sometimes outperforms 35b** on the same frozen architecture (S4, Gan F0). Local-model strategy should report both if 27b remains in the smoke ledger — but operational local default should still be evaluated on **35b first** per project intent, with 27b as a secondary local track.

### Surfaces where local cannot yet match closed

| Surface | Blocker | Evidence |
| --- | --- | --- |
| **G0 monthly accuracy** | Semantic adjudication gap on temporal candidates | Qwen 70.7% vs GPT 80.6% on identical builder-gap v1 |
| **S1 seizure_type** | Benchmark policy alignment | Qwen 55.7% vs GPT 90.5% F1; v4_12 diagnosis-stabilized Qwen arm exists but did not close gap |
| **S5 entire stack** | No transfer run | All S5 iteration (pre-vocab, AM guard, verifier v1/v2, A3) GPT-only |

### Surfaces where local matches or exceeds GPT 4.1-mini

| Surface | Observation | Caveat |
| --- | --- | --- |
| S2 | +1.7pp pooled micro | Per-family profile differs; comorbidity still weak |
| S3 | +0.1pp pooled micro | Sparse families remain weak on both tracks |
| S4 | +2.0pp pooled micro | Per-family divergences — do not claim universal S4 superiority |

---

## Part 3 — Model-Specific Effects We Must Account For

The last 24 hours reinforced that **program variant × model** interactions are real:

1. **Gan builder-gap v1** lifts Qwen +6.3pp but GPT +12.5pp vs respective F0 baselines — mechanism is model-agnostic; magnitude is not.
2. **ExECT S1** rewards GPT's seizure-type policy obedience; stronger general models (GPT 5.5, Claude) can score *lower* than GPT 4.1-mini on S1.
3. **ExECT S5 verifier** recall tradeoff (−6.9pp vs AM-guard-only) may behave differently on Qwen — reject-only verifier calibration is model-sensitive until tested.
4. **GEPA optimizers** regressed on Gan (−16 to −28pp) — optimizer arms cannot be assumed to transfer across models.
5. **Cap-25 optimism** (~+3.5pp vs full on S1) means local transfer gates should use **full validation** for promotion decisions, cap-25 for search only.

---

## Part 4 — Recommended Local-Model Transfer Program

Priority order: close the S5 gap first (largest untested promoted stack), then deepen G0/S1 where local clearly trails.

### Phase L1 — S5 Qwen transfer (blocking gap)

| Step | Action | Config pattern |
| --- | --- | --- |
| L1.1 | Full-validation Qwen transfer of **paper-frozen S5 v1 stack** | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_full_qwen35b_ollama.json` |
| L1.1 smoke | 3-record contract check before full run | `configs/experiments/exect_s5_frequency_pre_vocab_am_guard_frequency_verify_smoke_qwen35b_ollama.json` |
| L1.2 | Side-by-side table: GPT vs Qwen per family (especially freq, seizure_type, medication) | Inspection doc |
| L1.3 | Only after L1.1: Qwen cap-25 for **v2 arm** (parallel to GPT v2 gate) | Clone v2 cap-25 config |
| L1.4 | If Qwen freq F1 delta > −5pp vs GPT: accept local S5 variant; else document best local sub-variant | Promotion review |

**Gate (preregister):** local S5 acceptable if pooled micro ≥ GPT −5pp AND seizure_frequency F1 ≥ GPT −8pp on full validation, with guard families within −3pp each.

### Phase L2 — G0 Gan local optimization

| Step | Action |
| --- | --- |
| L2.1 | Error forensics: Qwen-only monthly mismatches vs GPT on builder-gap v1 (87 errors documented) |
| L2.2 | Test whether Qwen-specific prompt policy (not unknown-overuse — rejected) improves semantic adjudication |
| L2.3 | Optional: Qwen 27b builder-gap full validation if 35b ceiling confirmed |

**Goal:** raise Qwen monthly from 70.7% toward ≥75%; accept that GPT may remain operational default.

### Phase L3 — S1 seizure-type local bridge

| Step | Action |
| --- | --- |
| L3.1 | Re-run Qwen with v4_12 diagnosis-stabilized policy (configs exist; verify full-validation artifact) |
| L3.2 | If seizure_type still <75% F1: preregister Qwen-specific seizure-type examples or post-bridge — **one factor at a time** |
| L3.3 | Side-by-side: best local S1 vs best closed S1 (GPT 4.1-mini 92.3%) |

### Phase L4 — Closed-model ceiling documentation (S4/S5)

For paper and deployment honesty, run **one** best-closed comparison per hard surface:

| Surface | Closed challenger | Why |
| --- | --- | --- |
| S4 | GPT 5.5 (68.7% micro) | Beats GPT 4.1-mini on hard families |
| S5 | Gemini 3.1 or GPT 5.5 on promoted stack | Unknown — no S5 closed-model suite yet |
| G0 | Gemini 3 Flash on builder-gap v1 | May beat GPT 4.1-mini if ported to builder-gap (currently F0 evidence only) |

These are **comparison anchors**, not operational promotions, unless they clear existing gates.

---

## Part 5 — What Remains Uncertain

| Uncertainty | Why it matters |
| --- | --- |
| S5 Qwen transfer magnitude | Entire promoted stack untested locally |
| Whether v2 verifier generalizes to Qwen | v2 tuned on GPT residual audit |
| Qwen 35b vs 27b on builder-gap v1 | 27b stronger on F0/S4 in model suite; 35b is deployment target |
| Best closed model for S5 | Only GPT 4.1-mini tested on S5 hybrid stack |
| Real benchmark parity | All numbers synthetic validation; Gan Real and ExECT CUI reproduction blocked |
| S5 v2 cap-25 outcome | Pending GPT gate; should not run Qwen v2 before GPT v2 gate clears or simultaneously |
| S5 per-family decomposition ceiling | No test on 5-family S5 core surface; S1 cap-25 family-split arms rejected but used immature prompt/policy — not mechanism-closed |

---

## Part 6 — Kanban Steering Updates

### Completed (last 24h) — no further pull unless regression

- Pathways A, B, C, D, E
- Gan S0 operational default promotion + Pathway C closure
- ExECT S5 verifier v1 + A3 full-validation promotion
- Paper evidence freeze (D1–D3)
- Explorer catalog; provider smoke ledger

### Active (continue)

- ExECT S5 frequency v2 cap-25 gate (GPT) — config ready
- Post-promotion residual iteration documentation

### New priority — Local model transfer track

| Card | Priority | Depends on |
| --- | --- | --- |
| L1.1 S5 Qwen full-validation transfer | **P0** | None — clone existing GPT config |
| L1.2 S5 local vs closed comparison doc | P0 | L1.1 |
| L2 G0 Qwen error forensics | P1 | L1 complete |
| L3 S1 Qwen seizure-type arm | P1 | — |
| L4 Best-closed S4/S5 anchors | P2 | L1.1 |
| C1.0 S5 per-family parallel ceiling prereg | P2 | None — fresh design, not S1 PG1/g3 replay |
| C1.1–C1.4 S5 ceiling implement → tradeoff doc | P2 | C1.0; parallel with L-track |

### Explicit deferrals (unchanged)

- Gan Real(300)/Real(150)
- ExECT CUI-aware Table 1 reproduction
- D4 test/holdout protocol
- Broad Gan optimizer arms without prereg

---

## Artifact Index

| Category | Primary paths |
| --- | --- |
| Paper freeze | `docs/experiments/synthesis/paper_frozen_*.md` |
| Pathway walkthroughs | `docs/experiments/*/pathway_*_walkthrough_20260524.md` |
| S5 frequency | `docs/experiments/exect/exect_s5_frequency_*_20260524.md` |
| Gan S0 | `docs/experiments/gan/gan_s0_pathway_c_completion_walkthrough_20260524.md` |
| Model profiles | `docs/experiments/synthesis/model_suite_pattern_interpretation_20260522.md` |
| Registry | `docs/experiments/synthesis/experiment_registry.json` (204 rows) |
| Kanban | `docs/planning/kanban_plan.md` |

---

## Validation

No model calls or scorer changes for this report. Metrics traced to D1 operational defaults, pathway walkthroughs, model suite synthesis, and inspection docs dated 2026-05-23/24. S5 Qwen configs scaffolded 2026-05-24 (L1.1); run pending.

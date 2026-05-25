# Clinical Extraction Kanban Plan

**Active steering doc** — what to work on next. Run IDs, inspection tables, and frozen tracks: pathway walkthroughs, experiment inspections, and [kanban_frozen_threads_history.md](kanban_frozen_threads_history.md).

**Last refreshed:** 2026-05-25

## Steering References

| Purpose | Source |
| --- | --- |
| Research direction | [outline.md](../outline.md) |
| Hybrid doctrine | [hybrid_pipeline_research_pivot_20260521.md](../workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md) |
| Local-model gap (P0 rationale) | [24h_progress_and_local_model_gap_review_20260524.md](../experiments/synthesis/24h_progress_and_local_model_gap_review_20260524.md) |
| Paper defaults & rejects | [paper_frozen_operational_defaults_20260524.md](../experiments/synthesis/paper_frozen_operational_defaults_20260524.md), [paper_frozen_arm_reject_table_20260524.md](../experiments/synthesis/paper_frozen_arm_reject_table_20260524.md) |
| Paper narrative & critique | [paper_narrative_current_20260524.md](../experiments/synthesis/paper_narrative_current_20260524.md), [paper_narrative_critical_review_20260524.md](../experiments/synthesis/paper_narrative_critical_review_20260524.md), [paper_manuscript_draft_20260524.md](../experiments/synthesis/paper_manuscript_draft_20260524.md) — writing guidance only; metric authority remains primary run artifacts and frozen defaults |
| Dataset audits | [exect_gold_label_audit.md](../datasets/exect/exect_gold_label_audit.md), [gan_2026_label_audit.md](../datasets/gan/gan_2026_label_audit.md) |

---

## Current Priorities

1. **Local model transfer (P0).** S5 Qwen true-v2b transfer is accepted (near-parity, not Qwen-leading); next local gap is the newly promoted **S2/S3 clean ladder**. Target: replay the GPT-confirmed middle-rung stacks on Qwen3.6:35b without overlapping local Ollama jobs.
2. **Clean schema ladder comparison (P1).** S2/S3 now incorporate transferable S5 lessons (AM non-ASM/brand guard) plus middle-rung guards (I0 investigation, C0/C1 comorbidity, K0/K1 cause). Keep rejected or frequency-only S5 techniques out of S2/S3.
3. **S5 decomposition ceiling (P2).** **Closed (arm reject).** Per-family parallel cap-25: 83.6% micro (−4.6pp vs v2b), ~14× slower — single-pass v2b remains quality/efficiency anchor. See [C-track inspection](../experiments/exect/exect_s5_per_family_parallel_ceiling_gpt_cap25_v1_inspection_20260524.md).

S5 frequency v2b is **promoted** (73.9% freq F1, 85.8% micro). Further frequency work only via **preregistered verifier/policy tuning** — not candidate narrowing or v1.3+strict-qualitative stacking.

---

## Recent Context (2026-05-23 → 2026-05-25)

Pathways **A–E closed**; paper evidence frozen (D1–D3); workflow readiness complete (provider smoke ledger, Qwen context policy). Gan S0 mechanism search **frozen** at builder-gap v1 (80.6% monthly GPT / 70.7% Qwen). **L1.1/L1.2 complete after true v2b rerun**: Qwen3.6:35b on S5 v2b stack is near-parity with GPT (85.4% vs 85.8% micro F1), while seizure-frequency F1 trails GPT (71.4% vs 73.9%).

| Outcome | Headline |
| --- | --- |
| ExECT S5 frequency | v2b verifier promoted (+1.6pp freq F1 vs v1, recall flat 79.1%). Combined v2 and high-precision pruning **rejected** (recall loss). |
| ExECT S5 medication | AM brand/non-ASM guard promoted (88.7% F1). Temporal evidence guard **rejected** (−20.7pp recall cap-25). |
| Gan S0 | Pathway C complete; unknown-overuse and GEPA G1/G2 **rejected**. See [Thread G](kanban_frozen_threads_history.md#thread-g---gan-s0-pathway-c-frozen-2026-05-24). |
| S1 family-split probes | PG1/PG2/g3 all below monolithic S1 on cap-25 — **arm rejects**; not a spec for C-track. |
| S5 per-family parallel (C-track) | 83.6% micro vs 88.2% v2b single-pass cap-25 — **arm reject**; seizure_type −11.9pp; ~14× latency. |
| **L1.1/L1.2 S5 Qwen true-v2b full-validation** | 85.4% micro F1 (−0.4pp vs GPT v2b). Freq F1 **71.4%** (−2.5pp). Diagnosis +2.5pp. Seizure type −1.5pp. Evidence support 95.5% raw / 100% post-repair. **Accepted local transfer / near-parity — not Qwen-leading.** |
| **S2/S3 clean-ladder GPT completion** | Transferable S5 AM guard integrated into S2/S3; frequency-only/rejected S5 techniques excluded. GPT full validation: S2 **82.7%** (+1.8pp vs frozen v1.3), S3 **74.4%** (+2.3pp vs frozen v1.2). Inspection: [S2/S3 clean ladder](../experiments/exect/exect_s2_s3_clean_ladder_gpt_validation_v1_inspection_20260525.md). |
| Local gap (prior) | G0 −9.9pp, S1 −13.3pp vs GPT on same programs; S2–S4 local competitive or leading. S5 now resolved. |

Detail: [24h review](../experiments/synthesis/24h_progress_and_local_model_gap_review_20260524.md) · [Pathway D walkthrough](../experiments/synthesis/pathway_d_paper_evidence_freeze_walkthrough_20260524.md) · [L1.2 comparison](../experiments/synthesis/l1_2_s5_local_vs_closed_comparison_20260525.md)

---

## Active Work

### L-track — Local Model Transfer

| Card | Status | Next action |
| --- | --- | --- |
| L1.1 S5 Qwen full-validation (true v2b stack) | **Done** | 85.4% micro / 71.4% freq F1 — accepted local transfer, near-parity with GPT. Run `…v2b_full_qwen35b_ollama_20260525T072245Z`. |
| L1.2 S5 local vs closed comparison | **Done** | Per-family table updated after true v2b rerun: [l1_2_comparison](../experiments/synthesis/l1_2_s5_local_vs_closed_comparison_20260525.md) |
| L1.3 S2/S3 clean-ladder Qwen replay | **Ready** | GPT clean-ladder promoted as operational rung: S2 82.7%, S3 74.4%. Run `exect_s2_clean_ladder_v1_full_qwen35b_ollama.json` and `exect_s3_clean_ladder_v1_full_qwen35b_ollama.json` detached/external PowerShell **after the current local Qwen S5 job is clear**. Away-run queue available: `scripts/run_exect_qwen35b_s1_s5_ladder_today.ps1`. |
| L2 G0 Qwen error forensics | Backlog | 87 monthly mismatches on builder-gap v1 |
| L3 S1 Qwen seizure-type arm | Backlog | v4_12 configs exist; verify full-validation run |
| L4 Best-closed S4/S5 anchors | Backlog | GPT 5.5 S4; closed S5 suite untested |

### S2/S3 Clean Schema Ladder (GPT complete)

| Card | Status | Next action |
| --- | --- | --- |
| M1 S2 clean-ladder GPT validation | **Done** | Run `exect_s2_clean_ladder_v1_full_gpt4_1_mini_20260525T073213Z`: 82.7% micro, 92.9% medication, 93.1% investigation, 72.5% comorbidity. |
| M2 S3 clean-ladder GPT validation | **Done** | Run `exect_s3_clean_ladder_v1_full_gpt4_1_mini_20260525T073224Z`: 74.4% micro, 89.5% medication, 93.1% investigation, 22.2% cause. |
| M3 S5 technique transfer audit | **Done** | Integrated transferable AM guard; kept frequency pre-vocab/verifier, high-precision pruning, temporal medication guard, and per-family parallel out of S2/S3 because they are frequency-only or rejected. |
| M4 Qwen middle-rung replay | **Ready** | Depends on no local Ollama contention. Use L1.3 configs and compare against GPT clean-ladder plus prior Qwen S2/S3 anchors. |

### C-track — S5 Decomposition Ceiling (GPT only)

Fresh implementation on S5 core surface. **Do not replay** S1 family-split arms — negative probes only.

| Card | Status | Next action |
| --- | --- | --- |
| C1.2 Cap-25 gate + inspection | **Done** | [inspection](../experiments/exect/exect_s5_per_family_parallel_ceiling_gpt_cap25_v1_inspection_20260524.md) — run `exect_s5_core_field_family_parallel_v2b_cap25_gpt4_1_mini_20260524T212052Z`; **arm reject** |
| C1.3 Full validation vs single-pass | **Skipped** | Cap-25 gates failed |
| C1.4 Quality/efficiency synthesis | **Done** | Ceiling summary in inspection doc |

Prereg: [exect_s5_per_family_parallel_ceiling_gpt_cap25_v1_preregistration_20260524.md](../experiments/exect/exect_s5_per_family_parallel_ceiling_gpt_cap25_v1_preregistration_20260524.md)

### S5 Frequency — Next Iteration (gated)

v2b promoted to D1. Residual audit complete. Pull next arm only with prereg + cap-25 gates.

| Gate | Condition |
| --- | --- |
| New verifier/policy arm | Prereg + cap-25; high-recall candidate baseline preserved |
| Out of scope | Candidate narrowing; v1.3 abstention + strict qualitative guard stacking |

Artifacts: [residual audit](../experiments/exect/exect_s5_frequency_post_promotion_residual_audit_20260524.md) · [v2b promotion review](../experiments/exect/exect_s5_frequency_verifier_v2b_full_validation_promotion_review_20260524.md)

---

## Operational Defaults

Authoritative numbers: [paper_frozen_operational_defaults_20260524.md](../experiments/synthesis/paper_frozen_operational_defaults_20260524.md).

| Track | Default | Headline | Qwen3.6:35b | Caveat |
| --- | --- | --- | --- | --- |
| Gan S0 | builder-gap v1 / GPT 4.1-mini | 80.6% monthly | 70.7% monthly | Synthetic validation only |
| ExECT S1–S4 | Clean GPT ladder | S1 92.3% → S2 82.7% → S3 74.4% → S4 65.5% micro | S1 79.0%, S2/S3 clean-ladder Qwen pending, S4 67.5% | S2/S3 use transferable S5 guard lessons; S1 seizure_type gap remains |
| ExECT S5 | pre-vocab + AM guard + v2b freq / GPT | 85.8% micro; freq 73.9% F1 | **85.4% micro; freq 71.4% F1** | Accepted local transfer; Qwen frequency trails GPT |

---

## Gates & Deferred Work

| Item | Release condition |
| --- | --- |
| S5 local deployment claims | **Use cautious wording** — true v2b Qwen full-validation complete (85.4% micro near-parity); synthetic validation only, not deployment readiness |
| ExECTv2 Table 1 reproduction | CUI-aware scorer + explicit reproduction workstream |
| Gan Real(300)/Real(150) | Dataset access + preregistered reporting plan |
| Gan S0 / GEPA arms | Frozen; prereg + cap-25 gate ([Thread G](kanban_frozen_threads_history.md#thread-g---gan-s0-pathway-c-frozen-2026-05-24)) |
| Test/holdout reporting | Explicit protocol (D4 backlog) |

**Deferred follow-ons** (not active): Gan builder extension for no-candidate mismatches; Gan multi-type/window-priority prompts; C-track beyond C1 if P0 clears.

---

## Standing Guardrails

- Do not silently change scorer semantics; update tests and document interpretation.
- Gan gold is `seizure_frequency_number[0]`; `reference[0]` is diagnostic only.
- Distinguish `unknown` from `no seizure frequency reference`.
- Keep arm rejection separate from mechanism rejection; name `decision_scope` in inspection docs.
- ExECT S5 families: diagnosis, seizure type, annotated medication, investigation, seizure frequency.
- High-recall ExECT frequency candidates remain baseline; high-precision pruning is rejected.
- S2/S3 clean-ladder ports should include only transferable promoted S5 techniques; do not port frequency-only or rejected S5 mechanisms into rungs without those fields.
- Do not overlap S2/S3 Qwen replay with an active local Qwen S5 or Gan job on the same Ollama instance.
- Cursor SDK drafts are leads, not evidence, until promoted from primary artifacts.

# Component Ceiling Registry

Status: component ceiling registry
Last updated: 2026-05-28
Scope: current Gan S0 and ExECT decomposition status

This registry is the compact current map. It is not a full run registry. Use it
to decide what is active, what is historical evidence, and what must not be
repeated without a new preregistration.

## Gan S0

Current question: can seizure-frequency extraction be decomposed into candidate
inventory, temporal anchoring, target selection, label construction, and
unknown/no-reference policy before another broad prompt pass?

| Component | Status | Current evidence | Next action |
| --- | --- | --- | --- |
| Paper-comparison surface | blocked / benchmark-facing | Direct Gan paper comparison now requires `gan2026_paper_reproduction`; current headline rows mostly used `gan_frequency_deterministic_v1`. | Rescore current baselines before benchmark-comparison tables. |
| Synthetic operational default | promoted baseline | Builder-gap v1 GPT: 80.6% monthly canonical validation; Qwen: 70.7%. | Keep as synthetic paper-default baseline until rescored or explicitly superseded. |
| Mechanism baseline | operational default | D1 v1.2b schema guard only: 79.9% monthly, within 0.7pp of builder-gap v1 and more decomposed. | Use for mechanism experiments. |
| Candidate inventory | mechanism open | Builder-gap v1 and D1 show value, but inventory recall/strata coverage are not yet a first-class ceiling report. | Audit candidate coverage by label family and hard strata. |
| Temporal anchoring | mechanism open | R11 D1 won; R15 showed arithmetic injection and broad relative-anchor guardrails regress. | Keep arithmetic diagnostic-only until parser is seizure-specific. |
| Scope and target selection | mechanism open | Still bundled inside the final adjudicator. | Create residual strata for current/historical, multi-type, seizure-free conflict, and highest-current selection. |
| Label construction and aggregation | mechanism open | Scorer normalization is post-prediction; label construction remains largely LLM-bundled. | Test label-construction helpers separately from target selection. |
| Unknown vs no-reference policy | mechanism open | Canonical scorer separates them; paper reproduction collapses special classes differently. | Keep benchmark and clinical scorer modes separated in every report. |
| Evidence and schema | diagnostic only | High schema/evidence rates often coexist with wrong frequency labels. | Keep as gates and diagnostics, not proof of semantic correctness. |
| CLINES-style entity-first | rejected arm | R12 C1 caused severe context loss: GPT 20.8%, Qwen 12.0% monthly on cap-25. | Do not rerun same entity-first interface. Mechanism only reopens with preserved global context. |
| Self-consistency | rejected arm | R13 repeated sampling gave 0.0pp gain and 0% variance at temperature 0.7. | Do not spend 5x compute on Gan S0 self-consistency without a new instability hypothesis. |
| GEPA / optimizers | blocked | R14 requires compact-delta gate before Qwen GEPA. | No new Qwen GEPA until hosted compact-delta gate clears. |

Primary current docs:

- `experiments/gan/gan_s0_pipeline_decomposition_deep_dive_20260528.md`
- `experiments/gan/gan_s0_r11_temporal_date_stage_decision_20260528.md`
- `experiments/gan/gan_s0_r12_clines_entity_first_pipeline_gate_decision_20260528.md`
- `experiments/gan/gan_s0_r13_self_consistency_variance_probe_decision_20260528.md`
- `experiments/gan/gan_s0_r15_d1_guardrail_ablation_decision_20260528.md`
- `datasets/gan/gan_2026_label_audit.md`
- `policies/deterministic_scorer_semantics.md`

## ExECT

Current question: what are the isolated family ceilings and what interference
appears when optimized components are stacked?

| Component | Status | Current evidence | Next action |
| --- | --- | --- | --- |
| Clean ladder S1-S4 | diagnostic baseline | Shows schema breadth pressure, but not component ceilings. | Treat as unoptimized complexity stress test. |
| S5 core surface | promoted baseline | GPT v2b 85.8% micro / 73.9% frequency F1; Qwen 85.4% / 71.4% on validation. | Keep as current stacked baseline, not proof of optimal decomposition. |
| Holdout transfer | active risk | S1 GPT 92.3 -> 77.8 micro; S5 GPT frequency 73.9 -> 47.1 F1. | Run residual/causal split analysis; do not tune from holdout. |
| Frequency event/rate payload | coverage gate passed / adjudication open | E1 audit covers 43/43 validation gold labels, including quantified, qualitative, seizure-free, zero-rate, type-associated, temporal-scope, and multi-label cases; broad payload precision is only 22.2% with 151 extra candidates. | Split candidate selection/adjudication from label construction before model-backed stack work. |
| S1 raw/bridge/prompt split | mechanism open | Validation strong, holdout diagnosis/seizure-type weak; prompt and bridge effects are entangled. | Separate raw extraction, bridge-only, prompt-policy, and combined effects. |
| Medication current-Rx | likely high ceiling | S1 medication transfers well; S5 broad stack damages medication via over-emission/interference. | Build medication mention/current-Rx payload and benchmark bridge. |
| Medication lifecycle / temporality | mechanism open | Broad temporal guard arms collapsed recall; prescription gold lacks clean temporality column. | Build lifecycle table first, then decide benchmark-facing vs diagnostic target. |
| Family-span payload | mechanism open | Section-aware prompt routing failed as an arm; typed family spans remain untested. | Implement family-span/list payload with evidence coverage audit. |
| Investigation | likely near ceiling, unproven | High and stable in broad stacks and holdout, but isolated ceiling is not measured. | Confirm with isolated component run before calling solved. |
| Comorbidity / sparse S3 families | mechanism open | Weak and support-sensitive; broad ladder does not isolate causes. | Require support counts and family contract before new tuning. |
| Per-family parallel S5 | rejected arm | One parallel implementation regressed; it does not reject family-first decomposition. | Do not rerun same interface; reopen only with component substrates. |
| CUI-aware Table 1 reproduction | blocked | Current scorers are project field-family scorers, not full published benchmark reproduction. | Build CUI-aware all-family scorer before external ExECT comparison. |

Primary current docs:

- `experiments/exect/exect_task_deep_review_20260528.md`
- `experiments/exect/exect_frequency_event_rate_payload_audit_20260528.md`
- `experiments/synthesis/test_holdout_evaluation_report_20260527.md`
- `experiments/synthesis/paper_result_table_pack_20260525.md`
- `datasets/exect/exect_gold_label_audit.md`
- `policies/deterministic_scorer_semantics.md`
- `policies/published_benchmark_metrics.md`

## Registry Rules

- A component without an isolated ceiling is `mechanism open`, not solved.
- A failed config is a `rejected arm` unless a mechanism review explicitly closes
  the class.
- A promoted stacked baseline is allowed to be useful and still not be the
  research target.
- Holdout metrics can trigger analysis but must not drive tuning.

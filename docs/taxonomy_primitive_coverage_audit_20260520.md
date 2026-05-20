# Taxonomy Primitive Coverage Audit

Date: 2026-05-20  
Status: Card 23 audit complete  
Related: `docs/taxonomy_primitives_workstream_plan_20260520.md`, `docs/taxonomy_primitive_catalog.md`, `docs/exect_negative_probe_synthesis_20260520.md`, `docs/experiment_registry.json`, `docs/gan_2026_label_audit.md`, `docs/exect_gold_label_audit.md`

## Purpose

Classify typed taxonomy primitives by their current research role after the closed Gan and ExECT experiment batch. This audit does not change primitive behavior or registry metadata. It separates implementation status from evidence status so later experiments do not treat an implemented primitive as a promoted intervention by default.

Classification values:

- `promoted`: supported by a model-backed comparison group as part of the current default or case-study narrative.
- `diagnostic_only`: useful for measurement, fixtures, reporting, or bridge-contribution analysis, but not a new promoted prediction path.
- `rejected_for_current_arm`: implemented or tested, but the current experimental arm shape should not be rerun or promoted.
- `planned`: metadata/design exists, but no implementation or model-backed decision yet.
- `blocked`: blocked by external data or benchmark-reproduction infrastructure.

## Coverage Summary

| Primitive ID | Evidence status | Evidence anchor | Notes |
| --- | --- | --- | --- |
| `gan.frequency.temporal_candidates.v1` | `promoted` | Gan temporal-candidates full validations: Qwen `...230324Z`, GPT `...130933Z`; see `docs/kanban_plan.md` | Default Gan S0 architecture uses deterministic temporal preconditioning plus LLM adjudication. Do not transfer monthly normalization directly to ExECT. |
| `gan.frequency.verify_repair_policy.v1` | `promoted` | Gan temporal-candidates verify-repair narrative in `docs/kanban_plan.md` | Promoted as part of Gan default when paired with temporal candidates. Local Qwen verifier-only variants remain caveated by slice regressions. |
| `gan.frequency.label_policy_bridge.v1` | `diagnostic_only` | Gan scorer/audit policy; `docs/gan_2026_label_audit.md` | Scorer-facing bridge preserves raw, benchmark-facing, monthly, Purist, and Pragmatic values; not itself a new prediction arm. |
| `gan.frequency.evidence_guard.v1` | `diagnostic_only` | Gan evidence-support reporting in promoted runs | Evidence support is required for interpretation, but guard behavior is not a standalone promoted intervention unless a decision doc makes it prediction-affecting. |
| `gan.frequency.temporal_tool.v1` | `rejected_for_current_arm` | Gan ReAct temporal-tools H3 slice `...173943Z`; `docs/kanban_plan.md` | Tool-during ReAct did not replace preconditioning; keep as negative control, not default path. |
| `shared.evidence.substring_support.v1` | `diagnostic_only` | Primitive fixtures and evidence-support metrics | Exact quote support can validate raw evidence presence without validating normalized clinical interpretation. |
| `shared.evidence.verified_quote.v1` | `planned` | Catalog and registry metadata | Planned verifier/evidence guard. Needs a comparison group before prediction-affecting use. |
| `shared.fixtures.primitive_cases.v1` | `diagnostic_only` | `data/fixtures/primitive_cases.json`; primitive validation | No-model fixture infrastructure. Supports validation, not model-backed claims. |
| `shared.reporting.primitive_inspection.v1` | `diagnostic_only` | `docs/templates/primitive_inspection_template.md`, `docs/templates/experiment_decision_template.md` | Reporting infrastructure for traceability. |
| `exect.medication.benchmark_bridge.v1` | `diagnostic_only` | S1 interleaving GPT v2 and Qwen v1 inspection docs | Part of frozen S1 benchmark-policy bridge path. H1 post-bridge arms are diagnostic/null vs production, not new interventions. |
| `exect.seizure_type.benchmark_bridge.v1` | `diagnostic_only` | S1 interleaving GPT v2 and Qwen v1 inspection docs | Quantifies large bridge contribution, but Qwen seizure gap persists after bridging. Next work should diagnose model/prompt policy. |
| `exect.diagnosis.benchmark_bridge.v1` | `diagnostic_only` | S1 interleaving GPT v2 and Qwen v1 inspection docs | Near-ceiling GPT and strong Qwen diagnosis performance; bridge remains scorer-policy infrastructure. |
| `exect.medication.rx_candidates.v1` | `rejected_for_current_arm` | `docs/exect_s1_medication_pre_vocab_slice_gpt_inspection_20260520.md` | Medication-only H2 slice regressed medication F1 98.3% to 95.1%. Keep for fixtures or redesigned arms, not current H2 promotion. |
| `exect.frequency.rate_candidates.v1` | `rejected_for_current_arm` | `docs/exect_s4_frequency_deterministic_gpt_inspection_20260520.md` | S4 cap-25 H2 pre-candidates regressed seizure_frequency F1 49.1% to 47.1%. Requires a new presentation or repair mechanism before reuse. |
| `exect.frequency.benchmark_bridge.v1` | `diagnostic_only` | S4 frequency support-map inventory; frequency H2 inspection | Existing bridge policy is infrastructure around ExECT frequency surfaces; not a promoted new arm. |
| `exect.medication_temporality.post_classifier.v1` | `rejected_for_current_arm` | `docs/exect_s4_temporality_deterministic_gpt_inspection_20260520.md`; `docs/exect_s4_temporality_planned_taper_error_read_20260520.md` | Full-validation H1 rejected: +10.1pp precision but -6.6pp F1 from recall collapse. A narrower dose-only fallback would be a new mechanism. |
| `exect.sections.family_spans.v1` | `planned` | Registry/catalog metadata | Section filtering has no current promotion evidence; preserve full-note baselines. |
| `exect.investigation.surface_bridge.v1` | `planned` | Broad ExECT family backlog | Planned sparse-family metadata only. |
| `exect.investigation.planned_scan_guard.v1` | `planned` | Broad ExECT family backlog | Planned sparse-family metadata only. |
| `exect.comorbidity.overlap_policy.v1` | `planned` | Broad ExECT family backlog | Planned sparse-family metadata only. |
| `exect.birth_development.cui_phrase_bridge.v1` | `planned` | Broad ExECT family backlog | CUI/phrase work deferred until benchmark-reproduction scope is reopened. |
| `exect.onset.cui_phrase_bridge.v1` | `planned` | Broad ExECT family backlog | CUI/phrase work deferred until benchmark-reproduction scope is reopened. |
| `exect.epilepsy_cause.cui_phrase_bridge.v1` | `planned` | Broad ExECT family backlog | CUI/phrase work deferred until benchmark-reproduction scope is reopened. |
| `exect.when_diagnosed.cui_phrase_bridge.v1` | `planned` | Broad ExECT family backlog | CUI/phrase work deferred until benchmark-reproduction scope is reopened. |
| `exect.family_history.cui_phrase_bridge.v1` | `planned` | Broad ExECT family backlog | Planned sparse-family metadata only. |
| `exect.social_history.cui_phrase_bridge.v1` | `planned` | Broad ExECT family backlog | Planned sparse-family metadata only. |
| `exect.driving.cui_phrase_bridge.v1` | `planned` | Broad ExECT family backlog | Planned sparse-family metadata only. |
| `exect.pregnancy.cui_phrase_bridge.v1` | `planned` | Broad ExECT family backlog | Planned sparse-family metadata only. |
| `exect.ontology.cui_alignment.v1` | `blocked` | `docs/taxonomy_ontology_cui_scope_decision_20260520.md` | Blocked/deferred until published ExECT benchmark reproduction needs ontology-aligned scoring and primitives. |
| `gan.frequency.real_set_validation.v1` | `blocked` | `docs/kanban_plan.md`; `docs/taxonomy_primitives_workstream_plan_20260520.md` | Blocked on Gan Real(300)/Real(150)-style data access. |

## Interpretation

Gan has the only currently promoted deterministic intervention: temporal candidates plus verify-repair for S0 seizure frequency. The negative ReAct H3 result is useful because it narrows the Gan mechanism claim: deterministic temporal knowledge helped when precomputed and injected before adjudication, not when exposed as a tool-during reasoning substitute.

ExECT primitives are mostly infrastructure, diagnostics, or rejected current-arm interventions. S1 benchmark bridges remain necessary for current local diagnostic scoring, but the H1 post-bridge comparisons were null against production anchors. S1 and S4 H2 pre-candidate arms should not be reopened without a new mechanism because medication, seizure_type, and seizure_frequency all regressed on their primary family metrics.

The S4 medication-temporality post classifier is the clearest example of a useful but rejected primitive. It removed false positives, but the full-validation abstention policy over-pruned dose-only current ASM evidence. The next plausible medication-temporality mechanism would need a new preregistered fallback policy, not a broad rerun.

## Catalog Alignment Needed Next

Card 24 should update `docs/taxonomy_primitive_catalog.md` so the `Status` column or caveats distinguish registry implementation status from evidence status. The catalog should make the following especially visible:

- Gan temporal candidates and verify-repair are promoted only for Gan S0 synthetic validation under fixed scorer semantics.
- ExECT S1 benchmark bridges are diagnostic infrastructure, not a newly promoted H1 intervention.
- ExECT medication, seizure, and frequency pre-candidate primitives are rejected for the tested H2 arm shapes.
- ExECT medication-temporality post-classifier is rejected for the broad abstention policy, with a possible future dose-only fallback as a new mechanism.
- CUI/ontology and Gan real-set primitives remain blocked/deferred by external benchmark-reproduction constraints.

## Validation

Command run:

```powershell
uv run python scripts/validate_primitives.py --errors-only
```

Result: no validation errors. Existing warnings remain about adapter-extended interleaving positions for `gan.frequency.temporal_candidates.v1`, `exect.medication.rx_candidates.v1`, and `exect.medication.benchmark_bridge.v1`.

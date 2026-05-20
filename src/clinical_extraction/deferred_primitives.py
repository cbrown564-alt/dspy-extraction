"""Deferred and catalog-only primitive metadata not yet in a family pack."""

from __future__ import annotations

from clinical_extraction.primitives import PrimitiveMetadata

DEFERRED_CATALOG_PRIMITIVES: tuple[PrimitiveMetadata, ...] = (
    PrimitiveMetadata(
        primitive_id="gan.frequency.verify_repair_policy.v1",
        name="Gan frequency verify-repair policy",
        dataset="gan_2026",
        field_families=["frequency"],
        clinical_operation="verification",
        knowledge_sources=["temporal_rules", "benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post"],
        control_modes=["posthoc_correction"],
        input_contract="Initial Gan frequency prediction plus note text.",
        output_contract="Verified or repaired frequency label with second-pass policy metadata.",
        compatible_experiment_arms=["H1"],
        status="implemented",
        caveats=[
            "Hosted GPT benefited from verify-repair; local Qwen verifier damaged some correct temporal labels.",
            "Superseded as default path by temporal-candidates for hosted promotion.",
        ],
        implementation_refs=["src/clinical_extraction/programs/gan_frequency_s0.py"],
    ),
    PrimitiveMetadata(
        primitive_id="gan.frequency.temporal_tool.v1",
        name="Gan temporal tool interface",
        dataset="gan_2026",
        field_families=["frequency"],
        clinical_operation="tool_interface",
        knowledge_sources=["temporal_rules", "temporal_tooling", "gold_audit_policy"],
        hybrid_balance_class=["H3_interleaved_tool_hybrid"],
        interleaving_positions=["tool_during", "during"],
        control_modes=["tool_affordance", "soft_hint"],
        input_contract="Gan note text exposed through bounded ReAct temporal tools.",
        output_contract="Tool-during temporal candidate or normalization lookup results.",
        compatible_experiment_arms=["H3"],
        status="implemented",
        caveats=[
            "Gan ReAct H3 probe rejected; do not make tool-during the default path.",
            "Pre-injected candidates beat tool-during reasoning on the regression slice.",
        ],
        implementation_refs=[
            "src/clinical_extraction/gan/react_tools.py",
            "src/clinical_extraction/programs/gan_frequency_s0.py",
        ],
    ),
    PrimitiveMetadata(
        primitive_id="shared.reporting.primitive_inspection.v1",
        name="Primitive inspection reporting templates",
        dataset="shared",
        field_families=["multi_family"],
        clinical_operation="inspection_reporting",
        knowledge_sources=["manual_examples", "gold_audit_policy"],
        hybrid_balance_class=["D1_deterministic_only"],
        interleaving_positions=["eval_only"],
        control_modes=["diagnostic_only"],
        input_contract="Experiment run metadata, primitive IDs, and inspection findings.",
        output_contract=(
            "Structured inspection or decision documents with required taxonomy sections."
        ),
        compatible_experiment_arms=["D1"],
        status="implemented",
        caveats=[
            "Templates are inspection surfaces, not prediction-affecting primitives.",
        ],
        implementation_refs=[
            "docs/templates/primitive_inspection_template.md",
            "docs/templates/experiment_decision_template.md",
            "src/clinical_extraction/experiments/inspection_templates.py",
        ],
    ),
    PrimitiveMetadata(
        primitive_id="shared.evidence.verified_quote.v1",
        name="Verified quote evidence guard",
        dataset="shared",
        field_families=["multi_family"],
        clinical_operation="evidence_support",
        knowledge_sources=["regex_rules", "diagnostic_metric", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post"],
        control_modes=["posthoc_correction"],
        input_contract="Note text, model quote, and field prediction.",
        output_contract=(
            "Prediction retained, repaired, or flagged when quote support fails."
        ),
        compatible_experiment_arms=["H1"],
        status="planned",
        caveats=[
            "Must distinguish unsupported quotes from no-reference cases.",
        ],
    ),
    PrimitiveMetadata(
        primitive_id="exect.ontology.cui_alignment.v1",
        name="ExECT CUI ontology alignment",
        dataset="exect_v2",
        field_families=["multi_family"],
        clinical_operation="benchmark_bridge",
        knowledge_sources=["cui_or_ontology", "benchmark_label_policy", "gold_audit_policy"],
        hybrid_balance_class=["H1_post_deterministic", "D1_deterministic_only"],
        interleaving_positions=["post", "eval_only"],
        control_modes=["posthoc_correction", "diagnostic_only"],
        input_contract="Raw prediction surfaces plus CUI or ontology lookup context.",
        output_contract="CUI-aware benchmark-facing labels for published Table 1 reproduction.",
        compatible_experiment_arms=["H1", "D1"],
        status="planned",
        caveats=[
            "Deferred until published ExECT benchmark reproduction is explicitly in scope.",
            "Do not mix CUI-aware reproduction with local field-family diagnostics unless the comparison group says so.",
        ],
        implementation_refs=["docs/taxonomy_ontology_cui_scope_decision_20260520.md"],
    ),
    PrimitiveMetadata(
        primitive_id="gan.frequency.real_set_validation.v1",
        name="Gan real-set primitive validation",
        dataset="gan_2026",
        field_families=["frequency"],
        clinical_operation="inspection_reporting",
        knowledge_sources=["gold_audit_policy", "diagnostic_metric"],
        hybrid_balance_class=["D1_deterministic_only"],
        interleaving_positions=["eval_only"],
        control_modes=["diagnostic_only"],
        input_contract="Gan frequency primitives evaluated on Real(300)/Real(150)-style data.",
        output_contract="Reproduction-compatible validation and inspection artifacts.",
        compatible_experiment_arms=["D1"],
        status="planned",
        caveats=[
            "Blocked on access to Real(300)/Real(150)-style evaluation data.",
        ],
    ),
)

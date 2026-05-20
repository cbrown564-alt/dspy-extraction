from __future__ import annotations

import pytest
from pydantic import ValidationError

from clinical_extraction.primitives import (
    EvidenceSupportResult,
    NormalizationResult,
    PrimitiveCandidate,
    PRIMITIVE_REGISTRY,
    PrimitiveMetadata,
    check_evidence_support,
    primitive_registry_by_id,
)


def test_seed_primitive_registry_has_unique_ids():
    ids = [primitive.primitive_id for primitive in PRIMITIVE_REGISTRY]
    assert len(ids) == len(set(ids))
    assert {
        "gan.frequency.temporal_candidates.v1",
        "exect.medication.benchmark_bridge.v1",
        "shared.evidence.substring_support.v1",
    }.issubset(ids)


def test_seed_primitive_registry_lookup_by_id():
    registry = primitive_registry_by_id()
    assert registry["exect.medication.benchmark_bridge.v1"].normalization_scope == (
        "benchmark_bridge"
    )


def test_gan_frequency_primitive_metadata_validates():
    primitive = PrimitiveMetadata(
        primitive_id="gan.frequency.temporal_candidates.v1",
        name="Gan temporal frequency candidates",
        dataset="gan_2026",
        field_families=["frequency"],
        clinical_operation="candidate_generation",
        knowledge_sources=["temporal_rules", "regex_rules", "gold_audit_policy"],
        hybrid_balance_class=["H2_pre_deterministic", "H4_deterministic_first_llm_adjudicates"],
        interleaving_positions=["pre"],
        control_modes=["soft_hint"],
        input_contract="Gan note text plus optional document metadata.",
        output_contract="Temporal seizure-frequency candidates with raw spans and benchmark caveats.",
        compatible_experiment_arms=["H2", "H4"],
        status="implemented",
        caveats=[
            "Gan seizure_frequency_number[0] remains the benchmark-facing gold label.",
            "Monthly normalization is separate from ExECT frequency policy.",
        ],
    )

    assert primitive.dataset == "gan_2026"
    assert primitive.field_families == ["frequency"]
    assert primitive.is_prediction_affecting


def test_exect_medication_primitive_metadata_validates():
    primitive = PrimitiveMetadata(
        primitive_id="exect.medication.benchmark_bridge.v1",
        name="ExECT medication benchmark bridge",
        dataset="exect_v2",
        field_families=["medication"],
        clinical_operation="normalization",
        knowledge_sources=["controlled_vocabulary", "benchmark_label_policy"],
        hybrid_balance_class=["H1_post_deterministic"],
        interleaving_positions=["post"],
        control_modes=["posthoc_correction"],
        input_contract="Raw medication predictions with evidence quotes.",
        output_contract="Raw, canonical, benchmark-facing, and caveated medication values.",
        compatible_experiment_arms=["H1"],
        status="planned",
        caveats=["Do not reintroduce broad pre-vocabulary prompting as the default S1 medication path."],
    )

    assert primitive.clinical_operation == "normalization"
    assert primitive.normalization_scope == "benchmark_bridge"


def test_evidence_diagnostic_primitive_metadata_validates():
    primitive = PrimitiveMetadata(
        primitive_id="shared.evidence.substring_support.v1",
        name="Deterministic substring evidence support",
        dataset="shared",
        field_families=["multi_family"],
        clinical_operation="evidence_support",
        knowledge_sources=["regex_rules", "diagnostic_metric"],
        hybrid_balance_class=["D1_deterministic_only"],
        interleaving_positions=["eval_only"],
        control_modes=["diagnostic_only"],
        input_contract="Note text plus model quote or deterministic evidence candidate.",
        output_contract="Supported, unsupported, no-reference, or normalized-interpretation support result.",
        compatible_experiment_arms=["D1"],
        status="planned",
    )

    assert not primitive.is_prediction_affecting


def test_primitive_metadata_rejects_empty_contract_text():
    with pytest.raises(ValidationError, match="input_contract must be a non-empty string"):
        PrimitiveMetadata(
            primitive_id="bad.empty.input.v1",
            name="Bad empty input",
            dataset="shared",
            field_families=["multi_family"],
            clinical_operation="evidence_support",
            knowledge_sources=["diagnostic_metric"],
            hybrid_balance_class=["D1_deterministic_only"],
            interleaving_positions=["eval_only"],
            control_modes=["diagnostic_only"],
            input_contract=" ",
            output_contract="Some output.",
            compatible_experiment_arms=["D1"],
        )


def test_primitive_metadata_rejects_posthoc_correction_without_post_position():
    with pytest.raises(ValidationError, match="posthoc_correction requires post interleaving"):
        PrimitiveMetadata(
            primitive_id="bad.posthoc.position.v1",
            name="Bad posthoc position",
            dataset="exect_v2",
            field_families=["medication"],
            clinical_operation="normalization",
            knowledge_sources=["benchmark_label_policy"],
            hybrid_balance_class=["H1_post_deterministic"],
            interleaving_positions=["pre"],
            control_modes=["posthoc_correction"],
            input_contract="Raw medication predictions.",
            output_contract="Benchmark-facing medication predictions.",
            compatible_experiment_arms=["H1"],
        )


def test_candidate_object_round_trips_gan_frequency_example():
    candidate = PrimitiveCandidate(
        primitive_id="gan.frequency.temporal_candidates.v1",
        dataset="gan_2026",
        field_family="frequency",
        raw_text="4 clusters this quarter",
        normalized_value="4 cluster per 3 month, multiple per cluster",
        benchmark_value="4 cluster per 3 month, multiple per cluster",
        source_span_text="4 clusters this quarter",
        start=42,
        end=65,
        rule_name="clusters_this_quarter",
        confidence=1.0,
        caveats=["Gan cluster labels preserve cluster wording."],
    )

    round_tripped = PrimitiveCandidate.model_validate(candidate.model_dump())

    assert round_tripped == candidate
    assert round_tripped.source_span_text == round_tripped.raw_text
    assert round_tripped.is_benchmark_aligned


def test_candidate_object_preserves_exect_medication_policy_caveat():
    candidate = PrimitiveCandidate(
        primitive_id="exect.medication.rx_candidates.v1",
        dataset="exect_v2",
        field_family="medication",
        raw_text="lamotrigine was discussed but not started",
        normalized_value="lamotrigine",
        benchmark_value=None,
        source_span_text="lamotrigine was discussed but not started",
        rule_name="planned_or_discussed_medication",
        confidence=0.86,
        caveats=["Planned medication should not become benchmark current medication."],
    )

    assert candidate.normalized_value == "lamotrigine"
    assert candidate.benchmark_value is None
    assert not candidate.is_benchmark_aligned


def test_candidate_object_round_trips_exect_seizure_frequency_example():
    candidate = PrimitiveCandidate(
        primitive_id="exect.frequency.rate_candidates.v1",
        dataset="exect_v2",
        field_family="frequency",
        raw_text="two focal seizures each month",
        normalized_value={"count": 2, "period": "month"},
        benchmark_value="two focal seizures each month",
        source_span_text="two focal seizures each month",
        rule_name="explicit_rate_phrase",
        confidence=0.94,
        caveats=["ExECT surface templates remain separate from Gan monthly labels."],
    )

    assert PrimitiveCandidate.model_validate(candidate.model_dump()) == candidate


def test_candidate_object_rejects_partial_offsets_and_bad_confidence():
    with pytest.raises(ValidationError, match="source offsets must provide both start and end"):
        PrimitiveCandidate(
            primitive_id="gan.frequency.temporal_candidates.v1",
            dataset="gan_2026",
            field_family="frequency",
            raw_text="one seizure per month",
            source_span_text="one seizure per month",
            start=4,
            rule_name="explicit_rate",
        )

    with pytest.raises(ValidationError):
        PrimitiveCandidate(
            primitive_id="gan.frequency.temporal_candidates.v1",
            dataset="gan_2026",
            field_family="frequency",
            raw_text="one seizure per month",
            source_span_text="one seizure per month",
            rule_name="explicit_rate",
            confidence=1.5,
        )


def test_normalization_result_separates_raw_canonical_and_benchmark_values():
    result = NormalizationResult(
        primitive_id="exect.medication.benchmark_bridge.v1",
        dataset="exect_v2",
        field_family="medication",
        raw_value="Keppra",
        canonical_value="levetiracetam",
        benchmark_value="levetiracetam",
        clinical_caveat="Brand name mapped to generic benchmark surface.",
        transformation_rule="brand_to_generic",
        prediction_affecting=True,
    )

    assert result.has_changed_value
    assert result.is_benchmark_bridge
    assert result.benchmark_value == "levetiracetam"


def test_normalization_result_can_be_scorer_only_without_benchmark_value():
    result = NormalizationResult(
        primitive_id="gan.frequency.label_policy_bridge.v1",
        dataset="gan_2026",
        field_family="frequency",
        raw_value="about once monthly",
        canonical_value="1 per month",
        benchmark_value=None,
        clinical_caveat="Diagnostic monthly normalization, not a changed prediction.",
        transformation_rule="qualitative_monthly_rate",
        prediction_affecting=False,
        scorer_only=True,
    )

    assert result.has_changed_value
    assert not result.is_benchmark_bridge
    assert result.scorer_only


def test_evidence_support_distinguishes_exact_quote_support():
    result = check_evidence_support(
        document_text="She reports one seizure per month on levetiracetam.",
        quote="one seizure per month",
        normalized_value="1 per month",
    )

    assert result.support_status == "exact_substring"
    assert result.raw_quote_supported
    assert not result.normalized_interpretation_supported
    assert result.start == 12


def test_evidence_support_distinguishes_normalized_interpretation_support():
    result = check_evidence_support(
        document_text="She reports one seizure per month on levetiracetam.",
        quote="1 per month",
        normalized_value="1 per month",
        interpretation_evidence_text="one seizure per month",
    )

    assert result.support_status == "normalized_interpretation"
    assert not result.raw_quote_supported
    assert result.normalized_interpretation_supported


def test_evidence_support_distinguishes_unsupported_and_no_reference_cases():
    unsupported = check_evidence_support(
        document_text="No seizures have been documented since March.",
        quote="one seizure per month",
    )
    no_reference = check_evidence_support(
        document_text="No seizures have been documented since March.",
        quote=None,
    )

    assert unsupported.support_status == "unsupported_quote"
    assert no_reference.support_status == "no_reference"


def test_evidence_support_result_requires_consistent_flags():
    with pytest.raises(ValidationError, match="exact_substring requires raw quote support"):
        EvidenceSupportResult(
            primitive_id="shared.evidence.substring_support.v1",
            document_text="She reports one seizure per month.",
            quote="one seizure per month",
            support_status="exact_substring",
            raw_quote_supported=False,
        )

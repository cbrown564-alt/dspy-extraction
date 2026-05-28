from __future__ import annotations

from clinical_extraction.exect.seizure_type_primitives import (
    exect_seizure_type_benchmark_bridge,
)
from clinical_extraction.primitives import primitive_registry_by_id


def test_exect_seizure_type_bridge_coarsens_qwen_granular_focal_surface():
    results = exect_seizure_type_benchmark_bridge("focal impaired awareness seizure")

    assert len(results) == 1
    result = results[0]
    assert result.primitive_id == "exect.seizure_type.benchmark_bridge.v1"
    assert result.dataset == "exect_v2"
    assert result.field_family == "seizure_type"
    assert result.canonical_value == "focal impaired awareness seizure"
    assert result.benchmark_value == "focal seizure"
    assert result.transformation_rule == "exect_seizure_type_granularity_coarsening"
    assert "benchmark_bridge:granular_seizure_surface_coarsened" in (
        result.metadata["bridge_flags"]
    )


def test_exect_seizure_type_bridge_splits_fused_temporal_lobe_phrase():
    results = exect_seizure_type_benchmark_bridge(
        "temporal lobe onset focal seizures"
    )

    assert [result.benchmark_value for result in results] == [
        "temporal lobe seizure",
        "focal seizures",
    ]
    assert all(
        result.transformation_rule == "exect_seizure_type_fused_phrase_split"
        for result in results
    )


def test_exect_seizure_type_bridge_maps_secondary_phrase_without_frequency_spans():
    results = exect_seizure_type_benchmark_bridge(
        "secondary generalised seizures",
        note_text="Seizure type: secondary generalised seizures.",
    )

    assert [result.benchmark_value for result in results] == [
        "secondary generalized seizures",
        "secondary",
    ]
    assert "benchmark_bridge:secondary_token_co_listed" in (
        results[1].metadata["bridge_flags"]
    )
    assert all(
        result.metadata["source_policy"] == "diagnosis_json_seizure_type_surface"
        for result in results
    )


def test_exect_seizure_type_bridge_rejects_granular_absence_and_jerk_tokens():
    assert exect_seizure_type_benchmark_bridge("absences") == []
    assert exect_seizure_type_benchmark_bridge("jerks") == []


def test_exect_seizure_type_bridge_records_bridge_free_vs_bridge_applied_semantics():
    bridged = exect_seizure_type_benchmark_bridge(
        "focal seizures with secondary generalisation",
        prediction_affecting=True,
    )
    scorer_only = exect_seizure_type_benchmark_bridge(
        "focal seizures with secondary generalisation",
        prediction_affecting=False,
    )

    assert [result.benchmark_value for result in bridged] == [
        "focal seizures",
        "secondary generalisation",
        "generalized tonic clonic seizure",
    ]
    assert all(result.prediction_affecting for result in bridged)
    assert all(not result.scorer_only for result in bridged)
    assert all(not result.prediction_affecting for result in scorer_only)
    assert all(result.scorer_only for result in scorer_only)


def test_exect_seizure_type_bridge_primitive_is_registered():
    registry = primitive_registry_by_id()

    primitive = registry["exect.seizure_type.benchmark_bridge.v1"]

    assert primitive.status == "implemented"
    assert primitive.dataset == "exect_v2"
    assert primitive.field_families == ["seizure_type"]
    assert primitive.normalization_scope == "benchmark_bridge"

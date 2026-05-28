from __future__ import annotations

from clinical_extraction.exect.diagnosis_primitives import (
    exect_diagnosis_annotation_policy,
    exect_diagnosis_benchmark_bridge,
)
from clinical_extraction.primitives import primitive_registry_by_id


def test_exect_diagnosis_bridge_strips_uncertainty_and_preserves_jme_surface():
    results = exect_diagnosis_benchmark_bridge("probable juvenile myoclonic epilepsy")

    assert len(results) == 1
    result = results[0]
    assert result.primitive_id == "exect.diagnosis.benchmark_bridge.v1"
    assert result.dataset == "exect_v2"
    assert result.field_family == "diagnosis"
    assert result.canonical_value == "probable juvenile myoclonic epilepsy"
    assert result.benchmark_value == "juvenile myoclonic epilepsy"
    assert "benchmark_bridge:diagnosis_uncertainty_stripped" in (
        result.metadata["bridge_flags"]
    )


def test_exect_diagnosis_bridge_collapses_generic_parent_under_specific_diagnosis():
    results = exect_diagnosis_benchmark_bridge(
        ["epilepsy", "juvenile-myoclonic-epilepsy"]
    )

    assert [result.benchmark_value for result in results] == [
        "juvenile myoclonic epilepsy"
    ]
    assert results[0].metadata["collapsed_parent_diagnoses"] == [
        "epilepsy"
    ]
    assert "specificity_collapsed" in results[0].metadata["bridge_flags"]


def test_exect_diagnosis_bridge_restores_symptomatic_structural_focal_surface():
    results = exect_diagnosis_benchmark_bridge("symptomatic structural epilepsy")

    assert [result.benchmark_value for result in results] == [
        "symptomatic structural focal epilepsy"
    ]
    assert "benchmark_bridge:symptomatic_structural_focal_restored" in (
        results[0].metadata["bridge_flags"]
    )


def test_exect_diagnosis_bridge_note_gates_generic_epilepsy_co_list():
    results = exect_diagnosis_benchmark_bridge(
        ["primary generalized epilepsy"],
        note_text=(
            "Diagnosis: epilepsy - primary generalised epilepsy. "
            "The epilepsy remains controlled."
        ),
    )

    assert [result.benchmark_value for result in results] == [
        "primary generalized epilepsy",
        "epilepsy",
    ]
    epilepsy = results[1]
    assert epilepsy.metadata["co_list_augmented"]
    assert "benchmark_bridge:diagnosis_co_list_augmented" in (
        epilepsy.metadata["bridge_flags"]
    )


def test_exect_diagnosis_bridge_handles_empty_lists_without_single_event_inference():
    single_event = exect_diagnosis_benchmark_bridge(
        [],
        note_text="Diagnosis: single focal seizure. First event under review.",
    )
    unclassified = exect_diagnosis_benchmark_bridge(
        [],
        note_text="Diagnosis: epilepsy unclassified.",
    )

    assert single_event == []
    assert [result.benchmark_value for result in unclassified] == ["epilepsy"]
    assert "benchmark_bridge:diagnosis_co_list_augmented" in (
        unclassified[0].metadata["bridge_flags"]
    )


def test_exect_diagnosis_bridge_suppresses_seizure_descriptor_header_diagnosis():
    results = exect_diagnosis_benchmark_bridge(
        ["juvenile myoclonic epilepsy"],
        note_text="Diagnosis: GTCS and myoclonic jerks. Possible JME presenting.",
    )

    assert results == []


def test_exect_diagnosis_annotation_policy_keeps_certainty_threshold_explicit():
    included = exect_diagnosis_annotation_policy(
        {
            "CUIPhrase": "juvenile-myoclonic-epilepsy",
            "DiagCategory": "Epilepsy",
            "Negation": "Affirmed",
            "Certainty": "5",
        }
    )
    uncertain = exect_diagnosis_annotation_policy(
        {
            "CUIPhrase": "JME",
            "DiagCategory": "Epilepsy",
            "Negation": "Affirmed",
            "Certainty": "3",
        }
    )

    assert included.benchmark_value == "benchmark_included"
    assert included.metadata["benchmark_included"]
    assert uncertain.benchmark_value is None
    assert "below_certainty_threshold" in uncertain.metadata["rejected_reasons"]
    assert uncertain.scorer_only


def test_exect_diagnosis_bridge_primitive_is_registered():
    registry = primitive_registry_by_id()

    primitive = registry["exect.diagnosis.benchmark_bridge.v1"]

    assert primitive.status == "implemented"
    assert primitive.dataset == "exect_v2"
    assert primitive.field_families == ["diagnosis"]
    assert primitive.normalization_scope == "benchmark_bridge"

from __future__ import annotations

from clinical_extraction.evaluation.gan_frequency_content_gate import (
    gold_gate_class,
    predicted_gate_class,
)


def test_gold_gate_class_preserves_unknown_and_no_reference_boundary():
    assert gold_gate_class("no seizure frequency reference") == "no_reference"
    assert gold_gate_class("unknown") == "unknown_unclear_frequency"


def test_gold_gate_class_routes_unknown_cluster_to_unclear_frequency():
    assert (
        gold_gate_class("unknown, 2 to 3 per cluster")
        == "unknown_unclear_frequency"
    )


def test_gold_gate_class_separates_seizure_free_from_quantified_presence():
    assert gold_gate_class("seizure free for 6 month") == "seizure_free"
    assert gold_gate_class("2 per 3 month") == "quantified_frequency_presence"
    assert (
        gold_gate_class("2 cluster per month, 3 per cluster")
        == "quantified_frequency_presence"
    )


def test_predicted_gate_prioritizes_quantified_candidates_before_abstentions():
    assert (
        predicted_gate_class(["unknown", "no seizure frequency reference", "1 per month"])
        == "quantified_frequency_presence"
    )


def test_predicted_gate_keeps_seizure_free_as_own_content_class():
    assert predicted_gate_class(["seizure free for 1 year"]) == "seizure_free"


def test_predicted_gate_uses_unknown_when_only_unclear_frequency_is_supported():
    assert predicted_gate_class(["unknown"]) == "unknown_unclear_frequency"
    assert (
        predicted_gate_class(["unknown, 4 per cluster"])
        == "unknown_unclear_frequency"
    )


def test_predicted_gate_defaults_to_no_reference_without_supported_candidates():
    assert predicted_gate_class([]) == "no_reference"
    assert predicted_gate_class(["no seizure frequency reference"]) == "no_reference"

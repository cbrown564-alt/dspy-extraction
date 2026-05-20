from __future__ import annotations

import pytest

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.primitives import (
    build_gan_frequency_candidate_payloads,
    check_gan_frequency_evidence_guard,
    gan_frequency_label_policy_bridge,
)
from clinical_extraction.primitives import primitive_registry_by_id


def _record(record_id: str):
    return next(record for record in load_gan_records() if record.record_id == record_id)


def test_gan_frequency_candidate_payloads_reuse_shared_candidate_contract():
    record = _record("gan_10052")
    candidates = build_gan_frequency_candidate_payloads(record.note_text)

    candidate = next(
        item
        for item in candidates
        if item.benchmark_value == "4 cluster per 3 month, multiple per cluster"
    )

    assert candidate.primitive_id == "gan.frequency.temporal_candidates.v1"
    assert candidate.dataset == "gan_2026"
    assert candidate.field_family == "frequency"
    assert candidate.normalized_value == candidate.benchmark_value
    assert candidate.source_span_text == candidate.raw_text
    assert record.note_text[candidate.start : candidate.end] == candidate.source_span_text
    assert candidate.metadata["monthly_frequency"] == pytest.approx(4.0)
    assert candidate.metadata["pragmatic_category"] == "frequent"


def test_gan_frequency_label_policy_bridge_preserves_unknown_and_no_reference():
    unknown = gan_frequency_label_policy_bridge("unknown")
    no_reference = gan_frequency_label_policy_bridge("no seizure frequency reference")

    assert unknown.canonical_value == "unknown"
    assert unknown.benchmark_value == "unknown"
    assert unknown.metadata["label_policy_class"] == "unknown_frequency"
    assert unknown.metadata["monthly_frequency"] == pytest.approx(1000.0)

    assert no_reference.canonical_value == "no seizure frequency reference"
    assert no_reference.benchmark_value == "no seizure frequency reference"
    assert no_reference.metadata["label_policy_class"] == "no_frequency_reference"
    assert no_reference.metadata["monthly_frequency"] == pytest.approx(0.0)


def test_gan_frequency_label_policy_bridge_normalizes_surface_without_affecting_prediction():
    result = gan_frequency_label_policy_bridge("Seizure free for 6 months")

    assert result.raw_value == "Seizure free for 6 months"
    assert result.canonical_value == "seizure free for 6 month"
    assert result.benchmark_value == "seizure free for 6 month"
    assert result.transformation_rule == "gan_label_policy_normalization"
    assert not result.prediction_affecting
    assert result.scorer_only
    assert "Plural units are normalized" in result.clinical_caveat


def test_gan_frequency_evidence_guard_supports_elided_gold_evidence():
    note = "She had two seizures in January. She then had one seizure in March."
    result = check_gan_frequency_evidence_guard(
        note_text=note,
        evidence_text="two seizures in January ... one seizure in March",
        label="3 per 3 month",
    )

    assert result.support_status == "normalized_interpretation"
    assert result.normalized_interpretation_supported
    assert "multi-span elided evidence" in result.caveats


def test_gan_frequency_evidence_guard_keeps_no_reference_distinct_from_unknown():
    note = "Administrative letter confirming appointment cancellation."

    no_reference = check_gan_frequency_evidence_guard(
        note_text=note,
        evidence_text=None,
        label="no seizure frequency reference",
    )
    unknown = check_gan_frequency_evidence_guard(
        note_text=note,
        evidence_text=None,
        label="unknown",
    )

    assert no_reference.support_status == "no_reference"
    assert "Gan no-reference label" in no_reference.caveats
    assert unknown.support_status == "no_reference"
    assert "Gan unknown label still implies seizure-frequency context" in unknown.caveats


def test_gan_frequency_pack_primitives_are_registered():
    registry = primitive_registry_by_id()

    assert registry["gan.frequency.label_policy_bridge.v1"].status == "implemented"
    assert registry["gan.frequency.evidence_guard.v1"].status == "implemented"

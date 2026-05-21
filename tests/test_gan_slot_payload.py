from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.slot_payload import (
    build_slot_payloads_from_candidates,
    enrich_candidate_to_slot_payload,
    format_slot_payload_candidates_for_prompt,
    slot_payload_to_dict,
)
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates,
    format_temporal_candidates_for_prompt,
    presentation_for_implementation_variant,
)


def _record(record_id: str):
    return next(record for record in load_gan_records() if record.record_id == record_id)


def test_enrich_candidate_to_slot_payload_exposes_calendar_aggregation():
    candidate = next(
        candidate
        for candidate in build_temporal_frequency_candidates(_record("gan_14485"))
        if candidate.canonical_label == "2 per 3 month"
    )
    payload = enrich_candidate_to_slot_payload(candidate)

    assert payload.candidate_label == "2 per 3 month"
    assert payload.window_source == "calendar_aggregation"
    assert payload.denominator_status == "derivable"
    assert payload.event_count_or_range == "2"
    assert payload.supporting_quote == candidate.evidence_text


def test_enrich_candidate_to_slot_payload_exposes_cluster_slots():
    candidate = next(
        candidate
        for candidate in build_temporal_frequency_candidates(_record("gan_10410"))
        if "3 to 4 per cluster" in candidate.canonical_label
    )
    payload = enrich_candidate_to_slot_payload(candidate)

    assert payload.cluster_count_or_range == "1"
    assert payload.per_cluster_count_or_range == "3 to 4"
    assert payload.cluster_spacing_source == "explicit_spacing"


def test_enrich_candidate_to_slot_payload_flags_vague_cluster_multiplier():
    candidate = next(
        candidate
        for candidate in build_temporal_frequency_candidates(_record("gan_10003"))
        if candidate.canonical_label == "1 cluster per week, multiple per cluster"
    )
    payload = enrich_candidate_to_slot_payload(candidate)

    assert payload.per_cluster_count_or_range == "multiple"
    assert payload.cluster_spacing_source == "vague_recurrence"
    assert payload.denominator_status == "missing_or_ambiguous"
    assert payload.unknown_policy_cue is not None


def test_format_slot_payload_candidates_for_prompt_includes_structured_fields():
    candidates = build_temporal_frequency_candidates(_record("gan_14485"))
    formatted = format_slot_payload_candidates_for_prompt(candidates)

    assert "Deterministic temporal frequency slot payloads" in formatted
    assert "denominator_status" in formatted
    assert "target_priority_cue" in formatted
    assert '"slot_payloads"' in formatted
    assert slot_payload_to_dict(build_slot_payloads_from_candidates(candidates)[0])[
        "window_source"
    ]


def test_format_temporal_candidates_for_prompt_supports_slot_payload_presentation():
    candidates = build_temporal_frequency_candidates(_record("gan_14485"))
    formatted = format_temporal_candidates_for_prompt(
        candidates,
        presentation="slot_payload",
    )

    assert "slot payloads" in formatted.lower()
    assert "window_source" in formatted


def test_presentation_for_implementation_variant_maps_slot_payload():
    assert presentation_for_implementation_variant("slot_payload_v1") == "slot_payload"


def test_enrich_candidate_to_slot_payload_flags_unknown_denominator_policy():
    candidate = next(
        candidate
        for candidate in build_temporal_frequency_candidates(_record("gan_13993"))
        if candidate.canonical_label == "unknown"
    )
    payload = enrich_candidate_to_slot_payload(candidate)

    assert payload.denominator_status == "missing_or_ambiguous"
    assert payload.unknown_policy_cue is not None

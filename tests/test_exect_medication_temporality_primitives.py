from __future__ import annotations

from clinical_extraction.exect.primitives import (
    recover_exect_medication_temporality_with_post_classifier,
)


def test_recover_medication_temporality_post_classifier_reclassifies_planned_to_current():
    recovered, flags = recover_exect_medication_temporality_with_post_classifier(
        ["lamotrigine|planned"],
        ["Current medication: lamotrigine 75mg bd as detailed below to reduce"],
        "Current anti-epileptic medication: lamotrigine 75mg bd.",
    )

    assert recovered == ["lamotrigine|current"]
    assert "s4_bridge:medication_temporality_status_reclassified" in flags


def test_recover_medication_temporality_post_classifier_drops_non_asm():
    recovered, flags = recover_exect_medication_temporality_with_post_classifier(
        ["thyroxine|current", "citalopram|current"],
        ["thyroxine 100mcg daily", "citalopram 20mg daily"],
        "Current medication: thyroxine and citalopram.",
    )

    assert recovered == []
    assert flags.count("s4_bridge:medication_temporality_non_asm_removed") == 2


def test_recover_medication_temporality_post_classifier_keeps_planned():
    recovered, flags = recover_exect_medication_temporality_with_post_classifier(
        ["levetiracetam|current"],
        ["To start levetiracetam 250mg nocte if seizures recur."],
        "Current medication: Lamictal 100mg BD.",
    )

    assert recovered == ["levetiracetam|planned"]
    assert "s4_bridge:medication_temporality_status_reclassified" in flags


def test_recover_medication_temporality_post_classifier_drops_unknown_without_cues():
    recovered, flags = recover_exect_medication_temporality_with_post_classifier(
        ["lamotrigine|current"],
        ["discussed lamotrigine options"],
        "Discussed lamotrigine options at clinic.",
    )

    assert recovered == []
    assert "s4_bridge:medication_temporality_unknown_removed" in flags

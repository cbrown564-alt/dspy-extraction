from __future__ import annotations

from clinical_extraction.exect.medication_primitives import (
    recover_exect_medication_temporality_non_asm_dose_current_guard,
    recover_exect_medication_temporality_non_asm_guard,
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


def test_recover_medication_temporality_non_asm_guard_drops_non_asm():
    recovered, flags = recover_exect_medication_temporality_non_asm_guard(
        ["thyroxine|current", "citalopram|current"],
        ["thyroxine 100mcg daily", "citalopram 20mg daily"],
        "Current medication: thyroxine and citalopram.",
    )

    assert recovered == []
    assert flags.count("s4_bridge:medication_temporality_non_asm_removed") == 2


def test_recover_medication_temporality_non_asm_guard_keeps_asm_planned_without_reclassify():
    recovered, flags = recover_exect_medication_temporality_non_asm_guard(
        ["levetiracetam|planned"],
        ["To start levetiracetam 250mg nocte if seizures recur."],
        "Current medication: Lamictal 100mg BD.",
    )

    assert recovered == ["levetiracetam|planned"]
    assert "s4_bridge:medication_temporality_status_reclassified" not in flags


def test_recover_medication_temporality_non_asm_guard_keeps_dose_only_current():
    recovered, flags = recover_exect_medication_temporality_non_asm_guard(
        ["lamotrigine|current"],
        ["lamotrigine 150 milligrams twice a day"],
        "Discussed lamotrigine options at clinic.",
    )

    assert recovered == ["lamotrigine|current"]
    assert "s4_bridge:medication_temporality_unknown_removed" not in flags


def test_recover_medication_temporality_non_asm_dose_current_guard_keeps_dose_current():
    recovered, flags = recover_exect_medication_temporality_non_asm_dose_current_guard(
        ["lamotrigine|current"],
        ["lamotrigine 150 milligrams twice a day"],
        "Discussed lamotrigine options at clinic.",
    )

    assert recovered == ["lamotrigine|current"]
    assert "s4_bridge:medication_temporality_dose_current_preserved" in flags


def test_recover_medication_temporality_non_asm_dose_current_guard_drops_unsupported_planned():
    recovered, flags = recover_exect_medication_temporality_non_asm_dose_current_guard(
        ["lamotrigine|planned"],
        ["lamotrigine 150 milligrams twice a day"],
        "Current anti-epileptic medication: lamotrigine.",
    )

    assert recovered == []
    assert "s4_bridge:medication_temporality_unsupported_planned_previous_removed" in flags


def test_recover_medication_temporality_non_asm_dose_current_guard_keeps_explicit_planned():
    recovered, flags = recover_exect_medication_temporality_non_asm_dose_current_guard(
        ["levetiracetam|planned"],
        ["To start levetiracetam 250mg nocte if seizures recur."],
        "Current medication: lamotrigine.",
    )

    assert recovered == ["levetiracetam|planned"]
    assert "s4_bridge:medication_temporality_unsupported_planned_previous_removed" not in flags


def test_recover_medication_temporality_post_classifier_drops_unknown_without_cues():
    recovered, flags = recover_exect_medication_temporality_with_post_classifier(
        ["lamotrigine|current"],
        ["discussed lamotrigine options"],
        "Discussed lamotrigine options at clinic.",
    )

    assert recovered == []
    assert "s4_bridge:medication_temporality_unknown_removed" in flags

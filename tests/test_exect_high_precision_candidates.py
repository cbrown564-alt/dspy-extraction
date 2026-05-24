from __future__ import annotations

from clinical_extraction.exect.primitives import (
    build_exect_frequency_pre_vocab_labels_high_precision,
    format_exect_frequency_pre_vocab_note_high_precision,
)


def test_high_precision_omits_qualitative_cues():
    # In regular candidates, these would emit qualitative cues like 'frequency same' or 'frequency increased'
    notes_with_qualitative = [
        "Richard's seizures remain well controlled.",
        "Her seizure frequency remains the same.",
        "There has been no change in her seizure frequency.",
        "Richard's seizures remain stable.",
        "Many thanks for referring for increasing seizures.",
        "Huw has had more frequent seizures.",
    ]

    for note in notes_with_qualitative:
        labels = build_exect_frequency_pre_vocab_labels_high_precision(note)
        # Qualitative cues should be completely omitted
        assert "frequency same" not in labels
        assert "frequency increased" not in labels
        assert "frequency decreased" not in labels
        assert "infrequent" not in labels
        assert len(labels) == 0

    # For "seizures have been worse in the last year.", it has 'in the last year' (implicit quantified rate)
    # but the qualitative cue 'frequency increased' (from 'worse') must be omitted.
    note_worse = "seizures have been worse in the last year."
    labels_worse = build_exect_frequency_pre_vocab_labels_high_precision(note_worse)
    assert "frequency increased" not in labels_worse
    assert "1 per 1 year" in labels_worse
    assert len(labels_worse) == 1


def test_high_precision_omits_generic_non_dated_seizure_free():
    # In regular candidates, these might emit "seizure free"
    note = "He is currently seizure free."
    labels = build_exect_frequency_pre_vocab_labels_high_precision(note)
    assert "seizure free" not in labels
    assert len(labels) == 0


def test_high_precision_retains_quantified_rates_and_windows():
    # 1. Section-list adverbial rates
    labels_weekly = build_exect_frequency_pre_vocab_labels_high_precision("Myoclonic jerks weekly.")
    assert "1 per 1 week" in labels_weekly

    labels_twice_weekly = build_exect_frequency_pre_vocab_labels_high_precision("He gets jerks twice weekly.")
    assert "2 per 1 week" in labels_twice_weekly

    # 2. Extended quantified rates
    labels_once_month = build_exect_frequency_pre_vocab_labels_high_precision("About once a month she has a seizure.")
    assert "1 per 1 month" in labels_once_month

    labels_every_3_weeks = build_exect_frequency_pre_vocab_labels_high_precision("Focal seizures every 3 weeks.")
    assert "1 per 3 week" in labels_every_3_weeks

    # 3. Zero-rate windows
    labels_free_5_years = build_exect_frequency_pre_vocab_labels_high_precision("He has been seizure free for 5 years.")
    assert "0 per 5 year" in labels_free_5_years

    labels_no_sz_2_years = build_exect_frequency_pre_vocab_labels_high_precision("No seizures in the last 2 years.")
    assert "0 per 2 year" in labels_no_sz_2_years

    # 4. Seizure free since year
    labels_last_event = build_exect_frequency_pre_vocab_labels_high_precision("last event 2015")
    assert "seizure free since 2015" in labels_last_event

    labels_since_2017 = build_exect_frequency_pre_vocab_labels_high_precision("seizure free since 2017")
    assert "seizure free since 2017" in labels_since_2017


def test_format_note_high_precision_injects_header():
    note = "Focal seizures every 3 weeks."
    formatted = format_exect_frequency_pre_vocab_note_high_precision(note)
    
    assert "Precomputed benchmark-facing candidates (soft hints; emit only when note-supported):" in formatted
    assert "seizure_frequency: 1 per 3 week" in formatted
    assert "---" in formatted
    assert note in formatted

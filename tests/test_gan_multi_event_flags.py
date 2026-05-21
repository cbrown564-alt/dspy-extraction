from clinical_extraction.evaluation.gan_multi_event_flags import (
    build_multi_event_flags,
    stratify_rows_by_multi_event_flags,
)


def _raw_record(
    *,
    source_row_index: int = 1,
    note_text: str,
    analysis: str,
    gold_label: str = "4 per day",
    reference_label: str = "4 per day",
    gold_evidence: str = "daily absences",
) -> dict:
    return {
        "source_row_index": source_row_index,
        "clinic_date": note_text,
        "labels_match_all_categories": True,
        "quotes_ok_all_categories": True,
        "row_ok": True,
        "mismatch_categories": "",
        "quote_issue_categories": "",
        "check__Seizure Frequency Number": {
            "analysis": analysis,
            "seizure_frequency_number": [gold_label, gold_evidence],
            "reference": [reference_label, "reference evidence"],
        },
    }


def test_build_multi_event_flags_marks_highest_frequency_adjudication():
    raw = _raw_record(
        note_text=(
            "He has daily absences. He also has tonic-clonic seizures "
            "two times per month. No seizures have occurred since last review."
        ),
        analysis=(
            'Identify explicit frequencies: (1) "daily absences" -> 1 per day. '
            '(2) "two times per month" -> 2 per month. Apply rule: choose '
            "the highest frequency among different seizure types."
        ),
    )

    flags = build_multi_event_flags(raw)

    assert flags.record_id == "gan_1"
    assert flags.multiple_candidate_frequencies
    assert flags.highest_frequency_policy_required
    assert flags.seizure_free_conflict
    assert not flags.historical_current_conflict


def test_build_multi_event_flags_marks_unknown_with_event_mentions():
    raw = _raw_record(
        note_text=(
            "Events occur in bursts over several days with quieter stretches, "
            "but the spacing is not reliably documented."
        ),
        analysis="Frequency and spacing are not reliably documented; final label unknown.",
        gold_label="unknown",
        reference_label="unknown",
        gold_evidence="spacing is not reliably documented",
    )

    flags = build_multi_event_flags(raw)

    assert flags.unknown_with_event_mentions
    assert flags.cluster_adjudication_required


def test_stratify_rows_by_multi_event_flags_reports_monthly_accuracy_delta():
    flags = {
        "gan_1": build_multi_event_flags(
            _raw_record(note_text="daily seizures and weekly seizures", analysis="choose highest")
        ),
        "gan_2": build_multi_event_flags(
            _raw_record(
                source_row_index=2,
                note_text="one seizure per month",
                analysis="single frequency",
                gold_label="1 per month",
                reference_label="1 per month",
                gold_evidence="one seizure per month",
            )
        ),
    }
    rows = [
        {"record_id": "gan_1", "status": "scored", "monthly_match": False},
        {"record_id": "gan_2", "status": "scored", "monthly_match": True},
    ]

    report = stratify_rows_by_multi_event_flags(rows, flags)

    strict = report["flags"]["multi_or_highest_analysis_signal"]
    assert strict["true"]["valid_scored"] == 1
    assert strict["true"]["accuracies_valid_only"]["monthly_frequency"] == 0.0
    assert strict["false"]["accuracies_valid_only"]["monthly_frequency"] == 1.0

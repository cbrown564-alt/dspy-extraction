from clinical_extraction.datasets.exect import (
    canonical_seizure_frequency_label,
    format_medication_temporality_label,
    infer_prescription_temporality,
    load_exect_gold_document,
)


def test_canonical_seizure_frequency_label_quantified():
    label = canonical_seizure_frequency_label(
        {
            "NumberOfSeizures": "1",
            "NumberOfTimePeriods": "3",
            "TimePeriod": "Week",
            "CUIPhrase": "focal-seizures-with-altered-awareness",
        }
    )

    assert label == "1 per 3 week"


def test_canonical_seizure_frequency_label_frequency_change():
    label = canonical_seizure_frequency_label(
        {
            "FrequencyChange": "Increased",
            "CUIPhrase": "seizure",
        }
    )

    assert label == "frequency increased"


def test_canonical_seizure_frequency_label_seizure_free():
    label = canonical_seizure_frequency_label(
        {
            "NumberOfSeizures": "0",
            "CUIPhrase": "seizure-free",
        }
    )

    assert label == "seizure free"


def test_canonical_seizure_frequency_label_seizure_free_since_year():
    label = canonical_seizure_frequency_label(
        {
            "NumberOfSeizures": "0",
            "YearDate": "2017",
            "TimeSince_or_TimeOfEvent": "Since",
            "CUIPhrase": "focal-to-bilateral-convulsive-seizure",
        }
    )

    assert label == "seizure free since 2017"


def test_infer_prescription_temporality_treats_dose_change_as_current():
    assert infer_prescription_temporality(
        "Current-anti-epileptic-medication:-lamotrigine-75mg-bd-(to-reduce"
    ) == "current"
    assert (
        infer_prescription_temporality(
            "Lamotrigine-75mg-twice-a-day-(to-increase-as-detailed-below)"
        )
        == "current"
    )


def test_format_medication_temporality_label():
    assert format_medication_temporality_label("lamotrigine", "current") == "lamotrigine|current"


def test_load_exect_gold_document_includes_s4_field_families():
    gold = load_exect_gold_document("EA0008")

    assert "1 per 3 week" in gold.seizure_frequencies
    assert "frequency increased" in gold.seizure_frequencies
    assert "lamotrigine|current" in gold.medication_temporalities


def test_load_exect_gold_document_preserves_s3_field_families():
    gold = load_exect_gold_document("EA0062")

    assert "born normally" in gold.birth_histories
    assert gold.investigations or gold.comorbidities or gold.diagnoses


def test_load_exect_gold_document_deduplicates_seizure_frequency_labels():
    gold = load_exect_gold_document("EA0011")

    assert gold.seizure_frequencies.count("1 per 2 week") == 1
    assert "seizure free since 2017" in gold.seizure_frequencies

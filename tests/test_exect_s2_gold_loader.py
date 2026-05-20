from clinical_extraction.datasets.exect import (
    canonical_comorbidity_label,
    canonical_investigation_label,
    is_comorbidity_patient_history,
    load_exect_gold_document,
)


def test_canonical_investigation_label_uses_structured_modality_results():
    assert (
        canonical_investigation_label(
            {
                "EEG_Performed": "Yes",
                "EEG_Results": "Abnormal",
                "CUIPhrase": "EEG",
            }
        )
        == "eeg abnormal"
    )
    assert (
        canonical_investigation_label(
            {
                "MRI_Performed": "Yes",
                "MRI_Results": "Normal",
                "CUIPhrase": "mri-normal",
            }
        )
        == "mri normal"
    )


def test_canonical_investigation_label_parses_cuiphrase_fallback():
    assert canonical_investigation_label({"CUIPhrase": "eeg-abnormal"}) == "eeg abnormal"
    assert canonical_investigation_label({"CUIPhrase": "abnormal-mri"}) == "mri abnormal"
    assert canonical_investigation_label({"CUIPhrase": "normal-ct"}) == "ct normal"


def test_is_comorbidity_patient_history_excludes_seizure_history():
    assert not is_comorbidity_patient_history(
        "seizures",
        {"Negation": "Affirmed", "Certainty": "5"},
    )
    assert not is_comorbidity_patient_history(
        "febrile-seizures",
        {"Negation": "Affirmed", "Certainty": "5"},
    )
    assert is_comorbidity_patient_history(
        "diabetes",
        {"Negation": "Affirmed", "Certainty": "5"},
    )


def test_canonical_comorbidity_label_normalizes_hyphenated_phrases():
    assert canonical_comorbidity_label("type-1-diabetes") == "type 1 diabetes"
    assert canonical_comorbidity_label("learning-difficulties") == "learning difficulties"


def test_load_exect_gold_document_includes_investigations_and_comorbidities():
    gold = load_exect_gold_document("EA0007")

    assert "mri normal" in gold.investigations
    assert "diabetes" in gold.comorbidities


def test_load_exect_gold_document_deduplicates_comorbidities():
    gold = load_exect_gold_document("EA0116")

    assert gold.comorbidities.count("type 1 diabetes") == 1

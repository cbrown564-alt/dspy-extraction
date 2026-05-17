from clinical_extraction.datasets.exect import (
    canonical_medication_name,
    load_exect_gold_document,
    load_exect_gold_documents,
)


def test_ea0016_loads_single_seizure_type_from_json_diagnosis_rows():
    doc = load_exect_gold_document("EA0016")

    assert doc.document_id == "EA0016"
    assert doc.seizure_types == ["focal seizure"]
    assert doc.diagnoses == []
    assert "missing_gold" not in doc.quality_flags


def test_ea0029_collapses_generic_epilepsy_under_specific_diagnosis():
    doc = load_exect_gold_document("EA0029")

    assert "juvenile myoclonic epilepsy" in doc.raw_diagnoses
    assert "epilepsy" in doc.raw_diagnoses
    assert doc.diagnoses == ["juvenile myoclonic epilepsy"]
    assert "specificity_collapsed" in doc.quality_flags


def test_ea0026_filters_certainty_three_epilepsy_but_keeps_certain_seizure_type():
    doc = load_exect_gold_document("EA0026")

    assert doc.diagnoses == []
    assert doc.seizure_types == ["generalized tonic clonic seizures"]
    assert "missing_gold" not in doc.quality_flags


def test_ea0008_seizure_type_comes_from_diagnosis_rows_without_frequency_noise():
    doc = load_exect_gold_document("EA0008")

    assert doc.seizure_types == ["focal seizures with altered awareness"]
    assert "seizure" not in doc.seizure_types
    assert "seizures" not in doc.seizure_types
    assert "gold_noise" not in doc.quality_flags


def test_medication_synonyms_and_camel_case_normalize_to_canonical_names():
    assert canonical_medication_name("Keppra") == "levetiracetam"
    assert canonical_medication_name("Epilim") == "sodium valproate"
    assert canonical_medication_name("SodiumValproate") == "sodium valproate"
    assert canonical_medication_name("EslicarbazepineAcetate") == "eslicarbazepine"

    doc = load_exect_gold_document("EA0026")
    assert doc.current_medications == ["sodium valproate", "topiramate"]


def test_known_generic_seizure_noise_terms_are_absent_after_source_fix():
    noisy_docs = [
        doc.document_id
        for doc in load_exect_gold_documents()
        if "gold_noise" in doc.quality_flags
    ]

    assert noisy_docs == []

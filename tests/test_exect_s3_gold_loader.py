from clinical_extraction.datasets.exect import (
    canonical_birth_history_label,
    canonical_epilepsy_cause_label,
    canonical_onset_label,
    load_exect_gold_document,
)


def test_canonical_birth_history_label_normalizes_cuiphrase():
    assert canonical_birth_history_label("born-normally") == "born normally"
    assert canonical_birth_history_label("late-preterm-birth") == "late preterm birth"


def test_canonical_onset_label_normalizes_cuiphrase():
    assert canonical_onset_label("epilepsy") == "epilepsy"
    assert (
        canonical_onset_label("generalised-tonic-clonic-seizures")
        == "generalized tonic clonic seizures"
    )


def test_canonical_epilepsy_cause_label_normalizes_cuiphrase():
    assert canonical_epilepsy_cause_label("meningitis") == "meningitis"
    assert canonical_epilepsy_cause_label("Tuberous-sclerosis") == "tuberous sclerosis"


def test_load_exect_gold_document_includes_s3_field_families():
    gold = load_exect_gold_document("EA0062")

    assert "born normally" in gold.birth_histories


def test_load_exect_gold_document_deduplicates_epilepsy_cause():
    gold = load_exect_gold_document("EA0058")

    assert gold.epilepsy_causes.count("meningitis") == 1


def test_load_exect_gold_document_includes_onset_and_when_diagnosed():
    gold = load_exect_gold_document("EA0036")

    assert "birth was normal" in gold.birth_histories
    assert "epilepsy" in gold.when_diagnosed


def test_load_exect_gold_document_onset_includes_seizure_type_phrases():
    gold = load_exect_gold_document("EA0029")

    assert "epilepsy" in gold.onsets
    assert "generalized tonic clonic seizures" in gold.onsets


def test_load_exect_gold_document_preserves_s2_families():
    gold = load_exect_gold_document("EA0007")

    assert gold.investigations
    assert gold.comorbidities

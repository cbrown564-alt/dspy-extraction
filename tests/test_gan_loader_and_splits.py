from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.splits import make_gan_splits


def test_gan_loader_uses_seizure_frequency_number_as_gold_and_reference_as_metadata():
    records = load_gan_records()
    record = records[0]

    assert record.gold_label == record.raw["check__Seizure Frequency Number"]["seizure_frequency_number"][0]
    assert record.reference_label == record.raw["check__Seizure Frequency Number"]["reference"][0]
    assert "label_reference_disagreement" in record.flags or record.gold_label == record.reference_label


def test_gan_splits_are_deterministic_and_cover_all_records():
    records = load_gan_records()
    split_a = make_gan_splits(records, salt="test-salt")
    split_b = make_gan_splits(records, salt="test-salt")

    assert split_a == split_b
    assigned = split_a["development"] + split_a["validation"] + split_a["test"]
    assert len(assigned) == len(records)
    assert len(set(assigned)) == len(records)
    assert split_a["counts"] == {
        "development": len(split_a["development"]),
        "validation": len(split_a["validation"]),
        "test": len(split_a["test"]),
    }


def test_gan_split_metadata_documents_reproducibility_and_hard_cases():
    records = load_gan_records()
    splits = make_gan_splits(records, salt="test-salt")

    assert splits["salt"] == "test-salt"
    assert splits["split_ratios"] == {
        "development": 0.6,
        "validation": 0.2,
        "test": 0.2,
    }
    assert "round(n * ratio)" in splits["allocation_policy"]
    assert splits["stratification"]["fields"] == [
        "pragmatic_category",
        "purist_category",
        "row_ok",
        "label_reference_disagreement",
    ]
    assert "primary gold label differs" in splits["stratification"]["hard_case_definition"]

    hard_case_ids = {record.record_id for record in records if "hard_case" in record.flags}
    hard_case_counts = splits["stratification"]["hard_case_counts"]
    assert sum(hard_case_counts.values()) == len(hard_case_ids)
    for split in ["development", "validation", "test"]:
        assert hard_case_counts[split] == len(hard_case_ids.intersection(splits[split]))

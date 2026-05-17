from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_baseline import (
    build_gan_deterministic_baseline_report,
)


def test_gan_deterministic_baseline_report_compares_metric_semantics():
    report = build_gan_deterministic_baseline_report(load_gan_records())

    assert report["dataset"] == "gan_2026"
    assert report["scorer"] == "gan_frequency_deterministic_v1"
    assert report["counts"]["gold_records"] == 1500
    assert report["counts"]["hard_cases"] == 197
    assert report["counts"]["no_seizure_frequency_reference_gold"] == 54
    assert report["gold_distribution"]["pragmatic_category_counts"][
        "no_seizure_information"
    ] > report["counts"]["no_seizure_frequency_reference_gold"]

    gold_copy = report["prediction_fixtures"]["gold_copy"]
    assert gold_copy["monthly_frequency_accuracy"] == 1.0
    assert gold_copy["pragmatic_category_accuracy"] == 1.0

    surface_variants = report["prediction_fixtures"]["surface_variant_normalization"]
    assert surface_variants["raw_exact_accuracy"] < 1.0
    assert surface_variants["normalized_label_accuracy"] == 1.0
    assert surface_variants["monthly_frequency_accuracy"] == 1.0

    pragmatic_bucket = report["prediction_fixtures"]["pragmatic_bucket_proxy"]
    assert pragmatic_bucket["raw_exact_accuracy"] < pragmatic_bucket[
        "pragmatic_category_accuracy"
    ]
    assert pragmatic_bucket["monthly_frequency_accuracy"] < pragmatic_bucket[
        "pragmatic_category_accuracy"
    ]
    assert pragmatic_bucket["pragmatic_category_accuracy"] == 1.0

    assert report["caveats"] == [
        "Gan primary gold is check__Seizure Frequency Number.seizure_frequency_number[0].",
        "Reference labels mark secondary cross-check agreement and hard cases; they are not benchmark gold.",
        "Raw exact and normalized-label exact metrics are diagnostic, not benchmark-facing.",
        "Fixture predictions are deterministic probes of scorer behavior, not model outputs.",
    ]

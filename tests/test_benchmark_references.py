from clinical_extraction.evaluation.benchmarks import (
    AlignmentContext,
    AlignmentLabel,
    EXECT_TABLE1_REFERENCES,
    GAN_REFERENCES,
    benchmark_alignment,
)


def test_published_benchmark_constants_capture_exect_and_gan_headlines():
    assert EXECT_TABLE1_REFERENCES["diagnosis.per_item_f1"].value == 0.85
    assert EXECT_TABLE1_REFERENCES["diagnosis.per_letter_f1"].value == 0.94
    assert EXECT_TABLE1_REFERENCES["all.per_item_f1"].value == 0.87
    assert EXECT_TABLE1_REFERENCES["all.gold_annotations"].value == 2047

    assert GAN_REFERENCES["table8.cot15000.real300.purist_micro_f1"].value == 0.788
    assert GAN_REFERENCES["table8.cot15000.real300.pragmatic_micro_f1"].value == 0.847


def test_current_exect_field_family_scorer_is_only_partially_aligned():
    alignment = benchmark_alignment(
        AlignmentContext(
            dataset="exect_v2",
            evaluation_set="synthetic_200",
            scorer_mode="exect_field_family_deterministic_v1",
            metric_name="micro_f1",
            schema_level="exect_s0_s1_core",
        )
    )

    assert alignment.label == AlignmentLabel.PARTIAL
    assert alignment.reference is EXECT_TABLE1_REFERENCES["all.per_item_f1"]
    assert "narrower audited field-family view" in " ".join(alignment.caveats)


def test_current_gan_canonical_scorer_is_not_paper_comparable():
    alignment = benchmark_alignment(
        AlignmentContext(
            dataset="gan_2026",
            evaluation_set="synthetic_data_subset_1500",
            scorer_mode="gan_frequency_deterministic_v1",
            metric_name="purist_category_accuracy",
            schema_level="gan_frequency_s0",
        )
    )

    assert alignment.label == AlignmentLabel.NOT_COMPARABLE
    assert alignment.reference is GAN_REFERENCES["table8.cot15000.real300.purist_micro_f1"]
    assert "gan2026_paper_reproduction" in " ".join(alignment.caveats)


def test_gan_paper_reproduction_synthetic_subset_is_not_claimed_as_real_letter_reproduction():
    alignment = benchmark_alignment(
        AlignmentContext(
            dataset="gan_2026",
            evaluation_set="synthetic_data_subset_1500",
            scorer_mode="gan2026_paper_reproduction",
            metric_name="purist_category_accuracy",
            schema_level="gan_frequency_s0",
        )
    )

    assert alignment.label == AlignmentLabel.PARTIAL
    assert alignment.reference is GAN_REFERENCES["table8.cot15000.real300.purist_micro_f1"]
    assert "Real(300)" in " ".join(alignment.caveats)


def test_future_gan_real300_micro_f1_context_can_be_marked_aligned():
    alignment = benchmark_alignment(
        AlignmentContext(
            dataset="gan_2026",
            evaluation_set="Real(300)",
            scorer_mode="gan2026_paper_reproduction",
            metric_name="purist_micro_f1",
            schema_level="gan_frequency_s0",
        )
    )

    assert alignment.label == AlignmentLabel.ALIGNED
    assert alignment.reference is GAN_REFERENCES["table8.cot15000.real300.purist_micro_f1"]


def test_unknown_benchmark_context_is_not_comparable():
    alignment = benchmark_alignment(
        AlignmentContext(
            dataset="gan_2026",
            evaluation_set="Real(300)",
            scorer_mode="unreviewed_scorer",
            metric_name="raw_exact_match",
            schema_level="gan_frequency_s0",
        )
    )

    assert alignment.label == AlignmentLabel.NOT_COMPARABLE
    assert alignment.reference is None

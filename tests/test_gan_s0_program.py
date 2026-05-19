import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_FIELD,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    GanFrequencyS0DirectModule,
    GanFrequencyS0Module,
    GanFrequencyS0Signature,
    GanFrequencyS0TemporalCandidatesVerifyRepairModule,
    GanFrequencyS0VerifyRepairModule,
    GanFrequencyS0VerifierModule,
    GanFrequencyS0VerifierSignature,
    build_gan_s0_module,
    compile_gan_s0_module,
    compile_gan_s0_module_gepa,
    gan_frequency_s0_semantic_evidence_feedback_metric,
    gan_frequency_s0_semantic_evidence_metric,
    gan_frequency_s0_synthesis_feedback_metric,
    gan_frequency_s0_metric,
    gan_frequency_s0_synthesis_metric,
    gan_frequency_s0_run_metadata,
    make_gan_dspy_examples,
    make_gan_synthesis_dspy_examples,
    predict_gan_records,
)
from clinical_extraction.schemas import GanRecord


@pytest.fixture(autouse=True)
def reset_dspy_settings():
    """Isolate DSPy global state between tests."""
    yield
    dspy.settings.configure(lm=None)


def _configure_dummy(answers: list[dict]) -> None:
    dspy.configure(lm=DummyLM(answers=answers))


def test_gan_s0_module_maps_dspy_prediction_to_prediction_set():
    record = next(
        r for r in load_gan_records()
        if r.gold_evidence and r.gold_evidence in r.note_text
    )
    _configure_dummy([{
        "reasoning": "The note mentions the gold frequency.",
        "seizure_frequency_number": record.gold_label,
        "evidence_text": record.gold_evidence,
    }])

    module = GanFrequencyS0Module()
    prediction_set = predict_gan_records(
        module, [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    assert prediction_set.dataset == "gan_2026"
    assert prediction_set.schema_level == GAN_FREQUENCY_S0_SCHEMA_LEVEL
    assert prediction_set.metadata["program_variant"] == GAN_FREQUENCY_S0_VARIANT
    assert prediction_set.metadata["model_provider"] == "mock"

    value = prediction_set.predictions[0].values[0]
    assert value.field_name == GAN_FREQUENCY_S0_FIELD
    assert value.raw_value == record.gold_label
    assert value.normalized_value == record.gold_label
    assert value.evidence[0].text == record.gold_evidence
    assert (
        record.note_text[value.evidence[0].start: value.evidence[0].end]
        == record.gold_evidence
    )


def test_gan_s0_direct_module_maps_prediction_without_reasoning_field():
    record = next(
        r for r in load_gan_records()
        if r.gold_evidence and r.gold_evidence in r.note_text
    )
    _configure_dummy([{
        "seizure_frequency_number": record.gold_label,
        "evidence_text": record.gold_evidence,
    }])

    module = GanFrequencyS0DirectModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_DIRECT_VARIANT,
    )

    assert prediction_set.metadata["program_variant"] == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert prediction_set.predictions[0].metadata["program_variant"] == (
        GAN_FREQUENCY_S0_DIRECT_VARIANT
    )
    assert prediction_set.predictions[0].values[0].normalized_value == record.gold_label


def test_build_gan_s0_module_dispatches_program_variants():
    assert isinstance(build_gan_s0_module(GAN_FREQUENCY_S0_VARIANT), GanFrequencyS0Module)
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_DIRECT_VARIANT),
        GanFrequencyS0DirectModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT),
        GanFrequencyS0VerifyRepairModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT),
        GanFrequencyS0TemporalCandidatesVerifyRepairModule,
    )


def test_gan_s0_prediction_progress_callback_reports_each_completed_record():
    records = load_gan_records()[:2]
    _configure_dummy([
        {
            "reasoning": "The first note mentions the gold frequency.",
            "seizure_frequency_number": records[0].gold_label,
            "evidence_text": records[0].gold_evidence,
        },
        {
            "reasoning": "The second note mentions the gold frequency.",
            "seizure_frequency_number": records[1].gold_label,
            "evidence_text": records[1].gold_evidence,
        },
    ])
    progress: list[tuple[int, int, str]] = []

    module = GanFrequencyS0Module()
    prediction_set = predict_gan_records(
        module,
        records,
        model_provider="mock",
        model_name="dummy-fixture",
        progress_callback=lambda index, total, record_id: progress.append(
            (index, total, record_id)
        ),
    )

    assert len(prediction_set.predictions) == 2
    assert progress == [
        (1, 2, records[0].record_id),
        (2, 2, records[1].record_id),
    ]


def test_gan_s0_module_records_abstention_when_label_is_null():
    record = load_gan_records()[0]
    _configure_dummy([{
        "reasoning": "No frequency found.",
        "seizure_frequency_number": None,
        "evidence_text": None,
    }])

    module = GanFrequencyS0Module()
    prediction_set = predict_gan_records(
        module, [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    value = prediction_set.predictions[0].values[0]
    assert value.field_name == GAN_FREQUENCY_S0_FIELD
    assert value.raw_value is None
    assert value.normalized_value is None
    assert value.evidence == []
    assert "abstained" in value.quality_flags


def test_gan_s0_module_preserves_raw_label_when_normalizing_repairable_surface_form():
    record = load_gan_records()[0]
    _configure_dummy([{
        "reasoning": "The note supports a range around daily events.",
        "seizure_frequency_number": "1 per day to 1 per 2 day",
        "evidence_text": "dummy evidence",
    }])

    module = GanFrequencyS0Module()
    prediction_set = predict_gan_records(
        module, [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    value = prediction_set.predictions[0].values[0]
    assert value.raw_value == "1 per day to 1 per 2 day"
    assert value.normalized_value == "1 per 1 to 2 day"
    assert "normalized_label_repaired" in value.quality_flags


def test_gan_s0_module_repairs_extreme_daily_count_to_multiple_per_day():
    record = load_gan_records()[0]
    _configure_dummy([{
        "reasoning": "Hourly electrographic seizures should not exceed Gan scale.",
        "seizure_frequency_number": "96 per day",
        "evidence_text": "dummy evidence",
    }])

    module = GanFrequencyS0Module()
    prediction_set = predict_gan_records(
        module, [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    value = prediction_set.predictions[0].values[0]
    assert value.raw_value == "96 per day"
    assert value.normalized_value == "multiple per day"
    assert "normalized_label_repaired" in value.quality_flags


@pytest.mark.parametrize(
    ("raw_label", "normalized_label"),
    [
        ('"unknown"', "unknown"),
        ("'unknown'", "unknown"),
        ("1 per 3 week to 1 per 2 week", "1 per 2 to 3 week"),
        ("1 per 10 day to 1 per 7 day", "1 per 7 to 10 day"),
    ],
)
def test_gan_s0_module_repairs_full_validation_surface_errors(
    raw_label: str, normalized_label: str
):
    record = load_gan_records()[0]
    _configure_dummy([{
        "reasoning": "The note supports a repairable surface-form label.",
        "seizure_frequency_number": raw_label,
        "evidence_text": "dummy evidence",
    }])

    module = GanFrequencyS0Module()
    prediction_set = predict_gan_records(
        module, [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    value = prediction_set.predictions[0].values[0]
    assert value.raw_value == raw_label
    assert value.normalized_value == normalized_label
    assert "normalized_label_repaired" in value.quality_flags


@pytest.mark.parametrize(
    "raw_label",
    [
        "1 cluster per week",
        "2 cluster per 3 month",
        "1 cluster per 5 day",
        "1 cluster per month, unknown per cluster",
    ],
)
def test_gan_s0_module_does_not_repair_semantic_cluster_failures(raw_label: str):
    record = load_gan_records()[0]
    _configure_dummy([{
        "reasoning": "The note does not support enough information to complete the cluster label.",
        "seizure_frequency_number": raw_label,
        "evidence_text": "dummy evidence",
    }])

    module = GanFrequencyS0Module()
    prediction_set = predict_gan_records(
        module, [record],
        model_provider="mock",
        model_name="dummy-fixture",
    )

    value = prediction_set.predictions[0].values[0]
    assert value.raw_value == raw_label
    assert value.normalized_value == raw_label
    assert "normalized_label_repaired" not in value.quality_flags


@pytest.mark.parametrize(
    ("raw_label", "normalized_label"),
    [
        ("4 per hour", "multiple per day"),
        ("6 per hour", "multiple per day"),
        (
            "multiple per week, multiple per cluster",
            "multiple cluster per week, multiple per cluster",
        ),
        (
            "1 to 2 per month, multiple per cluster",
            "1 to 2 cluster per month, multiple per cluster",
        ),
    ],
)
def test_gan_s0_module_repairs_cap25_schema_invalid_surfaces(
    raw_label: str, normalized_label: str
):
    record = load_gan_records()[0]
    _configure_dummy([{
        "seizure_frequency_number": raw_label,
        "evidence_text": "dummy evidence",
    }])

    module = GanFrequencyS0DirectModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_DIRECT_VARIANT,
    )

    value = prediction_set.predictions[0].values[0]
    assert value.raw_value == raw_label
    assert value.normalized_value == normalized_label
    assert "normalized_label_repaired" in value.quality_flags
    score_gan_frequency_prediction(
        gold_label="unknown",
        predicted_label=normalized_label,
    )


@pytest.mark.parametrize(
    ("raw_label", "normalized_label"),
    [
        ("several per week", "multiple per week"),
        ("few per month", "multiple per month"),
        ("1-2 per week", "1 to 2 per week"),
        ("3 or 4 per week", "3 to 4 per week"),
        ("11 to 28 per quarter", "11 to 28 per 3 month"),
        ("1 per fortnight", "1 per 2 week"),
        ("fortnightly", "1 per 2 week"),
    ],
)
def test_gan_s0_module_repairs_local_qwen_canonicalization_surfaces(
    raw_label: str, normalized_label: str
):
    record = load_gan_records()[0]
    _configure_dummy([{
        "seizure_frequency_number": raw_label,
        "evidence_text": "dummy evidence",
    }])

    module = GanFrequencyS0DirectModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_DIRECT_VARIANT,
    )

    value = prediction_set.predictions[0].values[0]
    assert value.raw_value == raw_label
    assert value.normalized_value == normalized_label
    assert "normalized_label_repaired" in value.quality_flags


def test_gan_s0_module_strips_prompt_footer_from_evidence():
    note_text = (
        "Continue levetiracetam at 750 mg twice daily. "
        "She reports one seizure per month."
    )
    record = GanRecord(
        record_id="gan_test_evidence",
        source_row_index=1,
        note_text=note_text,
        gold_label="1 per month",
        gold_evidence="one seizure per month",
        reference_label=None,
        reference_evidence=None,
        row_ok=True,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        raw={},
    )
    _configure_dummy([{
        "seizure_frequency_number": "1 per month",
        "evidence_text": (
            "She reports one seizure per month. "
            "Respond with the corresponding output fields and start with [[ ## "
        ),
    }])

    module = GanFrequencyS0DirectModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_DIRECT_VARIANT,
    )

    value = prediction_set.predictions[0].values[0]
    assert value.evidence[0].text == "She reports one seizure per month."
    assert value.evidence[0].start == note_text.index("She reports one seizure per month.")
    assert "evidence_repaired:prompt_footer_stripped" in value.quality_flags


def test_gan_s0_module_truncates_evidence_to_longest_note_prefix():
    note_text = "Continue levetiracetam at 750 mg twice daily."
    record = GanRecord(
        record_id="gan_test_truncated_evidence",
        source_row_index=2,
        note_text=note_text,
        gold_label="unknown",
        gold_evidence=None,
        reference_label=None,
        reference_evidence=None,
        row_ok=True,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        raw={},
    )
    _configure_dummy([{
        "seizure_frequency_number": "unknown",
        "evidence_text": "Continue levetiracetam at 750 mg twice daily. extra spill",
    }])

    module = GanFrequencyS0DirectModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_DIRECT_VARIANT,
    )

    value = prediction_set.predictions[0].values[0]
    assert value.evidence[0].text == note_text
    assert value.evidence[0].start == 0
    assert "evidence_repaired:truncated_to_note_span" in value.quality_flags


def test_gan_frequency_s0_metric_returns_1_on_pragmatic_category_match():
    example = dspy.Example(
        note_text="...",
        seizure_frequency_number="2 per week",
    ).with_inputs("note_text")
    pred = dspy.Prediction(seizure_frequency_number="3 per week")

    score = gan_frequency_s0_metric(example, pred)
    assert score == 1.0


def test_gan_frequency_s0_metric_returns_0_on_category_mismatch():
    example = dspy.Example(
        note_text="...",
        seizure_frequency_number="1 per 6 month",
    ).with_inputs("note_text")
    pred = dspy.Prediction(seizure_frequency_number="3 per week")

    score = gan_frequency_s0_metric(example, pred)
    assert score == 0.0


def test_gan_frequency_s0_metric_returns_0_on_invalid_predicted_label():
    example = dspy.Example(
        note_text="...",
        seizure_frequency_number="1 per month",
    ).with_inputs("note_text")
    pred = dspy.Prediction(seizure_frequency_number="not a valid label at all")

    score = gan_frequency_s0_metric(example, pred)
    assert score == 0.0


def test_gan_frequency_s0_metric_returns_0_on_null_prediction():
    example = dspy.Example(
        note_text="...",
        seizure_frequency_number="2 per week",
    ).with_inputs("note_text")
    pred = dspy.Prediction(seizure_frequency_number=None)

    score = gan_frequency_s0_metric(example, pred)
    assert score == 0.0


def test_gan_frequency_s0_synthesis_metric_requires_exact_label_and_quote_support():
    example = dspy.Example(
        note_text="He reports 3 focal seizures per week despite medication.",
        seizure_frequency_number="3 per week",
        evidence_text="3 focal seizures per week",
    ).with_inputs("note_text")

    exact_with_quote = dspy.Prediction(
        seizure_frequency_number="3 per week",
        evidence_text="3 focal seizures per week",
    )
    pragmatic_only = dspy.Prediction(
        seizure_frequency_number="4 per week",
        evidence_text="3 focal seizures per week",
    )
    missing_quote = dspy.Prediction(
        seizure_frequency_number="3 per week",
        evidence_text=None,
    )
    paraphrased_quote = dspy.Prediction(
        seizure_frequency_number="3 per week",
        evidence_text="three seizures weekly",
    )

    assert gan_frequency_s0_synthesis_metric(example, exact_with_quote) == 1.0
    assert gan_frequency_s0_synthesis_metric(example, pragmatic_only) == 0.0
    assert gan_frequency_s0_synthesis_metric(example, missing_quote) == 0.0
    assert gan_frequency_s0_synthesis_metric(example, paraphrased_quote) == 0.0


def test_gan_frequency_s0_semantic_evidence_metric_rewards_frequency_grades():
    example = dspy.Example(
        note_text="He reports 4 focal seizures per week despite medication.",
        seizure_frequency_number="4 per week",
    ).with_inputs("note_text")

    exact = dspy.Prediction(
        seizure_frequency_number="4 per week",
        evidence_text="4 focal seizures per week",
    )
    same_purist = dspy.Prediction(
        seizure_frequency_number="3 per week",
        evidence_text="4 focal seizures per week",
    )
    pragmatic_only = dspy.Prediction(
        seizure_frequency_number="2 per month",
        evidence_text="4 focal seizures per week",
    )
    wrong_bucket = dspy.Prediction(
        seizure_frequency_number="unknown",
        evidence_text="4 focal seizures per week",
    )

    assert gan_frequency_s0_semantic_evidence_metric(example, exact) == 1.0
    assert gan_frequency_s0_semantic_evidence_metric(example, same_purist) == 0.65
    assert gan_frequency_s0_semantic_evidence_metric(example, pragmatic_only) == 0.4
    assert gan_frequency_s0_semantic_evidence_metric(example, wrong_bucket) == 0.0


def test_gan_frequency_s0_semantic_evidence_metric_gates_missing_evidence():
    example = dspy.Example(
        note_text="He reports 4 focal seizures per week despite medication.",
        seizure_frequency_number="4 per week",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="4 per week",
        evidence_text=None,
    )

    assert gan_frequency_s0_semantic_evidence_metric(example, pred) == 0.0


def test_gan_frequency_s0_semantic_evidence_metric_rewards_no_reference_without_evidence():
    example = dspy.Example(
        note_text="This administrative letter confirms the appointment was cancelled.",
        seizure_frequency_number="no seizure frequency reference",
    ).with_inputs("note_text")

    clean_no_reference = dspy.Prediction(
        seizure_frequency_number="no seizure frequency reference",
        evidence_text=None,
    )
    hallucinated_evidence = dspy.Prediction(
        seizure_frequency_number="no seizure frequency reference",
        evidence_text="appointment was cancelled",
    )

    assert gan_frequency_s0_semantic_evidence_metric(example, clean_no_reference) == 1.0
    assert gan_frequency_s0_semantic_evidence_metric(example, hallucinated_evidence) == 0.0


def test_gan_frequency_s0_semantic_evidence_feedback_metric_reports_partial_credit():
    example = dspy.Example(
        note_text="He reports 4 focal seizures per week despite medication.",
        seizure_frequency_number="4 per week",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="3 per week",
        evidence_text="4 focal seizures per week",
    )

    result = gan_frequency_s0_semantic_evidence_feedback_metric(example, pred)

    assert result.score == 0.65
    assert "[purist-category]" in result.feedback


def test_gan_frequency_s0_synthesis_metric_requires_quote_when_gold_evidence_is_paraphrased():
    example = dspy.Example(
        note_text="History: she reports one seizure per month since March.",
        seizure_frequency_number="1 per 1 month",
        evidence_text="Patient has monthly seizures after March.",
    ).with_inputs("note_text")
    exact_with_source_quote = dspy.Prediction(
        seizure_frequency_number="1 per 1 month",
        evidence_text="one seizure per month",
    )
    exact_missing_quote = dspy.Prediction(
        seizure_frequency_number="1 per 1 month",
        evidence_text=None,
    )
    exact_with_paraphrase = dspy.Prediction(
        seizure_frequency_number="1 per 1 month",
        evidence_text="Patient has monthly seizures after March.",
    )

    assert gan_frequency_s0_synthesis_metric(example, exact_with_source_quote) == 1.0
    assert gan_frequency_s0_synthesis_metric(example, exact_missing_quote) == 0.0
    assert gan_frequency_s0_synthesis_metric(example, exact_with_paraphrase) == 0.0


def test_gan_frequency_s0_synthesis_metric_allows_no_reference_without_quote():
    example = dspy.Example(
        note_text="This administrative letter confirms the appointment was cancelled.",
        seizure_frequency_number="no seizure frequency reference",
        evidence_text=None,
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="no seizure frequency reference",
        evidence_text=None,
    )

    assert gan_frequency_s0_synthesis_metric(example, pred) == 1.0


def test_gan_frequency_s0_synthesis_metric_rejects_no_reference_paraphrase():
    example = dspy.Example(
        note_text="This administrative letter confirms the appointment was cancelled.",
        seizure_frequency_number="no seizure frequency reference",
        evidence_text=None,
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="no seizure frequency reference",
        evidence_text="No direct mention of seizure frequency is present.",
    )

    assert gan_frequency_s0_synthesis_metric(example, pred) == 0.0


def test_gan_frequency_s0_synthesis_feedback_metric_accepts_exact_label_and_quote():
    example = dspy.Example(
        note_text="He reports 3 focal seizures per week despite medication.",
        seizure_frequency_number="3 per week",
        evidence_text="3 focal seizures per week",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="3 per week",
        evidence_text="3 focal seizures per week",
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score == 1.0
    assert "matched the normalized Gan label and evidence policy" in result.feedback


def test_gan_frequency_s0_synthesis_feedback_metric_flags_invalid_forbidden_unit():
    example = dspy.Example(
        note_text="Over the last quarter she had two to three seizures per month.",
        seizure_frequency_number="2 to 3 per month",
        evidence_text="two to three seizures per month",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="2 to 3 per quarter",
        evidence_text="two to three seizures per month",
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score == 0.0
    assert "invalid-format" in result.feedback
    assert "forbidden-unit" in result.feedback
    assert "quarter" in result.feedback


def test_gan_frequency_s0_synthesis_feedback_metric_flags_cluster_format_failure():
    example = dspy.Example(
        note_text="Diary: one cluster each week, usually three seizures per cluster.",
        seizure_frequency_number="1 cluster per week, multiple per cluster",
        evidence_text="one cluster each week, usually three seizures per cluster",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="1 cluster per week",
        evidence_text="one cluster each week, usually three seizures per cluster",
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score == 0.0
    assert "invalid-format" in result.feedback
    assert "cluster-format" in result.feedback


def test_gan_frequency_s0_synthesis_feedback_metric_flags_pragmatic_and_exact_mismatch():
    example = dspy.Example(
        note_text="She has one seizure every six months.",
        seizure_frequency_number="1 per 6 month",
        evidence_text="one seizure every six months",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="3 per week",
        evidence_text="3 per week",
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score < 0.5
    assert "exact-label" in result.feedback
    assert "pragmatic-category" in result.feedback


def test_gan_frequency_s0_synthesis_feedback_metric_flags_temporal_window_error():
    example = dspy.Example(
        note_text="Year to date she has had two seizures since January.",
        seizure_frequency_number="2 per 5 month",
        evidence_text="two seizures since January",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="2 per year",
        evidence_text="two seizures since January",
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score < 1.0
    assert "temporal-window" in result.feedback
    assert "year-to-date" in result.feedback


def test_gan_frequency_s0_synthesis_feedback_metric_flags_short_seizure_free_threshold():
    example = dspy.Example(
        note_text="She has been seizure free for 3 months after one seizure in the prior 3 months.",
        seizure_frequency_number="1 per 3 month",
        evidence_text="one seizure in the prior 3 months",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="seizure free for 3 month",
        evidence_text="seizure free for 3 months",
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score < 1.0
    assert "seizure-free-threshold" in result.feedback
    assert "6 months or longer" in result.feedback


def test_gan_frequency_s0_synthesis_feedback_metric_flags_missing_evidence():
    example = dspy.Example(
        note_text="The patient has one seizure per month.",
        seizure_frequency_number="1 per month",
        evidence_text="one seizure per month",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="1 per month",
        evidence_text=None,
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score == 0.8
    assert "evidence-support" in result.feedback
    assert "exact contiguous source quote" in result.feedback


def test_gan_frequency_s0_synthesis_feedback_metric_flags_unsupported_quote():
    example = dspy.Example(
        note_text="The patient has two seizures per month.",
        seizure_frequency_number="2 per month",
        evidence_text="two seizures per month",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number="2 per month",
        evidence_text="two monthly seizures",
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score == 0.8
    assert "evidence-support" in result.feedback
    assert "unsupported-quote" in result.feedback


def test_gan_frequency_s0_synthesis_feedback_metric_flags_abstention_failure():
    example = dspy.Example(
        note_text="There are multiple seizures each day.",
        seizure_frequency_number="multiple per day",
        evidence_text="multiple seizures each day",
    ).with_inputs("note_text")
    pred = dspy.Prediction(
        seizure_frequency_number=None,
        evidence_text=None,
    )

    result = gan_frequency_s0_synthesis_feedback_metric(example, pred)

    assert result.score == 0.0
    assert "abstention" in result.feedback
    assert "canonical Gan label" in result.feedback


def test_make_gan_dspy_examples_sets_note_text_as_input_and_gold_label_as_output():
    records = load_gan_records()[:5]
    examples = make_gan_dspy_examples(records)

    assert len(examples) == 5
    for example, record in zip(examples, records):
        assert example.note_text == record.note_text
        assert example.seizure_frequency_number == record.gold_label
        assert "note_text" in example.inputs()


def test_make_gan_synthesis_dspy_examples_includes_gold_evidence_for_optimizer():
    records = [
        r for r in load_gan_records()
        if r.gold_evidence and "..." not in r.gold_evidence and r.gold_evidence in r.note_text
    ][:5]
    examples = make_gan_synthesis_dspy_examples(records)
    records_by_note = {record.note_text: record for record in records}

    assert len(examples) == 5
    for example in examples:
        record = records_by_note[example.note_text]
        assert example.note_text == record.note_text
        assert example.seizure_frequency_number == record.gold_label
        assert example.evidence_text == record.gold_evidence
        assert "note_text" in example.inputs()


def test_make_gan_synthesis_dspy_examples_does_not_use_paraphrased_gold_as_quote():
    record = GanRecord(
        record_id="gan-paraphrase-demo",
        source_row_index=1,
        note_text="History: she reports one seizure per month since March.",
        gold_label="1 per 1 month",
        gold_evidence="Patient has monthly seizures after March.",
        reference_label=None,
        reference_evidence=None,
        row_ok=True,
        labels_match_all_categories=True,
        quotes_ok_all_categories=False,
        flags=["paraphrased_gold_evidence"],
        raw={},
    )

    examples = make_gan_synthesis_dspy_examples([record])

    assert examples[0].evidence_text is None


def test_make_gan_synthesis_dspy_examples_prioritizes_locatable_evidence():
    records = load_gan_records()
    examples = make_gan_synthesis_dspy_examples(records[:50])

    first = examples[0]
    assert first.seizure_frequency_number != "no seizure frequency reference"
    assert first.evidence_text
    assert "..." not in first.evidence_text
    assert first.evidence_text in first.note_text


def test_compile_gan_s0_module_labeled_fewshot_returns_callable_module():
    records = load_gan_records()[:4]
    compiled = compile_gan_s0_module(
        records,
        optimizer_name="LabeledFewShot",
        max_labeled_demos=2,
    )

    assert isinstance(compiled, GanFrequencyS0Module)
    _, predictor = compiled.named_predictors()[0]
    assert len(predictor.demos) == 2


def test_compile_gan_s0_module_labeled_fewshot_compiles_verify_repair_extractor_only():
    records = load_gan_records()[:4]
    compiled = compile_gan_s0_module(
        records,
        program_variant=GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
        optimizer_name="LabeledFewShot",
        max_labeled_demos=2,
        optimizer_metric="synthesis_exact_with_evidence",
    )

    assert isinstance(compiled, GanFrequencyS0VerifyRepairModule)
    extractor_predictors = compiled.extractor.named_predictors()
    assert len(extractor_predictors) == 1
    _, extractor = extractor_predictors[0]
    assert len(extractor.demos) == 2

    _, verifier = compiled.verifier.named_predictors()[0]
    assert not getattr(verifier, "demos", None)


def test_compile_gan_s0_module_bootstrap_rs_uses_random_search_optimizer(monkeypatch):
    records = load_gan_records()[:2]
    captured: dict[str, object] = {}

    class FakeBootstrapRS:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def compile(self, module, trainset):
            captured["trainset"] = trainset
            return module

    monkeypatch.setattr(dspy, "BootstrapFewShotWithRandomSearch", FakeBootstrapRS)

    compile_gan_s0_module(
        records,
        optimizer_name="BootstrapFewShotWithRandomSearch",
        num_candidate_programs=6,
        optimizer_metric="pragmatic_category",
    )

    assert captured["num_candidate_programs"] == 6
    assert captured["trainset"] is not None


def test_compile_gan_s0_module_bootstrap_returns_callable_module():
    """BootstrapFewShot compilation with DummyLM produces a callable compiled module."""
    records = load_gan_records()[:4]
    # Supply one correct response per bootstrap teacher call plus one for the prediction call.
    # follow_cycles=True guards against off-by-one in bootstrap internal calls.
    answers = [
        {
            "reasoning": "Found seizure frequency in note.",
            "seizure_frequency_number": r.gold_label,
            "evidence_text": None,
        }
        for r in records
    ]
    # Provide enough answers: one per bootstrap teacher call plus extra for prediction.
    answers = answers * 4
    _configure_dummy(answers)

    compiled = compile_gan_s0_module(
        records,
        max_bootstrapped_demos=2,
        max_labeled_demos=0,
        max_rounds=1,
    )

    assert isinstance(compiled, GanFrequencyS0Module)

    result = predict_gan_records(
        compiled,
        [records[0]],
        model_provider="mock",
        model_name="dummy-bootstrap",
        prompt_version="gan_frequency_s0_bootstrap_v1",
    )
    assert result.dataset == "gan_2026"
    assert len(result.predictions) == 1
    assert result.metadata["program_variant"] == GAN_FREQUENCY_S0_VARIANT


def test_compile_gan_s0_module_gepa_uses_reflection_lm(monkeypatch):
    records = load_gan_records()[:2]
    captured: dict[str, object] = {}
    configured_lm = DummyLM(
        answers=[
            {
                "seizure_frequency_number": records[0].gold_label,
                "evidence_text": None,
            }
        ]
    )

    class FakeGEPA:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        def compile(self, module, trainset):
            captured["module"] = module
            captured["trainset"] = trainset
            return module

    monkeypatch.setattr(dspy, "GEPA", FakeGEPA)
    dspy.configure(lm=configured_lm)

    compiled = compile_gan_s0_module_gepa(records)

    assert isinstance(compiled, GanFrequencyS0DirectModule)
    assert captured["reflection_lm"] is configured_lm
    assert captured["gepa_kwargs"] == {"use_cloudpickle": False}
    assert len(captured["trainset"]) == 2


def test_gan_frequency_s0_run_metadata_builds_correct_artifact_contract():
    metadata = gan_frequency_s0_run_metadata(
        run_id="gan_s0_dspy_test",
        split_name="gan_2026_fixed_v1:validation",
        model_provider="mock",
        model_name="dummy",
    )

    assert metadata.dataset == "gan_2026"
    assert metadata.split_name == "gan_2026_fixed_v1:validation"
    assert metadata.model_provider == "mock"
    assert metadata.model_name == "dummy"
    assert metadata.schema_level == GAN_FREQUENCY_S0_SCHEMA_LEVEL
    assert metadata.program_variant == GAN_FREQUENCY_S0_VARIANT
    assert metadata.scorer_mode == "gan_frequency_deterministic_v1"
    assert "monthly-frequency" in " ".join(metadata.metric_caveats).lower()


def test_gan_frequency_s0_run_metadata_accepts_direct_variant():
    metadata = gan_frequency_s0_run_metadata(
        run_id="gan_s0_direct_dspy_test",
        split_name="gan_2026_fixed_v1:validation",
        model_provider="mock",
        model_name="dummy",
        program_variant=GAN_FREQUENCY_S0_DIRECT_VARIANT,
    )

    assert metadata.program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT


def test_gan_s0_verifier_signature_documents_v2_4_policy_guardrails():
    doc = (GanFrequencyS0VerifierSignature.__doc__ or "").lower()

    assert "seizure free for" in doc
    assert "6 month" in doc
    assert "last resort" in doc
    assert "preserve" in doc and "evidence" in doc
    assert "1 per 3 week" in doc or "per 3 week" in doc
    assert "confirm-first" in doc or "confirm first" in doc
    assert "year-to-date" in doc or "year to date" in doc
    assert "multiple per cluster" in doc
    assert "count" in doc and "window" in doc
    assert "infrequent quantified" in doc
    assert "do not repair unknown to no seizure frequency reference" in doc
    assert GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION.endswith("_v2_4")


def test_gan_s0_verify_repair_module_runs_extraction_then_verification():
    record = next(
        r for r in load_gan_records()
        if r.gold_evidence and r.gold_evidence in r.note_text
    )
    _configure_dummy([
        {
            "seizure_frequency_number": "1 cluster per week",
            "evidence_text": "one cluster each week",
        },
        {
            "final_label": "1 cluster per week, 3 per cluster",
            "final_evidence": "one cluster each week, usually three seizures per cluster",
            "decision": "repair",
            "reason": "Initial cluster label was missing the per-cluster count.",
        },
    ])

    module = GanFrequencyS0VerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    )

    assert prediction_set.metadata["program_variant"] == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    pred = prediction_set.predictions[0]
    assert pred.metadata["program_variant"] == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT
    assert pred.metadata["verifier_decision"] == "repair"
    assert "per-cluster count" in pred.metadata["verifier_reason"]
    assert pred.metadata["initial_label"] == "1 cluster per week"
    assert pred.values[0].raw_value == "1 cluster per week, 3 per cluster"


def test_gan_s0_verify_repair_module_confirms_valid_prediction():
    record = next(
        r for r in load_gan_records()
        if r.gold_evidence and r.gold_evidence in r.note_text
    )
    _configure_dummy([
        {
            "seizure_frequency_number": record.gold_label,
            "evidence_text": record.gold_evidence,
        },
        {
            "final_label": record.gold_label,
            "final_evidence": record.gold_evidence,
            "decision": "confirm",
            "reason": "Initial prediction matches the note exactly.",
        },
    ])

    module = GanFrequencyS0VerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "confirm"
    assert pred.values[0].normalized_value == record.gold_label


def test_gan_s0_temporal_candidates_verify_repair_passes_candidates_to_verifier():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    _configure_dummy([
        {
            "seizure_frequency_number": "unknown",
            "evidence_text": "no seizures for nearly a year",
        },
        {
            "final_label": "1 per year",
            "final_evidence": (
                "no seizures for nearly a year before a single breakthrough tonic seizure"
            ),
            "decision": "repair",
            "reason": "Temporal candidate matches breakthrough-after-year window.",
            "temporal_candidates": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0TemporalCandidatesVerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "repair"
    assert pred.metadata["temporal_candidate_labels"] == ["1 per year"]
    assert pred.metadata["temporal_candidate_records"][0]["canonical_label"] == "1 per year"
    assert pred.values[0].raw_value == "1 per year"


def test_gan_s0_temporal_verify_repair_confirm_first_preserves_ytd_initial():
    record = next(r for r in load_gan_records() if r.record_id == "gan_12810")
    _configure_dummy([
        {
            "seizure_frequency_number": "5 per 2 month",
            "evidence_text": "five seizures this year to date",
        },
        {
            "final_label": "5 per year",
            "final_evidence": "five seizures this year to date",
            "decision": "repair",
            "reason": "Verifier incorrectly prefers annual denominator.",
            "temporal_candidates": "none",
        },
    ])

    module = GanFrequencyS0TemporalCandidatesVerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "confirm"
    assert pred.values[0].raw_value == "5 per 2 month"


def test_gan_s0_temporal_verify_repair_confirm_first_preserves_cluster_initial():
    record = next(r for r in load_gan_records() if r.record_id == "gan_10003")
    _configure_dummy([
        {
            "seizure_frequency_number": "1 cluster per week, multiple per cluster",
            "evidence_text": "weekly clusters with multiple seizures per cluster",
        },
        {
            "final_label": "1 cluster per week",
            "final_evidence": "weekly clusters with multiple seizures per cluster",
            "decision": "confirm",
            "reason": "Verifier paraphrased cluster label.",
            "temporal_candidates": "none",
        },
    ])

    module = GanFrequencyS0TemporalCandidatesVerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "confirm"
    assert pred.values[0].raw_value == "1 cluster per week, multiple per cluster"


def test_gan_s0_temporal_verify_repair_candidate_gated_repair_from_unknown():
    record = next(r for r in load_gan_records() if r.record_id == "gan_14881")
    _configure_dummy([
        {
            "seizure_frequency_number": "unknown",
            "evidence_text": "His last episode was recorded on 26 February",
        },
        {
            "final_label": "seizure free for 3 weeks",
            "final_evidence": "remained well since",
            "decision": "repair",
            "reason": "Verifier chose short seizure-free interval.",
            "temporal_candidates": "ignored",
        },
    ])

    module = GanFrequencyS0TemporalCandidatesVerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "repair"
    assert pred.values[0].raw_value == "1 per month"


def test_gan_s0_temporal_verify_repair_blocks_short_seizure_free_from_unknown():
    record = next(r for r in load_gan_records() if r.record_id == "gan_11221")
    _configure_dummy([
        {
            "seizure_frequency_number": "unknown",
            "evidence_text": "Last seizure on 30/5/2020",
        },
        {
            "final_label": "seizure free for 4 months",
            "final_evidence": "Last seizure on 30/5/2020",
            "decision": "repair",
            "reason": "Verifier over-repaired last-event date to seizure-free.",
            "temporal_candidates": "none",
        },
    ])

    module = GanFrequencyS0TemporalCandidatesVerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "confirm"
    assert pred.values[0].raw_value == "unknown"


def test_gan_s0_verify_repair_module_abstains_when_uncertain():
    record = load_gan_records()[0]
    _configure_dummy([
        {
            "seizure_frequency_number": "2 per week",
            "evidence_text": "two seizures per week",
        },
        {
            "final_label": None,
            "final_evidence": None,
            "decision": "abstain",
            "reason": "The note does not clearly support a quantified frequency.",
        },
    ])

    module = GanFrequencyS0VerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "abstain"
    assert pred.values[0].raw_value is None
    assert "abstained" in pred.values[0].quality_flags


def test_gan_s0_verifier_module_is_callable_standalone():
    _configure_dummy([{
        "final_label": "3 per week",
        "final_evidence": "three seizures weekly",
        "decision": "repair",
        "reason": "Corrected denominator.",
    }])

    verifier = GanFrequencyS0VerifierModule()
    result = verifier(
        note_text="Patient reports three seizures every week.",
        initial_label="3 per month",
        initial_evidence="three seizures every week",
    )

    assert result.final_label == "3 per week"
    assert result.decision == "repair"
    assert result.reason == "Corrected denominator."


def test_gan_frequency_s0_signature_documents_qwen_direct_policy_boundaries():
    doc = GanFrequencyS0Signature.__doc__ or ""
    assert "Unknown vs no seizure frequency reference" in doc
    assert "no-clinical-content" in doc
    assert "highest current" in doc
    assert "Year-to-date" in doc or "year to date" in doc.lower()
    assert "NEVER use \"N per year\"" in doc
    assert "multiple per cluster" in doc
    assert "Do NOT output" in doc
    assert "output unknown — never null" in doc
    assert "Quantified rates beat unknown" in doc
    assert "Do NOT collapse low-frequency quantified counts to unknown" in doc
    assert "Never use hour" in doc
    assert "Infrequent explicit" in doc or "infrequent" in doc.lower()
    assert "multiple per unit" in doc
    assert "admin/scheduling-only" in doc.lower() or "administrative" in doc.lower()

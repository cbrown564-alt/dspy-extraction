import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_FIELD,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_VARIANT,
    GanFrequencyS0Module,
    compile_gan_s0_module,
    gan_frequency_s0_metric,
    gan_frequency_s0_synthesis_metric,
    gan_frequency_s0_run_metadata,
    make_gan_dspy_examples,
    make_gan_synthesis_dspy_examples,
    predict_gan_records,
)


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


def test_make_gan_synthesis_dspy_examples_prioritizes_locatable_evidence():
    records = load_gan_records()
    examples = make_gan_synthesis_dspy_examples(records[:50])

    first = examples[0]
    assert first.seizure_frequency_number != "no seizure frequency reference"
    assert first.evidence_text
    assert "..." not in first.evidence_text
    assert first.evidence_text in first.note_text


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

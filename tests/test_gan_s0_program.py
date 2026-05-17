from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_FIELD,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_VARIANT,
    GanFrequencyS0Output,
    GanFrequencyS0Program,
)


def test_gan_s0_program_maps_mocked_output_to_prediction_set_with_evidence_offsets():
    record = next(
        record
        for record in load_gan_records()
        if record.gold_evidence and record.gold_evidence in record.note_text
    )

    def mock_extract(input_record):
        assert input_record.record_id == record.record_id
        assert input_record.note_text == record.note_text
        return GanFrequencyS0Output(
            seizure_frequency_number=record.gold_label,
            evidence_text=record.gold_evidence,
            confidence=0.91,
        )

    program = GanFrequencyS0Program(
        extractor=mock_extract,
        model_provider="mock",
        model_name="gold-label-fixture",
    )

    prediction_set = program.predict_records([record])

    assert prediction_set.dataset == "gan_2026"
    assert prediction_set.schema_level == GAN_FREQUENCY_S0_SCHEMA_LEVEL
    assert prediction_set.metadata["program_variant"] == GAN_FREQUENCY_S0_VARIANT
    assert prediction_set.metadata["model_provider"] == "mock"
    prediction = prediction_set.predictions[0]
    assert prediction.metadata["prompt_config"]["signature"] == "GanFrequencyS0Signature"
    value = prediction.values[0]
    assert value.field_name == GAN_FREQUENCY_S0_FIELD
    assert value.raw_value == record.gold_label
    assert value.normalized_value == record.gold_label
    assert value.confidence == 0.91
    assert value.evidence[0].text == record.gold_evidence
    assert record.note_text[value.evidence[0].start : value.evidence[0].end] == record.gold_evidence


def test_gan_s0_program_records_abstention_without_fabricating_label_or_evidence():
    record = load_gan_records()[0]
    program = GanFrequencyS0Program(
        extractor=lambda _input_record: GanFrequencyS0Output(
            seizure_frequency_number=None,
            evidence_text=None,
            abstained=True,
        ),
        model_provider="mock",
        model_name="abstain-fixture",
    )

    prediction_set = program.predict_records([record])

    value = prediction_set.predictions[0].values[0]
    assert value.field_name == GAN_FREQUENCY_S0_FIELD
    assert value.raw_value is None
    assert value.normalized_value is None
    assert value.evidence == []
    assert value.quality_flags == ["abstained"]


def test_gan_s0_program_builds_run_metadata_for_artifact_contract():
    program = GanFrequencyS0Program(
        extractor=lambda _input_record: GanFrequencyS0Output(
            seizure_frequency_number="unknown",
            evidence_text="",
        ),
        model_provider="mock",
        model_name="fixture",
    )

    metadata = program.run_metadata(
        run_id="gan_s0_mock_run",
        split_name="gan_2026_fixed_v1:validation",
    )

    assert metadata.dataset == "gan_2026"
    assert metadata.split_name == "gan_2026_fixed_v1:validation"
    assert metadata.model_provider == "mock"
    assert metadata.model_name == "fixture"
    assert metadata.schema_level == GAN_FREQUENCY_S0_SCHEMA_LEVEL
    assert metadata.program_variant == GAN_FREQUENCY_S0_VARIANT
    assert metadata.scorer_mode == "gan_frequency_deterministic_v1"
    assert "monthly-frequency" in " ".join(metadata.metric_caveats).lower()

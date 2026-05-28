import dspy

from clinical_extraction.gan.s0.prediction_bridge import (
    apply_gan_s0_evidence_span_check_guard,
    guard_gan_s0_evidence_text,
    predict_gan_records,
)
from clinical_extraction.gan.s0.variant_routing import (
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_FIELD,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    stage_graph_id_for_program_variant,
)
from clinical_extraction.schemas import GanRecord


class StubGanS0Module:
    def __init__(self, prediction: dspy.Prediction) -> None:
        self.prediction = prediction

    def __call__(self, *, note_text: str) -> dspy.Prediction:
        return self.prediction


def test_gan_s0_stage_routing_and_artifact_assembly_are_public_surfaces():
    record = GanRecord(
        record_id="gan-stage-fixture",
        source_row_index=1,
        note_text="Her seizures are now daily.",
        gold_label="1 per day",
        gold_evidence="daily",
        reference_label="1 per day",
        reference_evidence="daily",
        row_ok=True,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        raw={},
    )

    prediction_set = predict_gan_records(
        StubGanS0Module(
            dspy.Prediction(
                seizure_frequency_number="daily",
                evidence_text='"daily"',
            )
        ),
        [record],
        model_provider="mock",
        model_name="stage-fixture",
        prompt_version="gan_frequency_s0_direct_guardrails_v2_2",
        program_variant=GAN_FREQUENCY_S0_DIRECT_VARIANT,
    )

    prediction = prediction_set.predictions[0]
    value = prediction.values[0]

    assert prediction_set.dataset == "gan_2026"
    assert prediction_set.schema_level == GAN_FREQUENCY_S0_SCHEMA_LEVEL
    assert prediction_set.metadata["scorer_mode"] == GAN_FREQUENCY_S0_SCORER
    assert prediction.metadata["program_variant"] == GAN_FREQUENCY_S0_DIRECT_VARIANT
    assert value.field_name == GAN_FREQUENCY_S0_FIELD
    assert value.raw_value == "daily"
    assert value.normalized_value == "1 per day"
    assert value.evidence[0].text == "daily"
    assert value.evidence[0].start == record.note_text.index("daily")
    assert "normalized_label_repaired" in value.quality_flags
    assert "evidence_repaired:outer_quotes_stripped" in value.quality_flags
    assert (
        stage_graph_id_for_program_variant(
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT
        )
        == "g2_candidates_adjudicate"
    )


def test_gan_s0_evidence_guard_repairs_to_note_local_quote():
    note_text = "Current pattern: two seizures every month after sleep deprivation."

    repaired, flags = guard_gan_s0_evidence_text(
        note_text,
        '"Current pattern: two seizures every month after sleep deprivation."',
    )

    assert repaired == "Current pattern: two seizures every month after sleep deprivation."
    assert flags == ["evidence_repaired:outer_quotes_stripped"]


def test_gan_s0_span_check_guard_preserves_supported_initial_prediction():
    guarded = apply_gan_s0_evidence_span_check_guard(
        "Current pattern: two seizures every month.",
        dspy.Prediction(
            final_label="1 per month",
            final_evidence="not a quote in this note",
            decision="repair",
            reason="unsupported verifier repair",
        ),
        initial_label="2 per month",
        initial_evidence="two seizures every month",
    )

    assert guarded.final_label == "2 per month"
    assert guarded.final_evidence == "two seizures every month"
    assert guarded.decision == "confirm"
    assert "preserved initial prediction" in guarded.reason

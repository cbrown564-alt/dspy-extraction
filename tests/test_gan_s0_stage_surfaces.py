from types import SimpleNamespace

import dspy

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.s0.prediction_bridge import (
    apply_gan_s0_constrained_verifier_guard,
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


def test_gan_s0_evidence_guard_selects_locatable_ellipsis_segment():
    note_text = (
        "facial twitching. A second event occurred in Italy the following "
        "July 2019, once more during the night, lasting four minutes. "
        "Since returning to the UK, there have been no further events reported."
    )
    spliced = (
        '"A second event occurred in Italy the following July 2019... '
        'Since returning to the UK, there have been no further events reported."'
    )

    repaired, flags = guard_gan_s0_evidence_text(note_text, spliced)

    assert repaired in note_text
    assert repaired.startswith("Since returning to the UK")
    assert "evidence_repaired:outer_quotes_stripped" in flags
    assert "evidence_repaired:ellipsis_segment_selected" in flags


def test_gan_s0_evidence_guard_prefers_longest_temporal_candidate_fallback():
    note_text = (
        "Seizure history: His initial event was in April 2019 in Germany, arising "
        "from sleep. He awoke with jerking. A second event occurred in Italy the "
        "following July 2019, once more during the night, lasting four minutes."
    )
    bad_summary = (
        '"A second event occurred in Italy the following July 2019... '
        'Since returning to the UK, there have been no further events reported."'
    )
    candidate_span = (
        "His initial event was in April 2019 in Germany, arising from sleep. "
        "He awoke with jerking. A second event occurred in Italy the following "
        "July 2019, once more during the night, lasting four minutes."
    )

    repaired, flags = guard_gan_s0_evidence_text(
        note_text,
        bad_summary,
        fallback_evidence_texts=[candidate_span],
    )

    assert repaired == candidate_span
    assert "evidence_repaired:temporal_candidate_fallback" in flags


def test_gan_s0_evidence_guard_repairs_gpt_temporal_cap25_failure_snippets():
    by_id = {record.record_id: record for record in load_gan_records()}
    cases = [
        (
            "gan_12679",
            '"he continues to suffer one to two generalised tonic-clonic seizures per month"',
        ),
        (
            "gan_16251",
            '"She had 7 convulsions so far in Sep, 4 in Aug, 2 in Jul, one in Jun"',
        ),
        (
            "gan_16825",
            '"In October he had six nocturnal seizures"',
        ),
    ]

    for record_id, quoted in cases:
        record = by_id[record_id]
        repaired, _flags = guard_gan_s0_evidence_text(record.note_text, quoted)

        assert repaired in record.note_text, record_id


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


def test_gan_s0_constrained_verifier_guard_preserves_allowed_labels():
    note_text = "Patient has 3 seizures per week."
    candidates = [
        SimpleNamespace(canonical_label="3 per week", evidence_text="3 seizures per week")
    ]

    candidate_label = apply_gan_s0_constrained_verifier_guard(
        note_text=note_text,
        verified=dspy.Prediction(final_label="3 per week", decision="confirm", reason="ok"),
        candidates=candidates,
        initial_label="unknown",
        initial_evidence="no reference",
    )
    initial_label = apply_gan_s0_constrained_verifier_guard(
        note_text=note_text,
        verified=dspy.Prediction(final_label="1 per month", decision="confirm", reason="ok"),
        candidates=candidates,
        initial_label="1 per month",
        initial_evidence="monthly events",
    )
    unknown_label = apply_gan_s0_constrained_verifier_guard(
        note_text=note_text,
        verified=dspy.Prediction(final_label="unknown", decision="confirm", reason="ok"),
        candidates=candidates,
        initial_label="3 per week",
        initial_evidence="3 seizures per week",
    )

    assert candidate_label.final_label == "3 per week"
    assert candidate_label.final_evidence == "3 seizures per week"
    assert candidate_label.decision == "confirm"
    assert initial_label.final_label == "1 per month"
    assert initial_label.final_evidence == "monthly events"
    assert initial_label.decision == "confirm"
    assert unknown_label.final_label == "unknown"
    assert unknown_label.final_evidence is None
    assert unknown_label.decision == "confirm"


def test_gan_s0_constrained_verifier_guard_reverts_close_matches():
    note_text = "Patient has 3 seizures per week."
    candidates = [
        SimpleNamespace(canonical_label="3 per week", evidence_text="3 seizures per week")
    ]

    candidate_match = apply_gan_s0_constrained_verifier_guard(
        note_text=note_text,
        verified=dspy.Prediction(final_label="3 per wk", decision="confirm", reason="ok"),
        candidates=candidates,
        initial_label="unknown",
        initial_evidence=None,
    )
    initial_match = apply_gan_s0_constrained_verifier_guard(
        note_text=note_text,
        verified=dspy.Prediction(final_label="1 per mon", decision="confirm", reason="ok"),
        candidates=candidates,
        initial_label="1 per month",
        initial_evidence="monthly events",
    )

    assert candidate_match.final_label == "3 per week"
    assert candidate_match.final_evidence == "3 seizures per week"
    assert candidate_match.decision == "repair"
    assert "reverted to closest match" in candidate_match.reason
    assert initial_match.final_label == "1 per month"
    assert initial_match.final_evidence == "monthly events"
    assert initial_match.decision == "repair"


def test_gan_s0_constrained_verifier_guard_fallbacks():
    note_text = "Patient has 3 seizures per week."
    candidates = [
        SimpleNamespace(canonical_label="3 per week", evidence_text="3 seizures per week")
    ]

    initial_fallback = apply_gan_s0_constrained_verifier_guard(
        note_text=note_text,
        verified=dspy.Prediction(final_label="rarely", decision="confirm", reason="ok"),
        candidates=candidates,
        initial_label="3 per week",
        initial_evidence="3 seizures per week",
    )
    unknown_fallback = apply_gan_s0_constrained_verifier_guard(
        note_text=note_text,
        verified=dspy.Prediction(final_label="rarely", decision="confirm", reason="ok"),
        candidates=candidates,
        initial_label=None,
        initial_evidence=None,
    )

    assert initial_fallback.final_label == "3 per week"
    assert initial_fallback.final_evidence == "3 seizures per week"
    assert initial_fallback.decision == "repair"
    assert "fallback to" in initial_fallback.reason
    assert unknown_fallback.final_label == "unknown"
    assert unknown_fallback.final_evidence is None
    assert unknown_fallback.decision == "repair"
    assert "fallback to" in unknown_fallback.reason

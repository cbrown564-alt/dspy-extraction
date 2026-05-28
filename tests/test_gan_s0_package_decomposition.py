"""Characterization tests for the Gan S0 package decomposition."""

import json

import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.s0 import modules
from clinical_extraction.gan.s0 import prediction_bridge, variant_routing


@pytest.fixture(autouse=True)
def reset_dspy_settings():
    yield
    dspy.settings.configure(lm=None)


def _configure_dummy(answers: list[dict]) -> None:
    dspy.configure(lm=DummyLM(answers=answers))


def test_builder_gap_v1_fixed_record_parity_after_package_split():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    _configure_dummy(
        [
            {
                "seizure_frequency_number": "1 per year",
                "evidence_text": "no seizures for nearly a year",
                "temporal_candidates": "ignored by DummyLM",
            }
        ]
    )

    module = modules.build_gan_s0_module(
        variant_routing.GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
        prompt_version=(
            variant_routing.GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_ERROR_TAXONOMY_PROMPT_VERSION
        ),
    )
    prediction_set = prediction_bridge.predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="builder-gap-v1-fixture",
        program_variant=variant_routing.GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
        prompt_version=(
            variant_routing.GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_ERROR_TAXONOMY_PROMPT_VERSION
        ),
    )

    prediction = prediction_set.predictions[0]
    assert isinstance(module, modules.GanFrequencyS0TemporalCandidatesSinglePassModule)
    assert prediction.values[0].normalized_value == "1 per year"
    assert "1 per year" in prediction.metadata["temporal_candidate_labels"]
    assert prediction.metadata["temporal_candidate_source"] == "deterministic"
    assert prediction_set.metadata["prompt_version"] == (
        variant_routing.GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_ERROR_TAXONOMY_PROMPT_VERSION
    )


def test_d1_v1_2b_fixed_record_parity_after_package_split():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    _configure_dummy(
        [
            {
                "seizure_frequency_number": "1 per year",
                "evidence_text": "no seizures for nearly a year",
            }
        ]
    )

    module = modules.build_gan_s0_module(
        variant_routing.GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
        prompt_version=(
            variant_routing.GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_V1_2B_SCHEMA_GUARD_ONLY_PROMPT_VERSION
        ),
    )
    result = module(record.note_text)
    payload = json.loads(result.date_event_payload)

    assert isinstance(module, modules.GanFrequencyS0DateEventsCandidatesSinglePassModule)
    assert result.seizure_frequency_number == "1 per year"
    assert result.temporal_candidate_labels == payload["candidate_labels"]
    assert "1 per year" in payload["candidate_labels"]
    assert payload["stage_confidence"] == 1.0


def test_active_gan_factory_rejects_historical_arms_without_archive_opt_in():
    with pytest.raises(ValueError, match="archive-only"):
        modules.build_gan_s0_module(
            variant_routing.GAN_FREQUENCY_S0_DIRECT_VARIANT,
        )

    module = modules.build_gan_s0_module(
        variant_routing.GAN_FREQUENCY_S0_DIRECT_VARIANT,
        include_archive=True,
    )

    assert isinstance(module, modules.GanFrequencyS0DirectModule)

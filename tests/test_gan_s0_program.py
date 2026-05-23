import dspy
import pytest
from dspy.utils import DummyLM

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.gan.temporal_candidates import (
    build_temporal_frequency_candidates_from_note,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    _guard_evidence_text,
    _prompt_note_text_for_context_policy,
    GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY,
    GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES,
    GAN_FREQUENCY_S0_RETRIEVAL_EMPTY_CANDIDATES_NOTE_STUB,
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_FIELD,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_VARIANT,
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    GanFrequencyS0DirectModule,
    GanFrequencyS0Module,
    GanFrequencyS0ReactTemporalToolsModule,
    GanFrequencyS0Signature,
    GanFrequencyS0TemporalCandidatesVerifyRepairModule,
    GanFrequencyS0TemporalCandidatesSinglePassModule,
    GanFrequencyS0LlmTemporalCandidatesSinglePassModule,
    GanFrequencyS0HybridTemporalCandidatesSinglePassModule,
    GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairModule,
    GanFrequencyS0TemporalCandidatesAdjudicateConstrainedVerifierModule,
    _apply_constrained_verifier_guard,
    GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule,
    GanFrequencyS0TemporalCandidatesAdjudicateDetEvidenceModule,
    GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule,
    GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairNoGuardsModule,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT,
    GanFrequencyS0LlmTemporalCandidatesVerifyRepairModule,
    GanFrequencyS0TemporalEventTableVerifyRepairModule,
    GanFrequencyS0TemporalEventTableSinglePassModule,
    GanFrequencyS0MultipleAnswerDetSelectorModule,
    GanFrequencyS0VerifyRepairModule,
    GanFrequencyS0VerifierModule,
    GanFrequencyS0VerifierSignature,
    GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION,
    GAN_FREQUENCY_S0_GUARDRAILS_PORT_TEMPORAL_PROMPT_VERSION,
    GAN_FREQUENCY_S0_SYNTHESIS_PORT_TEMPORAL_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_ERROR_TAXONOMY_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_TARGETED_EXAMPLES_MIN7_PROMPT_VERSION,
    GanFrequencyS0TemporalAdjudicateSignature,
    select_gan_multiple_answer_option,
    stage_graph_id_for_program_variant,
    _apply_evidence_span_check_guard,
    build_gan_frequency_s0_extractor_signature,
    build_gan_frequency_s0_verifier_signature,
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
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT),
        GanFrequencyS0TemporalCandidatesSinglePassModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT),
        GanFrequencyS0LlmTemporalCandidatesSinglePassModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT),
        GanFrequencyS0HybridTemporalCandidatesSinglePassModule,
    )
    assert isinstance(
        build_gan_s0_module(
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT
        ),
        GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT),
        GanFrequencyS0LlmTemporalCandidatesVerifyRepairModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT),
        GanFrequencyS0ReactTemporalToolsModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT),
        GanFrequencyS0TemporalEventTableSinglePassModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT),
        GanFrequencyS0MultipleAnswerDetSelectorModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT),
        GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT),
        GanFrequencyS0TemporalCandidatesAdjudicateDetEvidenceModule,
    )
    assert isinstance(
        build_gan_s0_module(GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT),
        GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule,
    )
    assert isinstance(
        build_gan_s0_module(
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT
        ),
        GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairNoGuardsModule,
    )
    assert isinstance(
        build_gan_s0_module(
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT
        ),
        GanFrequencyS0TemporalCandidatesAdjudicateConstrainedVerifierModule,
    )


def test_stage_graph_id_for_program_variant_maps_known_variants():
    assert stage_graph_id_for_program_variant(GAN_FREQUENCY_S0_DIRECT_VARIANT) == "g1_direct"
    assert (
        stage_graph_id_for_program_variant(GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT)
        == "g2_extract_repair"
    )
    assert (
        stage_graph_id_for_program_variant(
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT
        )
        == "g2_candidates_adjudicate"
    )
    assert (
        stage_graph_id_for_program_variant(
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT
        )
        == "g2_candidates_adjudicate"
    )
    assert (
        stage_graph_id_for_program_variant(
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT
        )
        == "g3_candidates_extract_repair"
    )
    assert (
        stage_graph_id_for_program_variant(
            GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT
        )
        == "g2_candidates_adjudicate"
    )
    assert (
        stage_graph_id_for_program_variant(
            GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT
        )
        == "g2_candidates_adjudicate"
    )
    assert (
        stage_graph_id_for_program_variant(
            GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT
        )
        == "g2_candidates_adjudicate"
    )


def test_gan_s0_error_taxonomy_prompt_patch_adds_candidate_override_policy():
    signature_cls = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_ERROR_TAXONOMY_PROMPT_VERSION
    )

    prompt_doc = signature_cls.__doc__ or ""

    assert "Error-taxonomy policy patch" in prompt_doc
    assert "Broad Gan grouping rule" in prompt_doc
    assert "Counted events followed by" in prompt_doc
    assert "treat it as the preferred answer" in prompt_doc
    assert "Multiple current seizure types" in prompt_doc
    assert issubclass(signature_cls, GanFrequencyS0TemporalAdjudicateSignature)


def test_gan_s0_compact_hierarchy_prompt_adds_policy_density_arm():
    from clinical_extraction.programs.gan_frequency_s0 import (
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_COMPACT_HIERARCHY_PROMPT_VERSION,
    )

    signature_cls = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_COMPACT_HIERARCHY_PROMPT_VERSION
    )

    prompt_doc = signature_cls.__doc__ or ""

    assert "Compact Gan adjudication hierarchy" in prompt_doc
    assert "policy-density mini-grid" in prompt_doc
    assert "Group multiple recent events" in prompt_doc
    assert "Trigger-conditioned or pattern-only counts" in prompt_doc
    assert "Error-taxonomy policy patch" not in prompt_doc
    assert issubclass(signature_cls, GanFrequencyS0TemporalAdjudicateSignature)


def test_gan_s0_targeted_examples_prompt_adds_min7_example_pack():
    signature_cls = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_TARGETED_EXAMPLES_MIN7_PROMPT_VERSION
    )

    prompt_doc = signature_cls.__doc__ or ""

    assert "Error-taxonomy policy patch" in prompt_doc
    assert "Targeted Gan example pack" in prompt_doc
    assert "targeted_examples_min7_v1" in prompt_doc
    assert "Grouped recent events" in prompt_doc
    assert "Counted events plus short stability" in prompt_doc
    assert "Trigger-conditioned unknown" in prompt_doc
    assert "no seizure frequency reference" in prompt_doc
    assert issubclass(signature_cls, GanFrequencyS0TemporalAdjudicateSignature)


def test_gan_s0_retrieval_candidates_only_context_policy_assembles_evidence_windows():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    candidates = build_temporal_frequency_candidates_from_note(record.note_text)
    prompt_note = _prompt_note_text_for_context_policy(
        record.note_text,
        candidates,
        context_policy=GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY,
    )
    assert prompt_note != record.note_text
    for span in prompt_note.split("\n\n---\n\n"):
        assert span in record.note_text

    empty_prompt = _prompt_note_text_for_context_policy(
        record.note_text,
        [],
        context_policy=GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY,
    )
    assert empty_prompt == GAN_FREQUENCY_S0_RETRIEVAL_EMPTY_CANDIDATES_NOTE_STUB

    module = build_gan_s0_module(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
        context_policy=GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY,
    )
    assert isinstance(module, GanFrequencyS0TemporalCandidatesSinglePassModule)
    assert (
        module.context_policy
        == GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY
    )

    default_module = build_gan_s0_module(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
        context_policy=GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES,
    )
    assert isinstance(default_module, GanFrequencyS0TemporalCandidatesSinglePassModule)
    assert (
        default_module.context_policy
        == GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES
    )


def test_gan_s0_temporal_candidates_single_pass_injects_candidates_without_verifier():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    _configure_dummy([
        {
            "seizure_frequency_number": "1 per year",
            "evidence_text": (
                "no seizures for nearly a year before a single breakthrough tonic seizure"
            ),
            "temporal_candidates": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0TemporalCandidatesSinglePassModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert "verifier_decision" not in pred.metadata
    assert pred.metadata["temporal_candidate_labels"] == ["1 per year"]
    assert pred.values[0].raw_value == "1 per year"


def test_gan_s0_llm_temporal_candidates_single_pass_uses_llm_candidates():
    import json

    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    supported_evidence = (
        "In terms of seizure control, She had no seizures for nearly a year "
        "following initiation of Valproate, then developed myoclonic jerks "
        "leading to a tonic seizure three Saturdays ago"
    )
    candidate_payload = json.dumps(
        {
            "candidates": [
                {
                    "canonical_label": "1 per year",
                    "event_count": "1",
                    "window_count": "1",
                    "window_unit": "year",
                    "evidence_text": supported_evidence,
                    "derivation": "llm_test",
                }
            ]
        }
    )
    _configure_dummy([
        {"temporal_candidates_json": candidate_payload},
        {
            "seizure_frequency_number": "1 per year",
            "evidence_text": supported_evidence,
            "temporal_candidates": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0LlmTemporalCandidatesSinglePassModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["temporal_candidate_source"] == "llm"
    assert pred.metadata["temporal_candidate_labels"] == ["1 per year"]
    assert "verifier_decision" not in pred.metadata


def test_gan_s0_hybrid_temporal_candidates_single_pass_merges_sources():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    _configure_dummy([
        {
            "temporal_candidates_json": (
                '{"candidates": [{"canonical_label": "1 per month", '
                '"event_count": "1", "window_count": "1", "window_unit": "month", '
                '"evidence_text": "about once a month", "derivation": "llm_test"}]}'
            ),
        },
        {
            "seizure_frequency_number": "1 per year",
            "evidence_text": (
                "no seizures for nearly a year before a single breakthrough tonic seizure"
            ),
            "temporal_candidates": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0HybridTemporalCandidatesSinglePassModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["temporal_candidate_source"] == "hybrid"
    assert "1 per year" in pred.metadata["temporal_candidate_labels"]


def test_gan_s0_temporal_candidates_adjudicate_verify_repair_runs_verifier():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    supported_evidence = (
        "In terms of seizure control, She had no seizures for nearly a year "
        "following initiation of Valproate, then developed myoclonic jerks "
        "leading to a tonic seizure three Saturdays ago"
    )
    _configure_dummy([
        {
            "seizure_frequency_number": "1 per year",
            "evidence_text": supported_evidence,
            "temporal_candidates": "ignored by DummyLM",
        },
        {
            "final_label": "1 per year",
            "final_evidence": supported_evidence,
            "decision": "confirm",
            "reason": "already correct",
            "temporal_candidates": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "confirm"
    assert pred.metadata["temporal_candidate_source"] == "deterministic"
    assert pred.values[0].raw_value == "1 per year"


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


def test_guard_evidence_text_strips_outer_double_quotes():
    note_text = (
        "Over the past six months; he continues to suffer one to two "
        "generalised tonic-clonic seizures per month, with a longest "
        "seizure-free interval of two weeks."
    )
    quoted = (
        '"he continues to suffer one to two generalised tonic-clonic '
        'seizures per month"'
    )

    repaired, flags = _guard_evidence_text(note_text, quoted)

    assert repaired == (
        "he continues to suffer one to two generalised tonic-clonic seizures per month"
    )
    assert repaired in note_text
    assert "evidence_repaired:outer_quotes_stripped" in flags


def test_guard_evidence_text_selects_locatable_ellipsis_segment():
    note_text = (
        "facial twitching. A second event occurred in Italy the following "
        "July 2019, once more during the night, lasting four minutes. "
        "Since returning to the UK, there have been no further events reported."
    )
    spliced = (
        '"A second event occurred in Italy the following July 2019... '
        'Since returning to the UK, there have been no further events reported."'
    )

    repaired, flags = _guard_evidence_text(note_text, spliced)

    assert repaired in note_text
    assert repaired.startswith("Since returning to the UK")
    assert "evidence_repaired:outer_quotes_stripped" in flags
    assert "evidence_repaired:ellipsis_segment_selected" in flags


def test_guard_evidence_text_prefers_longest_temporal_candidate_fallback():
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

    repaired, flags = _guard_evidence_text(
        note_text,
        bad_summary,
        fallback_evidence_texts=[candidate_span],
    )

    assert repaired == candidate_span
    assert "evidence_repaired:temporal_candidate_fallback" in flags


def test_guard_evidence_text_repairs_gpt_temporal_cap25_failure_snippets():
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
        repaired, _flags = _guard_evidence_text(record.note_text, quoted)
        assert repaired in record.note_text, record_id


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


def test_build_gan_frequency_s0_extractor_signature_ports_policy_versions():
    synthesis = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_SYNTHESIS_PORT_TEMPORAL_PROMPT_VERSION
    )
    guardrails = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_GUARDRAILS_PORT_TEMPORAL_PROMPT_VERSION
    )

    assert synthesis is not GanFrequencyS0Signature
    assert "Synthesis-backed Gan frequency policy" in (synthesis.__doc__ or "")
    assert "Arithmetic and temporal guardrails" in (guardrails.__doc__ or "")


def test_build_gan_frequency_s0_extractor_signature_adds_canonical_format_examples():
    from clinical_extraction.programs.gan_frequency_s0 import (
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_CANONICAL_EXAMPLES_PROMPT_VERSION,
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    )

    control = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION
    )
    canonical = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_CANONICAL_EXAMPLES_PROMPT_VERSION
    )

    control_doc = control.__doc__ or ""
    canonical_doc = canonical.__doc__ or ""
    assert "Temporal-candidate adjudication policy (v1.1)" in control_doc
    assert "Canonical-format worked examples (v3/v5 port" not in control_doc
    assert "11 to 28 events per quarter" in canonical_doc
    assert len(canonical_doc) > len(control_doc)


def test_build_gan_frequency_s0_extractor_signature_adds_slot_payload_policy():
    from clinical_extraction.programs.gan_frequency_s0 import (
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_SLOT_PAYLOAD_PROMPT_VERSION,
    )

    control = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION
    )
    slot_payload = build_gan_frequency_s0_extractor_signature(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_SLOT_PAYLOAD_PROMPT_VERSION
    )

    control_doc = control.__doc__ or ""
    slot_doc = slot_payload.__doc__ or ""
    assert "Structured slot-payload adjudication policy (v1.3)" in slot_doc
    assert "denominator_status" in slot_doc
    assert "Structured slot-payload adjudication policy (v1.3)" not in control_doc
    assert len(slot_doc) > len(control_doc)


def test_build_gan_s0_module_accepts_prompt_version_for_temporal_verify_repair():
    module = build_gan_s0_module(
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
        prompt_version=GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION,
    )

    assert isinstance(module, GanFrequencyS0TemporalCandidatesVerifyRepairModule)
    assert (
        module.prompt_version
        == GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION
    )


def test_apply_evidence_span_check_guard_preserves_note_supported_initial():
    verified = dspy.Prediction(
        final_label="2 per 3 month",
        final_evidence="invented quote",
        decision="repair",
        reason="bad quote",
    )
    guarded = _apply_evidence_span_check_guard(
        "She had two seizures in the last three months.",
        verified,
        initial_label="2 per 3 month",
        initial_evidence="two seizures in the last three months",
    )

    assert guarded.decision == "confirm"
    assert guarded.final_evidence == "two seizures in the last three months"


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


def test_gan_s0_temporal_event_table_verify_repair_rescues_confirmed_unknown_with_sole_candidate():
    record = next(r for r in load_gan_records() if r.record_id == "gan_14881")
    event_table_json = (
        '{"events":[{"raw_phrase":"His last episode was recorded on 26 February",'
        '"evidence_text":"His last episode was recorded on 26 February",'
        '"role":"seizure_event"}],'
        '"seizure_free_intervals":[{"raw_phrase":"he has remained well since",'
        '"evidence_text":"His last episode was recorded on 26 February and he has remained well since.",'
        '"qualifies_for_seizure_free_label":false}],'
        '"selected_window_note":null}'
    )
    _configure_dummy([
        {
            "seizure_frequency_number": "unknown",
            "evidence_text": "His last episode was recorded on 26 February",
        },
        {"event_table_json": event_table_json},
        {
            "final_label": "unknown",
            "final_evidence": "His last episode was recorded on 26 February and he has remained well since.",
            "decision": "confirm",
            "reason": "Verifier kept unknown due to short post-episode window.",
            "temporal_candidates": "ignored by DummyLM",
            "temporal_event_table": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0TemporalEventTableVerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "repair"
    assert "Event-table candidate rescue" in pred.metadata["verifier_reason"]
    assert pred.values[0].raw_value == "1 per month"


def test_gan_s0_temporal_event_table_verify_repair_passes_event_table_to_verifier():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    event_table_json = (
        '{"events":[{"raw_phrase":"tonic seizure three Saturdays ago",'
        '"event_count":"1","window_phrase":"after nearly a year seizure-free",'
        '"evidence_text":"tonic seizure three Saturdays ago","role":"seizure_event"}],'
        '"seizure_free_intervals":[{"raw_phrase":"no seizures for nearly a year",'
        '"duration_phrase":"nearly a year",'
        '"evidence_text":"no seizures for nearly a year",'
        '"qualifies_for_seizure_free_label":true}],'
        '"selected_window_note":"Use breakthrough event over long quiet period."}'
    )
    _configure_dummy([
        {
            "seizure_frequency_number": "unknown",
            "evidence_text": "no seizures for nearly a year",
        },
        {
            "event_table_json": event_table_json,
        },
        {
            "final_label": "1 per year",
            "final_evidence": (
                "no seizures for nearly a year before a single breakthrough tonic seizure"
            ),
            "decision": "repair",
            "reason": "Event table supports breakthrough-after-year window.",
            "temporal_candidates": "ignored by DummyLM",
            "temporal_event_table": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0TemporalEventTableVerifyRepairModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["verifier_decision"] == "repair"
    assert pred.metadata["temporal_candidate_labels"] == ["1 per year"]
    assert pred.metadata["temporal_event_table_records"]["events"][0]["event_count"] == "1"
    assert pred.values[0].raw_value == "1 per year"


def test_gan_s0_temporal_event_table_single_pass_adjudicates_from_event_table():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    event_table_json = (
        '{"events":[{"raw_phrase":"a tonic seizure three Saturdays ago",'
        '"event_count":"1","window_phrase":"nearly a year",'
        '"evidence_text":"a tonic seizure three Saturdays ago","role":"seizure_event"}],'
        '"seizure_free_intervals":[{"raw_phrase":"no seizures for nearly a year",'
        '"duration_phrase":"nearly a year",'
        '"evidence_text":"no seizures for nearly a year",'
        '"qualifies_for_seizure_free_label":true}],'
        '"selected_window_note":"Breakthrough event after long quiet period."}'
    )
    _configure_dummy([
        {"event_table_json": event_table_json},
        {
            "seizure_frequency_number": "1 per year",
            "evidence_text": (
                "She had no seizures for nearly a year following initiation of Valproate"
            ),
            "temporal_event_table": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0TemporalEventTableSinglePassModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert "verifier_decision" not in pred.metadata
    assert pred.metadata["temporal_candidate_source"] == "llm_event_table"
    assert pred.metadata["temporal_event_table_records"]["events"][0]["event_count"] == "1"
    assert pred.values[0].raw_value == "1 per year"


def test_gan_s0_multiple_answer_selector_prefers_supported_quantified_option():
    selected = select_gan_multiple_answer_option(
        [
            {
                "canonical_label": "unknown",
                "evidence_text": "clusters after poor sleep",
                "status": "unknown",
                "ambiguity_flags": ["trigger_conditioned", "denominator_missing"],
                "rationale": "Trigger-conditioned pattern lacks denominator.",
            },
            {
                "canonical_label": "2 per 3 month",
                "evidence_text": "two seizures in the last three months",
                "status": "current",
                "ambiguity_flags": [],
                "rationale": "Count and window are explicit.",
            },
        ]
    )

    assert selected is not None
    assert selected["canonical_label"] == "2 per 3 month"


def test_gan_s0_multiple_answer_det_selector_filters_and_selects_options():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    supported_evidence = (
        "In terms of seizure control, She had no seizures for nearly a year "
        "following initiation of Valproate, then developed myoclonic jerks "
        "leading to a tonic seizure three Saturdays ago"
    )
    _configure_dummy([
        {
            "answer_options_json": (
                '{"answer_options": ['
                '{"canonical_label": "unknown", '
                '"evidence_text": "NOT IN NOTE", "status": "unknown", '
                '"ambiguity_flags": ["denominator_missing"], '
                '"rationale": "unsupported option should be dropped"}, '
                '{"canonical_label": "1 per year", '
                f'"evidence_text": {supported_evidence!r}, '
                '"status": "current", "ambiguity_flags": [], '
                '"rationale": "breakthrough after nearly one year"}'
                "]}"
            ).replace("'", '"')
        }
    ])

    module = GanFrequencyS0MultipleAnswerDetSelectorModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["temporal_candidate_source"] == (
        "llm_multiple_answer_det_selector"
    )
    assert pred.metadata["verifier_decision"] == "deterministic_select"
    assert pred.metadata["selected_answer_option"]["canonical_label"] == "1 per year"
    assert len(pred.metadata["multiple_answer_options"]) == 1
    assert pred.values[0].raw_value == "1 per year"


def test_build_gan_s0_module_supports_temporal_event_table_variant():
    module = build_gan_s0_module(GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT)
    assert isinstance(module, GanFrequencyS0TemporalEventTableVerifyRepairModule)
    single_pass = build_gan_s0_module(GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT)
    assert isinstance(single_pass, GanFrequencyS0TemporalEventTableSinglePassModule)


def test_gan_s0_react_temporal_tools_module_records_tool_metadata():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")
    _configure_dummy([
        {
            "next_thought": "Inspect deterministic temporal candidates first.",
            "next_tool_name": "find_temporal_frequency_candidates",
            "next_tool_args": {"note_text": record.note_text},
        },
        {
            "next_thought": "Candidates are sufficient.",
            "next_tool_name": "finish",
            "next_tool_args": {},
        },
        {
            "reasoning": "Breakthrough after nearly a year supports 1 per year.",
            "seizure_frequency_number": "1 per year",
            "evidence_text": "no seizures for nearly a year",
        },
    ])

    module = GanFrequencyS0ReactTemporalToolsModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["react_tool_call_count"] == 1
    assert pred.metadata["react_trajectory"]["tool_name_0"] == (
        "find_temporal_frequency_candidates"
    )
    assert pred.values[0].raw_value == "1 per year"


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


def test_gan_s0_validation_ladder_det_guards_emits_ladder_metadata():
    record = load_gan_records()[0]
    _configure_dummy(
        [{"seizure_frequency_number": "unknown", "evidence_text": "no clear rate"}]
    )
    prediction_set = predict_gan_records(
        GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT,
    )
    pred = prediction_set.predictions[0]
    assert pred.metadata["validation_ladder_rung"] == "det_plausibility"
    assert pred.metadata["verifier_decision"] == "confirm"


def test_gan_s0_validation_ladder_det_evidence_abstains_on_unsupported_quote():
    record = load_gan_records()[0]
    _configure_dummy(
        [{"seizure_frequency_number": "2 per week", "evidence_text": "NOT IN NOTE"}]
    )
    prediction_set = predict_gan_records(
        GanFrequencyS0TemporalCandidatesAdjudicateDetEvidenceModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT,
    )
    pred = prediction_set.predictions[0]
    assert pred.metadata["validation_ladder_rung"] == "det_evidence_grounding"
    assert pred.metadata["verifier_decision"] == "abstain"
    assert pred.values[0].raw_value is None


def test_gan_s0_validation_ladder_confirm_only_runs_second_llm_pass():
    record = load_gan_records()[0]
    _configure_dummy(
        [
            {"seizure_frequency_number": "1 per month", "evidence_text": "monthly seizure"},
            {
                "final_label": "1 per month",
                "final_evidence": "monthly seizure",
                "decision": "confirm",
                "reason": "Confirmed unchanged.",
                "temporal_candidates": "ignored",
            },
        ]
    )
    prediction_set = predict_gan_records(
        GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule(),
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT,
    )
    pred = prediction_set.predictions[0]
    assert pred.metadata["validation_ladder_rung"] == "llm_confirm_only"
    assert pred.metadata["verifier_decision"] == "confirm"


def test_build_gan_frequency_s0_confirm_only_verifier_signature_restricts_decisions():
    signature_cls = build_gan_frequency_s0_verifier_signature(
        "gan_frequency_s0_temporal_candidates_confirm_only_v1_1",
        temporal=True,
    )
    doc = signature_cls.__doc__ or ""
    assert "confirm only" in doc.lower()
    assert "MUST be confirm" in doc


def test_gan_s0_confirm_only_module_wires_confirm_only_verifier_signature():
    module = GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule()

    doc = module.verifier.verify.signature.__doc__ or ""
    assert "confirm only" in doc.lower()
    assert "MUST be confirm" in doc


def test_apply_constrained_verifier_guard_preserves_allowed():
    from types import SimpleNamespace
    note_text = "Patient has 3 seizures per week."
    candidates = [
        SimpleNamespace(canonical_label="3 per week", evidence_text="3 seizures per week")
    ]

    # Test case 1: label is in candidates
    verified = dspy.Prediction(final_label="3 per week", decision="confirm", reason="ok")
    res = _apply_constrained_verifier_guard(
        note_text=note_text,
        verified=verified,
        candidates=candidates,
        initial_label="unknown",
        initial_evidence="no reference",
    )
    assert res.final_label == "3 per week"
    assert res.final_evidence == "3 seizures per week"
    assert res.decision == "confirm"

    # Test case 2: label is the initial label
    verified = dspy.Prediction(final_label="1 per month", decision="confirm", reason="ok")
    res = _apply_constrained_verifier_guard(
        note_text=note_text,
        verified=verified,
        candidates=candidates,
        initial_label="1 per month",
        initial_evidence="monthly events",
    )
    assert res.final_label == "1 per month"
    assert res.final_evidence == "monthly events"
    assert res.decision == "confirm"

    # Test case 3: label is "unknown"
    verified = dspy.Prediction(final_label="unknown", decision="confirm", reason="ok")
    res = _apply_constrained_verifier_guard(
        note_text=note_text,
        verified=verified,
        candidates=candidates,
        initial_label="3 per week",
        initial_evidence="3 seizures per week",
    )
    assert res.final_label == "unknown"
    assert res.final_evidence is None
    assert res.decision == "confirm"


def test_apply_constrained_verifier_guard_reverts_close_matches():
    from types import SimpleNamespace
    note_text = "Patient has 3 seizures per week."
    candidates = [
        SimpleNamespace(canonical_label="3 per week", evidence_text="3 seizures per week")
    ]

    # Test case 1: close match to candidate label
    verified = dspy.Prediction(final_label="3 per wk", decision="confirm", reason="ok")
    res = _apply_constrained_verifier_guard(
        note_text=note_text,
        verified=verified,
        candidates=candidates,
        initial_label="unknown",
        initial_evidence=None,
    )
    assert res.final_label == "3 per week"
    assert res.final_evidence == "3 seizures per week"
    assert res.decision == "repair"
    assert "reverted to closest match" in res.reason

    # Test case 2: close match to initial label
    verified = dspy.Prediction(final_label="1 per mon", decision="confirm", reason="ok")
    res = _apply_constrained_verifier_guard(
        note_text=note_text,
        verified=verified,
        candidates=candidates,
        initial_label="1 per month",
        initial_evidence="monthly events",
    )
    assert res.final_label == "1 per month"
    assert res.final_evidence == "monthly events"
    assert res.decision == "repair"


def test_apply_constrained_verifier_guard_fallbacks():
    from types import SimpleNamespace
    note_text = "Patient has 3 seizures per week."
    candidates = [
        SimpleNamespace(canonical_label="3 per week", evidence_text="3 seizures per week")
    ]

    # Test case 1: no close match, fallback to initial label
    verified = dspy.Prediction(final_label="rarely", decision="confirm", reason="ok")
    res = _apply_constrained_verifier_guard(
        note_text=note_text,
        verified=verified,
        candidates=candidates,
        initial_label="3 per week",
        initial_evidence="3 seizures per week",
    )
    assert res.final_label == "3 per week"
    assert res.final_evidence == "3 seizures per week"
    assert res.decision == "repair"
    assert "fallback to" in res.reason

    # Test case 2: no close match, no initial label, fallback to "unknown"
    verified = dspy.Prediction(final_label="rarely", decision="confirm", reason="ok")
    res = _apply_constrained_verifier_guard(
        note_text=note_text,
        verified=verified,
        candidates=candidates,
        initial_label=None,
        initial_evidence=None,
    )
    assert res.final_label == "unknown"
    assert res.final_evidence is None
    assert res.decision == "repair"
    assert "fallback to" in res.reason


def test_gan_s0_constrained_verifier_module_runs():
    record = next(r for r in load_gan_records() if r.record_id == "gan_13123")

    # Configure DummyLM to simulate adjudicator returning "1 per year" (which is the gold label)
    # and then verifier returning "1 per yr" (out of bounds close match)
    _configure_dummy([
        {
            "seizure_frequency_number": "1 per year",
            "evidence_text": "no seizures for nearly a year",
            "temporal_candidates": "ignored by DummyLM",
        },
        {
            "final_label": "1 per yr",
            "final_evidence": "no seizures for nearly a year",
            "decision": "repair",
            "reason": "slightly wrong surface",
            "temporal_candidates": "ignored by DummyLM",
        },
    ])

    module = GanFrequencyS0TemporalCandidatesAdjudicateConstrainedVerifierModule()
    prediction_set = predict_gan_records(
        module,
        [record],
        model_provider="mock",
        model_name="dummy-fixture",
        program_variant=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT,
    )

    pred = prediction_set.predictions[0]
    assert pred.metadata["validation_ladder_rung"] == "constrained_verifier"
    assert pred.metadata["verifier_decision"] == "repair"
    # It should have reverted "1 per yr" to "1 per year"
    assert pred.values[0].raw_value == "1 per year"


import json
from pathlib import Path

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.gan_g4_reason_code_adjudicator import (
    G4_ARM_ID,
    build_gan_g4_reason_code_adjudicator_report,
    render_gan_g4_markdown,
)
from clinical_extraction.schemas import DocumentPrediction, ExtractedValue, PredictionSet


def _write_run(
    run_dir: Path,
    *,
    experiment_id: str,
    program_variant: str,
    predictions: list[DocumentPrediction],
) -> None:
    run_dir.mkdir()
    prediction_set = PredictionSet(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        predictions=predictions,
    )
    (run_dir / "predictions.json").write_text(
        prediction_set.model_dump_json(indent=2),
        encoding="utf-8",
    )
    (run_dir / "metadata.json").write_text(
        json.dumps(
            {
                "run_id": run_dir.name,
                "program_variant": program_variant,
                "model_provider": "unit",
                "model_name": "unit-model",
                "metadata": {"prompt_version": "unit_prompt"},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "experiment_id": experiment_id,
                "split_name": "gan_2026_fixed_v1:validation",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "metrics.json").write_text(
        json.dumps({"runtime": {"records": len(predictions)}}),
        encoding="utf-8",
    )


def _prediction(
    record_id: str,
    label: str,
    *,
    metadata: dict | None = None,
) -> DocumentPrediction:
    return DocumentPrediction(
        document_id=record_id,
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[
            ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value=label,
                normalized_value=label,
            )
        ],
        metadata=metadata or {},
    )


def _note_snippet(record_id: str) -> str:
    records = {record.record_id: record for record in load_gan_records()}
    return records[record_id].note_text[:80]


def test_g4_reason_code_report_records_traceability_and_failure_types(tmp_path):
    correct_id = "gan_13123"
    failure_id = "gan_14250"
    free_run = tmp_path / "free"
    candidate_run = tmp_path / "candidate"
    reason_run = tmp_path / "reason"
    g4_run = tmp_path / "g4"

    _write_run(
        free_run,
        experiment_id="free",
        program_variant="gan_frequency_s0_direct_single_pass",
        predictions=[
            _prediction(correct_id, "unknown"),
            _prediction(failure_id, "unknown"),
        ],
    )
    _write_run(
        candidate_run,
        experiment_id="candidate",
        program_variant="gan_frequency_s0_temporal_candidates_single_pass",
        predictions=[
            _prediction(correct_id, "1 per year"),
            _prediction(failure_id, "2 per month"),
        ],
    )
    _write_run(
        reason_run,
        experiment_id="reason",
        program_variant="gan_frequency_s0_seeded_multiple_answer_det_selector",
        predictions=[
            _prediction(correct_id, "1 per year"),
            _prediction(failure_id, "2 per month"),
        ],
    )
    _write_run(
        g4_run,
        experiment_id="g4",
        program_variant="gan_frequency_s0_explicit_reason_code_adjudicator",
        predictions=[
            _prediction(
                correct_id,
                "1 per year",
                metadata={
                    "target_selection_reason_code": "select_current_quantified_rate",
                    "target_selection_error_class": "none",
                    "selected_candidate_reference": {
                        "candidate_index": 1,
                        "constructed_label": "1 per year",
                        "evidence_text": _note_snippet(correct_id),
                    },
                    "label_construction_inputs": {
                        "event_count": "1",
                        "window_count": "1",
                        "window_unit": "year",
                    },
                    "temporal_candidate_labels": [
                        "1 per year",
                        "unknown",
                    ],
                    "reason_code_adjudication": {
                        "reason_code": "select_current_quantified_rate",
                        "error_class": "none",
                        "final_benchmark_label": "1 per year",
                    },
                },
            ),
            _prediction(
                failure_id,
                "seizure free for multiple month",
                metadata={
                    "target_selection_reason_code": "select_seizure_free_duration",
                    "target_selection_error_class": "none",
                    "selected_candidate_reference": {
                        "candidate_index": 2,
                        "constructed_label": "seizure free for multiple month",
                        "evidence_text": _note_snippet(failure_id),
                    },
                    "label_construction_inputs": {
                        "event_count": "0",
                        "window_unit": "multiple month",
                    },
                    "temporal_candidate_labels": [
                        "2 per month",
                        "seizure free for multiple month",
                    ],
                    "reason_code_adjudication": {
                        "reason_code": "select_seizure_free_duration",
                        "error_class": "none",
                        "final_benchmark_label": "seizure free for multiple month",
                    },
                },
            ),
        ],
    )

    report = build_gan_g4_reason_code_adjudicator_report(
        arm_run_dirs={
            "free_adjudication": free_run,
            "candidate_constrained": candidate_run,
            "reason_code_selector": reason_run,
            G4_ARM_ID: g4_run,
        }
    )

    diagnostics = report["g4_diagnostics"]
    assert diagnostics["reason_code_counts"] == {
        "select_current_quantified_rate": 1,
        "select_seizure_free_duration": 1,
    }
    assert diagnostics["selected_candidate_references_present"] == {
        "count": 2,
        "denominator": 2,
    }
    assert diagnostics["label_construction_inputs_present"] == {
        "count": 2,
        "denominator": 2,
    }
    assert diagnostics["unsupported_candidate_cases"] == []
    assert diagnostics["primary_failure_type_counts"]["target_selection"] == 1
    assert diagnostics["failure_signal_counts"]["policy"] == 1
    assert diagnostics["pairwise_deltas"]["candidate_constrained"][
        "g4_wrong_baseline_correct"
    ] == [failure_id]
    assert report["decision"]["promotion_recommendation"] == "do_not_promote_as_tested"
    assert "G4 Failure Records" in render_gan_g4_markdown(report)

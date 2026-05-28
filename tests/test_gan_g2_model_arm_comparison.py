import json
from pathlib import Path

import pytest

from clinical_extraction.evaluation.gan_g2_model_arm_comparison import (
    build_gan_g2_model_arm_comparison_report,
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


def _prediction(record_id: str, label: str, *, metadata: dict | None = None):
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


def test_g2_model_arm_report_scores_each_arm_under_both_scorers(tmp_path):
    free_run = tmp_path / "free"
    candidate_run = tmp_path / "candidate"
    reason_run = tmp_path / "reason"

    _write_run(
        free_run,
        experiment_id="free",
        program_variant="gan_frequency_s0_direct_single_pass",
        predictions=[
            _prediction("gan_13123", "unknown"),
            _prediction("gan_13574", "seizure free for multiple year"),
        ],
    )
    _write_run(
        candidate_run,
        experiment_id="candidate",
        program_variant="gan_frequency_s0_temporal_candidates_single_pass",
        predictions=[
            _prediction(
                "gan_13123",
                "1 per year",
                metadata={"temporal_candidate_labels": ["1 per year"]},
            ),
            _prediction(
                "gan_13574",
                "seizure free for multiple year",
                metadata={
                    "temporal_candidate_labels": ["seizure free for multiple year"]
                },
            ),
        ],
    )
    _write_run(
        reason_run,
        experiment_id="reason",
        program_variant="gan_frequency_s0_seeded_multiple_answer_det_selector",
        predictions=[
            _prediction(
                "gan_13123",
                "1 per year",
                metadata={
                    "multiple_answer_options": [{"canonical_label": "1 per year"}],
                    "selected_answer_option": {
                        "source": "deterministic_temporal_candidate",
                        "status": "current",
                    },
                },
            ),
            _prediction(
                "gan_13574",
                "seizure free for multiple year",
                metadata={
                    "multiple_answer_options": [
                        {"canonical_label": "seizure free for multiple year"}
                    ],
                    "selected_answer_option": {
                        "source": "llm_answer_option",
                        "status": "present",
                    },
                },
            ),
        ],
    )

    report = build_gan_g2_model_arm_comparison_report(
        arm_run_dirs={
            "free_adjudication": free_run,
            "candidate_constrained": candidate_run,
            "reason_code_selector": reason_run,
        }
    )

    arms = report["summary"]["arms"]
    assert arms["free_adjudication"]["canonical"]["monthly_frequency_accuracy"] == 0.5
    assert arms["candidate_constrained"]["canonical"]["monthly_frequency_accuracy"] == 1.0
    assert arms["reason_code_selector"]["paper_reproduction"][
        "monthly_frequency_accuracy"
    ] == 1.0
    assert arms["reason_code_selector"]["option_diagnostics"][
        "selected_answer_source_counts"
    ] == {
        "deterministic_temporal_candidate": 1,
        "llm_answer_option": 1,
    }
    assert report["summary"]["best_by_metric"]["canonical"][
        "monthly_frequency_accuracy"
    ]["arm_ids"] == [
        "candidate_constrained",
        "reason_code_selector",
    ]
    assert [row["record_id"] for row in report["summary"]["differential_records"]] == [
        "gan_13123"
    ]


def test_g2_model_arm_report_rejects_mismatched_arm_record_sets(tmp_path):
    free_run = tmp_path / "free"
    candidate_run = tmp_path / "candidate"

    _write_run(
        free_run,
        experiment_id="free",
        program_variant="gan_frequency_s0_direct_single_pass",
        predictions=[_prediction("gan_13123", "1 per year")],
    )
    _write_run(
        candidate_run,
        experiment_id="candidate",
        program_variant="gan_frequency_s0_temporal_candidates_single_pass",
        predictions=[_prediction("gan_13574", "seizure free for multiple year")],
    )

    with pytest.raises(ValueError, match="share the same record IDs"):
        build_gan_g2_model_arm_comparison_report(
            arm_run_dirs={
                "free_adjudication": free_run,
                "candidate_constrained": candidate_run,
            }
        )

import json
from pathlib import Path

from clinical_extraction.evaluation.gan_g22_closed_option_target_selector import (
    DEFAULT_BASELINE_RUNS,
    build_gan_g22_closed_option_target_selector_report,
    render_gan_g22_markdown,
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


def test_g22_report_preserves_row_level_before_after_ledger(tmp_path):
    baseline_run = tmp_path / "builder"
    g22_run = tmp_path / "g22"
    record_ids = ["gan_14485", "gan_6532", "gan_15997"]

    _write_run(
        baseline_run,
        experiment_id="baseline",
        program_variant="gan_frequency_s0_temporal_candidates_single_pass",
        predictions=[
            _prediction("gan_14485", "seizure free for 1 month"),
            _prediction("gan_6532", "5 per day"),
            _prediction("gan_15997", "5 per day"),
        ],
    )
    _write_run(
        g22_run,
        experiment_id="g22",
        program_variant="gan_frequency_s0_closed_option_target_selector",
        predictions=[
            _prediction(
                "gan_14485",
                "2 per 3 month",
                metadata={
                    "closed_answer_options": [
                        {
                            "option_id": "raw_1",
                            "canonical_label": "2 per 3 month",
                            "source": "deterministic_temporal_candidate",
                            "family": "quantified_rate",
                        }
                    ],
                    "selected_closed_answer_option": {
                        "option_id": "raw_1",
                        "canonical_label": "2 per 3 month",
                        "source": "deterministic_temporal_candidate",
                        "family": "quantified_rate",
                    },
                    "constructed_answer_options": [],
                    "closed_option_ranking": ["raw_1"],
                    "reason_code_adjudication": {"selected_option_id": "raw_1"},
                },
            ),
            _prediction(
                "gan_6532",
                "unknown, multiple per cluster",
                metadata={
                    "closed_answer_options": [
                        {
                            "option_id": "raw_1",
                            "canonical_label": "5 per day",
                            "source": "deterministic_temporal_candidate",
                            "family": "quantified_rate",
                        },
                        {
                            "option_id": "raw_2",
                            "canonical_label": "unknown, multiple per cluster",
                            "source": "deterministic_temporal_candidate",
                            "family": "unknown_cluster",
                        },
                    ],
                    "selected_closed_answer_option": {
                        "option_id": "raw_2",
                        "canonical_label": "unknown, multiple per cluster",
                        "source": "deterministic_temporal_candidate",
                        "family": "unknown_cluster",
                    },
                    "constructed_answer_options": [],
                    "closed_option_ranking": ["raw_2", "raw_1"],
                    "reason_code_adjudication": {"selected_option_id": "raw_2"},
                },
            ),
            _prediction(
                "gan_15997",
                "10 per 3 month",
                metadata={
                    "closed_answer_options": [
                        {
                            "option_id": "raw_1",
                            "canonical_label": "5 per day",
                            "source": "deterministic_temporal_candidate",
                            "family": "quantified_rate",
                        },
                        {
                            "option_id": "constructed_1",
                            "canonical_label": "10 per 3 month",
                            "source": "deterministic_aggregation_constructor",
                            "family": "quantified_rate",
                            "is_constructed": True,
                        },
                    ],
                    "selected_closed_answer_option": {
                        "option_id": "constructed_1",
                        "canonical_label": "10 per 3 month",
                        "source": "deterministic_aggregation_constructor",
                        "family": "quantified_rate",
                        "is_constructed": True,
                    },
                    "constructed_answer_options": [
                        {
                            "option_id": "constructed_1",
                            "canonical_label": "10 per 3 month",
                            "source": "deterministic_aggregation_constructor",
                            "family": "quantified_rate",
                            "is_constructed": True,
                        }
                    ],
                    "closed_option_ranking": ["constructed_1", "raw_1"],
                    "reason_code_adjudication": {
                        "selected_option_id": "constructed_1"
                    },
                },
            ),
        ],
    )

    report = build_gan_g22_closed_option_target_selector_report(
        g22_run_dir=g22_run,
        arm_run_dirs={"builder_gap_gpt": baseline_run},
        record_ids=record_ids,
    )

    assert report["decision_scope"] == "arm"
    assert report["g22_diagnostics"]["selected_closed_answer_option_present"] == {
        "count": 3,
        "denominator": 3,
    }
    assert report["g22_diagnostics"]["selected_option_source_counts"][
        "deterministic_aggregation_constructor"
    ] == 1
    assert report["g22_diagnostics"]["final_label_copied_from_selected_option"] == {
        "count": 3,
        "denominator": 3,
    }

    ledger = {row["record_id"]: row for row in report["before_after_ledger"]}
    assert ledger["gan_14485"]["g19_failure_classes"] == [
        "target_selection__seizure_free_over_quantified"
    ]
    assert ledger["gan_14485"]["before"]["builder_gap_gpt"][
        "paper_monthly_match"
    ] is False
    assert ledger["gan_14485"]["after"]["g22"]["paper_monthly_match"] is True
    assert ledger["gan_6532"]["g17_policy_bucket"] == (
        "unknown_cluster_misrouted_as_concrete"
    )
    assert ledger["gan_15997"]["g21_standard50"][
        "constructed_exact_covered"
    ] is True
    assert ledger["gan_15997"]["g22_selection"]["selected_option_source"] == (
        "deterministic_aggregation_constructor"
    )

    markdown = render_gan_g22_markdown(report)
    assert "Before/After Ledger" in markdown
    assert "`gan_6532`" in markdown


def test_g22_default_g15_baseline_path_matches_stored_run():
    assert (
        DEFAULT_BASELINE_RUNS["g15_support_aware_selector"] / "predictions.json"
    ).exists()

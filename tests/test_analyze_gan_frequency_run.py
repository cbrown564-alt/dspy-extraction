import json
import importlib.util
from pathlib import Path

from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExtractedValue,
    GanRecord,
    PredictionSet,
)
from clinical_extraction.evaluation.gan_failure_taxonomy import (
    classify_gan_frequency_failure,
    failure_action_tier,
)

_ANALYZE_SCRIPT = Path("scripts/analyze_gan_frequency_run.py")
_analyze_spec = importlib.util.spec_from_file_location(
    "analyze_gan_frequency_run", _ANALYZE_SCRIPT
)
assert _analyze_spec and _analyze_spec.loader
_analyze = importlib.util.module_from_spec(_analyze_spec)
_analyze_spec.loader.exec_module(_analyze)


def test_analysis_record_ids_uses_config_record_ids_filter(tmp_path: Path):
    from clinical_extraction.evaluation.gan_run_analysis import analysis_record_ids

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "config.json").write_text(
        json.dumps({"record_ids": ["gan_10509", "gan_10751"]}),
        encoding="utf-8",
    )
    record_ids, scope = analysis_record_ids(
        run_dir=run_dir,
        split_file=Path("data/splits/gan_2026_splits.json"),
        split_name="gan_2026_fixed_v1:validation",
        predictions_by_id={"gan_10509": object()},
    )
    assert scope == "record_ids_filter"
    assert record_ids == ["gan_10509", "gan_10751"]


def test_analysis_record_ids_cli_override_takes_precedence(tmp_path: Path):
    from clinical_extraction.evaluation.gan_run_analysis import analysis_record_ids

    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "config.json").write_text(
        json.dumps({"record_ids": ["gan_10509", "gan_10751"]}),
        encoding="utf-8",
    )
    record_ids, scope = analysis_record_ids(
        run_dir=run_dir,
        split_file=Path("data/splits/gan_2026_splits.json"),
        split_name="gan_2026_fixed_v1:validation",
        predictions_by_id={"gan_13123": object(), "gan_15306": object()},
        record_ids_override=["gan_13123", "gan_15306"],
    )
    assert scope == "record_ids_filter"
    assert record_ids == ["gan_13123", "gan_15306"]


def test_load_record_ids_filter_reads_regression_slice_fixture():
    from clinical_extraction.evaluation.gan_run_analysis import load_record_ids_filter
    from clinical_extraction.datasets.gan_qwen_regression_slice import (
        gan_qwen_error_regression_record_ids,
    )

    path = Path("data/fixtures/gan_s0_qwen_error_regression_slice.json")
    assert load_record_ids_filter(path) == gan_qwen_error_regression_record_ids(path)
    assert len(load_record_ids_filter(path)) == 14


def _scored_row(**overrides):
    base = {
        "status": "scored",
        "gold_label": "unknown",
        "predicted_label": "no seizure frequency reference",
        "normalized_gold_label": "unknown",
        "normalized_predicted_label": "no seizure frequency reference",
        "gold_pragmatic_category": "unknown",
        "predicted_pragmatic_category": "no_seizure_information",
        "gold_purist_category": "unknown",
        "predicted_purist_category": "no_seizure_information",
        "normalized_exact_match": False,
        "monthly_match": False,
        "purist_match": False,
        "pragmatic_match": False,
        "failure_class": "other_semantic_mismatch",
    }
    base.update(overrides)
    return base


def test_unknown_cluster_to_unknown_with_monthly_match_is_diagnostic_only():
    row = _scored_row(
        gold_label="unknown, 2 to 3 per cluster",
        predicted_label="unknown",
        normalized_gold_label="unknown, 2 to 3 per cluster",
        normalized_predicted_label="unknown",
        monthly_match=True,
        purist_match=True,
        pragmatic_match=True,
    )
    failure_class = classify_gan_frequency_failure(row)
    assert failure_class == "unknown_cluster_label_shape_mismatch"
    assert failure_action_tier(failure_class) == "diagnostic_only"


def test_seizure_free_to_no_reference_with_monthly_match_is_diagnostic_only():
    row = _scored_row(
        gold_label="seizure free for multiple year",
        predicted_label="no seizure frequency reference",
        normalized_gold_label="seizure free for multiple year",
        normalized_predicted_label="no seizure frequency reference",
        gold_pragmatic_category="infrequent",
        predicted_pragmatic_category="no_seizure_information",
        gold_purist_category="lt_1_per_6_months",
        predicted_purist_category="no_seizure_information",
        monthly_match=True,
        purist_match=True,
        pragmatic_match=True,
    )
    failure_class = classify_gan_frequency_failure(row)
    assert failure_class == "seizure_free_to_no_reference_monthly_match"
    assert failure_action_tier(failure_class) == "diagnostic_only"


def test_seizure_free_to_no_reference_without_monthly_match_is_benchmark_severe():
    row = _scored_row(
        gold_label="unknown",
        predicted_label="seizure free for 4 month",
        normalized_gold_label="unknown",
        normalized_predicted_label="seizure free for 4 month",
        monthly_match=False,
    )
    failure_class = classify_gan_frequency_failure(row)
    assert failure_class == "unknown_vs_seizure_free"
    assert failure_action_tier(failure_class) == "benchmark_severe"


def test_unknown_vs_no_reference_remains_benchmark_severe():
    row = _scored_row()
    failure_class = classify_gan_frequency_failure(row)
    assert failure_class == "unknown_vs_no_reference"
    assert failure_action_tier(failure_class) == "benchmark_severe"


def test_analyze_run_exposes_paper_reproduction_scorer_mode(tmp_path: Path):
    record_id = "gan_14036"
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "config.json").write_text(
        json.dumps({"experiment_id": "paper_scorer_probe"}),
        encoding="utf-8",
    )
    (run_dir / "predictions.json").write_text(
        _gan_prediction_set(
            _gan_prediction(
                record_id=record_id,
                raw_label="no seizure frequency reference",
                normalized_label="no seizure frequency reference",
                evidence_text="No seizure frequency is described.",
                start=0,
                end=35,
            )
        ).model_dump_json(),
        encoding="utf-8",
    )

    canonical = _analyze.analyze_run(
        run_dir=run_dir,
        split_file=Path("data/splits/gan_2026_splits.json"),
        split_name="gan_2026_fixed_v1:validation",
        record_ids_override=[record_id],
    )
    paper = _analyze.analyze_run(
        run_dir=run_dir,
        split_file=Path("data/splits/gan_2026_splits.json"),
        split_name="gan_2026_fixed_v1:validation",
        record_ids_override=[record_id],
        scorer_mode="gan2026_paper_reproduction",
    )

    assert canonical["summary"]["scorer_mode"] == "gan_frequency_deterministic_v1"
    assert not canonical["rows"][0]["monthly_match"]
    assert paper["summary"]["scorer_mode"] == "gan2026_paper_reproduction"
    assert paper["rows"][0]["scorer_mode"] == "gan2026_paper_reproduction"
    assert paper["rows"][0]["monthly_match"]
    assert paper["rows"][0]["gold_pragmatic_category"] == "seizure_freq_unknown"
    assert "gan2026_paper_reproduction" in _analyze._render_markdown(
        paper,
        "paper_scorer_probe",
    )


def test_build_gan_stratified_reporting_includes_operational_and_valid_denominators():
    from clinical_extraction.evaluation.gan_run_analysis import (
        build_gan_stratified_reporting,
    )

    rows = [
        {
            "status": "scored",
            "hard_case": False,
            "row_ok": True,
            "gold_pragmatic_category": "infrequent",
            "normalized_exact_match": True,
            "monthly_match": True,
            "purist_match": True,
            "pragmatic_match": True,
            "failure_action_tier": "diagnostic_only",
        },
        {
            "status": "invalid",
            "hard_case": True,
            "row_ok": False,
            "gold_pragmatic_category": "frequent",
            "failure_class": "invalid_predicted_label",
        },
        {
            "status": "scored",
            "hard_case": True,
            "row_ok": True,
            "gold_pragmatic_category": "frequent",
            "normalized_exact_match": False,
            "monthly_match": False,
            "purist_match": False,
            "pragmatic_match": False,
            "failure_action_tier": "benchmark_severe",
        },
    ]
    report = build_gan_stratified_reporting(rows)

    overall = report["overall"]
    assert overall["all_records"] == 3
    assert overall["valid_scored"] == 2
    assert overall["invalid_or_missing"] == 1
    assert overall["operational_failures"] == 2
    assert overall["operational_failure_rate"] == 2 / 3
    assert report["hard_case"]["true"]["all_records"] == 2
    assert report["row_ok"]["false"]["all_records"] == 1
    assert "infrequent" in report["gold_pragmatic_category"]


def test_build_temporal_candidate_diagnostics_reports_gold_coverage():
    from clinical_extraction.datasets.gan import load_gan_records
    from clinical_extraction.evaluation.gan_run_analysis import (
        build_temporal_candidate_diagnostics,
    )

    gold_by_id = {record.record_id: record for record in load_gan_records()}
    diagnostics = build_temporal_candidate_diagnostics(
        record_ids=["gan_13123", "gan_14485", "gan_14881", "gan_15306"],
        gold_by_id=gold_by_id,
    )

    assert diagnostics["gold_covered_count"] == 4
    assert diagnostics["gold_covered_rate"] == 1.0
    assert all(row["gold_in_candidates"] for row in diagnostics["records"])


def test_export_gan_record_report_csv_writes_full_text_as_final_column(tmp_path: Path):
    from clinical_extraction.evaluation.gan_run_analysis import (
        GAN_RECORD_REPORT_FIELDNAMES,
        export_gan_record_report_csv,
    )

    gold = _gan_record(
        record_id="gan_test",
        note_text="Clinic letter says seizures occurring every 2 days.",
        gold_label="1 per 2 day",
        gold_evidence="seizures occurring every 2 days",
    )
    prediction_set = _gan_prediction_set(
        _gan_prediction(
            record_id="gan_test",
            raw_label="1 per 2 day",
            normalized_label="1 per 2 day",
            evidence_text="seizures occurring every 2 days",
            start=24,
            end=55,
        )
    )
    output = tmp_path / "report.csv"

    export_gan_record_report_csv(
        prediction_set=prediction_set,
        gold_by_id={"gan_test": gold},
        output_path=output,
    )

    rows = output.read_text(encoding="utf-8-sig").splitlines()
    assert rows[0].split(",")[-1] == "full_text"
    assert GAN_RECORD_REPORT_FIELDNAMES[-1] == "full_text"

    import csv

    parsed = list(csv.DictReader(output.open(encoding="utf-8-sig", newline="")))
    assert parsed[0]["record_id"] == "gan_test"
    assert parsed[0]["normalized_label_exact_match"] == "Y"
    assert parsed[0]["monthly_frequency_match"] == "Y"
    assert parsed[0]["full_text"] == gold.note_text


def test_build_gan_record_report_rows_marks_invalid_label():
    from clinical_extraction.evaluation.gan_run_analysis import (
        build_gan_record_report_rows,
    )

    gold = _gan_record(
        record_id="gan_invalid",
        note_text="Clinic letter says four seizures in six weeks.",
        gold_label="4 per 6 week",
        gold_evidence="four seizures in six weeks",
    )
    prediction_set = _gan_prediction_set(
        _gan_prediction(
            record_id="gan_invalid",
            raw_label="4 per 6 week, multiple per cluster",
            normalized_label="4 per 6 week, multiple per cluster",
            evidence_text="four seizures in six weeks",
            start=19,
            end=45,
        )
    )

    rows = build_gan_record_report_rows(
        prediction_set=prediction_set,
        gold_by_id={"gan_invalid": gold},
    )

    assert rows[0]["status"] == "invalid"
    assert rows[0]["failure_class"] == "invalid_predicted_label"
    assert "Unsupported Gan frequency label" in rows[0]["invalid_reason"]
    assert rows[0]["full_text"] == gold.note_text


def _gan_record(
    *,
    record_id: str,
    note_text: str,
    gold_label: str,
    gold_evidence: str,
) -> GanRecord:
    return GanRecord(
        record_id=record_id,
        source_row_index=1,
        note_text=note_text,
        gold_label=gold_label,
        gold_evidence=gold_evidence,
        reference_label=gold_label,
        reference_evidence=gold_evidence,
        row_ok=True,
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        flags=[],
        raw={},
    )


def _gan_prediction_set(*predictions: DocumentPrediction) -> PredictionSet:
    return PredictionSet(
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        predictions=list(predictions),
    )


def _gan_prediction(
    *,
    record_id: str,
    raw_label: str,
    normalized_label: str,
    evidence_text: str,
    start: int,
    end: int,
) -> DocumentPrediction:
    return DocumentPrediction(
        document_id=record_id,
        dataset="gan_2026",
        schema_level="gan_frequency_s0",
        values=[
            ExtractedValue(
                field_name="seizure_frequency_number",
                raw_value=raw_label,
                normalized_value=normalized_label,
                evidence=[
                    EvidenceSpan(
                        document_id=record_id,
                        start=start,
                        end=end,
                        text=evidence_text,
                    )
                ],
            )
        ],
    )

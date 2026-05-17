import json
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from clinical_extraction.runs import RunMetadata, create_run_artifact_layout


def test_run_metadata_contract_requires_experiment_context():
    metadata = RunMetadata(
        run_id="20260517_gan_dev_deterministic",
        created_at=datetime(2026, 5, 17, tzinfo=timezone.utc),
        dataset="gan_2026",
        split_name="gan_2026_fixed_v1:validation",
        model_provider="deterministic",
        model_name="gold_fixture",
        schema_level="gan_frequency_s0",
        program_variant="stored_predictions",
        scorer_mode="gan_frequency_deterministic_v1",
        metric_caveats=["raw exact is diagnostic only"],
    )

    serialized = metadata.model_dump(mode="json")

    assert serialized["dataset"] == "gan_2026"
    assert serialized["split_name"] == "gan_2026_fixed_v1:validation"
    assert serialized["model_provider"] == "deterministic"
    assert serialized["model_name"] == "gold_fixture"
    assert serialized["schema_level"] == "gan_frequency_s0"
    assert serialized["program_variant"] == "stored_predictions"
    assert serialized["scorer_mode"] == "gan_frequency_deterministic_v1"
    assert serialized["artifact_paths"] == {
        "metadata": "metadata.json",
        "config": "config.json",
        "prompts": "prompts.json",
        "predictions": "predictions.json",
        "metrics": "metrics.json",
        "errors": "errors.json",
        "artifacts": "artifacts",
    }


def test_run_metadata_rejects_empty_required_fields():
    with pytest.raises(ValidationError, match="model_name"):
        RunMetadata(
            run_id="run_1",
            dataset="gan_2026",
            split_name="validation",
            model_provider="deterministic",
            model_name=" ",
            schema_level="S0",
            program_variant="stored_predictions",
            scorer_mode="gan_frequency_deterministic_v1",
        )


def test_create_run_artifact_layout_writes_metadata_and_artifact_directory(tmp_path):
    metadata = RunMetadata(
        run_id="run_1",
        created_at=datetime(2026, 5, 17, tzinfo=timezone.utc),
        dataset="gan_2026",
        split_name="validation",
        model_provider="deterministic",
        model_name="fixture",
        schema_level="S0",
        program_variant="stored_predictions",
        scorer_mode="gan_frequency_deterministic_v1",
    )

    paths = create_run_artifact_layout(metadata, root=tmp_path)

    assert paths["run"] == tmp_path / "run_1"
    assert paths["artifacts"].is_dir()
    assert paths["metadata"].is_file()
    written = json.loads(paths["metadata"].read_text(encoding="utf-8"))
    assert written["run_id"] == "run_1"
    assert written["artifact_paths"]["predictions"] == "predictions.json"

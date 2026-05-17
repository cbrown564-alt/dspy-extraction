from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import Field, model_validator

from clinical_extraction.paths import RUNS_ROOT
from clinical_extraction.schemas import FrozenModel


class RunArtifactPaths(FrozenModel):
    metadata: str = "metadata.json"
    config: str = "config.json"
    prompts: str = "prompts.json"
    predictions: str = "predictions.json"
    metrics: str = "metrics.json"
    errors: str = "errors.json"
    artifacts: str = "artifacts"


class RunMetadata(FrozenModel):
    run_id: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
    )
    dataset: str
    split_name: str
    model_provider: str
    model_name: str
    schema_level: str
    program_variant: str
    scorer_mode: str
    artifact_paths: RunArtifactPaths = Field(default_factory=RunArtifactPaths)
    metric_caveats: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_required_text_fields(self) -> RunMetadata:
        for field in [
            "run_id",
            "dataset",
            "split_name",
            "model_provider",
            "model_name",
            "schema_level",
            "program_variant",
            "scorer_mode",
        ]:
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must be a non-empty string.")
        return self


def run_directory(run_id: str, *, root: Path = RUNS_ROOT) -> Path:
    return root / run_id


def create_run_artifact_layout(
    metadata: RunMetadata,
    *,
    root: Path = RUNS_ROOT,
) -> dict[str, Path]:
    directory = run_directory(metadata.run_id, root=root)
    artifact_dir = directory / metadata.artifact_paths.artifacts
    artifact_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "run": directory,
        "metadata": directory / metadata.artifact_paths.metadata,
        "config": directory / metadata.artifact_paths.config,
        "prompts": directory / metadata.artifact_paths.prompts,
        "predictions": directory / metadata.artifact_paths.predictions,
        "metrics": directory / metadata.artifact_paths.metrics,
        "errors": directory / metadata.artifact_paths.errors,
        "artifacts": artifact_dir,
    }
    paths["metadata"].write_text(
        json.dumps(metadata.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return paths

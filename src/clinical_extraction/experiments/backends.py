"""Dataset-specific experiment backends for the generic runner."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Protocol, runtime_checkable

import dspy

from clinical_extraction.experiments.config import ExperimentConfig, OptimizerConfig
from clinical_extraction.experiments.exect_backend import ExectExperimentBackend
from clinical_extraction.experiments.gan_backend import GanExperimentBackend
from clinical_extraction.runs import RunMetadata


@runtime_checkable
class ExperimentBackend(Protocol):
    dataset: str

    def load_records_by_id(self) -> dict[str, Any]: ...

    def build_module(
        self,
        config: ExperimentConfig,
        *,
        prompt_version: str,
    ) -> dspy.Module: ...

    def run_metadata(
        self,
        *,
        run_id: str,
        split_name: str,
        model_provider: str,
        model_name: str,
        prompt_version: str,
        program_variant: str,
        extra: dict[str, Any],
    ) -> RunMetadata: ...

    def predict_records(
        self,
        *,
        module: dspy.Module,
        records: list[Any],
        model_provider: str,
        model_name: str,
        prompt_version: str,
        program_variant: str,
        repair_policy: str,
        progress_callback: Callable[[int, int, str], None] | None,
        schema_level: str | None = None,
        scorer_mode: str | None = None,
    ) -> Any: ...

    def evaluate_predictions(
        self,
        prediction_set: Any,
        *,
        scorer_mode: str | None = None,
    ) -> dict[str, Any]: ...

    def prompts_data(self, config: ExperimentConfig) -> dict[str, Any]: ...

    def compile_module(
        self,
        *,
        config: ExperimentConfig,
        module: dspy.Module,
        train_records: list[Any],
        artifact_paths: dict[str, Path],
        reflection_lm: dspy.LM | None,
    ) -> dspy.Module: ...

    def optimizer_unsupported_message(self, optimizer: OptimizerConfig) -> str | None: ...


BACKENDS: dict[str, ExperimentBackend] = {
    "gan_2026": GanExperimentBackend(),
    "exect_v2": ExectExperimentBackend(),
}


def get_backend(dataset: str) -> ExperimentBackend:
    try:
        return BACKENDS[dataset]
    except KeyError:
        raise SystemExit(f"Unsupported dataset: {dataset!r}")

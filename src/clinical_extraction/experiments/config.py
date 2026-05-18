from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_VARIANT,
)
from clinical_extraction.schemas import FrozenModel


StructuredOutputStrategy = Literal[
    "provider_json_schema_with_pydantic_validation",
    "strict_json_prompt_with_pydantic_validation",
]


class OptimizerConfig(FrozenModel):
    """BootstrapFewShot hyperparameters for DSPy module compilation."""

    name: Literal["BootstrapFewShot"] = "BootstrapFewShot"
    metric_name: Literal[
        "pragmatic_category",
        "synthesis_exact_with_evidence",
    ] = "pragmatic_category"
    max_bootstrapped_demos: int = Field(default=4, ge=1)
    max_labeled_demos: int = Field(default=0, ge=0)
    max_rounds: int = Field(default=1, ge=1)
    trainset_size: int | None = Field(default=None, gt=0)


class ExperimentControls(FrozenModel):
    few_shot_policy: str
    context_policy: str
    verifier_policy: str
    repair_policy: str
    abstention_policy: str

    @model_validator(mode="after")
    def validate_required_text_fields(self) -> ExperimentControls:
        for field in [
            "few_shot_policy",
            "context_policy",
            "verifier_policy",
            "repair_policy",
            "abstention_policy",
        ]:
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must be a non-empty string.")
        return self


class ExperimentConfig(FrozenModel):
    experiment_id: str
    hypothesis: str
    dataset: Literal["gan_2026"]
    split_name: str
    split_file: Path
    model_config_path: Path
    schema_level: Literal["gan_frequency_s0"] = GAN_FREQUENCY_S0_SCHEMA_LEVEL
    program_variant: Literal["gan_frequency_s0_single_pass"] = GAN_FREQUENCY_S0_VARIANT
    scorer_mode: Literal["gan_frequency_deterministic_v1"] = GAN_FREQUENCY_S0_SCORER
    prompt_version: str
    controls: ExperimentControls
    structured_output_strategy: StructuredOutputStrategy
    output_root: Path = Path("runs")
    max_records: int | None = Field(default=None, gt=0)
    report_on_test_split: bool = False
    metric_caveats: list[str] = Field(default_factory=list)
    optimizer: OptimizerConfig | None = None

    @model_validator(mode="after")
    def validate_experiment_context(self) -> ExperimentConfig:
        for field in [
            "experiment_id",
            "hypothesis",
            "split_name",
            "prompt_version",
        ]:
            if not getattr(self, field).strip():
                raise ValueError(f"{field} must be a non-empty string.")

        if self.split_name.endswith(":test") and not self.report_on_test_split:
            raise ValueError(
                "Gan S0 experiment configs must explicitly set "
                "report_on_test_split=true before reporting on the test split."
            )
        return self


def load_experiment_config(path: Path) -> ExperimentConfig:
    return ExperimentConfig.model_validate_json(path.read_text(encoding="utf-8"))


def write_experiment_config(config: ExperimentConfig, path: Path) -> None:
    path.write_text(
        json.dumps(config.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_SCHEMA_LEVEL,
    EXECT_S0_S1_SCORER,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_VARIANT,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
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
    dataset: Literal["gan_2026", "exect_v2"]
    split_name: str
    split_file: Path
    model_config_path: Path
    schema_level: Literal[
        "gan_frequency_s0",
        "exect_s0_s1_field_family",
    ] = GAN_FREQUENCY_S0_SCHEMA_LEVEL
    program_variant: Literal[
        "gan_frequency_s0_single_pass",
        "gan_frequency_s0_direct_single_pass",
        "exect_s0_s1_field_family_single_pass",
        "exect_s0_s1_field_family_section_aware",
    ] = GAN_FREQUENCY_S0_VARIANT
    scorer_mode: Literal[
        "gan_frequency_deterministic_v1",
        "exect_field_family_deterministic_v1",
    ] = GAN_FREQUENCY_S0_SCORER
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

        expected_contracts = {
            "gan_2026": (
                GAN_FREQUENCY_S0_SCHEMA_LEVEL,
                {GAN_FREQUENCY_S0_VARIANT, GAN_FREQUENCY_S0_DIRECT_VARIANT},
                GAN_FREQUENCY_S0_SCORER,
            ),
            "exect_v2": (
                EXECT_S0_S1_SCHEMA_LEVEL,
                {
                    EXECT_S0_S1_VARIANT,
                    EXECT_S0_S1_SECTION_AWARE_VARIANT,
                },
                EXECT_S0_S1_SCORER,
            ),
        }
        expected_schema, expected_variants, expected_scorer = expected_contracts[self.dataset]
        if (
            self.schema_level != expected_schema
            or self.program_variant not in expected_variants
            or self.scorer_mode != expected_scorer
        ):
            raise ValueError(
                f"{self.dataset} experiment configs must use schema_level="
                f"{expected_schema!r}, program_variant in {sorted(expected_variants)!r}, "
                f"and scorer_mode={expected_scorer!r}."
            )

        if self.split_name.endswith(":test") and not self.report_on_test_split:
            raise ValueError(
                "Experiment configs must explicitly set "
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

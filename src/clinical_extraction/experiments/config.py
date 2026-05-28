from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from clinical_extraction.gan.scoring import GAN_PAPER_REPRODUCTION_SCORER
from clinical_extraction.gan.s0.variant_routing import (
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_VARIANT,
)
from clinical_extraction.experiments.program_variant_registry import (
    program_contract_allows,
)
from clinical_extraction.experiments.taxonomy import (
    ExperimentTaxonomy,
    TaxonomyExemptionValue,
    taxonomy_covers_config,
)
from clinical_extraction.paths import resolve_config_path
from clinical_extraction.schemas import FrozenModel


StructuredOutputStrategy = Literal[
    "provider_json_schema_with_pydantic_validation",
    "strict_json_prompt_with_pydantic_validation",
]


class OptimizerConfig(FrozenModel):
    """DSPy optimizer hyperparameters for module compilation."""

    name: Literal[
        "BootstrapFewShot",
        "BootstrapFewShotWithRandomSearch",
        "LabeledFewShot",
        "GEPA",
    ] = "BootstrapFewShot"
    metric_name: Literal[
        "pragmatic_category",
        "semantic_frequency_with_evidence",
        "semantic_frequency_with_evidence_feedback",
        "gan_s0_stage_attributed_frequency_feedback",
        "synthesis_exact_with_evidence",
        "synthesis_exact_with_evidence_feedback",
        "exect_field_family_micro_f1",
        "exect_field_family_micro_f1_raw",
    ] = "semantic_frequency_with_evidence"
    max_bootstrapped_demos: int = Field(default=4, ge=0)
    max_labeled_demos: int = Field(default=0, ge=0)
    max_rounds: int = Field(default=1, ge=1)
    num_candidate_programs: int = Field(default=16, ge=1)
    trainset_size: int | None = Field(default=None, gt=0)
    auto: Literal["light", "medium", "heavy"] | None = None
    max_full_evals: int | None = Field(default=None, gt=0)
    max_metric_calls: int | None = Field(default=None, gt=0)
    reflection_minibatch_size: int = Field(default=3, ge=1)
    candidate_selection_strategy: Literal["pareto", "current_best"] = "pareto"
    skip_perfect_score: bool = True
    add_format_failure_as_feedback: bool = False
    track_stats: bool = False
    track_best_outputs: bool = False
    use_cloudpickle: bool = False
    num_threads: int | None = Field(default=None, gt=0)
    seed: int | None = 0

    @model_validator(mode="after")
    def validate_optimizer_settings(self) -> OptimizerConfig:
        if self.name == "LabeledFewShot":
            if self.max_labeled_demos < 1:
                raise ValueError(
                    "LabeledFewShot optimizer configs must set max_labeled_demos >= 1."
                )
            if self.metric_name in {
                "semantic_frequency_with_evidence_feedback",
                "gan_s0_stage_attributed_frequency_feedback",
                "synthesis_exact_with_evidence_feedback",
            }:
                raise ValueError(
                    "LabeledFewShot optimizer configs must use a scalar metric."
                )
            return self

        if self.name in {"BootstrapFewShot", "BootstrapFewShotWithRandomSearch"}:
            if self.max_bootstrapped_demos < 1:
                raise ValueError(
                    f"{self.name} optimizer configs must set max_bootstrapped_demos >= 1."
                )
            if self.metric_name in {
                "semantic_frequency_with_evidence_feedback",
                "gan_s0_stage_attributed_frequency_feedback",
                "synthesis_exact_with_evidence_feedback",
            }:
                raise ValueError(
                    f"{self.name} optimizer configs must use a scalar metric."
                )
            return self

        if self.metric_name not in {
            "semantic_frequency_with_evidence_feedback",
            "gan_s0_stage_attributed_frequency_feedback",
            "synthesis_exact_with_evidence_feedback",
        }:
            raise ValueError("GEPA optimizer configs must use a feedback metric.")
        configured_budgets = sum(
            value is not None
            for value in (self.auto, self.max_full_evals, self.max_metric_calls)
        )
        if configured_budgets == 0:
            raise ValueError(
                "GEPA optimizer configs must set auto, max_full_evals, or max_metric_calls."
            )
        if configured_budgets != 1:
            raise ValueError(
                "GEPA optimizer configs must set exactly one of auto, max_full_evals, "
                "or max_metric_calls."
            )
        return self


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
    schema_level: str = GAN_FREQUENCY_S0_SCHEMA_LEVEL
    program_variant: str = GAN_FREQUENCY_S0_VARIANT
    scorer_mode: str = GAN_PAPER_REPRODUCTION_SCORER
    prompt_version: str
    controls: ExperimentControls
    structured_output_strategy: StructuredOutputStrategy
    output_root: Path = Path("runs")
    max_records: int | None = Field(default=None, gt=0)
    record_ids: list[str] | None = None
    report_on_test_split: bool = False
    metric_caveats: list[str] = Field(default_factory=list)
    optimizer: OptimizerConfig | None = None
    taxonomy: ExperimentTaxonomy | None = None
    taxonomy_exemption: TaxonomyExemptionValue | None = None

    @model_validator(mode="after")
    def validate_taxonomy_fields(self) -> ExperimentConfig:
        if self.taxonomy is not None and self.taxonomy_exemption is not None:
            raise ValueError(
                "Experiment configs must set either taxonomy or taxonomy_exemption, not both."
            )
        if self.taxonomy is not None and not taxonomy_covers_config(
            self.dataset, self.taxonomy
        ):
            raise ValueError(
                "taxonomy.dataset must match the top-level dataset field on the config."
            )
        return self

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

        if not program_contract_allows(
            dataset=self.dataset,
            schema_level=self.schema_level,
            program_variant=self.program_variant,
            scorer_mode=self.scorer_mode,
        ):
            raise ValueError(
                f"{self.dataset} experiment configs must use a registered program "
                f"variant contract for schema_level/program_variant/scorer_mode."
            )

        if self.split_name.endswith(":test") and not self.report_on_test_split:
            raise ValueError(
                "Experiment configs must explicitly set "
                "report_on_test_split=true before reporting on the test split."
            )
        if self.record_ids is not None:
            if not self.record_ids:
                raise ValueError("record_ids must be a non-empty list when set.")
            if any(not record_id.strip() for record_id in self.record_ids):
                raise ValueError("record_ids entries must be non-empty strings.")
        return self


def load_experiment_config(
    path: Path,
    *,
    include_archive: bool = False,
) -> ExperimentConfig:
    path = resolve_config_path(path, include_archive=include_archive)
    return ExperimentConfig.model_validate_json(path.read_text(encoding="utf-8"))


def write_experiment_config(config: ExperimentConfig, path: Path) -> None:
    path.write_text(
        json.dumps(config.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

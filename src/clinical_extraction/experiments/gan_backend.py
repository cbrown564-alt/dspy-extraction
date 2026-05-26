"""Gan S0 experiment backend."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import dspy

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import evaluate_gan_predictions
from clinical_extraction.experiments.config import ExperimentConfig, OptimizerConfig
from clinical_extraction.experiments.gan_prompts import gan_prompts_data
from clinical_extraction.gan.temporal_candidates import (
    presentation_for_implementation_variant,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    build_gan_s0_module,
    compile_gan_s0_module,
    compile_gan_s0_module_gepa,
    gan_frequency_s0_run_metadata,
    predict_gan_records,
)
from clinical_extraction.runs import RunMetadata


class GanExperimentBackend:
    dataset = "gan_2026"

    def load_records_by_id(self) -> dict[str, Any]:
        return {record.record_id: record for record in load_gan_records()}

    def build_module(
        self,
        config: ExperimentConfig,
        *,
        prompt_version: str,
    ) -> dspy.Module:
        return build_gan_s0_module(
            config.program_variant,
            prompt_version=prompt_version,
            candidate_presentation=self._candidate_presentation_from_config(config),
            context_policy=config.controls.context_policy,
        )

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
    ) -> RunMetadata:
        return gan_frequency_s0_run_metadata(
            run_id=run_id,
            split_name=split_name,
            model_provider=model_provider,
            model_name=model_name,
            prompt_version=prompt_version,
            program_variant=program_variant,
            extra=extra,
        )

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
    ) -> Any:
        del schema_level
        return predict_gan_records(
            module,
            records,
            model_provider=model_provider,
            model_name=model_name,
            prompt_version=prompt_version,
            program_variant=program_variant,
            repair_policy=repair_policy,
            progress_callback=progress_callback,
        )

    def evaluate_predictions(self, prediction_set: Any) -> dict[str, Any]:
        return evaluate_gan_predictions(prediction_set)

    def prompts_data(self, config: ExperimentConfig) -> dict[str, Any]:
        return gan_prompts_data(
            program_variant=config.program_variant,
            prompt_version=config.prompt_version,
            structured_output_strategy=config.structured_output_strategy,
        )

    def compile_module(
        self,
        *,
        config: ExperimentConfig,
        module: dspy.Module,
        train_records: list[Any],
        artifact_paths: dict[str, Path],
        reflection_lm: dspy.LM | None,
    ) -> dspy.Module:
        optimizer = config.optimizer
        if optimizer is None:
            return module
        if optimizer.name == "GEPA":
            return compile_gan_s0_module_gepa(
                train_records,
                program_variant=config.program_variant,
                optimizer_metric=optimizer.metric_name,
                auto=optimizer.auto,
                max_full_evals=optimizer.max_full_evals,
                max_metric_calls=optimizer.max_metric_calls,
                reflection_minibatch_size=optimizer.reflection_minibatch_size,
                candidate_selection_strategy=optimizer.candidate_selection_strategy,
                skip_perfect_score=optimizer.skip_perfect_score,
                add_format_failure_as_feedback=optimizer.add_format_failure_as_feedback,
                track_stats=optimizer.track_stats,
                track_best_outputs=optimizer.track_best_outputs,
                use_cloudpickle=optimizer.use_cloudpickle,
                num_threads=optimizer.num_threads,
                seed=optimizer.seed,
                log_dir=artifact_paths["optimizer_logs"],
                reflection_lm=reflection_lm,
            )
        return compile_gan_s0_module(
            train_records,
            program_variant=config.program_variant,
            optimizer_name=optimizer.name,
            max_bootstrapped_demos=optimizer.max_bootstrapped_demos,
            max_labeled_demos=optimizer.max_labeled_demos,
            max_rounds=optimizer.max_rounds,
            num_candidate_programs=optimizer.num_candidate_programs,
            optimizer_metric=optimizer.metric_name,
        )

    def optimizer_unsupported_message(self, optimizer: OptimizerConfig) -> str | None:
        del optimizer
        return None

    @staticmethod
    def _candidate_presentation_from_config(
        config: ExperimentConfig,
    ) -> str | None:
        if config.taxonomy is None:
            return None
        return presentation_for_implementation_variant(
            config.taxonomy.implementation_variant
        )

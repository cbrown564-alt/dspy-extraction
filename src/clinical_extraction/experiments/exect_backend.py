"""ExECT S0-S4 experiment backend."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import dspy

from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.evaluation.exect import (
    score_exect_prediction_set,
    score_exect_s2_prediction_set,
    score_exect_s3_prediction_set,
    score_exect_s4_prediction_set,
    score_exect_s5_prediction_set,
)
from clinical_extraction.experiments.config import ExperimentConfig, OptimizerConfig
from clinical_extraction.experiments.exect_prompts import exect_prompts_data
from clinical_extraction.programs.exect_s2 import (
    EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
    EXECT_S2_COMORBIDITY_C0_VARIANT,
    EXECT_S2_INV_GUARD_I0_VARIANT,
    EXECT_S2_SCHEMA_LEVEL,
    EXECT_S2_VARIANT,
    build_exect_s2_module,
    exect_s2_run_metadata,
    predict_exect_s2_records,
)
from clinical_extraction.programs.exect_s3 import (
    EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S3_SCHEMA_LEVEL,
    EXECT_S3_VARIANT,
    build_exect_s3_module,
    exect_s3_run_metadata,
    predict_exect_s3_records,
)
from clinical_extraction.programs.exect_s4 import (
    EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
    EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
    EXECT_S4_FREQUENCY_PRE_VOCAB_HIGH_PRECISION_VARIANT,
    EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
    EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
    EXECT_S4_L1_VARIANT,
    EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT,
    EXECT_S4_SCHEMA_LEVEL,
    EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
    EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
    EXECT_S4_VARIANT,
    EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
    EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
    build_exect_s4_module,
    exect_s4_run_metadata,
    predict_exect_s4_records,
)
from clinical_extraction.programs.exect_s0_s1 import (
    build_exect_s0_s1_module,
    compile_exect_s0_s1_module,
    exect_s0_s1_run_metadata,
    predict_exect_records,
)
from clinical_extraction.runs import RunMetadata

EXECT_S5_SCHEMA_LEVEL = "exect_s5_core_field_family"

_EXECT_S2_PROGRAM_VARIANTS = frozenset(
    {
        EXECT_S2_VARIANT,
        EXECT_S2_COMORBIDITY_C0_VARIANT,
        EXECT_S2_COMORBIDITY_C0_C1_VARIANT,
        EXECT_S2_INV_GUARD_I0_VARIANT,
    }
)
_EXECT_S3_PROGRAM_VARIANTS = frozenset(
    {
        EXECT_S3_VARIANT,
        EXECT_S3_CAUSE_BRIDGE_K0_K1_VARIANT,
    }
)
_EXECT_S4_PROGRAM_VARIANTS = frozenset(
    {
        EXECT_S4_VARIANT,
        EXECT_S4_L1_VARIANT,
        EXECT_S4_FREQUENCY_PRE_VOCAB_VARIANT,
        EXECT_S4_FREQUENCY_PRE_VOCAB_HIGH_PRECISION_VARIANT,
        EXECT_S4_FREQUENCY_POST_MERGE_VARIANT,
        EXECT_S4_FREQUENCY_STRUCTURED_SLOTS_VARIANT,
        EXECT_S4_TEMPORALITY_POST_CLASSIFIER_VARIANT,
        EXECT_S4_MT_GUARD_NON_ASM_VARIANT,
        EXECT_S4_MT_GUARD_NON_ASM_DOSE_CURRENT_VARIANT,
        EXECT_S4_CAUSE_BRIDGE_K0_K1_VARIANT,
        EXECT_S5_AM_GUARD_NON_ASM_BRAND_ALIAS_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_VARIANT,
        EXECT_S5_FREQUENCY_PRE_VOCAB_AM_GUARD_FREQUENCY_VERIFY_VARIANT,
    }
)


class ExectExperimentBackend:
    dataset = "exect_v2"

    def load_records_by_id(self) -> dict[str, Any]:
        return {record.document_id: record for record in load_exect_gold_documents()}

    def build_module(
        self,
        config: ExperimentConfig,
        *,
        prompt_version: str,
    ) -> dspy.Module:
        program_variant = config.program_variant
        if program_variant in _EXECT_S4_PROGRAM_VARIANTS:
            return build_exect_s4_module(program_variant)
        if program_variant in _EXECT_S3_PROGRAM_VARIANTS:
            return build_exect_s3_module(program_variant)
        if program_variant in _EXECT_S2_PROGRAM_VARIANTS:
            return build_exect_s2_module(program_variant)
        return build_exect_s0_s1_module(program_variant, prompt_version=prompt_version)

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
        if program_variant in _EXECT_S4_PROGRAM_VARIANTS:
            return exect_s4_run_metadata(
                run_id=run_id,
                split_name=split_name,
                model_provider=model_provider,
                model_name=model_name,
                prompt_version=prompt_version,
                program_variant=program_variant,
                extra=extra,
                schema_level=extra.get("schema_level", EXECT_S4_SCHEMA_LEVEL),
            )
        if program_variant in _EXECT_S3_PROGRAM_VARIANTS:
            return exect_s3_run_metadata(
                run_id=run_id,
                split_name=split_name,
                model_provider=model_provider,
                model_name=model_name,
                prompt_version=prompt_version,
                program_variant=program_variant,
                extra=extra,
            )
        if program_variant in _EXECT_S2_PROGRAM_VARIANTS:
            return exect_s2_run_metadata(
                run_id=run_id,
                split_name=split_name,
                model_provider=model_provider,
                model_name=model_name,
                prompt_version=prompt_version,
                program_variant=program_variant,
                extra=extra,
            )
        return exect_s0_s1_run_metadata(
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
        if program_variant in _EXECT_S4_PROGRAM_VARIANTS:
            return predict_exect_s4_records(
                module,
                records,
                model_provider=model_provider,
                model_name=model_name,
                prompt_version=prompt_version,
                program_variant=program_variant,
                progress_callback=progress_callback,
                schema_level=schema_level or EXECT_S4_SCHEMA_LEVEL,
            )
        if program_variant in _EXECT_S3_PROGRAM_VARIANTS:
            return predict_exect_s3_records(
                module,
                records,
                model_provider=model_provider,
                model_name=model_name,
                prompt_version=prompt_version,
                program_variant=program_variant,
                progress_callback=progress_callback,
            )
        if program_variant in _EXECT_S2_PROGRAM_VARIANTS:
            return predict_exect_s2_records(
                module,
                records,
                model_provider=model_provider,
                model_name=model_name,
                prompt_version=prompt_version,
                program_variant=program_variant,
                progress_callback=progress_callback,
            )
        return predict_exect_records(
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
        if prediction_set.schema_level == EXECT_S5_SCHEMA_LEVEL:
            return score_exect_s5_prediction_set(prediction_set)
        if prediction_set.schema_level == EXECT_S4_SCHEMA_LEVEL:
            return score_exect_s4_prediction_set(prediction_set)
        if prediction_set.schema_level == EXECT_S3_SCHEMA_LEVEL:
            return score_exect_s3_prediction_set(prediction_set)
        if prediction_set.schema_level == EXECT_S2_SCHEMA_LEVEL:
            return score_exect_s2_prediction_set(prediction_set)
        return score_exect_prediction_set(prediction_set)

    def prompts_data(self, config: ExperimentConfig) -> dict[str, Any]:
        return exect_prompts_data(
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
        del artifact_paths, reflection_lm
        optimizer = config.optimizer
        if optimizer is None:
            return module
        return compile_exect_s0_s1_module(
            train_records,
            program_variant=config.program_variant,
            prompt_version=config.prompt_version,
            optimizer_name=optimizer.name,
            max_bootstrapped_demos=optimizer.max_bootstrapped_demos,
            max_labeled_demos=optimizer.max_labeled_demos,
            max_rounds=optimizer.max_rounds,
            num_candidate_programs=optimizer.num_candidate_programs,
            optimizer_metric=optimizer.metric_name,
        )

    def optimizer_unsupported_message(self, optimizer: OptimizerConfig) -> str | None:
        if optimizer.name == "GEPA":
            return "ExECT S0/S1 experiments do not support GEPA optimization yet."
        return None

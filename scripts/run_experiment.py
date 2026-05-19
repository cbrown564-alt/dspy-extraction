"""Run a Gan S0 experiment from an experiment config file.

Usage:
    uv run python scripts/run_experiment.py \\
        --experiment configs/experiments/gan_s0_baseline_gpt4_1_mini.json \\
        --env-file .env
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

import dspy

from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.exect import score_exect_prediction_set
from clinical_extraction.evaluation.cli import evaluate_gan_predictions
from clinical_extraction.experiments.config import load_experiment_config
from clinical_extraction.llms import LLMProviderConfig, build_dspy_lm
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT,
    EXECT_S0_S1_FIELD_FAMILIES,
    EXECT_S0_S1_LABEL_POLICY_GUIDANCE,
    EXECT_S0_S1_POLICY_EXAMPLES,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_VARIANT,
    build_exect_s0_s1_module,
    exect_s0_s1_run_metadata,
    predict_exect_records,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_SYNTHESIS_GUIDANCE,
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    GanFrequencyS0DirectModule,
    GanFrequencyS0Module,
    GanFrequencyS0TemporalCandidatesVerifyRepairModule,
    GanFrequencyS0VerifyRepairModule,
    build_gan_s0_module,
    compile_gan_s0_module_gepa,
    compile_gan_s0_module,
    gan_frequency_s0_run_metadata,
    predict_gan_records,
)
from clinical_extraction.runs import create_run_artifact_layout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a clinical extraction experiment from a config file.",
    )
    parser.add_argument("--experiment", required=True, type=Path)
    parser.add_argument("--run-id", help="Override auto-generated run ID.")
    parser.add_argument("--env-file", type=Path, help="Load API keys from .env file.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate config and print plan without making model calls.",
    )
    args = parser.parse_args(argv)

    if args.env_file:
        _load_env_file(args.env_file)

    config = load_experiment_config(args.experiment)
    print(f"Experiment: {config.experiment_id}")
    print(f"Dataset:    {config.dataset}")
    print(f"Split:      {config.split_name}")
    print(f"Model:      {config.model_config_path}")

    split_data = json.loads(config.split_file.read_text(encoding="utf-8"))
    split_subset = config.split_name.split(":")[-1]
    if split_subset not in split_data or not isinstance(split_data[split_subset], list):
        raise SystemExit(
            f"Split subset {split_subset!r} not found in {config.split_file}."
        )

    ordered_split_ids: list[str] = split_data[split_subset]
    if config.record_ids is not None:
        split_id_set = set(ordered_split_ids)
        missing_from_split = [
            record_id for record_id in config.record_ids if record_id not in split_id_set
        ]
        if missing_from_split:
            raise SystemExit(
                f"record_ids not in split {config.split_name!r}: {missing_from_split}"
            )
        ordered_split_ids = list(config.record_ids)
    if config.max_records is not None:
        ordered_split_ids = ordered_split_ids[: config.max_records]

    all_records = _load_records_by_id(config.dataset)
    records = [all_records[rid] for rid in ordered_split_ids if rid in all_records]
    missing_from_dataset = [rid for rid in ordered_split_ids if rid not in all_records]
    if missing_from_dataset:
        print(
            f"Warning: {len(missing_from_dataset)} split IDs not in {config.dataset} records: "
            f"{missing_from_dataset[:5]}"
        )

    record_note = ""
    if config.record_ids is not None:
        record_note = f" (record_ids filter, n={len(config.record_ids)})"
    elif config.max_records is not None:
        record_note = f" (capped at max_records={config.max_records})"
    print(f"Records:    {len(records)}{record_note}")
    _print_optimizer_plan(config.optimizer)

    if args.dry_run:
        print("\nDry run — exiting before model calls.")
        return 0

    model_config = LLMProviderConfig.model_validate_json(
        config.model_config_path.read_text(encoding="utf-8")
    )
    lm = build_dspy_lm(model_config)
    dspy.configure(lm=lm)
    reflection_lm = None
    if config.optimizer is not None and config.optimizer.name == "GEPA":
        reflection_config = model_config.model_copy(update={"temperature": 1.0})
        reflection_lm = build_dspy_lm(reflection_config)

    run_id = args.run_id or _make_run_id(config.experiment_id)
    metadata = _run_metadata(
        dataset=config.dataset,
        run_id=run_id,
        split_name=config.split_name,
        model_provider=model_config.provider,
        model_name=model_config.model,
        prompt_version=config.prompt_version,
        program_variant=config.program_variant,
        extra={
            "experiment_id": config.experiment_id,
            "structured_output_strategy": config.structured_output_strategy,
        },
    )
    metadata = metadata.model_copy(update={"metric_caveats": config.metric_caveats})
    paths = create_run_artifact_layout(metadata, root=config.output_root)
    print(f"\nRun directory: {paths['run']}")

    paths["config"].write_text(
        json.dumps(config.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    module = _build_module(config.dataset, config.program_variant)
    run_started = perf_counter()
    compile_duration_seconds: float | None = None

    if config.optimizer is not None:
        if config.dataset != "gan_2026":
            raise SystemExit("Only Gan S0 experiments currently support DSPy optimization.")
        dev_ids: list[str] = split_data.get("development", [])
        if config.optimizer.trainset_size is not None:
            dev_ids = dev_ids[: config.optimizer.trainset_size]
        dev_records = [all_records[rid] for rid in dev_ids if rid in all_records]
        _print_compile_message(config.optimizer, len(dev_records))
        compile_started = perf_counter()
        if config.optimizer.name == "GEPA":
            module = compile_gan_s0_module_gepa(
                dev_records,
                program_variant=config.program_variant,
                optimizer_metric=config.optimizer.metric_name,
                auto=config.optimizer.auto,
                max_full_evals=config.optimizer.max_full_evals,
                max_metric_calls=config.optimizer.max_metric_calls,
                reflection_minibatch_size=config.optimizer.reflection_minibatch_size,
                candidate_selection_strategy=config.optimizer.candidate_selection_strategy,
                skip_perfect_score=config.optimizer.skip_perfect_score,
                add_format_failure_as_feedback=(
                    config.optimizer.add_format_failure_as_feedback
                ),
                track_stats=config.optimizer.track_stats,
                track_best_outputs=config.optimizer.track_best_outputs,
                use_cloudpickle=config.optimizer.use_cloudpickle,
                num_threads=config.optimizer.num_threads,
                seed=config.optimizer.seed,
                log_dir=paths["optimizer_logs"],
                reflection_lm=reflection_lm,
            )
        else:
            module = compile_gan_s0_module(
                dev_records,
                program_variant=config.program_variant,
                optimizer_name=config.optimizer.name,
                max_bootstrapped_demos=config.optimizer.max_bootstrapped_demos,
                max_labeled_demos=config.optimizer.max_labeled_demos,
                max_rounds=config.optimizer.max_rounds,
                num_candidate_programs=config.optimizer.num_candidate_programs,
                optimizer_metric=config.optimizer.metric_name,
            )
        compile_duration_seconds = perf_counter() - compile_started
        print("Compilation complete.")

    prompts_data = _prompts_data(
        config.dataset,
        config.program_variant,
        config.prompt_version,
        config.structured_output_strategy,
    )
    if config.optimizer is not None:
        prompts_data["optimizer"] = config.optimizer.model_dump()
        _write_compiled_state(module, paths["compiled_state"])
        _write_optimizer_summary(config.optimizer.model_dump(), paths["optimizer_artifacts"])
    paths["prompts"].write_text(
        json.dumps(prompts_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Running {len(records)} predictions...")
    prediction_started = perf_counter()
    prediction_set = _predict_records(
        dataset=config.dataset,
        module=module,
        records=records,
        model_provider=model_config.provider,
        model_name=model_config.model,
        prompt_version=config.prompt_version,
        program_variant=config.program_variant,
        progress_callback=_print_prediction_progress,
    )
    prediction_duration_seconds = perf_counter() - prediction_started
    paths["predictions"].write_text(
        json.dumps(prediction_set.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Evaluating...")
    evaluation_started = perf_counter()
    report = _evaluate_predictions(prediction_set)
    evaluation_duration_seconds = perf_counter() - evaluation_started
    token_usage = _collect_lm_token_usage(
        [candidate for candidate in [lm, reflection_lm] if candidate is not None]
    )
    model_residency = _capture_local_model_residency(
        model_config.provider,
        model_config.model,
    )
    report["runtime"] = _runtime_report(
        records=len(records),
        optimizer=config.optimizer.model_dump() if config.optimizer else None,
        compile_duration_seconds=compile_duration_seconds,
        prediction_duration_seconds=prediction_duration_seconds,
        evaluation_duration_seconds=evaluation_duration_seconds,
        total_duration_seconds=perf_counter() - run_started,
        token_usage=token_usage,
        model_residency=model_residency,
    )
    paths["metrics"].write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths["errors"].write_text(
        json.dumps(report.get("errors", {}), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    _print_summary(report, config.metric_caveats)
    return 0


def _load_records_by_id(dataset: str) -> dict[str, Any]:
    if dataset == "gan_2026":
        return {record.record_id: record for record in load_gan_records()}
    if dataset == "exect_v2":
        return {record.document_id: record for record in load_exect_gold_documents()}
    raise SystemExit(f"Unsupported dataset: {dataset!r}")


def _build_module(dataset: str, program_variant: str) -> dspy.Module:
    if dataset == "gan_2026":
        return build_gan_s0_module(program_variant)
    if dataset == "exect_v2":
        return build_exect_s0_s1_module(program_variant)
    raise SystemExit(f"Unsupported dataset: {dataset!r}")


def _run_metadata(
    *,
    dataset: str,
    run_id: str,
    split_name: str,
    model_provider: str,
    model_name: str,
    prompt_version: str,
    program_variant: str,
    extra: dict[str, Any],
):
    if dataset == "gan_2026":
        return gan_frequency_s0_run_metadata(
            run_id=run_id,
            split_name=split_name,
            model_provider=model_provider,
            model_name=model_name,
            prompt_version=prompt_version,
            program_variant=program_variant,
            extra=extra,
        )
    if dataset == "exect_v2":
        return exect_s0_s1_run_metadata(
            run_id=run_id,
            split_name=split_name,
            model_provider=model_provider,
            model_name=model_name,
            prompt_version=prompt_version,
            program_variant=program_variant,
            extra=extra,
        )
    raise SystemExit(f"Unsupported dataset: {dataset!r}")


def _prompts_data(
    dataset: str,
    program_variant: str,
    prompt_version: str,
    structured_output_strategy: str,
) -> dict[str, Any]:
    if dataset == "gan_2026":
        module_name = "GanFrequencyS0Module"
        predictor_name = "dspy.ChainOfThought"
        if program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT:
            module_name = "GanFrequencyS0DirectModule"
            predictor_name = "dspy.Predict"
        elif program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT:
            module_name = "GanFrequencyS0VerifyRepairModule"
            predictor_name = "dspy.Predict + dspy.Predict"
        elif program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT:
            module_name = "GanFrequencyS0TemporalCandidatesVerifyRepairModule"
            predictor_name = (
                "dspy.Predict + deterministic temporal candidates + dspy.Predict"
            )
        return {
            "signature": "GanFrequencyS0Signature",
            "module": module_name,
            "predictor": predictor_name,
            "program_variant": program_variant,
            "prompt_version": prompt_version,
            "synthesis_guidance": GAN_FREQUENCY_SYNTHESIS_GUIDANCE,
            "structured_output_strategy": structured_output_strategy,
        }
    if dataset == "exect_v2":
        if program_variant == EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT:
            module_name = "ExectS0S1DiagnosisRecallProbeModule"
            predictor_name = "dspy.ChainOfThought + dspy.Predict"
        elif program_variant == EXECT_S0_S1_VARIANT:
            module_name = "ExectS0S1FieldFamilyModule"
            predictor_name = "dspy.ChainOfThought"
        else:
            module_name = "ExectS0S1SectionAwareFieldFamilyModule"
            predictor_name = (
                "dspy.ChainOfThought (diagnosis) + dspy.ChainOfThought (seizure) + "
                "dspy.ChainOfThought (medication)"
            )
        return {
            "signature": (
                "ExectS0S1FieldFamilySignature + ExectS0S1DiagnosisRecallSignature"
                if program_variant == EXECT_S0_S1_DIAGNOSIS_RECALL_VARIANT
                else (
                    "ExectS0S1FieldFamilySignature"
                    if program_variant == EXECT_S0_S1_VARIANT
                    else "ExectS0S1DiagnosisSignature + "
                    "ExectS0S1SeizureTypeSignature + ExectS0S1MedicationSignature"
                )
            ),
            "module": module_name,
            "predictor": predictor_name,
            "program_variant": program_variant,
            "prompt_version": prompt_version or EXECT_S0_S1_PROMPT_VERSION,
            "field_families": EXECT_S0_S1_FIELD_FAMILIES,
            "label_policy_guidance": EXECT_S0_S1_LABEL_POLICY_GUIDANCE,
            "label_policy_examples": EXECT_S0_S1_POLICY_EXAMPLES,
            "structured_output_strategy": structured_output_strategy,
        }
    raise SystemExit(f"Unsupported dataset: {dataset!r}")


def _predict_records(
    *,
    dataset: str,
    module: dspy.Module,
    records: list[Any],
    model_provider: str,
    model_name: str,
    prompt_version: str,
    program_variant: str,
    progress_callback: Callable[[int, int, str], None] | None,
) -> Any:
    if dataset == "gan_2026":
        return predict_gan_records(
            module,
            records,
            model_provider=model_provider,
            model_name=model_name,
            prompt_version=prompt_version,
            program_variant=program_variant,
            progress_callback=progress_callback,
        )
    if dataset == "exect_v2":
        return predict_exect_records(
            module,
            records,
            model_provider=model_provider,
            model_name=model_name,
            prompt_version=prompt_version,
            program_variant=program_variant,
            progress_callback=progress_callback,
        )
    raise SystemExit(f"Unsupported dataset: {dataset!r}")


def _evaluate_predictions(prediction_set) -> dict[str, Any]:
    if prediction_set.dataset == "gan_2026":
        return evaluate_gan_predictions(prediction_set)
    if prediction_set.dataset == "exect_v2":
        return score_exect_prediction_set(prediction_set)
    raise SystemExit(f"Unsupported dataset: {prediction_set.dataset!r}")


def _print_prediction_progress(index: int, total: int, record_id: str) -> None:
    if index == 1 or index == total or index % 10 == 0:
        print(f"  Predicted {index}/{total} records (last={record_id})", flush=True)


def _make_run_id(experiment_id: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{experiment_id}_{timestamp}"


def _load_env_file(path: Path) -> None:
    """Load KEY=VALUE pairs from a .env file into os.environ (existing vars win)."""
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value


def _write_compiled_state(
    module: GanFrequencyS0Module | GanFrequencyS0DirectModule | GanFrequencyS0VerifyRepairModule,
    compiled_state_path: Path,
) -> None:
    dump_state = getattr(module, "dump_state", None)
    if not callable(dump_state):
        return
    state = dump_state()
    compiled_state_path.write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_optimizer_summary(optimizer: dict[str, Any], optimizer_dir: Path) -> None:
    optimizer_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "optimizer": optimizer,
        "artifact_files": {
            "compiled_state": "../compiled_state.json",
            "gepa_logs": "logs" if optimizer.get("name") == "GEPA" else None,
        },
    }
    (optimizer_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _print_optimizer_plan(optimizer: Any | None) -> None:
    if optimizer is None:
        print("Optimizer: none")
        return

    if optimizer.name == "GEPA":
        print(
            "Optimizer: GEPA "
            f"(metric={optimizer.metric_name}, "
            f"auto={optimizer.auto}, "
            f"max_full_evals={optimizer.max_full_evals}, "
            f"max_metric_calls={optimizer.max_metric_calls}, "
            f"reflection_minibatch_size={optimizer.reflection_minibatch_size}, "
            f"candidate_selection={optimizer.candidate_selection_strategy})"
        )
        return

    if optimizer.name == "LabeledFewShot":
        print(
            "Optimizer: LabeledFewShot "
            f"(max_labeled_demos={optimizer.max_labeled_demos}, "
            f"trainset_size={optimizer.trainset_size})"
        )
        return

    if optimizer.name == "BootstrapFewShotWithRandomSearch":
        print(
            "Optimizer: BootstrapFewShotWithRandomSearch "
            f"(metric={optimizer.metric_name}, "
            f"max_bootstrapped_demos={optimizer.max_bootstrapped_demos}, "
            f"max_labeled_demos={optimizer.max_labeled_demos}, "
            f"max_rounds={optimizer.max_rounds}, "
            f"num_candidate_programs={optimizer.num_candidate_programs}, "
            f"trainset_size={optimizer.trainset_size})"
        )
        return

    print(
        "Optimizer: BootstrapFewShot "
        f"(metric={optimizer.metric_name}, "
        f"max_bootstrapped_demos={optimizer.max_bootstrapped_demos}, "
        f"max_labeled_demos={optimizer.max_labeled_demos}, "
        f"max_rounds={optimizer.max_rounds}, "
        f"trainset_size={optimizer.trainset_size})"
    )


def _print_compile_message(optimizer: Any, dev_record_count: int) -> None:
    if optimizer.name == "GEPA":
        print(
            f"Compiling with GEPA on {dev_record_count} dev records "
            f"(metric={optimizer.metric_name}, "
            f"auto={optimizer.auto}, "
            f"max_full_evals={optimizer.max_full_evals}, "
            f"max_metric_calls={optimizer.max_metric_calls})..."
        )
        return

    if optimizer.name == "LabeledFewShot":
        print(
            f"Compiling with LabeledFewShot on {dev_record_count} dev records "
            f"(max_labeled_demos={optimizer.max_labeled_demos})..."
        )
        return

    if optimizer.name == "BootstrapFewShotWithRandomSearch":
        print(
            f"Compiling with BootstrapFewShotWithRandomSearch on {dev_record_count} dev records "
            f"(metric={optimizer.metric_name}, "
            f"max_bootstrapped_demos={optimizer.max_bootstrapped_demos}, "
            f"max_labeled_demos={optimizer.max_labeled_demos}, "
            f"max_rounds={optimizer.max_rounds}, "
            f"num_candidate_programs={optimizer.num_candidate_programs})..."
        )
        return

    print(
        f"Compiling with BootstrapFewShot on {dev_record_count} dev records "
        f"(metric={optimizer.metric_name}, "
        f"max_bootstrapped_demos={optimizer.max_bootstrapped_demos}, "
        f"max_labeled_demos={optimizer.max_labeled_demos}, "
        f"max_rounds={optimizer.max_rounds})..."
    )


def _runtime_report(
    *,
    records: int,
    optimizer: dict[str, Any] | None,
    compile_duration_seconds: float | None,
    prediction_duration_seconds: float,
    evaluation_duration_seconds: float,
    total_duration_seconds: float,
    token_usage: dict[str, int] | None,
    model_residency: str,
) -> dict[str, Any]:
    prediction_seconds_per_record = (
        prediction_duration_seconds / records if records else None
    )
    estimated_model_calls = records
    if optimizer is not None:
        estimated_model_calls += int(optimizer.get("trainset_size") or 0)
    return {
        "records": records,
        "estimated_model_calls": estimated_model_calls,
        "optimizer": optimizer,
        "compile_duration_seconds": compile_duration_seconds,
        "prediction_duration_seconds": prediction_duration_seconds,
        "prediction_seconds_per_record": prediction_seconds_per_record,
        "evaluation_duration_seconds": evaluation_duration_seconds,
        "total_duration_seconds": total_duration_seconds,
        "token_usage": token_usage,
        "model_residency": model_residency,
    }


def _collect_lm_token_usage(lms: list[dspy.LM]) -> dict[str, int] | None:
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    history_entries = 0
    saw_usage = False

    for lm in lms:
        for entry in getattr(lm, "history", []):
            usage = entry.get("usage") if isinstance(entry, dict) else None
            if not isinstance(usage, dict) or not usage:
                continue
            saw_usage = True
            history_entries += 1
            prompt_value = _usage_int(usage, "prompt_tokens", "input_tokens")
            completion_value = _usage_int(usage, "completion_tokens", "output_tokens")
            total_value = _usage_int(usage, "total_tokens")
            prompt_tokens += prompt_value
            completion_tokens += completion_value
            total_tokens += total_value or (prompt_value + completion_value)

    if not saw_usage:
        return None

    return {
        "history_entries": history_entries,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
    }


def _usage_int(usage: dict[str, Any], *keys: str) -> int:
    for key in keys:
        value = usage.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
    return 0


def _capture_local_model_residency(
    provider: str,
    model_name: str,
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> str:
    if provider != "ollama":
        return "not_applicable"
    try:
        completed = runner(
            ["ollama", "ps"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return "unavailable"

    output = (completed.stdout or "").strip()
    if not output:
        return "unavailable"

    residency = _parse_ollama_ps_output(output, model_name)
    return residency or "unavailable"


def _parse_ollama_ps_output(output: str, model_name: str) -> str | None:
    lines = [line.rstrip() for line in output.splitlines() if line.strip()]
    if len(lines) < 2:
        return None

    for line in lines[1:]:
        columns = re.split(r"\s{2,}", line.strip())
        if len(columns) < 5 or columns[0] != model_name:
            continue
        processor = columns[3]
        context = columns[4]
        if not processor:
            return None
        return f"{processor} (context={context})"
    return None


def _print_summary(report: dict[str, Any], metric_caveats: list[str]) -> None:
    counts = report.get("counts", {})
    bm = report.get("benchmark_metrics", {})
    diag = report.get("diagnostic_metrics", {})

    def pct(v: float | None) -> str:
        return f"{v:.1%}" if v is not None else "N/A"

    print("\n--- Counts ---")
    print(f"  Evaluated:  {counts.get('evaluated_records')}")
    if report.get("dataset") == "gan_2026":
        print(f"  Valid:      {counts.get('valid_predictions')}")
        print(f"  Invalid:    {counts.get('invalid_predictions')}")
    print(f"  Missing:    {counts.get('missing_predictions')}")

    if report.get("dataset") == "exect_v2":
        print("\n--- Field-family metrics (partial ExECT S0/S1) ---")
        print(f"  Micro precision: {pct(bm.get('micro_precision'))}")
        print(f"  Micro recall:    {pct(bm.get('micro_recall'))}")
        print(f"  Micro F1:        {pct(bm.get('micro_f1'))}")
        for family, f1 in bm.get("field_f1", {}).items():
            support = bm.get("field_support", {}).get(family)
            print(f"  {family} F1: {pct(f1)} (support={support})")
        print("\n--- Diagnostic metrics ---")
        print(
            "  Documents with gold quality flags: "
            f"{pct(diag.get('documents_with_gold_quality_flags'))}"
        )
        print(f"  Evidence quote support rate: {pct(diag.get('evidence_quote_support_rate'))}")
        print(
            "  Evidence quote support rate (exact only): "
            f"{pct(diag.get('evidence_quote_support_rate_without_repairs'))}"
        )
        print(
            "  Evidence quote support rate (ellipsis repairs): "
            f"{pct(diag.get('evidence_quote_support_rate_repaired'))}"
        )
        print(f"  Evidence quote repair rate: {pct(diag.get('evidence_quote_repair_rate'))}")
        print(f"  Evidence offsets present rate: {pct(diag.get('evidence_offsets_present_rate'))}")
        print(f"  Evidence offsets valid rate:   {pct(diag.get('evidence_offsets_valid_rate'))}")
    else:
        print("\n--- Benchmark metrics (not published reproduction) ---")
        print(f"  Monthly frequency accuracy:  {pct(bm.get('monthly_frequency_accuracy'))}")
        print(f"  Purist category accuracy:    {pct(bm.get('purist_category_accuracy'))}")
        print(f"  Pragmatic category accuracy: {pct(bm.get('pragmatic_category_accuracy'))}")

        print("\n--- Diagnostic metrics ---")
        print(f"  Schema validity rate:         {pct(diag.get('schema_valid_prediction_rate'))}")
        print(f"  Normalized label accuracy:    {pct(diag.get('normalized_label_accuracy'))}")
        print(f"  Evidence quote support rate:  {pct(diag.get('evidence_quote_support_rate'))}")

    if metric_caveats:
        print("\n--- Caveats ---")
        for caveat in metric_caveats:
            print(f"  * {caveat}")


if __name__ == "__main__":
    raise SystemExit(main())

"""Generic experiment runner utilities shared across dataset backends."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, TextIO

import dspy

from clinical_extraction.experiments.backends import get_backend
from clinical_extraction.experiments.config import ExperimentConfig, OptimizerConfig, load_experiment_config
from clinical_extraction.llms import LLMProviderConfig, build_dspy_lm
from clinical_extraction.runs import create_run_artifact_layout


def make_run_id(experiment_id: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{experiment_id}_{timestamp}"


def load_env_file(path: Path) -> None:
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


def resolve_split_record_ids(config: ExperimentConfig) -> list[str]:
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
    return ordered_split_ids


def load_split_records(
    config: ExperimentConfig,
    all_records: dict[str, Any],
) -> tuple[list[Any], list[str]]:
    ordered_split_ids = resolve_split_record_ids(config)
    records = [all_records[rid] for rid in ordered_split_ids if rid in all_records]
    missing_from_dataset = [rid for rid in ordered_split_ids if rid not in all_records]
    return records, missing_from_dataset


def record_count_note(config: ExperimentConfig) -> str:
    if config.record_ids is not None:
        return f" (record_ids filter, n={len(config.record_ids)})"
    if config.max_records is not None:
        return f" (capped at max_records={config.max_records})"
    return ""


def print_prediction_progress(
    index: int,
    total: int,
    record_id: str,
    *,
    file: TextIO | None = None,
) -> None:
    if index == 1 or index == total or index % 10 == 0:
        print(
            f"  Predicted {index}/{total} records (last={record_id})",
            file=file,
            flush=True,
        )


def print_optimizer_plan(
    optimizer: OptimizerConfig | None,
    *,
    file: TextIO | None = None,
) -> None:
    if optimizer is None:
        print("Optimizer: none", file=file)
        return

    if optimizer.name == "GEPA":
        print(
            "Optimizer: GEPA "
            f"(metric={optimizer.metric_name}, "
            f"auto={optimizer.auto}, "
            f"max_full_evals={optimizer.max_full_evals}, "
            f"max_metric_calls={optimizer.max_metric_calls}, "
            f"reflection_minibatch_size={optimizer.reflection_minibatch_size}, "
            f"candidate_selection={optimizer.candidate_selection_strategy})",
            file=file,
        )
        return

    if optimizer.name == "LabeledFewShot":
        print(
            "Optimizer: LabeledFewShot "
            f"(max_labeled_demos={optimizer.max_labeled_demos}, "
            f"trainset_size={optimizer.trainset_size})",
            file=file,
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
            f"trainset_size={optimizer.trainset_size})",
            file=file,
        )
        return

    print(
        "Optimizer: BootstrapFewShot "
        f"(metric={optimizer.metric_name}, "
        f"max_bootstrapped_demos={optimizer.max_bootstrapped_demos}, "
        f"max_labeled_demos={optimizer.max_labeled_demos}, "
        f"max_rounds={optimizer.max_rounds}, "
        f"trainset_size={optimizer.trainset_size})",
        file=file,
    )


def print_compile_message(
    optimizer: OptimizerConfig,
    dev_record_count: int,
    *,
    file: TextIO | None = None,
) -> None:
    if optimizer.name == "GEPA":
        print(
            f"Compiling with GEPA on {dev_record_count} dev records "
            f"(metric={optimizer.metric_name}, "
            f"auto={optimizer.auto}, "
            f"max_full_evals={optimizer.max_full_evals}, "
            f"max_metric_calls={optimizer.max_metric_calls})...",
            file=file,
        )
        return

    if optimizer.name == "LabeledFewShot":
        print(
            f"Compiling with LabeledFewShot on {dev_record_count} dev records "
            f"(max_labeled_demos={optimizer.max_labeled_demos})...",
            file=file,
        )
        return

    if optimizer.name == "BootstrapFewShotWithRandomSearch":
        print(
            f"Compiling with BootstrapFewShotWithRandomSearch on {dev_record_count} dev records "
            f"(metric={optimizer.metric_name}, "
            f"max_bootstrapped_demos={optimizer.max_bootstrapped_demos}, "
            f"max_labeled_demos={optimizer.max_labeled_demos}, "
            f"max_rounds={optimizer.max_rounds}, "
            f"num_candidate_programs={optimizer.num_candidate_programs})...",
            file=file,
        )
        return

    print(
        f"Compiling with BootstrapFewShot on {dev_record_count} dev records "
        f"(metric={optimizer.metric_name}, "
        f"max_bootstrapped_demos={optimizer.max_bootstrapped_demos}, "
        f"max_labeled_demos={optimizer.max_labeled_demos}, "
        f"max_rounds={optimizer.max_rounds})...",
        file=file,
    )


def write_compiled_state(module: dspy.Module, compiled_state_path: Path) -> None:
    dump_state = getattr(module, "dump_state", None)
    if not callable(dump_state):
        return
    state = dump_state()
    compiled_state_path.write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_optimizer_summary(optimizer: dict[str, Any], optimizer_dir: Path) -> None:
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


def runtime_report(
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


def collect_lm_token_usage(lms: list[dspy.LM]) -> dict[str, int] | None:
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


def gepa_reflection_config(base: LLMProviderConfig) -> LLMProviderConfig:
    """Use a hotter reflection LM only when the provider accepts temperature."""
    if base.temperature is None:
        return base
    return base.model_copy(update={"temperature": 1.0})


def capture_local_model_residency(
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

    residency = parse_ollama_ps_output(output, model_name)
    return residency or "unavailable"


def parse_ollama_ps_output(output: str, model_name: str) -> str | None:
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


def print_summary(
    report: dict[str, Any],
    metric_caveats: list[str],
    *,
    file: TextIO | None = None,
) -> None:
    counts = report.get("counts", {})
    bm = report.get("benchmark_metrics", {})
    diag = report.get("diagnostic_metrics", {})

    def pct(v: float | None) -> str:
        return f"{v:.1%}" if v is not None else "N/A"

    print("\n--- Counts ---", file=file)
    print(f"  Evaluated:  {counts.get('evaluated_records')}", file=file)
    if report.get("dataset") == "gan_2026":
        print(f"  Valid:      {counts.get('valid_predictions')}", file=file)
        print(f"  Invalid:    {counts.get('invalid_predictions')}", file=file)
    print(f"  Missing:    {counts.get('missing_predictions')}", file=file)

    if report.get("dataset") == "exect_v2":
        print("\n--- Field-family metrics (partial ExECT S0/S1) ---", file=file)
        print(f"  Micro precision: {pct(bm.get('micro_precision'))}", file=file)
        print(f"  Micro recall:    {pct(bm.get('micro_recall'))}", file=file)
        print(f"  Micro F1:        {pct(bm.get('micro_f1'))}", file=file)
        for family, f1 in bm.get("field_f1", {}).items():
            support = bm.get("field_support", {}).get(family)
            print(f"  {family} F1: {pct(f1)} (support={support})", file=file)
        print("\n--- Diagnostic metrics ---", file=file)
        print(
            "  Documents with gold quality flags: "
            f"{pct(diag.get('documents_with_gold_quality_flags'))}",
            file=file,
        )
        print(
            f"  Evidence quote support rate: {pct(diag.get('evidence_quote_support_rate'))}",
            file=file,
        )
        print(
            "  Evidence quote support rate (exact only): "
            f"{pct(diag.get('evidence_quote_support_rate_without_repairs'))}",
            file=file,
        )
        print(
            "  Evidence quote support rate (ellipsis repairs): "
            f"{pct(diag.get('evidence_quote_support_rate_repaired'))}",
            file=file,
        )
        print(
            f"  Evidence quote repair rate: {pct(diag.get('evidence_quote_repair_rate'))}",
            file=file,
        )
        print(
            f"  Evidence offsets present rate: {pct(diag.get('evidence_offsets_present_rate'))}",
            file=file,
        )
        print(
            f"  Evidence offsets valid rate:   {pct(diag.get('evidence_offsets_valid_rate'))}",
            file=file,
        )
    else:
        gan_header = (
            "Gan 2026 paper-reproduction metrics"
            if report.get("scorer") == "gan2026_paper_reproduction"
            else "Benchmark metrics (not published reproduction)"
        )
        print(f"\n--- {gan_header} ---", file=file)
        print(
            f"  Monthly frequency accuracy:  {pct(bm.get('monthly_frequency_accuracy'))}",
            file=file,
        )
        print(
            f"  Purist category accuracy:    {pct(bm.get('purist_category_accuracy'))}",
            file=file,
        )
        print(
            f"  Pragmatic category accuracy: {pct(bm.get('pragmatic_category_accuracy'))}",
            file=file,
        )

        print("\n--- Diagnostic metrics ---", file=file)
        print(
            f"  Schema validity rate:         {pct(diag.get('schema_valid_prediction_rate'))}",
            file=file,
        )
        print(
            f"  Normalized label accuracy:    {pct(diag.get('normalized_label_accuracy'))}",
            file=file,
        )
        print(
            f"  Evidence quote support rate:  {pct(diag.get('evidence_quote_support_rate'))}",
            file=file,
        )

    if metric_caveats:
        print("\n--- Caveats ---", file=file)
        for caveat in metric_caveats:
            print(f"  * {caveat}", file=file)


def run_experiment(
    experiment_path: Path,
    *,
    run_id: str | None = None,
    env_file: Path | None = None,
    dry_run: bool = False,
    stdout: TextIO | None = None,
    refresh_explorer: bool | None = None,
) -> int:
    """Run a clinical extraction experiment from a config file path."""
    out = stdout or sys.stdout

    def emit(message: str = "", *, flush: bool = False) -> None:
        print(message, file=out, flush=flush)

    if env_file is not None:
        load_env_file(env_file)

    config = load_experiment_config(experiment_path)
    backend = get_backend(config.dataset)
    emit(f"Experiment: {config.experiment_id}")
    emit(f"Dataset:    {config.dataset}")
    emit(f"Split:      {config.split_name}")
    emit(f"Model:      {config.model_config_path}")

    model_config = LLMProviderConfig.model_validate_json(
        config.model_config_path.read_text(encoding="utf-8")
    )

    # B2 check: Add Runtime Environment Checks Before Live Provider Runs
    if model_config.provider not in ("ollama", "mock"):
        api_key_env = model_config.api_key_env
        if api_key_env:
            if not os.environ.get(api_key_env):
                emit(f"Warning: required API key environment variable {api_key_env!r} is not set in the current process or env file.")
                if not dry_run:
                    raise ValueError(f"Required API key environment variable {api_key_env!r} is not set.")
        elif not model_config.api_key:
            emit("Warning: no api_key or api_key_env configured for hosted provider.")
            if not dry_run:
                raise ValueError("No api_key or api_key_env configured for hosted provider.")

    # B3 check: Keep Qwen Context And Timeout Pairing Explicit
    if model_config.provider == "ollama":
        num_ctx = (model_config.extra_body.get("options") or {}).get("num_ctx")
        if num_ctx is not None and num_ctx >= 131072:
            is_stress_test = any(
                "stress" in caveat.lower() or "latency" in caveat.lower()
                for caveat in config.metric_caveats
            ) or "stress" in config.experiment_id.lower() or "latency" in config.experiment_id.lower()
            
            if model_config.timeout_seconds < 1800 and not is_stress_test:
                emit(
                    f"Warning: high-context Ollama model run (num_ctx={num_ctx}) is paired with "
                    f"a timeout of {model_config.timeout_seconds}s (recommended >= 1800s). "
                    "Stress or latency tests must declare this in metric_caveats or experiment_id."
                )

    all_records = backend.load_records_by_id()
    records, missing_from_dataset = load_split_records(config, all_records)
    if missing_from_dataset:
        emit(
            f"Warning: {len(missing_from_dataset)} split IDs not in {config.dataset} records: "
            f"{missing_from_dataset[:5]}"
        )

    emit(f"Records:    {len(records)}{record_count_note(config)}")
    print_optimizer_plan(config.optimizer, file=out)

    if dry_run:
        emit("\nDry run — exiting before model calls.")
        return 0

    lm = build_dspy_lm(model_config)
    dspy.configure(lm=lm)
    reflection_lm = None
    if config.optimizer is not None and config.optimizer.name == "GEPA":
        reflection_config = gepa_reflection_config(model_config)
        reflection_lm = build_dspy_lm(reflection_config)

    resolved_run_id = run_id or make_run_id(config.experiment_id)
    metadata = backend.run_metadata(
        run_id=resolved_run_id,
        split_name=config.split_name,
        model_provider=model_config.provider,
        model_name=model_config.model,
        prompt_version=config.prompt_version,
        program_variant=config.program_variant,
        extra={
            "experiment_id": config.experiment_id,
            "structured_output_strategy": config.structured_output_strategy,
            "schema_level": config.schema_level,
        },
    )
    metadata = metadata.model_copy(
        update={
            "metric_caveats": config.metric_caveats,
            "scorer_mode": config.scorer_mode,
        }
    )
    paths = create_run_artifact_layout(metadata, root=config.output_root)
    emit(f"\nRun directory: {paths['run']}")

    paths["config"].write_text(
        json.dumps(config.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    module = backend.build_module(config, prompt_version=config.prompt_version)
    run_started = perf_counter()
    compile_duration_seconds: float | None = None

    if config.optimizer is not None:
        unsupported = backend.optimizer_unsupported_message(config.optimizer)
        if unsupported is not None:
            raise SystemExit(unsupported)

        split_data = json.loads(config.split_file.read_text(encoding="utf-8"))
        train_ids: list[str] = split_data.get("train") or split_data.get("development", [])
        if config.optimizer.trainset_size is not None:
            train_ids = train_ids[: config.optimizer.trainset_size]
        train_records = [all_records[rid] for rid in train_ids if rid in all_records]
        print_compile_message(config.optimizer, len(train_records), file=out)
        compile_started = perf_counter()
        module = backend.compile_module(
            config=config,
            module=module,
            train_records=train_records,
            artifact_paths=paths,
            reflection_lm=reflection_lm,
        )
        compile_duration_seconds = perf_counter() - compile_started
        emit("Compilation complete.")

    prompts_data = backend.prompts_data(config)
    if config.optimizer is not None:
        prompts_data["optimizer"] = config.optimizer.model_dump()
        write_compiled_state(module, paths["compiled_state"])
        write_optimizer_summary(config.optimizer.model_dump(), paths["optimizer_artifacts"])
    paths["prompts"].write_text(
        json.dumps(prompts_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    emit(f"Running {len(records)} predictions...")
    prediction_started = perf_counter()
    prediction_set = backend.predict_records(
        module=module,
        records=records,
        model_provider=model_config.provider,
        model_name=model_config.model,
        prompt_version=config.prompt_version,
        program_variant=config.program_variant,
        repair_policy=config.controls.repair_policy,
        progress_callback=lambda index, total, record_id: print_prediction_progress(
            index, total, record_id, file=out
        ),
        schema_level=config.schema_level,
        scorer_mode=config.scorer_mode,
    )
    prediction_duration_seconds = perf_counter() - prediction_started
    paths["predictions"].write_text(
        json.dumps(prediction_set.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    emit("Evaluating...")
    evaluation_started = perf_counter()
    report = backend.evaluate_predictions(
        prediction_set,
        scorer_mode=config.scorer_mode,
    )
    evaluation_duration_seconds = perf_counter() - evaluation_started
    token_usage = collect_lm_token_usage(
        [candidate for candidate in [lm, reflection_lm] if candidate is not None]
    )
    model_residency = capture_local_model_residency(
        model_config.provider,
        model_config.model,
    )
    report["runtime"] = runtime_report(
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

    print_summary(report, config.metric_caveats, file=out)

    should_refresh = refresh_explorer
    if should_refresh is None:
        should_refresh = getattr(config, "refresh_explorer", False)

    if should_refresh:
        # Auto-refresh model catalog in exect-explorer if directories exist
        try:
            root_dir = Path(__file__).resolve().parents[3]
            exect_explorer_dir = root_dir / "exect-explorer"
            if exect_explorer_dir.exists():
                import subprocess
                dataset_type = report.get("dataset")
                if dataset_type == "exect_v2":
                    script_path = exect_explorer_dir / "scripts" / "build_model_catalog.py"
                    if script_path.exists():
                        emit("\nAuto-refreshing ExECT Model Catalog in exect-explorer...")
                        subprocess.run([sys.executable, str(script_path)], check=False, capture_output=True)
                elif dataset_type == "gan_2026":
                    script_path = exect_explorer_dir / "scripts" / "build_model_catalog_gan.py"
                    if script_path.exists():
                        emit("\nAuto-refreshing Gan Model Catalog in exect-explorer...")
                        subprocess.run([sys.executable, str(script_path)], check=False, capture_output=True)
        except Exception as ex:
            emit(f"\nWarning: failed to auto-refresh model catalog: {ex}")

    return 0

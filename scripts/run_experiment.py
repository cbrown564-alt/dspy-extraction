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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import dspy

from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.exect import score_exect_prediction_set
from clinical_extraction.evaluation.cli import evaluate_gan_predictions
from clinical_extraction.experiments.config import load_experiment_config
from clinical_extraction.llms import LLMProviderConfig, build_dspy_lm
from clinical_extraction.programs.exect_s0_s1 import (
    EXECT_S0_S1_FIELD_FAMILIES,
    EXECT_S0_S1_LABEL_POLICY_GUIDANCE,
    EXECT_S0_S1_POLICY_EXAMPLES,
    EXECT_S0_S1_PROMPT_VERSION,
    EXECT_S0_S1_SECTION_AWARE_VARIANT,
    EXECT_S0_S1_VARIANT,
    ExectS0S1FieldFamilyModule,
    ExectS0S1SectionAwareFieldFamilyModule,
    exect_s0_s1_run_metadata,
    predict_exect_records,
)
from clinical_extraction.programs.gan_frequency_s0 import (
    GAN_FREQUENCY_SYNTHESIS_GUIDANCE,
    GanFrequencyS0Module,
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

    print(
        f"Records:    {len(records)}"
        + (f" (capped at max_records={config.max_records})" if config.max_records else "")
    )

    if args.dry_run:
        print("\nDry run — exiting before model calls.")
        return 0

    model_config = LLMProviderConfig.model_validate_json(
        config.model_config_path.read_text(encoding="utf-8")
    )
    lm = build_dspy_lm(model_config)
    dspy.configure(lm=lm)

    module = _build_module(config.dataset, config.program_variant)

    if config.optimizer is not None:
        if config.dataset != "gan_2026":
            raise SystemExit("Only Gan S0 experiments currently support DSPy optimization.")
        dev_ids: list[str] = split_data.get("development", [])
        if config.optimizer.trainset_size is not None:
            dev_ids = dev_ids[: config.optimizer.trainset_size]
        dev_records = [all_records[rid] for rid in dev_ids if rid in all_records]
        print(
            f"Compiling with BootstrapFewShot on {len(dev_records)} dev records "
            f"(metric={config.optimizer.metric_name}, "
            f"max_bootstrapped_demos={config.optimizer.max_bootstrapped_demos}, "
            f"max_labeled_demos={config.optimizer.max_labeled_demos}, "
            f"max_rounds={config.optimizer.max_rounds})..."
        )
        module = compile_gan_s0_module(
            dev_records,
            max_bootstrapped_demos=config.optimizer.max_bootstrapped_demos,
            max_labeled_demos=config.optimizer.max_labeled_demos,
            max_rounds=config.optimizer.max_rounds,
            optimizer_metric=config.optimizer.metric_name,
        )
        print("Compilation complete.")

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
    prompts_data = _prompts_data(
        config.dataset,
        config.program_variant,
        config.prompt_version,
        config.structured_output_strategy,
    )
    if config.optimizer is not None:
        prompts_data["optimizer"] = config.optimizer.model_dump()
        _write_compiled_state(module, paths["artifacts"])
    paths["prompts"].write_text(
        json.dumps(prompts_data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"Running {len(records)} predictions...")
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
    paths["predictions"].write_text(
        json.dumps(prediction_set.model_dump(mode="json"), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Evaluating...")
    report = _evaluate_predictions(prediction_set)
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
        return GanFrequencyS0Module()
    if dataset == "exect_v2":
        if program_variant == EXECT_S0_S1_SECTION_AWARE_VARIANT:
            return ExectS0S1SectionAwareFieldFamilyModule()
        return ExectS0S1FieldFamilyModule()
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
        return {
            "signature": "GanFrequencyS0Signature",
            "module": "GanFrequencyS0Module",
            "prompt_version": prompt_version,
            "synthesis_guidance": GAN_FREQUENCY_SYNTHESIS_GUIDANCE,
            "structured_output_strategy": structured_output_strategy,
        }
    if dataset == "exect_v2":
        return {
            "signature": (
                "ExectS0S1FieldFamilySignature"
                if program_variant == EXECT_S0_S1_VARIANT
                else "ExectS0S1DiagnosisSignature + "
                "ExectS0S1SeizureTypeSignature + ExectS0S1MedicationSignature"
            ),
            "module": (
                "ExectS0S1FieldFamilyModule"
                if program_variant == EXECT_S0_S1_VARIANT
                else "ExectS0S1SectionAwareFieldFamilyModule"
            ),
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


def _write_compiled_state(module: GanFrequencyS0Module, artifact_dir: Path) -> None:
    dump_state = getattr(module, "dump_state", None)
    if not callable(dump_state):
        return
    state = dump_state()
    (artifact_dir / "compiled_state.json").write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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

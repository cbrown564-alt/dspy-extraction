"""G5 paper-reproduction rescore pack for promoted Gan S0 baselines."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

from clinical_extraction.evaluation.cli import evaluate_gan_predictions
from clinical_extraction.gan.scoring import (
    GAN_CANONICAL_SCORER,
    GAN_PAPER_REPRODUCTION_SCORER,
)
from clinical_extraction.paths import resolve_run_directory
from clinical_extraction.schemas import PredictionSet

DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/gan/gan_s0_g5_paper_scorer_rescore_pack_20260528.md"
)


@dataclass(frozen=True)
class GanPaperRescoreBaseline:
    baseline_id: str
    label: str
    role: str
    run_dir: Path


DEFAULT_BASELINE_SPECS = (
    GanPaperRescoreBaseline(
        baseline_id="builder_gap_v1_gpt",
        label="Builder-gap v1 GPT",
        role="promoted synthetic operational default",
        run_dir=Path(
            "gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z"
        ),
    ),
    GanPaperRescoreBaseline(
        baseline_id="builder_gap_v1_qwen",
        label="Builder-gap v1 Qwen",
        role="accepted local-transfer baseline",
        run_dir=Path(
            "gan_s0_candidate_builder_gap_v1_qwen35b_ollama_full_validation_20260523T215727Z"
        ),
    ),
    GanPaperRescoreBaseline(
        baseline_id="d1_v1_2b_schema_guard_gpt",
        label="D1 v1.2b schema guard GPT",
        role="mechanism baseline / operational D1 surface",
        run_dir=Path(
            "gan_s0_date_stage_d1_v1_2b_schema_guard_only_full_validation_gpt4_1_mini_20260528T074900Z"
        ),
    ),
)
DEFAULT_PAPER_SCORER_OPTIONS = {
    "apply_paper_prediction_repair": False,
    "allow_paper_prediction_range": False,
    "allow_paper_error_tolerance": False,
}
PRIMARY_METRIC_KEYS = (
    "monthly_frequency_accuracy",
    "purist_category_accuracy",
    "pragmatic_category_accuracy",
)


def build_gan_paper_rescore_pack_report(
    *,
    baseline_specs: Sequence[GanPaperRescoreBaseline] | None = None,
    paper_scorer_options: Mapping[str, bool] | None = None,
    bootstrap_samples: int = 1000,
    bootstrap_seed: int = 0,
) -> dict[str, Any]:
    """Rescore stored Gan S0 predictions under paper and canonical scorers."""

    baselines = list(baseline_specs or DEFAULT_BASELINE_SPECS)
    if not baselines:
        raise ValueError("At least one baseline run is required.")

    paper_options = dict(DEFAULT_PAPER_SCORER_OPTIONS)
    if paper_scorer_options:
        paper_options.update(paper_scorer_options)

    rows = [
        _baseline_rescore_row(
            spec,
            paper_scorer_options=paper_options,
            bootstrap_samples=bootstrap_samples,
            bootstrap_seed=bootstrap_seed,
        )
        for spec in baselines
    ]
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "kanban_card": "G5 - Gan Paper-Scorer Rescore Pack",
        "dataset": "gan_2026",
        "schema_level": "gan_frequency_s0",
        "split_name": _first_value(rows, "split_name"),
        "gold_source": "check__Seizure Frequency Number.seizure_frequency_number[0]",
        "reference_policy": (
            "reference[0] is a secondary cross-check and difficulty signal, not gold."
        ),
        "scope": (
            "Post-hoc rescore of stored synthetic-validation predictions; no model "
            "calls were made."
        ),
        "paper_scorer_options": paper_options,
        "scorer_views": {
            "paper_reproduction": {
                "scorer": GAN_PAPER_REPRODUCTION_SCORER,
                "claim_scope": (
                    "Benchmark-facing Gan 2026 compatibility scorer for synthetic-only "
                    "paper-table sensitivity."
                ),
            },
            "canonical": {
                "scorer": GAN_CANONICAL_SCORER,
                "claim_scope": (
                    "Audited project diagnostic scorer that keeps unknown and no "
                    "seizure frequency reference distinct."
                ),
            },
        },
        "summary": {
            "baselines": [_summary_row(row) for row in rows],
            "best_by_metric": _best_by_metric(rows),
        },
        "baselines": rows,
        "caveats": [
            "Synthetic validation only: this is not Real(300), Real(150), or a published Gan benchmark reproduction.",
            "Paper-reproduction metrics are the benchmark-facing view for direct Gan scorer compatibility; canonical metrics remain diagnostic sensitivity analyses.",
            "The primary paper-reproduction rows report the repair, range, and tolerance options explicitly.",
            "Stored prediction artifacts were rescored as-is; no scorer, loader, split, bridge, prompt, or prediction artifact was tuned.",
        ],
    }


def write_report_artifacts(
    report: dict[str, Any],
    *,
    json_output: Path = DEFAULT_JSON_OUTPUT,
    markdown_output: Path = DEFAULT_MARKDOWN_OUTPUT,
) -> None:
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_output.write_text(render_gan_paper_rescore_markdown(report), encoding="utf-8")


def render_gan_paper_rescore_markdown(report: dict[str, Any]) -> str:
    options = report["paper_scorer_options"]
    lines = [
        "# Gan S0 G5 Paper-Scorer Rescore Pack",
        "",
        f"Generated: `{report['generated_at']}`",
        "",
        "## Scope",
        "",
        f"- Dataset: `{report['dataset']}`",
        f"- Split: `{report['split_name']}`",
        f"- Schema level: `{report['schema_level']}`",
        f"- Gold source: `{report['gold_source']}`",
        f"- Reference policy: {report['reference_policy']}",
        f"- Run mode: {report['scope']}",
        "",
        "## Paper Scorer Options",
        "",
        "| Option | Enabled |",
        "| --- | ---: |",
        f"| `apply_paper_prediction_repair` | `{options['apply_paper_prediction_repair']}` |",
        f"| `allow_paper_prediction_range` | `{options['allow_paper_prediction_range']}` |",
        f"| `allow_paper_error_tolerance` | `{options['allow_paper_error_tolerance']}` |",
        "",
        "## Rescore Summary",
        "",
        "| Baseline | Run ID | Model | Paper monthly | Paper purist | Paper pragmatic | Canonical monthly | Canonical purist | Canonical pragmatic | Paper-canonical monthly | Valid paper/canonical |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["summary"]["baselines"]:
        paper = row["paper_reproduction"]["benchmark_metrics"]
        canonical = row["canonical"]["benchmark_metrics"]
        lines.append(
            "| "
            f"{row['label']} | "
            f"`{row['run_id']}` | "
            f"{row['model']} | "
            f"{_pct(paper['monthly_frequency_accuracy'])} | "
            f"{_pct(paper['purist_category_accuracy'])} | "
            f"{_pct(paper['pragmatic_category_accuracy'])} | "
            f"{_pct(canonical['monthly_frequency_accuracy'])} | "
            f"{_pct(canonical['purist_category_accuracy'])} | "
            f"{_pct(canonical['pragmatic_category_accuracy'])} | "
            f"{_delta_pp(row['paper_minus_canonical']['monthly_frequency_accuracy'])} | "
            f"{row['paper_reproduction']['counts']['valid_predictions']}/"
            f"{row['canonical']['counts']['valid_predictions']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- G5 is now available as a synthetic-validation rescore pack for paper-facing Gan S0 tables.",
            "- Builder-gap v1 GPT remains the strongest promoted synthetic operational baseline in the paper-reproduction view.",
            "- D1 v1.2b remains the cleaner mechanism baseline: it is close to builder-gap GPT while exposing the date/event candidate payload.",
            "- The paper-reproduction scorer can change both metric values and denominator behavior for malformed predictions; canonical rows are retained as diagnostic sensitivity views.",
            "",
            "## Caveats",
            "",
        ]
    )
    lines.extend(f"- {caveat}" for caveat in report["caveats"])
    lines.extend(
        [
            "",
            "## Source Artifacts",
            "",
            "| Baseline | Role | Run directory | Config |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in report["summary"]["baselines"]:
        lines.append(
            "| "
            f"{row['label']} | "
            f"{row['role']} | "
            f"`{row['run_dir']}` | "
            f"`{row['config_path']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def _baseline_rescore_row(
    spec: GanPaperRescoreBaseline,
    *,
    paper_scorer_options: Mapping[str, bool],
    bootstrap_samples: int,
    bootstrap_seed: int,
) -> dict[str, Any]:
    run_dir = resolve_run_directory(spec.run_dir, include_archive=True)
    prediction_set = PredictionSet.model_validate_json(
        (run_dir / "predictions.json").read_text(encoding="utf-8")
    )
    metadata = _load_json(run_dir / "metadata.json")
    config = _load_json(run_dir / "config.json")
    prior_metrics = _load_json(run_dir / "metrics.json")
    paper_report = evaluate_gan_predictions(
        prediction_set,
        bootstrap_samples=bootstrap_samples,
        bootstrap_seed=bootstrap_seed,
        scorer_mode=GAN_PAPER_REPRODUCTION_SCORER,
        apply_paper_prediction_repair=paper_scorer_options[
            "apply_paper_prediction_repair"
        ],
        allow_paper_prediction_range=paper_scorer_options[
            "allow_paper_prediction_range"
        ],
        allow_paper_error_tolerance=paper_scorer_options[
            "allow_paper_error_tolerance"
        ],
    )
    canonical_report = evaluate_gan_predictions(
        prediction_set,
        bootstrap_samples=bootstrap_samples,
        bootstrap_seed=bootstrap_seed,
        scorer_mode=GAN_CANONICAL_SCORER,
    )
    return {
        "baseline_id": spec.baseline_id,
        "label": spec.label,
        "role": spec.role,
        "run_id": metadata.get("run_id", run_dir.name),
        "run_dir": str(run_dir),
        "config_path": str(run_dir / "config.json"),
        "experiment_id": config.get("experiment_id"),
        "dataset": prediction_set.dataset,
        "schema_level": prediction_set.schema_level,
        "split_name": metadata.get("split_name") or config.get("split_name"),
        "model_provider": metadata.get("model_provider"),
        "model_name": metadata.get("model_name"),
        "program_variant": metadata.get("program_variant")
        or config.get("program_variant"),
        "prompt_version": metadata.get("metadata", {}).get("prompt_version")
        or metadata.get("prompt_version")
        or config.get("prompt_version"),
        "model_config_path": config.get("model_config_path"),
        "prior_scorer_mode": metadata.get("scorer_mode") or config.get("scorer_mode"),
        "prior_canonical_metrics": {
            "benchmark_metrics": prior_metrics.get("benchmark_metrics", {}),
            "diagnostic_metrics": prior_metrics.get("diagnostic_metrics", {}),
            "counts": prior_metrics.get("counts", {}),
        },
        "score_views": {
            "paper_reproduction": _compact_evaluation_report(paper_report),
            "canonical": _compact_evaluation_report(canonical_report),
        },
        "paper_minus_canonical": _metric_delta(
            paper_report["benchmark_metrics"],
            canonical_report["benchmark_metrics"],
        ),
    }


def _compact_evaluation_report(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "scorer": report["scorer"],
        "scorer_options": report["scorer_options"],
        "counts": report["counts"],
        "benchmark_metrics": report["benchmark_metrics"],
        "diagnostic_metrics": report["diagnostic_metrics"],
        "confidence_intervals": {
            key: report["confidence_intervals"].get(key)
            for key in (
                "monthly_frequency_accuracy",
                "purist_category_accuracy",
                "pragmatic_category_accuracy",
                "schema_valid_prediction_rate",
            )
        },
        "error_analysis_counts": report["error_analysis"]["counts"],
    }


def _summary_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "baseline_id": row["baseline_id"],
        "label": row["label"],
        "role": row["role"],
        "run_id": row["run_id"],
        "run_dir": row["run_dir"],
        "config_path": row["config_path"],
        "experiment_id": row["experiment_id"],
        "model": _model_label(row),
        "program_variant": row["program_variant"],
        "prompt_version": row["prompt_version"],
        "paper_reproduction": row["score_views"]["paper_reproduction"],
        "canonical": row["score_views"]["canonical"],
        "paper_minus_canonical": row["paper_minus_canonical"],
    }


def _metric_delta(
    paper_metrics: Mapping[str, float | None],
    canonical_metrics: Mapping[str, float | None],
) -> dict[str, float | None]:
    delta: dict[str, float | None] = {}
    for key in PRIMARY_METRIC_KEYS:
        paper_value = paper_metrics.get(key)
        canonical_value = canonical_metrics.get(key)
        if paper_value is None or canonical_value is None:
            delta[key] = None
        else:
            delta[key] = paper_value - canonical_value
    return delta


def _best_by_metric(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, dict[str, Any]] = {}
    for view_key in ("paper_reproduction", "canonical"):
        result[view_key] = {}
        for metric_key in PRIMARY_METRIC_KEYS:
            scores = {
                row["baseline_id"]: row["score_views"][view_key]["benchmark_metrics"][
                    metric_key
                ]
                for row in rows
            }
            best = max(value for value in scores.values() if value is not None)
            result[view_key][metric_key] = {
                "accuracy": best,
                "baseline_ids": [
                    baseline_id
                    for baseline_id, value in scores.items()
                    if value == best
                ],
            }
    return result


def _first_value(rows: Sequence[dict[str, Any]], key: str) -> Any:
    for row in rows:
        if row.get(key) is not None:
            return row[key]
    return None


def _model_label(row: Mapping[str, Any]) -> str:
    provider = row.get("model_provider") or "unknown"
    name = row.get("model_name") or "unknown"
    return f"{name} / {provider}"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def _delta_pp(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:+.1f}pp"

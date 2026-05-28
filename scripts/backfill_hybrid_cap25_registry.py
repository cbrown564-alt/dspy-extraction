"""Append hybrid-grid cap-25 rows to docs/experiments/synthesis/experiment_registry.json.

Reads historical row specs from the retained provenance manifest, then reads the
latest run under runs/ per experiment_id and builds minimal registry rows.
Skips experiment_ids already present.

Usage:
    uv run python scripts/backfill_hybrid_cap25_registry.py
    uv run python scripts/backfill_hybrid_cap25_registry.py --dry-run
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG_PATH = ROOT / "docs" / "experiments" / "synthesis" / "experiment_registry.json"
RUNS = ROOT / "runs"

MANIFEST_PATH = (
    ROOT
    / "docs"
    / "archive"
    / "experiments"
    / "synthesis"
    / "pre_component_pivot"
    / "hybrid_cap25_registry_backfill_manifest_20260528.json"
)


def load_backfill_specs(manifest_path: Path = MANIFEST_PATH) -> list[dict]:
    """Load historical cap-slice registry specs from retained provenance."""

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError(f"{manifest_path} must contain a rows list.")
    return [dict(row) for row in rows]


def _latest_run_dir(experiment_id: str) -> Path | None:
    matches = sorted(RUNS.glob(f"{experiment_id}_*"), reverse=True)
    return matches[0] if matches else None


def _gan_headline_from_metrics(metrics_path: Path) -> dict | None:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    bench = metrics.get("benchmark_metrics") or {}
    monthly = bench.get("monthly_frequency_accuracy")
    if monthly is None:
        return None
    diag = metrics.get("diagnostic_metrics") or {}
    return {
        "name": "monthly_frequency_accuracy",
        "value": monthly,
        "secondary": {
            "purist_category_accuracy": bench.get("purist_category_accuracy"),
            "pragmatic_category_accuracy": bench.get("pragmatic_category_accuracy"),
            "evidence_quote_support_rate": diag.get("evidence_quote_support_rate"),
            "schema_valid_prediction_rate": diag.get("schema_valid_prediction_rate"),
        },
    }


def _exect_headline_from_metrics(
    metrics_path: Path,
    *,
    primary_field: str | None = None,
) -> dict | None:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    bench = metrics.get("benchmark_metrics") or {}
    diag = metrics.get("diagnostic_metrics") or {}
    field_f1 = bench.get("field_f1") or {}
    if primary_field:
        value = field_f1.get(primary_field)
        if value is None:
            return None
        return {
            "name": f"{primary_field}_f1",
            "value": value,
            "secondary": {
                "micro_f1": bench.get("micro_f1"),
                "evidence_quote_support_rate": diag.get("evidence_quote_support_rate"),
            },
        }
    micro_f1 = bench.get("micro_f1")
    if micro_f1 is None:
        return None
    return {
        "name": "micro_f1",
        "value": micro_f1,
        "secondary": {
            "diagnosis_f1": field_f1.get("diagnosis"),
            "seizure_type_f1": field_f1.get("seizure_type"),
            "annotated_medication_f1": field_f1.get("annotated_medication"),
            "evidence_quote_support_rate": diag.get("evidence_quote_support_rate"),
        },
    }


def _build_gan_row(spec: dict) -> dict | None:
    run_dir = _latest_run_dir(spec["experiment_id"])
    if run_dir is None:
        return None
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return None
    headline = _gan_headline_from_metrics(metrics_path)
    config_path = ROOT / "configs" / "experiments" / f"{spec['experiment_id']}.json"
    return {
        "experiment_id": spec["experiment_id"],
        "dataset": "gan_2026",
        "schema_complexity": "gan_s0",
        "clinical_task_family": ["frequency"],
        "model_track": "gpt4_1_mini",
        "program_architecture": spec["program_architecture"],
        "hybrid_balance_class": spec["hybrid_balance_class"],
        "deterministic_roles": [
            "benchmark_label_policy",
            "frequency_normalization",
            "json_schema_constraint",
            "pydantic_validation",
            "temporal_candidate_generation",
        ],
        "llm_roles": [
            "evidence_quote_generation",
            "frequency_interpretation",
        ],
        "interleaving_positions": spec["interleaving_positions"],
        "knowledge_sources": [
            "benchmark_label_policy",
            "json_schema",
            "pydantic_validation",
            "temporal_rules",
        ],
        "control_modes": ["hard_constraint", "soft_hint"],
        "context_strategy": "full_note_plus_deterministic_temporal_candidates",
        "evidence_strategy": "model_quote_required",
        "normalization_strategy": "benchmark_policy_prompt",
        "verification_strategy": spec.get(
            "verification_strategy",
            "none"
            if spec["program_architecture"] == "temporal_candidates_single_pass"
            else "llm_verify_repair",
        ),
        "schema_integrity_strategy": ["json_schema", "pydantic_validation"],
        "example_strategy": "zero_shot_or_prompt_only",
        "comparison_group": spec["comparison_group"],
        "fixed_controls": {
            "schema_level": "gan_frequency_s0",
            "scorer": "gan_frequency_deterministic_v1",
            "model_config_path": "configs/models/gan_s0_gpt4_1_mini.json",
            "split": "gan_2026_fixed_v1:validation",
        },
        "varied_factor": spec["varied_factor"],
        "run_scope": spec.get(
            "run_scope",
            "cap50" if "cap50" in spec["experiment_id"] else "slice",
        ),
        "canonical_run_id": run_dir.name,
        "outcome": spec["outcome"],
        "decision_doc": spec["decision_doc"],
        "metric_caveats": [
            "Cap-25 search grid under hybrid pipeline pivot; not mechanism closure.",
            f"stage_graph_id={spec.get('stage_graph_id')}; "
            f"stage_executor={spec.get('stage_executor', 'n/a')}; "
            f"implementation_variant={spec.get('implementation_variant', 'n/a')}; "
            f"validation_ladder_rung={spec.get('validation_ladder_rung', 'n/a')}.",
        ],
        "artifact_paths": [f"runs/{run_dir.name}"],
        "headline_metric": headline,
        "prompt_versions": (
            json.loads(config_path.read_text(encoding="utf-8")).get("prompt_version")
            if config_path.exists()
            else "gan_frequency_s0_temporal_candidates_single_pass_v1_1"
        ),
        "config_paths": str(config_path.relative_to(ROOT)).replace("\\", "/"),
        "notes": spec["notes"],
        "comparison_groups": [spec["comparison_group"]],
    }


def _build_exect_row(spec: dict) -> dict | None:
    run_dir = _latest_run_dir(spec["experiment_id"])
    if run_dir is None:
        return None
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return None
    headline = _exect_headline_from_metrics(
        metrics_path,
        primary_field=spec.get("headline_metric_field"),
    )
    config_path = ROOT / "configs" / "experiments" / f"{spec['experiment_id']}.json"
    schema_complexity = spec.get("schema_complexity", "exect_s1")
    schema_level = spec.get("schema_level", "exect_s0_s1_field_family")
    scorer = spec.get("scorer", "exect_field_family_deterministic_v1")
    scope_label = (
        "ExECT S4 field-family diagnostics"
        if schema_complexity == "exect_s4"
        else "partial ExECT S0/S1 diagnostics"
    )
    llm_roles = [
        "benchmark_policy_application",
        "clinical_field_extraction",
        "evidence_quote_generation",
    ]
    if spec["verification_strategy"] == "verify_repair":
        llm_roles.extend(["repair", "verification"])
    deterministic_roles = [
        "benchmark_label_policy",
        "field_family_scoring",
        "json_schema_constraint",
        "pydantic_validation",
    ]
    if spec["hybrid_balance_class"] == ["H2_pre_deterministic"]:
        deterministic_roles.append("controlled_vocabulary_filter")
    if spec["hybrid_balance_class"] == ["H1_post_deterministic"]:
        deterministic_roles.append("benchmark_bridge")
    knowledge_sources = [
        "benchmark_label_policy",
        "gold_audit_policy",
        "json_schema",
        "pydantic_validation",
    ]
    if spec["context_strategy"] == "candidate_injected":
        knowledge_sources.insert(1, "controlled_vocabulary")
    control_modes = ["hard_constraint"]
    if spec["hybrid_balance_class"] == ["H1_post_deterministic"]:
        control_modes.append("posthoc_correction")
    if spec["hybrid_balance_class"] == ["H2_pre_deterministic"]:
        control_modes.append("soft_hint")
    return {
        "experiment_id": spec["experiment_id"],
        "dataset": "exect_v2",
        "schema_complexity": schema_complexity,
        "clinical_task_family": spec["clinical_task_family"],
        "model_track": "gpt4_1_mini",
        "program_architecture": spec["program_architecture"],
        "hybrid_balance_class": spec["hybrid_balance_class"],
        "deterministic_roles": deterministic_roles,
        "llm_roles": llm_roles,
        "interleaving_positions": spec["interleaving_positions"],
        "knowledge_sources": knowledge_sources,
        "control_modes": control_modes,
        "context_strategy": spec["context_strategy"],
        "evidence_strategy": "model_quote_with_diagnostic_span_check",
        "normalization_strategy": spec["normalization_strategy"],
        "verification_strategy": spec["verification_strategy"],
        "schema_integrity_strategy": ["json_schema", "pydantic_validation"],
        "example_strategy": "manual_few_shot_or_policy_examples",
        "comparison_group": spec["comparison_group"],
        "fixed_controls": {
            "schema_level": schema_level,
            "scorer": scorer,
            "model_config_path": "configs/models/gan_s0_gpt4_1_mini.json",
            "split": "exectv2_fixed_v1:validation",
        },
        "varied_factor": spec["varied_factor"],
        "run_scope": "cap25",
        "canonical_run_id": run_dir.name,
        "outcome": spec["outcome"],
        "decision_doc": spec["decision_doc"],
        "metric_caveats": [
            "Cap-25 search grid under hybrid pipeline pivot; not mechanism closure.",
            f"These are {scope_label}, not published ExECTv2 benchmark reproduction.",
            f"stage_graph_id={spec.get('stage_graph_id')}; "
            f"stage_executor={spec.get('stage_executor', 'n/a')}; "
            f"implementation_variant={spec.get('implementation_variant', 'n/a')}.",
        ],
        "artifact_paths": [f"runs/{run_dir.name}"],
        "headline_metric": headline,
        "prompt_versions": spec["prompt_versions"],
        "config_paths": str(config_path.relative_to(ROOT)).replace("\\", "/"),
        "notes": spec["notes"],
        "comparison_groups": [spec["comparison_group"]],
    }


def _build_row(spec: dict) -> dict | None:
    if spec["experiment_id"].startswith("exect_"):
        return _build_exect_row(spec)
    return _build_gan_row(spec)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(REG_PATH.read_text(encoding="utf-8"))
    existing = {row["experiment_id"] for row in data["experiments"]}
    added: list[str] = []
    missing_runs: list[str] = []

    for spec in load_backfill_specs():
        if spec["experiment_id"] in existing:
            continue
        row = _build_row(spec)
        if row is None:
            missing_runs.append(spec["experiment_id"])
            continue
        data["experiments"].append(row)
        added.append(spec["experiment_id"])

    data["row_count"] = len(data["experiments"])
    print(f"Added {len(added)} rows: {added}")
    if missing_runs:
        print(f"Skipped (no run): {missing_runs}")

    if args.dry_run:
        return
    REG_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()

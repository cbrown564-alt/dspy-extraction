"""Append Phase 2/3 hybrid-grid cap-25 rows to docs/experiment_registry.json.

Reads latest run under runs/ per experiment_id and builds minimal registry rows.
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
REG_PATH = ROOT / "docs" / "experiment_registry.json"
RUNS = ROOT / "runs"

GRID_ROWS: list[dict] = [
    {
        "experiment_id": "gan_s0_stage_graph_g1_direct_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g1_direct",
        "program_architecture": "direct_single_pass",
        "hybrid_balance_class": ["L1_llm_constrained"],
        "interleaving_positions": ["during"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A1; 44% monthly; reject vs A3 winner.",
    },
    {
        "experiment_id": "gan_s0_stage_graph_g2_extract_repair_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g2_extract_repair",
        "program_architecture": "verify_repair",
        "hybrid_balance_class": ["H1_post_deterministic"],
        "interleaving_positions": ["during", "post"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A2; 44% monthly; reject vs A3.",
    },
    {
        "experiment_id": "gan_s0_stage_graph_g2_candidates_adjudicate_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g2_candidates_adjudicate",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A3 winner; 52% monthly; anchor for Axis 2/3.",
    },
    {
        "experiment_id": "gan_s0_stage_graph_g3_extract_verify_repair_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g3_extract_verify_repair",
        "program_architecture": "verify_repair",
        "hybrid_balance_class": ["H1_post_deterministic"],
        "interleaving_positions": ["during", "post"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A4; 44% monthly; label-duplicate of A2.",
    },
    {
        "experiment_id": "gan_s0_stage_graph_g3_candidates_extract_repair_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_pipeline_stage_graph_gpt_cap25_v1",
        "varied_factor": "pipeline_stage_graph",
        "stage_graph_id": "g3_candidates_extract_repair",
        "program_architecture": "temporal_candidates_verify_repair",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_pipeline_stage_graph_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 1 cap-25 A5; 44% monthly; promoted skeleton did not win Axis 1 search.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e1_det_candidates_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate",
        "program_architecture": "temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E1; 52% monthly; det-candidate anchor confirmed.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e2_llm_candidates_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "llm_candidates_llm_adjudicate",
        "program_architecture": "llm_temporal_candidates_single_pass",
        "hybrid_balance_class": ["H2_pre_deterministic", "H4_deterministic_first_llm_adjudicates"],
        "interleaving_positions": ["pre", "during"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E2; 29.2% monthly; LLM JSON candidate path reject.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e3_hybrid_candidates_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "hybrid_candidates_llm_adjudicate",
        "program_architecture": "hybrid_temporal_candidates_single_pass",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E3; 41.7% monthly; hybrid merge reject vs det.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e4_det_vr_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "det_candidates_llm_adjudicate_llm_vr",
        "program_architecture": "temporal_candidates_adjudicate_verify_repair",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "outcome": "hold",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E4 diagnostic; 52% monthly; VR neutral after adjudicate.",
    },
    {
        "experiment_id": "gan_s0_stage_executor_e5_llm_vr_cap25_gpt4_1_mini",
        "comparison_group": "gan_s0_stage_executor_gpt_cap25_v1",
        "varied_factor": "stage_executor",
        "stage_graph_id": "g2_candidates_adjudicate",
        "stage_executor": "llm_candidates_llm_adjudicate_llm_vr",
        "program_architecture": "llm_temporal_candidates_verify_repair",
        "hybrid_balance_class": [
            "H2_pre_deterministic",
            "H4_deterministic_first_llm_adjudicates",
        ],
        "interleaving_positions": ["pre", "during", "post"],
        "outcome": "reject",
        "decision_doc": "docs/gan_s0_stage_executor_gpt_cap25_v1_inspection_20260521.md",
        "notes": "decision_scope: arm. Axis 2 E5 diagnostic; 29.2% monthly; VR cannot rescue LLM candidates.",
    },
]


def _latest_run_dir(experiment_id: str) -> Path | None:
    matches = sorted(RUNS.glob(f"{experiment_id}_*"), reverse=True)
    return matches[0] if matches else None


def _headline_from_metrics(metrics_path: Path) -> dict | None:
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


def _build_row(spec: dict) -> dict | None:
    run_dir = _latest_run_dir(spec["experiment_id"])
    if run_dir is None:
        return None
    metrics_path = run_dir / "metrics.json"
    if not metrics_path.exists():
        return None
    headline = _headline_from_metrics(metrics_path)
    config_path = (
        ROOT / "configs" / "experiments" / f"{spec['experiment_id']}.json"
    )
    row = {
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
        "verification_strategy": "none"
        if spec["program_architecture"] == "temporal_candidates_single_pass"
        else "llm_verify_repair",
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
        "run_scope": "slice",
        "canonical_run_id": run_dir.name,
        "outcome": spec["outcome"],
        "decision_doc": spec["decision_doc"],
        "metric_caveats": [
            "Cap-25 search grid under hybrid pipeline pivot; not mechanism closure.",
            f"stage_graph_id={spec.get('stage_graph_id')}; "
            f"stage_executor={spec.get('stage_executor', 'n/a')}.",
        ],
        "artifact_paths": [f"runs/{run_dir.name}"],
        "headline_metric": headline,
        "prompt_versions": "gan_frequency_s0_temporal_candidates_single_pass_v1_1",
        "config_paths": str(config_path.relative_to(ROOT)).replace("\\", "/"),
        "notes": spec["notes"],
        "comparison_groups": [spec["comparison_group"]],
    }
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    data = json.loads(REG_PATH.read_text(encoding="utf-8"))
    existing = {row["experiment_id"] for row in data["experiments"]}
    added: list[str] = []
    missing_runs: list[str] = []

    for spec in GRID_ROWS:
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

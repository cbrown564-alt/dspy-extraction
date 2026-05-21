from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Literal

from clinical_extraction.experiments.config import ExperimentConfig, load_experiment_config
from clinical_extraction.experiments.taxonomy import (
    REGISTRY_PATH,
    load_experiment_registry,
)

IssueLevel = Literal["error", "warning"]

DECISION_OUTCOMES_REQUIRING_DOC = frozenset(
    {"promote", "freeze", "reject", "superseded"}
)
PLACEHOLDER_DECISION_DOC = "pending_backfill"
PENDING_BACKFILL = "pending_backfill"

ARRAY_CONTROLLED_FIELDS = frozenset(
    {
        "hybrid_balance_class",
        "deterministic_roles",
        "llm_roles",
        "interleaving_positions",
        "knowledge_sources",
        "control_modes",
        "schema_integrity_strategy",
        "clinical_task_family",
    }
)

SINGLE_CONTROLLED_FIELDS: dict[str, frozenset[str]] = {
    "dataset": frozenset({"gan_2026", "exect_v2", PENDING_BACKFILL}),
    "schema_complexity": frozenset(
        {
            "gan_s0",
            "exect_s1",
            "exect_s2",
            "exect_s3",
            "exect_s4",
            PENDING_BACKFILL,
        }
    ),
    "model_track": frozenset(
        {
            "gpt4_1_mini",
            "gpt5_5",
            "gemini",
            "qwen35b",
            "qwen9b",
            "unknown",
            PENDING_BACKFILL,
        }
    ),
    "program_architecture": frozenset(
        {
            "single_pass",
            "direct_single_pass",
            "verify_repair",
            "temporal_candidates_verify_repair",
            "temporal_candidates_single_pass",
            "llm_temporal_candidates_single_pass",
            "hybrid_temporal_candidates_single_pass",
            "temporal_candidates_adjudicate_verify_repair",
            "temporal_candidates_adjudicate_det_guards",
            "temporal_candidates_adjudicate_det_evidence",
            "temporal_candidates_adjudicate_confirm_only",
            "temporal_candidates_adjudicate_verify_repair_no_guards",
            "temporal_candidates_adjudicate_verify_repair_span_check",
            "llm_temporal_candidates_verify_repair",
            "temporal_event_table_verify_repair",
            "react_temporal_tools",
            "section_aware",
            "diagnosis_recall",
            "optimizer_compiled_single_pass",
            PENDING_BACKFILL,
        }
    ),
    "context_strategy": frozenset(
        {
            "full_note",
            "full_note_plus_deterministic_temporal_candidates",
            "section_filtered",
            "candidate_injected",
            "retrieved_spans",
            "regression_slice",
            PENDING_BACKFILL,
        }
    ),
    "evidence_strategy": frozenset(
        {
            "absent",
            "model_quote",
            "model_quote_required",
            "model_quote_with_diagnostic_span_check",
            "injected_candidates",
            "verified_quote",
            "deterministic_span_check",
            "verified_quote_with_deterministic_span_check",
            PENDING_BACKFILL,
        }
    ),
    "normalization_strategy": frozenset(
        {
            "model_only",
            "list_constrained",
            "tool_mediated",
            "deterministic_mapping",
            "benchmark_bridge",
            "benchmark_policy_prompt",
            "scorer_only",
            "none",
            PENDING_BACKFILL,
        }
    ),
    "verification_strategy": frozenset(
        {
            "none",
            "llm_verifier",
            "llm_verify_repair",
            "llm_confirm_only",
            "deterministic_guards_only",
            "deterministic_evidence_span_check",
            "deterministic_validator",
            "verify_repair",
            "adjudicator",
            "llm_recall_pass_with_deterministic_merge",
            PENDING_BACKFILL,
        }
    ),
    "example_strategy": frozenset(
        {
            "zero_shot_or_prompt_only",
            "manual_few_shot_or_policy_examples",
            "labeled_few_shot",
            "bootstrapped",
            "optimizer_or_bootstrapped",
            "gepa",
            "mipro",
            "none",
            PENDING_BACKFILL,
        }
    ),
    "outcome": frozenset(
        {
            "promote",
            "freeze",
            "reject",
            "hold",
            "superseded",
            "exploratory",
            "pending",
            PENDING_BACKFILL,
        }
    ),
    "run_scope": frozenset(
        {
            "smoke",
            "cap1",
            "cap3",
            "cap5",
            "cap10",
            "cap25",
            "cap100",
            "slice",
            "full_validation",
            "test_holdout",
            "unclear",
            PENDING_BACKFILL,
        }
    ),
    "varied_factor": frozenset(
        {
            "program_architecture",
            "hybrid_balance_class",
            "interleaving_position",
            "knowledge_source_position",
            "model_track",
            "schema_complexity",
            "prompt_policy",
            "optimizer_strategy",
            "ladder_rung",
            "validation_ladder_rung",
            "run_scope",
            "normalization_strategy",
            "verification_strategy",
            "evidence_strategy",
            "control_mode",
            "pipeline_stage_graph",
            "stage_executor",
            "implementation_variant",
            "context_selection_policy",
            "multi_factor",
            PENDING_BACKFILL,
        }
    ),
}

ARRAY_FIELD_ALLOWED: dict[str, frozenset[str]] = {
    "hybrid_balance_class": frozenset(
        {
            "L0_llm_only",
            "L1_llm_constrained",
            "H1_post_deterministic",
            "H2_pre_deterministic",
            "H3_interleaved_tool_hybrid",
            "H4_deterministic_first_llm_adjudicates",
            "D1_deterministic_only",
            PENDING_BACKFILL,
        }
    ),
    "deterministic_roles": frozenset(
        {
            "none",
            "json_schema_constraint",
            "pydantic_validation",
            "benchmark_label_policy",
            "gold_audit_policy",
            "field_family_scoring",
            "section_context_selection",
            "temporal_candidate_generation",
            "frequency_normalization",
            "controlled_vocabulary_filter",
            "evidence_span_guard",
            "evidence_quote_repair",
            "benchmark_bridge",
            "schema_repair",
            "add_only_recall_merge",
            "optimizer_metric",
            "diagnostic_scoring",
            PENDING_BACKFILL,
        }
    ),
    "llm_roles": frozenset(
        {
            "none",
            "clinical_field_extraction",
            "frequency_interpretation",
            "temporal_reasoning",
            "candidate_selection",
            "benchmark_policy_application",
            "evidence_quote_generation",
            "normalization",
            "verification",
            "repair",
            "adjudication",
            "recall_pass",
            "tool_guided_reasoning",
            "optimizer_candidate_generation",
            PENDING_BACKFILL,
        }
    ),
    "interleaving_positions": frozenset(
        {
            "pre",
            "during",
            "tool_during",
            "post",
            "eval_only",
            PENDING_BACKFILL,
        }
    ),
    "knowledge_sources": frozenset(
        {
            "regex_rules",
            "temporal_rules",
            "controlled_vocabulary",
            "benchmark_label_policy",
            "json_schema",
            "pydantic_validation",
            "manual_examples",
            "bootstrapped_examples",
            "optimizer_feedback",
            "cui_or_ontology",
            "gold_audit_policy",
            "temporal_tooling",
            "diagnostic_metric",
            PENDING_BACKFILL,
        }
    ),
    "control_modes": frozenset(
        {
            "none",
            "soft_hint",
            "hard_constraint",
            "tool_affordance",
            "posthoc_correction",
            "diagnostic_only",
            PENDING_BACKFILL,
        }
    ),
    "schema_integrity_strategy": frozenset(
        {
            "none",
            "json_schema",
            "pydantic_validation",
            "retry_repair",
            "scorer_only",
            PENDING_BACKFILL,
        }
    ),
    "clinical_task_family": frozenset(
        {
            "frequency",
            "diagnosis",
            "seizure_type",
            "medication",
            "investigation",
            "comorbidity",
            "birth_development",
            "family_history",
            "social_history",
            "driving",
            "pregnancy",
            "multi_family",
            PENDING_BACKFILL,
        }
    ),
}

VARIED_FACTOR_ALLOWS_DIMENSION: dict[str, frozenset[str]] = {
    "scorer": frozenset({"schema_complexity", "multi_factor"}),
    "split": frozenset({"run_scope", "multi_factor"}),
    "schema_level": frozenset({"schema_complexity", "multi_factor"}),
    "schema_complexity": frozenset({"schema_complexity", "multi_factor"}),
    "model_track": frozenset({"model_track", "multi_factor"}),
    "program_architecture": frozenset({"program_architecture", "multi_factor"}),
    "hybrid_balance_class": frozenset({"hybrid_balance_class", "multi_factor"}),
}

MISSING_RUN_DOC_MARKERS = (
    "not present in the current local runs",
    "run directory is referenced by docs but is not present",
    "original run directory is referenced",
)


@dataclass(frozen=True)
class ValidationIssue:
    level: IssueLevel
    code: str
    message: str
    path: str = ""

    def format(self) -> str:
        prefix = f"[{self.level}] {self.code}"
        if self.path:
            prefix = f"{prefix} ({self.path})"
        return f"{prefix}: {self.message}"


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_path(value: str) -> str:
    return value.replace("\\", "/")


def _row_comparison_groups(row: dict[str, Any]) -> list[str]:
    groups: list[str] = []
    primary = row.get("comparison_group")
    if primary and primary != PENDING_BACKFILL:
        groups.append(primary)
    for group in row.get("comparison_groups") or []:
        if group and group != PENDING_BACKFILL:
            groups.append(group)
    return list(dict.fromkeys(groups))


def _fixed_control(row: dict[str, Any], key: str) -> str | None:
    controls = row.get("fixed_controls") or {}
    value = controls.get(key)
    if value is None:
        return None
    return str(value)


def _canonical_run_documented_missing(row: dict[str, Any]) -> bool:
    haystack = " ".join(
        [
            row.get("notes") or "",
            *[
                caveat
                for caveat in row.get("metric_caveats") or []
                if isinstance(caveat, str)
            ],
        ]
    ).lower()
    return any(marker in haystack for marker in MISSING_RUN_DOC_MARKERS)


def _validate_controlled_value(
    *,
    field: str,
    value: str,
    allowed: frozenset[str],
    path: str,
) -> list[ValidationIssue]:
    if value in allowed:
        return []
    return [
        ValidationIssue(
            level="error",
            code="invalid_controlled_value",
            message=f"{field}={value!r} is not in the controlled vocabulary.",
            path=path,
        )
    ]


def validate_registry_row_controlled_values(
    row: dict[str, Any],
    *,
    experiment_index: int,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    experiment_id = row.get("experiment_id") or f"row[{experiment_index}]"
    base_path = f"experiments[{experiment_id}]"

    if not row.get("experiment_id") or not str(row["experiment_id"]).strip():
        issues.append(
            ValidationIssue(
                level="error",
                code="missing_experiment_id",
                message="Registry row is missing experiment_id.",
                path=base_path,
            )
        )
        return issues

    for field, allowed in SINGLE_CONTROLLED_FIELDS.items():
        if field not in row or row[field] is None:
            continue
        issues.extend(
            _validate_controlled_value(
                field=field,
                value=str(row[field]),
                allowed=allowed,
                path=f"{base_path}.{field}",
            )
        )

    for field in ARRAY_CONTROLLED_FIELDS:
        if field not in row or row[field] is None:
            continue
        values = _as_list(row[field])
        if not isinstance(row[field], list):
            issues.append(
                ValidationIssue(
                    level="error",
                    code="array_field_not_array",
                    message=f"{field} must be a JSON array.",
                    path=f"{base_path}.{field}",
                )
            )
        allowed = ARRAY_FIELD_ALLOWED[field]
        for value in values:
            issues.extend(
                _validate_controlled_value(
                    field=field,
                    value=str(value),
                    allowed=allowed,
                    path=f"{base_path}.{field}",
                )
            )

    return issues


def validate_registry_row_canonical_run(
    row: dict[str, Any],
    *,
    runs_root: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    experiment_id = row["experiment_id"]
    canonical_run_id = row.get("canonical_run_id")
    if not canonical_run_id:
        return issues

    run_dir = runs_root / canonical_run_id
    if run_dir.is_dir():
        return issues

    if _canonical_run_documented_missing(row):
        issues.append(
            ValidationIssue(
                level="warning",
                code="canonical_run_missing_documented",
                message=(
                    f"canonical_run_id {canonical_run_id!r} is absent under runs/, "
                    "but the row documents the missing artifact."
                ),
                path=f"experiments[{experiment_id}].canonical_run_id",
            )
        )
        return issues

    issues.append(
        ValidationIssue(
            level="error",
            code="canonical_run_missing",
            message=f"canonical_run_id {canonical_run_id!r} has no runs/{canonical_run_id} directory.",
            path=f"experiments[{experiment_id}].canonical_run_id",
        )
    )
    return issues


def validate_registry_row_decision_doc(
    row: dict[str, Any],
    *,
    repo_root: Path,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    experiment_id = row["experiment_id"]
    outcome = row.get("outcome")
    if outcome not in DECISION_OUTCOMES_REQUIRING_DOC:
        return issues

    decision_doc = row.get("decision_doc")
    if not decision_doc or decision_doc == PLACEHOLDER_DECISION_DOC:
        issues.append(
            ValidationIssue(
                level="error",
                code="decision_doc_missing",
                message=(
                    f"outcome={outcome!r} requires a non-placeholder decision_doc path."
                ),
                path=f"experiments[{experiment_id}].decision_doc",
            )
        )
        return issues

    doc_path = repo_root / _normalize_path(decision_doc)
    if not doc_path.is_file():
        issues.append(
            ValidationIssue(
                level="error",
                code="decision_doc_not_found",
                message=f"decision_doc {decision_doc!r} does not exist.",
                path=f"experiments[{experiment_id}].decision_doc",
            )
        )
    return issues


def _dimension_explained(
    rows: list[dict[str, Any]],
    *,
    dimension: str,
    values: set[str | None],
) -> bool:
    if len(values) <= 1:
        return True

    allowed_factors = VARIED_FACTOR_ALLOWS_DIMENSION.get(dimension, frozenset())
    row_factors = {row.get("varied_factor") for row in rows}
    if row_factors & allowed_factors:
        return True
    if any(row.get("comparison_caveat") for row in rows):
        return True
    return False


def validate_comparison_groups(rows: list[dict[str, Any]]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in rows:
        for group_id in _row_comparison_groups(row):
            grouped[group_id].append(row)

    for group_id, members in sorted(grouped.items()):
        scorers = {_fixed_control(row, "scorer") for row in members}
        splits = {_fixed_control(row, "split") for row in members}
        schema_complexities = {row.get("schema_complexity") for row in members}
        model_tracks = {row.get("model_track") for row in members}

        checks = [
            ("scorer", scorers),
            ("split", splits),
            ("schema_complexity", schema_complexities),
            ("model_track", model_tracks),
        ]
        for dimension, values in checks:
            if _dimension_explained(members, dimension=dimension, values=values):
                continue
            issues.append(
                ValidationIssue(
                    level="error",
                    code="comparison_group_incompatible",
                    message=(
                        f"comparison group {group_id!r} mixes {dimension} values "
                        f"{sorted(v for v in values if v is not None)!r} without "
                        "varied_factor, comparison_caveat, or metric_caveats documenting "
                        "the exception."
                    ),
                    path=f"comparison_group:{group_id}",
                )
            )
    return issues


def validate_experiment_config_coverage(
    config: ExperimentConfig,
    *,
    config_path: Path,
    registry_ids: frozenset[str],
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if config.taxonomy is not None:
        return issues
    if config.taxonomy_exemption is not None:
        return issues
    if config.experiment_id in registry_ids:
        return issues

    issues.append(
        ValidationIssue(
            level="error",
            code="config_taxonomy_missing",
            message=(
                "Config must include taxonomy, taxonomy_exemption, or a registry row."
            ),
            path=str(config_path),
        )
    )
    return issues


def validate_experiment_taxonomy(
    repo_root: Path | None = None,
    *,
    registry_path: Path | None = None,
    config_dir: Path | None = None,
    runs_root: Path | None = None,
) -> list[ValidationIssue]:
    root = (repo_root or Path.cwd()).resolve()
    registry_file = registry_path or (root / REGISTRY_PATH)
    configs = config_dir or (root / "configs" / "experiments")
    runs = runs_root or (root / "runs")

    issues: list[ValidationIssue] = []
    payload = load_experiment_registry(registry_file)
    rows = payload.get("experiments") or []
    registry_ids = frozenset(row["experiment_id"] for row in rows if row.get("experiment_id"))

    for index, row in enumerate(rows):
        issues.extend(validate_registry_row_controlled_values(row, experiment_index=index))
        issues.extend(validate_registry_row_canonical_run(row, runs_root=runs))
        issues.extend(validate_registry_row_decision_doc(row, repo_root=root))

    issues.extend(validate_comparison_groups(rows))

    for config_path in sorted(configs.glob("*.json")):
        config = load_experiment_config(config_path)
        issues.extend(
            validate_experiment_config_coverage(
                config,
                config_path=config_path.relative_to(root),
                registry_ids=registry_ids,
            )
        )

    return issues


def format_validation_report(issues: Iterable[ValidationIssue]) -> str:
    lines = [issue.format() for issue in issues]
    return "\n".join(lines)


def validation_failed(issues: Iterable[ValidationIssue], *, include_warnings: bool = True) -> bool:
    for issue in issues:
        if issue.level == "error":
            return True
        if include_warnings and issue.level == "warning":
            return True
    return False

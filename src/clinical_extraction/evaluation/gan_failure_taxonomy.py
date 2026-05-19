"""Action-oriented failure taxonomy for Gan frequency run analysis."""

from __future__ import annotations

from typing import Any, Literal

FailureActionTier = Literal["benchmark_severe", "diagnostic_only", "operational"]

BENCHMARK_SEVERE_CLASSES = frozenset(
    {
        "unknown_vs_no_reference",
        "unknown_cluster_vs_no_reference",
        "unknown_vs_seizure_free",
        "seizure_free_to_no_reference_benchmark_severe",
        "cluster_missing_per_cluster",
        "cluster_structure_swap",
        "cluster_semantic_mismatch",
        "cluster_collapsed_to_rate",
        "false_positive_rate",
        "missed_frequency_reference",
        "frequent_undercalled",
        "frequent_overcalled",
        "unknown_as_quantified_rate",
        "unknown_as_high_rate",
        "purist_bin_boundary_within_pragmatic",
        "pragmatic_match_monthly_divergence",
        "purist_match_monthly_divergence",
        "other_semantic_mismatch",
    }
)

DIAGNOSTIC_ONLY_CLASSES = frozenset(
    {
        "unknown_cluster_label_shape_mismatch",
        "unknown_label_shape_mismatch",
        "seizure_free_to_no_reference_monthly_match",
        "seizure_free_label_shape_mismatch",
        "seizure_free_semantic_mismatch",
        "cluster_label_shape_mismatch",
        "monthly_match_label_surface_mismatch",
    }
)

OPERATIONAL_CLASSES = frozenset(
    {
        "missing_prediction",
        "schema_missing_field",
        "invalid_predicted_label",
        "abstention_or_missing_value",
    }
)


def failure_action_tier(failure_class: str) -> FailureActionTier:
    if failure_class in BENCHMARK_SEVERE_CLASSES:
        return "benchmark_severe"
    if failure_class in DIAGNOSTIC_ONLY_CLASSES:
        return "diagnostic_only"
    if failure_class in OPERATIONAL_CLASSES:
        return "operational"
    if failure_class == "all_metrics_match":
        return "diagnostic_only"
    return "benchmark_severe"


def classify_gan_frequency_failure(row: dict[str, Any]) -> str:
    if row["status"] != "scored":
        return row["failure_class"]

    g_norm = row["normalized_gold_label"]
    p_norm = row["normalized_predicted_label"]
    g_prag = row["gold_pragmatic_category"]
    p_prag = row["predicted_pragmatic_category"]

    if row["normalized_exact_match"]:
        return "all_metrics_match"

    if g_norm == "unknown" and p_norm == "no seizure frequency reference":
        return "unknown_vs_no_reference"
    if g_norm.startswith("unknown") and p_norm == "no seizure frequency reference":
        return "unknown_cluster_vs_no_reference"
    if g_norm == "unknown" and p_norm.startswith("seizure free"):
        return "unknown_vs_seizure_free"
    if g_norm == "unknown" and p_norm == "unknown":
        return "unknown_label_shape_mismatch"
    if (
        g_norm.startswith("unknown")
        and "per cluster" in g_norm
        and p_norm == "unknown"
        and row["monthly_match"]
    ):
        return "unknown_cluster_label_shape_mismatch"
    if (
        g_norm.startswith("seizure free")
        and p_norm == "no seizure frequency reference"
        and row["monthly_match"]
    ):
        return "seizure_free_to_no_reference_monthly_match"
    if g_norm.startswith("seizure free") and p_norm == "no seizure frequency reference":
        return "seizure_free_to_no_reference_benchmark_severe"
    if g_norm.startswith("seizure free") and p_norm.startswith("seizure free"):
        if row["monthly_match"]:
            return "seizure_free_label_shape_mismatch"
        return "seizure_free_semantic_mismatch"
    if "cluster" in g_norm and "cluster" in p_norm and g_norm != p_norm:
        if "multiple per cluster" in g_norm and "per cluster" not in p_norm:
            return "cluster_missing_per_cluster"
        if p_norm.count("cluster") != g_norm.count("cluster"):
            return "cluster_structure_swap"
        return "cluster_semantic_mismatch"
    if "cluster" in g_norm and "cluster" not in p_norm:
        if row["monthly_match"]:
            return "cluster_label_shape_mismatch"
        return "cluster_collapsed_to_rate"
    if g_norm == "no seizure frequency reference" and p_norm not in (
        "no seizure frequency reference",
        "unknown",
    ):
        return "false_positive_rate"
    if g_norm != "no seizure frequency reference" and p_norm == "no seizure frequency reference":
        return "missed_frequency_reference"
    if g_prag == p_prag and not row["purist_match"]:
        return "purist_bin_boundary_within_pragmatic"
    if row["monthly_match"] and not row["normalized_exact_match"]:
        return "monthly_match_label_surface_mismatch"
    if row["pragmatic_match"] and not row["monthly_match"]:
        return "pragmatic_match_monthly_divergence"
    if row["purist_match"] and not row["monthly_match"]:
        return "purist_match_monthly_divergence"
    if g_prag == "frequent" and p_prag == "infrequent":
        return "frequent_undercalled"
    if g_prag == "infrequent" and p_prag == "frequent":
        return "frequent_overcalled"
    if g_prag == "unknown" and p_prag == "infrequent":
        return "unknown_as_quantified_rate"
    if g_prag == "unknown" and p_prag == "frequent":
        return "unknown_as_high_rate"
    return "other_semantic_mismatch"

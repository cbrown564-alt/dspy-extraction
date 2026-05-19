#!/usr/bin/env python3
"""Comprehensive Gan frequency run error analysis."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.gan import load_gan_records
from clinical_extraction.evaluation.cli import _gan_frequency_value, _prediction_label
from clinical_extraction.gan.frequency import pragmatic_category, purist_category
from clinical_extraction.evaluation.gan_failure_taxonomy import (
    classify_gan_frequency_failure,
    failure_action_tier,
)
from clinical_extraction.evaluation.gan_run_analysis import (
    analysis_record_ids,
    load_split_ids,
)
from clinical_extraction.gan.scoring import score_gan_frequency_prediction
from clinical_extraction.schemas import PredictionSet


METRIC_KEYS = (
    "normalized_exact",
    "monthly",
    "purist",
    "pragmatic",
)


def _metric_pattern(row: dict[str, Any]) -> str:
    bits = [
        "1" if row["normalized_exact_match"] else "0",
        "1" if row["monthly_match"] else "0",
        "1" if row["purist_match"] else "0",
        "1" if row["pragmatic_match"] else "0",
    ]
    return "".join(bits)


def analyze_run(
    *,
    run_dir: Path,
    split_file: Path,
    split_name: str,
) -> dict[str, Any]:
    prediction_set = PredictionSet.model_validate_json(
        (run_dir / "predictions.json").read_text(encoding="utf-8")
    )
    gold_by_id = {record.record_id: record for record in load_gan_records()}
    predictions_by_id = {
        prediction.document_id: prediction
        for prediction in prediction_set.predictions
    }
    analysis_record_ids_list, analysis_scope = analysis_record_ids(
        run_dir=run_dir,
        split_file=split_file,
        split_name=split_name,
        predictions_by_id=predictions_by_id,
    )

    rows: list[dict[str, Any]] = []
    for record_id in analysis_record_ids_list:
        gold = gold_by_id[record_id]
        base = {
            "record_id": record_id,
            "gold_label": gold.gold_label,
            "reference_label": gold.reference_label,
            "row_ok": gold.row_ok,
            "hard_case": "hard_case" in gold.flags,
            "label_reference_disagreement": gold.reference_label is not None
            and gold.reference_label != gold.gold_label,
            "gold_pragmatic_category": pragmatic_category(gold.gold_label),
            "gold_purist_category": purist_category(gold.gold_label),
        }
        prediction = predictions_by_id.get(record_id)
        if prediction is None:
            rows.append(
                {
                    **base,
                    "status": "missing_prediction",
                    "failure_class": "missing_prediction",
                }
            )
            continue

        predicted_value = _gan_frequency_value(prediction)
        if predicted_value is None:
            rows.append(
                {
                    **base,
                    "status": "invalid",
                    "failure_class": "schema_missing_field",
                    "predicted_label": None,
                }
            )
            continue

        predicted_label = _prediction_label(predicted_value)
        repair_applied = predicted_value.metadata.get("repair_applied") is True
        abstained = "abstained" in predicted_value.quality_flags
        extras = {
            "raw_predicted_label": predicted_value.raw_value,
            "normalized_predicted_value": predicted_value.normalized_value,
            "repair_applied": repair_applied,
            "abstained": abstained,
            "evidence_count": len(predicted_value.evidence),
        }

        if predicted_label is None:
            rows.append(
                {
                    **base,
                    **extras,
                    "status": "invalid",
                    "failure_class": "abstention_or_missing_value",
                    "predicted_label": None,
                }
            )
            continue

        try:
            score = score_gan_frequency_prediction(
                gold_label=gold.gold_label,
                predicted_label=predicted_label,
            )
        except ValueError as exc:
            rows.append(
                {
                    **base,
                    **extras,
                    "status": "invalid",
                    "failure_class": "invalid_predicted_label",
                    "predicted_label": predicted_label,
                    "invalid_reason": str(exc),
                }
            )
            continue

        row = {
            **base,
            **extras,
            "status": "scored",
            "predicted_label": predicted_label,
            "normalized_gold_label": score.normalized_gold_label,
            "normalized_predicted_label": score.normalized_predicted_label,
            "gold_monthly_frequency": score.gold_monthly_frequency,
            "predicted_monthly_frequency": score.predicted_monthly_frequency,
            "predicted_pragmatic_category": score.predicted_pragmatic_category,
            "predicted_purist_category": score.predicted_purist_category,
            "raw_exact_match": gold.gold_label == predicted_label,
            "normalized_exact_match": score.exact_normalized_match,
            "monthly_match": score.monthly_frequency_match,
            "purist_match": score.purist_category_match,
            "pragmatic_match": score.pragmatic_category_match,
            "monthly_delta": abs(
                score.gold_monthly_frequency - score.predicted_monthly_frequency
            ),
        }
        row["metric_pattern"] = _metric_pattern(row)
        row["failure_class"] = classify_gan_frequency_failure(row)
        row["failure_action_tier"] = failure_action_tier(row["failure_class"])
        rows.append(row)

    scored = [row for row in rows if row["status"] == "scored"]
    valid = scored
    invalid = [row for row in rows if row["status"] != "scored"]

    pattern_counts = Counter(row["metric_pattern"] for row in valid)
    scored_misses = [row for row in valid if not row["normalized_exact_match"]]
    failure_counts = Counter(row["failure_class"] for row in scored_misses)
    failure_action_tier_counts = Counter(row["failure_action_tier"] for row in scored_misses)
    failure_taxonomy_by_action_tier: dict[str, dict[str, int]] = {
        tier: dict(
            Counter(
                row["failure_class"]
                for row in scored_misses
                if row["failure_action_tier"] == tier
            )
        )
        for tier in ("benchmark_severe", "diagnostic_only", "operational")
    }
    invalid_failure_counts = Counter(row["failure_class"] for row in invalid)

    divergence: dict[str, Any] = {
        "metric_pattern_counts": dict(sorted(pattern_counts.items())),
        "patterns": {},
    }
    pattern_labels = {
        "1111": "all_four_match",
        "1110": "normalized_monthly_purist_not_pragmatic_impossible",
        "1101": "normalized_monthly_pragmatic_not_purist_impossible",
        "1100": "normalized_monthly_only_impossible",
        "1011": "normalized_purist_pragmatic_not_monthly_impossible",
        "1010": "normalized_purist_not_monthly_pragmatic_impossible",
        "1001": "normalized_pragmatic_not_monthly_purist",
        "1000": "normalized_only_impossible",
        "0111": "monthly_purist_pragmatic_not_normalized",
        "0110": "monthly_purist_not_normalized_pragmatic_impossible",
        "0101": "monthly_pragmatic_not_normalized_purist",
        "0100": "monthly_only",
        "0011": "purist_pragmatic_not_monthly",
        "0010": "purist_only_not_monthly",
        "0001": "pragmatic_only",
        "0000": "all_four_wrong",
    }
    for pattern, count in pattern_counts.items():
        label = pattern_labels.get(pattern, "unknown_pattern")
        examples = [
            {
                "record_id": row["record_id"],
                "gold_label": row["gold_label"],
                "predicted_label": row["predicted_label"],
                "gold_monthly_frequency": row["gold_monthly_frequency"],
                "predicted_monthly_frequency": row["predicted_monthly_frequency"],
                "gold_purist_category": row["gold_purist_category"],
                "predicted_purist_category": row["predicted_purist_category"],
                "gold_pragmatic_category": row["gold_pragmatic_category"],
                "predicted_pragmatic_category": row["predicted_pragmatic_category"],
                "failure_class": row["failure_class"],
            }
            for row in valid
            if row["metric_pattern"] == pattern
        ][:5]
        divergence["patterns"][pattern] = {
            "label": label,
            "count": count,
            "share_of_valid": count / len(valid) if valid else 0.0,
            "examples": examples,
        }

    metric_implications = {
        "normalized_exact_implies": {
            "monthly": sum(
                1
                for row in valid
                if row["normalized_exact_match"] and row["monthly_match"]
            ),
            "purist": sum(
                1
                for row in valid
                if row["normalized_exact_match"] and row["purist_match"]
            ),
            "pragmatic": sum(
                1
                for row in valid
                if row["normalized_exact_match"] and row["pragmatic_match"]
            ),
            "total_normalized_exact": sum(
                1 for row in valid if row["normalized_exact_match"]
            ),
        },
        "monthly_implies": {
            "purist": sum(
                1 for row in valid if row["monthly_match"] and row["purist_match"]
            ),
            "pragmatic": sum(
                1 for row in valid if row["monthly_match"] and row["pragmatic_match"]
            ),
            "normalized_exact": sum(
                1
                for row in valid
                if row["monthly_match"] and row["normalized_exact_match"]
            ),
            "total_monthly_match": sum(1 for row in valid if row["monthly_match"]),
        },
        "purist_implies": {
            "pragmatic": sum(
                1 for row in valid if row["purist_match"] and row["pragmatic_match"]
            ),
            "monthly": sum(
                1 for row in valid if row["purist_match"] and row["monthly_match"]
            ),
            "total_purist_match": sum(1 for row in valid if row["purist_match"]),
        },
    }

    taxonomy_by_metric: dict[str, dict[str, int]] = {}
    for metric in ("normalized_exact", "monthly", "purist", "pragmatic"):
        key = f"{metric}_match" if metric != "normalized_exact" else "normalized_exact_match"
        misses = [row for row in valid if not row[key]]
        taxonomy_by_metric[metric] = dict(Counter(row["failure_class"] for row in misses))

    boundary_cases = {
        "purist_bin_boundary_within_pragmatic": [
            row
            for row in valid
            if row["pragmatic_match"]
            and not row["purist_match"]
            and not row["normalized_exact_match"]
        ],
        "pragmatic_match_monthly_divergence": [
            row
            for row in valid
            if row["pragmatic_match"] and not row["monthly_match"]
        ],
        "purist_match_monthly_divergence": [
            row
            for row in valid
            if row["purist_match"] and not row["monthly_match"]
        ],
        "monthly_match_label_surface_mismatch": [
            row
            for row in valid
            if row["monthly_match"] and not row["normalized_exact_match"]
        ],
    }

    summary = {
        "run_dir": str(run_dir),
        "split_name": split_name,
        "analysis_scope": analysis_scope,
        "record_counts": {
            "split_total": len(load_split_ids(split_file, split_name)),
            "analysis_total": len(analysis_record_ids_list),
            "predicted": len(predictions_by_id),
            "scored_valid": len(valid),
            "invalid_or_missing": len(invalid),
        },
        "accuracies_valid_only": {
            "normalized_label": sum(1 for r in valid if r["normalized_exact_match"])
            / len(valid),
            "monthly_frequency": sum(1 for r in valid if r["monthly_match"]) / len(valid),
            "purist_category": sum(1 for r in valid if r["purist_match"]) / len(valid),
            "pragmatic_category": sum(1 for r in valid if r["pragmatic_match"])
            / len(valid),
        },
        "metric_implications": metric_implications,
        "divergence": divergence,
        "failure_taxonomy_scored_misses": dict(failure_counts.most_common()),
        "failure_action_tier_counts": dict(failure_action_tier_counts.most_common()),
        "failure_taxonomy_by_action_tier": failure_taxonomy_by_action_tier,
        "failure_taxonomy_invalid": dict(invalid_failure_counts.most_common()),
        "taxonomy_by_metric_misses": taxonomy_by_metric,
        "boundary_case_counts": {
            key: len(value) for key, value in boundary_cases.items()
        },
    }

    return {
        "summary": summary,
        "rows": rows,
        "boundary_cases": boundary_cases,
    }


def _render_markdown(analysis: dict[str, Any], experiment_id: str) -> str:
    summary = analysis["summary"]
    rows = analysis["rows"]
    boundary = analysis["boundary_cases"]
    valid = [r for r in rows if r["status"] == "scored"]
    invalid = [r for r in rows if r["status"] != "scored"]

    lines: list[str] = []
    lines.append(f"# Gan S0 Error Analysis: {experiment_id}")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- Artifact directory: `{summary['run_dir']}`")
    lines.append(f"- Split: `{summary['split_name']}`")
    lines.append(f"- Analysis scope: `{summary.get('analysis_scope', 'full_split')}`")
    lines.append(f"- Records in split: {summary['record_counts']['split_total']}")
    lines.append(
        f"- Records analyzed: {summary['record_counts'].get('analysis_total', summary['record_counts']['split_total'])}"
    )
    lines.append(f"- Valid scored predictions: {summary['record_counts']['scored_valid']}")
    lines.append(
        f"- Invalid or missing predictions: {summary['record_counts']['invalid_or_missing']}"
    )
    lines.append("")
    lines.append("## Metrics snapshot (valid predictions only)")
    lines.append("")
    acc = summary["accuracies_valid_only"]
    lines.append(
        f"| Metric | Accuracy | Correct | Denominator |"
    )
    lines.append(f"| --- | ---: | ---: | ---: |")
    n = summary["record_counts"]["scored_valid"]
    for name, value in acc.items():
        correct = round(value * n)
        lines.append(f"| {name} | {value:.1%} | {correct} | {n} |")
    lines.append("")
    lines.append(
        "Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. "
        "Normalized-label exact is diagnostic format fidelity."
    )
    lines.append("")
    lines.append("## Do the four metrics move together?")
    lines.append("")
    lines.append(
        "Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match)."
    )
    lines.append("")
    lines.append("| Pattern | Label | Count | Share |")
    lines.append("| --- | --- | ---: | ---: |")
    for pattern, payload in summary["divergence"]["patterns"].items():
        lines.append(
            f"| `{pattern}` | {payload['label']} | {payload['count']} | {payload['share_of_valid']:.1%} |"
        )
    lines.append("")
    impl = summary["metric_implications"]
    lines.append("### Logical containment on this run")
    lines.append("")
    ne = impl["normalized_exact_implies"]["total_normalized_exact"]
    lines.append(
        f"- Normalized exact ({ne} records): always co-occurs with monthly, Purist, and Pragmatic match."
    )
    mm = impl["monthly_implies"]["total_monthly_match"]
    lines.append(
        f"- Monthly match ({mm} records): always implies Purist and Pragmatic; "
        f"{impl['monthly_implies']['normalized_exact']} also have normalized exact."
    )
    pm = impl["purist_implies"]["total_purist_match"]
    lines.append(
        f"- Purist match ({pm} records): always implies Pragmatic; "
        f"{impl['purist_implies']['monthly']} also match monthly."
    )
    lines.append(
        f"- Pragmatic-only wins (pattern `0001`): "
        f"{summary['divergence']['patterns'].get('0001', {}).get('count', 0)} records."
    )
    lines.append(
        f"- Purist-without-monthly (pattern `0010`/`0011`): "
        f"{summary['divergence']['patterns'].get('0010', {}).get('count', 0)} + "
        f"{summary['divergence']['patterns'].get('0011', {}).get('count', 0)} records."
    )
    lines.append("")
    lines.append("### Boundary cases")
    lines.append("")
    for name, count in summary["boundary_case_counts"].items():
        lines.append(f"- **{name}**: {count}")
    lines.append("")
    lines.append("## Holistic failure taxonomy")
    lines.append("")
    lines.append("### Action tiers (scored misses)")
    lines.append("")
    lines.append(
        "Benchmark-severe classes should drive prompt or verifier work. "
        "Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite "
        "normalized-label mismatch."
    )
    lines.append("")
    lines.append("| Action tier | Count |")
    lines.append("| --- | ---: |")
    for tier, count in summary.get("failure_action_tier_counts", {}).items():
        lines.append(f"| {tier} | {count} |")
    lines.append("")
    for tier, class_counts in summary.get("failure_taxonomy_by_action_tier", {}).items():
        if not class_counts:
            continue
        lines.append(f"#### {tier}")
        lines.append("")
        lines.append("| Failure class | Count |")
        lines.append("| --- | ---: |")
        for cls, count in sorted(class_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {cls} | {count} |")
        lines.append("")
    lines.append("### Scored misses (normalized label wrong)")
    lines.append("")
    lines.append("| Failure class | Count |")
    lines.append("| --- | ---: |")
    for cls, count in summary["failure_taxonomy_scored_misses"].items():
        lines.append(f"| {cls} | {count} |")
    lines.append("")
    lines.append("### Invalid / abstained / missing")
    lines.append("")
    lines.append("| Failure class | Count |")
    lines.append("| --- | ---: |")
    for cls, count in summary["failure_taxonomy_invalid"].items():
        lines.append(f"| {cls} | {count} |")
    lines.append("")
    lines.append("### Taxonomy grouped by which metric failed")
    lines.append("")
    for metric, counts in summary["taxonomy_by_metric_misses"].items():
        lines.append(f"#### Misses against **{metric}**")
        lines.append("")
        if not counts:
            lines.append("_No misses._")
        else:
            lines.append("| Failure class | Count |")
            lines.append("| --- | ---: |")
            for cls, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
                lines.append(f"| {cls} | {count} |")
        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append(_interpretation(summary, valid, invalid, boundary))
    lines.append("")
    lines.append("## Record index")
    lines.append("")
    lines.append(
        "Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder."
    )
    lines.append("")
    lines.append("| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |")
    lines.append("| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |")
    for row in rows:
        if row["status"] != "scored":
            lines.append(
                f"| {row['record_id']} | {row['status']} | - | - | - | - | {row['failure_class']} | {row['gold_label']} | {row.get('predicted_label', '')} |"
            )
            continue
        lines.append(
            f"| {row['record_id']} | scored | "
            f"{'Y' if row['normalized_exact_match'] else 'N'} | "
            f"{'Y' if row['monthly_match'] else 'N'} | "
            f"{'Y' if row['purist_match'] else 'N'} | "
            f"{'Y' if row['pragmatic_match'] else 'N'} | "
            f"{row['failure_class']} | {row['gold_label']} | {row['predicted_label']} |"
        )
    return "\n".join(lines) + "\n"


def _interpretation(
    summary: dict[str, Any],
    valid: list[dict[str, Any]],
    invalid: list[dict[str, Any]],
    boundary: dict[str, list[dict[str, Any]]],
) -> str:
    parts: list[str] = []
    parts.append(
        "The four metrics form a strict hierarchy on valid predictions: "
        "normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. "
        "They do **not** always improve together in the sense that fixing one layer "
        "can leave coarser layers unchanged, but finer success never appears without coarser success."
    )
    parts.append("")
    benchmark_failures = summary.get("failure_taxonomy_by_action_tier", {}).get(
        "benchmark_severe", {}
    )
    if benchmark_failures:
        sorted_failures = sorted(
            benchmark_failures.items(), key=lambda item: (-item[1], item[0])
        )
        top_count = sorted_failures[0][1]
        top_failures = [
            failure_class
            for failure_class, count in sorted_failures
            if count == top_count
        ]
        top_failure_text = ", ".join(f"`{failure}`" for failure in top_failures)
        miss_text = (
            "1 scored miss"
            if top_count == 1
            else f"{top_count} scored misses"
        )
        count_suffix = " each" if len(top_failures) > 1 else ""
        parts.append(
            f"The leading benchmark-severe failure class"
            f"{'es' if len(top_failures) > 1 else ''} on this run "
            f"{'are' if len(top_failures) > 1 else 'is'} {top_failure_text} "
            f"({miss_text}{count_suffix}). These are the first prompt or "
            f"verifier targets; lower-tier metric wins should not hide them."
        )
    else:
        parts.append(
            "No benchmark-severe scored misses appear in this run; remaining cleanup is "
            "diagnostic-only or operational invalid/abstention handling."
        )
    parts.append("")
    cluster = sum(
        1
        for row in valid
        if not row["normalized_exact_match"]
        and "cluster" in row["failure_class"]
    )
    parts.append(
        f"Cluster-format errors account for {cluster} scored misses, split between incomplete "
        f"cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates."
    )
    parts.append("")
    prag_only = summary["divergence"]["patterns"].get("0001", {}).get("count", 0)
    parts.append(
        f"There are {prag_only} **pragmatic-only** successes: same coarse bucket "
        f"(infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. "
        f"These are clinically misleading if only Pragmatic accuracy is reported."
    )
    parts.append("")
    purist_monthly = len(boundary.get("purist_match_monthly_divergence", []))
    prag_monthly = len(boundary.get("pragmatic_match_monthly_divergence", []))
    parts.append(
        f"Purist-without-monthly cases: {purist_monthly}; pragmatic-without-monthly: {prag_monthly}. "
        f"These arise when different labels land in the same bin but convert to different seizures/month."
    )
    parts.append("")
    abst = sum(1 for row in invalid if row["failure_class"] == "abstention_or_missing_value")
    inv = sum(1 for row in invalid if row["failure_class"] == "invalid_predicted_label")
    parts.append(
        f"Outside scored metrics: {abst} abstentions/null outputs and {inv} schema-invalid labels "
        f"(mostly incomplete cluster surfaces and unsupported per-hour rates). "
        f"These are excluded from the 281-record denominator but are full failures operationally."
    )
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", type=Path)
    parser.add_argument(
        "--split-file",
        type=Path,
        default=Path("data/splits/gan_2026_splits.json"),
    )
    parser.add_argument(
        "--split-name",
        default="gan_2026_fixed_v1:validation",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Defaults to <run_dir>/analysis",
    )
    parser.add_argument(
        "--markdown",
        type=Path,
        default=None,
        help="Optional markdown output path",
    )
    args = parser.parse_args()

    analysis = analyze_run(
        run_dir=args.run_dir,
        split_file=args.split_file,
        split_name=args.split_name,
    )
    output_dir = args.output_dir or (args.run_dir / "analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "summary.json").write_text(
        json.dumps(analysis["summary"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "records.jsonl").open("w", encoding="utf-8") as handle:
        for row in analysis["rows"]:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    config = json.loads((args.run_dir / "config.json").read_text(encoding="utf-8"))
    experiment_id = config.get("experiment_id", args.run_dir.name)
    markdown_path = args.markdown or Path(
        f"docs/{experiment_id}_error_analysis.md"
    )
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(
        _render_markdown(analysis, experiment_id),
        encoding="utf-8",
    )
    print(f"Wrote {output_dir / 'summary.json'}")
    print(f"Wrote {output_dir / 'records.jsonl'}")
    print(f"Wrote {markdown_path}")


if __name__ == "__main__":
    main()

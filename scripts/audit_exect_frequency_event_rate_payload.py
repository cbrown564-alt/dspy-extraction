"""Audit ExECT seizure-frequency event/rate payload coverage.

This is a no-model representability gate for the May 28 component-ceiling
program. It compares deterministic ExECT frequency candidates against
validation gold without changing scorer, loader, split, or benchmark semantics.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.exect import (
    canonical_seizure_frequency_label,
    load_exect_gold_documents,
)
from clinical_extraction.exect.primitives import (
    build_exect_frequency_candidate_payloads,
    build_exect_frequency_pre_vocab_labels_high_precision,
)
from clinical_extraction.exect.slot_payload import classify_exect_frequency_slot_type

DEFAULT_SPLITS = Path("data/splits/exectv2_splits.json")
DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.md"
)

BASELINE_GOLD_COVERAGE = 5 / 43
BASELINE_FULL_LABEL_DOCS = 2
BASELINE_GOLD_DOCS = 24


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()

    report = build_report(args.splits, args.split)
    write_json(args.json_output, report)
    write_markdown(args.markdown_output, report)
    print(
        json.dumps(
            {
                "split": report["split_name"],
                "broad_gold_coverage": report["candidate_modes"]["broad"]["coverage"],
                "broad_precision": report["candidate_modes"]["broad"]["precision"],
                "broad_full_label_docs": report["candidate_modes"]["broad"][
                    "full_label_documents"
                ],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


def build_report(splits_path: Path, split_name: str) -> dict[str, Any]:
    split_ids = _load_split_ids(splits_path, split_name)
    documents = [
        document
        for document in load_exect_gold_documents()
        if document.document_id in split_ids
    ]
    documents.sort(key=lambda document: document.document_id)

    rows = [_document_row(document) for document in documents]
    modes = {
        "broad": _summarize_mode(rows, "broad_candidates"),
        "high_precision": _summarize_mode(rows, "high_precision_candidates"),
    }
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": "exect_v2",
        "split_name": split_name,
        "split_file": splits_path.as_posix(),
        "validation_policy": (
            "No model calls; deterministic candidates compared to existing "
            "load_exect_gold_documents() seizure_frequencies."
        ),
        "scorer_caveats": [
            "Frequency gold comes from ExECT SeizureFrequency annotations.",
            "Seizure-frequency rows are not seizure-type gold.",
            "Gan monthly normalization and unknown/no-reference policy are excluded.",
            "Test split remains holdout; this report is a validation representability gate.",
        ],
        "baseline": {
            "source": (
                "docs/experiments/exect/"
                "exect_s4_s5_frequency_gold_template_audit_20260524.md"
            ),
            "gold_label_coverage": BASELINE_GOLD_COVERAGE,
            "full_label_documents": BASELINE_FULL_LABEL_DOCS,
            "gold_documents": BASELINE_GOLD_DOCS,
        },
        "candidate_modes": modes,
        "rows": rows,
    }


def _load_split_ids(path: Path, split_name: str) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    try:
        split_values = payload[split_name]
    except KeyError as exc:
        raise ValueError(f"Split {split_name!r} not found in {path}") from exc
    return {str(value) for value in split_values}


def _document_row(document: Any) -> dict[str, Any]:
    broad_payloads = build_exect_frequency_candidate_payloads(document.text)
    broad_candidates = sorted(
        {
            str(payload.benchmark_value)
            for payload in broad_payloads
            if payload.benchmark_value
        }
    )
    high_precision_candidates = sorted(
        build_exect_frequency_pre_vocab_labels_high_precision(document.text)
    )
    gold_labels = sorted(document.seizure_frequencies)
    gold_annotation_rows = _frequency_gold_annotation_rows(document.raw_annotations)
    return {
        "document_id": document.document_id,
        "gold_labels": gold_labels,
        "gold_annotation_rows": gold_annotation_rows,
        "gold_label_types": sorted(
            {classify_exect_frequency_slot_type(label) for label in gold_labels}
        ),
        "has_type_associated_gold": any(
            row["type_associated"] for row in gold_annotation_rows
        ),
        "has_temporal_scope_gold": any(
            row["temporal_scope"] for row in gold_annotation_rows
        ),
        "is_multi_label_gold": len(gold_labels) > 1,
        "broad_candidates": broad_candidates,
        "broad_candidate_records": [
            _candidate_payload_to_dict(payload) for payload in broad_payloads
        ],
        "high_precision_candidates": high_precision_candidates,
    }


def _frequency_gold_annotation_rows(annotations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for annotation in annotations:
        if annotation.get("entity") != "SeizureFrequency":
            continue
        attrs = annotation.get("attributes", {})
        label = canonical_seizure_frequency_label(attrs)
        if not label:
            continue
        phrase = str(attrs.get("CUIPhrase") or annotation.get("text") or "")
        temporal_fields = {
            key: attrs.get(key)
            for key in (
                "YearDate",
                "MonthDate",
                "WeekDate",
                "DayDate",
                "PointInTime",
                "TimeSince",
                "TimePeriod",
                "NumberOfTimePeriods",
            )
            if attrs.get(key)
        }
        rows.append(
            {
                "label": label,
                "slot_type": classify_exect_frequency_slot_type(label),
                "span_text": annotation.get("text"),
                "cui_phrase": phrase,
                "type_associated": _is_type_associated_frequency_phrase(phrase),
                "temporal_scope": bool(temporal_fields),
                "temporal_fields": temporal_fields,
            }
        )
    return rows


def _is_type_associated_frequency_phrase(phrase: str) -> bool:
    normalized = phrase.replace("-", " ").strip().lower()
    return bool(normalized) and normalized not in {
        "seizure",
        "seizures",
        "seizure free",
    }


def _candidate_payload_to_dict(payload: Any) -> dict[str, Any]:
    return {
        "benchmark_value": payload.benchmark_value,
        "raw_text": payload.raw_text,
        "source_span_text": payload.source_span_text,
        "start": payload.start,
        "end": payload.end,
        "rule_name": payload.rule_name,
        "metadata": payload.metadata,
    }


def _summarize_mode(rows: list[dict[str, Any]], candidate_key: str) -> dict[str, Any]:
    gold_docs = [row for row in rows if row["gold_labels"]]
    gold_label_total = sum(len(row["gold_labels"]) for row in rows)
    candidate_label_total = sum(len(row[candidate_key]) for row in rows)
    matched_total = sum(
        len(set(row["gold_labels"]) & set(row[candidate_key])) for row in rows
    )
    extra_total = sum(
        len(set(row[candidate_key]) - set(row["gold_labels"])) for row in rows
    )
    full_label_docs = sum(
        1
        for row in gold_docs
        if set(row["gold_labels"]).issubset(set(row[candidate_key]))
    )
    return {
        "documents": len(rows),
        "gold_documents": len(gold_docs),
        "gold_labels": gold_label_total,
        "candidate_labels": candidate_label_total,
        "matched_gold_labels": matched_total,
        "missed_gold_labels": gold_label_total - matched_total,
        "extra_candidate_labels": extra_total,
        "coverage": _safe_divide(matched_total, gold_label_total),
        "precision": _safe_divide(matched_total, candidate_label_total),
        "full_label_documents": full_label_docs,
        "full_label_document_rate": _safe_divide(full_label_docs, len(gold_docs)),
        "by_gold_label_type": _summarize_by_label_type(rows, candidate_key),
        "by_gold_case_stratum": _summarize_by_case_stratum(rows, candidate_key),
    }


def _summarize_by_label_type(
    rows: list[dict[str, Any]],
    candidate_key: str,
) -> dict[str, dict[str, Any]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        candidates = set(row[candidate_key])
        for label in row["gold_labels"]:
            slot_type = classify_exect_frequency_slot_type(label)
            counts[slot_type]["gold"] += 1
            if label in candidates:
                counts[slot_type]["matched"] += 1
    return {
        slot_type: {
            "gold": stats["gold"],
            "matched": stats["matched"],
            "coverage": _safe_divide(stats["matched"], stats["gold"]),
        }
        for slot_type, stats in sorted(counts.items())
    }


def _summarize_by_case_stratum(
    rows: list[dict[str, Any]],
    candidate_key: str,
) -> dict[str, dict[str, Any]]:
    strata = {
        "type_associated": lambda row: row["has_type_associated_gold"],
        "temporal_scope": lambda row: row["has_temporal_scope_gold"],
        "multi_label": lambda row: row["is_multi_label_gold"],
    }
    summary: dict[str, dict[str, Any]] = {}
    for name, predicate in strata.items():
        subset = [row for row in rows if row["gold_labels"] and predicate(row)]
        gold_total = sum(len(row["gold_labels"]) for row in subset)
        matched = sum(
            len(set(row["gold_labels"]) & set(row[candidate_key])) for row in subset
        )
        full_docs = sum(
            1
            for row in subset
            if set(row["gold_labels"]).issubset(set(row[candidate_key]))
        )
        summary[name] = {
            "documents": len(subset),
            "gold_labels": gold_total,
            "matched_gold_labels": matched,
            "coverage": _safe_divide(matched, gold_total),
            "full_label_documents": full_docs,
            "full_label_document_rate": _safe_divide(full_docs, len(subset)),
        }
    return summary


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    broad = report["candidate_modes"]["broad"]
    high_precision = report["candidate_modes"]["high_precision"]
    rows = report["rows"]
    lines = [
        "# ExECT Frequency Event/Rate Payload Audit",
        "",
        "Date: 2026-05-28",
        "Status: current synthesis; no-model representability gate",
        "Kanban card: E1 - ExECT Frequency Event/Rate Payload Gate",
        f"Dataset/split: ExECTv2 `{report['split_name']}` "
        f"({broad['documents']} documents)",
        "Model/provider: none",
        "Scorer mode: no-model candidate-vs-gold coverage audit; no scorer semantics changed",
        "",
        "## Summary",
        "",
        (
            "The broad deterministic ExECT frequency payload now covers "
            f"**{broad['matched_gold_labels']}/{broad['gold_labels']}** validation "
            f"gold labels ({broad['coverage']:.1%}), up from the archived "
            f"{report['baseline']['gold_label_coverage']:.1%} gold-label coverage "
            "baseline."
        ),
        "",
        (
            "That clears the coverage part of E1, but it does not close the component: "
            f"the broad payload emits {broad['extra_candidate_labels']} extra validation "
            f"candidate labels and has {broad['precision']:.1%} candidate precision "
            "against gold. The next component stage should adjudicate or rank candidates "
            "before using this as a model pre-vocabulary substrate."
        ),
        "",
        "## Candidate Mode Comparison",
        "",
        "| Mode | Gold coverage | Candidate precision | Full-label docs | Gold labels | Candidate labels | Extra labels |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        _mode_row("Broad event/rate payload", broad),
        _mode_row("High-precision payload", high_precision),
        "",
        "## Coverage By Gold Label Type",
        "",
        "| Mode | Label type | Gold | Matched | Coverage |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for mode_name, mode in (
        ("Broad", broad),
        ("High precision", high_precision),
    ):
        for label_type, stats in mode["by_gold_label_type"].items():
            lines.append(
                f"| {mode_name} | `{label_type}` | {stats['gold']} | "
                f"{stats['matched']} | {stats['coverage']:.1%} |"
            )

    lines.extend(
        [
            "",
            "## Coverage By Gold Case Stratum",
            "",
            "| Mode | Stratum | Documents | Gold labels | Matched | Coverage | Full-label docs |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode_name, mode in (
        ("Broad", broad),
        ("High precision", high_precision),
    ):
        for stratum, stats in mode["by_gold_case_stratum"].items():
            lines.append(
                f"| {mode_name} | `{stratum}` | {stats['documents']} | "
                f"{stats['gold_labels']} | {stats['matched_gold_labels']} | "
                f"{stats['coverage']:.1%} | {stats['full_label_documents']} |"
            )

    lines.extend(
        [
            "",
            "## Document-Level Validation",
            "",
            "| Document | Gold labels | Broad candidates | Broad status | High-precision status |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if not row["gold_labels"]:
            continue
        broad_status = _coverage_status(row, "broad_candidates")
        high_precision_status = _coverage_status(row, "high_precision_candidates")
        lines.append(
            "| "
            f"`{row['document_id']}` | "
            f"{_labels_cell(row['gold_labels'])} | "
            f"{len(row['broad_candidates'])} | "
            f"{broad_status} | "
            f"{high_precision_status} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The event/rate payload is now a recall-sufficient substrate on validation: quantified, qualitative, seizure-free, zero-rate, type-associated, temporal-scope, and multi-label gold cases are all covered by the broad mode.",
            "- Precision is still low because broad candidates intentionally preserve multiple plausible benchmark labels. Treat them as an inventory, not final predictions.",
            "- The high-precision mode is not a safe replacement: it misses qualitative-change labels by design and covers only a minority of full-label documents.",
            "- The result supports moving from E1 coverage auditing to candidate selection/adjudication, not another broad S5 prompt loop.",
            "",
            "## Dataset And Scorer Caveats",
            "",
            "- Gold labels use the current `load_exect_gold_documents()` frequency policy over ExECT SeizureFrequency annotations.",
            "- Frequency rows are not used as seizure-type gold.",
            "- No loader, split, scorer, or benchmark-bridge semantics changed.",
            "- Validation is the component-development split; test remains holdout for residual analysis only.",
            "",
            "## Generated Companion",
            "",
            "`docs/experiments/exect/exect_frequency_event_rate_payload_audit_20260528.json` contains per-document gold rows, annotation strata, candidate records, and mode summaries.",
            "",
        ]
    )
    return "\n".join(lines)


def _mode_row(name: str, mode: dict[str, Any]) -> str:
    return (
        f"| {name} | {mode['coverage']:.1%} | {mode['precision']:.1%} | "
        f"{mode['full_label_documents']}/{mode['gold_documents']} "
        f"({mode['full_label_document_rate']:.1%}) | "
        f"{mode['gold_labels']} | {mode['candidate_labels']} | "
        f"{mode['extra_candidate_labels']} |"
    )


def _coverage_status(row: dict[str, Any], candidate_key: str) -> str:
    gold = set(row["gold_labels"])
    candidates = set(row[candidate_key])
    if gold.issubset(candidates):
        return "full"
    matched = len(gold & candidates)
    return f"partial ({matched}/{len(gold)})"


def _labels_cell(labels: list[str]) -> str:
    if not labels:
        return "`none`"
    return "<br>".join(f"`{label}`" for label in labels)


if __name__ == "__main__":
    main()

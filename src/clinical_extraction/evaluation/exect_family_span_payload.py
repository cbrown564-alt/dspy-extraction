"""Audit ExECT typed family-span payload coverage."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.exect import canonical_seizure_frequency_label
from clinical_extraction.datasets.exect import is_comorbidity_patient_history
from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.exect.family_spans import (
    FAMILY_ORDER,
    build_exect_family_span_payloads,
    family_span_context,
)

DEFAULT_SPLITS = Path("data/splits/exectv2_splits.json")
DEFAULT_JSON_OUTPUT = Path(
    "docs/experiments/exect/exect_family_span_payload_audit_20260528.json"
)
DEFAULT_MARKDOWN_OUTPUT = Path(
    "docs/experiments/exect/exect_family_span_payload_audit_20260528.md"
)
CAP_SLICE_FAMILIES = (
    "diagnosis_problem",
    "seizure",
    "medication",
    "investigation",
)


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
                "documents": report["candidate_summary"]["documents"],
                "span_count": report["candidate_summary"]["span_count"],
                "cap_slice_char_ratio": report["cap_slice_prompt_comparison"][
                    "family_span_char_ratio"
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
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset": "exect_v2",
        "split_name": split_name,
        "split_file": splits_path.as_posix(),
        "validation_policy": (
            "No model calls; deterministic family spans compared to audited "
            "annotation evidence offsets."
        ),
        "scorer_caveats": [
            "Family spans are document-geometry hints, not benchmark labels.",
            "Coverage uses annotation offsets and does not change scorer semantics.",
            "Section-aware prompt routing remains a rejected arm; this tests typed span geometry.",
            "Validation is the component-development split; test remains holdout.",
        ],
        "candidate_summary": _candidate_summary(rows),
        "gold_coverage_by_family": _gold_coverage_by_family(rows),
        "false_family_span_counts": _false_family_span_counts(rows),
        "cap_slice_prompt_comparison": _cap_slice_prompt_comparison(documents[:25]),
        "rows": rows,
    }


def _document_row(document: Any) -> dict[str, Any]:
    spans = build_exect_family_span_payloads(document.text)
    gold = [
        item
        for item in (
            _gold_annotation_record(annotation, document.text)
            for annotation in document.raw_annotations
        )
        if item is not None
    ]
    return {
        "document_id": document.document_id,
        "family_spans": [_span_to_dict(span) for span in spans],
        "gold_annotations": gold,
        "coverage": _document_coverage(spans, gold),
        "false_family_spans": _document_false_family_spans(spans, gold),
    }


def _gold_annotation_record(
    annotation: dict[str, Any],
    document_text: str,
) -> dict[str, Any] | None:
    family = _annotation_family(annotation)
    if family is None:
        return None
    start, end = _annotation_offsets(annotation, document_text)
    if start is None or end is None:
        return None
    return {
        "family": family,
        "entity": annotation.get("entity"),
        "text": str(annotation.get("text") or "").replace("-", " "),
        "start": start,
        "end": end,
    }


def _annotation_family(annotation: dict[str, Any]) -> str | None:
    entity = annotation.get("entity")
    attrs = annotation.get("attributes", {})
    if entity == "Diagnosis":
        if not _is_affirmed_high_certainty(attrs):
            return None
        category = attrs.get("DiagCategory")
        if category == "Epilepsy":
            return "diagnosis_problem"
        if category in {"MultipleSeizures", "SingleSeizure"}:
            return "seizure"
        return None
    if entity == "Prescription":
        return "medication"
    if entity == "Investigations":
        return "investigation"
    if entity == "SeizureFrequency":
        if canonical_seizure_frequency_label(attrs):
            return "frequency"
        return None
    if entity == "PatientHistory":
        if is_comorbidity_patient_history(annotation.get("text"), attrs):
            return "history_background"
        return None
    if entity in {"BirthHistory", "Onset", "EpilepsyCause", "WhenDiagnosed"}:
        if _is_affirmed_high_certainty(attrs):
            return "history_background"
    return None


def _candidate_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_family = Counter()
    for row in rows:
        by_family.update(span["family"] for span in row["family_spans"])
    return {
        "documents": len(rows),
        "span_count": sum(by_family.values()),
        "by_family": dict(sorted(by_family.items())),
    }


def _gold_coverage_by_family(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        for family, covered in row["coverage"]:
            counts[family]["gold_annotations"] += 1
            if covered:
                counts[family]["covered_annotations"] += 1
    return {
        family: {
            "gold_annotations": stats["gold_annotations"],
            "covered_annotations": stats["covered_annotations"],
            "missed_annotations": (
                stats["gold_annotations"] - stats["covered_annotations"]
            ),
            "coverage": _safe_divide(
                stats["covered_annotations"],
                stats["gold_annotations"],
            ),
        }
        for family, stats in sorted(counts.items())
    }


def _false_family_span_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter()
    for row in rows:
        counts.update(item["family"] for item in row["false_family_spans"])
    return dict(sorted(counts.items()))


def _cap_slice_prompt_comparison(documents: list[Any]) -> dict[str, Any]:
    full_chars = sum(len(document.text) for document in documents)
    span_chars = sum(
        len(
            family_span_context(
                document.text,
                families=CAP_SLICE_FAMILIES,
            )
        )
        for document in documents
    )
    rows = [_document_row(document) for document in documents]
    relevant = [
        (family, covered)
        for row in rows
        for family, covered in row["coverage"]
        if family in CAP_SLICE_FAMILIES
    ]
    covered = sum(1 for _family, is_covered in relevant if is_covered)
    return {
        "documents": len(documents),
        "families": list(CAP_SLICE_FAMILIES),
        "full_note_chars": full_chars,
        "family_span_chars": span_chars,
        "family_span_char_ratio": _safe_divide(span_chars, full_chars),
        "gold_annotations": len(relevant),
        "covered_gold_annotations": covered,
        "gold_coverage": _safe_divide(covered, len(relevant)),
    }


def _document_coverage(
    spans: list[Any],
    gold: list[dict[str, Any]],
) -> list[tuple[str, bool]]:
    results: list[tuple[str, bool]] = []
    for item in gold:
        family = item["family"]
        covered = any(
            str(span.normalized_value) == family
            and span.start is not None
            and span.end is not None
            and _covers_annotation(span.start, span.end, item["start"], item["end"])
            for span in spans
        )
        results.append((family, covered))
    return results


def _document_false_family_spans(
    spans: list[Any],
    gold: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    false_spans: list[dict[str, Any]] = []
    for span in spans:
        family = str(span.normalized_value)
        overlapping = [
            item
            for item in gold
            if span.start is not None
            and span.end is not None
            and _overlaps(span.start, span.end, item["start"], item["end"])
        ]
        if not overlapping:
            continue
        if any(item["family"] == family for item in overlapping):
            continue
        false_spans.append(
            {
                "family": family,
                "start": span.start,
                "end": span.end,
                "source_span_text": span.source_span_text,
                "overlapping_gold_families": sorted(
                    {item["family"] for item in overlapping}
                ),
            }
        )
    return false_spans


def _span_to_dict(span: Any) -> dict[str, Any]:
    return {
        "family": span.normalized_value,
        "source_span_text": span.source_span_text,
        "start": span.start,
        "end": span.end,
        "rule_name": span.rule_name,
        "metadata": span.metadata,
    }


def _annotation_offsets(
    annotation: dict[str, Any],
    document_text: str,
) -> tuple[int | None, int | None]:
    try:
        start = int(annotation.get("start_index"))
        end = int(annotation.get("end_index"))
    except (TypeError, ValueError):
        return None, None
    if start < 0 or end < start:
        return None, None
    end = min(end, len(document_text))
    while start < end and document_text[start].isspace():
        start += 1
    while end > start and document_text[end - 1].isspace():
        end -= 1
    return start, end


def _is_affirmed_high_certainty(attrs: dict[str, Any]) -> bool:
    try:
        certainty = int(attrs.get("Certainty", 0))
    except (TypeError, ValueError):
        certainty = 0
    return attrs.get("Negation") == "Affirmed" and certainty >= 4


def _overlaps(left_start: int, left_end: int, right_start: int, right_end: int) -> bool:
    return left_start < right_end and right_start < left_end


def _covers_annotation(
    span_start: int,
    span_end: int,
    annotation_start: int,
    annotation_end: int,
) -> bool:
    if span_start <= annotation_start and span_end >= annotation_end:
        return True
    overlap_start = max(span_start, annotation_start)
    overlap_end = min(span_end, annotation_end)
    overlap = max(0, overlap_end - overlap_start)
    annotation_length = max(1, annotation_end - annotation_start)
    return (overlap / annotation_length) >= 0.5


def _load_split_ids(path: Path, split_name: str) -> set[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    try:
        split_values = payload[split_name]
    except KeyError as exc:
        raise ValueError(f"Split {split_name!r} not found in {path}") from exc
    return {str(value) for value in split_values}


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    cap = report["cap_slice_prompt_comparison"]
    lines = [
        "# ExECT Family-Span Payload Audit",
        "",
        "Date: 2026-05-28",
        "Status: current synthesis; no-model representability gate",
        "Kanban card: E4 - Family-Span Payload",
        f"Dataset/split: ExECTv2 `{report['split_name']}` "
        f"({report['candidate_summary']['documents']} documents)",
        "Model/provider: none",
        "Scorer mode: no-model span-vs-gold evidence coverage audit; no scorer semantics changed",
        "",
        "## Summary",
        "",
        (
            "The typed `exect.sections.family_spans.v1` payload emits "
            f"{report['candidate_summary']['span_count']} validation spans across "
            "diagnosis/problem, seizure, medication, investigation, "
            "history/background, frequency, and plan/follow-up families."
        ),
        "",
        (
            "On the first 25 validation documents, the S1-plus-investigation "
            "family-span context uses "
            f"{cap['family_span_chars']}/{cap['full_note_chars']} characters "
            f"({cap['family_span_char_ratio']:.1%} of the full-note prompt substrate) "
            f"while covering {cap['covered_gold_annotations']}/{cap['gold_annotations']} "
            f"gold annotations ({cap['gold_coverage']:.1%})."
        ),
        "",
        "## Gold Evidence Coverage By Family",
        "",
        "| Family | Gold annotations | Covered | Coverage |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family in FAMILY_ORDER:
        stats = report["gold_coverage_by_family"].get(family)
        if stats is None:
            continue
        lines.append(
            f"| `{family}` | {stats['gold_annotations']} | "
            f"{stats['covered_annotations']} | {stats['coverage']:.1%} |"
        )
    lines.extend(
        [
            "",
            "## False-Family Span Count",
            "",
            "| Span family | Count |",
            "| --- | ---: |",
        ]
    )
    false_counts = report["false_family_span_counts"]
    if false_counts:
        for family, count in false_counts.items():
            lines.append(f"| `{family}` | {count} |")
    else:
        lines.append("| `none` | 0 |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The family-span payload is a typed document-geometry substrate, not a promoted section-filtering arm.",
            "- Coverage and false-family counts should gate any future family-span prompting run against a full-note baseline.",
            "- Plan/follow-up spans are retained as routing context but have no current benchmark gold family in this audit.",
            "",
            "## Dataset And Scorer Caveats",
            "",
            "- Gold evidence coverage uses existing annotation offsets and audited inclusion policy for diagnosis and seizure-type rows.",
            "- No loader, split, scorer, or benchmark bridge semantics changed.",
            "- Validation is the component-development split; test remains holdout for residual analysis only.",
            "",
            "## Generated Companion",
            "",
            "`docs/experiments/exect/exect_family_span_payload_audit_20260528.json` contains per-document spans, gold annotation coverage, and false-family rows.",
            "",
        ]
    )
    return "\n".join(lines)


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


if __name__ == "__main__":
    main()

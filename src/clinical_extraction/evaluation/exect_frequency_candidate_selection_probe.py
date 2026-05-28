"""Export the E10 ExECT frequency candidate-selection split probe."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.evaluation.exect import score_exect_s4_document
from clinical_extraction.evaluation.exect_frequency_event_rate_payload import (
    DEFAULT_JSON_OUTPUT as DEFAULT_E1_PAYLOAD,
    build_report as build_e1_report,
)
from clinical_extraction.paths import resolve_run_directory
from clinical_extraction.schemas import (
    DocumentPrediction,
    EvidenceSpan,
    ExectGoldDocument,
    ExtractedValue,
    PredictionSet,
)

DEFAULT_SPLITS = Path("data/splits/exectv2_splits.json")
DEFAULT_OUTPUT_JSON = Path(
    "docs/experiments/exect/"
    "exect_frequency_candidate_selection_probe_20260528.json"
)
DEFAULT_OUTPUT_MARKDOWN = Path(
    "docs/experiments/exect/"
    "exect_frequency_candidate_selection_probe_20260528.md"
)
DEFAULT_S4_RUN = "exect_s4_validation_full_gpt4_1_mini_20260520T071248Z"
DEFAULT_S5_RUN = (
    "exect_s5_frequency_pre_vocab_am_guard_frequency_verify_v2b_full_gpt4_1_mini_"
    "20260524T211229Z"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--splits", type=Path, default=DEFAULT_SPLITS)
    parser.add_argument("--split", default="validation")
    parser.add_argument("--e1-payload", type=Path, default=DEFAULT_E1_PAYLOAD)
    parser.add_argument("--s4-run", default=DEFAULT_S4_RUN)
    parser.add_argument("--s5-run", default=DEFAULT_S5_RUN)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_OUTPUT_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_OUTPUT_MARKDOWN)
    args = parser.parse_args()

    report = build_report(
        splits_path=args.splits,
        split_name=args.split,
        e1_payload_path=args.e1_payload,
        s4_run=args.s4_run,
        s5_run=args.s5_run,
    )
    write_json(args.json_output, report)
    write_markdown(args.markdown_output, report)
    print(
        json.dumps(
            {
                "split": report["split_name"],
                "broad_payload_f1": report["surface_summaries"][
                    "broad_event_rate_payload"
                ]["f1"],
                "oracle_f1": report["surface_summaries"][
                    "candidate_constrained_oracle"
                ]["f1"],
                "s5_frequency_f1": report["surface_summaries"][
                    "s5_gpt_frequency_surface"
                ]["f1"],
                "json_output": args.json_output.as_posix(),
                "markdown_output": args.markdown_output.as_posix(),
            },
            indent=2,
        )
    )


def build_report(
    *,
    splits_path: Path,
    split_name: str,
    e1_payload_path: Path,
    s4_run: str,
    s5_run: str,
) -> dict[str, Any]:
    e1_payload = _load_or_build_e1_payload(e1_payload_path, splits_path, split_name)
    gold_by_id = _gold_rows_from_e1_payload(e1_payload)

    surfaces = {
        "broad_event_rate_payload": {
            "label": "Broad event/rate payload",
            "classification": "diagnostic coverage substrate",
            "model_provider": "none",
            "run_id": None,
            "prediction_set": _prediction_set_from_e1_candidates(
                e1_payload, "broad_candidates", "e10_broad_event_rate_payload"
            ),
        },
        "high_precision_payload": {
            "label": "High-precision payload",
            "classification": "diagnostic narrowed substrate",
            "model_provider": "none",
            "run_id": None,
            "prediction_set": _prediction_set_from_e1_candidates(
                e1_payload,
                "high_precision_candidates",
                "e10_high_precision_payload",
            ),
        },
        "candidate_constrained_oracle": {
            "label": "Candidate-constrained gold oracle",
            "classification": "oracle upper bound / not deployable",
            "model_provider": "none",
            "run_id": None,
            "prediction_set": _oracle_prediction_set_from_e1_payload(e1_payload),
        },
        "s4_gpt_frequency_surface": {
            "label": "Existing S4 GPT frequency surface",
            "classification": "existing S4 diagnostic surface",
            "model_provider": "GPT 4.1-mini / OpenAI",
            "run_id": s4_run,
            "prediction_set": _frequency_only_prediction_set(_load_prediction_set(s4_run)),
        },
        "s5_gpt_frequency_surface": {
            "label": "Existing S5 GPT frequency surface",
            "classification": "existing stacked operational surface",
            "model_provider": "GPT 4.1-mini / OpenAI",
            "run_id": s5_run,
            "prediction_set": _frequency_only_prediction_set(_load_prediction_set(s5_run)),
        },
    }

    summaries: dict[str, Any] = {}
    error_attribution: dict[str, Any] = {}
    for key, surface in surfaces.items():
        summary, attribution = _score_frequency_surface(
            surface["prediction_set"],
            gold_by_id=gold_by_id,
            e1_rows=e1_payload["rows"],
        )
        summaries[key] = {
            **summary,
            "label": surface["label"],
            "classification": surface["classification"],
            "model_provider": surface["model_provider"],
            "run_id": surface["run_id"],
        }
        error_attribution[key] = attribution

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "kanban_card": "E10 - ExECT Frequency Candidate Selection Split",
        "dataset": "exect_v2",
        "split_name": split_name,
        "split_file": splits_path.as_posix(),
        "component": "seizure_frequency candidate selection and benchmark-label construction",
        "scorer_mode": "seizure-frequency slice of exect_s4_field_family_deterministic_v1",
        "bridge_normalization_policy": (
            "Current ExECT frequency benchmark-facing labels from "
            "load_exect_gold_documents(); no Gan monthly normalization."
        ),
        "source_artifacts": {
            "e1_payload": e1_payload_path.as_posix(),
            "s4_run": s4_run,
            "s5_run": s5_run,
        },
        "surface_summaries": summaries,
        "extra_candidate_strata": {
            "broad_event_rate_payload": _extra_candidate_strata(
                e1_payload, "broad_candidate_records"
            ),
            "high_precision_payload": _extra_candidate_strata_from_labels(
                e1_payload, "high_precision_candidates"
            ),
        },
        "error_attribution": error_attribution,
        "decision": {
            "payload_coverage": "broad payload covers all validation gold labels",
            "candidate_selection": "open; broad payload precision is too low for direct promotion",
            "label_construction": (
                "not the main blocker for payload rows: oracle selection over broad "
                "candidate labels reaches perfect validation F1"
            ),
            "next_action": (
                "Design a candidate adjudicator/ranker against the broad payload before "
                "another stacked prompt or full-validation promotion."
            ),
        },
        "caveats": [
            "This is a validation-split component probe; test remains holdout for residual analysis only.",
            "The candidate-constrained oracle uses gold labels and is not deployable.",
            "S4 and S5 comparison runs are archived provenance artifacts resolved by explicit opt-in.",
            "No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, or prompt changes were made.",
            "Frequency rows are not seizure-type gold; type-associated frequency rows stay within the frequency component.",
        ],
    }


def _load_or_build_e1_payload(
    path: Path,
    splits_path: Path,
    split_name: str,
) -> dict[str, Any]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return build_e1_report(splits_path, split_name)


def _gold_rows_from_e1_payload(payload: dict[str, Any]) -> dict[str, ExectGoldDocument]:
    return {
        row["document_id"]: ExectGoldDocument(
            document_id=row["document_id"],
            text="",
            seizure_frequencies=list(row["gold_labels"]),
        )
        for row in payload["rows"]
    }


def _prediction_set_from_e1_candidates(
    payload: dict[str, Any],
    candidate_key: str,
    schema_level: str,
) -> PredictionSet:
    predictions = []
    for row in payload["rows"]:
        record_by_label = {
            record["benchmark_value"]: record
            for record in row.get("broad_candidate_records", [])
            if record.get("benchmark_value")
        }
        values = [
            _frequency_value_from_candidate(
                row["document_id"], label, record_by_label.get(label)
            )
            for label in row[candidate_key]
        ]
        predictions.append(
            DocumentPrediction(
                document_id=row["document_id"],
                dataset="exect_v2",
                schema_level=schema_level,
                values=values,
                metadata={"component": "seizure_frequency"},
            )
        )
    return PredictionSet(
        dataset="exect_v2",
        schema_level=schema_level,
        predictions=predictions,
        metadata={"program_variant": schema_level, "model_provider": "none"},
    )


def _oracle_prediction_set_from_e1_payload(payload: dict[str, Any]) -> PredictionSet:
    predictions = []
    for row in payload["rows"]:
        broad = set(row["broad_candidates"])
        values = [
            _frequency_value_from_candidate(row["document_id"], label, None)
            for label in row["gold_labels"]
            if label in broad
        ]
        predictions.append(
            DocumentPrediction(
                document_id=row["document_id"],
                dataset="exect_v2",
                schema_level="e10_candidate_constrained_oracle",
                values=values,
                metadata={"component": "seizure_frequency"},
            )
        )
    return PredictionSet(
        dataset="exect_v2",
        schema_level="e10_candidate_constrained_oracle",
        predictions=predictions,
        metadata={"program_variant": "e10_candidate_constrained_oracle"},
    )


def _frequency_value_from_candidate(
    document_id: str,
    label: str,
    record: dict[str, Any] | None,
) -> ExtractedValue:
    evidence = []
    if record and record.get("source_span_text"):
        evidence.append(
            EvidenceSpan(
                document_id=document_id,
                text=record["source_span_text"],
                start=record.get("start"),
                end=record.get("end"),
            )
        )
    return ExtractedValue(
        field_name="seizure_frequency",
        raw_value=label,
        normalized_value=label,
        evidence=evidence,
        temporality="not_applicable",
        negation="affirmed",
        metadata={"source": "e10_frequency_candidate_surface"},
    )


def _load_prediction_set(run_id: str) -> PredictionSet:
    run_dir = resolve_run_directory(run_id, include_archive=True)
    payload = json.loads((run_dir / "predictions.json").read_text(encoding="utf-8"))
    return PredictionSet.model_validate(payload)


def _frequency_only_prediction_set(prediction_set: PredictionSet) -> PredictionSet:
    predictions = []
    schema_level = f"{prediction_set.schema_level}_frequency_only"
    for prediction in prediction_set.predictions:
        values = [
            value
            for value in prediction.values
            if value.field_name in {"seizure_frequency", "seizure_frequencies"}
        ]
        predictions.append(
            DocumentPrediction(
                document_id=prediction.document_id,
                dataset=prediction.dataset,
                schema_level=schema_level,
                values=values,
                quality_flags=prediction.quality_flags,
                metadata=prediction.metadata,
            )
        )
    return PredictionSet(
        dataset=prediction_set.dataset,
        schema_level=schema_level,
        predictions=predictions,
        metadata=prediction_set.metadata,
    )


def _score_frequency_surface(
    prediction_set: PredictionSet,
    *,
    gold_by_id: dict[str, ExectGoldDocument],
    e1_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    predictions_by_id = {
        prediction.document_id: prediction for prediction in prediction_set.predictions
    }
    tp = fp = fn = 0
    row_errors = []
    for document_id, gold in sorted(gold_by_id.items()):
        prediction = predictions_by_id.get(
            document_id,
            DocumentPrediction(
                document_id=document_id,
                dataset="exect_v2",
                schema_level=prediction_set.schema_level,
            ),
        )
        score = score_exect_s4_document(gold=gold, prediction=prediction)
        freq_score = score.field_scores["seizure_frequency"]
        tp += len(freq_score.true_positives)
        fp += len(freq_score.false_positives)
        fn += len(freq_score.false_negatives)
        if freq_score.false_positives or freq_score.false_negatives:
            row_errors.append(
                {
                    "document_id": document_id,
                    "false_positives": freq_score.false_positives,
                    "false_negatives": freq_score.false_negatives,
                    "predicted_values": freq_score.predicted_values,
                    "gold_values": freq_score.gold_values,
                    "categories": _error_categories(
                        document_id,
                        false_positives=freq_score.false_positives,
                        false_negatives=freq_score.false_negatives,
                        e1_rows=e1_rows,
                    ),
                }
            )
    summary = {
        "documents": len(gold_by_id),
        "gold_support": sum(
            len(gold.seizure_frequencies) for gold in gold_by_id.values()
        ),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": _precision(tp, fp),
        "recall": _recall(tp, fn),
        "f1": _f1(tp, fp, fn),
    }
    category_counts = Counter(
        category for residual in row_errors for category in residual["categories"]
    )
    return summary, {
        "row_count": len(row_errors),
        "category_counts": dict(sorted(category_counts.items())),
        "rows": row_errors,
    }


def _error_categories(
    document_id: str,
    *,
    false_positives: list[str],
    false_negatives: list[str],
    e1_rows: list[dict[str, Any]],
) -> list[str]:
    row = next(item for item in e1_rows if item["document_id"] == document_id)
    broad = set(row["broad_candidates"])
    high_precision = set(row["high_precision_candidates"])
    gold_types = {item["label"]: item["slot_type"] for item in row["gold_annotation_rows"]}
    record_by_label = {
        record["benchmark_value"]: record
        for record in row.get("broad_candidate_records", [])
        if record.get("benchmark_value")
    }
    categories = []
    for value in false_positives:
        if value in broad:
            source = _candidate_source(record_by_label.get(value))
            categories.append(f"fp:target_selection_extra_candidate:{source}")
        else:
            categories.append("fp:label_construction_not_in_broad_payload")
    for value in false_negatives:
        if value in high_precision:
            categories.append("fn:adjudication_missed_high_precision_candidate")
        elif value in broad:
            categories.append(
                f"fn:adjudication_missed_broad_candidate:{gold_types.get(value, 'unknown')}"
            )
        else:
            categories.append(
                f"fn:payload_coverage_gap:{gold_types.get(value, 'unknown')}"
            )
    return sorted(categories)


def _candidate_source(record: dict[str, Any] | None) -> str:
    if not record:
        return "unknown_source"
    metadata = record.get("metadata") or {}
    return str(metadata.get("candidate_source") or record.get("rule_name") or "unknown_source")


def _extra_candidate_strata(
    payload: dict[str, Any],
    record_key: str,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in payload["rows"]:
        gold = set(row["gold_labels"])
        for record in row.get(record_key, []):
            label = record.get("benchmark_value")
            if label and label not in gold:
                counts[_candidate_source(record)] += 1
    return dict(sorted(counts.items()))


def _extra_candidate_strata_from_labels(
    payload: dict[str, Any],
    candidate_key: str,
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for row in payload["rows"]:
        gold = set(row["gold_labels"])
        broad_record_by_label = {
            record["benchmark_value"]: record
            for record in row.get("broad_candidate_records", [])
            if record.get("benchmark_value")
        }
        for label in row.get(candidate_key, []):
            if label not in gold:
                counts[_candidate_source(broad_record_by_label.get(label))] += 1
    return dict(sorted(counts.items()))


def write_json(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(report), encoding="utf-8")


def render_markdown(report: dict[str, Any]) -> str:
    summaries = report["surface_summaries"]
    lines = [
        "# ExECT Frequency Candidate Selection Split",
        "",
        "Date: 2026-05-28",
        "Status: current synthesis; preregistered component probe",
        "Kanban card: E10 - ExECT Frequency Candidate Selection Split",
        f"Dataset/split: ExECTv2 `{report['split_name']}` "
        f"({summaries['broad_event_rate_payload']['documents']} documents)",
        "Model/provider: none for payload/oracle surfaces; GPT 4.1-mini / OpenAI for S4/S5 comparison surfaces",
        f"Scorer mode: `{report['scorer_mode']}`",
        "",
        "## Summary",
        "",
        (
            "The broad event/rate payload is recall-sufficient but not prediction-ready: "
            f"it scores **{summaries['broad_event_rate_payload']['recall']:.1%} recall** "
            f"and **{summaries['broad_event_rate_payload']['precision']:.1%} precision** "
            "when promoted directly as frequency predictions."
        ),
        "",
        (
            "A gold-constrained oracle over the same broad candidate set reaches "
            f"**{summaries['candidate_constrained_oracle']['f1']:.1%} F1**, so the "
            "remaining component work is candidate adjudication/target selection rather "
            "than payload coverage."
        ),
        "",
        "## Surface Comparison",
        "",
        "| Surface | Classification | Precision | Recall | F1 | TP | FP | FN |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key in (
        "broad_event_rate_payload",
        "high_precision_payload",
        "candidate_constrained_oracle",
        "s4_gpt_frequency_surface",
        "s5_gpt_frequency_surface",
    ):
        surface = summaries[key]
        lines.append(
            f"| {surface['label']} | {surface['classification']} | "
            f"{_fmt_pct(surface['precision'])} | {_fmt_pct(surface['recall'])} | "
            f"{_fmt_pct(surface['f1'])} | {surface['tp']} | {surface['fp']} | "
            f"{surface['fn']} |"
        )
    lines.extend(
        [
            "",
            "## Extra-Candidate Strata",
            "",
            "| Surface | Strata |",
            "| --- | --- |",
            (
                "| Broad event/rate payload | "
                f"{_format_category_counts(report['extra_candidate_strata']['broad_event_rate_payload'])} |"
            ),
            (
                "| High-precision payload | "
                f"{_format_category_counts(report['extra_candidate_strata']['high_precision_payload'])} |"
            ),
            "",
            "## Error Attribution",
            "",
            "| Surface | Error docs | Categories |",
            "| --- | ---: | --- |",
        ]
    )
    for key in (
        "high_precision_payload",
        "s4_gpt_frequency_surface",
        "s5_gpt_frequency_surface",
    ):
        attribution = report["error_attribution"][key]
        lines.append(
            f"| {summaries[key]['label']} | {attribution['row_count']} | "
            f"{_format_category_counts(attribution['category_counts'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Broad payload coverage is not a frequency ceiling because direct promotion creates many extra labels.",
            "- The high-precision payload is not safe as a replacement because it drops qualitative-change and seizure-free/zero-rate coverage.",
            "- S4/S5 model surfaces sit between direct-payload promotion and the oracle, which localizes remaining error to adjudication plus a smaller amount of label construction outside the broad payload.",
            "- The next E10 step should be an adjudicator/ranker comparison against this fixed broad payload, not another broad-stack prompt loop.",
            "",
            "## Reproducibility",
            "",
            f"- E1 payload: `{report['source_artifacts']['e1_payload']}`",
            f"- S4 comparison run: `{report['source_artifacts']['s4_run']}`",
            f"- S5 comparison run: `{report['source_artifacts']['s5_run']}`",
            "- No model calls, scorer changes, loader changes, split changes, benchmark bridge changes, or prompt changes were made.",
            "",
        ]
    )
    return "\n".join(lines)


def _format_category_counts(counts: dict[str, int]) -> str:
    if not counts:
        return "none"
    return "; ".join(f"`{key}` {value}" for key, value in counts.items())


def _precision(tp: int, fp: int) -> float | None:
    return tp / (tp + fp) if tp + fp else None


def _recall(tp: int, fn: int) -> float | None:
    return tp / (tp + fn) if tp + fn else None


def _f1(tp: int, fp: int, fn: int) -> float | None:
    precision = _precision(tp, fp)
    recall = _recall(tp, fn)
    if precision is None and recall is None:
        return None
    if not precision or not recall:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.1%}"


if __name__ == "__main__":
    main()

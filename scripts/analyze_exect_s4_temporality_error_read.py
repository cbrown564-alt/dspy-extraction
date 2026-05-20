"""Analyze ExECT S4 medication-temporality L1 vs H1 full-validation errors."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.evaluation.exect import score_exect_s4_prediction_set
from clinical_extraction.exect.primitives import infer_exect_medication_temporality
from clinical_extraction.schemas import PredictionSet

PLANNED_MARKERS = (
    "to start",
    "please start",
    "plan to start",
    "will start",
    "recommend starting",
    "grateful if you could prescribe",
    "could prescribe",
    "to change to",
)
TAPER_MARKERS = (
    "reduce and stop",
    "reduce the",
    "weaned",
    "taper",
    "stop over",
    "every week until",
)
CURRENT_MARKERS = (
    "current medication",
    "current medications",
    "current anti-epileptic medication",
    "currently taking",
    "currently she is taking",
    "currently he is taking",
)


def load_predictions(path: Path) -> PredictionSet:
    return PredictionSet.model_validate(json.loads(path.read_text(encoding="utf-8")))


def mt_mismatches(report: dict) -> dict[str, dict]:
    return {
        mismatch["document_id"]: mismatch
        for mismatch in report["errors"]["field_family_mismatches"]
        if mismatch["field_family"] == "medication_temporality"
    }


def cue_tags(text: str | None) -> list[str]:
    lowered = (text or "").lower()
    tags: list[str] = []
    if any(marker in lowered for marker in PLANNED_MARKERS):
        tags.append("planned")
    if any(marker in lowered for marker in TAPER_MARKERS):
        tags.append("taper")
    if any(marker in lowered for marker in CURRENT_MARKERS):
        tags.append("current")
    return tags


def medication_temporality_evidence(prediction, label: str) -> str:
    medication = label.split("|", 1)[0].lower()
    for value in prediction.values:
        if value.field_name not in {"medication_temporality", "medication_temporalities"}:
            continue
        raw = (value.raw_value or "").lower()
        normalized = (value.normalized_value or "").lower()
        if medication in raw or medication in normalized or label.lower() in raw:
            if value.evidence:
                return value.evidence[0].text
    return ""


def analyze(l1_path: Path, h1_path: Path) -> dict:
    l1 = load_predictions(l1_path)
    h1 = load_predictions(h1_path)
    l1_report = score_exect_s4_prediction_set(l1)
    h1_report = score_exect_s4_prediction_set(h1)
    l1_mm = mt_mismatches(l1_report)
    h1_mm = mt_mismatches(h1_report)
    notes = {gold.document_id: gold.text for gold in load_exect_gold_documents()}
    l1_by_id = {prediction.document_id: prediction for prediction in l1.predictions}
    h1_by_id = {prediction.document_id: prediction for prediction in h1.predictions}

    h1_new_false_negatives: list[dict] = []
    for document_id, h1_mismatch in h1_mm.items():
        l1_mismatch = l1_mm.get(document_id, {"false_negatives": []})
        for false_negative in h1_mismatch["false_negatives"]:
            if false_negative not in l1_mismatch["false_negatives"]:
                evidence = medication_temporality_evidence(
                    l1_by_id[document_id],
                    false_negative,
                )
                note_text = notes.get(document_id, "")
                classification = infer_exect_medication_temporality(
                    evidence or note_text
                )
                tags = cue_tags(evidence) or cue_tags(note_text)
                h1_new_false_negatives.append(
                    {
                        "document_id": document_id,
                        "gold_label": false_negative,
                        "evidence_quote": evidence,
                        "cue_tags": tags,
                        "inferred_status": classification.canonical_value,
                        "inferred_cues": classification.metadata.get("cues", []),
                        "l1_predicted": l1_mismatch.get("false_positives", [])
                        + [
                            label
                            for label in false_negative.split("|")
                            if label
                        ],
                    }
                )

    precision_wins: list[dict] = []
    for document_id, l1_mismatch in l1_mm.items():
        h1_mismatch = h1_mm.get(document_id, {"false_positives": []})
        for false_positive in l1_mismatch["false_positives"]:
            if false_positive not in h1_mismatch["false_positives"]:
                evidence = medication_temporality_evidence(
                    l1_by_id[document_id],
                    false_positive,
                )
                classification = infer_exect_medication_temporality(
                    evidence or notes.get(document_id, "")
                )
                precision_wins.append(
                    {
                        "document_id": document_id,
                        "removed_fp": false_positive,
                        "evidence_quote": evidence,
                        "cue_tags": cue_tags(evidence),
                        "inferred_status": classification.canonical_value,
                    }
                )

    planned_taper_slice = [
        item
        for item in h1_new_false_negatives
        if "planned" in item["cue_tags"] or "taper" in item["cue_tags"]
    ]
    taper_on_current = [
        item
        for item in h1_new_false_negatives
        if "taper" in item["cue_tags"] and "current" in item["cue_tags"]
    ]
    unknown_removed = [
        item
        for item in h1_new_false_negatives
        if item["inferred_status"] == "unknown"
    ]
    non_asm_related = [
        item
        for item in precision_wins
        if item["inferred_status"] in {"planned", "previous", "unknown"}
    ]

    return {
        "l1_run": str(l1_path.parent.name),
        "h1_run": str(h1_path.parent.name),
        "metrics": {
            "l1": l1_report["benchmark_metrics"]["field_f1"]["medication_temporality"],
            "h1": h1_report["benchmark_metrics"]["field_f1"]["medication_temporality"],
            "l1_precision": l1_report["benchmark_metrics"]["field_precision"][
                "medication_temporality"
            ],
            "h1_precision": h1_report["benchmark_metrics"]["field_precision"][
                "medication_temporality"
            ],
            "l1_recall": l1_report["benchmark_metrics"]["field_recall"][
                "medication_temporality"
            ],
            "h1_recall": h1_report["benchmark_metrics"]["field_recall"][
                "medication_temporality"
            ],
        },
        "counts": {
            "h1_new_false_negatives": len(h1_new_false_negatives),
            "precision_wins": len(precision_wins),
            "planned_taper_slice_fns": len(planned_taper_slice),
            "taper_on_current_fns": len(taper_on_current),
            "unknown_removed_fns": len(unknown_removed),
        },
        "cue_bucket_counts": {
            "+".join(tags) if tags else "no_cue": count
            for tags, count in Counter(
                tuple(item["cue_tags"]) or ("no_cue",) for item in h1_new_false_negatives
            ).items()
        },
        "h1_new_false_negatives": h1_new_false_negatives,
        "precision_wins": precision_wins,
        "planned_taper_slice": planned_taper_slice,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--l1-run", required=True)
    parser.add_argument("--h1-run", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    analysis = analyze(Path(args.l1_run) / "predictions.json", Path(args.h1_run) / "predictions.json")
    Path(args.output).write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(analysis["counts"], indent=2))
    print(json.dumps(analysis["cue_bucket_counts"], indent=2))


if __name__ == "__main__":
    main()

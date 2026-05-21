"""Analyze ExECT S1 seizure_type mismatches for Qwen vs GPT H1 post-bridge runs."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from clinical_extraction.datasets.exect import load_exect_gold_documents
from clinical_extraction.evaluation.exect import score_exect_prediction_set
from clinical_extraction.schemas import PredictionSet

CATEGORIES = (
    "surface_inflection",
    "unsupported_overcall",
    "focal_specificity",
    "secondary_generalisation_policy",
    "missed_gold_label",
    "evidence_unsupported",
    "audit_scorer_caveat",
    "other_model_wording",
)

OVERCALL_TERMS = ("absence", "myoclonic")
SECONDARY_GOLD_TERMS = (
    "secondary generali",
    "secondarily generali",
    "secondary generalisation",
    "complex partial",
)
SECONDARY_PRED_TERMS = ("secondary", "secondarily", "complex partial")


def load_predictions(path: Path) -> PredictionSet:
    return PredictionSet.model_validate(json.loads(path.read_text(encoding="utf-8")))


def seizure_mismatches(report: dict) -> dict[str, dict]:
    return {
        mismatch["document_id"]: mismatch
        for mismatch in report["errors"]["field_family_mismatches"]
        if mismatch["field_family"] == "seizure_type"
    }


def _normalize(label: str) -> str:
    return re.sub(r"\s+", " ", label.lower().strip())


def inflection_equivalent(left: str, right: str) -> bool:
    a, b = _normalize(left), _normalize(right)
    if a == b:
        return True
    if a + "s" == b or b + "s" == a:
        return True
    if a.endswith(" seizure") and b == a + "s":
        return True
    if b.endswith(" seizure") and a == b + "s":
        return True
    if a.endswith(" seizures") and b == a[:-1]:
        return True
    if b.endswith(" seizures") and a == b[:-1]:
        return True
    return False


def is_overcall(label: str, gold_labels: set[str]) -> bool:
    lowered = _normalize(label)
    if any(term in lowered for term in OVERCALL_TERMS):
        return not any(term in _normalize(gold) for gold in gold_labels for term in OVERCALL_TERMS)
    return False


def is_secondary_policy(label: str, *, predicted: bool) -> bool:
    lowered = _normalize(label)
    terms = SECONDARY_PRED_TERMS if predicted else SECONDARY_GOLD_TERMS
    return any(term in lowered for term in terms)


def is_focal_specificity(label: str, counterpart: str | None, gold_labels: set[str]) -> bool:
    lowered = _normalize(label)
    if "focal" not in lowered:
        return False
    if counterpart and inflection_equivalent(label, counterpart):
        return True
    if any("focal" in _normalize(gold) for gold in gold_labels):
        return label not in gold_labels and not any(
            inflection_equivalent(label, gold) for gold in gold_labels
        )
    return False


def classify_atom(
    *,
    document_id: str,
    kind: str,
    label: str,
    mismatch: dict,
    gold_labels: set[str],
    evidence_docs: set[str],
    quality_flags: list[str],
) -> str:
    fps = mismatch["false_positives"]
    fns = mismatch["false_negatives"]
    counterparts = fns if kind == "fp" else fps

    for counterpart in counterparts:
        if inflection_equivalent(label, counterpart):
            return "surface_inflection"

    if kind == "fp" and is_overcall(label, gold_labels):
        return "unsupported_overcall"

    if is_secondary_policy(label, predicted=kind == "fp") or any(
        is_secondary_policy(counterpart, predicted=False) for counterpart in counterparts
    ):
        return "secondary_generalisation_policy"

    if document_id in evidence_docs and kind == "fp":
        return "evidence_unsupported"

    if kind == "fn":
        if is_focal_specificity(label, None, gold_labels):
            return "focal_specificity"
        if _normalize(label) in {"epileptic seizures", "epileptic seizure"} and quality_flags:
            return "audit_scorer_caveat"
        return "missed_gold_label"

    if is_focal_specificity(label, None, gold_labels):
        return "focal_specificity"

    if quality_flags and kind == "fp":
        return "audit_scorer_caveat"

    return "other_model_wording"


def seizure_evidence_error_docs(run_dir: Path) -> set[str]:
    for name in ("errors.json", "metrics.json"):
        path = run_dir / name
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = payload.get("errors", payload)
        return {
            item["document_id"]
            for item in errors.get("evidence_support_errors", [])
            if item.get("field_name") == "seizure_type"
        }
    return set()


def analyze_run(
    *,
    run_dir: Path,
    track: str,
    gold_by_id: dict[str, object],
) -> dict:
    report = score_exect_prediction_set(load_predictions(run_dir / "predictions.json"))
    mismatches = seizure_mismatches(report)
    evidence_docs = seizure_evidence_error_docs(run_dir)
    atoms: list[dict] = []
    category_counts: Counter[str] = Counter()
    docs_by_category: dict[str, set[str]] = defaultdict(set)

    for document_id, mismatch in mismatches.items():
        gold = gold_by_id[document_id]
        gold_labels = {label.lower() for label in gold.seizure_types}
        flags = list(mismatch.get("gold_quality_flags") or gold.quality_flags or [])
        for kind, labels in (("fp", mismatch["false_positives"]), ("fn", mismatch["false_negatives"])):
            for label in labels:
                category = classify_atom(
                    document_id=document_id,
                    kind=kind,
                    label=label,
                    mismatch=mismatch,
                    gold_labels=gold_labels,
                    evidence_docs=evidence_docs,
                    quality_flags=flags,
                )
                category_counts[category] += 1
                docs_by_category[category].add(document_id)
                atoms.append(
                    {
                        "document_id": document_id,
                        "track": track,
                        "kind": kind,
                        "label": label,
                        "category": category,
                        "false_positives": mismatch["false_positives"],
                        "false_negatives": mismatch["false_negatives"],
                        "gold_quality_flags": flags,
                    }
                )

    return {
        "track": track,
        "run_id": run_dir.name,
        "seizure_f1": report["benchmark_metrics"]["field_f1"]["seizure_type"],
        "micro_f1": report["benchmark_metrics"]["micro_f1"],
        "mismatch_documents": len(mismatches),
        "false_positive_count": sum(len(m["false_positives"]) for m in mismatches.values()),
        "false_negative_count": sum(len(m["false_negatives"]) for m in mismatches.values()),
        "category_counts": dict(category_counts),
        "documents_by_category": {
            category: sorted(document_ids)
            for category, document_ids in docs_by_category.items()
        },
        "mismatch_documents_sorted": sorted(mismatches),
        "atoms": atoms,
        "mismatches": mismatches,
    }


def recommend_next_action(qwen: dict, gpt: dict) -> str:
    qwen_counts = Counter(qwen["category_counts"])
    qwen_only_docs = set(qwen["mismatch_documents_sorted"]) - set(
        gpt["mismatch_documents_sorted"]
    )
    qwen_only_atoms = [
        atom for atom in qwen["atoms"] if atom["document_id"] in qwen_only_docs
    ]
    qwen_only_categories = Counter(atom["category"] for atom in qwen_only_atoms)

    overcall = qwen_counts["unsupported_overcall"] + qwen_counts["other_model_wording"]
    inflection = qwen_counts["surface_inflection"]
    secondary = qwen_counts["secondary_generalisation_policy"]
    missed = qwen_counts["missed_gold_label"]
    audit = qwen_counts["audit_scorer_caveat"]
    model_wording = overcall + qwen_counts["evidence_unsupported"]

    if audit >= 8 and audit > model_wording:
        return "manual_audit_review"
    if model_wording >= inflection and model_wording >= secondary:
        return "prompt_policy_preregistration"
    if inflection >= secondary and inflection >= missed:
        return "narrow_post_template_repair_preregistration"
    if secondary >= missed and secondary >= inflection:
        return "prompt_policy_preregistration"
    if len({atom["category"] for atom in qwen["atoms"]}) >= 6:
        return "synthesis_pause"
    return "prompt_policy_preregistration"


def analyze(
    *,
    qwen_h1_run: Path,
    gpt_h1_run: Path,
    qwen_l1_run: Path | None,
) -> dict:
    gold_by_id = {gold.document_id: gold for gold in load_exect_gold_documents()}
    qwen = analyze_run(run_dir=qwen_h1_run, track="qwen_h1", gold_by_id=gold_by_id)
    gpt = analyze_run(run_dir=gpt_h1_run, track="gpt_h1", gold_by_id=gold_by_id)
    qwen_l1 = None
    if qwen_l1_run is not None:
        qwen_l1 = analyze_run(run_dir=qwen_l1_run, track="qwen_l1_raw", gold_by_id=gold_by_id)

    shared_docs = sorted(
        set(qwen["mismatch_documents_sorted"]) & set(gpt["mismatch_documents_sorted"])
    )
    qwen_only_docs = sorted(
        set(qwen["mismatch_documents_sorted"]) - set(gpt["mismatch_documents_sorted"])
    )
    gpt_only_docs = sorted(
        set(gpt["mismatch_documents_sorted"]) - set(qwen["mismatch_documents_sorted"])
    )

    bridge_delta = None
    if qwen_l1 is not None:
        bridge_delta = {
            "seizure_f1_delta": qwen["seizure_f1"] - qwen_l1["seizure_f1"],
            "mismatch_documents_delta": qwen["mismatch_documents"]
            - qwen_l1["mismatch_documents"],
            "false_positive_delta": qwen["false_positive_count"]
            - qwen_l1["false_positive_count"],
            "false_negative_delta": qwen["false_negative_count"]
            - qwen_l1["false_negative_count"],
        }

    return {
        "qwen_h1": qwen,
        "gpt_h1": gpt,
        "qwen_l1_raw": qwen_l1,
        "bridge_delta": bridge_delta,
        "overlap": {
            "shared_mismatch_documents": shared_docs,
            "qwen_only_mismatch_documents": qwen_only_docs,
            "gpt_only_mismatch_documents": gpt_only_docs,
        },
        "recommended_next_action": recommend_next_action(qwen, gpt),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--qwen-h1-run", required=True)
    parser.add_argument("--gpt-h1-run", required=True)
    parser.add_argument("--qwen-l1-run")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    analysis = analyze(
        qwen_h1_run=Path(args.qwen_h1_run),
        gpt_h1_run=Path(args.gpt_h1_run),
        qwen_l1_run=Path(args.qwen_l1_run) if args.qwen_l1_run else None,
    )
    Path(args.output).write_text(json.dumps(analysis, indent=2) + "\n", encoding="utf-8")
    print("recommended_next_action:", analysis["recommended_next_action"])
    print("qwen category_counts:", json.dumps(analysis["qwen_h1"]["category_counts"], indent=2))
    print("gpt category_counts:", json.dumps(analysis["gpt_h1"]["category_counts"], indent=2))


if __name__ == "__main__":
    main()

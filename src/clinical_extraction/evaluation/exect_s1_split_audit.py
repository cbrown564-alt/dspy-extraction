"""Deterministic ExECT S1 raw/bridge/prompt split audit helpers."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from clinical_extraction.datasets.exect import load_exect_gold_documents

S1_SPLIT_FIELDS = ("diagnosis", "seizure_type")
S1_RESIDUAL_CLASSES = (
    "extraction",
    "bridge",
    "policy",
    "specificity_collapse",
    "scope",
)

_BRIDGE_FLAG_PREFIXES = ("benchmark_bridge:", "s1_clean_bridge:")
_SCOPE_CUES = (
    "family history",
    "father has",
    "mother has",
    "sibling has",
    "brother has",
    "sister has",
    "differential",
    "possible non-epileptic",
    "non epileptic",
    "non-epileptic",
    "?syncope",
    "syncope",
    "dissociative",
    "psychogenic",
)
_POLICY_LABEL_CUES = (
    "altered awareness",
    "impaired awareness",
    "secondary",
    "generalised",
    "generalized",
    "tonic clonic",
    "focal onset",
    "focal seizure",
    "focal seizures",
    "myoclonic",
    "absence",
    "juvenile myoclonic",
    "single focal seizure",
    "possible",
    "probable",
)


def summarize_s1_run(
    run_dir: Path,
    *,
    gold_text_by_id: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Summarize an S1 run artifact without re-scoring predictions."""

    run_dir = Path(run_dir)
    config = _read_json(run_dir / "config.json")
    metrics = _read_json(run_dir / "metrics.json")
    errors = _read_json(run_dir / "errors.json")
    predictions = _read_json(run_dir / "predictions.json")

    benchmark = metrics["benchmark_metrics"]
    field_f1 = _field_map(benchmark.get("field_f1", {}))
    field_precision = _field_map(benchmark.get("field_precision", {}))
    field_recall = _field_map(benchmark.get("field_recall", {}))
    field_support = _field_map(benchmark.get("field_support", {}))

    prediction_values_by_id = {
        prediction["document_id"]: prediction.get("values", [])
        for prediction in predictions.get("predictions", [])
    }
    bridge_flag_counts = _count_bridge_flagged_values(prediction_values_by_id)
    bridge_flag_names = _count_bridge_flag_names(prediction_values_by_id)

    residuals = []
    residual_class_counts: Counter[str] = Counter()
    for mismatch in errors.get("field_family_mismatches", []):
        field_family = mismatch.get("field_family")
        if field_family not in S1_SPLIT_FIELDS:
            continue
        document_id = str(mismatch.get("document_id", ""))
        prediction_values = prediction_values_by_id.get(document_id, [])
        residual_class = classify_s1_residual(
            mismatch,
            prediction_values,
            note_text=(gold_text_by_id or {}).get(document_id, ""),
        )
        residual_class_counts[residual_class] += 1
        residuals.append(
            {
                "document_id": document_id,
                "field_family": field_family,
                "residual_class": residual_class,
                "false_positives": list(mismatch.get("false_positives", [])),
                "false_negatives": list(mismatch.get("false_negatives", [])),
                "gold_quality_flags": list(mismatch.get("gold_quality_flags", [])),
                "prediction_quality_flags": _quality_flags_for_field(
                    prediction_values,
                    str(field_family),
                ),
            }
        )

    return {
        "run_id": run_dir.name,
        "run_dir": run_dir.as_posix(),
        "split_name": config.get("split_name"),
        "program_variant": config.get("program_variant"),
        "prompt_version": config.get("prompt_version"),
        "repair_policy": config.get("controls", {}).get("repair_policy")
        or config.get("repair_policy"),
        "scorer_mode": config.get("scorer_mode"),
        "model_config_path": config.get("model_config_path"),
        "micro_f1": benchmark.get("micro_f1"),
        "field_f1": field_f1,
        "field_precision": field_precision,
        "field_recall": field_recall,
        "field_support": field_support,
        "counts": metrics.get("counts", {}),
        "bridge_flag_counts": dict(bridge_flag_counts),
        "bridge_flag_names": dict(sorted(bridge_flag_names.items())),
        "residual_class_counts": _ordered_residual_counts(residual_class_counts),
        "residuals": residuals,
    }


def classify_s1_residual(
    mismatch: Mapping[str, Any],
    prediction_values: Sequence[Mapping[str, Any]],
    *,
    note_text: str = "",
) -> str:
    """Classify an S1 diagnosis/seizure residual for causal inspection."""

    field_family = str(mismatch.get("field_family", ""))
    flags = set(mismatch.get("gold_quality_flags", []))
    flags.update(_quality_flags_for_field(prediction_values, field_family))
    labels = _mismatch_labels(mismatch)
    note_lower = note_text.lower()

    if field_family == "diagnosis" and (
        "specificity_collapsed" in flags or _looks_like_specificity_pair(labels)
    ):
        return "specificity_collapse"
    if any(
        flag.startswith(_BRIDGE_FLAG_PREFIXES)
        for flag in flags
    ):
        return "bridge"
    if mismatch.get("false_positives") and any(cue in note_lower for cue in _SCOPE_CUES):
        return "scope"
    if any(cue in label.lower() for label in labels for cue in _POLICY_LABEL_CUES):
        return "policy"
    return "extraction"


def field_f1_delta(
    before_summary: Mapping[str, Any],
    after_summary: Mapping[str, Any],
) -> dict[str, float]:
    """Return field-F1 deltas for the E2 diagnosis/seizure split only."""

    before = before_summary.get("field_f1", {})
    after = after_summary.get("field_f1", {})
    return {
        field: after[field] - before[field]
        for field in S1_SPLIT_FIELDS
        if field in before and field in after
    }


def build_s1_raw_bridge_prompt_audit(
    *,
    run_dirs: Mapping[str, Path],
    residual_sample_limit: int = 12,
) -> dict[str, Any]:
    """Assemble the E2 audit from existing validation and holdout artifacts."""

    gold_text_by_id = {
        document.document_id: document.text
        for document in load_exect_gold_documents()
    }
    run_summaries = {
        name: summarize_s1_run(path, gold_text_by_id=gold_text_by_id)
        for name, path in run_dirs.items()
    }

    deltas = {
        "prompt_policy_raw_cap25": field_f1_delta(
            run_summaries["schema_raw_cap25"],
            run_summaries["policy_raw_cap25"],
        ),
        "bridge_cap25": field_f1_delta(
            run_summaries["policy_raw_cap25"],
            run_summaries["policy_post_bridge_cap25"],
        ),
        "bridge_full_validation": field_f1_delta(
            run_summaries["policy_raw_full_validation"],
            run_summaries["policy_post_bridge_full_validation"],
        ),
        "qwen_holdout_minus_validation": field_f1_delta(
            run_summaries["qwen_clean_validation"],
            run_summaries["qwen_clean_test_holdout"],
        ),
    }

    return {
        "audit_id": "exect_s1_raw_bridge_prompt_split_audit_20260528",
        "dataset": "exect_v2",
        "schema_level": "exect_s0_s1_field_family",
        "field_families": list(S1_SPLIT_FIELDS),
        "scorer_mode": "exect_field_family_deterministic_v1",
        "artifact_only": True,
        "model_calls": 0,
        "run_summaries": run_summaries,
        "stage_deltas": deltas,
        "bridge_only_repair_counts": {
            name: summary["bridge_flag_counts"]
            for name, summary in run_summaries.items()
            if "bridge" in name or "clean" in name
        },
        "residual_comparison": {
            name: summary["residual_class_counts"]
            for name, summary in run_summaries.items()
            if name in {
                "policy_post_bridge_full_validation",
                "qwen_clean_validation",
                "qwen_clean_test_holdout",
            }
        },
        "residual_samples": {
            name: summary["residuals"][:residual_sample_limit]
            for name, summary in run_summaries.items()
            if name in {
                "policy_post_bridge_full_validation",
                "qwen_clean_validation",
                "qwen_clean_test_holdout",
            }
        },
        "interpretation": _interpret_s1_split(run_summaries, deltas),
        "caveats": [
            "This audit reuses stored artifacts and makes no model calls.",
            "It does not change loader, scorer, split, or benchmark bridge semantics.",
            "Cap-25 prompt-policy deltas are diagnostic slice comparisons, not full-validation estimates.",
            "Test-holdout metrics are reported only from the pre-existing test-holdout run and must not be used for tuning.",
            "Medication is excluded from E2 because this card targets diagnosis and seizure-type causal attribution.",
        ],
    }


def render_s1_raw_bridge_prompt_audit_markdown(report: Mapping[str, Any]) -> str:
    """Render the E2 audit as a compact inspection note."""

    lines = [
        "# ExECT S1 Raw/Bridge/Prompt Split Audit",
        "",
        "Date: 2026-05-28",
        "",
        "## Scope",
        "",
        "- Dataset: ExECTv2",
        "- Split surfaces: validation cap-25, full validation, and pre-existing test holdout",
        "- Fields: diagnosis and seizure type",
        "- Scorer: `exect_field_family_deterministic_v1`",
        "- Model calls: 0",
        "",
        "## Stage Metrics",
        "",
        "| Surface | Split | Repair policy | Micro F1 | Diagnosis F1 | Seizure-type F1 |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ]
    for name, summary in report["run_summaries"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    str(summary.get("split_name") or ""),
                    str(summary.get("repair_policy") or ""),
                    _pct(summary.get("micro_f1")),
                    _pct(summary["field_f1"].get("diagnosis")),
                    _pct(summary["field_f1"].get("seizure_type")),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Field-F1 Deltas",
            "",
            "| Contrast | Diagnosis | Seizure type | Interpretation |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    interpretations = {
        "prompt_policy_raw_cap25": "v4.10 prompt policy without bridges vs schema-only raw cap-25.",
        "bridge_cap25": "Post benchmark bridge effect on the v4.10 policy cap-25 surface.",
        "bridge_full_validation": "Post benchmark bridge effect on the full validation surface.",
        "qwen_holdout_minus_validation": "Qwen clean v2 test holdout minus Qwen clean v2 validation.",
    }
    for name, delta in report["stage_deltas"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    _pp(delta.get("diagnosis")),
                    _pp(delta.get("seizure_type")),
                    interpretations[name],
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Bridge-Flagged Values",
            "",
            "| Surface | Diagnosis | Seizure type |",
            "| --- | ---: | ---: |",
        ]
    )
    for name, counts in report["bridge_only_repair_counts"].items():
        lines.append(
            f"| {name} | {counts.get('diagnosis', 0)} | {counts.get('seizure_type', 0)} |"
        )

    lines.extend(
        [
            "",
            "## Residual Classes",
            "",
            "| Surface | Extraction | Bridge | Policy | Specificity/collapse | Scope |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for name, counts in report["residual_comparison"].items():
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    str(counts.get("extraction", 0)),
                    str(counts.get("bridge", 0)),
                    str(counts.get("policy", 0)),
                    str(counts.get("specificity_collapse", 0)),
                    str(counts.get("scope", 0)),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Holdout Residual Sample",
            "",
            "| Document | Field | Class | False positives | False negatives |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in report["residual_samples"].get("qwen_clean_test_holdout", []):
        lines.append(
            "| "
            + " | ".join(
                [
                    row["document_id"],
                    row["field_family"],
                    row["residual_class"],
                    _join_values(row["false_positives"]),
                    _join_values(row["false_negatives"]),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    for item in report["interpretation"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Caveats",
            "",
        ]
    )
    for caveat in report["caveats"]:
        lines.append(f"- {caveat}")

    lines.append("")
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _field_map(values: Mapping[str, Any]) -> dict[str, Any]:
    return {
        field: values[field]
        for field in S1_SPLIT_FIELDS
        if field in values
    }


def _count_bridge_flagged_values(
    prediction_values_by_id: Mapping[str, Sequence[Mapping[str, Any]]],
) -> Counter[str]:
    counts: Counter[str] = Counter({field: 0 for field in S1_SPLIT_FIELDS})
    for values in prediction_values_by_id.values():
        for value in values:
            field = value.get("field_name")
            if field not in S1_SPLIT_FIELDS:
                continue
            flags = value.get("quality_flags", [])
            if any(
                flag == "specificity_collapsed"
                or str(flag).startswith(_BRIDGE_FLAG_PREFIXES)
                for flag in flags
            ):
                counts[str(field)] += 1
    return counts


def _count_bridge_flag_names(
    prediction_values_by_id: Mapping[str, Sequence[Mapping[str, Any]]],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for values in prediction_values_by_id.values():
        for value in values:
            if value.get("field_name") not in S1_SPLIT_FIELDS:
                continue
            for flag in value.get("quality_flags", []):
                flag = str(flag)
                if flag == "specificity_collapsed" or flag.startswith(_BRIDGE_FLAG_PREFIXES):
                    counts[flag] += 1
    return counts


def _ordered_residual_counts(counts: Counter[str]) -> dict[str, int]:
    return {
        residual_class: counts.get(residual_class, 0)
        for residual_class in S1_RESIDUAL_CLASSES
        if counts.get(residual_class, 0)
    }


def _quality_flags_for_field(
    prediction_values: Sequence[Mapping[str, Any]],
    field_family: str,
) -> list[str]:
    flags: list[str] = []
    for value in prediction_values:
        if value.get("field_name") != field_family:
            continue
        for flag in value.get("quality_flags", []):
            if str(flag) not in flags:
                flags.append(str(flag))
    return flags


def _mismatch_labels(mismatch: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    for key in ("false_positives", "false_negatives"):
        labels.extend(str(value) for value in mismatch.get(key, []))
    return labels


def _looks_like_specificity_pair(labels: Sequence[str]) -> bool:
    normalized = {label.lower() for label in labels}
    if "epilepsy" in normalized and any(
        label.endswith("epilepsy") and label != "epilepsy"
        for label in normalized
    ):
        return True
    if "focal epilepsy" in normalized and any(
        label in normalized
        for label in {
            "temporal lobe epilepsy",
            "frontal lobe epilepsy",
            "parietal lobe epilepsy",
            "occipital lobe epilepsy",
            "symptomatic structural focal epilepsy",
        }
    ):
        return True
    return False


def _interpret_s1_split(
    run_summaries: Mapping[str, Mapping[str, Any]],
    deltas: Mapping[str, Mapping[str, float]],
) -> list[str]:
    validation_bridge = run_summaries["policy_post_bridge_full_validation"]
    raw_full = run_summaries["policy_raw_full_validation"]
    bridge_delta = deltas["bridge_full_validation"]
    holdout_delta = deltas["qwen_holdout_minus_validation"]

    return [
        (
            "Full-validation GPT S1 is near ceiling only after benchmark-policy bridges: "
            f"diagnosis rises from {_pct(raw_full['field_f1'].get('diagnosis'))} raw "
            f"to {_pct(validation_bridge['field_f1'].get('diagnosis'))} bridged, "
            f"and seizure type rises from {_pct(raw_full['field_f1'].get('seizure_type'))} "
            f"to {_pct(validation_bridge['field_f1'].get('seizure_type'))}."
        ),
        (
            "The full-validation bridge contribution remains large "
            f"({ _pp(bridge_delta.get('diagnosis')) } diagnosis, "
            f"{ _pp(bridge_delta.get('seizure_type')) } seizure type), so raw extraction "
            "is not itself at ceiling."
        ),
        (
            "The Qwen clean v2 test holdout drops sharply relative to its validation anchor "
            f"({ _pp(holdout_delta.get('diagnosis')) } diagnosis, "
            f"{ _pp(holdout_delta.get('seizure_type')) } seizure type), so S1 should be "
            "treated as validation-aligned rather than globally solved."
        ),
        (
            "Residuals should be worked family by family: diagnosis failures skew toward "
            "scope/specificity/extraction boundaries, while seizure-type failures retain "
            "policy and bridge-sensitive granularity problems."
        ),
        (
            "Decision: E2 supports keeping S1 as a strong validation anchor, but not as a "
            "near-ceiling mechanism claim until raw extraction and prompt-policy transfer "
            "are verified on holdout without using holdout for tuning."
        ),
    ]


def _pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:.1f}%"


def _pp(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value) * 100:+.1f} pp"


def _join_values(values: Sequence[str]) -> str:
    return ", ".join(values) if values else "-"

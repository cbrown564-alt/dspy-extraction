from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.datasets.gan import FREQUENCY_KEY
from clinical_extraction.evaluation.gan_run_analysis import load_split_ids
from clinical_extraction.gan.frequency import normalize_label


SEIZURE_TERMS_RE = re.compile(
    r"\b(seizure|seizures|event|events|episode|episodes|absence|absences|"
    r"drop attack|drop attacks|jerk|jerks|myoclonic|tonic[- ]clonic|"
    r"convulsion|convulsions|cluster|clusters|aura|auras|spell|spells)\b",
    re.IGNORECASE,
)
FREQUENCY_CUES_RE = re.compile(
    r"\b("
    r"\d+|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"once|twice|daily|weekly|monthly|yearly|per|every|each|"
    r"day|days|week|weeks|month|months|year|years|"
    r"morning|mornings|night|nights|since|last|previous|current|"
    r"recent|recently|no further|seizure[- ]free|free for|"
    r"multiple|several|few|occasional|sporadic|infrequent|"
    r"×|x/month|x/week"
    r")\b",
    re.IGNORECASE,
)
HIGHEST_POLICY_RE = re.compile(
    r"\b("
    r"choose|select|chosen|highest|more frequent|most frequent|higher frequency|"
    r"apply rule|among different seizure types|among multiple seizure types"
    r")\b",
    re.IGNORECASE,
)
MULTIPLE_ANALYSIS_RE = re.compile(
    r"(\(\s*1\s*\).*(\(\s*2\s*\)|\b2\)|second)|"
    r"identify (all )?(explicit )?frequenc|"
    r"multiple (different |candidate |concurrent )?frequenc|"
    r"two patterns|several (candidate|frequenc)|"
    r"in addition.*\b(per|daily|weekly|monthly|frequency|seizure))",
    re.IGNORECASE | re.DOTALL,
)
HISTORICAL_CURRENT_RE = re.compile(
    r"\b(current|currently|now|present|historical|previously|prior|past|"
    r"baseline|deterioration|improvement|improved|worsened|formerly|"
    r"since last|last review|last appointment)\b",
    re.IGNORECASE,
)
SEIZURE_FREE_RE = re.compile(
    r"\b(no further seizures|no seizures|seizure[- ]free|free of seizures|"
    r"longest seizure[- ]free|without seizures|event-free|no recent seizures)\b",
    re.IGNORECASE,
)
CLUSTER_RE = re.compile(
    r"\b(cluster|clusters|grouped|groupings|batches|bursts|flurries|runs)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class GanMultiEventFlags:
    record_id: str
    source_row_index: int
    clinical_record: bool
    gold_label: str
    reference_label: str | None
    label_reference_disagreement: bool
    gold_evidence_multispan: bool
    broad_frequency_mention_count: int
    broad_frequency_mentions_ge_2: bool
    broad_frequency_mentions_ge_3: bool
    analysis_highest_frequency_language: bool
    analysis_multiple_frequency_language: bool
    multi_or_highest_analysis_signal: bool
    multiple_candidate_frequencies: bool
    highest_frequency_policy_required: bool
    historical_current_conflict: bool
    seizure_free_conflict: bool
    cluster_adjudication_required: bool
    unknown_with_event_mentions: bool
    flag_names: list[str]


def build_multi_event_flags(raw: dict[str, Any]) -> GanMultiEventFlags:
    frequency = raw[FREQUENCY_KEY]
    source_row_index = int(raw["source_row_index"])
    record_id = f"gan_{source_row_index}"
    gold = frequency["seizure_frequency_number"]
    reference = frequency.get("reference") or [None, None]
    gold_label = normalize_label(gold[0])
    reference_label = normalize_label(reference[0]) if reference[0] else None
    gold_evidence = str(gold[1] if len(gold) > 1 and gold[1] is not None else "")
    note_text = str(raw.get("clinic_date", ""))
    analysis = str(frequency.get("analysis") or "")
    combined = f"{analysis}\n{note_text}"

    mention_count = count_broad_frequency_mentions(note_text)
    analysis_highest = bool(HIGHEST_POLICY_RE.search(analysis))
    analysis_multiple = bool(MULTIPLE_ANALYSIS_RE.search(analysis))
    multi_or_highest = analysis_highest or analysis_multiple
    clinical_record = gold_label != "no seizure frequency reference"

    multiple_candidate_frequencies = multi_or_highest or mention_count >= 3
    highest_frequency_policy_required = analysis_highest
    historical_current_conflict = bool(HISTORICAL_CURRENT_RE.search(analysis)) and bool(
        re.search(r"\b(current|currently|now|present)\b", analysis, re.IGNORECASE)
    ) and bool(
        re.search(r"\b(historical|previously|prior|past|baseline|formerly)\b", analysis, re.IGNORECASE)
    )
    seizure_free_conflict = bool(SEIZURE_FREE_RE.search(combined)) and gold_label not in {
        "no seizure frequency reference",
    }
    cluster_adjudication_required = "cluster" in gold_label or bool(CLUSTER_RE.search(combined))
    unknown_with_event_mentions = gold_label == "unknown" and (
        mention_count > 0 or bool(SEIZURE_TERMS_RE.search(analysis))
    )

    flag_names = []
    for name, value in (
        ("multiple_candidate_frequencies", multiple_candidate_frequencies),
        ("highest_frequency_policy_required", highest_frequency_policy_required),
        ("historical_current_conflict", historical_current_conflict),
        ("seizure_free_conflict", seizure_free_conflict),
        ("cluster_adjudication_required", cluster_adjudication_required),
        ("unknown_with_event_mentions", unknown_with_event_mentions),
    ):
        if value:
            flag_names.append(name)

    return GanMultiEventFlags(
        record_id=record_id,
        source_row_index=source_row_index,
        clinical_record=clinical_record,
        gold_label=gold_label,
        reference_label=reference_label,
        label_reference_disagreement=(
            reference_label is not None and reference_label != gold_label
        ),
        gold_evidence_multispan="..." in gold_evidence,
        broad_frequency_mention_count=mention_count,
        broad_frequency_mentions_ge_2=mention_count >= 2,
        broad_frequency_mentions_ge_3=mention_count >= 3,
        analysis_highest_frequency_language=analysis_highest,
        analysis_multiple_frequency_language=analysis_multiple,
        multi_or_highest_analysis_signal=multi_or_highest,
        multiple_candidate_frequencies=multiple_candidate_frequencies,
        highest_frequency_policy_required=highest_frequency_policy_required,
        historical_current_conflict=historical_current_conflict,
        seizure_free_conflict=seizure_free_conflict,
        cluster_adjudication_required=cluster_adjudication_required,
        unknown_with_event_mentions=unknown_with_event_mentions,
        flag_names=flag_names,
    )


def count_broad_frequency_mentions(note_text: str) -> int:
    sentences = split_sentences(note_text)
    return sum(
        1
        for sentence in sentences
        if SEIZURE_TERMS_RE.search(sentence) and FREQUENCY_CUES_RE.search(sentence)
    )


def split_sentences(text: str) -> list[str]:
    chunks = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def build_flags_for_raw_records(raw_records: list[dict[str, Any]]) -> list[GanMultiEventFlags]:
    return [build_multi_event_flags(raw) for raw in raw_records]


def summarize_flags(flags: list[GanMultiEventFlags]) -> dict[str, Any]:
    clinical = [flag for flag in flags if flag.clinical_record]
    total = len(clinical)

    def count(attr: str) -> int:
        return sum(1 for flag in clinical if getattr(flag, attr))

    counts = {
        "clinical_records": total,
        "broad_frequency_mentions_ge_2": count("broad_frequency_mentions_ge_2"),
        "broad_frequency_mentions_ge_3": count("broad_frequency_mentions_ge_3"),
        "analysis_highest_frequency_language": count(
            "analysis_highest_frequency_language"
        ),
        "analysis_multiple_frequency_language": count(
            "analysis_multiple_frequency_language"
        ),
        "multi_or_highest_analysis_signal": count("multi_or_highest_analysis_signal"),
        "analysis_both_multiple_and_highest": sum(
            1
            for flag in clinical
            if flag.analysis_multiple_frequency_language
            and flag.analysis_highest_frequency_language
        ),
        "label_reference_disagreement": count("label_reference_disagreement"),
        "gold_evidence_multispan": count("gold_evidence_multispan"),
        "label_reference_disagreement_plus_multi_or_highest": sum(
            1
            for flag in clinical
            if flag.label_reference_disagreement
            and flag.multi_or_highest_analysis_signal
        ),
        "multiple_candidate_frequencies": count("multiple_candidate_frequencies"),
        "highest_frequency_policy_required": count(
            "highest_frequency_policy_required"
        ),
        "historical_current_conflict": count("historical_current_conflict"),
        "seizure_free_conflict": count("seizure_free_conflict"),
        "cluster_adjudication_required": count("cluster_adjudication_required"),
        "unknown_with_event_mentions": count("unknown_with_event_mentions"),
    }
    return {
        "counts": counts,
        "shares_of_clinical": {
            key: value / total if total else None
            for key, value in counts.items()
            if key != "clinical_records"
        },
        "note": (
            "Diagnostic flags only. Broad mention counts are upper-bound text "
            "screens; analysis-language flags are conservative audit-trail signals."
        ),
    }


def load_analysis_rows(records_jsonl: Path) -> list[dict[str, Any]]:
    rows = []
    with records_jsonl.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def stratify_rows_by_multi_event_flags(
    rows: list[dict[str, Any]],
    flags_by_id: dict[str, GanMultiEventFlags],
) -> dict[str, Any]:
    joined_rows = []
    for row in rows:
        flags = flags_by_id.get(row["record_id"])
        if flags is None:
            continue
        joined_rows.append({**row, "multi_event_flags": asdict(flags)})

    flag_names = [
        "multiple_candidate_frequencies",
        "highest_frequency_policy_required",
        "historical_current_conflict",
        "seizure_free_conflict",
        "cluster_adjudication_required",
        "unknown_with_event_mentions",
        "multi_or_highest_analysis_signal",
        "label_reference_disagreement",
        "gold_evidence_multispan",
    ]
    return {
        "records_joined": len(joined_rows),
        "flags": {
            flag_name: {
                "true": _stratum_summary(
                    [
                        row
                        for row in joined_rows
                        if row["multi_event_flags"].get(flag_name)
                    ]
                ),
                "false": _stratum_summary(
                    [
                        row
                        for row in joined_rows
                        if not row["multi_event_flags"].get(flag_name)
                    ]
                ),
            }
            for flag_name in flag_names
        },
        "monthly_miss_flag_counts": monthly_miss_flag_counts(joined_rows, flag_names),
    }


def monthly_miss_flag_counts(
    joined_rows: list[dict[str, Any]], flag_names: list[str]
) -> dict[str, Any]:
    misses = [
        row
        for row in joined_rows
        if row.get("status") == "scored"
        and row.get("monthly_match") is False
        and row.get("failure_action_tier") == "benchmark_severe"
    ]
    return {
        "monthly_miss_count": len(misses),
        "flag_counts": {
            flag_name: sum(
                1 for row in misses if row["multi_event_flags"].get(flag_name)
            )
            for flag_name in flag_names
        },
        "failure_class_by_multi_or_highest": {
            str(bucket).lower(): dict(
                Counter(
                    row.get("failure_class")
                    for row in misses
                    if bool(row["multi_event_flags"].get("multi_or_highest_analysis_signal"))
                    is bucket
                )
            )
            for bucket in (True, False)
        },
    }


def build_validation_stratification(
    *,
    flags: list[GanMultiEventFlags],
    records_jsonl: Path,
    split_file: Path | None = None,
    split_name: str | None = None,
) -> dict[str, Any]:
    rows = load_analysis_rows(records_jsonl)
    if split_file is not None and split_name is not None:
        split_ids = set(load_split_ids(split_file, split_name))
        rows = [row for row in rows if row["record_id"] in split_ids]
    return stratify_rows_by_multi_event_flags(
        rows, {flag.record_id: flag for flag in flags}
    )


def write_flag_artifacts(
    *,
    flags: list[GanMultiEventFlags],
    output_dir: Path,
    validation_stratification: dict[str, Any] | None = None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = summarize_flags(flags)
    if validation_stratification is not None:
        summary["validation_stratification"] = validation_stratification
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "flags.jsonl").open("w", encoding="utf-8") as handle:
        for flag in flags:
            handle.write(json.dumps(asdict(flag), sort_keys=True) + "\n")


def _stratum_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid_rows = [row for row in rows if row.get("status") == "scored"]
    all_records = len(rows)
    operational_failures = sum(
        1
        for row in rows
        if row.get("status") != "scored"
        or row.get("failure_action_tier") == "benchmark_severe"
    )
    return {
        "all_records": all_records,
        "valid_scored": len(valid_rows),
        "invalid_or_missing": all_records - len(valid_rows),
        "operational_failures": operational_failures,
        "operational_failure_rate": (
            operational_failures / all_records if all_records else None
        ),
        "accuracies_valid_only": _accuracies_valid_only(valid_rows),
    }


def _accuracies_valid_only(valid_rows: list[dict[str, Any]]) -> dict[str, float | None]:
    if not valid_rows:
        return {
            "normalized_label": None,
            "monthly_frequency": None,
            "purist_category": None,
            "pragmatic_category": None,
        }
    count = len(valid_rows)
    return {
        "normalized_label": sum(
            1 for row in valid_rows if row.get("normalized_exact_match")
        )
        / count,
        "monthly_frequency": sum(1 for row in valid_rows if row.get("monthly_match"))
        / count,
        "purist_category": sum(1 for row in valid_rows if row.get("purist_match"))
        / count,
        "pragmatic_category": sum(1 for row in valid_rows if row.get("pragmatic_match"))
        / count,
    }

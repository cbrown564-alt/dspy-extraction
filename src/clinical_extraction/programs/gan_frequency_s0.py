"""Gan seizure-frequency S0 DSPy program."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

import dspy

from clinical_extraction.gan.s0.prediction_bridge import (  # noqa: F401
    _apply_constrained_verifier_guard,
    _apply_evidence_span_check_guard,
    _apply_temporal_verifier_guards,
    _evidence_policy_feedback,
    _evidence_policy_ok,
    _evidence_spans,
    _forbidden_unit,
    _guard_evidence_text,
    _has_temporal_window_mismatch,
    _is_short_seizure_free_label,
    _looks_like_cluster_failure,
    _looks_like_no_reference_note,
    _normalize_predicted_label,
    _predict_record,
    _requires_evidence_support,
    gan_frequency_s0_run_metadata,
    predict_gan_records,
)
from clinical_extraction.gan.s0.variant_routing import (  # noqa: F401
    GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY,
    GAN_CONTEXT_POLICY_FULL_NOTE,
    GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES,
    GAN_FREQUENCY_S0_ADJUDICATE_VERIFY_REPAIR_SPAN_CHECK_PROMPT_VERSION,
    GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_V1_2_GUARDRAILS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_V1_2B_SCHEMA_GUARD_ONLY_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_DEFAULT_PROMPT_BY_VARIANT,
    GAN_FREQUENCY_S0_DIRECT_GUARDRAILS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DIRECT_VARIANT,
    GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_EVIDENCE_OPTIONAL_PROMPT_VERSION,
    GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION,
    GAN_FREQUENCY_S0_FIELD,
    GAN_FREQUENCY_S0_GUARDRAILS_PORT_TEMPORAL_PROMPT_VERSION,
    GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT,
    GAN_FREQUENCY_S0_RETRIEVAL_EMPTY_CANDIDATES_NOTE_STUB,
    GAN_FREQUENCY_S0_SCHEMA_LEVEL,
    GAN_FREQUENCY_S0_SCORER,
    GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT,
    GAN_FREQUENCY_S0_STAGE_GRAPH_BY_VARIANT,
    GAN_FREQUENCY_S0_SYNTHESIS_PORT_TEMPORAL_PROMPT_VERSION,
    GAN_FREQUENCY_S0_SYNTHESIS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_CANONICAL_EXAMPLES_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_COMPACT_HIERARCHY_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_ERROR_TAXONOMY_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_QWEN_EXACT_POLICY_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_QWEN_HYBRID_RESOLUTION_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_QWEN_SCHEMA_VALIDITY_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_SLOT_PAYLOAD_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_TARGETED_EXAMPLES_MIN7_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_UNKNOWN_OVERUSE_GUARD_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT,
    GAN_FREQUENCY_S0_TOOL_DATE_RESOLVER_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TOOL_DATE_RESOLVER_SINGLE_PASS_VARIANT,
    GAN_FREQUENCY_S0_VARIANT,
    GAN_FREQUENCY_S0_VARIANT_SPECS,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT,
    GanS0VariantSpec,
    default_gan_frequency_s0_prompt_version,
    gan_frequency_s0_variant_spec,
    stage_graph_id_for_program_variant,
)
from clinical_extraction.schemas import GanRecord

GAN_FREQUENCY_SYNTHESIS_GUIDANCE = (
    "Synthesis-backed Gan frequency policy: output only canonical Gan labels; "
    "use singular units day/week/month/year; convert daily or nightly to 1 per day; "
    "convert every N unit to 1 per N unit; use 'to' for numeric ranges; "
    "choose the highest current quantified seizure-type frequency; use full cluster "
    "format 'N cluster per unit, M per cluster'; for year-to-date counts use months "
    "elapsed since January as the denominator; treat a quarter as an observation "
    "window when the note gives a per-month rate over the last quarter; use seizure "
    "free labels only for seizure freedom of 6 months or longer, otherwise compute "
    "the rate from total events over the described period; return an exact contiguous "
    "source quote for every present claim."
)


class GanFrequencyS0Signature(dspy.Signature):
    """Extract the Gan seizure-frequency label and supporting evidence from a clinical note.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    The label must match the Gan annotation vocabulary exactly. Abstain (null) only when
    the note contains no usable seizure-frequency information at all. When seizures are
    discussed but not quantifiable, output unknown — never null. Administrative or
    no-clinical-content letters MUST output no seizure frequency reference (not null,
    not unknown).

    Synthesis-backed policy:
    - Output only canonical Gan labels: N per unit, N to M per unit, N per M unit,
      N cluster per unit, M per cluster, seizure free for N unit, unknown, or
      no seizure frequency reference.
    - Use singular units: day, week, month, year. Never use hour or other units.
    - Convert daily/nightly to 1 per day, every N unit to 1 per N unit, and
      numeric "or" ranges to "to" ranges.
    - Choose the highest current quantified seizure-type frequency.
    - Quantified rates beat unknown: when the note states an explicit event count
      over a time window — even infrequent — output the canonical N per M unit rate.
      Do NOT collapse low-frequency quantified counts to unknown. Infrequent explicit
      rates are still quantified — never answer unknown when both count and window
      are present. Worked examples (output the rate, NOT unknown):
      "two seizures in the last three months" → "2 per 3 month";
      "about once a month" → "1 per month";
      "one seizure per year" / "once yearly" → "1 per year";
      "10 seizures over six months" → "10 per 6 month";
      "2 to 3 events in 15 months" → "2 to 3 per 15 month".
      Reserve unknown for qualitative or pattern-only descriptions where no
      count+window can be extracted from the note.
    - Multiple vs undercount: when the note uses multiple, several, a few, or similar
      without an exact count for the highest current rate, output multiple per unit
      (e.g. multiple per week). Do NOT round vague multiplicity down to 1 per week
      or 1 per month. When several quantified rates appear, choose the highest
      current rate; if that rate is expressed as multiple/severe/vague multiplicity,
      preserve multiple in the label.
    - Cluster format is mandatory: every cluster label must include BOTH parts
      separated by a comma — "N cluster per unit, M per cluster". Never emit an
      incomplete cluster such as "1 cluster per week" alone. When the per-cluster
      count is unknown or not documented, use "multiple per cluster". Example:
      "weekly clusters, number per cluster not documented" →
      "1 cluster per week, multiple per cluster"; "4 clusters this quarter" →
      "4 cluster per 3 month, multiple per cluster". Distinguish cluster period
      from seizures per cluster: "now weekly, 3 or 4 per cluster" →
      "1 cluster per week, 3 to 4 per cluster" (NOT "3 to 4 cluster per week").
    - Use seizure free for N unit only when seizure freedom is at least 6 months.
      If seizure freedom is shorter than 6 months, compute the rate from the
      total events over the described period.
    - Year-to-date counts: NEVER use "N per year" for "this year to date" or YTD
      phrasing. Divide the count by months elapsed since January through the
      clinic or letter date — e.g. 5 seizures YTD in February → "5 per 2 month";
      9 seizures YTD in January → "9 per month". Reserve "N per year" only for
      explicit full-calendar-year or "per year" wording, not YTD counts.
    - Treat "over the last quarter" as an observation window when the note gives
      a per-month rate; do not automatically convert it to per 3 month.
    - Unknown vs no seizure frequency reference: use unknown ONLY when seizures,
      episodes, clusters, or a last-seizure date are discussed but no explicit
      count+time-window can be extracted. If the note gives N events over M
      months/weeks/years, output the rate — not unknown. Use no seizure frequency
      reference ONLY when the note lacks usable seizure-frequency information
      (including administrative or no-clinical-content letters). For admin or
      no-clinical-content letters, output no seizure frequency reference — never
      null and never unknown. Do NOT output no seizure frequency reference when
      seizures are mentioned with clinical frequency content — that is unknown.
      Examples: admin/scheduling-only letter → no seizure frequency reference;
      "clusters after poor sleep" with no counts → unknown; "last seizure on DATE"
      without an ongoing rate → unknown; "none in 4 months but bursts with travel"
      → unknown; "two in three months" → "2 per 3 month" (NOT unknown).
      Do not output null for no-content cases.
    - When multiple quantified seizure-type frequencies are present, choose the
      highest current rate for the primary label.
    - evidence_text must be an exact contiguous quote from the note.
    """

    note_text: str = dspy.InputField(desc="Clinical neurology note text")
    seizure_frequency_number: Optional[str] = dspy.OutputField(
        desc=(
            "Seizure frequency in Gan label format. One of: "
            "'{count} per {unit}' e.g. '2 per week', '1 per 3 month'; "
            "'{count} cluster per {unit}, {n} per cluster' (both parts required; "
            "use 'multiple per cluster' when count unknown); "
            "'unknown'; 'no seizure frequency reference'; "
            "or null to abstain. Unit must be singular: day/week/month/year."
        )
    )
    evidence_text: Optional[str] = dspy.OutputField(
        desc=(
            "Shortest exact contiguous quote from the note supporting the label. "
            "Do not include prompt instructions or wrapper text. Null if abstaining."
        )
    )


class GanFrequencyS0Module(dspy.Module):
    """Narrow Gan seizure-frequency S0 DSPy module.

    Uses ChainOfThought so the model reasons before committing to a label.
    Compile with BootstrapFewShot or MIPROv2 + ``gan_frequency_s0_metric``
    before running on the evaluation split.
    """

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.ChainOfThought(GanFrequencyS0Signature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class GanFrequencyS0DirectModule(dspy.Module):
    """Gan S0 module that predicts the structured fields without a reasoning output."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_DIRECT_GUARDRAILS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.extract = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class GanFrequencyS0VerifierSignature(dspy.Signature):
    """Verify and optionally repair a Gan seizure-frequency prediction.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    Review the initial prediction against the source note. **Confirm-first:** when
    the initial label is already canonical, note-supported, and initial_evidence is
    an exact contiguous note substring, confirm without repair. Repair only for a
    strictly better supported label. Abstain only as a last resort.

    Canonical Gan vocabulary (singular units: day, week, month, year):
    - N per unit, N to M per unit, N per M unit
    - N cluster per unit, M per cluster — BOTH parts required; "multiple per cluster"
      is a standard Gan unit when per-cluster count is undocumented
    - seizure free for N unit — VALID and canonical when N is at least 6 months
      (e.g. seizure free for 7 month, seizure free for 35 year)
    - unknown — note discusses seizures but frequency cannot be quantified
    - no seizure frequency reference — note lacks usable frequency information

    Decision policy:
    - confirm: default when initial label is canonical, note-supported, and evidence
      is an exact contiguous note substring. Do not add quotes or wrapper punctuation.
    - repair: fix a specific error to a strictly better canonical label supported
      by the note. Do not repair imprecise-but-valid labels to unknown.
    - abstain: last resort only — set final_label to null when no confident
      canonical label is supported.

    Confirm-first rules (do not over-repair):
    - If initial_label and initial_evidence already match the note, confirm unchanged.
    - Keep correct seizure-free labels such as seizure free for 7 month.
    - seizure free for N unit is canonical when seizure freedom is >= 6 months;
      never reject it as non-canonical or replace it with no seizure frequency
      reference.
    - Year-to-date (YTD): if initial_label uses months elapsed since January for a
      "this year to date" / YTD note (e.g. 9 per month in January, 5 per 2 month in
      February), confirm — never expand YTD to a 12-month or per-year denominator.
    - Full cluster labels: if initial_label includes "N cluster per unit, M per cluster"
      (including ", multiple per cluster"), confirm — never strip the second clause
      or collapse to "N per week" / "N per month".
    - Confirm initial_label unknown when seizures are discussed but the pattern is
      qualitative only: clusters without counts; trigger-dependent infrequency
      (e.g. none at home but bursts with travel); last-seizure date without an ongoing
      rate window; "none in N months" without a stable canonical rate.

    Repair rules:
    - Incomplete cluster labels: add the per-cluster count when the note states it
      and initial_label omitted it — preserve ", multiple per cluster" when count
      is still undocumented.
    - Short seizure-free periods (< 6 months): compute a rate from total events over
      the described period; do NOT emit seizure free for N unit when N < 6 months.
    - Infrequent quantified rates over unknown — span discipline: repair unknown
      to a canonical N per M unit rate ONLY when initial_label is unknown AND the
      note gives an explicit event count AND an explicit/shared time window in ONE
      contiguous evidence span (count and window together). Worked examples:
      "two to three single jerks remain since 12/2020" over ~15 months →
      "2 to 3 per 15 month"; "two seizures in the last three months" → "2 per 3 month".
      Do NOT repair when count and window require stitching non-adjacent spans,
      when a longer stability window conflicts with a recent event only, or when
      partial phrases (e.g. "three Saturdays ago") lack a shared denominator with
      the count. Do NOT repair unknown using only "no further events since DATE"
      when earlier dated events define the rate.
    - Imprecise but valid labels (e.g. multiple per week): sharpen toward the
      nearest supported canonical form or confirm; do not collapse to unknown.
    - Unknown vs no-reference: use unknown when seizures are discussed but not
      quantifiable; use no-reference only when the note lacks frequency information.
    - Do not repair unknown to a quantified rate when the note only gives qualitative
      infrequency, clusters without counts, or a last-seizure date without an ongoing
      rate window.

    Anti-over-repair (never do these):
    - Do not repair unknown to no seizure frequency reference when seizures,
      episodes, clusters, or a last-seizure date are discussed.
    - Do not repair unknown to seizure free for N unit when N < 6 months.
    - Do not repair a correct YTD-based initial_label to per year or per 12 month.
    - Do not strip ", multiple per cluster" or collapse cluster labels to simple rates.

    Evidence rules:
    - final_evidence must be the shortest exact contiguous substring of note_text.
    - On confirm, preserve initial_evidence when it already supports the label.
    - On repair off unknown, final_evidence must contain BOTH the count and the
      time-window phrase used for the denominator in one contiguous quote.
    - Never replace a note-contained quote with an unsupported or invented quote.

    Arithmetic and temporal guardrails:
    - Do not invent monthly rates without explicit support (e.g. one seizure in
      three weeks → 1 per 3 week, not 3 per month).
    - Apply the 6-month seizure-free threshold before labeling seizure free.
    - For year-to-date counts, use months elapsed since January as denominator.

    Target failure modes:
    - Incomplete cluster labels (missing per-cluster count)
    - Temporal-window or denominator errors (year-to-date, quarter misinterpretation)
    - Short seizure-free periods labeled as seizure free
    - Misrejecting valid seizure free for N unit labels
    - Over-repairing to unknown or no seizure frequency reference
    - Over-unknown on infrequent quantified rates (unknown when count+window present)
    - Unknown vs no seizure frequency reference confusion
    - Non-canonical or unsupported evidence quotes
    """

    note_text: str = dspy.InputField(desc="Clinical neurology note text")
    initial_label: Optional[str] = dspy.InputField(
        desc="Initial predicted seizure-frequency label"
    )
    initial_evidence: Optional[str] = dspy.InputField(
        desc="Initial predicted evidence quote"
    )
    final_label: Optional[str] = dspy.OutputField(
        desc=(
            "Confirmed or repaired canonical Gan label without wrapper quotes. "
            "Formats: N per unit, N to M per unit, N per M unit, "
            "N cluster per unit, M per cluster, seizure free for N unit (>= 6 months), "
            "unknown, no seizure frequency reference, or null to abstain."
        )
    )
    final_evidence: Optional[str] = dspy.OutputField(
        desc=(
            "Shortest exact contiguous quote from note_text supporting final_label. "
            "Preserve initial_evidence on confirm when it already matches the note. "
            "Null only when abstaining or final_label is no seizure frequency reference."
        )
    )
    decision: str = dspy.OutputField(
        desc=(
            "confirm when the initial prediction is already correct; "
            "repair only for a strictly better supported canonical label; "
            "abstain only as a last resort"
        )
    )
    reason: str = dspy.OutputField(
        desc="Brief explanation citing the note span and why confirm/repair/abstain"
    )


class GanFrequencyS0VerifierModule(dspy.Module):
    """Standalone verifier for Gan S0 predictions."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        signature_cls = build_gan_frequency_s0_verifier_signature(
            prompt_version,
            temporal=False,
        )
        self.verify = dspy.Predict(signature_cls)

    def forward(
        self,
        note_text: str,
        initial_label: str | None,
        initial_evidence: str | None,
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_label=initial_label,
            initial_evidence=initial_evidence,
        )


class GanFrequencyS0VerifyRepairModule(dspy.Module):
    """Gan S0 module that extracts then verifies/repairs the prediction."""

    def __init__(
        self,
        extractor_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        extractor_prompt_version = resolve_gan_frequency_s0_extractor_prompt_version(
            prompt_version
        )
        self.extractor = build_gan_s0_module(
            extractor_variant,
            prompt_version=extractor_prompt_version,
        )
        self.verifier = GanFrequencyS0VerifierModule(prompt_version=prompt_version)

    def forward(self, note_text: str) -> dspy.Prediction:
        initial = self.extractor(note_text=note_text)
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )


class GanFrequencyS0TemporalVerifierSignature(GanFrequencyS0VerifierSignature):
    """Verify/repair with deterministic temporal-candidate hints.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    In addition to the base verifier policy, temporal_candidates lists auditable
    event/window interpretations extracted deterministically from the note. These
    are diagnostic hints, not gold labels.

    Temporal-candidate policy (v1.1 confirm-first):
    - Candidate repair is allowed ONLY when initial_label is unknown or abstain/null.
    - When initial_label is any other canonical label, ALWAYS confirm unchanged —
      never repair to a candidate or alternative aggregation, even if candidates differ.
    - When initial_label is unknown, repair ONLY to a listed candidate label when that
      candidate's evidence_text is an exact contiguous substring of note_text and the
      candidate derivation matches the note's event/window structure.
    - Never repair to seizure free for N unit when N < 6 months, including from
      candidates or when no candidate supports seizure-free.
    - If initial_label is unknown, candidates exist, and a repair target is not in the
      candidate list, prefer the first note-supported candidate over an invented label.
    - If no candidate fits or candidates conflict with confirm-first rules, keep
      unknown or abstain rather than inventing a label.
    """

    temporal_candidates: str = dspy.InputField(
        desc=(
            "Deterministic temporal frequency candidates: canonical labels with "
            "event counts, windows, derivations, and evidence spans from the note."
        )
    )


class GanFrequencyS0LlmTemporalCandidatesSignature(dspy.Signature):
    """Extract auditable temporal frequency candidates from a clinical note.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    Build candidate interpretations that could support canonical Gan labels.
    Each candidate must include an exact contiguous evidence_text substring
    from note_text. Do not invent counts, windows, or labels unsupported by
    the note.

    Output temporal_candidates_json as a JSON object with key "candidates":
    a list of objects with canonical_label, event_count, window_count,
    window_unit, evidence_text, and derivation fields.
    """

    note_text: str = dspy.InputField(desc="Clinical neurology note text")
    temporal_candidates_json: str = dspy.OutputField(
        desc=(
            'JSON object {"candidates": [...]} where each candidate includes '
            "canonical_label, event_count, window_count, window_unit, "
            "evidence_text, and derivation."
        )
    )


class GanFrequencyS0TemporalAdjudicateSignature(GanFrequencyS0Signature):
    """Adjudicate Gan seizure frequency with deterministic temporal-candidate hints.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    temporal_candidates lists auditable event/window interpretations extracted
    deterministically from the note. Use them as diagnostic hints when choosing
    the canonical label, not as gold labels.
    """

    temporal_candidates: str = dspy.InputField(
        desc=(
            "Deterministic temporal frequency candidates: canonical labels with "
            "event counts, windows, derivations, and evidence spans from the note."
        )
    )


GAN_FREQUENCY_S0_GUARDRAILS_PORT_EXTRACTOR_ADDENDUM = """
    Prompt policy (guardrails port on temporal verify-repair):
    Arithmetic and temporal guardrails:
    - Do not invent monthly rates without explicit support (e.g. one seizure in
      three weeks → 1 per 3 week, not 3 per month).
    - Apply the 6-month seizure-free threshold before labeling seizure free.
    - For year-to-date counts, use months elapsed since January as denominator.
"""

GAN_FREQUENCY_S0_EVIDENCE_OPTIONAL_ADDENDUM = """
    Evidence policy (optional quote; Gan label policy unchanged):
    - evidence_text may be null when the canonical label is still note-supported.
    - Prefer an exact contiguous quote when one is readily available.
"""

GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_VERIFIER_ADDENDUM = """
    Evidence policy (span-checked quote; Gan label policy unchanged):
    - Reject or repair predictions whose final_evidence is not an exact contiguous
      substring of note_text.
    - On confirm, require initial_evidence to be note-supported when present.
"""

GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_ADDENDUM = """
    Validation-ladder confirm-only policy:
    - decision MUST be confirm only.
    - final_label and final_evidence MUST equal initial_label and initial_evidence.
    - Do not repair or abstain.
"""

GAN_FREQUENCY_S0_ADJUDICATE_VR_SPAN_CHECK_PROMPT_VERSIONS = frozenset(
    {
        GAN_FREQUENCY_S0_ADJUDICATE_VERIFY_REPAIR_SPAN_CHECK_PROMPT_VERSION,
        GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION,
    }
)

GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_GENERATOR_ADDENDUM = """
    LLM temporal-candidate generation policy (v1.1):
    - Propose auditable event/window interpretations that could map to canonical
      Gan labels: N per unit, N to M per unit, N per M unit, cluster labels,
      seizure free for N unit (>= 6 months), unknown, or no seizure frequency
      reference when appropriate.
    - Every candidate must include evidence_text as an exact contiguous substring
      of note_text.
    - Prefer quantified count+window pairs when the note states them.
    - Do not emit duplicate candidates with the same label and evidence span.
"""

GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM = """
    Temporal-candidate adjudication policy (v1.1):
    - temporal_candidates lists auditable event/window interpretations extracted
      deterministically from the note. These are diagnostic hints, not gold labels.
    - Prefer note-supported quantified rates from candidates when they match the
      note's event/window structure.
    - Do not blindly copy a candidate label if the note supports a different
      canonical label.
    - Cluster labels must include both cluster period and per-cluster count.
    - evidence_text must be an exact contiguous substring of note_text.
"""

GAN_FREQUENCY_S0_DATE_EVENTS_ADJUDICATE_EXTRACTOR_ADDENDUM = """
    Date-event payload adjudication policy (v1.2):
    - date_event_payload lists clinic date, temporal anchors, seizure events,
      seizure-free intervals, cluster events, current window cues, candidate labels,
      evidence text, and calculated arithmetic totals/denominators extracted from the note.
    - Treat candidate_labels as diagnostic hints, not gold labels.
    - Prefer note-supported quantified rates from candidates when they match the
      note's event/window structure.
    - Do calendar math: calculate the exact number of months between the clinic date
      and the start date of any seizure-free period or event onset. Use this calculated
      number as the denominator (e.g. 'multiple per 15 month').
    - Identify minor active events: if a note describes generalised seizure freedom
      but describes ongoing myoclonic jerks, brief jumps, or absences, count these
      as active events rather than classifying the patient as seizure-free (e.g.
      'multiple per 15 month').
    - Cluster labels must include both cluster period and per-cluster count.
    - evidence_text must be an exact contiguous substring of note_text.
    - Strict Label Schema Guard: You MUST NOT output hybrid labels containing 'unknown' combined with numbers or units (e.g., '3 per unknown', 'unknown per month', or 'unknown cluster per month'). The only valid ways to use 'unknown' are as the standalone label 'unknown' or in the cluster format 'unknown, multiple per cluster' / 'unknown, N per cluster'. If the event count or the window unit/denominator is unknown, output the standalone label 'unknown'.
    - Ambiguity & Relative Anchor Guardrail: If a note describes events occurring "since starting [medication]", "since beginning [treatment]", "since discharge", or "since last visit" without providing an explicit, documented start date/anchor (e.g., month/year or date), you MUST NOT guess a denominator or calculate a calendar-window using the latest event date or clinic date. In all such unanchored relative cases, output 'unknown' per Gan policy.
    - Trigger-dependent or vague recurrence guardrail: If the note states that seizures only happen after specific triggers (e.g., lack of sleep, illness, travel) but does not state the frequency of those triggers, the overall frequency is unquantifiable. You MUST output 'unknown' rather than estimating a rate.
"""

GAN_FREQUENCY_S0_CANONICAL_FORMAT_EXAMPLES_ADDENDUM = """
    Canonical-format worked examples (v3/v5 port — output the label exactly):
    - 'Two events over the last five months' -> "2 per 5 month"
    - '3 to 4 focal seizures per month' -> "3 to 4 per month"
    - 'Seizure-free for 18 months' -> "seizure free for 18 month"  [SF >= 6 months]
    - 'Seizures are sporadic but frequency unclear' -> "unknown"
    - '<= 6 to 7 per year' -> "6 to 7 per year"  [strip inequality qualifiers]
    - 'daily' or 'nightly' -> "1 per day"
    - 'biweekly' or 'fortnightly' -> "1 per 2 week"
    - 'every 4 days' -> "1 per 4 day"
    - '3 or 4 per week' -> "3 to 4 per week"  [or -> to]
    - 'daily absences and 2 focal seizures per month' -> "1 per day"  [highest type]
    - '2 cluster days per month; typically 4 to 6 seizures on each cluster day'
      -> "2 cluster per month, 4 to 6 per cluster"
    - 'Cluster frequency unclear this month; last month approximately 4 clusters'
      -> "4 cluster per month, multiple per cluster"
    - 'He had 4 seizures in February when withdrawing from medication; has remained
      well since (now May, 3 months later)' -> "4 per 3 month"  [SF < 6 months: rate]
    - 'Had 2 seizures in January; none since (now April, 3 months)' -> "2 per 3 month"
    - 'Has been seizure-free for the past 2 weeks; typically has 1 to 2 seizures
      per month' -> "1 to 2 per month"  [ongoing rate overrides short SF period]
    - 'Currently seizure free; no events for the past 14 months on current medication'
      -> "seizure free for 14 month"  [SF >= 6 months]
    - '11 to 28 events per quarter' -> "11 to 28 per 3 month"  [quarter = 3 month]
"""

GAN_FREQUENCY_S0_SLOT_PAYLOAD_ADJUDICATE_ADDENDUM = """
    Structured slot-payload adjudication policy (v1.3):
    - temporal_candidates now expose structured slots: event_count_or_range,
      event_type, target_priority_cue, window_count/window_unit, window_source,
      denominator_status, cluster slots, unknown_policy_cue, supporting_quote.
    - Prefer the benchmark-facing highest/current seizure-frequency target when
      multiple concurrent seizure types are mentioned. Do not pick a lower-rate
      tonic-clonic or last-event quote if a higher-frequency concurrent type
      is present elsewhere in the note.
    - When denominator_status is missing_or_ambiguous or unknown_policy_cue says
      to prefer unknown, output "unknown" rather than inventing a per-month or
      per-week denominator from an unanchored count or latest date alone.
    - When window_source is calendar_aggregation or elapsed_since_date, derive
      the denominator from the summed counts and elapsed window rather than
      compressing to a single-month rate.
    - For cluster slots, preserve cluster form when cluster_count_or_range is
      present; do not collapse cluster spacing to a simple rate when
      cluster_spacing_source is vague_recurrence unless the note gives explicit
      spacing.
    - candidate_label is a provisional canonical label from slot provenance only;
      choose the final label after reading slots and the full note.
    - evidence_text must remain an exact contiguous substring of note_text.
"""

GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM = """
    Error-taxonomy policy patch (v1.4; Gan S0 Qwen 2026-05-22 follow-up):
    - Broad Gan grouping rule: group multiple recent events into the relevant
      observation window, then compute a canonical rate from the grouped count
      and denominator. When several separate current event frequencies or
      seizure types are stated, choose the most frequent note-supported rate.
    - Counted events followed by "no further events", "stable since", or
      "well since" remain the counted-window label unless the note states a
      seizure-free interval of at least 6 months. Do not convert these cases
      to unknown only because the most recent status is stable.
    - Use seizure free for N unit when the note explicitly says seizure-free,
      no events, or no seizures over a duration or review interval of at least
      6 months. Do not map multi-year remission/no-events language to unknown.
    - Use unknown when a count is trigger-conditioned or pattern-only and lacks
      a usable time denominator across calendar time, e.g. events after nights
      of poor sleep without a rate for how often those nights/events occur.
    - When temporal_candidates contains a note-supported count+window label,
      treat it as the preferred answer. Override it only when the full note
      clearly supports a higher current seizure-type frequency, a seizure-free
      label of at least 6 months, or unknown/no-reference by Gan policy.
    - If overriding a candidate, evidence_text must quote the text that justifies
      the override rather than a later vague stability phrase alone.
    - Multiple current seizure types: choose the highest current epileptic
      seizure-frequency label, not the most severe seizure type and not merely
      the most recent sentence.
    - Cluster distinction: use cluster labels only when the note describes
      events grouped into clusters. Repeated events within a period are not
      automatically clusters. If per-cluster count is known but cluster spacing
      is not, use "unknown, N per cluster" rather than inventing a spacing.
    - EEG/electrographic seizure rates: frequent electrographic seizures captured
      on EEG (e.g. "~4/h", "~6/h") indicate extremely active clinical events
      and must map to "multiple per day". Do not treat active electrographic
      seizures as unknown or subclinical.
    - Flare/bad-week phrasing: frequency counts describing flares or worst-case
      stretches (e.g., "up to seven in bad weeks", "up to 7 in bad weeks")
      must map to the flare rate (e.g. "7 per week"), even if the note mentions
      that events cluster or there are stretches of several weeks without any
      seizures. Prioritize the flare rate over a cluster label or unknown.
    - Trigger-conditioned counts: if a count is conditioned on a trigger (e.g.
      "typically 1 to 2 events in the morning following nights with less than five
      hours of rest", or "after lack of sleep"), you must output "unknown" unless
      the note provides a specific rate of how often the trigger or the events occur
      in calendar time (do not assume weekly/monthly rates for trigger-conditioned counts).
    - Distinguish between "no seizure frequency reference" and "unknown": if the
      note discusses epilepsy or active/interval/breakthrough seizures (even if
      only in relation to missed doses, e.g. "Seizures with missed ASM doses", or
      "breakthrough events"), but does not specify a calendar-time frequency rate,
      you must output "unknown" rather than "no seizure frequency reference". Use
      "no seizure frequency reference" only if seizures are not mentioned at all or
      are explicitly confirmed as remote history only (e.g. seizure-free for multiple
      years/remission).
    - Multiple current seizure types details: if the note mentions multiple types of
      seizures with different frequencies (e.g. generalised GTC seizures are rare at
      "3 per year", but focal sensory or absence seizures occur "several times each
      week" or "twice weekly"), you must prioritize the higher frequency rate
      ("multiple per week" or "2 per week") over the lower frequency rate ("3 per year"
      or "2 per 2 month"), regardless of seizure severity.
    - Unanchored counts over vague intervals: if the note describes a count since an
      unspecified date or event (e.g. "since beginning Clobazam...", "since her last
      clinic appointment...", or "since last review..."), and the duration of that
      interval is not explicitly stated in the note, you must output "unknown" (do
      not invent a rate).
    - Last/single event elapsed windows: if the note describes a last seizure or single event at a specific date less than 6 months ago, and the patient is stable/seizure-free since then, compute the rate over that elapsed window (e.g., last seizure on Jan 2nd and seen on Jan 28th maps to "1 per month"; last seizure on May 20th and seen on Aug 15th maps to "1 per 3 month"). Trust the corresponding candidate rates in temporal_candidates. Do not map these to "unknown" or "seizure free for N month" (since N is less than 6).
    - Counted/withdrawal events followed by stability: counted events or withdrawal events followed by "stable since", "no further events", "seizure free since", or "well since" must remain the rate over the elapsed window (e.g. "4 per 3 month", "2 to 4 per 3 month") if the elapsed seizure-free duration is less than 6 months. Do not map these short-term stable periods (less than 6 months) to "seizure free for N month"; only use "seizure free for N unit" if the duration is at least 6 months. Prioritize these candidate rates over outputting "unknown".
    - Specific seizure terms: when counting events, treat terms like "drop attack",
      "myoclonic jerk", "absence", "convulsion", "focal event", or "prolonged event"
      as active seizures. Do not output "no seizure frequency reference" or "unknown"
      if these specific events are counted and dated in the note. Group them into the
      observation window to compute a rate (e.g. 3 events from Jan to Jul maps to
      "3 per 7 month").
    - Seizure days: if the note states the number of seizure days in a month (e.g.
      "Seizure days: 9/30 this month", "3/30 this month", "5/30"), map this to N per
      month (e.g. "9/30 this month" maps to "9 per month", "3/30 this month" maps to
      "3 per month"). Do not map "9/30" to "1 per month".
    - Non-specific symptoms and seizure freedom: if the note describes the patient as
      having no seizures/events since their last review (e.g. "no witnessed convulsions
      and has continued with a stable spell without events", or "steady run without
      clear seizures"), but mentions non-specific symptoms (e.g., "occasional brief
      moments of lost thread during conversation occurring once every few weeks", or
      "intermittent light-headedness"), do not treat these non-specific symptoms as
      active seizures. Prioritize the seizure-free status and output "seizure free
      for multiple month" (or the elapsed duration).
"""



GAN_FREQUENCY_S0_COMPACT_HIERARCHY_POLICY_ADDENDUM = """
    Compact Gan adjudication hierarchy (v1.5; policy-density mini-grid):
    - First decide whether the note has clinical seizure-frequency content.
      If not, output "no seizure frequency reference".
    - If seizures are discussed but no count+window or cluster spacing can be
      interpreted from the note, output "unknown".
    - Prefer note-supported temporal_candidates with explicit count+window
      evidence. Override candidates only for a clearly higher current rate, a
      qualifying seizure-free interval, or a clearer Gan abstention category.
    - Group multiple recent events into their shared observation window when
      the note supports a common denominator.
    - If multiple current seizure types or frequencies are stated, choose the
      highest note-supported current frequency.
    - Counted events followed by "stable", "no further events", or "well since"
      remain counted-window labels unless the seizure-free interval is at least
      6 months.
    - Trigger-conditioned or pattern-only counts without calendar-time
      denominator remain "unknown".
    - Cluster labels require cluster spacing plus per-cluster count; if only the
      per-cluster count is known, use "unknown, N per cluster".
    - evidence_text must quote the source span that supports the selected label,
      especially when overriding a temporal candidate.
"""

GAN_FREQUENCY_S0_TARGETED_EXAMPLES_MIN7_ADDENDUM = """
    Targeted Gan example pack (v1.6 targeted_examples_min7_v1):
    These examples supplement the v1.4 policy for known ambiguity families.
    Follow the examples only when the note supports the same policy shape.

    - Grouped recent events:
      note: "Since review three months ago, she had one focal seizure in March
      and two in April."
      output: "3 per 3 month"; evidence_text: "one focal seizure in March
      and two in April"

    - Counted events plus short stability:
      note: "He had four seizures during February but no further events since
      then; seen in May."
      output: "4 per 3 month"; evidence_text: "four seizures during February"

    - Highest current frequency:
      note: "Generalised tonic-clonic seizures are yearly, but focal aware
      seizures continue twice each month."
      output: "2 per month"; evidence_text: "focal aware seizures continue
      twice each month"

    - Year-to-date denominator:
      note: "Clinic date is 15 February. She reports four seizures so far this
      year."
      output: "4 per 2 month"; evidence_text: "four seizures so far this year"

    - Trigger-conditioned unknown:
      note: "Events happen after sleep deprivation, but there is no pattern for
      how often this occurs."
      output: "unknown"; evidence_text: "Events happen after sleep deprivation"

    - Cluster ambiguity:
      note: "Her clusters contain three to four brief seizures, but the spacing
      between clusters is unclear."
      output: "unknown, 3 to 4 per cluster"; evidence_text: "clusters contain
      three to four brief seizures"

    - No-reference boundary:
      note: "This letter confirms cancellation of the neurology appointment and
      does not discuss seizures."
      output: "no seizure frequency reference"; evidence_text: null
"""


GAN_FREQUENCY_S0_QWEN_EXACT_POLICY_ADDENDUM = """
    Qwen exact-frequency policy slice (v1.7; L2 local-gap follow-up):
    Apply the v1.4 error-taxonomy policy first. This addendum narrows Qwen's
    residual tendency to replace exact note-supported labels with coarser labels.

    - Exact numeric preservation: if the note gives a specific count, range, or
      denominator, preserve it in the label. Do not replace "2 per day" with
      "multiple per day", "6 per week" with "multiple per week", "1 per 2 week"
      with "2 per month", or "10 per 6 month" with "10 per 5 month".
    - Explicit ranges remain ranges. Use "to" and the note's denominator:
      "2 to 3 per 2 week" remains "2 to 3 per 2 week"; do not compress it to
      "2 to 3 per week" or "multiple per week".
    - Cluster structure has priority over a simple rate whenever the note says
      seizures occur in clusters. Preserve both slots: cluster frequency and
      per-cluster count. Do not output a non-cluster rate if the note supports
      "N cluster per unit, M per cluster".
    - Per-cluster specificity: when the note states a per-cluster value, use
      that value instead of "multiple per cluster". Use "multiple per cluster"
      only when the per-cluster count is not stated.
    - Unknown is not a fallback for difficult arithmetic. Use "unknown" only
      when seizure frequency cannot be quantified from the note. If GPT-style
      exact arithmetic is possible from a count and window, emit the arithmetic
      label rather than "unknown".
    - Unknown/seizure-free boundary: do not convert unknown to seizure-free
      unless the note explicitly supports seizure freedom for at least 6 months.
      Do not convert seizure-free remission language to unknown when a qualifying
      seizure-free duration is stated.
    - Canonical surface discipline: never emit synonyms or shorthand such as
      "many per month", "monthly", or "q2-3wk". Convert them to the canonical
      Gan surface only when the note directly supports that surface.
"""


GAN_FREQUENCY_S0_QWEN_SCHEMA_VALIDITY_ADDENDUM = """
    Qwen schema-validity patch (v1.8; R1.1 restart gate):
    Apply v1.7 first, then enforce this canonical surface gate before emitting
    seizure_frequency_number. This patch targets schema validity only; it does
    not change Gan gold labels, scorer semantics, or the candidate-builder surface.

    - Multiplicity words: never emit "many per month", "many per week", or
      similar prose. Use the canonical keyword "multiple": "many per month" →
      "multiple per month".
    - Per-cluster-only surfaces are incomplete. If the note gives events per
      cluster but no cluster spacing, output "unknown, N per cluster"; e.g.
      "4 to 6 per cluster" → "unknown, 4 to 6 per cluster". If spacing is
      known, output the full two-slot cluster label:
      "N cluster per unit, M per cluster".
    - Canonical units are only day, week, month, and year. Do not emit "night",
      "nights", "hour", "quarter", or "fortnight" as units. Convert nightly
      to day, e.g. "1 per night" → "1 per day"; convert fortnight to
      "2 week" and quarter to "3 month".
    - "unknown, N per cluster" is the only valid "unknown, ..." suffix. Do not
      emit "unknown, 6 per hour" or "unknown, N per day/week/month/year"; if a
      rate is quantifiable, return the rate in canonical units.
    - Final self-check: if the label is not exactly one of the Gan formats
      listed above, repair the surface to a canonical Gan label before returning.
"""


GAN_FREQUENCY_S0_QWEN_HYBRID_RESOLUTION_ADDENDUM = """
    Qwen hybrid-resolution patch (v1.9; R9 hybrid resolution):
    Apply v1.8 first, then enforce this hybrid prevention gate:
    - Never prefix a canonical rate label with 'unknown,' (e.g. 'unknown, 2 per month',
      'unknown, multiple per day', 'unknown, 1 per week' are strictly invalid and forbidden).
    - If a rate is quantifiable from the note or candidates, output ONLY the canonical rate
      label (e.g., '2 per month'). If the rate cannot be quantified or is completely unknown,
      output ONLY 'unknown'.
    - Do not mix uncertainty prefixes with rate expressions. The only allowed comma-separated
      'unknown' suffix is 'unknown, N per cluster' (for cluster timing cases only).
"""


GAN_FREQUENCY_S0_UNKNOWN_OVERUSE_GUARD_ADDENDUM = """
    Unknown-overuse guard policy (v1.5 unknown_overuse_guard; C2 arm):
    Layered on top of the v1.4 error-taxonomy policy. Apply all existing v1.4
    rules first, then apply the following refinements for unknown/no-reference
    boundary cases:

    1. Quantified-window preservation: If the note gives a count of events in
       an explicit calendar window (e.g. 'N seizures in the past M months',
       'N per M weeks'), preserve the rate label even if the note also says
       'no further events since'. Override to 'unknown' ONLY if the window is
       trigger-conditioned (e.g. after medication withdrawal, following a
       single febrile episode), explicitly stated as exceptional, or shorter
       than two weeks with no follow-up window.

    2. Seizure-free vs unknown boundary: Use 'seizure free for N unit' when
       the note states documented freedom for at least 6 months with no
       intercurrent breakthrough event. Use 'unknown' when the note mentions
       seizure activity but no usable frequency denominator is available. If
       the note says 'no further events' without a duration, and no prior
       window count is available, use 'unknown'.

    3. No seizure frequency reference vs unknown: Use 'no seizure frequency
       reference' ONLY when the note has no current or recent epileptic
       seizure events at all (only remote history, childhood events, or
       non-epileptic episodes). Use 'unknown' when seizure activity is
       described but frequency cannot be quantified. Do NOT use 'unknown' as
       a fallback for notes with zero seizure context.
       Examples:
       - Admin/scheduling-only letter -> 'no seizure frequency reference'
       - 'clusters after poor sleep' with no counts -> 'unknown'
       - 'last seizure on DATE' without an ongoing rate -> 'unknown'
       - Childhood febrile seizures only, no current events -> check whether
         seizure freedom for many years applies ('seizure free for multiple
         year') rather than 'unknown'.

    4. Candidate-override discipline: If a deterministic temporal candidate
       is present, either accept it as the answer or emit a structured
       override reason. Valid override reasons:
       - 'no_current_evidence': candidate evidence is historical, not current.
       - 'historical_only': note clearly marks the event as past, not active.
       - 'trigger_conditioned_only': event was tied to a medication change
         or acute provocation only.
       Do NOT emit 'unknown' simply because the candidate rate seems
       low-frequency; override only when one of the above reasons applies.
       Worked example: candidate 'multiple per day' from an EEG window is
       current evidence and must be accepted, not overridden to 'unknown'.
"""


def resolve_gan_frequency_s0_extractor_prompt_version(
    prompt_version: str,
) -> str:
    if prompt_version == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_PROMPT_VERSION:
        return GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_ERROR_TAXONOMY_PROMPT_VERSION
    if prompt_version in {
        GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
        "gan_frequency_s0_direct_verify_repair_v2",
    }:
        return GAN_FREQUENCY_S0_DIRECT_GUARDRAILS_PROMPT_VERSION
    if prompt_version in {
        GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_PROMPT_VERSION,
        GAN_FREQUENCY_S0_ADJUDICATE_VERIFY_REPAIR_SPAN_CHECK_PROMPT_VERSION,
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION,
    }:
        return GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION
    return prompt_version


def resolve_gan_frequency_s0_verifier_prompt_version(
    prompt_version: str,
) -> str:
    if prompt_version == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_PROMPT_VERSION:
        return GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION
    if prompt_version in {
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION,
        GAN_FREQUENCY_S0_ADJUDICATE_VERIFY_REPAIR_SPAN_CHECK_PROMPT_VERSION,
    }:
        return GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION
    if prompt_version == GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION:
        return GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION
    return prompt_version


def build_gan_frequency_s0_extractor_signature(
    prompt_version: str = GAN_FREQUENCY_S0_DIRECT_GUARDRAILS_PROMPT_VERSION,
) -> type[GanFrequencyS0Signature]:
    if prompt_version == GAN_FREQUENCY_S0_SYNTHESIS_PORT_TEMPORAL_PROMPT_VERSION:
        doc = (
            "Extract the Gan seizure-frequency label and supporting evidence from a "
            "clinical note.\n\n    /no_think\n    Do not use hidden reasoning. Emit "
            "only the requested output fields.\n\n    "
            f"{GAN_FREQUENCY_SYNTHESIS_GUIDANCE}\n    - evidence_text must be an exact "
            "contiguous quote from the note when provided."
        )
        return type(
            "GanFrequencyS0SynthesisPortSignature",
            (GanFrequencyS0Signature,),
            {"__doc__": doc},
        )
    doc = GanFrequencyS0Signature.__doc__ or ""
    if prompt_version == GAN_FREQUENCY_S0_GUARDRAILS_PORT_TEMPORAL_PROMPT_VERSION:
        doc = doc + GAN_FREQUENCY_S0_GUARDRAILS_PORT_EXTRACTOR_ADDENDUM
        return type(
            "GanFrequencyS0GuardrailsPortSignature",
            (GanFrequencyS0Signature,),
            {"__doc__": doc},
        )
    if prompt_version in {
        GAN_FREQUENCY_S0_EVIDENCE_OPTIONAL_PROMPT_VERSION,
        GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION,
    }:
        doc = doc + GAN_FREQUENCY_S0_EVIDENCE_OPTIONAL_ADDENDUM
        return type(
            "GanFrequencyS0EvidenceOptionalExtractorSignature",
            (GanFrequencyS0Signature,),
            {"__doc__": doc},
        )
    if prompt_version in {
        GAN_FREQUENCY_S0_DIRECT_GUARDRAILS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
        GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
        GAN_FREQUENCY_S0_SYNTHESIS_PORT_TEMPORAL_PROMPT_VERSION,
        GAN_FREQUENCY_S0_GUARDRAILS_PORT_TEMPORAL_PROMPT_VERSION,
        "gan_frequency_s0_direct_verify_repair_v2",
        "gan_frequency_s0_v1",
    }:
        return GanFrequencyS0Signature
    if prompt_version == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION:
        doc = (GanFrequencyS0Signature.__doc__ or "") + (
            GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_CANONICAL_EXAMPLES_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_CANONICAL_FORMAT_EXAMPLES_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateCanonicalExamplesExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_SLOT_PAYLOAD_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_SLOT_PAYLOAD_ADJUDICATE_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateSlotPayloadExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_ERROR_TAXONOMY_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateErrorTaxonomyExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_COMPACT_HIERARCHY_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_COMPACT_HIERARCHY_POLICY_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateCompactHierarchyExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_TARGETED_EXAMPLES_MIN7_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_TARGETED_EXAMPLES_MIN7_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateTargetedExamplesMin7ExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_QWEN_EXACT_POLICY_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_QWEN_EXACT_POLICY_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateQwenExactPolicyExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_QWEN_SCHEMA_VALIDITY_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_QWEN_EXACT_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_QWEN_SCHEMA_VALIDITY_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateQwenSchemaValidityExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_QWEN_HYBRID_RESOLUTION_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_QWEN_EXACT_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_QWEN_SCHEMA_VALIDITY_ADDENDUM
            + GAN_FREQUENCY_S0_QWEN_HYBRID_RESOLUTION_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateQwenHybridResolutionExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if (
        prompt_version
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_UNKNOWN_OVERUSE_GUARD_PROMPT_VERSION
    ):
        doc = (
            (GanFrequencyS0Signature.__doc__ or "")
            + GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_UNKNOWN_OVERUSE_GUARD_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateUnknownOveruseGuardExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if prompt_version in {
        GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION,
        GAN_FREQUENCY_S0_ADJUDICATE_VERIFY_REPAIR_SPAN_CHECK_PROMPT_VERSION,
        GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_PROMPT_VERSION,
    }:
        doc = (GanFrequencyS0Signature.__doc__ or "") + (
            GAN_FREQUENCY_S0_TEMPORAL_ADJUDICATE_EXTRACTOR_ADDENDUM
        )
        return type(
            "GanFrequencyS0TemporalAdjudicateExecutorExtractorSignature",
            (GanFrequencyS0TemporalAdjudicateSignature,),
            {"__doc__": doc},
        )
    if prompt_version in {
        GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_V1_2_GUARDRAILS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_TOOL_DATE_RESOLVER_SINGLE_PASS_PROMPT_VERSION,
        GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_PROMPT_VERSION,
    }:
        doc = (
            (GanFrequencyS0DateEventsAdjudicateSignature.__doc__ or "")
            + GAN_FREQUENCY_S0_DATE_EVENTS_ADJUDICATE_EXTRACTOR_ADDENDUM
            + GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_CANONICAL_FORMAT_EXAMPLES_ADDENDUM
        )
        return type(
            "GanFrequencyS0DateEventsAdjudicateEnhancedSignature",
            (GanFrequencyS0DateEventsAdjudicateSignature,),
            {"__doc__": doc},
        )
    if prompt_version == GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_V1_2B_SCHEMA_GUARD_ONLY_PROMPT_VERSION:
        # Ablation: schema guard only — no relative anchor guardrail. Used to isolate its 4.2pp cost.
        doc = (
            (GanFrequencyS0DateEventsAdjudicateSignature.__doc__ or "")
            + GAN_FREQUENCY_S0_DATE_EVENTS_ADJUDICATE_EXTRACTOR_SCHEMA_GUARD_ONLY_ADDENDUM
            + GAN_FREQUENCY_S0_ERROR_TAXONOMY_POLICY_ADDENDUM
            + GAN_FREQUENCY_S0_CANONICAL_FORMAT_EXAMPLES_ADDENDUM
        )
        return type(
            "GanFrequencyS0DateEventsAdjudicateSchemaGuardOnlySignature",
            (GanFrequencyS0DateEventsAdjudicateSignature,),
            {"__doc__": doc},
        )
    raise ValueError(f"Unsupported Gan S0 extractor prompt version: {prompt_version!r}")



def build_gan_frequency_s0_verifier_signature(
    prompt_version: str = GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
    *,
    temporal: bool = False,
) -> type[GanFrequencyS0VerifierSignature]:
    base_cls = (
        GanFrequencyS0TemporalVerifierSignature
        if temporal
        else GanFrequencyS0VerifierSignature
    )
    doc = base_cls.__doc__ or ""
    if prompt_version == GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_PROMPT_VERSION:
        doc = doc + GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_ADDENDUM
        name = (
            "GanFrequencyS0TemporalConfirmOnlyVerifierSignature"
            if temporal
            else "GanFrequencyS0ConfirmOnlyVerifierSignature"
        )
        return type(name, (base_cls,), {"__doc__": doc})
    if prompt_version in GAN_FREQUENCY_S0_ADJUDICATE_VR_SPAN_CHECK_PROMPT_VERSIONS:
        doc = doc + GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_VERIFIER_ADDENDUM
        name = (
            "GanFrequencyS0TemporalAdjudicateSpanCheckVerifierSignature"
            if temporal
            else "GanFrequencyS0AdjudicateSpanCheckVerifierSignature"
        )
        return type(name, (base_cls,), {"__doc__": doc})
    if prompt_version == GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION:
        doc = doc + GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_VERIFIER_ADDENDUM
        name = (
            "GanFrequencyS0TemporalEvidenceSpanCheckVerifierSignature"
            if temporal
            else "GanFrequencyS0EvidenceSpanCheckVerifierSignature"
        )
        return type(name, (base_cls,), {"__doc__": doc})
    if prompt_version == GAN_FREQUENCY_S0_EVIDENCE_OPTIONAL_PROMPT_VERSION:
        doc = doc + GAN_FREQUENCY_S0_EVIDENCE_OPTIONAL_ADDENDUM
        name = (
            "GanFrequencyS0TemporalEvidenceOptionalVerifierSignature"
            if temporal
            else "GanFrequencyS0EvidenceOptionalVerifierSignature"
        )
        return type(name, (base_cls,), {"__doc__": doc})
    if prompt_version in {
        GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
        GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
        GAN_FREQUENCY_S0_SYNTHESIS_PORT_TEMPORAL_PROMPT_VERSION,
        GAN_FREQUENCY_S0_GUARDRAILS_PORT_TEMPORAL_PROMPT_VERSION,
        "gan_frequency_s0_direct_verify_repair_v2",
    }:
        return base_cls
    raise ValueError(f"Unsupported Gan S0 verifier prompt version: {prompt_version!r}")


class GanFrequencyS0TemporalVerifierModule(dspy.Module):
    """Verifier that receives deterministic temporal-candidate structure."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        signature_cls = build_gan_frequency_s0_verifier_signature(
            prompt_version,
            temporal=True,
        )
        self.verify = dspy.Predict(signature_cls)

    def forward(
        self,
        note_text: str,
        initial_label: str | None,
        initial_evidence: str | None,
        temporal_candidates: str,
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_label=initial_label,
            initial_evidence=initial_evidence,
            temporal_candidates=temporal_candidates,
        )


class GanFrequencyS0TemporalCandidatesVerifyRepairModule(dspy.Module):
    """Direct extraction plus temporal-candidate-aware verify/repair."""

    def __init__(
        self,
        extractor_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        extractor_prompt_version = resolve_gan_frequency_s0_extractor_prompt_version(
            prompt_version
        )
        self.extractor = build_gan_s0_module(
            extractor_variant,
            prompt_version=extractor_prompt_version,
        )
        self.verifier = GanFrequencyS0TemporalVerifierModule(prompt_version=prompt_version)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.extractor(note_text=note_text)
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        if self.prompt_version == GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION:
            verified = _apply_evidence_span_check_guard(
                note_text,
                verified,
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
            )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
            temporal_candidate_labels=[c.canonical_label for c in candidates],
            temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
        )


def _prompt_note_text_for_context_policy(
    note_text: str,
    candidates: list[Any],
    *,
    context_policy: str,
) -> str:
    """Assemble prompt-visible note text for retrieval/context-selection arms."""

    if context_policy == GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY:
        spans: list[str] = []
        seen: set[str] = set()
        for candidate in candidates:
            evidence = getattr(candidate, "evidence_text", "")
            if evidence and evidence not in seen:
                seen.add(evidence)
                spans.append(evidence)
        if spans:
            return "\n\n---\n\n".join(spans)
        return GAN_FREQUENCY_S0_RETRIEVAL_EMPTY_CANDIDATES_NOTE_STUB
    return note_text


class GanFrequencyS0TemporalCandidatesSinglePassModule(dspy.Module):
    """Deterministic temporal candidates followed by a single LLM adjudication pass."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
        candidate_presentation: str | None = None,
        context_policy: str = (
            GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.candidate_presentation = candidate_presentation
        self.context_policy = context_policy
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            TemporalCandidatePresentation,
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        presentation: TemporalCandidatePresentation = (
            self.candidate_presentation or "prose"
        )
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            presentation=presentation,
        )
        prompt_note_text = _prompt_note_text_for_context_policy(
            note_text,
            candidates,
            context_policy=self.context_policy,
        )
        result = self.adjudicate(
            note_text=prompt_note_text,
            temporal_candidates=temporal_candidates_text,
        )
        return _temporal_adjudication_prediction(
            result,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            candidate_source="deterministic",
            extra_metadata={
                "context_policy": self.context_policy,
                "prompt_note_text_is_full_note": (
                    self.context_policy
                    != GAN_CONTEXT_POLICY_DETERMINISTIC_TEMPORAL_CANDIDATES_ONLY
                ),
                "prompt_note_text_char_count": len(prompt_note_text),
                "source_note_text_char_count": len(note_text),
            },
        )


def _build_gan_frequency_s0_llm_candidate_generator_signature() -> type[
    GanFrequencyS0LlmTemporalCandidatesSignature
]:
    doc = (GanFrequencyS0LlmTemporalCandidatesSignature.__doc__ or "") + (
        GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_GENERATOR_ADDENDUM
    )
    return type(
        "GanFrequencyS0LlmTemporalCandidatesGeneratorSignature",
        (GanFrequencyS0LlmTemporalCandidatesSignature,),
        {"__doc__": doc},
    )


class GanFrequencyS0LlmTemporalCandidatesGeneratorModule(dspy.Module):
    """Model pass that emits structured temporal frequency candidates."""

    def __init__(self) -> None:
        super().__init__()
        signature_cls = _build_gan_frequency_s0_llm_candidate_generator_signature()
        self.generate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.generate(note_text=note_text)


def _temporal_adjudication_prediction(
    result: dspy.Prediction,
    *,
    candidates: list[Any],
    temporal_candidates_text: str,
    candidate_source: str,
    llm_candidate_records: list[dict[str, str]] | None = None,
    extra_metadata: dict[str, Any] | None = None,
) -> dspy.Prediction:
    from clinical_extraction.gan.temporal_candidates import temporal_candidate_to_dict

    metadata: dict[str, Any] = {
        "seizure_frequency_number": result.seizure_frequency_number,
        "evidence_text": result.evidence_text,
        "temporal_candidates": temporal_candidates_text,
        "temporal_candidate_labels": [c.canonical_label for c in candidates],
        "temporal_candidate_records": [
            temporal_candidate_to_dict(candidate) for candidate in candidates
        ],
        "temporal_candidate_source": candidate_source,
    }
    if llm_candidate_records is not None:
        metadata["llm_temporal_candidate_records"] = llm_candidate_records
    if extra_metadata:
        metadata.update(extra_metadata)
    return dspy.Prediction(**metadata)


def _synthetic_confirm_from_adjudicate(
    *,
    initial_label: str | None,
    initial_evidence: str | None,
    reason: str,
) -> dspy.Prediction:
    return dspy.Prediction(
        final_label=initial_label,
        final_evidence=initial_evidence,
        decision="confirm",
        reason=reason,
    )


def _apply_det_evidence_grounding(
    note_text: str,
    *,
    initial_label: str | None,
    initial_evidence: str | None,
) -> dspy.Prediction:
    """Deterministic in-note evidence check before plausibility guards (ladder V3+)."""
    if initial_label in (None, "no seizure frequency reference"):
        return _synthetic_confirm_from_adjudicate(
            initial_label=initial_label,
            initial_evidence=initial_evidence,
            reason="Det evidence grounding skipped for abstain/no-reference.",
        )
    feedback = _evidence_policy_feedback(
        gold_label=initial_label,
        predicted_evidence=initial_evidence,
        note_text=note_text,
    )
    if feedback is None:
        return _synthetic_confirm_from_adjudicate(
            initial_label=initial_label,
            initial_evidence=initial_evidence,
            reason="Det evidence grounding passed.",
        )
    return dspy.Prediction(
        final_label=None,
        final_evidence=None,
        decision="abstain",
        reason=f"Det evidence grounding abstained: {feedback}",
    )


def _prediction_from_temporal_adjudicate_validation(
    *,
    initial_label: str | None,
    initial_evidence: str | None,
    verified: dspy.Prediction,
    candidates: list[Any],
    temporal_candidates_text: str,
    validation_ladder_rung: str,
) -> dspy.Prediction:
    from clinical_extraction.gan.temporal_candidates import temporal_candidate_to_dict

    return dspy.Prediction(
        seizure_frequency_number=verified.final_label,
        evidence_text=verified.final_evidence,
        verifier_decision=verified.decision,
        verifier_reason=verified.reason,
        initial_label=initial_label,
        initial_evidence=initial_evidence,
        temporal_candidates=temporal_candidates_text,
        temporal_candidate_labels=[c.canonical_label for c in candidates],
        temporal_candidate_records=[
            temporal_candidate_to_dict(candidate) for candidate in candidates
        ],
        temporal_candidate_source="deterministic",
        validation_ladder_rung=validation_ladder_rung,
    )


def _llm_temporal_candidates_from_prediction(
    note_text: str,
    prediction: dspy.Prediction,
) -> list[Any]:
    from clinical_extraction.gan.temporal_candidates import (
        parse_llm_temporal_candidates_json,
    )

    return parse_llm_temporal_candidates_json(
        prediction.temporal_candidates_json,
        note_text=note_text,
    )


class GanFrequencyS0LlmTemporalCandidatesSinglePassModule(dspy.Module):
    """LLM temporal candidates followed by a single LLM adjudication pass."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.candidate_generator = GanFrequencyS0LlmTemporalCandidatesGeneratorModule()
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )

        generated = self.candidate_generator(note_text=note_text)
        candidates = _llm_temporal_candidates_from_prediction(note_text, generated)
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            source="llm",
        )
        result = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        return _temporal_adjudication_prediction(
            result,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            candidate_source="llm",
            llm_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
        )


class GanFrequencyS0HybridTemporalCandidatesSinglePassModule(dspy.Module):
    """Merged deterministic+LLM temporal candidates with LLM adjudication."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.candidate_generator = GanFrequencyS0LlmTemporalCandidatesGeneratorModule()
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
            merge_temporal_frequency_candidates,
            temporal_candidate_to_dict,
        )

        deterministic_candidates = build_temporal_frequency_candidates_from_note(
            note_text
        )
        generated = self.candidate_generator(note_text=note_text)
        llm_candidates = _llm_temporal_candidates_from_prediction(note_text, generated)
        candidates = merge_temporal_frequency_candidates(
            deterministic_candidates,
            llm_candidates,
        )
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            source="hybrid",
        )
        result = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        return _temporal_adjudication_prediction(
            result,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            candidate_source="hybrid",
            llm_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in llm_candidates
            ],
        )


from clinical_extraction.schemas import FrozenModel
from pydantic import Field

class GanDateEventPayload(FrozenModel):
    clinic_date: str | None = None
    temporal_anchors: list[str] = Field(default_factory=list)
    seizure_events: list[str] = Field(default_factory=list)
    seizure_free_intervals: list[str] = Field(default_factory=list)
    cluster_events: list[str] = Field(default_factory=list)
    current_window_cues: list[str] = Field(default_factory=list)
    candidate_labels: list[str] = Field(default_factory=list)
    evidence_text: str | None = None
    stage_confidence: float | None = None
    calculated_arithmetic: str | None = None

def run_arithmetic_calculator(note_text: str) -> tuple[str, str] | None:
    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
    }
    number_words_map = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    
    # 1. Segmented monthly series (e.g. In Nov he had 3 ... In Jan he had 5)
    month_pattern = r"\b(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\b"
    month_mentions = []
    for m in re.finditer(month_pattern, note_text, re.IGNORECASE):
        m_name = m.group(1).lower()
        month_mentions.append((month_map[m_name], m.start(), m.end()))
        
    if len(month_mentions) >= 2:
        segments = []
        for i in range(len(month_mentions)):
            start_pos = month_mentions[i][2]
            end_pos = month_mentions[i+1][1] if i + 1 < len(month_mentions) else len(note_text)
            seg_text = note_text[start_pos:end_pos]
            period_idx = seg_text.find('.')
            if period_idx != -1:
                seg_text = seg_text[:period_idx]
            segments.append((month_mentions[i][0], seg_text))
            
        parsed_series = []
        number_pattern = r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b"
        for m_num, seg_text in segments:
            counts = []
            for num_match in re.finditer(number_pattern, seg_text, re.IGNORECASE):
                val_str = num_match.group(1)
                if val_str.isdigit():
                    val = int(val_str)
                    if 2020 <= val <= 2030:
                        continue
                else:
                    val = number_words_map.get(val_str.lower(), 0)
                counts.append(val)
            if counts:
                parsed_series.append((m_num, sum(counts)))
                
        if len(parsed_series) >= 2:
            total = sum(x[1] for x in parsed_series)
            years = [0]
            for i in range(1, len(parsed_series)):
                prev_m = parsed_series[i-1][0]
                curr_m = parsed_series[i][0]
                if curr_m < prev_m:
                    years.append(years[-1] + 1)
                else:
                    years.append(years[-1])
            start_idx = 0
            end_idx = len(parsed_series) - 1
            month_span = (years[end_idx] - years[start_idx]) * 12 + parsed_series[end_idx][0] - parsed_series[start_idx][0] + 1
            if month_span > 0:
                lbl = f"{total} per {month_span} month" if month_span > 1 else f"{total} per month"
                deriv = f"Summed monthly series ({' + '.join(str(x[1]) for x in parsed_series)} = {total}) over {month_span} months"
                return lbl, deriv

    # 2. Co-occurring event tally (e.g. two drop attacks and five tonic-clonic in past three months)
    window_match = re.search(
        r"(?:in|over|during)\s+(?:the\s+)?(?:past|last)\s+(\d+|one|two|three|four|five|six|seven|eight|nine|ten)?\s*(month|week|year)s?",
        note_text, re.IGNORECASE
    )
    if window_match:
        window_start = window_match.start()
        window_str = window_match.group(1)
        unit = window_match.group(2).lower()
        
        pre_text = note_text[max(0, window_start - 150):window_start]
        number_pattern = r"\b(\d+|one|two|three|four|five|six|seven|eight|nine|ten)\b"
        matches = list(re.finditer(number_pattern, pre_text, re.IGNORECASE))
        if len(matches) >= 2:
            total = 0
            for m in matches:
                val_str = m.group(1)
                if val_str.isdigit():
                    total += int(val_str)
                else:
                    total += number_words_map.get(val_str.lower(), 0)
            
            w = int(window_str) if (window_str and window_str.isdigit()) else number_words_map.get((window_str or "").lower(), 1)
            if total > 0:
                lbl = f"{total} per {w} {unit}" if w > 1 else f"{total} per {unit}"
                deriv = f"Summed co-occurring event types ({' + '.join(m.group(1) for m in matches)} = {total}) over {w} {unit}"
                return lbl, deriv

    return None

def validate_and_fallback_label(label: str | None) -> str | None:
    if label is None:
        return None
    from clinical_extraction.gan.frequency import gan_label_policy_failure_class
    fail_class = gan_label_policy_failure_class(label)
    if fail_class in {"unknown_quantified_hybrid", "malformed_cluster_unknown_slot"}:
        return "unknown"
    return label

def build_deterministic_date_event_payload(note_text: str) -> GanDateEventPayload:
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
        _clinic_date,
    )
    candidates = list(build_temporal_frequency_candidates_from_note(note_text))
    
    # Arithmetic calculator: run for diagnostic reporting only (v1.3: not injected as candidates
    # because the month-series parser fires on non-seizure month mentions, adding spurious candidates).
    arith_res = run_arithmetic_calculator(note_text)
    calculated_arithmetic = None
    if arith_res:
        lbl, deriv = arith_res
        calculated_arithmetic = f"{lbl} (derived via: {deriv})"
        # NOTE: calculator result is stored in calculated_arithmetic for prompt context
        # but NOT appended to candidates to avoid spurious candidate injection.
    
    clinic_d = _clinic_date(note_text)
    clinic_date_str = clinic_d.isoformat() if clinic_d else None
    
    temporal_anchors = []
    seizure_events = []
    seizure_free_intervals = []
    cluster_events = []
    current_window_cues = []
    candidate_labels = []
    evidence_pieces = []
    
    for c in candidates:
        candidate_labels.append(c.canonical_label)
        if c.evidence_text:
            evidence_pieces.append(c.evidence_text)
        
        label_lower = c.canonical_label.lower()
        if "seizure free" in label_lower or "seizure-free" in label_lower:
            seizure_free_intervals.append(f"{c.canonical_label} (based on: {c.evidence_text!r})")
        elif "cluster" in label_lower:
            cluster_events.append(f"{c.canonical_label} (based on: {c.evidence_text!r})")
        else:
            seizure_events.append(f"{c.canonical_label} (based on: {c.evidence_text!r})")
            
        if c.derivation:
            current_window_cues.append(c.derivation)
            
    if clinic_date_str:
        temporal_anchors.append(f"clinic_date={clinic_date_str}")
        
    unique_evidence = list(dict.fromkeys(evidence_pieces))
    evidence_text = " | ".join(unique_evidence) if unique_evidence else None
    
    return GanDateEventPayload(
        clinic_date=clinic_date_str,
        temporal_anchors=list(dict.fromkeys(temporal_anchors)),
        seizure_events=list(dict.fromkeys(seizure_events)),
        seizure_free_intervals=list(dict.fromkeys(seizure_free_intervals)),
        cluster_events=list(dict.fromkeys(cluster_events)),
        current_window_cues=list(dict.fromkeys(current_window_cues)),
        candidate_labels=list(dict.fromkeys(candidate_labels)),
        evidence_text=evidence_text,
        stage_confidence=1.0,
        calculated_arithmetic=calculated_arithmetic,
    )

GAN_FREQUENCY_S0_DATE_EVENTS_ADJUDICATE_EXTRACTOR_ADDENDUM = """
    Date-event payload adjudication policy (v1.2):
    - date_event_payload lists clinic date, temporal anchors, seizure events,
      seizure-free intervals, cluster events, current window cues, candidate labels,
      evidence text, and calculated arithmetic totals/denominators extracted from the note.
    - Treat candidate_labels as diagnostic hints, not gold labels.
    - Prefer note-supported quantified rates from candidates when they match the
      note's event/window structure.
    - Do calendar math: calculate the exact number of months between the clinic date
      and the start date of any seizure-free period or event onset. Use this calculated
      number as the denominator (e.g. 'multiple per 15 month').
    - Identify minor active events: if a note describes generalised seizure freedom
      but describes ongoing myoclonic jerks, brief jumps, or absences, count these
      as active events rather than classifying the patient as seizure-free. If the
      candidates list includes 'multiple per [months] month', you MUST select
      'multiple per [months] month' (e.g., 'multiple per 15 month') as the primary label.
      Do NOT collapse this to unknown or seizure-free.
    - Cluster labels must include both cluster period and per-cluster count.
    - evidence_text must be an exact contiguous substring of note_text.
    - Strict Label Schema Guard: You MUST NOT output hybrid labels containing 'unknown' combined with numbers or units (e.g., '3 per unknown', 'unknown per month', or 'unknown cluster per month'). The only valid ways to use 'unknown' are as the standalone label 'unknown' or in the cluster format 'unknown, multiple per cluster' / 'unknown, N per cluster'. If the event count or the window unit/denominator is unknown, output the standalone label 'unknown'.
    - Ambiguity & Relative Anchor Guardrail: If a note describes events occurring "since starting [medication]", "since beginning [treatment]", "since discharge", or "since last visit" without providing an explicit, documented start date/anchor (e.g., month/year or date), you MUST NOT guess a denominator or calculate a calendar-window using the latest event date or clinic date. In all such unanchored relative cases, output 'unknown' per Gan policy.
    - Trigger-dependent or vague recurrence guardrail: If the note states that seizures only happen after specific triggers (e.g., lack of sleep, illness, travel) but does not state the frequency of those triggers, the overall frequency is unquantifiable. You MUST output 'unknown' rather than estimating a rate.
"""

# Schema-guard-only addendum (v1.2b): strips the relative anchor guardrail to isolate its impact.
# Used for ablation: if full-validation accuracy recovers to ~79.5%, anchor guardrail owns the 4.2pp delta.
GAN_FREQUENCY_S0_DATE_EVENTS_ADJUDICATE_EXTRACTOR_SCHEMA_GUARD_ONLY_ADDENDUM = """
    Date-event payload adjudication policy (v1.2b — schema guard only):
    - date_event_payload lists clinic date, temporal anchors, seizure events,
      seizure-free intervals, cluster events, current window cues, candidate labels,
      evidence text, and calculated arithmetic totals/denominators extracted from the note.
    - Treat candidate_labels as diagnostic hints, not gold labels.
    - Prefer note-supported quantified rates from candidates when they match the
      note's event/window structure.
    - Do calendar math: calculate the exact number of months between the clinic date
      and the start date of any seizure-free period or event onset. Use this calculated
      number as the denominator (e.g. 'multiple per 15 month').
    - Identify minor active events: if a note describes generalised seizure freedom
      but describes ongoing myoclonic jerks, brief jumps, or absences, count these
      as active events rather than classifying the patient as seizure-free. If the
      candidates list includes 'multiple per [months] month', you MUST select
      'multiple per [months] month' (e.g., 'multiple per 15 month') as the primary label.
      Do NOT collapse this to unknown or seizure-free.
    - Cluster labels must include both cluster period and per-cluster count.
    - evidence_text must be an exact contiguous substring of note_text.
    - Strict Label Schema Guard: You MUST NOT output hybrid labels containing 'unknown' combined with numbers or units (e.g., '3 per unknown', 'unknown per month', or 'unknown cluster per month'). The only valid ways to use 'unknown' are as the standalone label 'unknown' or in the cluster format 'unknown, multiple per cluster' / 'unknown, N per cluster'. If the event count or the window unit/denominator is unknown, output the standalone label 'unknown'.
    - Trigger-dependent or vague recurrence guardrail: If the note states that seizures only happen after specific triggers (e.g., lack of sleep, illness, travel) but does not state the frequency of those triggers, the overall frequency is unquantifiable. You MUST output 'unknown' rather than estimating a rate.
"""

class GanFrequencyS0DateEventsExtractionSignature(dspy.Signature):
    """Extract date anchors, seizure events, cluster events, and seizure-free intervals from a note.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    Output the date_event_payload as a JSON object matching the requested schema.
    
    JSON Schema fields:
    - clinic_date: ISO date (YYYY-MM-DD) or null.
    - temporal_anchors: List of string date/time reference anchors in the note.
    - seizure_events: List of candidate rate strings with raw text references, e.g., "N per day/week/month/year (based on: '...')" or "N per M day/week/month/year (based on: '...')".
    - seizure_free_intervals: List of seizure-free intervals, e.g., "seizure free for N day/week/month/year (based on: '...')" (N >= 6 months).
    - cluster_events: List of cluster events, e.g., "N cluster per day/week/month/year, M per cluster (based on: '...')".
    - current_window_cues: List of window or calculation cues.
    - candidate_labels: List of canonical Gan frequency label candidates. EVERY candidate label in this list MUST match the exact canonical Gan frequency vocabulary:
      * 'N per [day/week/month/year]'
      * 'N to M per [day/week/month/year]'
      * 'N per M [day/week/month/year]'
      * 'N cluster per [day/week/month/year], M per cluster'
      * 'seizure free for N [day/week/month/year]' (only when N >= 6 months)
      * 'unknown'
      * 'no seizure frequency reference'
      
      CRITICAL VOCABULARY AND MATH INSTRUCTIONS:
      1. Use concrete units (day, week, month, year). Do not use the word 'unit'.
      2. Perform calendar month subtraction: calculate the exact number of months between the clinic date (e.g., Dec 2019) and the start date of any seizure-free period or event onset (e.g., Sep 2018 -> 15 months). Use this calculated number as the denominator (e.g. 'multiple per 15 month').
      3. Identify minor active events: if a note describes generalised seizure freedom but describes ongoing myoclonic jerks, brief jumps, or absences, count these as active events rather than classifying the patient as seizure-free (e.g. 'multiple per 15 month').
      4. Do NOT output raw medical/clinical entity tags (like "generalised tonic-clonic seizure" or "Valproate treatment") in candidate_labels. Only output valid seizure frequency rates or "unknown" / "no seizure frequency reference".
    - evidence_text: Shortest exact contiguous quote containing all the extracted events and windows.
    - stage_confidence: float (1.0).

    Worked Examples for candidate_labels generation:
    - 'remained seizure-free for seven months ... before experiencing a generalised tonic-clonic seizure 3 Tuesdays ago, preceded by absences' -> candidate_labels: ["2 per 7 month"]
    - 'She had no seizures for nearly a year ... then developed myoclonic jerks leading to a tonic seizure three Saturdays ago' -> candidate_labels: ["1 per year"]
    - 'she experienced two to four seizures in the following month' -> candidate_labels: ["2 to 4 per month"]
    - 'No further tonic-clonic seizures have occurred since Feb 2021, although one or two single jerks remain (now April 2022, 14 months later)' -> candidate_labels: ["1 to 2 per 14 month"]
    - 'typically has 1 to 2 seizures per month' -> candidate_labels: ["1 to 2 per month"]
    - 'seizure free for years' -> candidate_labels: ["seizure free for multiple year"]
    """
    note_text: str = dspy.InputField(desc="Clinical note text")
    date_event_payload_json: str = dspy.OutputField(
        desc="JSON object containing clinic_date, temporal_anchors, seizure_events, seizure_free_intervals, cluster_events, current_window_cues, candidate_labels, evidence_text, stage_confidence"
    )

class GanFrequencyS0DateEventsAdjudicateSignature(GanFrequencyS0Signature):
    """Adjudicate Gan seizure frequency with a specialist date/event payload.
    
    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.
    """
    date_event_payload: str = dspy.InputField(
        desc="JSON object containing clinic_date, temporal_anchors, seizure_events, seizure_free_intervals, cluster_events, current_window_cues, candidate_labels, evidence_text, stage_confidence"
    )

class GanFrequencyS0DateEventsCandidatesSinglePassModule(dspy.Module):
    """Deterministic date/event extraction followed by a single LLM adjudication pass."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        payload = build_deterministic_date_event_payload(note_text)
        payload_json = payload.model_dump_json(indent=2)
        
        result = self.adjudicate(
            note_text=note_text,
            date_event_payload=payload_json,
        )
        final_lbl = validate_and_fallback_label(result.seizure_frequency_number)
        return dspy.Prediction(
            seizure_frequency_number=final_lbl,
            evidence_text=result.evidence_text,
            date_event_payload=payload_json,
            temporal_candidate_labels=payload.candidate_labels,
        )

class GanFrequencyS0LlmDateEventsCandidatesSinglePassModule(dspy.Module):
    """LLM date/event extraction followed by single LLM adjudication."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.extractor = dspy.ChainOfThought(GanFrequencyS0DateEventsExtractionSignature)
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        extracted = self.extractor(note_text=note_text)
        payload_json = extracted.date_event_payload_json
        
        try:
            raw = json.loads(payload_json)
            candidate_labels = raw.get("candidate_labels", [])
        except Exception:
            candidate_labels = []
            
        result = self.adjudicate(
            note_text=note_text,
            date_event_payload=payload_json,
        )
        final_lbl = validate_and_fallback_label(result.seizure_frequency_number)
        return dspy.Prediction(
            seizure_frequency_number=final_lbl,
            evidence_text=result.evidence_text,
            date_event_payload=payload_json,
            temporal_candidate_labels=candidate_labels,
        )

class GanFrequencyS0HybridDateEventsCandidatesSinglePassModule(dspy.Module):
    """Deterministic + LLM date/events merge followed by LLM adjudication."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.extractor = dspy.ChainOfThought(GanFrequencyS0DateEventsExtractionSignature)
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        det_payload = build_deterministic_date_event_payload(note_text)
        extracted = self.extractor(note_text=note_text)
        llm_payload_json = extracted.date_event_payload_json
        
        temporal_anchors = list(det_payload.temporal_anchors)
        seizure_events = list(det_payload.seizure_events)
        seizure_free_intervals = list(det_payload.seizure_free_intervals)
        cluster_events = list(det_payload.cluster_events)
        current_window_cues = list(det_payload.current_window_cues)
        candidate_labels = list(det_payload.candidate_labels)
        
        try:
            raw = json.loads(llm_payload_json)
            if isinstance(raw.get("temporal_anchors"), list):
                temporal_anchors.extend(raw["temporal_anchors"])
            if isinstance(raw.get("seizure_events"), list):
                seizure_events.extend(raw["seizure_events"])
            if isinstance(raw.get("seizure_free_intervals"), list):
                seizure_free_intervals.extend(raw["seizure_free_intervals"])
            if isinstance(raw.get("cluster_events"), list):
                cluster_events.extend(raw["cluster_events"])
            if isinstance(raw.get("current_window_cues"), list):
                current_window_cues.extend(raw["current_window_cues"])
            if isinstance(raw.get("candidate_labels"), list):
                candidate_labels.extend(raw["candidate_labels"])
        except Exception:
            pass

        def to_str(x):
            if isinstance(x, str):
                return x
            if isinstance(x, dict):
                return x.get("text") or x.get("label") or json.dumps(x)
            return str(x)

        temporal_anchors = [to_str(x) for x in temporal_anchors]
        seizure_events = [to_str(x) for x in seizure_events]
        seizure_free_intervals = [to_str(x) for x in seizure_free_intervals]
        cluster_events = [to_str(x) for x in cluster_events]
        current_window_cues = [to_str(x) for x in current_window_cues]
        candidate_labels = [to_str(x) for x in candidate_labels]
            
        merged_payload = GanDateEventPayload(
            clinic_date=det_payload.clinic_date,
            temporal_anchors=list(dict.fromkeys(temporal_anchors)),
            seizure_events=list(dict.fromkeys(seizure_events)),
            seizure_free_intervals=list(dict.fromkeys(seizure_free_intervals)),
            cluster_events=list(dict.fromkeys(cluster_events)),
            current_window_cues=list(dict.fromkeys(current_window_cues)),
            candidate_labels=list(dict.fromkeys(candidate_labels)),
            evidence_text=det_payload.evidence_text,
            stage_confidence=1.0,
        )
        payload_json = merged_payload.model_dump_json(indent=2)
        
        result = self.adjudicate(
            note_text=note_text,
            date_event_payload=payload_json,
        )
        final_lbl = validate_and_fallback_label(result.seizure_frequency_number)
        return dspy.Prediction(
            seizure_frequency_number=final_lbl,
            evidence_text=result.evidence_text,
            date_event_payload=payload_json,
            temporal_candidate_labels=merged_payload.candidate_labels,
        )

class GanFrequencyS0EntityTagsSignature(dspy.Signature):
    """Extract clinical entities and events with offsets and temporality context.
    
    Output entity_tags as a JSON object with key "entity_tags".
    """
    note_text: str = dspy.InputField(desc="Clinical note text")
    entity_tags_json: str = dspy.OutputField(
        desc='JSON object {"entity_tags": [...]} containing clinical entities, counts, and temporality hints'
    )

class GanFrequencyS0EntityTagsDateEventsSinglePassModule(dspy.Module):
    """LLM clinical entities/events tags -> Date/event payload -> Adjudicate."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.tagger = dspy.Predict(GanFrequencyS0EntityTagsSignature)
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        tagged = self.tagger(note_text=note_text)
        tags_json = tagged.entity_tags_json
        
        temporal_anchors = []
        seizure_events = []
        seizure_free_intervals = []
        cluster_events = []
        current_window_cues = []
        candidate_labels = []
        evidence_pieces = []
        
        try:
            raw = json.loads(tags_json)
            tags = raw.get("entity_tags", [])
            for tag in tags:
                etype = tag.get("entity_type")
                text = tag.get("text", "")
                hint = tag.get("temporality_hint", "")
                count_hint = tag.get("count_or_duration_hint")
                
                if text:
                    evidence_pieces.append(text)
                    
                display = f"{text}"
                if count_hint:
                    display += f" (count/duration: {count_hint})"
                if hint:
                    display += f" [{hint}]"
                    
                if etype == "temporal_anchor":
                    temporal_anchors.append(display)
                elif etype in ("seizure_free_status", "negation_or_absence"):
                    seizure_free_intervals.append(display)
                elif etype == "cluster":
                    cluster_events.append(display)
                elif etype in ("seizure_event", "seizure_frequency"):
                    seizure_events.append(display)
                elif etype in ("medication_change", "other_relevant_context"):
                    current_window_cues.append(display)
                
                if count_hint and etype in ("seizure_event", "seizure_frequency", "cluster"):
                    candidate_labels.append(count_hint)
        except Exception:
            pass
            
        from clinical_extraction.gan.temporal_candidates import _clinic_date
        clinic_d = _clinic_date(note_text)
        clinic_date_str = clinic_d.isoformat() if clinic_d else None
        if clinic_date_str:
            temporal_anchors.append(f"clinic_date={clinic_date_str}")
            
        payload = GanDateEventPayload(
            clinic_date=clinic_date_str,
            temporal_anchors=list(dict.fromkeys(temporal_anchors)),
            seizure_events=list(dict.fromkeys(seizure_events)),
            seizure_free_intervals=list(dict.fromkeys(seizure_free_intervals)),
            cluster_events=list(dict.fromkeys(cluster_events)),
            current_window_cues=list(dict.fromkeys(current_window_cues)),
            candidate_labels=list(dict.fromkeys(candidate_labels)),
            evidence_text=" | ".join(dict.fromkeys(evidence_pieces)) if evidence_pieces else None,
            stage_confidence=1.0,
        )
        payload_json = payload.model_dump_json(indent=2)
        
        result = self.adjudicate(
            note_text=note_text,
            date_event_payload=payload_json,
        )
        return dspy.Prediction(
            seizure_frequency_number=result.seizure_frequency_number,
            evidence_text=result.evidence_text,
            date_event_payload=payload_json,
            temporal_candidate_labels=payload.candidate_labels,
        )

class GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule(dspy.Module):
    """Adjudicate then deterministic plausibility guards only (validation ladder V2)."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _synthetic_confirm_from_adjudicate(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            reason="Synthetic confirm for det-plausibility rung (no LLM verifier).",
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="det_plausibility",
        )


class GanFrequencyS0TemporalCandidatesAdjudicateDetEvidenceModule(dspy.Module):
    """Adjudicate, deterministic evidence grounding, then plausibility guards (V3)."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_det_evidence_grounding(
            note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        if verified.decision != "abstain":
            verified = _apply_temporal_verifier_guards(
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
                verified=verified,
                candidates=candidates,
            )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="det_evidence_grounding",
        )


class GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule(dspy.Module):
    """V3 stack plus LLM verifier restricted to confirm-only (V4)."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        adjudicate_prompt = resolve_gan_frequency_s0_extractor_prompt_version(
            prompt_version
        )
        signature_cls = build_gan_frequency_s0_extractor_signature(adjudicate_prompt)
        self.adjudicate = dspy.Predict(signature_cls)
        verifier_prompt = resolve_gan_frequency_s0_verifier_prompt_version(prompt_version)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=verifier_prompt
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_det_evidence_grounding(
            note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        if verified.decision == "abstain":
            return _prediction_from_temporal_adjudicate_validation(
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
                verified=verified,
                candidates=candidates,
                temporal_candidates_text=temporal_candidates_text,
                validation_ladder_rung="llm_confirm_only",
            )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        verified = self.verifier(
            note_text=note_text,
            initial_label=verified.final_label,
            initial_evidence=verified.final_evidence,
            temporal_candidates=temporal_candidates_text,
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="llm_confirm_only",
        )


class GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairNoGuardsModule(dspy.Module):
    """Det evidence grounding plus full LLM verify-repair without post-VR guards (V5)."""

    def __init__(
        self,
        *,
        prompt_version: str = (
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        adjudicate_prompt = resolve_gan_frequency_s0_extractor_prompt_version(
            prompt_version
        )
        signature_cls = build_gan_frequency_s0_extractor_signature(adjudicate_prompt)
        self.adjudicate = dspy.Predict(signature_cls)
        verifier_prompt = resolve_gan_frequency_s0_verifier_prompt_version(prompt_version)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=verifier_prompt
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_det_evidence_grounding(
            note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        if verified.decision == "abstain":
            return _prediction_from_temporal_adjudicate_validation(
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
                verified=verified,
                candidates=candidates,
                temporal_candidates_text=temporal_candidates_text,
                validation_ladder_rung="llm_verify_repair",
            )
        verified = self.verifier(
            note_text=note_text,
            initial_label=verified.final_label,
            initial_evidence=verified.final_evidence,
            temporal_candidates=temporal_candidates_text,
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="llm_verify_repair",
        )


class GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairModule(dspy.Module):
    """Deterministic candidates, LLM adjudicate, then temporal verify-repair."""

    def __init__(
        self,
        *,
        prompt_version: str = (
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)
        verifier_prompt = resolve_gan_frequency_s0_verifier_prompt_version(prompt_version)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=verifier_prompt
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        if self.prompt_version in GAN_FREQUENCY_S0_ADJUDICATE_VR_SPAN_CHECK_PROMPT_VERSIONS:
            verified = _apply_evidence_span_check_guard(
                note_text,
                verified,
                initial_label=initial.seizure_frequency_number,
                initial_evidence=initial.evidence_text,
            )
        ladder_rung = (
            "llm_vr_det_guards_span_check"
            if self.prompt_version in GAN_FREQUENCY_S0_ADJUDICATE_VR_SPAN_CHECK_PROMPT_VERSIONS
            else "llm_verify_repair_det_guards"
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung=ladder_rung,
        )


class GanFrequencyS0TemporalCandidatesAdjudicateConstrainedVerifierModule(dspy.Module):
    """Deterministic candidates, LLM adjudicate, then constrained verify-repair."""

    def __init__(
        self,
        *,
        prompt_version: str = (
            GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_PROMPT_VERSION
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        extractor_prompt_version = resolve_gan_frequency_s0_extractor_prompt_version(prompt_version)
        signature_cls = build_gan_frequency_s0_extractor_signature(extractor_prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)
        verifier_prompt = resolve_gan_frequency_s0_verifier_prompt_version(prompt_version)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=verifier_prompt
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_constrained_verifier_guard(
            note_text=note_text,
            verified=verified,
            candidates=candidates,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
        )
        return _prediction_from_temporal_adjudicate_validation(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            temporal_candidates_text=temporal_candidates_text,
            validation_ladder_rung="constrained_verifier",
        )


class GanFrequencyS0LlmTemporalCandidatesVerifyRepairModule(dspy.Module):
    """LLM candidates, LLM adjudicate, then temporal verify-repair."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.candidate_generator = GanFrequencyS0LlmTemporalCandidatesGeneratorModule()
        signature_cls = build_gan_frequency_s0_extractor_signature(prompt_version)
        self.adjudicate = dspy.Predict(signature_cls)
        self.verifier = GanFrequencyS0TemporalVerifierModule(
            prompt_version=GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_PROMPT_VERSION
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )

        generated = self.candidate_generator(note_text=note_text)
        candidates = _llm_temporal_candidates_from_prediction(note_text, generated)
        temporal_candidates_text = format_temporal_candidates_for_prompt(
            candidates,
            source="llm",
        )
        initial = self.adjudicate(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
        )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
            temporal_candidate_labels=[c.canonical_label for c in candidates],
            temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
            temporal_candidate_source="llm",
            llm_temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
        )


class GanFrequencyS0TemporalEventTableSignature(dspy.Signature):
    """Extract a structured seizure event table from a clinical note.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    Build an auditable event table before final Gan label selection:
    - List distinct seizure, cluster, and aura mentions as separate events.
    - List seizure-free intervals separately from counted seizure events.
    - Preserve raw phrases and exact evidence spans from the note.
    - Do not invent counts, dates, or windows that are not stated in the note.
    - When a count and window appear together, keep both on the same event row.
    - Mark seizure-free intervals as qualifying for a seizure-free label only
      when the note states at least six months of seizure freedom.
    - Optionally add selected_window_note when multiple windows compete and one
      appears annotation-relevant for the current frequency statement.

    Output event_table_json as a JSON object with keys:
    events, seizure_free_intervals, selected_window_note.
    Each event requires raw_phrase and evidence_text. Each seizure-free interval
    requires raw_phrase and evidence_text.
    """

    note_text: str = dspy.InputField(
        desc="Full clinical note text for seizure-frequency extraction."
    )
    event_table_json: str = dspy.OutputField(
        desc=(
            "JSON object with events, seizure_free_intervals, and optional "
            "selected_window_note. Every evidence_text must be an exact "
            "contiguous substring of note_text."
        )
    )


class GanFrequencyS0TemporalEventTableVerifierSignature(
    GanFrequencyS0TemporalVerifierSignature
):
    """Verify/repair with deterministic candidates plus a model event table.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    In addition to temporal_candidates, temporal_event_table lists structured
    seizure events and seizure-free intervals extracted from the note. These are
    diagnostic hints, not gold labels.

    Event-table policy:
    - Prefer event rows whose evidence_text is note-supported when choosing a
      denominator window for unknown initial labels.
    - Do not repair to seizure free for N unit when the event table only shows
      short seizure-free intervals under six months.
    - Keep confirm-first rules from temporal-candidate v1.1 unchanged.
    """

    temporal_event_table: str = dspy.InputField(
        desc=(
            "Structured seizure event table with events, seizure-free intervals, "
            "and optional selected-window note."
        )
    )


class GanFrequencyS0TemporalEventTableAdjudicateSignature(GanFrequencyS0Signature):
    """Adjudicate Gan seizure frequency from a model-extracted event table.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    This is a G5 event-table candidate-stage arm. The first model pass emits
    seizure events, windows, and seizure-free intervals; this second pass
    selects the final canonical Gan label and evidence quote. The event table is
    a candidate-stage hint, not a gold label and not a free-form repair pass.

    Event-table adjudication policy:
    - Prefer note-supported counted event rows when they provide a count and
      shared calendar window.
    - Group multiple recent counted events into the relevant observation window
      when the rows support a shared denominator.
    - If several current seizure types or event frequencies are stated, choose
      the highest note-supported current frequency.
    - Counted events followed by short stability/no-further-events language
      remain counted-window labels unless seizure freedom is at least 6 months.
    - Use seizure-free labels only when a seizure_free_intervals row explicitly
      qualifies for the seizure-free label.
    - Trigger-conditioned or pattern-only rows without a calendar denominator
      remain "unknown".
    - If the note has no clinical seizure-frequency content, output
      "no seizure frequency reference".
    - evidence_text must be an exact contiguous quote from note_text.
    """

    temporal_event_table: str = dspy.InputField(
        desc=(
            "Structured seizure event table with counted events, windows, "
            "seizure-free intervals, and optional selected-window note."
        )
    )


class GanFrequencyS0TemporalEventTableExtractorModule(dspy.Module):
    """Model pass that emits a structured temporal event table."""

    def __init__(self) -> None:
        super().__init__()
        self.extract = dspy.Predict(GanFrequencyS0TemporalEventTableSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.extract(note_text=note_text)


class GanFrequencyS0TemporalEventTableVerifierModule(dspy.Module):
    """Verifier that receives deterministic candidates and an event table."""

    def __init__(self) -> None:
        super().__init__()
        self.verify = dspy.Predict(GanFrequencyS0TemporalEventTableVerifierSignature)

    def forward(
        self,
        note_text: str,
        initial_label: str | None,
        initial_evidence: str | None,
        temporal_candidates: str,
        temporal_event_table: str,
    ) -> dspy.Prediction:
        return self.verify(
            note_text=note_text,
            initial_label=initial_label,
            initial_evidence=initial_evidence,
            temporal_candidates=temporal_candidates,
            temporal_event_table=temporal_event_table,
        )


class GanFrequencyS0TemporalEventTableVerifyRepairModule(dspy.Module):
    """Direct extraction, model event table, then temporal verify/repair."""

    def __init__(self, extractor_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT) -> None:
        super().__init__()
        self.extractor = build_gan_s0_module(extractor_variant)
        self.event_table_extractor = GanFrequencyS0TemporalEventTableExtractorModule()
        self.verifier = GanFrequencyS0TemporalEventTableVerifierModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )
        from clinical_extraction.gan.temporal_events import (
            format_temporal_event_table_for_prompt,
            parse_temporal_event_table_json,
            temporal_event_table_to_dict,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        initial = self.extractor(note_text=note_text)
        event_table_raw = self.event_table_extractor(note_text=note_text)
        event_table = parse_temporal_event_table_json(
            event_table_raw.event_table_json,
            note_text=note_text,
        )
        temporal_event_table_text = format_temporal_event_table_for_prompt(event_table)
        verified = self.verifier(
            note_text=note_text,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
            temporal_event_table=temporal_event_table_text,
        )
        verified = _apply_temporal_verifier_guards(
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            verified=verified,
            candidates=candidates,
            event_table=event_table,
        )
        return dspy.Prediction(
            seizure_frequency_number=verified.final_label,
            evidence_text=verified.final_evidence,
            verifier_decision=verified.decision,
            verifier_reason=verified.reason,
            initial_label=initial.seizure_frequency_number,
            initial_evidence=initial.evidence_text,
            temporal_candidates=temporal_candidates_text,
            temporal_candidate_labels=[c.canonical_label for c in candidates],
            temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
            temporal_event_table=temporal_event_table_text,
            temporal_event_table_records=temporal_event_table_to_dict(event_table),
        )


class GanFrequencyS0TemporalEventTableSinglePassModule(dspy.Module):
    """Model event table followed by one final LLM adjudication pass."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.event_table_extractor = GanFrequencyS0TemporalEventTableExtractorModule()
        self.adjudicate = dspy.Predict(GanFrequencyS0TemporalEventTableAdjudicateSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_events import (
            format_temporal_event_table_for_prompt,
            parse_temporal_event_table_json,
            temporal_event_table_to_dict,
        )

        event_table_raw = self.event_table_extractor(note_text=note_text)
        event_table = parse_temporal_event_table_json(
            event_table_raw.event_table_json,
            note_text=note_text,
        )
        temporal_event_table_text = format_temporal_event_table_for_prompt(event_table)
        result = self.adjudicate(
            note_text=note_text,
            temporal_event_table=temporal_event_table_text,
        )
        return dspy.Prediction(
            seizure_frequency_number=result.seizure_frequency_number,
            evidence_text=result.evidence_text,
            temporal_event_table=temporal_event_table_text,
            temporal_event_table_records=temporal_event_table_to_dict(event_table),
            temporal_candidate_source="llm_event_table",
            prompt_version=self.prompt_version,
        )


class GanFrequencyS0MultipleAnswerSignature(dspy.Signature):
    """Propose multiple canonical Gan seizure-frequency answers from the note.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    This is a G6 multiple-answer candidate-stage arm. The model should emit
    explicit answer options rather than an event table. A deterministic selector
    will choose among the options, so each option must expose enough policy
    metadata to audit the choice.

    Output answer_options_json as a JSON object with key "answer_options".
    Each option must include:
    - canonical_label: canonical Gan label, unknown, or no seizure frequency reference.
    - evidence_text: exact contiguous note quote supporting the option; may be
      null only for no seizure frequency reference.
    - status: one of current, historical, seizure_free, unknown, no_reference.
    - ambiguity_flags: list of short strings, e.g. denominator_missing,
      trigger_conditioned, pattern_only, historical_only, no_clinical_content.
    - rationale: short provenance note.

    Proposer policy:
    - Include all plausible benchmark-facing readings when the note is ambiguous.
    - Preserve count/window slots inside canonical_label; do not emit event rows
      that require the selector to reconstruct the label.
    - Prefer exact count+window labels over unknown when both count and window
      are present in the same current-frequency reading.
    - Include unknown for trigger-conditioned or pattern-only events without a
      calendar-time denominator.
    - Include no seizure frequency reference only when the note lacks usable
      clinical seizure-frequency content.
    """

    note_text: str = dspy.InputField(
        desc="Full clinical note text for seizure-frequency extraction."
    )
    answer_options_json: str = dspy.OutputField(
        desc=(
            'JSON object {"answer_options": [...]} with canonical_label, '
            "evidence_text, status, ambiguity_flags, and rationale for each option."
        )
    )


class GanFrequencyS0SeededMultipleAnswerSignature(dspy.Signature):
    """Propose additional canonical Gan answers after reading deterministic candidates.

    /no_think
    Do not use hidden reasoning. Emit only the requested output fields.

    This is a G6b seeded hybrid answer-options arm. Deterministic temporal
    candidates are already available to the selector; the model should add
    plausible missing or competing readings, not restate the prompt.

    Output answer_options_json as a JSON object with key "answer_options".
    Each option must include canonical_label, evidence_text, status,
    ambiguity_flags, and rationale.

    Seeded policy:
    - Treat temporal_candidates as note-derived seed options. Add an LLM option
      only when it improves, competes with, or flags ambiguity in those seeds.
    - Preserve exact count/window slots in canonical_label.
    - Use exact contiguous evidence_text from the note for every option except
      no seizure frequency reference.
    - Include unknown only for genuine pattern-only or trigger-conditioned
      readings without a denominator.
    - Do not discard deterministic candidates; the deterministic selector will
      merge them with these LLM options.
    """

    note_text: str = dspy.InputField(
        desc="Full clinical note text for seizure-frequency extraction."
    )
    temporal_candidates: str = dspy.InputField(
        desc="Deterministic temporal frequency candidate labels and evidence."
    )
    answer_options_json: str = dspy.OutputField(
        desc=(
            'JSON object {"answer_options": [...]} with canonical_label, '
            "evidence_text, status, ambiguity_flags, and rationale for each option."
        )
    )


def _multiple_answer_option_to_dict(option: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "canonical_label": option["canonical_label"],
        "evidence_text": option.get("evidence_text"),
        "status": option.get("status", ""),
        "ambiguity_flags": list(option.get("ambiguity_flags", [])),
        "rationale": option.get("rationale", ""),
    }
    if "source" in option:
        payload["source"] = option["source"]
    if "rejection_reason" in option:
        payload["rejection_reason"] = option["rejection_reason"]
    return payload


def _raw_multiple_answer_option_to_dict(
    row: dict[str, Any],
    *,
    rejection_reason: str,
) -> dict[str, Any]:
    flags_raw = row.get("ambiguity_flags") or []
    if isinstance(flags_raw, str):
        flags = [flags_raw]
    elif isinstance(flags_raw, list):
        flags = [str(flag) for flag in flags_raw if str(flag).strip()]
    else:
        flags = []
    return {
        "canonical_label": row.get("canonical_label"),
        "evidence_text": row.get("evidence_text"),
        "status": row.get("status"),
        "ambiguity_flags": flags,
        "rationale": row.get("rationale"),
        "source": row.get("source", "llm_answer_option"),
        "rejection_reason": rejection_reason,
    }


def _parse_multiple_answer_options_json(
    payload: str | dict[str, Any] | None,
    *,
    note_text: str,
) -> list[dict[str, Any]]:
    parsed, _rejected = _parse_multiple_answer_options_json_with_rejections(
        payload,
        note_text=note_text,
    )
    return parsed


def _parse_multiple_answer_options_json_with_rejections(
    payload: str | dict[str, Any] | None,
    *,
    note_text: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if payload is None:
        return [], []
    if isinstance(payload, str):
        stripped = payload.strip()
        if not stripped or stripped.lower() in {"none", "null"}:
            return [], []
        try:
            raw = json.loads(stripped)
        except json.JSONDecodeError:
            return [], [
                {
                    "canonical_label": None,
                    "evidence_text": None,
                    "status": None,
                    "ambiguity_flags": [],
                    "rationale": payload,
                    "source": "llm_answer_option",
                    "rejection_reason": "invalid_json",
                }
            ]
    else:
        raw = payload

    if isinstance(raw, list):
        rows = raw
    elif isinstance(raw, dict):
        rows = raw.get("answer_options") or raw.get("candidates") or []
    else:
        return [], []
    if not isinstance(rows, list):
        return [], []

    parsed: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen: set[tuple[str, str | None]] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        label_raw = row.get("canonical_label")
        if not isinstance(label_raw, str) or not label_raw.strip():
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="missing_canonical_label",
                )
            )
            continue
        label = _normalize_predicted_label(label_raw)
        if not label:
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="empty_normalized_label",
                )
            )
            continue
        evidence = row.get("evidence_text")
        evidence_text = evidence.strip() if isinstance(evidence, str) else None
        if label != "no seizure frequency reference" and (
            not evidence_text or evidence_text not in note_text
        ):
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="unsupported_or_missing_evidence",
                )
            )
            continue
        try:
            _multiple_answer_label_class(label)
        except ValueError:
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="noncanonical_label",
                )
            )
            continue
        flags_raw = row.get("ambiguity_flags") or []
        if isinstance(flags_raw, str):
            flags = [flags_raw]
        elif isinstance(flags_raw, list):
            flags = [str(flag) for flag in flags_raw if str(flag).strip()]
        else:
            flags = []
        status = str(row.get("status") or "").strip().lower()
        option = {
            "canonical_label": label,
            "evidence_text": evidence_text,
            "status": status,
            "ambiguity_flags": flags,
            "rationale": str(row.get("rationale") or ""),
            "source": str(row.get("source") or "llm_answer_option"),
        }
        key = (label, evidence_text)
        if key in seen:
            rejected.append(
                _raw_multiple_answer_option_to_dict(
                    row,
                    rejection_reason="duplicate_label_evidence",
                )
            )
            continue
        seen.add(key)
        parsed.append(option)
    return parsed, rejected


def _multiple_answer_label_class(label: str) -> str:
    from clinical_extraction.gan.frequency import label_to_monthly_frequency

    normalized = label.strip().lower()
    if normalized == "no seizure frequency reference":
        return "no_reference"
    if normalized == "unknown" or normalized.startswith("unknown,"):
        return "unknown"
    if normalized.startswith("seizure free for "):
        label_to_monthly_frequency(normalized)
        return "seizure_free"
    label_to_monthly_frequency(normalized)
    return "quantified"


def _multiple_answer_selector_score(option: dict[str, Any]) -> tuple[int, float, str]:
    from clinical_extraction.gan.frequency import label_to_monthly_frequency

    label = option["canonical_label"]
    label_class = _multiple_answer_label_class(label)
    flags = {str(flag).lower() for flag in option.get("ambiguity_flags", [])}
    status = str(option.get("status") or "").lower()

    if label_class == "quantified":
        rank = 400
        if status == "historical" or "historical_only" in flags:
            rank -= 150
        if {"denominator_missing", "trigger_conditioned", "pattern_only"} & flags:
            rank -= 120
        return (rank, label_to_monthly_frequency(label), label)
    if label_class == "seizure_free":
        rank = 350
        if status == "historical" or "historical_only" in flags:
            rank -= 150
        return (rank, 0.0, label)
    if label_class == "unknown":
        rank = 300
        if {"denominator_missing", "trigger_conditioned", "pattern_only"} & flags:
            rank += 25
        return (rank, 0.0, label)
    return (100, 0.0, label)


def select_gan_multiple_answer_option(
    options: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Select one answer option with a deterministic Gan-policy hierarchy."""

    if not options:
        return None
    return max(options, key=_multiple_answer_selector_score)


def _temporal_candidates_to_multiple_answer_options(
    candidates: list[Any],
) -> list[dict[str, Any]]:
    options: list[dict[str, Any]] = []
    for candidate in candidates:
        label = _normalize_predicted_label(candidate.canonical_label)
        if not label:
            continue
        try:
            _multiple_answer_label_class(label)
        except ValueError:
            continue
        options.append(
            {
                "canonical_label": label,
                "evidence_text": candidate.evidence_text,
                "status": "current",
                "ambiguity_flags": [],
                "rationale": (
                    "Seeded from deterministic temporal candidate "
                    f"{candidate.derivation}."
                ),
                "source": "deterministic_temporal_candidate",
            }
        )
    return options


class GanFrequencyS0MultipleAnswerGeneratorModule(dspy.Module):
    """Model pass that proposes canonical answer options for deterministic selection."""

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.Predict(GanFrequencyS0MultipleAnswerSignature)

    def forward(self, note_text: str) -> dspy.Prediction:
        return self.generate(note_text=note_text)


class GanFrequencyS0SeededMultipleAnswerGeneratorModule(dspy.Module):
    """Model pass that proposes answer options after seeing deterministic seeds."""

    def __init__(self) -> None:
        super().__init__()
        self.generate = dspy.Predict(GanFrequencyS0SeededMultipleAnswerSignature)

    def forward(self, note_text: str, temporal_candidates: str) -> dspy.Prediction:
        return self.generate(
            note_text=note_text,
            temporal_candidates=temporal_candidates,
        )


class GanFrequencyS0MultipleAnswerDetSelectorModule(dspy.Module):
    """LLM multiple-answer proposer followed by deterministic Gan-policy selector."""

    def __init__(
        self,
        *,
        prompt_version: str = GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_PROMPT_VERSION,
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.generator = GanFrequencyS0MultipleAnswerGeneratorModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        generated = self.generator(note_text=note_text)
        options = _parse_multiple_answer_options_json(
            generated.answer_options_json,
            note_text=note_text,
        )
        selected = select_gan_multiple_answer_option(options)
        if selected is None:
            return dspy.Prediction(
                seizure_frequency_number="unknown",
                evidence_text=None,
                multiple_answer_options=[],
                selected_answer_option=None,
                temporal_candidate_source="llm_multiple_answer_det_selector",
                verifier_decision="abstain",
                verifier_reason=(
                    "Deterministic selector found no valid note-supported answer options."
                ),
                prompt_version=self.prompt_version,
            )
        return dspy.Prediction(
            seizure_frequency_number=selected["canonical_label"],
            evidence_text=selected.get("evidence_text"),
            multiple_answer_options=[
                _multiple_answer_option_to_dict(option) for option in options
            ],
            selected_answer_option=_multiple_answer_option_to_dict(selected),
            temporal_candidate_source="llm_multiple_answer_det_selector",
            verifier_decision="deterministic_select",
            verifier_reason=(
                "Selected by deterministic Gan policy hierarchy over explicit "
                "canonical answer options."
            ),
            prompt_version=self.prompt_version,
        )


class GanFrequencyS0SeededMultipleAnswerDetSelectorModule(dspy.Module):
    """Deterministic temporal seeds plus LLM options followed by deterministic selection."""

    def __init__(
        self,
        *,
        prompt_version: str = (
            GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_PROMPT_VERSION
        ),
    ) -> None:
        super().__init__()
        self.prompt_version = prompt_version
        self.generator = GanFrequencyS0SeededMultipleAnswerGeneratorModule()

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.temporal_candidates import (
            build_temporal_frequency_candidates_from_note,
            format_temporal_candidates_for_prompt,
            temporal_candidate_to_dict,
        )

        candidates = build_temporal_frequency_candidates_from_note(note_text)
        temporal_candidates_text = format_temporal_candidates_for_prompt(candidates)
        generated = self.generator(
            note_text=note_text,
            temporal_candidates=temporal_candidates_text,
        )
        llm_options, rejected_options = (
            _parse_multiple_answer_options_json_with_rejections(
                generated.answer_options_json,
                note_text=note_text,
            )
        )
        seeded_options = _temporal_candidates_to_multiple_answer_options(candidates)
        options = seeded_options + llm_options
        selected = select_gan_multiple_answer_option(options)
        if selected is None:
            return dspy.Prediction(
                seizure_frequency_number="unknown",
                evidence_text=None,
                temporal_candidates=temporal_candidates_text,
                temporal_candidate_labels=[c.canonical_label for c in candidates],
                temporal_candidate_records=[
                    temporal_candidate_to_dict(candidate) for candidate in candidates
                ],
                multiple_answer_options=[],
                rejected_multiple_answer_options=rejected_options,
                selected_answer_option=None,
                temporal_candidate_source="seeded_hybrid_multiple_answer_det_selector",
                verifier_decision="abstain",
                verifier_reason=(
                    "Deterministic selector found no valid seeded or LLM answer options."
                ),
                prompt_version=self.prompt_version,
            )
        return dspy.Prediction(
            seizure_frequency_number=selected["canonical_label"],
            evidence_text=selected.get("evidence_text"),
            temporal_candidates=temporal_candidates_text,
            temporal_candidate_labels=[c.canonical_label for c in candidates],
            temporal_candidate_records=[
                temporal_candidate_to_dict(candidate) for candidate in candidates
            ],
            multiple_answer_options=[
                _multiple_answer_option_to_dict(option) for option in options
            ],
            rejected_multiple_answer_options=rejected_options,
            selected_answer_option=_multiple_answer_option_to_dict(selected),
            temporal_candidate_source="seeded_hybrid_multiple_answer_det_selector",
            verifier_decision="deterministic_select",
            verifier_reason=(
                "Selected by deterministic Gan policy hierarchy over deterministic "
                "temporal seeds plus valid LLM answer options."
            ),
            prompt_version=self.prompt_version,
        )


class GanFrequencyS0ReactTemporalToolsSignature(dspy.Signature):
    """Extract Gan seizure frequency using bounded ReAct temporal tools.

    /no_think
    Do not use hidden reasoning in the final answer fields. Use tools first,
    then emit only the requested output fields.

    ReAct turn rules (mandatory on every tool step):
    - Keep next_thought to at most two short sentences.
    - ALWAYS emit next_tool_name and next_tool_args together; never emit
      next_thought alone.
    - If tool observations are sufficient, call finish on the next turn.
    - If stuck after two tool rounds, call finish and decide from observations.

    Policy:
    - Use deterministic tools to gather temporal candidates, clinic dates,
      frequency mention spans, label validation, and evidence support before
      committing to a label.
    - Prefer note-supported quantified rates over unknown when count and window
      can be assembled from tool observations.
    - Use seizure free for N unit only when seizure freedom is at least 6 months.
    - Cluster labels must include both cluster period and per-cluster count.
    - evidence_text must be an exact contiguous substring of note_text.
    - Call finish once tool observations are sufficient to choose the label.
    """

    note_text: str = dspy.InputField(
        desc="Full clinical note text for seizure-frequency extraction."
    )
    seizure_frequency_number: str = dspy.OutputField(
        desc=(
            "Canonical Gan seizure-frequency label, unknown, "
            "no seizure frequency reference, or abstain/null."
        )
    )
    evidence_text: str = dspy.OutputField(
        desc="Exact contiguous quote from note_text supporting the label."
    )


class GanFrequencyS0ReactTemporalToolsModule(dspy.Module):
    """Bounded ReAct probe with deterministic temporal helper tools."""

    def __init__(
        self,
        *,
        max_iters: int | None = None,
    ) -> None:
        from clinical_extraction.gan.react_tools import (
            GAN_REACT_TEMPORAL_MAX_ITERS,
            GAN_REACT_TEMPORAL_TOOLS,
        )

        super().__init__()
        self.max_iters = max_iters or GAN_REACT_TEMPORAL_MAX_ITERS
        self.react = dspy.ReAct(
            GanFrequencyS0ReactTemporalToolsSignature,
            tools=GAN_REACT_TEMPORAL_TOOLS,
            max_iters=self.max_iters,
        )

    def forward(self, note_text: str) -> dspy.Prediction:
        from clinical_extraction.gan.react_tools import (
            count_react_tool_calls,
            serialize_react_trajectory,
        )

        try:
            result = self.react(note_text=note_text)
        except Exception as exc:
            return dspy.Prediction(
                seizure_frequency_number="unknown",
                evidence_text=None,
                react_trajectory={},
                react_tool_call_count=0,
                react_error=f"{type(exc).__name__}: {exc}",
            )

        trajectory = getattr(result, "trajectory", {}) or {}
        return dspy.Prediction(
            seizure_frequency_number=result.seizure_frequency_number,
            evidence_text=result.evidence_text,
            react_trajectory=serialize_react_trajectory(trajectory),
            react_tool_call_count=count_react_tool_calls(trajectory),
        )


# ---------------------------------------------------------------------------
# DSPy metric for optimizer training
# ---------------------------------------------------------------------------

def gan_frequency_s0_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """DSPy metric for Gan S0 optimizer training.

    Uses pragmatic category match (infrequent / frequent / unknown) as the
    optimization target — it is the coarsest benchmark-facing signal and
    therefore most stable across minor label format variation.

    Returns 1.0 on pragmatic category match, 0.0 on mismatch or invalid label.
    """
    from clinical_extraction.gan.scoring import score_gan_frequency_prediction

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)

    if not predicted or not gold:
        return 0.0

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
        return float(score.pragmatic_category_match)
    except ValueError:
        return 0.0


def gan_frequency_s0_synthesis_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """Stricter optimizer metric for synthesis-backed Gan S0 compilation.

    This metric is intentionally optimizer-facing. It does not change the
    benchmark evaluator. A trace passes only when the predicted label matches
    the normalized gold label and, unless the gold label is no-reference, the
    prediction supplies an exact contiguous quote from the note.
    """
    from clinical_extraction.gan.scoring import score_gan_frequency_prediction

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)

    if not predicted or not gold:
        return 0.0

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError:
        return 0.0

    if not score.exact_normalized_match:
        return 0.0

    predicted_evidence = getattr(pred, "evidence_text", None)
    if gold == "no seizure frequency reference":
        return float(predicted_evidence is None or not str(predicted_evidence).strip())

    if not _requires_evidence_support(gold):
        return 1.0

    if not isinstance(predicted_evidence, str) or not predicted_evidence.strip():
        return 0.0
    return float(predicted_evidence.strip() in example.note_text)


def gan_frequency_s0_synthesis_feedback_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
    pred_name=None,
    pred_trace=None,
):
    """GEPA-compatible Gan S0 feedback metric.

    This metric is optimizer-facing only. It preserves the benchmark scorer
    contract while surfacing richer textual feedback for common Gan failure
    modes such as canonical-label drift, temporal-window errors, cluster-format
    failures, abstentions, and unsupported evidence quotes.
    """
    from dspy.teleprompt.gepa.gepa_utils import ScoreWithFeedback

    from clinical_extraction.gan.scoring import score_gan_frequency_prediction

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)
    note_text = getattr(example, "note_text", "") or ""

    if not gold:
        return base

    if not predicted:
        return ScoreWithFeedback(
            score=0.0,
            feedback=(
                "[abstention] The prediction did not provide seizure_frequency_number. "
                "Return a canonical Gan label or no seizure frequency reference, and "
                "abstain only when the note truly lacks usable seizure-frequency information."
            ),
        )
    if not gold:
        return ScoreWithFeedback(
            score=0.0,
            feedback="The training example is missing the gold Gan frequency label.",
        )

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError as exc:
        feedback = [
            (
                "[invalid-format] "
                f"The predicted label {predicted!r} is not a valid canonical Gan "
                f"frequency label: {exc}."
            )
        ]
        if _looks_like_cluster_failure(str(predicted)):
            feedback.append(
                "[cluster-format] Cluster labels must use the full format "
                "'N cluster per unit, M per cluster' and must not drop the "
                "per-cluster count."
            )
        forbidden_unit = _forbidden_unit(str(predicted))
        if forbidden_unit is not None:
            feedback.append(
                f"[forbidden-unit] Replace {forbidden_unit!r} with canonical Gan "
                "units day, week, month, or year."
            )
        return ScoreWithFeedback(
            score=0.0,
            feedback=" ".join(feedback),
        )

    predicted_evidence = getattr(pred, "evidence_text", None)
    feedback: list[str] = []
    metric_score = 0.8 if score.exact_normalized_match else 0.0

    if not score.exact_normalized_match:
        feedback.append(
            "[exact-label] "
            f"Expected normalized Gan label {gold!r}, but the prediction was "
            f"{predicted!r}. Preserve the benchmark-facing label semantics."
        )
        if score.pragmatic_category_match:
            metric_score = 0.3
        else:
            feedback.append(
                "[pragmatic-category] The prediction crossed the benchmark-facing "
                f"Pragmatic bucket from {score.gold_pragmatic_category!r} to "
                f"{score.predicted_pragmatic_category!r}."
            )
        if (
            _looks_like_cluster_failure(score.predicted_label)
            or "cluster" in score.normalized_gold_label
        ):
            feedback.append(
                "[cluster-format] Preserve the cluster structure exactly. Do not "
                "drop the cluster period or the per-cluster count, and do not back "
                "off to unknown when the note gives both values."
            )
        if _is_short_seizure_free_label(score.normalized_predicted_label):
            feedback.append(
                "[seizure-free-threshold] Use seizure-free labels only for 6 months "
                "or longer. Shorter seizure-free periods should be converted into "
                "the appropriate quantified rate."
            )
        if _has_temporal_window_mismatch(
            note_text,
            gold_label=score.normalized_gold_label,
            predicted_label=score.normalized_predicted_label,
        ):
            feedback.append(
                "[temporal-window] The note looks like a year-to-date or bounded-window "
                "case. Use the described observation window as the denominator; for "
                "year-to-date counts, use months elapsed since January."
            )

    evidence_ok = True
    if gold == "no seizure frequency reference":
        if isinstance(predicted_evidence, str) and predicted_evidence.strip():
            evidence_ok = False
            feedback.append(
                "[evidence-support] No-reference labels should not include supporting "
                "frequency evidence."
            )
    elif _requires_evidence_support(gold):
        if not isinstance(predicted_evidence, str) or not predicted_evidence.strip():
            evidence_ok = False
            feedback.append(
                "[evidence-support] The prediction must include an exact contiguous "
                "source quote as evidence."
            )
        elif predicted_evidence.strip() not in example.note_text:
            evidence_ok = False
            feedback.append(
                "[evidence-support][unsupported-quote] The evidence_text is not an "
                "exact contiguous quote from the note."
            )

    if evidence_ok:
        metric_score += 0.2

    if not feedback:
        feedback.append(
            "The prediction matched the normalized Gan label and evidence policy."
        )
    return ScoreWithFeedback(score=metric_score, feedback=" ".join(feedback))


def gan_frequency_s0_semantic_evidence_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
) -> float:
    """Graded optimizer metric for Gan frequency extraction.

    This optimizer-facing metric keeps benchmark reporting unchanged while
    matching the practical research objective more closely than Pragmatic-only
    or exact-label-only rewards. Invalid labels and unsupported evidence receive
    zero; valid, grounded predictions then receive graded credit for exact
    monthly frequency, Purist category, or Pragmatic category agreement.
    """
    from clinical_extraction.gan.scoring import score_gan_frequency_prediction

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)

    if not predicted or not gold:
        return 0.0

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError:
        return 0.0

    predicted_evidence = getattr(pred, "evidence_text", None)
    if not _evidence_policy_ok(
        gold_label=gold,
        predicted_evidence=predicted_evidence,
        note_text=getattr(example, "note_text", "") or "",
    ):
        return 0.0

    return _semantic_frequency_reward(score)


def gan_frequency_s0_semantic_evidence_feedback_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
    pred_name=None,
    pred_trace=None,
):
    """GEPA-compatible graded Gan S0 feedback metric."""
    from dspy.teleprompt.gepa.gepa_utils import ScoreWithFeedback

    from clinical_extraction.gan.scoring import score_gan_frequency_prediction

    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)
    note_text = getattr(example, "note_text", "") or ""

    if not predicted:
        return ScoreWithFeedback(
            score=0.0,
            feedback=(
                "[abstention] The prediction did not provide seizure_frequency_number. "
                "Return a canonical Gan label or no seizure frequency reference."
            ),
        )
    if not gold:
        return ScoreWithFeedback(
            score=0.0,
            feedback="The training example is missing the gold Gan frequency label.",
        )

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold, predicted_label=predicted
        )
    except ValueError as exc:
        return ScoreWithFeedback(
            score=0.0,
            feedback=(
                "[invalid-format] "
                f"The predicted label {predicted!r} is not a valid canonical Gan "
                f"frequency label: {exc}."
            ),
        )

    predicted_evidence = getattr(pred, "evidence_text", None)
    evidence_feedback = _evidence_policy_feedback(
        gold_label=gold,
        predicted_evidence=predicted_evidence,
        note_text=note_text,
    )
    if evidence_feedback is not None:
        return ScoreWithFeedback(score=0.0, feedback=evidence_feedback)

    metric_score = _semantic_frequency_reward(score)
    feedback = _semantic_frequency_feedback(score)
    return ScoreWithFeedback(score=metric_score, feedback=feedback)


def gan_frequency_s0_stage_attributed_feedback_metric(
    example: dspy.Example,
    pred: dspy.Prediction,
    trace=None,
    pred_name=None,
    pred_trace=None,
):
    """GEPA feedback metric that names the Gan S0 pipeline stage at fault.

    This is optimizer-facing only. It keeps benchmark scoring unchanged while
    making GEPA feedback usable for multi-stage programs whose failures may sit
    in candidate generation, adjudication, verifier/repair, evidence, or format.
    """
    from dspy.teleprompt.gepa.gepa_utils import ScoreWithFeedback

    from clinical_extraction.gan.scoring import score_gan_frequency_prediction
    from clinical_extraction.gan.temporal_candidates import (
        build_temporal_frequency_candidates_from_note,
    )

    base = gan_frequency_s0_semantic_evidence_feedback_metric(
        example,
        pred,
        trace=trace,
        pred_name=pred_name,
        pred_trace=pred_trace,
    )
    predicted = getattr(pred, GAN_FREQUENCY_S0_FIELD, None)
    gold = getattr(example, GAN_FREQUENCY_S0_FIELD, None)
    note_text = getattr(example, "note_text", "") or ""

    stage_feedback: list[str] = []
    if not predicted:
        stage_feedback.append(
            "[stage:adjudicator] The LLM did not select a canonical Gan label."
        )
        return ScoreWithFeedback(
            score=base.score,
            feedback=" ".join(stage_feedback + [base.feedback]),
        )

    try:
        score = score_gan_frequency_prediction(
            gold_label=gold,
            predicted_label=predicted,
        )
    except ValueError:
        stage_feedback.append(
            "[stage:format] The emitted label is malformed before benchmark "
            "scoring can compare frequency semantics."
        )
        return ScoreWithFeedback(
            score=base.score,
            feedback=" ".join(stage_feedback + [base.feedback]),
        )

    candidate_labels = {
        candidate.canonical_label
        for candidate in build_temporal_frequency_candidates_from_note(note_text)
    }
    normalized_candidate_labels = {
        score_gan_frequency_prediction(gold_label=label, predicted_label=label)
        .normalized_gold_label
        for label in candidate_labels
    }
    gold_candidate_missing = (
        gold not in {"unknown", "no seizure frequency reference"}
        and score.normalized_gold_label not in normalized_candidate_labels
    )
    if gold_candidate_missing:
        stage_feedback.append(
            "[stage:candidate_surface] The deterministic temporal-candidate "
            "surface did not include the normalized gold label; do not treat this "
            "as an adjudicator-only failure."
        )

    evidence_feedback = _evidence_policy_feedback(
        gold_label=gold,
        predicted_evidence=getattr(pred, "evidence_text", None),
        note_text=note_text,
    )
    if evidence_feedback is not None:
        stage_feedback.append(
            "[stage:evidence] The label/evidence pair failed the source-quote "
            "support contract."
        )

    if not score.exact_normalized_match:
        if getattr(pred, "verifier_decision", None) or getattr(pred, "verifier_reason", None):
            stage_feedback.append(
                "[stage:verifier] The verify/repair stage returned a residual "
                "frequency error after seeing the initial label."
            )
        elif not gold_candidate_missing:
            stage_feedback.append(
                "[stage:adjudicator] The gold-compatible candidate surface was "
                "available or not disproven, but the selected label missed the "
                "Gan frequency semantics."
            )
        if (
            _looks_like_cluster_failure(score.predicted_label)
            or "cluster" in score.normalized_gold_label
        ):
            stage_feedback.append(
                "[stage:format] Preserve canonical cluster structure and "
                "per-cluster counts."
            )

    if not stage_feedback:
        stage_feedback.append(
            "[stage:all] Candidate surface, adjudication, evidence, and format "
            "matched the optimizer-facing contract."
        )

    return ScoreWithFeedback(
        score=base.score,
        feedback=" ".join(stage_feedback + [base.feedback]),
    )


def _semantic_frequency_reward(score) -> float:
    if score.exact_normalized_match:
        return 1.0
    if score.monthly_frequency_match:
        return 0.85
    if score.purist_category_match:
        return 0.65
    if score.pragmatic_category_match:
        return 0.4
    return 0.0


def _semantic_frequency_feedback(score) -> str:
    if score.exact_normalized_match:
        return (
            "[exact-label][evidence-support] The prediction matched the normalized "
            "Gan label and evidence policy."
        )
    if score.monthly_frequency_match:
        return (
            "[monthly-frequency] The prediction converts to the correct seizures "
            "per month, but the canonical Gan label surface differs from gold."
        )
    if score.purist_category_match:
        return (
            "[purist-category] The prediction preserves the fine-grained Purist "
            "frequency category but misses the exact monthly value or canonical label."
        )
    if score.pragmatic_category_match:
        return (
            "[pragmatic-category] The prediction preserves only the coarse "
            "infrequent/frequent/unknown/no-reference bucket. Improve the temporal "
            "window, cluster details, or numeric conversion."
        )
    return (
        "[frequency-semantics] The prediction crossed the benchmark-facing "
        f"Pragmatic bucket from {score.gold_pragmatic_category!r} to "
        f"{score.predicted_pragmatic_category!r}."
    )


# ---------------------------------------------------------------------------
# DSPy Example helpers
# ---------------------------------------------------------------------------

def make_gan_dspy_examples(records: list[GanRecord]) -> list[dspy.Example]:
    """Convert Gan records into DSPy Examples for training or evaluation.

    Each example exposes ``note_text`` as input and ``seizure_frequency_number``
    (the gold label) as the expected output for the metric.
    """
    return [
        dspy.Example(
            note_text=record.note_text,
            seizure_frequency_number=record.gold_label,
        ).with_inputs("note_text")
        for record in records
    ]


def make_gan_synthesis_dspy_examples(records: list[GanRecord]) -> list[dspy.Example]:
    """Convert Gan records into synthesis-backed examples.

    Evidence outputs are included only when the annotation text is a contiguous
    source quote. Paraphrased or elided Gan evidence is not used as a quote demo.
    """
    return [
        dspy.Example(
            note_text=record.note_text,
            seizure_frequency_number=record.gold_label,
            evidence_text=_locatable_gold_evidence(record),
        ).with_inputs("note_text")
        for record in sorted(records, key=_synthesis_example_priority)
    ]


def _locatable_gold_evidence(record: GanRecord) -> str | None:
    if not record.gold_evidence or "..." in record.gold_evidence:
        return None
    if record.gold_evidence not in record.note_text:
        return None
    return record.gold_evidence


def _synthesis_example_priority(record: GanRecord) -> tuple[int, int, str]:
    if _locatable_gold_evidence(record):
        evidence_rank = 0
    elif record.gold_label == "no seizure frequency reference":
        evidence_rank = 2
    else:
        evidence_rank = 1

    label = record.gold_label
    if "cluster" in label:
        label_rank = 0
    elif label.startswith("seizure free"):
        label_rank = 1
    elif " per " in label:
        label_rank = 2
    elif label == "unknown":
        label_rank = 3
    else:
        label_rank = 4
    return (evidence_rank, label_rank, record.record_id)


# ---------------------------------------------------------------------------
# BootstrapFewShot compilation helper
# ---------------------------------------------------------------------------

GAN_FREQUENCY_S0_OPTIMIZER_METRICS = {
    "pragmatic_category": gan_frequency_s0_metric,
    "semantic_frequency_with_evidence": gan_frequency_s0_semantic_evidence_metric,
    "semantic_frequency_with_evidence_feedback": (
        gan_frequency_s0_semantic_evidence_feedback_metric
    ),
    "gan_s0_stage_attributed_frequency_feedback": (
        gan_frequency_s0_stage_attributed_feedback_metric
    ),
    "synthesis_exact_with_evidence": gan_frequency_s0_synthesis_metric,
    "synthesis_exact_with_evidence_feedback": gan_frequency_s0_synthesis_feedback_metric,
}


def _gan_s0_optimizer_trainset(
    records: list[GanRecord],
    *,
    optimizer_metric: str,
) -> list[dspy.Example]:
    if optimizer_metric in {
        "semantic_frequency_with_evidence",
        "semantic_frequency_with_evidence_feedback",
        "gan_s0_stage_attributed_frequency_feedback",
        "synthesis_exact_with_evidence",
        "synthesis_exact_with_evidence_feedback",
    }:
        return make_gan_synthesis_dspy_examples(records)
    return make_gan_dspy_examples(records)


def compile_gan_s0_module(
    records: list[GanRecord],
    *,
    program_variant: str = GAN_FREQUENCY_S0_VARIANT,
    optimizer_name: str = "BootstrapFewShot",
    max_bootstrapped_demos: int = 4,
    max_labeled_demos: int = 0,
    max_rounds: int = 1,
    num_candidate_programs: int = 16,
    optimizer_metric: str = "semantic_frequency_with_evidence",
) -> (
    GanFrequencyS0Module
    | GanFrequencyS0DirectModule
    | GanFrequencyS0VerifyRepairModule
    | GanFrequencyS0TemporalCandidatesVerifyRepairModule
    | GanFrequencyS0TemporalCandidatesSinglePassModule
):
    """Compile a Gan S0 module with a few-shot DSPy optimizer.

    Supports ``LabeledFewShot``, ``BootstrapFewShot``, and
    ``BootstrapFewShotWithRandomSearch`` (``BootstrapRS``). LabeledFewShot
    samples labeled demonstrations from the trainset without bootstrapping.
    BootstrapFewShot keeps teacher traces that pass the optimizer metric.
    BootstrapFewShotWithRandomSearch searches over candidate demo sets.

    For verify-repair variants, LabeledFewShot compiles only the extractor
    sub-module so trainset demos stay on the direct extraction signature.
    """
    trainset = _gan_s0_optimizer_trainset(records, optimizer_metric=optimizer_metric)
    module = build_gan_s0_module(program_variant)

    if optimizer_name == "LabeledFewShot":
        optimizer = dspy.LabeledFewShot(k=max_labeled_demos)
        if isinstance(
            module,
            (
                GanFrequencyS0VerifyRepairModule,
                GanFrequencyS0TemporalCandidatesVerifyRepairModule,
            ),
        ):
            module.extractor = optimizer.compile(module.extractor, trainset=trainset)
            return module
        return optimizer.compile(module, trainset=trainset)

    try:
        metric = GAN_FREQUENCY_S0_OPTIMIZER_METRICS[optimizer_metric]
    except KeyError as exc:
        allowed = ", ".join(sorted(GAN_FREQUENCY_S0_OPTIMIZER_METRICS))
        raise ValueError(f"Unknown optimizer_metric {optimizer_metric!r}; use {allowed}.") from exc

    if optimizer_name == "BootstrapFewShotWithRandomSearch":
        optimizer = dspy.BootstrapFewShotWithRandomSearch(
            metric=metric,
            max_bootstrapped_demos=max_bootstrapped_demos,
            max_labeled_demos=max_labeled_demos,
            max_rounds=max_rounds,
            num_candidate_programs=num_candidate_programs,
        )
        return optimizer.compile(module, trainset=trainset)

    if optimizer_name != "BootstrapFewShot":
        raise ValueError(
            f"Unsupported few-shot optimizer {optimizer_name!r}; use "
            "LabeledFewShot, BootstrapFewShot, or BootstrapFewShotWithRandomSearch."
        )

    optimizer = dspy.BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=max_bootstrapped_demos,
        max_labeled_demos=max_labeled_demos,
        max_rounds=max_rounds,
    )
    return optimizer.compile(module, trainset=trainset)


def compile_gan_s0_module_gepa(
    records: list[GanRecord],
    *,
    program_variant: str = GAN_FREQUENCY_S0_DIRECT_VARIANT,
    optimizer_metric: str = "semantic_frequency_with_evidence_feedback",
    auto: str | None = None,
    max_full_evals: int | None = None,
    max_metric_calls: int | None = None,
    reflection_minibatch_size: int = 3,
    candidate_selection_strategy: str = "pareto",
    skip_perfect_score: bool = True,
    add_format_failure_as_feedback: bool = False,
    track_stats: bool = False,
    track_best_outputs: bool = False,
    use_cloudpickle: bool = False,
    num_threads: int | None = None,
    seed: int | None = 0,
    log_dir: Path | None = None,
    reflection_lm: dspy.LM | None = None,
) -> GanFrequencyS0Module | GanFrequencyS0DirectModule:
    """Compile a Gan S0 module with GEPA and a feedback metric."""
    try:
        metric = GAN_FREQUENCY_S0_OPTIMIZER_METRICS[optimizer_metric]
    except KeyError as exc:
        allowed = ", ".join(sorted(GAN_FREQUENCY_S0_OPTIMIZER_METRICS))
        raise ValueError(f"Unknown optimizer_metric {optimizer_metric!r}; use {allowed}.") from exc

    trainset = make_gan_synthesis_dspy_examples(records)
    optimizer = dspy.GEPA(
        metric=metric,
        auto=auto,
        max_full_evals=max_full_evals,
        max_metric_calls=max_metric_calls,
        reflection_minibatch_size=reflection_minibatch_size,
        candidate_selection_strategy=candidate_selection_strategy,
        reflection_lm=reflection_lm or dspy.settings.lm,
        skip_perfect_score=skip_perfect_score,
        add_format_failure_as_feedback=add_format_failure_as_feedback,
        track_stats=track_stats,
        track_best_outputs=track_best_outputs,
        num_threads=num_threads,
        seed=seed,
        log_dir=str(log_dir) if log_dir is not None else None,
        gepa_kwargs={"use_cloudpickle": use_cloudpickle},
    )
    module = build_gan_s0_module(program_variant)
    return optimizer.compile(module, trainset=trainset)


def build_gan_s0_module(
    program_variant: str,
    *,
    prompt_version: str | None = None,
    candidate_presentation: str | None = None,
    context_policy: str | None = None,
) -> (
    GanFrequencyS0Module
    | GanFrequencyS0DirectModule
    | GanFrequencyS0VerifyRepairModule
    | GanFrequencyS0TemporalCandidatesVerifyRepairModule
    | GanFrequencyS0TemporalCandidatesSinglePassModule
    | GanFrequencyS0TemporalEventTableVerifyRepairModule
    | GanFrequencyS0TemporalEventTableSinglePassModule
    | GanFrequencyS0MultipleAnswerDetSelectorModule
    | GanFrequencyS0SeededMultipleAnswerDetSelectorModule
    | GanFrequencyS0ReactTemporalToolsModule
):
    resolved_prompt_version = prompt_version or default_gan_frequency_s0_prompt_version(
        program_variant
    )
    if program_variant == GAN_FREQUENCY_S0_VARIANT:
        return GanFrequencyS0Module()
    if program_variant == GAN_FREQUENCY_S0_DIRECT_VARIANT:
        return GanFrequencyS0DirectModule(prompt_version=resolved_prompt_version)
    if program_variant == GAN_FREQUENCY_S0_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0VerifyRepairModule(prompt_version=resolved_prompt_version)
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0TemporalCandidatesVerifyRepairModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        resolved_context_policy = (
            context_policy
            or GAN_CONTEXT_POLICY_FULL_NOTE_PLUS_DETERMINISTIC_TEMPORAL_CANDIDATES
        )
        return GanFrequencyS0TemporalCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version,
            candidate_presentation=candidate_presentation,
            context_policy=resolved_context_policy,
        )
    if program_variant == GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0LlmTemporalCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0DateEventsCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0LlmDateEventsCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0HybridDateEventsCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_VARIANT:
        return GanFrequencyS0EntityTagsDateEventsSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_VARIANT:
        return GanFrequencyS0HybridTemporalCandidatesSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_GUARDS_VARIANT:
        return GanFrequencyS0TemporalCandidatesAdjudicateDetGuardsModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_DET_EVIDENCE_VARIANT:
        return GanFrequencyS0TemporalCandidatesAdjudicateDetEvidenceModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONFIRM_ONLY_VARIANT:
        return GanFrequencyS0TemporalCandidatesAdjudicateConfirmOnlyModule(
            prompt_version=resolved_prompt_version
        )
    if (
        program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_NO_GUARDS_VARIANT
    ):
        return GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairNoGuardsModule(
            prompt_version=resolved_prompt_version
        )
    if (
        program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_VARIANT
    ):
        return GanFrequencyS0TemporalCandidatesAdjudicateVerifyRepairModule(
            prompt_version=resolved_prompt_version
        )
    if (
        program_variant
        == GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_VARIANT
    ):
        return GanFrequencyS0TemporalCandidatesAdjudicateConstrainedVerifierModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0LlmTemporalCandidatesVerifyRepairModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_VERIFY_REPAIR_VARIANT:
        return GanFrequencyS0TemporalEventTableVerifyRepairModule()
    if program_variant == GAN_FREQUENCY_S0_TEMPORAL_EVENT_TABLE_SINGLE_PASS_VARIANT:
        return GanFrequencyS0TemporalEventTableSinglePassModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT:
        return GanFrequencyS0MultipleAnswerDetSelectorModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_SEEDED_MULTIPLE_ANSWER_DET_SELECTOR_VARIANT:
        return GanFrequencyS0SeededMultipleAnswerDetSelectorModule(
            prompt_version=resolved_prompt_version
        )
    if program_variant == GAN_FREQUENCY_S0_REACT_TEMPORAL_TOOLS_VARIANT:
        return GanFrequencyS0ReactTemporalToolsModule()
    raise ValueError(f"Unsupported Gan S0 program variant: {program_variant!r}")

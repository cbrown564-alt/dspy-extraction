"""Gan S0 DSPy signatures and prompt-version builders."""
from __future__ import annotations

from typing import Optional

import dspy

from clinical_extraction.gan.s0.variant_routing import (
    GAN_FREQUENCY_S0_ADJUDICATE_VERIFY_REPAIR_SPAN_CHECK_PROMPT_VERSION,
    GAN_FREQUENCY_S0_CONFIRM_ONLY_VERIFIER_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_V1_2_GUARDRAILS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DATE_EVENTS_CANDIDATES_SINGLE_PASS_V1_2B_SCHEMA_GUARD_ONLY_PROMPT_VERSION,
    GAN_FREQUENCY_S0_DIRECT_GUARDRAILS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_ENTITY_TAGS_DATE_EVENTS_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_EVIDENCE_OPTIONAL_PROMPT_VERSION,
    GAN_FREQUENCY_S0_EVIDENCE_SPAN_CHECK_PROMPT_VERSION,
    GAN_FREQUENCY_S0_GUARDRAILS_PORT_TEMPORAL_PROMPT_VERSION,
    GAN_FREQUENCY_S0_HYBRID_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_HYBRID_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_DATE_EVENTS_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_LLM_TEMPORAL_CANDIDATES_VERIFY_REPAIR_PROMPT_VERSION,
    GAN_FREQUENCY_S0_SYNTHESIS_PORT_TEMPORAL_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_CONSTRAINED_VERIFIER_PROMPT_VERSION,
    GAN_FREQUENCY_S0_TEMPORAL_CANDIDATES_ADJUDICATE_VERIFY_REPAIR_PROMPT_VERSION,
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
    GAN_FREQUENCY_S0_TOOL_DATE_RESOLVER_SINGLE_PASS_PROMPT_VERSION,
    GAN_FREQUENCY_S0_VERIFY_REPAIR_PROMPT_VERSION,
)


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


class GanFrequencyS0EntityTagsSignature(dspy.Signature):
    """Extract clinical entities and events with offsets and temporality context.
    
    Output entity_tags as a JSON object with key "entity_tags".
    """
    note_text: str = dspy.InputField(desc="Clinical note text")
    entity_tags_json: str = dspy.OutputField(
        desc='JSON object {"entity_tags": [...]} containing clinical entities, counts, and temporality hints'
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

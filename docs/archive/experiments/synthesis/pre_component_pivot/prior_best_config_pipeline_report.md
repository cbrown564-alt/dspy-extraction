# Best Config Pipeline Report

Date prepared: 2026-05-21

This report explains the best-performing ExECTv2 and Gan 2026 configurations,
what they were asked to do, how a document moves through the pipeline, how
normalisation and scoring are applied, and what the remaining error patterns
mean. It is intended to be readable without first reading the codebase.

## Executive Summary

The project evaluates modular clinical extraction conditions. A result is
traceable through:

`condition id -> resolved components -> prompt/schema -> model response -> parsed output -> projection -> scoring view -> aggregate table`.

The best configurations identified in the preserved analyses are:

| Dataset | Best config | Model | Main result |
|---|---|---|---|
| ExECTv2 | `full_exect_qwen35_sz_diag_tuned` | `qwen_3_6_35b` | Best local/Qwen full-schema config; seizure type F1 `0.639`, diagnosis exact match `0.711`, medication name F1 `0.977`. |
| ExECTv2 | `full_exect_gemini_combined_examples` | `gemini_3_flash` | Best overall/frontier-like ExECT config; seizure type F1 `0.678`, diagnosis exact match `0.868`, medication name F1 `0.892`. |
| Gan 2026 | `gan_frequency_v3_qwen35` | `qwen_3_6_35b` | Best completed Gan frequency format-sweep condition; relaxed diagnostic match `0.646`, strict match `0.592`. Completed-document relaxed match was `190/233 = 0.815`, with timeout failures masking full-set performance. |

Important caveat: the final write-ups and comparison tables are preserved in
`docs/`, but the raw Round 2 ExECT and Gan-v3 document-level run directories
are not present under `runs/0. Pilot/` in this checkout. The worked examples
below therefore use the current repository code/configs to render the prompt
and demonstrate validation, projection, normalisation, and scoring on real
dataset documents. The aggregate metrics are taken from the preserved analysis
documents.

## Pipeline Overview

For each condition, the single-agent runner:

1. Loads and resolves a condition from `configs/conditions.yaml`.
2. Loads the task, dataset slice, component variants, schema contract, and
   scoring views.
3. Renders one prompt per document with the resolved task rules, examples,
   field contracts, JSON shape, and source letter.
4. Calls a provider adapter and stores the raw response.
5. Parses JSON and validates it against the schema contract.
6. Projects the parsed payload into a neutral field structure.
7. Scores projected fields against gold records through explicit scoring views.
8. Aggregates document-level scoring records into summary tables.

The runner writes this artifact shape for each document when raw run artifacts
are available:

| Artifact | Meaning |
|---|---|
| `prompt.txt` | Exact model-facing prompt for the document. |
| `raw_response.json` / `.txt` | Provider-normalised raw output and text. |
| `parsed_response.json` | Parsed JSON object, if available. |
| `output_validation.json` | Parse/schema/format validity and abstention state. |
| `projected_output.json` | Neutral projected fields plus projection metadata. |
| `scoring_records.json` | Atomic score records used to build aggregate metrics. |
| `errors.json` | Provider errors, validation errors, and missing-gold state. |

Core implementation entry points:

| Step | File |
|---|---|
| Resolve configs | `src/clinical_extraction/runners/conditions.py` |
| Render prompt | `src/clinical_extraction/prompts/assembly.py` |
| Validate JSON | `src/clinical_extraction/schemas/validation.py` |
| Project payload | `src/clinical_extraction/projection/policies.py` |
| Score output | `src/clinical_extraction/runners/single_agent.py` |
| Field scorers | `src/clinical_extraction/scoring/field_scorers.py` |
| Gan frequency normaliser | `src/clinical_extraction/normalizers/seizure_frequency.py` |

## Resolved Best Configs

### ExECTv2: `full_exect_qwen35_sz_diag_tuned`

This condition uses the schema-ladder minimal full-frequency base rather than
the original `best_config`, because the richer ILAE guideline was net-negative
for Qwen at full schema width.

Key resolved choices:

| Family | Choice |
|---|---|
| Dataset | `exect_v2`, validation slice |
| Task | `exect_full_clinical_frequency` |
| Model | `qwen_3_6_35b` |
| Guideline | `minimal_current_clinical` via schema-ladder base |
| Schema | `full_clinical_extraction_with_frequency` |
| Example policy | `seizure_and_diagnosis_mapping_examples` |
| Projection | `relaxed` |
| Normalisation | `clinical_then_benchmark` |
| Scoring views | medication, seizure type, seizure status, diagnosis, investigation, normalised frequency, relaxed diagnostic, format, abstention, evidence validity/support |

The main Round 2 change was adding seizure/diagnosis mapping examples. These
examples reduce label-granularity errors such as mapping "focal seizures with
altered awareness" to the benchmark-compatible `focal seizure` rather than the
more ILAE-specific `focal impaired awareness seizure`.

### ExECTv2: `full_exect_gemini_combined_examples`

This is the best ExECT overall condition in the preserved comparison. Gemini
benefited from the richer original ExECT full configuration, but its medication
performance regressed when boundary examples were replaced by seizure/diagnosis
examples. The final condition combines both example sets.

Key resolved choices:

| Family | Choice |
|---|---|
| Dataset | `exect_v2`, validation slice |
| Task | `exect_full_clinical_frequency` |
| Model | `gemini_3_flash` |
| Base | `exect_full` / original Gemini full-schema anchor |
| Example policy | `boundary_and_seizure_diag_examples` |
| Projection | `relaxed` |
| Normalisation | `clinical_then_benchmark` |

This preserves medication temporality examples while adding seizure/diagnosis
mapping examples.

### Gan 2026: `gan_frequency_v3_qwen35`

This condition targets only current seizure-frequency extraction and
normalisation.

Key resolved choices:

| Family | Choice |
|---|---|
| Dataset | `gan_2026`, validation slice |
| Task | `gan_frequency_core` |
| Model | `qwen_3_6_35b` |
| Guideline | `gan_frequency_policy_v3` |
| Schema | `gan_frequency_json` |
| Example policy | `gan_frequency_format_examples_v3` |
| Projection | `relaxed` |
| Main scoring | strict normalised frequency and relaxed Purist diagnostic bucket |

The v3 condition adds the critical Gan annotation rule:

Use a seizure-free label only when seizure freedom is at least 6 months. If
seizure-free for less than 6 months, compute a rate from total events over the
described period instead of outputting `seizure free for N unit`.

## Full Example Prompt

This is the full prompt rendered by the current code for condition
`gan_frequency_v3_qwen35` on real validation document `GAN014540`.

```text
You are extracting current clinical facts from an epilepsy clinic letter.

Task: Determine the current clinically relevant seizure frequency from the letter.
Requested fields:
- current_seizure_frequency

Clinical extraction rules:
Inclusion rules:
- Extract the current seizure frequency.
Normalization rules:
- Prefer explicit present frequency.
- Compute from dated events when needed; if current period unclear, use the most recent stated count and period.
- Choose the highest current seizure-type frequency when multiple current types are quantified.
- Output only: 'N per unit', 'N to M per unit', 'N per M unit', 'N cluster per unit, M per cluster', 'seizure free for N unit', 'unknown', or 'no seizure frequency reference'.
- Valid units: day, week, month, year (singular). Convert quarter -> 3 month, fortnight -> 2 week.
- Strip inequality prefixes (<=, >=, at most, at least, up to).
- Use 'to' not 'or' for numeric ranges.
- Convert adjective rates: daily or nightly -> '1 per day'; weekly -> '1 per week'; monthly -> '1 per month'; biweekly or fortnightly -> '1 per 2 week'.
- Convert 'every N unit' -> '1 per N unit'.
- For cluster seizures: 'N cluster per unit, M per cluster'.
- Use 'unknown' only for purely qualitative descriptions with no numeric count.
Abstention rules:
- Only use 'seizure free for N unit' when the patient has been seizure-free for 6 months or longer. If seizure-free for less than 6 months, compute the rate from the total event count over the full described period (including events before the seizure-free period began).
- Do not use 'seizure free for N unit' when the letter also reports a current quantified rate; prefer the rate.

First apply the task rules and field constraints silently. Then return only the final JSON.

Evidence requirements:
- Every present claim must include an exact contiguous source quote copied verbatim.
- For normalized labels, the quote must contain the specific text that justifies the label assigned, not merely a related mention.
- If no verbatim quote directly supports a claim, omit the claim or use the schema's null or empty value.

Examples (format, clusters, historical period, and 6-month SF threshold):
- 'Two events over the last five months' -> "2 per 5 month"
- '3 to 4 focal seizures per month' -> "3 to 4 per month"
- 'Seizure-free for 18 months' -> "seizure free for 18 month"  [SF >= 6 months: use SF label]
- 'Seizures are sporadic but frequency unclear' -> "unknown"
- '<= 6 to 7 per year' -> "6 to 7 per year"  [strip inequality qualifiers]
- 'daily' or 'nightly' -> "1 per day"  [adjective rate -> canonical]
- 'biweekly' or 'fortnightly' -> "1 per 2 week"  [named interval -> canonical]
- 'every 4 days' -> "1 per 4 day"  [every-N pattern]
- '3 or 4 per week' -> "3 to 4 per week"  [or -> to]
- 'daily absences and 2 focal seizures per month' -> "1 per day"  [pick highest frequency type]
- '2 cluster days per month; typically 4 to 6 seizures on each cluster day' -> "2 cluster per month, 4 to 6 per cluster"  [cluster format]
- 'Cluster frequency unclear this month; last month approximately 4 clusters' -> "4 cluster per month, multiple per cluster"  [use most recent stated count]
- 'He had 4 seizures in February when withdrawing from medication; has remained well since (now May, 3 months later)' -> "4 per 3 month"  [SF < 6 months: compute rate from total count over full period, not SF label]
- 'Had 2 seizures in January; none since (now April, 3 months)' -> "2 per 3 month"  [SF < 6 months: use period count]
- 'Has been seizure-free for the past 2 weeks; typically has 1 to 2 seizures per month' -> "1 to 2 per month"  [ongoing rate overrides short SF period]
- 'Currently seizure free; no events for the past 14 months on current medication' -> "seizure free for 14 month"  [SF >= 6 months: use SF label]
- '11 to 28 events per quarter' -> "11 to 28 per 3 month"  [quarter = 3 month]

Return JSON only with this shape:
{
  "current_seizure_frequency": "string",
  "evidence": [
    {
      "quote": "string"
    }
  ],
  "abstain_reason": "string"
}

Field contracts:
- current_seizure_frequency:
  semantics: Current clinically relevant seizure frequency from the letter.
  allowed_values: normalized frequency label, unknown, no seizure frequency reference
  null_policy: Use an empty string only when abstain_reason explains no supported current frequency.
  abstention_behavior: Provide abstain_reason when the source is vague, conflicting, historical only, or lacks a current frequency reference.
- evidence:
  semantics: Exact source quote or quotes supporting the current frequency or abstention decision.
  null_policy: Use an empty list when no supporting quote exists and explain in abstain_reason.
- abstain_reason:
  semantics: Explanation for abstaining or for returning unknown/no-reference instead of a normalized rate.
  null_policy: Use an empty string only when a supported current frequency is provided.
- evidence.quote:
  semantics: Exact contiguous source quote supporting the current frequency, unknown decision, or no-reference decision.
  support_behavior: Quote must exist in source and contain the specific frequency, rate, or absence statement that justifies the label assigned, not merely a general seizure mention.
  null_policy: Use an empty evidence list only when no quote supports the frequency value or abstention.

Source letter:

KINGS NEUROSCIENCES CENTRE


Clinic Date: 14 August 2018

Dr Wang
Saffron Park Hospital

Saffron Park, London, E14 7JL
Dear Dr Wang
John Doe, DOB: 21-11-1982, Hospital No: P546484 NHS No. 5484656746
Flat 15 Roundwood Road, London, E14 7JL

I reviewed the above patient in the Neurology Clinic today. He was referred following two discrete events suggestive of seizures and has been under our care since early 2018. He reports no prior neurological history, no significant head injuries, and no family history of similar events. Sleep has been irregular due to shift work, and he previously missed evening doses of medication, for which he has now set up smartphone alarms and NFC tag prompts at home to improve adherence.

His first seizure occurred in December 2017 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of deja vu. The second event was in August 2018 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms. There have been no witnessed daytime events, tongue biting, or urinary incontinence reported, and post-event confusion was brief on both occasions. He denies aura outside of these episodes and has not reported myoclonic jerks on awakening.

He was initially started by the admitting team on Lamotrigine, titrated to 100 mg b.d., but developed a dose-related rash at week five which resolved on withdrawal. We then introduced Levetiracetam which he is currently taking at 750 mg b.d. without mood disturbance. He also trialled low-dose Propranolol for tremor related to anxiety around medication taking, which he discontinued after three weeks as symptoms settled once his reminder system was in place. He now uses the smartphone alarms and NFC tags consistently and reports no missed doses in the last six weeks.

Since commencing Levetiracetam he has not had further events. He notes mild fatigue at the end of shifts but no cognitive complaints at work. He does not drive. Bloods in July 2018 (U&E, LFT, FBC, vitamin D) were within reference ranges. A routine EEG in May 2018 was non-diagnostic, and MRI brain with epilepsy protocol in June 2018 was structurally unremarkable.

Plan: given the interval without further events on the current regimen and improved adherence, I have advised continuation of Levetiracetam 750 mg b.d. without change. We discussed sleep hygiene and maintaining the digital reminders. I have provided a rescue plan for any prolonged event (seizure first aid guidance shared in clinic). He will keep a simple event and trigger diary on his phone. Should further episodes occur, we will consider ambulatory EEG and revisit treatment options.

I will review him in three months or sooner if there are recurrent events or adverse effects. Please let me know if there are any concerns in the interim.

Yours sincerely

Do not include reasoning, markdown, or commentary. Return only the final JSON object.
```

## Worked Example: Gan Document `GAN014540`

### Dataset Input And Gold

The source letter says there were two seizure events: one in December 2017 and
one in August 2018. The clinic date is 14 August 2018. Although the letter also
says there have been no further events since starting levetiracetam, the second
event occurred in the clinic month, so the 6-month seizure-free threshold is not
met.

Gold fields:

```json
{
  "current_seizure_frequency": "2 per 8 month",
  "seizure_frequency_per_month": 0.25,
  "seizure_frequency_purist": "(1/6M,1/M)",
  "seizure_frequency_pragmatic": "infrequent",
  "reference_label": "2 per 8 month",
  "reference_per_month": 0.25
}
```

Gold rationale:

```text
The letter describes two discrete seizure events: first in December 2017 and second in August 2018.
The patient has not been seizure-free for at least 6 months. Since that criterion is not met, calculate frequency.
The explicit count is 2 events over December 2017 to August 2018, which is 8 months.
```

### Example Model Output

This is a valid output shape for the condition and document:

```json
{
  "current_seizure_frequency": "2 per 8 month",
  "evidence": [
    {
      "quote": "His first seizure occurred in December 2017 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of deja vu. The second event was in August 2018 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms"
    }
  ],
  "abstain_reason": ""
}
```

### Validation Output

The validator checks only the JSON/schema contract, not clinical correctness.

```json
{
  "parse_valid": true,
  "schema_valid": true,
  "format_valid": true,
  "validation_errors": [],
  "abstained": false,
  "abstain_reason": null
}
```

### Projection Output

The projection policy is `relaxed`. For Gan, projection mostly preserves
`current_seizure_frequency` and moves the payload into the neutral `fields`
object used by scorers.

```json
{
  "projection_policy": "relaxed",
  "fields": {
    "current_seizure_frequency": "2 per 8 month",
    "evidence": [
      {
        "quote": "His first seizure occurred in December 2017 in Ireland, at night while asleep. He woke with rhythmic twitching of the right arm and a sense of deja vu. The second event was in August 2018 in Scotland, also during sleep, lasting five minutes with a similar pattern of symptoms"
      }
    ]
  },
  "metadata": {
    "normalize_values": true,
    "require_evidence_for_present": false,
    "drop_unsupported_present_fields": false,
    "source_projection_policy_id": "relaxed",
    "schema_contract_id": "gan_frequency_json"
  },
  "projection_status": "projected"
}
```

The actual projected object also includes empty neutral fields for medications,
seizure types, diagnosis, and investigations because the shared compact
projection function supports all extraction schemas. The scoring plan gates
those irrelevant fields off because this Gan task only asks for
`current_seizure_frequency`.

### Normalisation And Scoring Transform

The Gan frequency normaliser converts both prediction and gold to seizures per
month and to diagnostic categories.

```json
{
  "prediction": {
    "label": "2 per 8 month",
    "normalised_string": "2 per 8 month",
    "per_month": 0.25,
    "purist": "(1/6M,1/M)",
    "pragmatic": "infrequent"
  },
  "gold": {
    "label": "2 per 8 month",
    "normalised_string": "2 per 8 month",
    "per_month": 0.25,
    "purist": "(1/6M,1/M)",
    "pragmatic": "infrequent"
  },
  "strict_frequency_match": true,
  "relaxed_diagnostic_match": true
}
```

Scoring records emitted for this example:

```json
[
  {"scoring_view": "format_validity", "metric": "parse_valid", "value": true},
  {"scoring_view": "format_validity", "metric": "schema_valid", "value": true},
  {"scoring_view": "format_validity", "metric": "format_valid", "value": true},
  {"scoring_view": "abstention", "metric": "abstained", "value": false},
  {"scoring_view": "normalized_frequency", "metric": "frequency_match", "value": true},
  {"scoring_view": "relaxed_diagnostic", "metric": "frequency_relaxed_match", "value": true},
  {"scoring_view": "evidence_validity", "metric": "quote_exists", "value": true},
  {"scoring_view": "evidence_support", "metric": "support_status", "value": "valid_quote_no_gold_overlap"},
  {"scoring_view": "evidence_support", "metric": "supported", "value": false},
  {"scoring_view": "abstention", "metric": "expected_abstention", "value": false},
  {"scoring_view": "abstention", "metric": "abstention_decision_correct", "value": true},
  {"scoring_view": "abstention", "metric": "abstain_reason_present", "value": false}
]
```

`valid_quote_no_gold_overlap` is expected for Gan because the dataset provides
support quote strings but not offset-based gold evidence spans. Therefore Gan
evidence support is structurally not comparable with ExECT gold-span support.
For Gan, quote validity (`quote_exists`) is the meaningful evidence metric.

## Worked Example: ExECT Document `EA0008`

The ExECT examples demonstrate the broader multi-field projection/scoring path.
The current code renders an 8,905-character prompt for `EA0008` under
`full_exect_qwen35_sz_diag_tuned`; it includes task rules, allowed labels,
schema shape, field contracts, and the full source letter.

### Source Facts

Key source statements:

```text
Diagnosis: symptomatic structural focal epilepsy
Seizure type and frequency: focal seizures with altered awareness every 3 weeks
Current anti-epileptic medication: lamotrigine 75mg bd (to reduce and stop as detailed below)
To start levetiracetam as detailed below
```

Gold fields:

```json
{
  "current_anti_seizure_medications": [
    {
      "name": "lamotrigine",
      "dose": "75",
      "dose_unit": "mg",
      "frequency": "twice daily"
    }
  ],
  "planned_anti_seizure_medications": [
    {"name": "levetiracetam"}
  ],
  "current_seizure_frequency": [
    {
      "value": "1 per 3 week",
      "count": "1",
      "period_count": "3",
      "period_unit": "week",
      "seizure_type": "focal seizure"
    }
  ],
  "current_seizure_status": "active seizures",
  "seizure_types": ["focal seizure"],
  "investigations": {"eeg": "", "mri": ""},
  "epilepsy_diagnosis_type": ["focal epilepsy"]
}
```

### Example Model Output

```json
{
  "current_anti_seizure_medications": [
    {
      "name": "lamotrigine",
      "dose": "75",
      "dose_unit": "mg",
      "frequency": "bd"
    }
  ],
  "seizure_types": ["focal seizures with altered awareness"],
  "current_seizure_status": "active seizures",
  "epilepsy_diagnosis_type": "symptomatic structural focal epilepsy",
  "investigations": {
    "eeg": "not stated",
    "mri": "not stated"
  },
  "current_seizure_frequency": "1 per 3 week"
}
```

### Projection Output

The relaxed projection applies clinical normalisers:

```json
{
  "projection_policy": "relaxed",
  "fields": {
    "current_anti_seizure_medications": [
      {
        "name": "lamotrigine",
        "dose": "75",
        "dose_unit": "mg",
        "frequency": "twice daily",
        "temporality": "uncertain",
        "confidence": "",
        "evidence": []
      }
    ],
    "seizure_types": ["focal seizure"],
    "current_seizure_status": "active seizures",
    "epilepsy_diagnosis_type": "focal epilepsy",
    "current_seizure_frequency": "1 per 3 week",
    "investigations": {
      "eeg": "",
      "mri": ""
    }
  },
  "projection_status": "projected"
}
```

Important transformations:

| Raw output | Projected output | Why |
|---|---|---|
| `bd` | `twice daily` | Medication frequency normaliser. |
| `focal seizures with altered awareness` | `focal seizure` | Benchmark-compatible seizure type normalisation. |
| `symptomatic structural focal epilepsy` | `focal epilepsy` | Diagnosis normaliser removes unsupported/modifier-specific surface form. |
| `not stated` investigation | empty canonical field | Canonical investigation result maps absence/not-stated to the empty benchmark-compatible value. |
| `1 per 3 week` | `1 per 3 week` | Already canonical. |

### Scoring Outcome

For this worked example, the projected output scores as correct on the core
fields:

| Scoring view | Result |
|---|---|
| medication_name | TP 1, FP 0, FN 0, F1 1.0 |
| medication_tuple | TP 1, FP 0, FN 0, F1 1.0 |
| medication_detail | dose 1.0, dose_unit 1.0, frequency 1.0 |
| seizure_type | TP 1, FP 0, FN 0, F1 1.0 |
| seizure_type_gold_projected | TP 1, FP 0, FN 0, F1 1.0 |
| benchmark_collapsed seizure type | TP 1, FP 0, FN 0, F1 1.0 |
| seizure_status | exact match true |
| diagnosis | exact match any gold true |
| normalized_frequency | strict match true |
| relaxed_diagnostic | relaxed match true |

Frequency transform:

```json
{
  "prediction": {
    "label": "1 per 3 week",
    "per_month": 1.3333333333333333,
    "purist": "(1/M,1/W)",
    "pragmatic": "frequent"
  },
  "gold": {
    "label": "1 per 3 week",
    "per_month": 1.3333333333333333,
    "purist": "(1/M,1/W)",
    "pragmatic": "frequent"
  },
  "strict_frequency_match": true,
  "relaxed_diagnostic_match": true
}
```

Because this particular ExECT condition does not require quote-bearing fields,
the example output has no evidence quotes. Core extraction scores can still be
correct, while evidence validity/support records are false or `no_quote`.

## Normalisation And Scoring Code

The exact code is in the files listed below. This section extracts the
decision-critical parts.

### Output Validation

File: `src/clinical_extraction/schemas/validation.py`

```python
def validate_output(payload: Any, schema: dict[str, Any]) -> OutputValidationResult:
    parse_valid = payload is not None
    validation_errors = [] if parse_valid else ["parsed output is null"]
    if parse_valid:
        validation_errors = _validate_schema(payload, schema, path="$")
    schema_valid = parse_valid and not validation_errors
    abstain_reason = extract_abstain_reason(payload)
    return OutputValidationResult(
        parse_valid=parse_valid,
        schema_valid=schema_valid,
        format_valid=parse_valid and schema_valid,
        validation_errors=validation_errors,
        abstained=abstain_reason is not None,
        abstain_reason=abstain_reason,
    )
```

Validation only checks parse/schema/format compliance and explicit abstention.
It does not decide whether the extracted clinical claim is correct.

### Projection

File: `src/clinical_extraction/projection/policies.py`

```python
RELAXED_POLICY = ProjectionPolicy(
    name="relaxed",
    normalize_values=True,
    require_evidence_for_present=False,
    force_current_temporality=False,
    drop_unsupported_present_fields=False,
)

def medication_from_raw(item: Any, policy: ProjectionPolicy) -> dict[str, Any] | None:
    projected = {
        "name": canonical_anti_seizure_medication_name(item.get("name")) if policy.normalize_values else item.get("name"),
        "dose": normalize_dose(item.get("dose")) if policy.normalize_values else item.get("dose"),
        "dose_unit": normalize_unit(item.get("dose_unit") or item.get("unit")) if policy.normalize_values else item.get("dose_unit") or item.get("unit"),
        "frequency": normalize_frequency(item.get("frequency")) if policy.normalize_values else item.get("frequency"),
        "temporality": "current" if policy.force_current_temporality else item.get("temporality", "uncertain"),
        "confidence": item.get("confidence", ""),
        "evidence": item.get("evidence", []),
    }
    if policy.drop_unsupported_present_fields and not has_evidence(projected):
        return None
    return projected
```

Projection is an explicit experimental intervention. Under `relaxed`, values
are normalised, but unsupported present fields are not dropped.

### Frequency Label Normalisation

File: `src/clinical_extraction/normalizers/seizure_frequency.py`

```python
def normalise_label_string(label: Any) -> str:
    if label is None:
        return ""
    text = re.sub(r"\s+", " ", str(label).strip().lower())
    text = text.replace("–", "-").replace("—", "-")
    for plural in ("months", "weeks", "days", "years"):
        text = re.sub(rf"\b{plural}\b", plural[:-1], text)
    text = re.sub(r"(?<=\d)-(?=\d)", " to ", text)
    return text

def label_to_per_month(label: Any) -> float | None:
    s = normalise_label_string(label)
    if not s:
        return None
    if s in ("no seizure frequency reference", "no seizure", "no seizures"):
        return NO_SEIZURE
    if s.startswith("seizure free"):
        return NO_SEIZURE
    if s.startswith("unknown"):
        return UNKNOWN_FREQUENCY
    # cluster and simple-rate regexes then convert day/week/month/year to per-month
```

Key conversion constants:

```python
_UNIT_TO_MONTH = {
    "day": 30.0,
    "week": 4.0,
    "month": 1.0,
    "year": 1.0 / 12.0,
}
```

Ranges such as `3 to 4 per month` resolve to their midpoint for per-month
classification. The keyword `multiple` maps to 3.

### Strict Vs Relaxed Frequency Scoring

File: `src/clinical_extraction/scoring/field_scorers.py`

```python
def frequency_score(predicted: Any, gold_values: list[Any]) -> bool:
    pred_cls, pred_key = _frequency_strict_class(predicted)
    valid_gold = [_frequency_strict_class(g) for g in gold_values]
    valid_gold = [(cls, key) for cls, key in valid_gold if cls != "unparsed"]
    if not valid_gold:
        return pred_cls == "no_reference"
    return any(
        pred_cls == g_cls and (pred_cls != "rate" or pred_key == g_key)
        for g_cls, g_key in valid_gold
    )

def frequency_relaxed_diagnostic_score(predicted: Any, gold_values: list[Any]) -> bool:
    pred_cls, pred_pm = _frequency_relaxed_pm(predicted)
    valid_gold = [_frequency_relaxed_pm(g) for g in gold_values]
    valid_gold = [(cls, pm) for cls, pm in valid_gold if cls != "unparsed"]
    if not valid_gold:
        return pred_cls == "no_reference"
    pred_purist = _purist_for_relaxed(pred_cls, pred_pm)
    return pred_purist is not None and any(
        _purist_for_relaxed(g_cls, g_pm) == pred_purist for g_cls, g_pm in valid_gold
    )
```

Strict scoring requires the same canonical label string for rate labels.
Relaxed scoring compares the Purist diagnostic bucket after converting to
seizures per month.

### Seizure Type And Diagnosis Scoring

File: `src/clinical_extraction/scoring/field_scorers.py`

```python
def seizure_type_score(predicted, gold, *, collapsed=False, gold_projected=False, benchmark_canonical=False, ilae2022=False):
    if gold_projected:
        normalizer = canonical_seizure_type_contract_projected
    elif collapsed:
        normalizer = benchmark_seizure_type_label
    elif benchmark_canonical:
        normalizer = canonical_seizure_type_benchmark
    elif ilae2022:
        normalizer = canonical_seizure_type_ilae2022
    else:
        normalizer = canonical_seizure_type
    return score_sets(
        [normalizer(_seizure_type_label(item)) for item in predicted],
        [normalizer(_seizure_type_label(item)) for item in gold],
    )

def diagnosis_score(predicted: Any, gold: Any, *, collapsed: bool = False) -> bool:
    normalizer = benchmark_epilepsy_label if collapsed else canonical_diagnosis
    return bool(normalizer(predicted) and normalizer(predicted) == normalizer(gold))
```

The runner also explicitly handles empty diagnosis gold:

```python
if gold_diagnoses:
    diag_match = any(diagnosis_score(predicted_diagnosis, d, collapsed=False) for d in gold_diagnoses)
else:
    diag_match = not canonical_diagnosis(predicted_diagnosis)
```

This fixed a prior artifact where correct null predictions were scored wrong
because `any([])` is always false.

## Full Summary Stats

### ExECT Round 2 Results

These are the authoritative Round 2 values preserved in
`docs/schema_ladder_sweep_findings.md` and `docs/primary_sweep_plan.md`.

| Metric | ladder_qwen35 | qwen35_best | qwen35_r2 | gemini_best | gemini_r2 | gemini_combined |
|---|---:|---:|---:|---:|---:|---:|
| medication_name F1 | 0.989 | 0.885 | 0.977 | 0.886 | 0.798 | 0.892 |
| medication_tuple F1 | 0.859 | 0.768 | 0.856 | 0.761 | 0.712 | 0.776 |
| benchmark_collapsed F1 | 0.808 | 0.769 | 0.769 | 0.794 | 0.804 | 0.808 |
| seizure_type F1 | 0.438 | 0.404 | 0.639 | 0.510 | 0.664 | 0.678 |
| seizure_type_gold_projected F1 | 0.520 | 0.451 | 0.691 | 0.552 | 0.695 | 0.730 |
| diagnosis exact_match | 0.579 | 0.579 | 0.711 | 0.684 | 0.868 | 0.868 |
| seizure_status exact_match | 0.789 | 0.763 | 0.763 | 0.763 | 0.789 | 0.763 |
| eeg_match | 0.917 | 0.917 | 0.917 | 0.833 | 0.833 | 0.833 |
| mri_match | 0.867 | 0.867 | 0.867 | 0.933 | 0.933 | 0.933 |
| normalized_frequency | 0.263 | 0.316 | 0.342 | 0.263 | 0.184 | 0.237 |
| schema_valid | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

Interpretation:

- `full_exect_qwen35_sz_diag_tuned` is the best Qwen configuration.
- `full_exect_gemini_combined_examples` is the best Gemini configuration and
  the best overall ExECT configuration in this comparison.
- Round 2 primarily improved seizure-type and diagnosis fields.
- Frequency remained weak, even in the best ExECT conditions.

### Gan Frequency Format Sweep Results

These are the final all-doc scores preserved in
`docs/gan_frequency_format_sweep_log.md`.

| Condition | Relaxed match | Strict match | ns_wrong | unk_wrong | bucket | unparsed | Notes |
|---|---:|---:|---:|---:|---:|---:|---|
| baseline v1 | 0.578 | 0.554 | 23 | 35 | 22 | 44 | Original Qwen single-call condition. |
| rich_examples | 0.561 | 0.514 | 80 | 11 | 29 | 9 | Examples alone; strict worse than baseline. |
| rich_both | 0.578 | 0.554 | 74 | 22 | 26 | 2 | Guideline + examples; no net relaxed gain. |
| rich_policy | 0.588 | 0.558 | 71 | 20 | 28 | 2 | Policy alone outperformed combined. |
| v2 | 0.588 | 0.565 | 80 | 13 | 23 | 5 | Cluster + historical rule; ns_wrong rebounded. |
| v4 | 0.585 | 0.558 | 73 | 20 | 25 | 4 | Quarter counter-example fixed one case, no overall gain. |
| v5 | 0.592 | 0.575 | 66 | 24 | 28 | 2 | Shorter prompt; lowest ns_wrong, highest unk_wrong. |
| v3 | 0.646 | 0.592 | 67 | 10 | 26 | 1 | Best overall; adds 6-month seizure-free threshold. |

Additional v3 note from the complete error analysis:

- Full-set relaxed match: `190/294 = 0.646`.
- 60 of 104 misses were timeouts.
- Completed-document relaxed match: `190/233 = 0.815`.
- Therefore the v3 prompt content cleared the 0.800 target on completed
  documents, but infrastructure/runtime timeout failures pulled down the
  full-set aggregate.

## Error Analysis Summary

### ExECTv2

Main pre-Round 2 failure:

- Seizure type errors were dominated by label granularity mismatch, not basic
  comprehension failure.
- The model often produced clinically natural ILAE-specific labels where the
  benchmark gold expected broader labels. Example: `focal impaired awareness
  seizure` vs `focal seizure`.
- Diagnosis errors included modifier-capture failures and null-gold scoring
  artifacts.

Round 2 interventions:

- Pruned attractor seizure labels from the benchmark allow-list.
- Added benchmark-canonical seizure normalisation.
- Added `seizure_and_diagnosis_mapping_examples`.
- For Gemini, combined those examples with medication boundary examples to
  prevent medication regression.

Remaining ExECT issues:

- Normalised frequency is still the hardest field. Best values in Round 2 are
  `0.342` for Qwen and `0.237` for Gemini.
- Medication detail remains strong for Qwen, but richer guidance can reduce
  medication recall.
- Investigation fields are near ceiling where gold exists, but a structural
  pattern remains: prior result plus planned repeat investigation can confuse
  result status.
- Evidence support is meaningful on ExECT because gold spans exist, but support
  rates are well below quote-existence rates. Quote generation and gold-span
  grounding are separate capabilities.

### Gan 2026

Main v1/baseline failures:

| Category | Meaning |
|---|---|
| unparsed | Model output was clinically meaningful but not in a canonical label form. |
| wrong UNK | Model abstained with `unknown` when the gold had a computable rate. |
| wrong NS/no_ref | Model used seizure-free/no-reference when the gold expected a rate. |
| wrong bucket | Model produced a rate in a different Purist category from gold. |

The most important discovered annotation rule was the 6-month seizure-free
threshold. Many baseline errors came from short seizure-free windows after a
recent cluster: the model naturally wrote `seizure free for 2 month`, while the
gold expected a rate such as `2 per 2 month`.

v3 fixed the largest semantic direction by adding the 6-month threshold rule,
but introduced or retained:

- Timeout sensitivity from the longer prompt.
- Residual short seizure-free failures, especially medication-withdrawal
  clusters followed by recent stability.
- Year-to-date denominator errors, e.g. treating "five seizures this year to
  date" as per year rather than per January-to-clinic-month window.
- Partial cluster-format failures, e.g. outputting only per-cluster count and
  dropping cluster frequency.
- Calendar arithmetic misses where the model must sum month-named events over a
  span.
- Some probable gold ambiguities or annotation inconsistencies.

Recommended next Gan improvement:

- Re-run v3 or a trimmed v7-like prompt with higher timeout or shorter prompt.
- Preserve the 6-month threshold rule.
- Add targeted examples for medication-withdrawal clusters, year-to-date
  windows, and full cluster-format assembly.
- Treat Gan evidence support as quote validity, not gold-span overlap, unless
  offset gold spans are added.

## What A New Collaborator Should Understand

1. The configs are the experiment design. A "best config" is not just a model;
   it is a named bundle of task, schema, examples, guideline, projection,
   normalisation, and scoring views.
2. Projection is not neutral cleanup. It is an explicit policy that changes
   output interpretation.
3. ExECT and Gan measure different things. ExECT is multi-field and
   span-aware; Gan is narrow but deep frequency normalisation.
4. Strict frequency matching and relaxed diagnostic matching answer different
   questions. Strict asks whether the exact canonical label matches; relaxed
   asks whether the per-month rate lands in the same Purist diagnostic bucket.
5. Evidence validity and evidence support are separate. A quote can exist in
   the source without overlapping a gold evidence span; for Gan, gold span
   overlap is structurally unavailable.
6. The ExECT Round 2 gain is mainly a label-contract/examples gain. The Gan v3
   gain is mainly an annotation-policy gain.
7. The strongest current ExECT overall condition is Gemini combined examples.
   The strongest local ExECT condition is Qwen seizure/diagnosis tuned. The
   strongest completed Gan format-sweep condition is Qwen v3, but its full-set
   score is limited by timeouts.

## Source Documents Used

- `docs/schema_ladder_sweep_findings.md`
- `docs/primary_sweep_plan.md`
- `docs/gan_frequency_format_sweep_log.md`
- `docs/gan_frequency_v3_error_analysis.md`
- `configs/conditions.yaml`
- `configs/tasks.yaml`
- `configs/components.yaml`
- `src/clinical_extraction/runners/single_agent.py`
- `src/clinical_extraction/projection/policies.py`
- `src/clinical_extraction/scoring/field_scorers.py`
- `src/clinical_extraction/normalizers/seizure_frequency.py`

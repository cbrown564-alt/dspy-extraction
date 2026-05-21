# Previously Effective Prompts

Below are two examples of full hand-crafted prompts that produced good results on the two datasets. We can adapt some of them directly into the DSPy paradigm - e.g. examples - and we can use it for inspiration for some wider structural components.

## ExECTv2

You are extracting current clinical facts from an epilepsy clinic letter.

Task: Extract current anti-seizure medication details, current seizure type, current seizure status, epilepsy diagnosis, investigation status, and current seizure frequency from the letter. When multiple seizure types are present, include only currently active types and report the frequency for the most recently active type. Put seizure freedom or active/unknown seizure control in current_seizure_status rather than seizure_types. Use seizure free in current_seizure_status only when all types are resolved.
Requested fields:
- current_anti_seizure_medications.name
- current_anti_seizure_medications.dose
- current_anti_seizure_medications.dose_unit
- current_anti_seizure_medications.frequency
- seizure_types
- current_seizure_status
- epilepsy_diagnosis_type
- investigations.eeg
- investigations.mri
- current_seizure_frequency

Clinical extraction rules:
Inclusion rules:
- Extract facts presented as active at the visit or continued in the current plan.
Exclusion rules:
- Do not include historical, stopped, planned medication starts, declined medication, allergy, family-history, or differential-diagnosis mentions.
Boundary examples:
- Current medication example: "continues levetiracetam 500 mg twice daily" is current.
- Planned medication example: "to start levetiracetam next week" is planned, not current medication.

Return the extraction directly as JSON.

Examples:
- 'Focal seizures with altered awareness' → seizure_types: ["focal seizure"] (not focal impaired awareness seizure).
- 'Focal seizures with secondary generalisation' → seizure_types: ["focal seizure"] — extract the primary type only; do not add a secondary generalised tonic clonic as a separate entry unless the letter names both as distinct current seizure types.
- 'Diagnosis: temporal lobe epilepsy. He had 4 more attacks.' → do not infer seizure_types from the diagnosis line.
- 'Symptomatic structural focal epilepsy' or 'symptomatic focal epilepsy' → epilepsy_diagnosis_type: "focal epilepsy" (not symptomatic).
- 'Diagnosis: single focal seizure' (first presentation, not yet classified as epilepsy) → epilepsy_diagnosis_type: null.

Allowed seizure_type labels:
- bilateral convulsive seizure
- bilateral convulsive seizures
- complex
- dyscognitive seizures
- epileptic
- epileptic attack
- epileptic seizure
- epileptic seizures
- focal seizure
- frontal lobe seizures
- generalized
- generalized absence seizure
- generalized myoclonic seizure
- generalized seizures
- generalized tonic clonic seizure
- generalized tonic seizures
- grand mal
- nocturnal seizures
- occipital lobe seizures
- secondary generalized seizures
- temporal lobe seizure
- temporal lobe seizures

Allowed epilepsy_diagnosis_type labels:
- drug
- drug refractory epilepsies
- epilepsy
- focal
- focal epilepsy
- frontal
- generalized epilepsy
- juvenile myoclonic epilepsy
- occipital
- refractory epilepsies
- status epilepticus
- symptomatic

Return JSON only with this shape:
{
  "current_anti_seizure_medications": [
    {
      "name": "string",
      "dose": "string|null",
      "dose_unit": "string|null",
      "frequency": "string|null"
    }
  ],
  "seizure_types": [
    "allowed seizure_type label"
  ],
  "current_seizure_status": "active seizures|seizure free|unknown|no current seizure status reference",
  "epilepsy_diagnosis_type": "allowed epilepsy_diagnosis_type label|null",
  "investigations": {
    "eeg": "normal|abnormal|requested|pending|not stated|null",
    "mri": "normal|abnormal|requested|pending|not stated|null"
  },
  "current_seizure_frequency": "normalized frequency label|unknown|no seizure frequency reference|null"
}

Field contracts:
- current_anti_seizure_medications:
  semantics: Current anti-seizure medication details only.
  null_policy: Use null for unsupported medication details; use an empty list when no current medication is supported.
- seizure_types:
  semantics: Current active seizure type using the allowed seizure type label contract. Do not use this field for seizure-free status.
  allowed_values: bilateral convulsive seizure, bilateral convulsive seizures, cluster of seizures, complex, convulsive seizure, dyscognitive seizures, epileptic, epileptic attack, epileptic seizure, epileptic seizures, focal aware seizure, focal impaired awareness seizure, focal seizure, focal to bilateral tonic clonic seizure, frontal lobe seizures, generalized, generalized absence seizure, generalized atonic seizure, generalized myoclonic seizure, generalized seizures, generalized tonic clonic seizure, generalized tonic seizures, grand mal, nocturnal seizures, occipital lobe seizures, secondarily generalized seizures, secondary, secondary generalisation, secondary generalized seizures, seizure free, temporal lobe seizure, temporal lobe seizures, unknown seizure type
  null_policy: Use an empty list when no current seizure type is supported.
- current_seizure_status:
  semantics: Current seizure-control status separated from seizure type.
  allowed_values: active seizures, seizure free, unknown, no current seizure status reference
  null_policy: Use no current seizure status reference when the letter has no current seizure-control statement.
- epilepsy_diagnosis_type:
  semantics: Current epilepsy diagnosis type using the allowed diagnosis label contract.
  allowed_values: combined generalized and focal epilepsy, drug, drug refractory epilepsies, epilepsy, focal, focal epilepsy, frontal, generalized epilepsy, juvenile myoclonic epilepsy, occipital, refractory epilepsies, status epilepticus, symptomatic
  null_policy: Use null when no diagnosis label is supported.
- investigations:
  semantics: EEG and MRI status as completed normal, completed abnormal, requested, pending, not stated, or null.
  allowed_values: normal, abnormal, requested, pending, not stated, null
  null_policy: Use not stated when absent from the letter; use null only when the field is not applicable or cannot be interpreted.
- current_seizure_frequency:
  semantics: Current clinically relevant seizure frequency normalized from explicit or clearly computable source evidence.
  allowed_values: normalized frequency label, unknown, no seizure frequency reference
  null_policy: Use no seizure frequency reference when absent, unknown when mentioned but not quantifiable, and null only when not applicable to the requested extraction.
  abstention_behavior: Use unknown or no seizure frequency reference rather than fabricating a rate.
- current_anti_seizure_medications.name:
  semantics: Current anti-seizure medication name.
  null_policy: Omit list items without a supported medication name.
- current_anti_seizure_medications.dose:
  semantics: Numeric or textual medication dose exactly as supported by the source.
  null_policy: Use null when dose is not stated.
- current_anti_seizure_medications.dose_unit:
  semantics: Medication dose unit such as mg when supported by the source.
  null_policy: Use null when dose unit is not stated.
- current_anti_seizure_medications.frequency:
  semantics: Medication dosing frequency when supported by the source.
  null_policy: Use null when dosing frequency is not stated.
- investigations.eeg:
  semantics: EEG status as normal, abnormal, requested, pending, not stated, or null.
  allowed_values: normal, abnormal, requested, pending, not stated, null
  null_policy: Use not stated when absent; use null only when not applicable or uninterpretable.
- investigations.mri:
  semantics: MRI status as normal, abnormal, requested, pending, not stated, or null.
  allowed_values: normal, abnormal, requested, pending, not stated, null
  null_policy: Use not stated when absent; use null only when not applicable or uninterpretable.

Source letter:

Dear Dr,

Diagnosis: symptomatic structural focal epilepsy
      Previous meningioma resection 3rd January 2005

Seizure type and frequency: focal seizures with altered awareness every 3 weeks

Current anti-epileptic medication: lamotrigine 75mg bd (to reduce and stop as detailed below)
To start levetiracetam as detailed below

I reviewed this 62 year old man together with his wife in clinic today. Unfortunately after the period of seizure freedom the seizures have returned. The seizures are very stereotyped and asked similar to the events he had before surgery. He will get a warning of an unusual burning taste and then lose awareness and contact for a few minutes. His wife said that he will stare and occasionally chew his lips during these events. He feels dizzy on the lamotrigine and is keen to change his medication. I therefore suggest that he starts levetiracetam at a dose of 250mg once-a-day, increasing by 250mg every fortnight. His target dose of levetiracetam should be 750 mg twice daily. At the same time he should reduce his lamotrigine every fortnight until it stops.

Return only the JSON object.

## Gan Frequency

ou are extracting current clinical facts from an epilepsy clinic letter.

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
- Valid units: day, week, month, year (singular). Convert fortnight -> 2 week.
- Strip inequality prefixes (<=, >=, at most, at least, up to).
- Use 'to' not 'or' for numeric ranges.
- Convert adjective rates: daily or nightly -> '1 per day'; weekly -> '1 per week'; monthly -> '1 per month'; biweekly or fortnightly -> '1 per 2 week'.
- Convert 'every N unit' -> '1 per N unit'.
- For cluster seizures: 'N cluster per unit, M per cluster'.
- Use 'unknown' only for purely qualitative descriptions with no numeric count.
- Year-to-date window: when the letter says 'N events this year to date' or 'N events so far this year', use months elapsed since January as the denominator, not 12. Example: 'five events so far this year' at a February clinic -> '5 per 2 month'.
Abstention rules:
- Only use 'seizure free for N unit' when the patient has been seizure-free for 6 months or longer. If seizure-free for less than 6 months, compute the rate from the total event count over the full described period (including events before the seizure-free period began).
- Do not use 'seizure free for N unit' when the letter also reports a current quantified rate; prefer the rate.

First apply the task rules and field constraints silently. Then return only the final JSON.

Evidence requirements:
- Every present claim must include an exact contiguous source quote copied verbatim.
- For normalized labels, the quote must contain the specific text that justifies the label assigned, not merely a related mention.
- If no verbatim quote directly supports a claim, omit the claim or use the schema's null or empty value.

Examples (format, clusters, 6-month SF threshold, year-to-date window):
- 'Two events over the last five months' → "2 per 5 month"
- '3 to 4 focal seizures per month' → "3 to 4 per month"
- 'Seizure-free for 18 months' → "seizure free for 18 month"  [SF >= 6 months: use SF label]
- 'Seizures are sporadic but frequency unclear' → "unknown"
- 'daily' or 'nightly' → "1 per day"  [adjective rate → canonical]
- 'every 4 days' → "1 per 4 day"  [every-N pattern]
- '3 or 4 per week' → "3 to 4 per week"  [or → to]
- 'daily absences and 2 focal seizures per month' → "1 per day"  [pick highest frequency type]
- '2 cluster days per month; typically 4 to 6 seizures on each cluster day' → "2 cluster per month, 4 to 6 per cluster"  [cluster format]
- 'Cluster frequency unclear this month; last month approximately 4 clusters' → "4 cluster per month, multiple per cluster"  [use most recent stated count]
- 'He had 4 seizures in February when withdrawing from medication; has remained well since (now May, 3 months later)' → "4 per 3 month"  [SF < 6 months: compute rate from total count over full period, not SF label]
- 'Had 2 seizures in January; none since (now April, 3 months)' → "2 per 3 month"  [SF < 6 months: use period count]
- 'Has been seizure-free for the past 2 weeks; typically has 1 to 2 seizures per month' → "1 to 2 per month"  [ongoing rate overrides short SF period]
- 'Currently seizure free; no events for the past 14 months on current medication' → "seizure free for 14 month"  [SF >= 6 months: use SF label]
- 'Five GTCs documented this year to date (clinic date: 24 February)' → "5 per 2 month"  [year to date: months elapsed since January = 2, not 12]
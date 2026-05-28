# Gan S0 Exact-Frequency Residual Slice Error Read

Date: 2026-05-21
Run: `gan_s0_gpt4_1_mini_temporal_candidates_verify_repair_full_validation_guardrails_20260520T130933Z`
Dataset / split: `gan_2026_fixed_v1:validation`
Scorer: `gan_frequency_deterministic_v1`

## Scope

This read queue contains 30 representative records from 104 benchmark-severe monthly-frequency misses.

## Slice Counts

| Group | Count | Selected |
| --- | ---: | ---: |
| `arithmetic_window_precision` | 51 | 10 |
| `cluster_composition` | 12 | 8 |
| `other_benchmark_severe` | 13 | 0 |
| `unknown_vs_quantified` | 18 | 8 |
| `infrequent_long_denominator_or_boundary` | 10 | 4 |

## Read Queue

| Group | record_id | failure_class | gold | predicted | reference | candidates |
| --- | --- | --- | --- | --- | --- | ---: |
| `arithmetic_window_precision` | `gan_12562` | `purist_bin_boundary_within_pragmatic` | `1 per day` | `4 per week` | `1 per day` | 0 |
| `arithmetic_window_precision` | `gan_12667` | `purist_bin_boundary_within_pragmatic` | `1 per day` | `2 per month` | `1 per day` | 0 |
| `arithmetic_window_precision` | `gan_12679` | `purist_bin_boundary_within_pragmatic` | `1 per day` | `1 to 2 per month` | `1 per day` | 0 |
| `arithmetic_window_precision` | `gan_14250` | `purist_bin_boundary_within_pragmatic` | `2 per month` | `2 per week` | `2 per month` | 0 |
| `arithmetic_window_precision` | `gan_14271` | `purist_bin_boundary_within_pragmatic` | `2 to 3 per month` | `2 to 3 per week` | `2 to 3 per month` | 0 |
| `arithmetic_window_precision` | `gan_15923` | `purist_bin_boundary_within_pragmatic` | `8 per 2 month` | `7 per month` | `8 per 2 month` | 0 |
| `arithmetic_window_precision` | `gan_16251` | `purist_bin_boundary_within_pragmatic` | `14 per 4 month` | `7 per month` | `14 per 4 month` | 0 |
| `arithmetic_window_precision` | `gan_16753` | `purist_bin_boundary_within_pragmatic` | `19 per 6 month` | `5 per month` | `19 per 6 month` | 0 |
| `arithmetic_window_precision` | `gan_16947` | `purist_bin_boundary_within_pragmatic` | `2 per week` | `4 per 2 month` | `2 per week` | 0 |
| `arithmetic_window_precision` | `gan_16964` | `purist_bin_boundary_within_pragmatic` | `2 per week` | `4 to 5 per 2 month` | `2 per week` | 0 |
| `unknown_vs_quantified` | `gan_10618` | `cluster_structure_swap` | `unknown, 4 to 6 per cluster` | `1 cluster per day, 4 to 6 per cluster` | `unknown` | 0 |
| `unknown_vs_quantified` | `gan_10751` | `unknown_as_high_rate` | `unknown` | `1 cluster per week, multiple per cluster` | `unknown` | 0 |
| `unknown_vs_quantified` | `gan_13993` | `unknown_as_high_rate` | `unknown` | `2 to 3 per month` | `unknown` | 0 |
| `unknown_vs_quantified` | `gan_14025` | `unknown_as_high_rate` | `unknown` | `2 per 6 week` | `unknown` | 0 |
| `unknown_vs_quantified` | `gan_14036` | `unknown_as_high_rate` | `unknown` | `4 per month` | `unknown` | 0 |
| `unknown_vs_quantified` | `gan_14081` | `unknown_as_high_rate` | `unknown` | `2 to 3 per month` | `unknown` | 0 |
| `unknown_vs_quantified` | `gan_14092` | `unknown_as_high_rate` | `unknown` | `5 per 2 month` | `unknown` | 0 |
| `unknown_vs_quantified` | `gan_14137` | `unknown_as_high_rate` | `unknown` | `3 to 4 per 3 month` | `unknown` | 0 |
| `cluster_composition` | `gan_10031` | `cluster_collapsed_to_rate` | `1 cluster per week, multiple per cluster` | `unknown` | `1 cluster per week, multiple per cluster` | 0 |
| `cluster_composition` | `gan_10434` | `cluster_collapsed_to_rate` | `multiple cluster per week, 2 to 3 per cluster` | `unknown` | `unknown` | 0 |
| `cluster_composition` | `gan_10673` | `cluster_collapsed_to_rate` | `1 cluster per month, multiple per cluster` | `unknown` | `1 cluster per month, multiple per cluster` | 0 |
| `cluster_composition` | `gan_15240` | `cluster_collapsed_to_rate` | `multiple cluster per 12 month, multiple per cluster` | `unknown` | `multiple cluster per 12 month, multiple per cluster` | 0 |
| `cluster_composition` | `gan_15255` | `cluster_semantic_mismatch` | `multiple cluster per 15 month, multiple per cluster` | `1 cluster per week, multiple per cluster` | `multiple cluster per 15 month, multiple per cluster` | 0 |
| `cluster_composition` | `gan_15404` | `cluster_semantic_mismatch` | `1 cluster per 4 month, 3 to 4 per cluster` | `1 cluster per day, 3 to 4 per cluster` | `1 cluster per 4 month, 3 to 4 per cluster` | 0 |
| `cluster_composition` | `gan_10984` | `cluster_semantic_mismatch` | `3 cluster per month, 3 to 4 per cluster` | `1 cluster per month, 3 to 4 per cluster` | `3 cluster per month, 3 to 4 per cluster` | 0 |
| `cluster_composition` | `gan_10993` | `cluster_semantic_mismatch` | `2 cluster per month, 2 to 4 per cluster` | `1 cluster per month, 2 to 4 per cluster` | `2 cluster per month, 2 to 4 per cluster` | 0 |
| `infrequent_long_denominator_or_boundary` | `gan_13290` | `frequent_overcalled` | `4 per 6 month` | `2 per 3 week` | `4 per 6 month` | 0 |
| `infrequent_long_denominator_or_boundary` | `gan_14354` | `frequent_overcalled` | `2 to 4 per 3 month` | `2 to 4 per month` | `2 to 4 per 3 month` | 0 |
| `infrequent_long_denominator_or_boundary` | `gan_15302` | `frequent_overcalled` | `1 to 2 per 14 month` | `1 to 2 per month` | `1 to 2 per 14 month` | 0 |
| `infrequent_long_denominator_or_boundary` | `gan_15306` | `frequent_overcalled` | `2 to 3 per 15 month` | `1 to 3 per month` | `2 to 3 per 15 month` | 1 |

## Record Notes

### 1. `gan_12562` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `1 per day` (30.0/month, `frequent`, `gte_1_per_day`)
- Predicted: `4 per week` (17.32/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Reference: `1 per day`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
He also has daily drop attacks.
```

**Predicted Evidence**

```text
he continues to have up to 3 or 4 generalised tonic-clonic seizures per week
```

**Verifier Reason**

```text
Initial label matches the note text exactly and no temporal candidates suggest a better label.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
ry to track any temporal associations with events. They remain vigilant about maintaining hydration and sleep where possible during these periods.

Seizure frequency remains unchanged over the last six months; he continues to have up to 3 or 4 generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures with disorientation are reported every four to six weeks. No events have occurred since his most recent review. His mother feels the recent quiet spell coincided with stricter adherence to evening routines during the non-fasting days; they plan to continue the seizure diary to clarify patterns.

There

---

ily report that religious fasting periods may alter routine, particularly morning and evening dosing times, and they have been keeping a diary to track any temporal associations with events. They remain vigilant about maintaining hydration and sleep where possible during these periods.

Seizure frequency remains unchanged over the last six months; he continues to have up to 3 or 4 generalised tonic-clonic seizures per week, rarely achieving more than ten consecutive seizure-free days. He also has daily drop attacks. Furthermore, focal impaired-awareness seizures with disorientation are reported every four to six weeks. No events have occurred since his most recent review. His mother feels the recent quiet spell coincided with stricter adherence to evening routines d
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 2. `gan_12667` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `1 per day` (30.0/month, `frequent`, `gte_1_per_day`)
- Predicted: `2 per month` (2.0/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `1 per day`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
He has daily absences.
```

**Predicted Evidence**

```text
he continues to suffer one to two generalised tonic-clonic seizures per month
```

**Verifier Reason**

```text
The initial label "2 per month" matches the note text exactly: "he continues to suffer one to two generalised tonic-clonic seizures per month." No temporal candidates were extracted, but the initial evidence is a direct quote supporting the label.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
ive to light-trigger avoidance at work (he has adjusted monitor refresh settings and brightness) and avoids venues with strobe lighting. Seizure frequency has not altered significantly over the past six months; he continues to suffer one to two generalised tonic-clonic seizures per month, with a longest seizure-free interval of around three weeks. He has daily absences. In addition, he experiences focal clonic with disorientation every three to four weeks, together with drop attacks. Since the last clinic visit, no further seizures have been reported. He attributes this to stricter trigger avoidance and better sleep routine, though he accepts this may be coincidental; we will continue to monitor.

Yours sincerely

---

me
- Review in six months, earlier if seizure pattern changes or adverse effects emerge

Since his last appointment he reports being attentive to light-trigger avoidance at work (he has adjusted monitor refresh settings and brightness) and avoids venues with strobe lighting. Seizure frequency has not altered significantly over the past six months; he continues to suffer one to two generalised tonic-clonic seizures per month, with a longest seizure-free interval of around three weeks. He has daily absences. In addition, he experiences focal clonic with disorientation every three to four weeks, together with drop attacks. Since the last clinic visit, no further seizures have been reported. He attributes this to stricter trigger avoidance and better sleep routine, thoug
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 3. `gan_12679` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `1 per day` (30.0/month, `frequent`, `gte_1_per_day`)
- Predicted: `1 to 2 per month` (1.5/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `1 per day`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
He has daily absences.
```

**Predicted Evidence**

```text
he continues to suffer one to two generalised tonic-clonic seizures per month
```

**Verifier Reason**

```text
Confirm-first guard preserved initial label '"1 to 2 per month"' instead of verifier confirm to '1 to 2 per month'.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
episodes. Occupational disruption has increased, with missed deadlines and reduced capacity to commute independently.

Seizure summary: Seizure frequency has not altered significantly over the past six months; he continues to suffer one to two generalised tonic-clonic seizures per month, with a longest seizure-free interval of around three weeks. He has daily absences. In addition, he experiences focal non-motor with disorientation every three to four weeks, together with drop attacks. Since the last clinic visit, no further seizures have been reported. In the context of the above, although headline frequency is unchanged, he perceives deterioration due to greater seizure clustering around stress points, longer

---

near-falls at home, with one witnessed minor head knock without loss of consciousness, and escalating anxiety regarding unpredictability of episodes. Occupational disruption has increased, with missed deadlines and reduced capacity to commute independently.

Seizure summary: Seizure frequency has not altered significantly over the past six months; he continues to suffer one to two generalised tonic-clonic seizures per month, with a longest seizure-free interval of around three weeks. He has daily absences. In addition, he experiences focal non-motor with disorientation every three to four weeks, together with drop attacks. Since the last clinic visit, no further seizures have been reported. In the context of the above, although headline frequency is unchanged, he per
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 4. `gan_14250` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `2 per month` (2.0/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Predicted: `2 per week` (8.66/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Reference: `2 per month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
In the following week, he had 2 seizures, one associated with sleep deprivation. No further seizures have occurred since.
```

**Predicted Evidence**

```text
In the following week, he had 2 seizures
```

**Verifier Reason**

```text
The initial label "2 per week" matches the note text "In the following week, he had 2 seizures" exactly and is supported by the note; no candidates extracted but initial label is valid and supported.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
y. Since our last contact he has engaged with dietetic services and has been following ketogenic-style dietary guidance under supervision. He reports improved energy stability during the day and better sleep hygiene, and his family have noticed a clearer pattern to his triggers and improved overall wellbeing. 

He came off Levetiracetam on 03-Mar. In the following week, he had 2 seizures, one associated with sleep deprivation. No further seizures have occurred since. He feels steadier in himself and has not required any emergency attendance. 

Current anti-seizure therapy has otherwise remained unchanged, and he has tolerated the regimen without new adverse effects. He reports no rashes, no mood deterioration, and only mild intermittent fatigue that has improved since optimising his diet and sleep routine. He

---

y. Since our last contact he has engaged with dietetic services and has been following ketogenic-style dietary guidance under supervision. He reports improved energy stability during the day and better sleep hygiene, and his family have noticed a clearer pattern to his triggers and improved overall wellbeing. 

He came off Levetiracetam on 03-Mar. In the following week, he had 2 seizures, one associated with sleep deprivation. No further seizures have occurred since. He feels steadier in himself and has not required any emergency attendance. 

Current anti-seizure therapy has otherwise remained unchanged, and he has tolerated the regimen without new adverse effects. He reports no rashes, no mood deterioration, and only mild interm
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 5. `gan_14271` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `2 to 3 per month` (2.5/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Predicted: `2 to 3 per week` (10.825/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Reference: `2 to 3 per month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
In the following week, he had 2 - 3 seizures, one associated with sleep deprivation. No further seizures have occurred since.
```

**Predicted Evidence**

```text
In the following week, he had 2 - 3 seizures, one associated with sleep deprivation.
```

**Verifier Reason**

```text
The initial label and evidence accurately reflect the note's statement about seizure frequency in the week following medication cessation.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
cally as a potential alternative but never initiated. No other antiseizure therapies currently prescribed. 

Blood Tests/Drug Levels: None indicated presently as not on a maintenance antiseizure therapy. Routine safety bloods with GP last month reportedly within normal limits (patient-reported). 

Seizures: He came off Levetiracetam on 10 January. In the following week, he had 2 - 3 seizures, one associated with sleep deprivation. No further seizures have occurred since. He denies injuries or prolonged post-ictal confusion. Partner reports brief loss of awareness with tonic stiffening and tongue bite on one occasion; recovery within 15 minutes. No auras described. 

Background: History of childhood febrile seizures noted; no neurological sequelae. Family history negative for epilepsy. No history of significant hea

---

cally as a potential alternative but never initiated. No other antiseizure therapies currently prescribed. 

Blood Tests/Drug Levels: None indicated presently as not on a maintenance antiseizure therapy. Routine safety bloods with GP last month reportedly within normal limits (patient-reported). 

Seizures: He came off Levetiracetam on 10 January. In the following week, he had 2 - 3 seizures, one associated with sleep deprivation. No further seizures have occurred since. He denies injuries or prolonged post-ictal confusion. Partner reports brief loss of awareness with tonic stiffening and tongue bite on one occasion; recovery within 15 minutes. No auras described. 

Background: History of childhood febrile seizures noted; no neurological sequelae. Family history negative fo
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 6. `gan_15923` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `8 per 2 month` (4.0/month, `frequent`, `eq_1_per_week`)
- Predicted: `7 per month` (7.0/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Reference: `8 per 2 month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
In Oct she had no nocturnal seizures but 2 daytime events. In Nov she had a nocturnal seizure and 5 while awake.
```

**Predicted Evidence**

```text
In Oct she had no nocturnal seizures but 2 daytime events. In Nov she had a nocturnal seizure and 5 while awake.
```

**Verifier Reason**

```text
The initial label "7 per month" is directly supported by the note text specifying 2 daytime events in October and 6 events (1 nocturnal + 5 awake) in November, consistent with the initial evidence. No temporal candidates were extracted to suggest a better label.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
l No: KCH482917 NHS No. 9432081675  
12 Brookside Close, London, SE15 2AB

Thank you for asking me to review this patient in the neurology clinic. She attended with her partner, who helped provide the history. They describe a clear deterioration over the past two months with limited benefit from the prior medication regimen despite good adherence. In Oct she had no nocturnal seizures but 2 daytime events. In Nov she had a nocturnal seizure and 5 while awake. The daytime episodes were reported as sudden behavioural arrest with loss of awareness, brief right-hand clenching, and a confused, irritable recovery lasting 20–30 minutes. The nocturnal event was witnessed as a cry, stiffening, and subsequent heavy breathing with bite to the lateral tongue and marked fatigue the following day.

Intercurrently, s
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 7. `gan_16251` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `14 per 4 month` (3.5/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Predicted: `7 per month` (7.0/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Reference: `14 per 4 month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
She had 7 convulsions so far in Sep, 4 in Aug, 2 in Jul, one in Jun
```

**Predicted Evidence**

```text
She had 7 convulsions so far in Sep, 4 in Aug, 2 in Jul, one in Jun
```

**Verifier Reason**

```text
Confirm-first guard preserved initial label '"7 per month"' instead of verifier confirm to '7 per month'.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
don NW3 1TJ  

Epilepsy 

Medication: Patient reports current use of sodium valproate 500 mg twice daily since May 2014. She also takes folic acid 5 mg once daily. No other regular antiepileptic medication. 

Valproate Blood Level: 

15 September 2014: 58 mg/L (local reference 50–100 mg/L). Dose at time of sampling: 500 mg twice daily. 

Seizures: She had 7 convulsions so far in Sep, 4 in Aug, 2 in Jul, one in Jun both from being awake and asleep. She describes brief confusion afterwards lasting 10–20 minutes, with muscle soreness the following day. No tongue-biting recalled; occasional urinary incontinence has been reported. No consistent prodrome or warning noted. Triggers are uncertain; she wonders if poor sleep and alcohol the night before may have cont
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 8. `gan_16753` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `19 per 6 month` (3.1666666666666665/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Predicted: `5 per month` (5.0/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Reference: `19 per 6 month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
In May he had 3 short seizures in a brief series. In Aug 7 daytime events were noted, in Sep four myoclonic jerks occurred, and in Oct five generalised tonic-clonic seizures at the centre (staff-witnessed).
```

**Predicted Evidence**

```text
In May he had 3 short seizures in a brief series. In Aug 7 daytime events were noted, in Sep four myoclonic jerks occurred, and in Oct five generalised tonic-clonic seizures at the centre (staff-witnessed).
```

**Verifier Reason**

```text
Confirm-first guard preserved initial label '"5 per month"' instead of verifier confirm to '5 per month'.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
ests a possible cyclical influence on seizure occurrence, with several clusters aligning with the late luteal phase according to the app’s logged cycles. She does not identify a consistent aura, and recovery times vary from minutes to an hour depending on the event.

To summarise the recent pattern from her diary and the centre’s incident reports: In May he had 3 short seizures in a brief series. In Aug 7 daytime events were noted, in Sep four myoclonic jerks occurred, and in Oct five generalised tonic-clonic seizures at the centre (staff-witnessed). The patient and partner note that the May and August clusters coincided with days −3 to +2 around menses on the app logs, while September was peri-ovulatory by their record, and October overlapped with the late luteal phase again. There is no clear precipitant beyond possible hormonal timing, though poor sleep was recorded before two of the Octobe
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 9. `gan_16947` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `2 per week` (8.66/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Predicted: `4 per 2 month` (2.0/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `2 per week`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
Absence seizures remain infrequent, usually no more than twice weekly
```

**Predicted Evidence**

```text
She experiences four generalised tonic-clonic seizures every 2 months.
```

**Verifier Reason**

```text
The initial label matches the exact quoted seizure frequency in the note text; no candidate corrections are available.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
ackground and Current Status: 

I reviewed Ms Hannah Keane in clinic today accompanied by her primary carer, who reports increasing fatigue related to caregiving responsibilities, particularly overnight supervision. Over the past year seizure control has been relatively stable. She experiences four generalised tonic-clonic seizures every 2 months. Absence seizures remain infrequent, usually no more than twice weekly, and myoclonic jerks are reported only occasionally in the mornings. From a focal epilepsy perspective, her semiology remains consistent with focal onset seizures with preserved awareness progressing on occasion to behavioural arrest; there has been no new aura evolution. There have been no injuries, status episodes, or emergency attendances. Medi

---

rlier if escalation in frequency, injury, or medication intolerance.

Background and Current Status: 

I reviewed Ms Hannah Keane in clinic today accompanied by her primary carer, who reports increasing fatigue related to caregiving responsibilities, particularly overnight supervision. Over the past year seizure control has been relatively stable. She experiences four generalised tonic-clonic seizures every 2 months. Absence seizures remain infrequent, usually no more than twice weekly, and myoclonic jerks are reported only occasionally in the mornings. From a focal epilepsy perspective, her semiology remains consistent with focal onset seizures with preserved awareness progressing on occasion to behavioural arrest; there has been no new aura evolution. There
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 10. `gan_16964` — `arithmetic_window_precision`

- Failure: `purist_bin_boundary_within_pragmatic` / pattern `0001`
- Gold: `2 per week` (8.66/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Predicted: `4 to 5 per 2 month` (2.25/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `2 per week`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
Absence seizures remain infrequent, usually no more than twice weekly
```

**Predicted Evidence**

```text
She experiences 4 to 5 generalised tonic-clonic seizures every 2 months
```

**Verifier Reason**

```text
The initial label matches the exact phrase in the note text describing seizure frequency; no candidates extracted but initial prediction is precise and supported.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
W10 5LR 

Medication: 

Sodium valproate (Epilim) 500 mg morning and 1000 mg evening. Clobazam 10 mg at night as needed for clusters.

I reviewed Sophie Williams in clinic today regarding her generalised epilepsy. Over the past year seizure control has been relatively stable. She experiences 4 to 5 generalised tonic-clonic seizures every 2 months. Absence seizures remain infrequent, usually no more than twice weekly, and myoclonic jerks are reported only occasionally in the mornings. She keeps a detailed seizure diary, which aligns with collateral accounts from her partner. There have been no emergency admissions, tongue bites are occasional, and post-ictal confusion typically lasts 20–30 minutes.

She reports good adherence to medication with no missed doses

---

-1992, Hospital No: N841205 NHS No. 5839201746  
12 Beech Grove, London, W10 5LR 

Medication: 

Sodium valproate (Epilim) 500 mg morning and 1000 mg evening. Clobazam 10 mg at night as needed for clusters.

I reviewed Sophie Williams in clinic today regarding her generalised epilepsy. Over the past year seizure control has been relatively stable. She experiences 4 to 5 generalised tonic-clonic seizures every 2 months. Absence seizures remain infrequent, usually no more than twice weekly, and myoclonic jerks are reported only occasionally in the mornings. She keeps a detailed seizure diary, which aligns with collateral accounts from her partner. There have been no emergency admissions, tongue bites are occasional, and post-ictal confusion typically lasts 20–30
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 11. `gan_10618` — `unknown_vs_quantified`

- Failure: `cluster_structure_swap` / pattern `0000`
- Gold: `unknown, 4 to 6 per cluster` (1000.0/month, `unknown`, `unknown`)
- Predicted: `1 cluster per day, 4 to 6 per cluster` (150.0/month, `frequent`, `gte_1_per_day`)
- Reference: `unknown`; hard case: `True`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
typically around four to six short spells grouped together on days when they occur
```

**Predicted Evidence**

```text
episodes tend to come in small runs: typically around four to six short spells grouped together on days when they occur
```

**Verifier Reason**

```text
The initial label matches the note text exactly and accurately reflects the described seizure frequency and clustering pattern.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
of awareness for 10–20 seconds, sometimes followed by a short period of confusion. There are no consistent focal auras reported. Injuries have not occurred. Family have witnessed two events and noted blank staring with unresponsiveness, without clear limb jerking. 

Regarding frequency, the patient reports that episodes tend to come in small runs: typically around four to six short spells grouped together on days when they occur, most commonly later in the day towards the evening period. There may then be several days without events. Sleep disruption and higher anxiety levels appear to precede these clusters, and caffeine excess may contribute. Alcohol intake is modest and there is no recreational drug use. 

Past medical history is notable for longstanding anxiety with i

---

en sense of "switching off" and loss of awareness for 10–20 seconds, sometimes followed by a short period of confusion. There are no consistent focal auras reported. Injuries have not occurred. Family have witnessed two events and noted blank staring with unresponsiveness, without clear limb jerking. 

Regarding frequency, the patient reports that episodes tend to come in small runs: typically around four to six short spells grouped together on days when they occur, most commonly later in the day towards the evening period. There may then be several days without events. Sleep disruption and higher anxiety levels appear to precede these clusters, and caffeine excess may contribute. Alcohol intake is modest and there is no recreational drug use. 

Past medical history is notable for longstanding anxiety with i
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 12. `gan_10751` — `unknown_vs_quantified`

- Failure: `unknown_as_high_rate` / pattern `0000`
- Gold: `unknown` (1000.0/month, `unknown`, `unknown`)
- Predicted: `1 cluster per week, multiple per cluster` (12.99/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Reference: `unknown`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
Episodes remain infrequent at home (none in the last 4 months) but he describes short bursts occurring around long-distance travel across multiple time zones
```

**Predicted Evidence**

```text
he
```

**Verifier Reason**

```text
Initial label matches the note's description of seizure clustering around travel schedule changes; no temporal candidates to suggest repair.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
es: Patient has focal epilepsy with focal aware sensory onset evolving to impaired awareness on some occasions. He reports brief epigastric rising and metallic taste as typical auras, sometimes followed by behavioural arrest lasting 30–60 seconds, with occasional right-hand automatisms. No generalised tonic-clonic events since May 2024. 

Pattern: Episodes remain infrequent at home (none in the last 4 months) but he describes short bursts occurring around long-distance travel across multiple time zones, particularly when sleep schedule is disrupted and he is dehydrated. He notes these "time-shift flurries" tend to appear within 24–48 hours after overnight flights and then settle as his sleep normalises. High caffeine intake acknowledged; he reports consuming 5–7 strong coffees per day during travel periods, occasionally adding energy drinks (Ã‚Â

---

James Patel, DOB: 22-11-1989, Hospital No: H4739201 NHS No. 9842156703  
44 St Alban’s Road, London, N1 4QJ  

Focal Epilepsy 

Medication: Lamotrigine ongoing since March 2024; Levetiracetam introduced August 2025 

Current regimen:  
- Lamotrigine 100 mg twice daily (film‑coated)  
- Levetiracetam 500 mg twice daily  

Therapeutic Drug Monitoring:  
- Lamotrigine level (17 September 2025): 3.2 mg/L (reference 1.0–15.0 mg/L)  
- Levetiracetam level not indicated; clinical response under review  

Seizures: Patient has focal epilepsy with focal aware sensory onset evolving to impaired awareness on some occasions. He reports brief epigastric rising and metallic taste a
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 13. `gan_13993` — `unknown_vs_quantified`

- Failure: `unknown_as_high_rate` / pattern `0000`
- Gold: `unknown` (1000.0/month, `unknown`, `unknown`)
- Predicted: `2 to 3 per month` (2.5/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `unknown`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
since discharge from hospital he has experienced two - three seizures
```

**Predicted Evidence**

```text
since discharge from hospital he has experienced two - three seizures, the last one being on 22-Oct
```

**Verifier Reason**

```text
The initial label "2 to 3 per month" matches the note text exactly and is supported by the evidence quote. No temporal candidates were extracted, so the initial prediction is confirmed.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
NHS No. 2478913650  
18 Willow Crescent, London, SE15 2QR

Thank you for asking me to review your patient following his recent discharge. He attended today with his wife. He described a steady routine since returning home and reports that he commutes mainly by bicycle, which he finds helpful for structure and general wellbeing. 

He explained that since discharge from hospital he has experienced two - three seizures, the last one being on 22-Oct. He is keeping a brief diary and notes that the events are typically followed by a variable recovery period with fatigue and reduced concentration for the rest of the day. There has been no clear precipitating factor identified by him. Night-time events have not been observed by his wife recently, and there has been n

---

NHS No. 2478913650  
18 Willow Crescent, London, SE15 2QR

Thank you for asking me to review your patient following his recent discharge. He attended today with his wife. He described a steady routine since returning home and reports that he commutes mainly by bicycle, which he finds helpful for structure and general wellbeing. 

He explained that since discharge from hospital he has experienced two - three seizures, the last one being on 22-Oct. He is keeping a brief diary and notes that the events are typically followed by a variable recovery period with fatigue and reduced concentration for the rest of the day. There has been no clear precipitating factor identified by him. Night-time events have not been observed by his wife recently, and there has been no associated injury reported.
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 14. `gan_14025` — `unknown_vs_quantified`

- Failure: `unknown_as_high_rate` / pattern `0000`
- Gold: `unknown` (1000.0/month, `unknown`, `unknown`)
- Predicted: `2 per 6 week` (1.4433333333333334/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `unknown`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
since starting ketogenic diet he has had two drop attacks, the latest one on 10-Jan
```

**Predicted Evidence**

```text
since starting ketogenic diet he has had two drop attacks, the latest one on 10-Jan
```

**Verifier Reason**

```text
Initial label matches the note text exactly and is supported by the evidence quote; no temporal candidates to suggest repair.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
nt illness, no new head injuries, and sleep has been more regular with a set bedtime. Appetite is stable and weight unchanged.

Epilepsy details: He has generalised epilepsy with prior history of drop attacks and brief absence episodes. The family report he commenced a ketogenic diet under dietetic supervision six weeks ago. The parents state that since starting ketogenic diet he has had two drop attacks, the latest one on 10-Jan. They have not observed prolonged confusion afterwards, and there has been no rescue medication use. No clear triggers identified beyond occasional sleep deprivation. There have been no generalised tonic–clonic seizures reported since starting dietary therapy.

Examination: Alert and cooperative, mild cognitive slowing but oriented to person and p
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 15. `gan_14036` — `unknown_vs_quantified`

- Failure: `unknown_as_high_rate` / pattern `0000`
- Gold: `unknown` (1000.0/month, `unknown`, `unknown`)
- Predicted: `4 per month` (4.0/month, `frequent`, `eq_1_per_week`)
- Reference: `unknown`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
since starting ketogenic diet he has had 4 drop attacks, the latest one on 17 Dec
```

**Predicted Evidence**

```text
since starting ketogenic diet he has had 4 drop attacks, the latest one on 17 Dec
```

**Verifier Reason**

```text
The initial label "4 per month" matches the note text exactly: "since starting ketogenic diet he has had 4 drop attacks," which supports the frequency. No temporal candidates were extracted, but the initial evidence is a direct quote from the note.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
N TRUST)
Subject: Review and medication adjustment

Hi Emily

Epilepsy Diagnosis:

Diagnosis remains under review with ongoing characterisation. No definitive electroclinical classification assigned at present.

Present Medication:

1. Sodium valproate 300 mg twice daily
2. Clobazam 5 mg at night

Present Seizure Frequency:

The parents state that since starting ketogenic diet he has had 4 drop attacks, the latest one on 17 Dec. They report no clear precipitating triggers; sleep is variable due to the family currently awaiting relocation from temporary accommodation, with crowded living conditions noted and frequent nocturnal disturbances.

Plan of Action:

- Continue ketogenic diet with dietician oversight; parents to maintain seizure and dietary logs and report any con
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 16. `gan_14081` — `unknown_vs_quantified`

- Failure: `unknown_as_high_rate` / pattern `0000`
- Gold: `unknown` (1000.0/month, `unknown`, `unknown`)
- Predicted: `2 to 3 per month` (2.5/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `unknown`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
she has had 2 - 3 myoclonic jerks, the last reported on 24 August
```

**Predicted Evidence**

```text
she has had 2 - 3 myoclonic jerks, the last reported on 24 August
```

**Verifier Reason**

```text
Initial label matches the note text exactly and is supported by the evidence quote; no temporal candidates to contradict or improve the label.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
ported adherence >95%)
- Clobazam 10 mg at night taken intermittently for clusters (none required in the last 6 weeks)

Therapeutic Monitoring:
- Levetiracetam trough level (ED draw) 11 July 2024: 17 mg/L (laboratory reference 12–46 mg/L). Dose at time of sampling: 1000 mg twice daily

Seizures:
- She told me that since her last clinic appointment she has had 2 - 3 myoclonic jerks, the last reported on 24 August. These were brief, morning events without loss of awareness, no injury, and no progression to generalised tonic–clonic seizure. No auras or focal features described.

History Since Last Review:
- Multiple recent ED triage records exist; nursing documentation summarised where relevant. On 11 July she attended for transient palpitations and light-he
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 17. `gan_14092` — `unknown_vs_quantified`

- Failure: `unknown_as_high_rate` / pattern `0000`
- Gold: `unknown` (1000.0/month, `unknown`, `unknown`)
- Predicted: `5 per 2 month` (2.5/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `unknown`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
she has had 5 myoclonic jerks, the last reported on 7 April
```

**Predicted Evidence**

```text
she has had 5 myoclonic jerks, the last reported on 7 April
```

**Verifier Reason**

```text
The initial label "5 per 2 month" is supported by the note text "she has had 5 myoclonic jerks, the last reported on 7 April" indicating 5 events since the last review, which is consistent with a roughly 2-month period; no temporal candidates contradict this.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
vening doses. She has linked her smartphone alarm schedule to bedside and kitchen NFC tags, and reports that the act of tapping the device to the tag has helped her confirm dose administration and avoid duplicate dosing. She brought her adherence log, which corresponds with pharmacy refill dates.

She told me that since her last clinic appointment she has had 5 myoclonic jerks, the last reported on 7 April. These were brief, occurred in the early morning within 30 minutes of waking, and did not lead to loss of awareness or falls. There have been no tonic–clonic events, no emergency department attendances, and no use of rescue medication. She denies new triggers, though notes that two events followed nights of reduced sleep and one followed a missed
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 18. `gan_14137` — `unknown_vs_quantified`

- Failure: `unknown_as_high_rate` / pattern `0000`
- Gold: `unknown` (1000.0/month, `unknown`, `unknown`)
- Predicted: `3 to 4 per 3 month` (1.1666666666666667/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `unknown`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
he has had 3 - 4 generalised tonic-clonic seizures, the most recent on 23 December
```

**Predicted Evidence**

```text
since beginning Clobazam he has had 3 - 4 generalised tonic-clonic seizures, the most recent on 23 December
```

**Verifier Reason**

```text
Initial label matches the note text exactly and no temporal candidates extracted to suggest a better label.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
etiology: 

No structural lesion identified on prior imaging; workup ongoing 

Other Medical Problems: 

Mild asthma on salbutamol as required; seasonal allergic rhinitis managed with cetirizine 

Management Plan: 

- Deterioration noted with emergence of a new event phenotype and increased convulsive burden. He noted that since beginning Clobazam he has had 3 - 4 generalised tonic-clonic seizures, the most recent on 23 December. We will obtain urgent antiseizure medication levels (where applicable), arrange repeat EEG with sleep deprivation, and bring forward MRI brain with epilepsy protocol. 
- Rationalise treatment: continue current Clobazam dose for now pending review, but we discussed that changes may be required; he will keep a detailed seizure diary and provide cor

---

ation not established 

Aetiology: 

No structural lesion identified on prior imaging; workup ongoing 

Other Medical Problems: 

Mild asthma on salbutamol as required; seasonal allergic rhinitis managed with cetirizine 

Management Plan: 

- Deterioration noted with emergence of a new event phenotype and increased convulsive burden. He noted that since beginning Clobazam he has had 3 - 4 generalised tonic-clonic seizures, the most recent on 23 December. We will obtain urgent antiseizure medication levels (where applicable), arrange repeat EEG with sleep deprivation, and bring forward MRI brain with epilepsy protocol. 
- Rationalise treatment: continue current Clobazam dose for now pending review, but we discussed that changes may be required; he will keep a detailed seizure diary and provide cor
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 19. `gan_10031` — `cluster_composition`

- Failure: `cluster_collapsed_to_rate` / pattern `0000`
- Gold: `1 cluster per week, multiple per cluster` (12.99/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Predicted: `unknown` (1000.0/month, `unknown`, `unknown`)
- Reference: `1 cluster per week, multiple per cluster`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
Since mid-August 2025, the patient describes short-lived spells shortly after waking on some weeks, occurring as grouped events on those mornings; the exact count within each grouping has not been recorded
```

**Predicted Evidence**

```text
Since mid-August 2025, the patient describes short-lived spells shortly after waking on some weeks, occurring as grouped events on those mornings; the exact count within each grouping has not been recorded by the patient or witnesses.
```

**Verifier Reason**

```text
Initial label is unknown and no temporal frequency candidates were extracted from the note to support a repair; the note describes grouped events without exact counts or frequency, so unknown is appropriate.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
or episodes of transient loss of awareness

Medication:
- Levetiracetam 500 mg in the evening for 7 days, then 500 mg twice daily from 15 September 2025
- No reported adverse effects other than mild fatigue in the first week, now settled

Therapeutic Levels:
- No antiepileptic drug levels indicated or checked

Seizure history and current status:
- Since mid-August 2025, the patient describes short-lived spells shortly after waking on some weeks, occurring as grouped events on those mornings; the exact count within each grouping has not been recorded by the patient or witnesses. These have not led to injuries or emergency presentations.
- No clear prodrome reported; partner has occasionally noticed brief pauses and unresponsiveness lasting under one minute, with quick recovery.
- No nocturnal tongue biting or incontinence reported. Sleep deprivation and missed meals appear to precipitate episo

---

or episodes of transient loss of awareness

Medication:
- Levetiracetam 500 mg in the evening for 7 days, then 500 mg twice daily from 15 September 2025
- No reported adverse effects other than mild fatigue in the first week, now settled

Therapeutic Levels:
- No antiepileptic drug levels indicated or checked

Seizure history and current status:
- Since mid-August 2025, the patient describes short-lived spells shortly after waking on some weeks, occurring as grouped events on those mornings; the exact count within each grouping has not been recorded by the patient or witnesses. These have not led to injuries or emergency presentations.
- No clear prodrome reported; partner has occasionally noticed brief pauses and unresponsiveness lasting under one minute, with quick recovery.
- No nocturnal tongue biting or incontinence reported. Sleep deprivation and missed meals appear to precipitate episodes per patient account.

Cli
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 20. `gan_10434` — `cluster_composition`

- Failure: `cluster_collapsed_to_rate` / pattern `0000`
- Gold: `multiple cluster per week, 2 to 3 per cluster` (32.475/month, `frequent`, `gte_1_per_day`)
- Predicted: `unknown` (1000.0/month, `unknown`, `unknown`)
- Reference: `unknown`; hard case: `True`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
occurring on several mornings each week despite taking his tablets as prescribed. He describes these as short spells of disorientation with a metallic taste and a need to pause for 30–60 seconds, without loss of awareness, sometimes repeating two or three times within the same morning.
```

**Predicted Evidence**

```text
brief episodes are tending to bunch together after he wakes, occurring on several mornings each week
```

**Verifier Reason**

```text
Initial label is unknown and no deterministic temporal frequency candidates were extracted from the note to support a repair; the initial evidence accurately reflects the note's description of seizure frequency.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
1 g twice daily. He reports good adherence and tolerates this without notable side effects. 

Since his last review, he continues working in metal fabrication and welding. He uses an auto-darkening visor and follows workplace safety protocols. Over the past six weeks he has noticed that brief episodes are tending to bunch together after he wakes, occurring on several mornings each week despite taking his tablets as prescribed. He describes these as short spells of disorientation with a metallic taste and a need to pause for 30–60 seconds, without loss of awareness, sometimes repeating two or three times within the same morning. He has not had any injuries or prolonged events. There is no clear association with missed doses, alcohol, illness, or sleep deprivation. He wonders whether intermittent exposure to arc light is relevant; he keeps the visor down consistently but occasionally steps into the welding bay where others are working. 

We discussed practical measures aro

---

9 Forge Court, London, SE16 2LP 

Medication: 

Levetiracetam 1 g twice daily. He reports good adherence and tolerates this without notable side effects. 

Since his last review, he continues working in metal fabrication and welding. He uses an auto-darkening visor and follows workplace safety protocols. Over the past six weeks he has noticed that brief episodes are tending to bunch together after he wakes, occurring on several mornings each week despite taking his tablets as prescribed. He describes these as short spells of disorientation with a metallic taste and a need to pause for 30–60 seconds, without loss of awareness, sometimes repeating two or three times within the same morning. He has not had any injuries or prolonged events. There is no clear association with missed doses, alco
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 21. `gan_10673` — `cluster_composition`

- Failure: `cluster_collapsed_to_rate` / pattern `0000`
- Gold: `1 cluster per month, multiple per cluster` (3.0/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Predicted: `unknown` (1000.0/month, `unknown`, `unknown`)
- Reference: `1 cluster per month, multiple per cluster`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
pattern of seizures recurring in short bursts around the beginning of most months
```

**Predicted Evidence**

```text
pattern of seizures recurring in short bursts around the beginning of most months shortly after waking, with quieter intervals between these bursts
```

**Verifier Reason**

```text
Initial label unknown is appropriate as no deterministic temporal frequency candidates were extracted and the note describes a complex pattern without a clear numeric frequency.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
and a momentary speech arrest; on occasion these evolve into focal impaired awareness seizures with right-hand automatisms and subsequent confusion lasting 10–15 minutes. In addition, he reports intermittent generalised tonic–clonic seizures, typically without warning and followed by myalgia and headache for several hours. The calendar indicates a pattern of seizures recurring in short bursts around the beginning of most months shortly after waking, with quieter intervals between these bursts. He records that the focal aware events often precede the larger events by 24–48 hours. 

In terms of frequency, his paper log demonstrates repeated short runs around month‑end to mid‑month, mainly noted on waking in the early morning, with two months showing additional daytime even

---

and a momentary speech arrest; on occasion these evolve into focal impaired awareness seizures with right-hand automatisms and subsequent confusion lasting 10–15 minutes. In addition, he reports intermittent generalised tonic–clonic seizures, typically without warning and followed by myalgia and headache for several hours. The calendar indicates a pattern of seizures recurring in short bursts around the beginning of most months shortly after waking, with quieter intervals between these bursts. He records that the focal aware events often precede the larger events by 24–48 hours. 

In terms of frequency, his paper log demonstrates repeated short runs around month‑end to mid‑month, mainly noted on waking in the early morning, with two months showing additional daytime events under stress. This pattern has been consistent since spring thi
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 22. `gan_15240` — `cluster_composition`

- Failure: `cluster_collapsed_to_rate` / pattern `0000`
- Gold: `multiple cluster per 12 month, multiple per cluster` (0.75/month, `infrequent`, `gt_1_per_6_months_lt_1_per_month`)
- Predicted: `unknown` (1000.0/month, `unknown`, `unknown`)
- Reference: `multiple cluster per 12 month, multiple per cluster`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
Her last convulsive seizure was recorded in 10 - 2016, with occasional clusters of jumps persisting.
```

**Predicted Evidence**

```text
She reports
```

**Verifier Reason**

```text
Initial label is unknown and no deterministic temporal frequency candidates were extracted from the note to support a repair. The note describes intermittent jerks and occasional clusters but does not provide a clear seizure frequency label. Therefore, confirming the initial unknown label is appropriate.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
that demands frequent multitasking; she reports that planned midday rest breaks are often interrupted by staffing needs and children’s routines.

Since I last saw her in January 2017, she reports intermittent brief myoclonic jerks, typically in the late morning or shortly after lunch when she has been on her feet and unable to take a quiet break. Her last convulsive seizure was recorded in 10 - 2016, with occasional clusters of jumps persisting. She has adapted by handing over certain tasks when she feels a build-up of warning sensations (described as a sudden internal "jolt" and diffuse unease lasting seconds), though this is not always possible on busy days. There have been no injuries, tongue bites or incontinence. She denies prolonged confusional states; post-event fatigue tends to be

---

artial response but increased dizziness; discontinued in mid-2016. She also trialled Zonisamide to 200 mg nocte in late 2015, stopped due to appetite suppression and low mood. Currently she takes Levetiracetam 1,000 mg b.d. and Clobazam 10 mg nocte, with Propranolol 10 mg t.d.s. as needed for situational tremor/anxiety around observations at work. She reports good adherence (uses a phone alarm and weekly pill organiser). Side effects are limited to occasional irritability and mild morning lethargy, which she feels are manageable.

Sleep is fragmented by early starts; caffeine intake is two cups in the morning and one at midday. Alcohol intake is minimal. She notes that missed or curtailed rest at lunch
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 23. `gan_15255` — `cluster_composition`

- Failure: `cluster_semantic_mismatch` / pattern `0000`
- Gold: `multiple cluster per 15 month, multiple per cluster` (0.6000000000000001/month, `infrequent`, `gt_1_per_6_months_lt_1_per_month`)
- Predicted: `1 cluster per week, multiple per cluster` (12.99/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Reference: `multiple cluster per 15 month, multiple per cluster`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
Her last convulsive seizure was recorded in 2/2021, with occasional clusters of myoclonic jerks persisting.
```

**Predicted Evidence**

```text
clusters comprise multiple jerks over minutes to an hour and may recur on a few mornings within the same week before settling
```

**Verifier Reason**

```text
The initial label matches the note's description of clusters recurring on a few mornings within the same week, with multiple jerks per cluster; no temporal candidates to suggest repair.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
variability in pace can increase her tiredness by the end of a late shift, though she denies missed doses of medication. Sleep is generally 6–7 hours on early shifts and 7–8 hours on late shifts. No new injuries or absences from work were reported. 

Seizures: The epilepsy phenotype remains combined, with both generalised and focal seizure types. Her last convulsive seizure was recorded in 2/2021, with occasional clusters of myoclonic jerks persisting. She describes these clusters as brief, shock-like jerks of both arms and sometimes the shoulders, typically occurring on awakening after several early starts or following consecutive heavy-lifting shifts; clusters comprise multiple jerks over minutes to an hour and may recur on a few mornings within the same week before settling. In addition, she

---

generalised and focal seizure types. Her last convulsive seizure was recorded in 2/2021, with occasional clusters of myoclonic jerks persisting. She describes these clusters as brief, shock-like jerks of both arms and sometimes the shoulders, typically occurring on awakening after several early starts or following consecutive heavy-lifting shifts; clusters comprise multiple jerks over minutes to an hour and may recur on a few mornings within the same week before settling. In addition, she continues to experience infrequent focal aware sensory auras (tingling in the left hand with a rising epigastric sensation) without evolution to impaired awareness; these occur sporadically and are not associated with convulsions. There have been no episodes of loss of awareness on the warehouse floor, and no recent injuries. She
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 24. `gan_15404` — `cluster_composition`

- Failure: `cluster_semantic_mismatch` / pattern `0000`
- Gold: `1 cluster per 4 month, 3 to 4 per cluster` (0.875/month, `infrequent`, `gt_1_per_6_months_lt_1_per_month`)
- Predicted: `1 cluster per day, 3 to 4 per cluster` (105.0/month, `frequent`, `gte_1_per_day`)
- Reference: `1 cluster per 4 month, 3 to 4 per cluster`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
She may remain seizure-free for up to 4 month, but then will experience clusters of three - four seizures in a single day.
```

**Predicted Evidence**

```text
she
```

**Verifier Reason**

```text
Initial label matches the note text exactly and no temporal candidates were extracted to suggest a better label.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
ted. Patient maintains good adherence using workplace shift-based reminders.

History since last review: 

She works in metal fabrication and welding, with intermittent arc-light exposure; she uses a protective visor as per workplace routine and reports that the visor is always down during active welding. She describes variable seizure occurrence: She may remain seizure-free for up to 4 month, but then will experience clusters of three - four seizures in a single day. These clusters tend to happen without a clear warning, occasionally following periods of poor sleep after late shifts. She denies missed medication around these times. There is no consistent relation to alcohol (rare use) or intercurrent illness. She has not sustained injuries at work and confirms strict adherence to safety policies, including ste

---

-1990, Hospital No: H938271 NHS No. 5839201746  
Flat 5, 14 Forge Street, London, W10 6DF 

Medication: 

Levetiracetam 1 g twice daily. No adverse effects reported. Patient maintains good adherence using workplace shift-based reminders.

History since last review: 

She works in metal fabrication and welding, with intermittent arc-light exposure; she uses a protective visor as per workplace routine and reports that the visor is always down during active welding. She describes variable seizure occurrence: She may remain seizure-free for up to 4 month, but then will experience clusters of three - four seizures in a single day. These clusters tend to happen without a clear warning, occasionally f
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 25. `gan_10984` — `cluster_composition`

- Failure: `cluster_semantic_mismatch` / pattern `0001`
- Gold: `3 cluster per month, 3 to 4 per cluster` (10.5/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Predicted: `1 cluster per month, 3 to 4 per cluster` (3.5/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `3 cluster per month, 3 to 4 per cluster`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
Morning clusters 3×/month; ~three - four events over 90 min.
```

**Predicted Evidence**

```text
Morning clusters 3×/month; ~three - four events over 90 min
```

**Verifier Reason**

```text
The initial label matches the note text exactly and no temporal candidates were extracted to suggest a better label.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
ospital No: C672154 NHS No. 4728395612
78 Willow Lane, London, W9 3HT

Medication:

Oxcarbazepine (Trileptal) 600 mg morning / 600 mg night.

History since last review:

Emily Carter works rotating shifts including nights, and reports that her sleep pattern is frequently disrupted. Over the past three months she has noticed a consistent pattern of Morning clusters 3×/month; ~three - four events over 90 min. These episodes tend to occur after a week of night shifts or following abrupt transition back to early starts. She describes brief sensory warning symptoms with preserved awareness, without progression to convulsive events, and no injuries. Recovery is spontaneous and she is able to continue routine activities later the same day, though she feels
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 26. `gan_10993` — `cluster_composition`

- Failure: `cluster_semantic_mismatch` / pattern `0001`
- Gold: `2 cluster per month, 2 to 4 per cluster` (6.0/month, `frequent`, `gt_1_per_week_lt_1_per_day`)
- Predicted: `1 cluster per month, 2 to 4 per cluster` (3.0/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `2 cluster per month, 2 to 4 per cluster`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
Current pattern: Morning clusters 2×/month; ~2 to 4 events over 90 min.
```

**Predicted Evidence**

```text
Morning clusters 2×/month; ~2 to 4 events over 90 min
```

**Verifier Reason**

```text
Initial label matches the note text exactly and no temporal candidates extracted; confirm as correct.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
ion and tingling in the right hand, followed by behavioural arrest and impaired awareness for under a minute, sometimes with right-hand automatisms and brief post-event disorientation. There has been no generalised tonic–clonic activity reported for over six months. No injuries, tongue biting, or incontinence have been described in this interval.

Current pattern: Morning clusters 2×/month; ~2 to 4 events over 90 min. These clusters are usually preceded by a shorter night or early wake for meetings. Outside of these cluster mornings, he has had only two isolated focal impaired-awareness events in the last eight weeks. He attributes the overall improvement to reduced early starts, scheduled rest breaks, and better hydration as part of his remote working routine.

---

in the right hand, followed by behavioural arrest and impaired awareness for under a minute, sometimes with right-hand automatisms and brief post-event disorientation. There has been no generalised tonic–clonic activity reported for over six months. No injuries, tongue biting, or incontinence have been described in this interval.

Current pattern: Morning clusters 2×/month; ~2 to 4 events over 90 min. These clusters are usually preceded by a shorter night or early wake for meetings. Outside of these cluster mornings, he has had only two isolated focal impaired-awareness events in the last eight weeks. He attributes the overall improvement to reduced early starts, scheduled rest breaks, and better hydration as part of his remote working routine
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 27. `gan_13290` — `infrequent_long_denominator_or_boundary`

- Failure: `frequent_overcalled` / pattern `0000`
- Gold: `4 per 6 month` (0.6666666666666666/month, `infrequent`, `gt_1_per_6_months_lt_1_per_month`)
- Predicted: `2 per 3 week` (2.8866666666666667/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `4 per 6 month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
He did not have seizures for over 6 months, but then reported two generalised tonic-clonic seizures two Fridays ago, each preceded by myoclonic jerks.
```

**Predicted Evidence**

```text
he di
```

**Verifier Reason**

```text
The initial label "2 per 3 week" matches the note's description of two seizures occurring recently after a seizure-free period of over 6 months, and the initial evidence quote is an exact contiguous substring of the note text supporting this frequency. No temporal candidates were extracted, so confirmation is appropriate.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
and he has noted higher stress levels around project deadlines. He denies recent alcohol binges and has maintained hydration and meals as advised. He mentioned occasional brief startles in the mornings over the past few weeks, which he recorded as isolated jerks with no confusion.

Regarding recent events, his seizure diary confirms the following: He did not have seizures for over 6 months, but then reported two generalised tonic-clonic seizures two Fridays ago, each preceded by myoclonic jerks. He described the jerks as brief, occurring in clusters over a few minutes before each convulsion. On both occasions the events occurred shortly after waking. The app entries include witness notes from his partner describing bilateral stiffening followed by rhythmic jerking lasting approximately 90–120 seconds, with a post-ictal phase of about 30 m

---

adherence is self-reported as high and corroborated by his app’s reminder logs. He remains on Levetiracetam 1500 mg b.d., Lamotrigine 150 mg b.d., and Clobazam 10 mg nocte. He reports mild daytime fatigue and intermittent irritability, which he attributes to work stress; no rash, visual disturbance, or gait issues. He uses a smartwatch linked to the diary for sleep tracking; data around the seizure dates indicate reduced sleep duration and increased sleep fragmentation. He has logged caffeine intake on the preceding days as higher than usual.

Neurological examination today is unremarkable. Vital signs are stable. No focal deficits. We reviewed his safety measures: he continues to avoid heights,
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 28. `gan_14354` — `infrequent_long_denominator_or_boundary`

- Failure: `frequent_overcalled` / pattern `0000`
- Gold: `2 to 4 per 3 month` (1.0/month, `infrequent`, `eq_1_per_month`)
- Predicted: `2 to 4 per month` (3.0/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `2 to 4 per 3 month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
He withdrew from Clobazam on 14/Jan. At that time, he had 2 to 4 seizures... He has remained stable without seizures since.
```

**Predicted Evidence**

```text
He withdrew from Clobazam on 14/Jan. At that time, he had 2 to 4 seizures, one precipitated by illness.
```

**Verifier Reason**

```text
The initial label matches the note text exactly describing seizure frequency at the time of Clobazam withdrawal; no temporal candidates to suggest repair.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
edical Centre, 14 Barrow Street, London SE1 2AB  

Dear Dr Ahmed,  

James Walker, DOB: 23-11-1985, Hospital No: NHS4820317 NHS No. 9102746351  
12 Brookfield Road, London, SW4 8HT 

Medication: 

Levetiracetam 1 g twice daily. No adverse effects reported. He prefers to continue with this regimen and has not used rescue medication since January. 

He withdrew from Clobazam on 14/Jan. At that time, he had 2 to 4 seizures, one precipitated by illness. He has remained stable without seizures since. This period has included several weeks of increased work-related stress and regular commuting by bicycle without incident, which he reports simply as part of his usual routine. Sleep pattern has been consistent, and there have been no intercurrent infections since the early January episode. 

We discu
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 29. `gan_15302` — `infrequent_long_denominator_or_boundary`

- Failure: `frequent_overcalled` / pattern `0000`
- Gold: `1 to 2 per 14 month` (0.10714285714285714/month, `infrequent`, `lt_1_per_6_months`)
- Predicted: `1 to 2 per month` (1.5/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `1 to 2 per 14 month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `False`; candidate count: `0`

**Gold Evidence**

```text
No further tonic-clonic seizures have occurred since 2 - 2021, although one or two single jerks remain.
```

**Predicted Evidence**

```text
one or two single jerks remain
```

**Verifier Reason**

```text
Initial label matches the note text "one or two single jerks remain" which supports the frequency of 1 to 2 per month; no temporal candidates to contradict.
```

**Candidate Labels**

```text
(empty)
```

**Frequency Context Snippet**

```text
Dear Dr Patel,  

Emily Carter, DOB: 14-07-1990, Hospital No: H592014 NHS No. 8473629105  
29 Brookside Avenue, Salford, M6 7LP  

Diagnoses: 

Seizure disorder under ongoing evaluation. 

I reviewed Emily Carter today in the follow-up clinic with her partner in attendance. She reports adherence with current medication and good general health. No further tonic-clonic seizures have occurred since 2 - 2021, although one or two single jerks remain. These brief myoclonic-type events occur without clear triggers and do not lead to loss of awareness or injury. There have been no emergency presentations, no nocturnal events reported by her partner, and no new focal neurological symptoms. 

Current treatment remains unchanged and well tolerated, with no reported adverse effects. Sleep hygiene and

---

4 NHS No. 8473629105  
29 Brookside Avenue, Salford, M6 7LP  

Diagnoses: 

Seizure disorder under ongoing evaluation. 

I reviewed Emily Carter today in the follow-up clinic with her partner in attendance. She reports adherence with current medication and good general health. No further tonic-clonic seizures have occurred since 2 - 2021, although one or two single jerks remain. These brief myoclonic-type events occur without clear triggers and do not lead to loss of awareness or injury. There have been no emergency presentations, no nocturnal events reported by her partner, and no new focal neurological symptoms. 

Current treatment remains unchanged and well tolerated, with no reported adverse effects. Sleep hygiene an
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

### 30. `gan_15306` — `infrequent_long_denominator_or_boundary`

- Failure: `frequent_overcalled` / pattern `0000`
- Gold: `2 to 3 per 15 month` (0.16666666666666666/month, `infrequent`, `eq_1_per_6_months`)
- Predicted: `1 to 3 per month` (2.0/month, `frequent`, `gt_1_per_month_lt_1_per_week`)
- Reference: `2 to 3 per 15 month`; hard case: `False`; row_ok: `True`
- Gold in deterministic candidates: `True`; candidate count: `1`

**Gold Evidence**

```text
No further tonic-clonic seizures have occurred since 12/2020, although two to three single jerks remain
```

**Predicted Evidence**

```text
two to three single jerks remain, typically noted at the end of long shifts or on waking after reduced sleep
```

**Verifier Reason**

```text
The initial label "1 to 3 per month" matches the note's description of "two to three single jerks remain" with no explicit monthly window stated, and the initial evidence is an exact contiguous quote from the note supporting this frequency. The candidate "2 to 3 per 15 month" is less precise and not the initial label, so per policy, confirm the initial label.
```

**Candidate Labels**

```text
2 to 3 per 15 month
```

**Frequency Context Snippet**

```text
ent has generalised epilepsy.

Background and current status:
They work on the gate line at a busy metro station where prolonged standing, variable sleep patterns due to early shifts, and occasional crowd surges are part of the daily environment. They report being mindful of hydration and breaks, and have avoided known precipitants where possible. No further tonic-clonic seizures have occurred since 12/2020, although two to three single jerks remain, typically noted at the end of long shifts or on waking after reduced sleep. There is no associated loss of awareness with these jerks and no injuries reported. 

Current medication:
1. Tegretol Retard 600 mg twice daily
2. Keppra 500 mg twice daily

Assessment:
Overall control of tonic-clonic events is maintained. The residual brief myoclonic jer

---

on the gate line at a busy metro station where prolonged standing, variable sleep patterns due to early shifts, and occasional crowd surges are part of the daily environment. They report being mindful of hydration and breaks, and have avoided known precipitants where possible. No further tonic-clonic seizures have occurred since 12/2020, although two to three single jerks remain, typically noted at the end of long shifts or on waking after reduced sleep. There is no associated loss of awareness with these jerks and no injuries reported. 

Current medication:
1. Tegretol Retard 600 mg twice daily
2. Keppra 500 mg twice daily

Assessment:
Overall control of tonic-clonic events is maintained. The residual brief myoclonic jerks are infrequent and appear situational. Mood and cognition are stable on t
```

**Manual Read Notes**

- Mechanism:
- Candidate-slot implication:
- Deterministic repair allowed?:

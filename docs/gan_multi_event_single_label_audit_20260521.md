# Gan Multi-Event / Single-Frequency Label Audit

Date: 2026-05-21

## Question

Does the Gan seizure-frequency dataset contain a common hard extraction problem: letters that
mention multiple seizure events, seizure types, or temporal windows, but provide only one
`seizure_frequency_number` output?

## Scope

This audit covers `data/Gan (2026)/synthetic_data_subset_1500.json`, the 1,500-record synthetic
Gan corpus. The primary gold remains `check__Seizure Frequency Number.seizure_frequency_number[0]`.
The `reference` field is a secondary cross-check, not gold.

The separate Excel file, `data/Gan (2026)/Ten_example_Annotation.xlsx`, is not the main target
here because it is a separate real-letter annotation file and does not have the same JSON
gold/evidence/reference structure.

## Short Answer

Yes. The Gan synthetic JSON has this problem in a substantial and structurally important way.
It is not just noise: many records explicitly require adjudicating between several seizure
frequencies and collapsing them to one benchmark-facing label.

The single-label policy is usually to select the most clinically/benchmark-relevant current
frequency, often the highest frequency across seizure types. This makes the task harder than
extracting "the frequency phrase" because a model must identify all candidate mentions, discard
historical or lower-priority mentions, and normalize the selected one.

## Method

I used the existing Gan audit guidance first:

- `seizure_frequency_number[0]` is gold.
- `reference[0]` is a secondary cross-check and disagreement signal.
- `unknown` and `no seizure frequency reference` are distinct.
- Evidence spans can be non-verbatim or multi-span, so evidence matching is only diagnostic.

Then I ran three complementary checks over the 1,446 clinical/non-`no seizure frequency reference`
records:

1. **Broad letter-text screen**: count sentence-level seizure-frequency/event mentions using
   seizure terms plus frequency/time-window/count cues.
2. **Audit-trail screen**: search each record's `analysis` field for explicit adjudication language
   such as "select the highest frequency", enumerated `(1) ... (2)` frequencies, "two patterns",
   "in addition", and competing seizure-type statements.
3. **Known difficulty signals**: intersect the above with label/reference disagreement and
   multi-span gold evidence (`...` in `seizure_frequency_number[1]`).

These are diagnostic counts, not a replacement for human annotation. The broad screen is an upper
bound because letters often repeat a frequency in the plan or history. The audit-trail screen is a
more conservative lower bound because it only catches cases where the generator/validator analysis
made the adjudication explicit.

## Quantitative Findings

Clinical records audited: 1,446.

| Signal | Count | Share of clinical records | Interpretation |
|---|---:|---:|---|
| At least 2 broad seizure-frequency/event mentions in the letter | 1,336 | 92.4% | Upper-bound signal; includes repetitions and plan text. |
| At least 3 broad seizure-frequency/event mentions in the letter | 1,089 | 75.3% | Strong sign that letters often contain multiple event/time-window references. |
| `analysis` says to select/choose the highest or more frequent rate | 468 | 32.4% | Conservative evidence that single-label adjudication is needed. |
| `analysis` explicitly enumerates multiple frequencies/patterns | 275 | 19.0% | Conservative evidence of multiple candidate outputs in one letter. |
| `analysis` has either multiple-frequency or highest-selection language | 530 | 36.7% | Best conservative lower-bound family for this problem. |
| `analysis` has both multiple-frequency and highest-selection language | 136 | 9.4% | Very high-confidence multi-candidate single-label cases. |
| Gold/reference disagreement | 197 | 13.6% | Independent signal of difficult or ambiguous interpretation. |
| Gold evidence uses `...` multi-span elision | 102 | 7.1% | Evidence often spans non-adjacent parts of the letter. |
| Gold/reference disagreement plus strict multi/highest language | 69 | 4.8% | Cases where multi-candidate structure likely contributes to ambiguity. |

The headline is the 530/1,446 conservative audit-trail signal: over a third of clinical records
have analysis language indicating either multiple candidate frequencies or a highest-frequency
selection rule. The 1,336/1,446 broad text signal shows the model will almost always see more than
one seizure-related temporal/event sentence, even when only one is ultimately label-bearing.

## Failure Modes Found

### 1. Multiple seizure types with different frequencies

This is the clearest version of the problem. The letter contains separate frequencies for focal,
generalised, absence, drop, myoclonic, aura, or cluster events, but the output is a single label.

Example `gan_12383`:

- Gold: `4 per day`
- Gold evidence: `he still has focal onset seizures four times per day`
- Other same-sentence candidate: `tonic-clonic seizures 2 times per month`
- Analysis says the record has focal seizures, drop attacks, and tonic-clonic seizures, then applies
  the rule to choose the highest frequency.

Example `gan_15876`:

- Gold: `6 per week`
- Gold evidence: `Drop attacks are now reported six times weekly`
- Other candidates: myoclonic clusters `3-4 mornings per week`; focal sensory auras `1-2 times per week`
- The gold chooses the highest explicit numeric frequency, not all seizure types.

### 2. Historical/baseline frequency versus current frequency

Many letters describe prior control, recent deterioration/improvement, and current status. The
single label usually reflects the current or benchmark-relevant frequency.

Example `gan_4026`:

- Gold: `1 per month`
- Current evidence: `Now down to roughly one brief absence episode in a typical month`
- Historical competing mention: previously `six to seven absence-type events per month`
- The output requires ignoring the older higher rate.

Example `gan_698`:

- Gold: `1 per week`
- Current evidence: `The current seizure frequency is once a week`
- Competing temporal context: prior seizure freedom for eight months and two travel-associated
  episodes inside the recent period.

### 3. Seizure-free intervals coexisting with active events

The letters often include longest seizure-free interval, no seizures since last appointment, or no
generalised seizures while another seizure type remains active. This is especially risky because a
model can over-select the nearest "no seizures" phrase.

Example `gan_12643`:

- Gold: `1 per day`
- Evidence: `He has daily absences`
- Other mentions include weekly generalised tonic-clonic seizures, focal non-motor events every
  three to four weeks, drop attacks, and `Since the last clinic visit, no further seizures have
  been reported`.

The single label follows the active highest-frequency seizure type, not the short interval since
review.

### 4. Cluster semantics are a separate adjudication burden

Cluster records can mention inter-cluster interval, number per cluster, isolated events between
clusters, or vague cluster counts. The single output must choose one normalized cluster/rate form.

Example `gan_15513`:

- Gold: `1 cluster per 4 to 5 day, 2 to 3 per cluster`
- Evidence: `four to five days without seizures` plus `two - three occurring within 24 hours`
- Other context: a last generalised tonic-clonic seizure 10 days ago with two events that same day.

Example `gan_10010`:

- Gold: `multiple per week`
- Reference: `1 cluster per week, multiple per cluster`
- The letter supports most-morning myoclonic jerks and roughly weekly convulsive groupings. The
  gold chooses the more frequent myoclonic pattern; the reference chose the cluster framing.

### 5. Unknown labels can still contain multiple event descriptions

`unknown` does not mean no event mentions. It often means multiple events/windows exist but cannot
be normalized to a supported frequency.

Example `gan_10183`:

- Gold: `unknown`
- Evidence is multi-span: the recent pattern is difficult to quantify, and both frequency and
  spacing are not reliably documented.
- The letter describes bursts over a few days, quieter stretches, two nocturnal episodes in six
  weeks, several weeks where events bunched together, and inconsistent logs.

This is exactly the sort of case where "extract any numeric event count" would produce a false
specific label.

## Relationship to Existing Audit Signals

The earlier Gan label audit already documented:

- 197 label/reference disagreements.
- 102 multi-span elided evidence records.
- The need to treat reference disagreements as difficulty signals.

This deeper audit explains one major reason for those difficulty signals: the letter often contains
several plausible seizure-frequency candidates, but the benchmark only stores one selected output.

However, multi-event/single-label structure is broader than the 197 disagreements. Many records
with agreement still require correct internal adjudication; `gan_12383`, `gan_11948`, and
`gan_15876` are clean agreement examples that still contain multiple candidate frequencies.

## Implications

1. A Gan S0 extractor should not be evaluated mentally as "find the frequency mention." The real
   task is closer to:
   - enumerate candidate seizure-frequency statements,
   - determine current versus historical/repeated/plan mentions,
   - separate seizure types,
   - normalize cluster and rate forms,
   - select the single Gan-policy output.

2. Prompting or deterministic scaffolds that expose a candidate table are justified. The existing
   temporal-candidate direction is addressing a real dataset property, not an artificial model
   failure.

3. The scorer should remain single-label for benchmark reproduction, but analysis/reporting should
   track multi-candidate cases separately. Otherwise monthly-frequency accuracy hides whether a
   model failed extraction, temporal adjudication, seizure-type prioritization, or normalization.

4. For future error analysis, add a dataset diagnostic flag family:
   - `multiple_candidate_frequencies`
   - `highest_frequency_policy_required`
   - `historical_current_conflict`
   - `seizure_free_conflict`
   - `cluster_adjudication_required`
   - `unknown_with_event_mentions`

## Recommended Next Step

Create a durable audit artifact that exports these flags per record, then stratify existing Gan S0
validation errors by those flags. The highest-value comparison is monthly-frequency accuracy on:

- strict multi/highest records versus other clinical records,
- cluster-adjudication records versus non-cluster records,
- historical/current conflict records,
- gold/reference disagreement records.

This would show whether current model failures are mainly caused by single-label adjudication or by
downstream numeric normalization.


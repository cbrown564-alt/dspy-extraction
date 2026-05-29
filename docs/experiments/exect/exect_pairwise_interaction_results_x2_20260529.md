# ExECT Pairwise Interaction Results X2

Date: 2026-05-29
Status: design correction; prior ladder-aligned comparisons are non-answering
Kanban card: X2 - ExECT Pairwise Interaction Tests

## Correction Summary

This document supersedes the earlier X2 result interpretation. The previously
recorded comparisons were aligned to existing schema ladder surfaces:

- Pair 4 used S1 versus S2 Clean Ladder.
- Pair 3 used S4 baseline versus S4 medication-temporality guard variants.

Those comparisons do not cleanly test pairwise component interaction. X2 is
about individual components and the effect of adding a paired component as
context, before deciding how to stack components into broader optimized
systems.

Therefore, the prior runs below are retained only as diagnostic provenance. They
must not be used to promote, reject, or close Pair 3 or Pair 4 interaction
mechanisms.

## Correct X2 Contract

Dataset: ExECTv2 `exectv2_fixed_v1:validation`, 40 records.
Model policy: GPT 4.1-mini for validation search when model calls are needed.
Decision scope: arm for each corrected pairwise run; mechanism only after
multiple arms or interaction positions are reviewed.
Scorer scope: existing project field-family scorers; not CUI-aware ExECT Table
1 reproduction.

Each pairwise test must use a component-isolated comparison:

| Requirement | Correct design |
| --- | --- |
| Primary varied factor | Presence versus absence of the paired component signal |
| Baseline arm | Target component alone |
| Interaction arm | Same target component plus paired component context/payload |
| Scored endpoint | The target component's benchmark-facing field only |
| Diagnostic fields | May explain errors, but must not become headline metrics |
| Forbidden shortcut | Comparing schema ladder rungs such as S1 vs S2 or S4 baseline vs S4 guard |

## Pair 3: Annotated Medication + Medication Temporality

### Correct Question

Does medication temporality improve benchmark-facing annotated medication
extraction when temporality is supplied as context or a routing signal?

### Correct Comparator

| Arm | Input / context | Output scored | What it tests |
| --- | --- | --- | --- |
| AM-only | Full note plus medication extraction context, without lifecycle/temporality routing | `annotated_medication` only | Current medication component behavior without temporality |
| AM+MT | Same medication component plus medication temporality/lifecycle signal | `annotated_medication` only | Whether temporality helps suppress planned, previous, taper, non-current, or unknown-temporality medication mentions |

Medication temporality itself remains diagnostic under E5. It is not a
benchmark-facing medication-status target, and its F1 must not be the headline
X2 metric unless a separate lifecycle target policy is preregistered.

Primary metrics:

- annotated medication precision, recall, F1, TP, FP, and FN
- false-positive reduction in planned, previous, taper, dose-line,
  other-medication/non-current, and annotation-policy strata
- recall preservation on E6 annotation-derived current-Rx labels

Promotion rule from the X2 plan still applies: promote only if annotated
medication F1 improves by at least 3.0 points or annotated medication precision
improves by at least 5.0 points with recall loss no greater than one label on
validation.

### Prior Non-Answering Diagnostic

The earlier S4 guard comparison did not test AM-only versus AM+MT. It compared
S4 ladder variants and post-processed `medication_temporality` predictions
without using those predictions to route the scored `annotated_medication`
output.

| Run / Variant | Annotated Med F1 | Annotated Med P/R | Med Temp F1 | Med Temp P/R |
| --- | ---: | --- | ---: | --- |
| S4 Baseline | 71.3% | 56.1% / 97.9% | 62.5% | 46.4% / 95.7% |
| S4 MT non-ASM Guard | 71.3% | 56.1% / 97.9% | 72.0% | 57.7% / 95.7% |
| S4 MT non-ASM Dose/Current Guard | 71.3% | 56.1% / 97.9% | 78.9% | 69.4% / 91.5% |

Interpretation: useful as medication-temporality guard diagnostics only. These
values do not answer the Pair 3 interaction question.

## Pair 4: Investigation + Comorbidity

### Correct Question

Does investigation context improve comorbidity extraction, or does comorbidity
context degrade investigation extraction, when the two components are compared
outside the schema ladder?

### Correct Comparator

Pair 4 needs directional component-isolated arms rather than S1 versus S2:

| Direction | Baseline arm | Interaction arm | Output scored |
| --- | --- | --- | --- |
| Investigation target | investigation-only | investigation plus comorbidity context | investigation |
| Comorbidity target | comorbidity-only | comorbidity plus investigation context | comorbidity |

Diagnosis, seizure type, and annotated medication may be monitored as safety
diagnostics if a shared prompt surface is used, but they are not the primary
Pair 4 endpoint.

### Prior Non-Answering Diagnostic

The earlier S1 versus S2 comparison changed the schema family set and scorer
surface, so it cannot reject the investigation+comorbidity interaction arm.

| Field Family | S1 Baseline F1 | S2 Ladder F1 | Delta | S1 Precision / Recall | S2 Precision / Recall |
| --- | ---: | ---: | ---: | --- | --- |
| diagnosis | 93.8% | 88.9% | -4.9 | 97.4% / 90.5% | 92.3% / 85.7% |
| seizure_type | 90.5% | 71.0% | -19.5 | 89.6% / 91.5% | 71.7% / 70.2% |
| annotated_medication | 90.5% | 92.9% | +2.4 | 89.6% / 91.5% | 88.5% / 97.9% |
| investigation | 96.7%* | 93.1% | -3.6 | 96.7% / 96.7% | 96.4% / 90.0% |
| comorbidity | N/A | 72.5% | N/A | N/A | 68.5% / 77.1% |

*The S1 surface does not score investigation; the baseline value was borrowed
from E12/S4 context and is not a matched component-isolated comparator.

Interpretation: useful as broad-stack caution only. These values do not answer
the Pair 4 interaction question and must not be treated as a rejected pairwise
arm.

## Open Cells And Next Steps

- X2 pairwise interaction evidence remains open.
- Pair 3 should be rerun or re-inspected as a clean AM-only versus AM+MT
  comparison with annotated medication as the sole scored endpoint.
- Pair 4 should be redesigned as investigation-only versus investigation+COM
  and COM-only versus COM+investigation, rather than S1 versus S2.
- B1 optimized stack reconstruction remains blocked until corrected isolated
  ceilings and component-isolated pairwise evidence exist.

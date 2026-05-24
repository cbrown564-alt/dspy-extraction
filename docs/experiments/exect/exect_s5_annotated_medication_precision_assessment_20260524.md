# ExECT S5 Annotated Medication Precision Assessment

Date: 2026-05-24  
Status: Assessment complete; implementation still open  
Kanban card: S5 annotated medication precision guards  
Decision scope: diagnostic assessment, not a scorer or model-semantics change

## Research Question

Why is ExECT S5 `annotated_medication` F1 worse than the frozen S1 result, and is the deficit solvable within the expanded S5 schema using more complex deterministic rules?

## Method

Compared the frozen S1 GPT 4.1-mini full-validation run against the active S5 GPT 4.1-mini full-validation runs:

| Surface | Run ID | Schema | Scorer |
| --- | --- | --- | --- |
| S1 frozen reference | `exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` | `exect_s0_s1_field_family` | `exect_field_family_deterministic_v1` |
| S5 baseline | `exect_s5_validation_full_gpt4_1_mini_20260524T142812Z` | `exect_s5_core_field_family` | `exect_s5_core_field_family_deterministic_v1` |
| S5 frequency pre-vocab | `exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z` | `exect_s5_core_field_family` | `exect_s5_core_field_family_deterministic_v1` |

No scorer semantics were changed. The assessment uses the audited ExECT prescription view: `annotated_medication` is the S1 prescription-name family only, and medication temporality remains excluded from S5.

## Headline Result

| Run | Medication precision | Medication recall | Medication F1 | Mismatch docs |
| --- | ---: | ---: | ---: | ---: |
| S1 frozen reference | 90.0% | 95.7% | 92.8% | 4 |
| S5 baseline | 56.1% | 97.9% | 71.3% | 22 |
| S5 frequency pre-vocab | 59.0% | 97.9% | 73.6% | 19 |

The S5 deficit is a precision failure, not a recall failure. S5 finds almost all gold medications, but it emits many extra medication labels that S1 avoided.

## Error Anatomy

S1 had four `annotated_medication` mismatch documents:

- `EA0052`: missed `carbamazepine`
- `EA0078`: false-positive `levetiracetam`, `carbamazepine` against a `missing_gold` document
- `EA0136`: `epilim chrono` brand mismatch plus extra `carbamazepine`
- `EA0143`: historical `lamotrigine` false positive

S5 pre-vocab had nineteen mismatch documents. The new burden is mostly false positives:

- non-ASM/comorbidity medication leakage: `simvastatin`, `aspirin`, `venlafaxine`, `omeprazole`, `thyroxine`, `warfarin`, `ramipril`, `bisprolol`, `midazolam`, `pravastatin`, `insulin`, `sumitriptan`
- planned ASM leakage: `levetiracetam` in suggestions such as "would suggest starting"
- historical/failed ASM leakage: `levetiracetam gave her mood disorder`, `lamotrigine wasn't effective`, `changed from levetiracetam`, `initially treated with lamotrigine`
- brand/surface mismatch: `eplim` / `eplim chrono` versus `epilim chrono`
- duplicate same-drug surfaces: `eplim` plus `sodium valproate`
- gold-policy or annotation-limit cases: `EA0078` has `missing_gold`; `EA0136` text says current `carbamazepine` and `Eplim Chrono`, but gold contains only `epilim chrono`

## Why S5 Is Worse Than S1

S5 uses the same benchmark-facing medication scorer semantics as S1, but the extraction context is different. The S5 program asks the model to populate a broader clinical surface: diagnosis, seizure type, annotated medication, investigation, seizure frequency, and internally still carries broader S4-style fields in the prediction artifact. That wider prompt context appears to pull medication-history, comorbidity-drug, planned-treatment, and rescue-medication surfaces into `annotated_medication`.

The regression is therefore not evidence that the ExECT medication gold is intrinsically harder under S5. It is an expanded-schema interference problem: the broader task makes the model less conservative about the narrow S1 prescription-name family.

This matches prior S4 medication-temporality findings: S4 full validation showed high recall but poor precision, with non-ASM leakage and planned/previous ASM over-tagging as the dominant residuals. S5 inherits the same failure shape even though S5 excludes `medication_temporality`.

## No-Model Guard Simulation

A no-model simulation was run against `exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z` predictions using the existing `exect.medication.benchmark_bridge.v1` behavior: drop non-ASM labels and apply benchmark medication surface alignment. This preserves scorer semantics and only changes prediction-facing medication labels.

| Condition | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| S5 pre-vocab observed | 59.0% | 97.9% | 73.6% |
| Drop non-ASM + existing bridge | 78.0% | 97.9% | 86.8% |
| Drop non-ASM + explicit `eplim`/`eplim chrono` repair sketch | 77.0% | 100.0% | 87.0% |

The exact F1 depends on brand-repair policy because `epilim` surfaces can either preserve the brand or collapse to `sodium valproate`. The important result is robust: non-ASM filtering alone clears the Kanban target of >80% F1, but it does not restore S1-level precision.

## Residual After Simple Guards

After non-ASM and brand/surface repair, residual errors concentrate in a smaller number of harder cases:

| Document | Residual issue | Solvability read |
| --- | --- | --- |
| `EA0016` | planned `levetiracetam` suggestion with no gold medication | solvable with planned-start guard |
| `EA0052` | planned switch to `eslicarbazepine`; previous failed `levetiracetam` / `lamotrigine` | solvable with planned/history evidence guard |
| `EA0053` | planned `levetiracetam` start | solvable with planned-start guard |
| `EA0059` | `gabapentin` listed under "Other medication" while ASM gold has `brivaracetam`, `lamotrigine` | partly solvable with section/current-ASM-list guard, but clinically ambiguous because gabapentin can be ASM |
| `EA0078` | `missing_gold` document with clinically plausible medication mentions | not cleanly solvable without changing missing-gold handling or accepting annotation-faithful drops |
| `EA0098` | previous `levetiracetam` after switch to `lamotrigine` | solvable with history/switch guard |
| `EA0102` | duplicate/misspelled valproate surfaces | solvable with canonical duplicate and `eplim` repair |
| `EA0131` | previous `carbamazepine` monotherapy after switch to valproate | solvable with switch/history guard |
| `EA0136` | extra `carbamazepine` despite current-taking text; gold only has `epilim chrono` | hard annotation-policy case, not a purely clinical rule |
| `EA0143` | historical `lamotrigine` | solvable with history guard |
| `EA0188` | future possible `lamotrigine` increase | solvable with future/consider guard |

## Interpretation

The medication F1 deficit is substantially solvable in S5, but the solution should be tiered:

1. **M0 non-ASM guard**: drop labels whose canonical medication is not in the ASM allowlist. This is low-risk and likely lifts S5 medication F1 from 73.6% to the mid/high 80s.
2. **M1 brand/surface repair**: explicitly repair `eplim` and `eplim chrono` to the audited `epilim chrono` surface where appropriate, and dedupe same-canonical valproate surfaces.
3. **M2 planned/history/future evidence guard**: drop ASM labels when aligned evidence is clearly planned, previous, failed, switched-from, or future-hypothetical, unless the same document has current prescription evidence for the same canonical medication.
4. **M3 section/current-list guard**: prefer explicit current anti-epileptic/current medication sections over "other medication", history, discussion, and plan sections.

M0+M1 should be enough to satisfy the immediate Kanban validation target (>80% F1). M2+M3 are needed if the goal is S1-like 90%+ precision, but they should be preregistered as a separate implementation variant because they introduce more annotation-policy risk.

## Caveats

- This assessment is validation-split only, not test reporting or published ExECT Table 1 reproduction.
- The no-model simulation is diagnostic; it did not write new prediction artifacts or change scorer semantics.
- `EA0078` and `EA0136` show that some residual "errors" are annotation-policy or missing-gold cases. A clinically richer extractor may remain wrong under the audited benchmark view.
- Evidence support remains diagnostic and was not used to change benchmark-facing scoring.

## Recommendation

Implement a narrow S5 annotated-medication guard arm rather than changing the S5 scorer:

- primitive / implementation variant: `am_guard_non_asm_brand_alias_v1`
- position: post-prediction, prediction-affecting bridge for `annotated_medication`
- behavior: drop non-ASM, repair `eplim`/`eplim chrono`, dedupe same-canonical medications while preserving the benchmark-facing surface
- gate: full-validation `annotated_medication` F1 >80%, no diagnosis/seizure-type/investigation regression, and report remaining planned/history ASM residuals separately

If that clears the gate, follow with a separately preregistered `am_guard_temporal_evidence_v1` for planned/history/future ASM leakage. Do not merge temporal evidence pruning into the first guard without an explicit cap-25 comparison, because it can silently encode annotation-policy choices.

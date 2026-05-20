# ExECT S2 Cap-25 Validation — Error Read

Date: 2026-05-19

Run artifact:

- `runs/exect_s2_validation_cap25_gpt4_1_mini_20260519T224038Z`

Config:

- `configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json`
- `prompt_version`: `exect_s2_field_family_v1_label_policy`
- `scorer`: `exect_s2_field_family_deterministic_v1`
- S1 bridges: frozen v4.10 (imported unchanged from `exect_s0_s1.py`)

Comparison anchor (same 25 validation records, S1-only):

- `runs/exect_s0_s1_validation_cap25_gpt4_1_mini_20260519T221936Z` — 95.8% micro F1, seizure F1 95.4%, **2** seizure-mismatch records

Design context: `docs/exect_s2_field_expansion_design.md`

## Headline metrics

| Metric | S2 cap-25 (5 fam) | S1 v4.10 cap-25 (3 fam) |
| --- | ---: | ---: |
| Micro F1 | **66.4%** | 95.8% |
| Diagnosis F1 | 88.4% | (within S1 micro) |
| Seizure F1 | **40.0%** | **95.4%** |
| Medication F1 | 81.7% | (within S1 micro) |
| Investigation F1 | 85.7% | n/a |
| Comorbidity F1 | 49.0% | n/a |
| Evidence support | 87.1% | ~96% |

**Records with any field-family mismatch:** 22 / 25 (S2) vs ~5 / 25 (S1 cap-25, estimated from family doc counts).

**Seizure regression is not bridge regression.** Side-by-side predictions on the 16 seizure-mismatch records show **14 records green on S1 cap-25 and red on S2** with the same post-bridge pipeline. Only **EA0072** and **EA0109** fail seizure scoring on both runs (persistent S1 gaps).

## Seizure regression — root cause

Adding investigation + comorbidity fields in one pass changes **model raw outputs** for seizure type before deterministic bridges run. Bridges are unchanged; they do not recover all S1 surfaces when the model modernizes or shortens phrasing.

### Comparison table (seizure labels after bridges)

| Record | S1 v4.10 cap-25 (pass) | S2 v1 (fail) | Pattern |
| --- | --- | --- | --- |
| EA0008 | focal seizures with **altered** awareness | focal seizures with **impaired** awareness | Lexical swap (no bridge) |
| EA0016 | focal **seizure** | **focal** | Specificity collapse |
| EA0018 | temporal lobe seizure, focal seizures, occipital lobe seizures | focal **aware** seizure, focal seizure | ILAE modernization / drop anatomical |
| EA0026 | generalized tonic clonic **seizures** | generalized tonic clonic **seizure** | Plural loss |
| EA0029 | generalized tonic clonic **seizures** | generalized tonic **seizures**, **absence seizures** | Plural + absence FP |
| EA0045 | focal seizures with **altered** awareness, focal to bilateral **convulsive** seizures | focal **impaired awareness seizure**, focal to bilateral **tonic clonic** seizure | ILAE + convulsive→TBC |
| EA0047 | **generalized seizures** | generalized **seizure**, absence seizure, myoclonic jerk | Coarse surface + absence FP |
| EA0050 | generalized tonic clonic **seizures** | generalized tonic clonic **seizure**, absence seizure | Plural + absence FP |
| EA0053 | myoclonic **seizures** | myoclonic **seizure** | Plural loss |
| EA0061 | same as EA0045 | same ILAE pattern as EA0045 | ILAE + convulsive→TBC |
| EA0072 | focal motor seizures, secondary generalized seizures, **secondary** | (unchanged) | Persistent S1 bridge gap |
| EA0100 | *(empty)* | generalized tonic clonic seizure | New FP (no gold seizure) |
| EA0109 | temporal lobe seizure, focal seizures | focal **aware** seizure | ILAE collapse |
| EA0116 | generalized tonic clonic **seizures** | generalized tonic clonic **seizure** | Plural loss |
| EA0124 | generalized tonic clonic **seizures** | GTCS + **absence seizures** | Absence FP |
| EA0125 | generalized tonic **seizures** | generalized tonic **seizures**, **absence seizures** | Absence FP |

### Tagged seizure clusters for S2 v1.1 (prompt-first; bridges only if prompt insufficient)

1. **Plural preservation (GTCS / myoclonic)** — EA0026, EA0029, EA0050, EA0053, EA0116. Reinforce S1 rule: preserve plural `seizures` when the note uses plural; do not emit singular GTCS when gold uses plural GTCS.
2. **Altered vs impaired awareness** — EA0008, EA0045, EA0061. Explicitly forbid `impaired awareness` when the note says `altered awareness`; keep audited phrase.
3. **Anti-ILAE surface guard** — EA0018, EA0045, EA0061, EA0109. Do not emit `focal aware`, `focal impaired awareness seizure`, or similar ILAE labels when the note uses anatomical or legacy benchmark surfaces.
4. **Absence / JME over-extraction** — EA0029, EA0047, EA0050, EA0124, EA0125. Do not add `absence seizures` unless the note explicitly names absence events in the seizure-type slot (reuse S1 JME coarse-surface policy).
5. **Convulsive vs tonic-clonic wording** — EA0045, EA0061. Prefer `focal to bilateral convulsive seizures` when that is the note surface, not `tonic clonic`.
6. **Specificity collapse** — EA0016. Do not emit bare `focal` when gold expects `focal seizure`.
7. **Persistent S1 tail** — EA0072 (`secondary` FP), EA0109 (ILAE). Fix in S2 prompt recovery first; only touch S1 bridges if prompt fails on cap-25 replay.

## Comorbidity — primary S2 tuning target

13 / 25 records with comorbidity mismatches. Patterns:

| Pattern | Records | Example |
| --- | --- | --- |
| **Umbrella vs atomized gold** | EA0016 | Pred `stroke` / evidence “CVA with right hemiparesis”; gold `cva`, `hemiparesis`, `infarct` separately |
| **Modifier granularity** | EA0072, EA0124 | Gold `learning difficulties`; pred `moderate learning difficulties` / `mild learning difficulties` |
| **Singular/plural** | EA0090, EA0125 | Gold `migraines`; pred `migraine` |
| **Synonym / specificity** | EA0072 | Gold `trisomy`; pred `trisomy 21` |
| **Missed affirmed history** | EA0059, EA0061, EA0053, EA0048 | FN `meningitis`, `brain atrophy`, `cortical dysplasia`, `arachnoid cyst`, `jerk` |
| **Procedure vs condition** | EA0008 | FN `meningioma surgery` (gold treats resection as comorbidity phrase) |
| **New FP (no gold)** | EA0078, EA0100, EA0125 | depression, hypertension, migraine |

**Policy hypothesis for v1.1:** Prefer **atomized** PatientHistory CUIPhrase surfaces over clinical umbrella terms; match gold canonicalization via `canonical_comorbidity_label` (hyphen→space, lower case); avoid severity modifiers not in gold; emit each affirmed history phrase as its own label when the note lists components separately.

## Investigation

3 / 25 records with mismatches — generally strong (85.7% F1).

| Record | Issue |
| --- | --- |
| EA0016 | FP `mri unknown` (no performed MRI result in note) |
| EA0102 | FP `eeg abnormal` vs gold `eeg normal` |
| EA0125 | FP `eeg unknown`, `mri unknown` |

**Policy hypothesis:** Tighten “performed + stated result only”; do not emit `unknown` unless the note explicitly says result unknown; do not flip normal→abnormal.

## Medication (S1 family collateral damage)

10 / 25 records — **FP only, FN=0**. Model over-extracts non–anti-seizure or non-annotated drugs when attending to comorbidity/investigation context (e.g. EA0016 simvastatin/aspirin, EA0116 insulin).

**Policy hypothesis:** Reinforce S1 prescription-only medication policy at top of S2 signature; do not expand medication list because comorbidities mention other drugs.

## Evidence support (diagnostic)

22 evidence support errors across fields — mix of missing spans, header quote formatting, and ellipsis in quotes (EA0016 seizure/comorbidity). Not the primary F1 blocker but contributes to 87.1% vs ~96% S1 cap-25.

## Recommended S2 v1.1 scope (bounded)

**In scope (S2 prompt + optional S2-only bridges, not S1 validation retune):**

1. Seizure clusters 1–4 above (prompt reinforcement of existing S1 label-policy rules at top of signature).
2. Comorbidity atomization + modifier guard (prompt + examples).
3. Investigation performed/result guard.
4. Medication prescription-only reinforcement.

**Out of scope:**

- Reopening S1 v4.10 bridge logic on validation split unless cap-25 replay after prompt-only v1.1 still shows EA0072-class failures.
- Full 40-record validation until cap-25 seizure F1 recovers toward S1 cap-25 band (~90%+ on seizure family).

## Commands

```powershell
uv run python scripts/run_experiment.py --experiment configs/experiments/exect_s2_validation_cap25_gpt4_1_mini.json --env-file .env
```

After v1.1 prompt/policy change, replay cap-25 before full validation.

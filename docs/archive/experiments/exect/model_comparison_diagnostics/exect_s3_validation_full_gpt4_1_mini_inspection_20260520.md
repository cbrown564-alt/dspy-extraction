# ExECT S3 Full Validation (40) — Error Read

Date: 2026-05-20

Run artifact:

- `runs/exect_s3_validation_full_gpt4_1_mini_20260519T233810Z`

Config:

- `configs/experiments/exect_s3_validation_full_gpt4_1_mini.json`
- `prompt_version`: `exect_s3_field_family_v1_0_label_policy`
- `program_variant`: `exect_s3_field_family_single_pass`
- `scorer`: `exect_s3_field_family_deterministic_v1`
- S2 bridges: reused from frozen `exect_s2.py` (not edited); S1 bridges from frozen v4.10

Comparison anchors:

| Run | Records | Scope |
| --- | ---: | --- |
| S3 cap-25 v1.0 | 25 | `…233252Z` |
| S3 smoke v1.0 | 3 | `…233117Z` |
| **S2 full v1.3 (frozen)** | 40 | `…231223Z` — **80.9%** micro F1 (5 fam) |
| S2 cap-25 v1.3 | 25 | `…230945Z` — 87.5% micro F1 (5 fam) |

Design context: `docs/experiments/exect/exect_s2_s4_schema_ladder_design.md`, `docs/experiments/exect/exect_s3_phase1_overlap_policy.md`

## Headline metrics

| Metric | Full v1.0 (40) | Cap-25 v1.0 (25) | Δ (full − cap) | S2 full v1.3 (40, 5 fam) |
| --- | ---: | ---: | ---: | ---: |
| Micro F1 (9 fam) | **56.1%** | 61.7% | −5.6pp | 80.9% (not comparable scope) |
| Diagnosis F1 | **92.5%** | 95.2% | −2.7pp | 88.9% |
| Seizure F1 | **61.2%** | 67.6% | −6.4pp | 71.0% |
| Medication F1 | **78.6%** | 77.1% | +1.5pp | 90.0% |
| Investigation F1 | **10.3%** | 9.3% | +1.0pp | **90.0%** |
| Comorbidity F1 | **57.1%** | 71.0% | **−13.9pp** | 69.3% |
| Birth history F1 | **26.7%** | 66.7% | **−40.0pp** | n/a |
| Onset F1 | **10.0%** | 15.4% | −5.4pp | n/a |
| Epilepsy cause F1 | **23.5%** | 22.2% | +1.3pp | n/a |
| When diagnosed F1 | **23.5%** | 25.0% | −1.5pp | n/a |
| Micro recall | 63.6% | 72.3% | −8.7pp | 82.2% |
| Evidence support | **87.8%** | 87.3% | +0.5pp | — |

**Records with any field-family mismatch:** 37 / 40 (123 family-level mismatch entries).

Cap-25 was optimistic on **comorbidity** and **birth_history** but pessimistic on pooled 9-family micro vs full. Investigation was already collapsed on cap-25 (9.3% F1); full validation confirms this is not a small-sample artifact.

## Root cause summary

| Pattern | Families affected | Mechanism |
| --- | --- | --- |
| **Label-policy drift in wider pass** | investigation (primary) | Model emits clinical/imaging prose (`mri brain normal`, `eeg generalized spike and wave`) instead of benchmark `modality+result` strings (`mri normal`, `eeg abnormal`). Only **4 / 48** investigation predictions match canonical gold format. |
| **Multi-family output drift** | seizure, medication, comorbidity | Same failure mode as S1→S2: adding fields without stronger S2-priority guidance degrades frozen-family outputs despite unchanged bridges. |
| **Sparse gold + surface mismatch** | birth_history, onset, cause, when_diagnosed | Low support on validation split; model paraphrases gold CUIPhrases (`normal birth` vs `birth was normal`) or mis-assigns timing phrases across S3 slots. |
| **Not primary** | All | Scorer/loader regression — gold supports unchanged; S2 full on same 40 records still scores 90% investigation. |
| **Not primary** | All | Evidence — 87.8% quote support; 68 evidence diagnostics (36 missing spans, 32 unsupported quotes) do not explain investigation F1 collapse. |

## Mismatch mix (123 family-level mismatch entries)

| Family | Mismatch entries |
| --- | ---: |
| Investigation | 25 |
| Seizure type | 19 |
| Comorbidity | 18 |
| Onset | 16 |
| Annotated medication | 14 |
| When diagnosed | 11 |
| Epilepsy cause | 9 |
| Diagnosis | 6 |
| Birth history | 5 |

## Investigation — binding failure (not bridge failure)

Gold labels are exclusively `eeg|mri|ct` + `normal|abnormal|unknown` (30 gold labels on 40 records). Predictions:

- **48** investigation values emitted across 40 records
- **40** unique surfaces
- **4** canonical modality+result matches
- **44** non-canonical (clinical descriptions, planned imaging, punctuation variants)

Example false-positive surfaces (each seen once in mismatch list):

- `mri brain normal`, `mri+normal`, `eeg+generalized spike and wave`
- `eeg planned`, `mri brain planned`
- `mri: normal apart from incidental arachnoid cyst`
- `mri generalized brain atrophy with white matter ischaemic change`

Gold false-negatives (canonical labels missed when model emitted prose instead):

- `eeg normal`, `eeg abnormal`, `eeg unknown`, `mri normal`, `mri abnormal`, `ct normal`, `ct abnormal` (one miss each among mismatched records)

**Read:** The nine-family prompt dilutes the frozen S2 investigation policy. Deterministic bridges cannot map free-text imaging findings to a unique `modality+result` label without semantic repair (out of scope for Phase 1).

## Comorbidity — drift + cap optimism

Full F1 **57.1%** vs S2 full **69.3%** (−12.2pp). Cap-25 was **71.0%**, so full split adds **−13.9pp** — comorbidity on the 15 records outside cap-25 is worse, similar to S2 v1.2 full read.

False positives (sample): `cerebrovascular accident`, `right hemiparesis`, `mood disorder`, `depression`, `meningitis` (when not atomized to audited surfaces).

False negatives (sample): `cva`, `hemiparesis`, `stroke`, `infarct`, `diabetes`, `traumatic`, `brain injury` — atomized gold not recovered; S2 v1.3 bridges not fully effective when model skips labels in the wider pass.

**jerk** FP cluster is smaller than S2 v1.2 full read (no dominant 7× jerk count in top FP list); drift here is broader omission/paraphrase, not only jerk.

## Seizure and medication

| Family | S3 full | S2 full | Δ |
| --- | ---: | ---: | ---: |
| Seizure | 61.2% | 71.0% | −9.8pp |
| Medication | 78.6% | 90.0% | −11.4pp |

Seizure FP examples: ILAE-style or umbrella labels (`focal seizures with temporal lobe onset`, `absence seizures`, `myoclonic jerk`, `generalized seizure`) — same multi-family drift class as S2 cap-25 before v1.1, but investigation collapse is new and worse.

Medication: recall remains high (93.6%) but precision drops (67.7%) — over-extraction of drug names or comorbidity bleed in the nine-family pass.

## S3-only families (sparse gold on validation)

| Family | F1 | Support | Notes |
| --- | ---: | ---: | --- |
| birth_history | 26.7% | 8 | Cap-25 **66.7%** on n=3 only — full split exposes paraphrase (`born normally` pred vs `birth was normal` / `normal birth` gold). |
| onset | 10.0% | 3 | Many onset **FPs** on records without gold onset (16 mismatch entries, support=3). |
| epilepsy_cause | 23.5% | 7 | Cause vs comorbidity slot confusion (`meningioma`, `stroke` as cause); gold `meningitis` missed when phrasing differs. |
| when_diagnosed | 23.5% | 4 | Model emits seizure/diagnosis phrases in timing slot (`single focal seizure` on EA0016). |

Overlap policy (`docs/experiments/exect/exect_s3_phase1_overlap_policy.md`) is working as designed at scorer level; extraction assigns phrases to wrong families or non-canonical surfaces.

## Evidence

| Metric | Value |
| --- | ---: |
| Quote support | 87.8% |
| Offsets valid (when present) | 100% |
| Evidence errors | 68 |
| Missing evidence spans | 36 |
| Unsupported quotes | 32 |

Evidence is adequate for contract gating; it does not explain investigation metric collapse.

## Decision read

| Gate | Result |
| --- | --- |
| Full validation executed | **Pass** — 40/40, schema valid |
| Frozen S2 families held | **Fail** — investigation −79.7pp vs `…231223Z`; comorbidity −12.2pp; seizure/medication −10–11pp |
| S3 new families baseline | **Weak** — best birth_history 26.7%; onset/cause/when_diagnosed &lt;25% F1 on sparse gold |
| Cap-25 promotion proxy | **Fail** for S2 families — investigation already broken on cap; comorbidity/birth_history optimistic |
| Evidence / contract | **Pass** |

## Recommended next steps (Thread D)

1. **Do not** tune on validation or edit S2 v1.3 / S1 v4.10 frozen prompts.
2. If continuing S3: ship **v1.1 label-policy** with explicit **S2-priority block** (mirror S2 v1.1 after S1 seizure regression):
   - Restate investigation `modality+result` only; forbid imaging prose in `investigation`.
   - Reinforce comorbidity atomization and seizure legacy surfaces before any S3 field.
   - Cap-25 regate → full replay; compare investigation canonical rate (target: majority of preds in `eeg|mri|ct` + `normal|abnormal|unknown`).
3. **Alternative:** **Freeze ladder at S2 v1.3** for benchmark-facing work; treat S3 Phase 1 as infrastructure-only until a staged extraction design (e.g. S2 pass + S3 pass) is justified.
4. Record this run as the **S3 v1.0 full baseline** in Kanban; any v1.1+ must cite `…233810Z`.

**Do not:** compare 56.1% nine-family micro F1 to 80.9% five-family S2 micro as a single regression headline.

## Artifact quick reference

```powershell
$run = "runs/exect_s3_validation_full_gpt4_1_mini_20260519T233810Z"
Get-Content "$run/metrics.json" | ConvertFrom-Json | Select-Object -ExpandProperty benchmark_metrics
```

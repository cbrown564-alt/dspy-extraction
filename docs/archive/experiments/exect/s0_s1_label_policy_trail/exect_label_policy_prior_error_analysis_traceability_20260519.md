# ExECT Label Policy vs Prior Error Analysis: Traceability Report

Date: 2026-05-19

## Research Question

Are the ExECT S0/S1 label-policy iterations through v4.4 (`exect_s0_s1_field_family_v4_4_label_policy`) incorporating the knowledge documented in `docs/archive/prior-context/previous_exect_error_analysis.md`, or has rapid experimentation drifted away from previously established failure modes and fixes?

## Motivation

Between 2026-05-16 and 2026-05-19 the project ran a dense ladder of ExECT experiments (v2 → v4.4), expanded a regression slice from 12 to 23 records, and promoted v4.4 as the new monolithic anchor (82.0% micro F1 on full validation). That pace raises a legitimate risk: fixes driven only by the latest full-validation false positives may omit canonical cases that were already analyzed in the primary Qwen/Gemini sweep.

This report reconciles the 2026-05-16 error analysis with the current audited gold/scorer contract, the v4.x implementation chain, and the v4.4 validation artifacts.

## Method

### Source documents

| Document | Role |
| --- | --- |
| `docs/archive/prior-context/previous_exect_error_analysis.md` | Primary sweep seizure/diagnosis failure taxonomy and Round 2 recommendations (§7–8) |
| `docs/archive/prior-context/prior_prompt_error_analysis_synthesis.md` | Cross-project synthesis; only explicit upstream link to the prior ExECT analysis |
| `docs/datasets/exect/exect_gold_label_audit.md` | Authoritative annotation-policy and loader quirks |
| `docs/experiments/exect/exect_s0_s1_baseline_design.md` | Benchmark-facing S0/S1 hypothesis and label-policy constraints |
| `docs/experiments/exect/exect_s0_s1_smoke_inspection.md` | Documented conflict: old `symptomatic → focal epilepsy` vs audited scorer for EA0008 |
| `docs/experiments/exect/exect_s0_label_policy_v4_2_implementation.md` through `docs/experiments/exect/exect_s0_label_policy_v4_4_implementation.md` | v4 ladder implementation and metrics |
| `docs/experiments/exect/exect_s0_s1_diagnosis_recall_probe_inspection_20260519.md` | Closed add-only recall path; recommended co-list approach adopted in v4.4 |

### Code and policy artifacts

- Prompt policy: `src/clinical_extraction/programs/exect_s0_s1.py` (`EXECT_S0_S1_LABEL_POLICY_GUIDANCE`, `EXECT_S0_S1_POLICY_EXAMPLES`, deterministic bridges)
- Regression gate: `data/fixtures/exect_s0_label_policy_error_regression_slice.json` (37 records after v4.4 full read; was 23)
- Scorer: `exect_field_family_deterministic_v1` (unchanged across v4 ladder)

### Evaluation artifacts

| Run | Config scope | Prompt version |
| --- | --- | --- |
| `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T210602Z` | Full validation (40 records) | v4.4 |
| `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T210111Z` | Full validation (40 records) | v4.3 (comparison anchor) |
| `runs/exect_s0_s1_label_policy_regression_slice_gpt4_1_mini_20260519T210540Z` | 23-record slice | v4.4 |

Model: GPT 4.1-mini via OpenAI. Program variant: `exect_s0_s1_field_family_single_pass`.

### Canonical case check

For each record in `docs/archive/prior-context/previous_exect_error_analysis.md` §8, gold labels were loaded via `load_exect_gold_document` and compared to v4.4 predictions from the full-validation run above.

## Results

### Executive summary

| Question | Finding |
| --- | --- |
| Is prior error analysis incorporated? | **Partially** — behavioral patterns yes; several **literal** Round 2 prescriptions no |
| Is v4.4 aligned with the old doc? | **Mixed** — improves diagnosis *recall* (co-list `epilepsy`); old doc often targeted *precision* via coarser labels |
| Did rapid iteration lose track? | **Somewhat** — regression slice tracks recent full-val FPs, not the old §8 canonical catalog |
| Is v4.4 effective? | **Yes on headline metrics**; residual failures match families the old doc named |

### The audited-gold pivot (why “literal” recommendations diverge)

The 2026-05-16 analysis assumed primary-sweep gold surfaces, for example:

- EA0008 seizure: `focal seizure` (coarse)
- EA0008 diagnosis: `focal epilepsy` (collapsed from symptomatic structural wording)

The **current** audited loader/scorer expects:

- EA0008 seizure: `focal seizures with altered awareness`
- EA0008 diagnosis: `symptomatic structural focal epilepsy`

The v2 implementation explicitly chose audited surfaces over recovered hand-crafted guidance (`docs/experiments/exect/exect_s0_s1_smoke_inspection.md`, §2026-05-18 Label-Policy V2 Follow-Up). Many Round 2 items in the old analysis are therefore **inverted** relative to today’s benchmark, not omitted by accident.

### Round 2 recommendation traceability

#### Seizure type (`previous_exect_error_analysis.md` §7.1)

| Old recommendation | v4.4 status | Notes |
| --- | --- | --- |
| Remove `focal impaired awareness seizure` / `focal aware seizure` from benchmark label list | **Not done** | No separate `labels.py`; model emits free text normalized via `canonical_clinical_phrase` + bridges |
| Mapping example: impaired awareness → `focal seizure` | **Inverted** | `plural_seizure_type_preservation` keeps `focal seizures with altered awareness` |
| Revise ILAE “clinically natural” guidance | **N/A** | Different architecture; policy is audit-surface oriented |
| Do not add secondary GTCS as separate type unless named | **Partially inverted** | Guidance forbids independent secondary labels; **fused** phrase `focal seizures with secondary generalisation` is **split** into three audited labels (matches EA0090 gold) |
| Do not infer seizure type from diagnosis | **Incorporated** | Policy guidance + `test_exect_s0_s1_bridge_does_not_infer_seizure_type_from_diagnosis` |

Simulated +0.14 seizure F1 from coarse ILAE remap (old §2.2) is **not applicable** under current gold without a scorer change.

#### Diagnosis (`previous_exect_error_analysis.md` §7.2)

| Old recommendation | v4.4 status | Notes |
| --- | --- | --- |
| `symptomatic structural focal` → `focal epilepsy` | **Rejected** | `symptomatic_structural_focal_preservation` example + restoration bridge |
| Single-event / provisional diagnosis → null | **Incorporated** | `single_event_diagnosis_null` example; EA0016 correct on full val |
| Five-label constrained diagnosis set | **Rejected** | `ALLOWED_DIAGNOSIS_LABELS` remains broad (`symptomatic`, `focal`, lobe labels, etc.) |
| Investigate `[]` vs `''` scoring artifact | **Likely N/A** | Field-family scorer: zero gold diagnosis support → `f1 is None`, not a false mismatch (`tests/test_exect_scoring.py`) |
| Do not over-specify `epilepsy` → `focal epilepsy` | **Opposite problem now** | v4.4 **adds** generic `epilepsy` via prompt + `diagnosis_co_list_augmented` bridge |

#### Medication and evidence

Not covered in `previous_exect_error_analysis.md`. Absorbed in v4.2–v4.3 (planned/historical ASM exclusion, brand surfaces, evidence contiguity)—aligned with `prior_prompt_error_analysis_synthesis.md` §5 (evidence as a first-class target).

### v4 ladder vs iteration driver

```text
previous_exect_error_analysis.md
        │
        ▼
prior_prompt_error_analysis_synthesis.md
        │
        ├──────────────────┐
        ▼                  ▼
exect_gold_label_audit   full-validation FP clusters
        │                  │
        ▼                  ▼
   v2 audited surfaces   regression slice (12→23 records)
        │
        ▼
   v3–v4 bridges (splits, secondary gen, symptomatic focal)
        │
        ▼
   v4.2 seizure coarse + medication FP guards
        │
        ▼
   v4.3 medication + evidence
        │
        ▼
   v4.4 diagnosis co-list (generic epilepsy, focal/focal onset)
```

**Iteration driver:** `data/fixtures/exect_s0_label_policy_error_regression_slice.json` grew from v3/v4.2 **full-validation failure modes**, not from the old analysis §8 case list.

**Documentation gap:** v4.x implementation notes do not cite `previous_exect_error_analysis.md`; only the synthesis doc does.

### Headline metrics (v4.4 full validation, 40 records)

| Metric | v4.4 | v4.3 | Delta |
| --- | ---: | ---: | ---: |
| Micro F1 | **82.0%** | 79.8% | +2.2pp |
| Diagnosis F1 | **79.5%** | 74.3% | +5.2pp |
| Seizure F1 | **76.8%** | 74.7% | +2.1pp |
| Medication F1 | 89.4% | 89.4% | 0 |
| Evidence support | 94.1% | 94.1% | 0 |

Scorer unchanged: `exect_field_family_deterministic_v1`.

Source: `docs/experiments/exect/exect_s0_label_policy_v4_4_implementation.md`, run `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T210602Z`.

### Canonical cases (§8) under v4.4

| Record | Old failure mode | Current gold (audited) | v4.4 prediction | Status |
| --- | --- | --- | --- | --- |
| EA0008 | ILAE seizure label; `symptomatic` diagnosis | `symptomatic structural focal epilepsy`; `focal seizures with altered awareness`; `lamotrigine` | Diagnosis + seizure **match**; medication **empty** | Seizure/diag **fixed** vs old sweep; med **FN** |
| EA0016 | Inferred `focal epilepsy` from single event | `[]` diag; `focal seizure` | `[]` diag; `focal seizure` | **Fixed** |
| EA0052 | Seizure inferred from diagnosis header | `temporal lobe epilepsy`; no seizure types | Same | **Fixed** |
| EA0045 | ILAE + secondary as separate types | Rich surfaces incl. `focal to bilateral convulsive seizures` | Matches gold | **Fixed** (under current gold) |
| EA0148 | Triple ILAE vs single `focal seizure` | `epilepsy`; no seizure types | Empty | **Diagnosis FN** (`epilepsy`) |
| EA0090 | Secondary generalisation handling | Three-way seizure split | Three-way split | **Fixed** |

Records **not** in the 23-record regression slice but central in the old analysis: **EA0008** (medication), **EA0016**, **EA0148**.

### Residual failure families (full v4.4 validation)

From `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T210602Z/metrics.json` field-family mismatches:

1. **Generic `epilepsy` false negatives** — EA0131, EA0148, EA0150, EA0170, EA0173, EA0174 (v4.4 co-list did not fully close this).
2. **Granular JME / myoclonic descriptors** — `myoclonic seizures` false positives where gold uses specificity collapse (EA0029, EA0050, EA0125).
3. **Specificity-collapse diagnosis** — EA0188 still misses `focal`, `drug`, `occipital` while over-predicting rich seizure phrases.
4. **Medication** — EA0008 `lamotrigine` FN; EA0052 `carbamazepine` FN (planned-switch exclusion); EA0078 historical over-prediction.
5. **Evidence** — missing spans or unsupported quotes on several records (diagnostic, not in field F1).

v4.4 implementation “next” item (JME tonic-clonic vs myoclonic coarsening) aligns with (2).

## Interpretation

### What was preserved from the prior analysis

The old document’s **mechanistic** claims remain valid and are reflected in current engineering:

1. Seizure and diagnosis errors are often **label-policy** failures before model-capability failures.
2. **Few-shot mapping examples** and allowed-label surfaces strongly steer benchmark behavior.
3. **Null diagnosis** for single events and **no seizure-from-diagnosis** are high-leverage rules.
4. Evidence and medication scope need explicit policy, not implicit clinical reasoning.

Under **audited** gold, several canonical §8 cases now pass on GPT 4.1-mini v4.4 where the primary sweep failed—using **richer** surfaces than the old doc recommended.

### What was deliberately not preserved

| Old prescription | Why not |
| --- | --- |
| Coarse remap `focal impaired awareness` → `focal seizure` | Current gold uses modifier-rich plural surfaces |
| `symptomatic` → `focal epilepsy` | Scorer expects full `symptomatic structural focal epilepsy` for EA0008 |
| Five-label diagnosis constraint | Collides with multi-label audited diagnoses and specificity-collapse flags |
| “Do not split secondary generalisation” (unqualified) | Audited gold **requires** split for fused phrases (EA0090) |

These are **contract changes**, not forgotten lessons.

### Where drift risk is real

1. **No explicit traceability table** in v4.x implementation docs back to `previous_exect_error_analysis.md` §7.
2. **Regression slice ≠ canonical catalog** — slice grew from recent FPs; EA0016 is fixed but ungated; EA0148 still fails but is absent from the main slice.
3. **Closed negative paths** (diagnosis-recall v1, verify-repair) are documented; **positive** mapping from old analysis to v4.4 is not.
4. **Model family changed** — old analysis is Qwen/Gemini primary sweep; v4 ladder is GPT 4.1-mini; pattern transfer is plausible but not re-measured on Qwen for the same policy.

## Caveats

- Metrics are **partial ExECT S0/S1** (diagnosis, seizure type, annotated medication only), not published ExECTv2 benchmark reproduction.
- Cap-25 runs remain optimistic vs full validation (documented in v4.2/v4.3 implementation notes).
- `previous_exect_error_analysis.md` references `src/clinical_extraction/labels.py` and `BENCHMARK_SEIZURE_LABELS`; that module does not exist in the current tree—label control is prompt + bridges + canonicalization.
- Do not compare ExECT micro F1 to Gan monthly-frequency metrics (different scorers and tasks).

## Recommendations

### Documentation

1. Link this report from `docs/experiments/exect/exect_s0_label_policy_v4_4_implementation.md` under a “Prior analysis traceability” subsection.
2. When closing v4.5+ work, update the § “Round 2 traceability” table with done/open/inverted status.

### Regression governance

Add **canonical anchors** to `data/fixtures/exect_s0_label_policy_error_regression_slice.json` even when temporarily green:

| Record | Failure mode to guard |
| --- | --- |
| EA0008 | Rich seizure/diag surfaces + prescription medication |
| EA0016 | Single-event null diagnosis |
| EA0148 | Generic `epilepsy` co-list |
| EA0131 | `epilepsy` + `primary generalized epilepsy` co-list |

### Next experiments (bounded)

1. Tighten **generic epilepsy** co-list triggers (note-gated; avoid recall-probe-style FPs).
2. **JME / myoclonic** coarse-surface hypothesis (already flagged in v4.4 implementation doc).
3. **EA0008 medication** — reconcile prescription markup (“to reduce”) with planned-medication exclusion policy.
4. **Specificity-collapse co-list** for diagnosis (EA0188 pattern) via prompt/bridge, not a blind second LLM pass.

### Do not do without scorer + audit change

- Reintroduce coarse ILAE → `focal seizure` mapping.
- Collapse `symptomatic structural focal epilepsy` → `focal epilepsy`.
- Adopt five-label diagnosis-only surface for benchmark scoring.

## Related artifacts

| Artifact | Path |
| --- | --- |
| Prior ExECT error analysis | `docs/archive/prior-context/previous_exect_error_analysis.md` |
| Cross-project synthesis | `docs/archive/prior-context/prior_prompt_error_analysis_synthesis.md` |
| Gold audit | `docs/datasets/exect/exect_gold_label_audit.md` |
| v4.4 implementation | `docs/experiments/exect/exect_s0_label_policy_v4_4_implementation.md` |
| v4.4 full validation run | `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T210602Z` |
| Regression slice fixture | `data/fixtures/exect_s0_label_policy_error_regression_slice.json` |
| Program / policy source | `src/clinical_extraction/programs/exect_s0_s1.py` |

## Conclusion

The project **did not** discard `docs/archive/prior-context/previous_exect_error_analysis.md`. Its behavioral insights are embedded in the v4 label-policy program, and several §8 canonical cases **pass** under audited gold on v4.4. The project **did** supersede the old document’s **literal** label-collapse prescriptions after aligning to `exect_gold_label_audit.md` and the field-family scorer.

v4.4 is best understood as a **diagnosis-recall** patch on the new contract (co-list `epilepsy`, focal/focal onset), not a reimplementation of the 2026-05-16 Round 2 checklist. The operational risk is slice-driven promotion without systematically gating the historical canonical case list—addressable by expanding the regression fixture and maintaining this traceability report.

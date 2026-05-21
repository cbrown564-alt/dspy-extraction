# ExECT S1–S3 Residual Qualitative Queue and Cross-Level Taxonomy

Date: 2026-05-21  
Status: No-model operational synthesis (Phase 5d-a queued work)  
Decision scope: `operational` — regression-guard and prereg inputs only; does not mechanism-close staged extraction, bridges, pre-vocab, verification, or sparse-family repair.  
Sources:

- `docs/experiments/exect/exect_s1_residual_error_analysis_20260521.md` — anchor `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z`
- `docs/experiments/exect/exect_s2_residual_error_analysis_20260521.md` — anchor `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z`
- `docs/experiments/exect/exect_s3_residual_error_analysis_20260521.md` — anchor `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z`
- S4 alignment: `docs/experiments/exect/exect_s4_sparse_family_surface_policy_20260521.md`, `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`

## Purpose

Complete Phase **5d-a** queued no-model work: per-level qualitative tags on preregistered document queues, merged into a cross-level residual taxonomy for hybrid-program and Axis 3 prereg design.

Use this doc when:

- scoping narrow guards (seizure modifier, medication precision, comorbidity surface policy);
- protecting regression families as schemas widen (S2 → S3 → S4);
- tagging S4 sparse-family bridge fixtures (overlap with S3 queue docs).

Do **not** use pooled ladder micro F1 as a single optimization objective across S1–S4.

---

## Cross-level residual taxonomy

Apply **one primary tag** per labeled atom (FP or FN). Add a secondary tag only when two mechanisms are equally responsible.

| Tag | Definition | Typical families | Mechanism implication |
| --- | --- | --- | --- |
| `scorer-surface` | Clinically plausible output; exact audited label string differs (spelling, British/American, plural, legacy vs modern term). | seizure_type, comorbidity, cause, birth_history | Narrow canonicalization or CUIPhrase bridge; not broad semantic repair. |
| `atomization` | Model emits composite or expanded phrase; gold uses atomized PatientHistory / cause labels (or reverse). | comorbidity, epilepsy_cause | Post surface policy or atomized-label bridge; avoid free-form composite extraction. |
| `over-specificity` | Model label is clinically richer or more specific than gold allows. | diagnosis, seizure_type, epilepsy_cause | Negative guard or benchmark-facing collapse policy; recall-boost prompts risk new FPs. |
| `uncertainty-leakage` | Differential, historical, or uncertain wording becomes a scored label. | seizure_type, comorbidity (psychiatric symptoms) | Narrow negative guard; do not reopen rejected static pre-vocab without new variant ID. |
| `timing-slot-leakage` | Age, date, or “since …” phrasing scored in the wrong family (often seizure_type or when_diagnosed). | seizure_type, when_diagnosed, onset | Family-boundary policy; sparse slots need annotation-faithful bridges before model sweeps. |
| `cross-family-overlap` | Same phrase valid in multiple gold families; model placement differs from audited view. | cause, comorbidity, birth_history, onset | Bridge per family; scorer overlap policy unchanged without audit. |
| `over-extraction` | Extra label in family scope without `missing_gold` (includes non-ASM medication, out-of-scope investigation modality). | annotated_medication, investigation, comorbidity | Precision guard tier; separate from sparse-surface policy. |
| `missing-evidence` | Label may match clinically but evidence span missing or unsupported (diagnostic; may co-occur with match). | all high-support | Selector for review only; not a global abstention filter without prereg. |
| `gold-quality-caveat` | `missing_gold` or `specificity_collapsed`; not fair evidence of model failure. | annotated_medication, diagnosis, investigation | Document in inspection; exclude from guard training signals. |

**S4 sparse-family memo alignment:** `scorer-surface` and `atomization` justify annotation-faithful CUIPhrase bridges; `over-specificity` / `clinical-semantics` beyond gold may stay out of scope under that policy.

---

## S1 qualitative queue (GPT v4.10 full validation)

**Queue documents:** EA0143, EA0136, EA0072, EA0174, EA0179, EA0125  
**Anchor:** `runs/exect_s0_s1_validation_full_gpt4_1_mini_20260519T221944Z` (92.3% micro)

| Doc | Family | Error | Tag | Notes |
| --- | --- | --- | --- | --- |
| EA0143 | diagnosis | FP `symptomatic structural focal epilepsy` | over-specificity | Rich clinical diagnosis vs absent specific gold |
| EA0143 | seizure_type | FP `focal seizures with altered awareness`; FN `focal` | scorer-surface | Modernized term vs sparse gold surface |
| EA0143 | annotated_medication | FP `lamotrigine` | over-extraction | Scope beyond annotated prescription gold |
| EA0136 | annotated_medication | FP `carbamazepine`, `sodium valproate`; FN `epilim chrono` | scorer-surface | Brand/generic split; gold brand form missed |
| EA0072 | seizure_type | FP `secondary`; FN `focal motor seizure` | uncertainty-leakage + scorer-surface | Generic modifier replaces specific gold label |
| EA0174 | seizure_type | FP descriptive shaking span; FN `epileptic seizures` | scorer-surface | Clinical span vs broad gold |
| EA0179 | seizure_type | FP `complex partial seizures` | uncertainty-leakage | Differential/history language → label |
| EA0125 | diagnosis | FN `jme` | gold-quality-caveat | `specificity_collapsed` on gold |

**S1 queue read:** Cross-family boundary case (EA0143) plus seizure modifier leakage (EA0072, EA0179). Medication (EA0136) is a narrow brand/surface repair candidate only. No justification for broad S1 validation retuning.

---

## S2 qualitative queue (GPT v1.3 full validation)

**Queue documents:** EA0150, EA0179, EA0170, EA0136, EA0090, EA0148, EA0188  
**Anchor:** `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` (80.9% micro)

| Doc | Family | Error | Tag | Notes |
| --- | --- | --- | --- | --- |
| EA0150 | comorbidity | FP composites (`traumatic brain injury`, …); FN atomized trauma labels | atomization | Semantically close; scorer rewards atomized gold |
| EA0150 | seizure_type | FP modernized focal/bilateral labels; FN legacy `complex partial` / `secondary` | scorer-surface | Inherited S1 drift in five-family pass |
| EA0150 | diagnosis | FN `epilepsy` | scorer-surface | Generic gold omitted |
| EA0179 | comorbidity | FN episode/syncope/febrile block | scorer-surface | Large recall miss on PatientHistory surfaces |
| EA0179 | seizure_type | (see S1) differential FP | uncertainty-leakage | Same pattern as S1 |
| EA0179 | investigation | FN `eeg unknown` | scorer-surface | Unknown-result policy edge |
| EA0170 | comorbidity | FP/FN cerebrovascular wording variants | scorer-surface | British/American and plural mismatch |
| EA0170 | seizure_type | specificity FP/FN | scorer-surface | Co-occurring with comorbidity surfaces |
| EA0136 | annotated_medication | FP `carbamazepine`, typo `eplim chrono` | scorer-surface | Brand typo + extra ASM |
| EA0136 | seizure_type | legacy vs modernized labels | scorer-surface | Same as S1 EA0136 pattern |
| EA0090 | seizure_type | plural/multi-label FP/FN | scorer-surface + atomization | Multi-label gold vs single modernized output |
| EA0090 | comorbidity | FP `headache` | over-extraction | Symptom outside gold comorbidity set |
| EA0148 | comorbidity | FP reflux/smoking; FN `head injuries` | scorer-surface | Scope and surface mismatch |
| EA0188 | diagnosis | FN `occipital lobe epilepsy` | gold-quality-caveat | `specificity_collapsed` |
| EA0188 | investigation | FN `eeg abnormal` | gold-quality-caveat + scorer-surface | Collapsed gold + recall miss |
| EA0188 | comorbidity | mixed FP/FN | scorer-surface | Secondary to investigation/diagnosis caveats |

**S2 queue read:** EA0150 is the canonical cross-family read (comorbidity atomization + seizure modernization). Comorbidity surface policy is the highest-value S2-specific prereg target; investigation `unknown` and ECG out-of-scope are regression guards for wider schemas.

---

## S3 qualitative queue (GPT v1.2 full validation)

**Queue documents:** EA0150, EA0016, EA0137, EA0179, EA0143, EA0188, EA0136  
**Anchor:** `runs/exect_s3_validation_full_gpt4_1_mini_20260519T235439Z` (72.1% micro)

| Doc | Family | Error | Tag | Notes |
| --- | --- | --- | --- | --- |
| EA0150 | comorbidity / cause / when_diagnosed | trauma atomization; timing `epilepsy` FPs | atomization + timing-slot-leakage | Full cross-family burden; overlaps S4 queue |
| EA0150 | seizure_type / diagnosis / medication | (inherits S2 patterns) | scorer-surface + over-extraction | Medication precision degrades in nine-family pass |
| EA0016 | comorbidity | FP `cva`/`hemiparesis` prose; FN abbreviations | scorer-surface + atomization | Stroke surface variants |
| EA0016 | seizure_type | FP `focal seizures with altered awareness` | scorer-surface | Same modernized-label pattern |
| EA0016 | annotated_medication | (precision FPs in run) | over-extraction | Non-ASM leakage in wider pass |
| EA0137 | birth_history / cause / onset | perinatal overlap; FN hypoxia labels | cross-family-overlap | Cause vs birth_history boundary |
| EA0137 | onset | FP `epilepsy` (typical pattern) | timing-slot-leakage | Gold uses diagnosis-like CUIPhrase |
| EA0137 | seizure_type | FP `secondary`; FN diagnosis `epilepsy` | uncertainty-leakage + scorer-surface | S1 patterns persist |
| EA0179 | comorbidity | FN recall block; FP `mild learning disabilities` | scorer-surface | Specificity vs gold wording |
| EA0179 | seizure_type / investigation | (as S2) | uncertainty-leakage + scorer-surface | Regression guard families |
| EA0143 | seizure_type | FP altered awareness + `seizures started at age 19` | timing-slot-leakage | Onset phrase in seizure_type |
| EA0143 | when_diagnosed / cause | timing and cause FPs | timing-slot-leakage + scorer-surface | Overlaps S4 EA0143 read |
| EA0188 | birth_history / onset | paraphrase FPs vs gold | scorer-surface | Sparse-family surface mismatch |
| EA0188 | diagnosis / comorbidity | (as S2) | gold-quality-caveat + scorer-surface | |
| EA0136 | medication / seizure / comorbidity | (as S2) | scorer-surface | No S3-only medication policy win |

**S3 queue read:** High-support drift (comorbidity, medication precision) dominates; sparse families (onset, when_diagnosed, cause, birth) are annotation-surface-bound with heavy overlap. EA0150, EA0016, EA0137 are shared with S4 qualitative queue — use one tagged read for sparse-family bridge design.

---

## Cross-level patterns (merged tags)

| Pattern | Levels | Primary tags | Documents (shared) | Recommended handling |
| --- | --- | --- | --- | --- |
| Seizure generic `secondary` / differential leakage | S1–S4 | uncertainty-leakage, scorer-surface | EA0072, EA0137, EA0179 | Narrow negative guard; new variant ID if modeled |
| Modernized vs legacy seizure labels | S1–S4 | scorer-surface | EA0150, EA0016, EA0090, EA0143 | Regression guard in wider prompts; not static pre-vocab rerun |
| Comorbidity atomization vs composites | S2–S4 | atomization | EA0150, EA0170, EA0148 | Comorbidity surface-policy prereg (S2-led) |
| Medication brand/generic and scope | S1–S4 | scorer-surface, over-extraction | EA0136, EA0143, EA0052 | Narrow spelling/brand repair; S4 MT guard separate track |
| Diagnosis specificity / collapsed gold | S1–S3 | over-specificity, gold-quality-caveat | EA0125, EA0143, EA0188 | Do not broad-recall boost |
| Investigation modality/unknown/ECG | S2–S4 | over-extraction, scorer-surface | EA0179, EA0188, EA0016 | Regression guard after v1.2 repair |
| Sparse timing slots (`epilepsy` as when_diagnosed/onset) | S3–S4 | timing-slot-leakage, scorer-surface | EA0137, EA0143, EA0150 | Policy memo + CUIPhrase bridges before cap-25 sweeps |
| Cause/comorbidity/birth overlap | S3–S4 | cross-family-overlap, atomization | EA0016, EA0137, EA0150 | First bridge: `epilepsy_cause` per sparse-family policy |
| Missing-gold medication outputs | S1–S2 | gold-quality-caveat | EA0078, EA0100 | Exclude from precision-guard training |

---

## Hybrid-program implications

| Residual class | Ladder levels | Axis | Action |
| --- | --- | --- | --- |
| S1 near-ceiling residuals | S1 | — | Qualitative regression queue only; no broad prompt churn |
| Comorbidity surface/atomization | S2–S4 | 3 (no-model → narrow prereg) | Surface policy before model budget |
| Medication precision drift | S3–S4 | 3 | Guards only; S1 medication pre-vocab remains rejected |
| Investigation regression | S2–S4 | — | Freeze as guard in any wider schema or staged graph |
| Sparse annotation-surface families | S3–S4 | — / 3 | Bridges per `exect_s4_sparse_family_surface_policy_20260521.md` |
| Seizure legacy surfaces | S1–S4 | 3 | Negative guards; do not reopen E3–E5 pre-vocab arms |

**Targeted action designs (2026-05-21):** see `docs/experiments/exect/exect_s1_s3_residual_targeted_actions_20260521.md` for prereg IDs, tiers, and execution order.

**Explicit non-goals:** mechanism-close bridge placement, verify-repair, candidate presentation, or “S3 prompt fixes pooled micro” from this taxonomy alone.

---

## Links to S4 queue

S4 representative queue (`docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`): EA0150, EA0016, EA0137, EA0143, EA0059, EA0052, EA0136, EA0153, EA0109, EA0179.

**Overlap with S3 queue (tag once, reuse):** EA0150, EA0016, EA0137, EA0143, EA0136, EA0179. Extend S4-only reads: EA0059 (frequency multi-surface), EA0052, EA0153, EA0109.

---

## Open cells

- Record-level evidence quotes for queue docs (optional deep read; not required for prereg scaffolds).
- Fixture tests per tag class for first `epilepsy_cause` bridge.
- Qwen track tags on same document IDs (separate model profile; seizure gap larger at S1).

## References

- Implementation plan §5d-a: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md`
- Mechanism status: `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`

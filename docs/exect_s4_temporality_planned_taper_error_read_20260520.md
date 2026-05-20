# ExECT S4 Medication-Temporality — Planned/Taper Slice Error Read

Date: 2026-05-20  
Comparison group: `exect_s4_temporality_deterministic_v1`  
Inspection anchor: `docs/exect_s4_temporality_deterministic_gpt_inspection_20260520.md`  
Analysis artifact: `runs/exect_s4_temporality_planned_taper_error_read_20260520.json`  
Regenerate: `uv run python scripts/analyze_exect_s4_temporality_error_read.py --l1-run runs/exect_s4_temporality_l1_baseline_full_gpt4_1_mini_20260520T204207Z --h1-run runs/exect_s4_temporality_h1_post_classifier_full_gpt4_1_mini_20260520T204216Z --output runs/exect_s4_temporality_planned_taper_error_read_20260520.json`

## Scope

This note diagnoses the full-validation recall collapse that caused **H1 reject** (+10.1pp MT precision, −6.6pp MT F1). The kanban optional next step was a planned/taper phrase slice read on H1 false negatives before any classifier retune.

Grounding:

- Scorer: `exect_s4_field_family_deterministic_v1` (unchanged between arms)
- Primitive: `exect.medication_temporality.post_classifier.v1`
- Gold: medication temporality inferred from annotated Prescription span text (`docs/exect_s4_gold_policy.md`)
- Full-validation runs: L1 `…204207Z`, H1 `…204216Z` (40 records)

## Metrics snapshot

| Arm | MT precision | MT F1 | MT recall |
| --- | ---: | ---: | ---: |
| L1 baseline | 46.4% | 62.5% | 95.7% |
| H1 post classifier | 56.5% | 55.9% | 55.3% |

H1 introduced **19 new false negatives** (gold labels L1 matched but H1 dropped) and **37 precision wins** (L1 false positives H1 removed).

## Main finding

**Recall collapse is not primarily a planned/taper boundary bug.** Only **4 of 19** new FNs sit in a planned/taper phrase slice, and **zero** are taper-on-current-prescription-line cases (the policy case covered by `test_exect_medication_temporality_distinguishes_current_planned_previous_and_taper`).

The dominant failure mode is **unknown-abstention on dose-only ASM evidence** (17/19 new FNs): H1 drops predictions when the aligned evidence quote lacks explicit current/planned/previous markers, even when L1 emitted `medication|current` and gold agrees.

| Failure mode | Count (of 19 new FNs) | Interpretation |
| --- | ---: | --- |
| Dose-only / missing temporality cue in evidence | 12 | e.g. `lamotrigine 150 milligrams twice a day` → inferred `unknown` → dropped |
| Planned/taper note or evidence cue | 4 | Includes titration schedules and one misclassified “already started” previous cue |
| Status misclassification | 2 | `previous` inferred where gold is `current` (EA0150 clobazam, EA0179 sodium valproate) |
| Empty or mismatched evidence quote | 1 | EA0150 clobazam — no aligned quote; note-level previous cue fired |

Cue bucket counts on new FNs: `no_cue` 13, `planned` 3, `current` 2, `taper` 1.

## Planned/taper slice (4 records)

These are the cases the support map flagged for phrase-boundary inspection. None justify a taper-specific retune.

| Doc | Gold | Evidence (L1 quote) | H1 drop reason |
| --- | --- | --- | --- |
| EA0026 | `topiramate\|current` | `topiramate 100 mg twice a day` | Dose-only → `unknown` removed; `planned` appears elsewhere in note, not in quote |
| EA0116 | `levetiracetam\|current` | Titration schedule (`…increasing by 250mgs every 2 weeks…`) | No planned marker match; inferred `unknown` |
| EA0124 | `zonisamide\|current` | `Zonisamide 50mg bd` | Taper language elsewhere in note; quote is dose-only → `unknown` |
| EA0179 | `sodium valproate\|current` | `He has already been started on sodium valproate 300mg bd…` | Misclassified as `previous` (`started` matched previous markers) |

**Taper-on-current policy is not implicated.** EA0008-style lines (`current … to reduce and stop as detailed below`) were not among H1 new FNs on full validation.

## Representative dose-only recall losses

H1 removed true positives where L1 trusted model-assigned `|current` on prescription-style dose lines:

- EA0029: `lamotrigine 150 milligrams twice a day`, `Keppra 1000 milligrams twice a day`
- EA0059: `Lamotrigine 200mg bd`
- EA0069: `Lamotrigine 50mg am…`, `Levetiracetam 1500mg bd`
- EA0102: `She does continue to take sodium valproate 200 milligrammes twice a day` (no `_CURRENT_MARKERS` match)
- EA0137: `She is now taking 50mg twice a day` (`is now taking` not in marker list)
- EA0188: `Brivitiracetam 50mg bd`, `Zonismaide 100mg bd`

These account for most of the −40.4pp recall delta (95.7% → 55.3%).

## Precision wins (37 removals)

H1 precision gains are largely legitimate:

| Category | Count | Examples |
| --- | ---: | --- |
| Non-ASM removed | 19 | simvastatin, aspirin, thyroxine, insulin, citalopram |
| Previous/planned FP removed | 16 | `levetiracetam\|previous` on narrative switches, `carbamazepine\|planned` on historical trials |
| Other ASM status cleanup | 2 | Duplicate brand (`eplim\|current` when sodium valproate scored), dose-only current on wrong medication |

The classifier is doing useful FP pruning; the reject outcome is driven by **over-aggressive unknown abstention**, not by planned/taper over-pruning.

## Decision

| Question | Answer |
| --- | --- |
| Is planned/taper retune the right next step? | **No** — only 4/19 new FNs; 0 taper-on-current failures |
| What caused full-validation reject? | Unknown-drop on dose-only ASM evidence where model status was correct |
| Should H1 be promoted or retuned? | **Keep rejected** — do not wire into default S4 recovery |
| If revisiting H1, what to change? | Soften unknown policy: preserve model-assigned `current` on ASM dose-only prescription lines; expand current markers (`is now taking`, `continue to take`, titration-on-current-Rx); do **not** narrow taper rules first |

## Recommended next work

1. **No classifier retune** until a revised abstention policy is pre-registered (model-status fallback on ASM dose lines).
2. Keep L1 frozen as ExECT S4 GPT default (`docs/kanban_plan.md`).
3. Use registry matrix for methods drafting; no new model-backed S4 family probe unless abstention policy changes.

## Validation

- Analysis script: `scripts/analyze_exect_s4_temporality_error_read.py`
- Artifact JSON: `runs/exect_s4_temporality_planned_taper_error_read_20260520.json`
- Existing primitive tests unchanged; no scorer semantics changed

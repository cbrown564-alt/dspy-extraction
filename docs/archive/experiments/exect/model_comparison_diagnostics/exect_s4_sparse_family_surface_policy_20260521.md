# ExECT S4 Sparse-Family Annotation Surface Policy

Date: 2026-05-21  
Status: Policy memo — gates hybrid-plan item 24 model spend  
Parent plan: `docs/workstreams/hybrid/hybrid_pipeline_exploration_implementation_plan_20260521.md` (Phase 5d queue item 3)  
Evidence: `docs/experiments/exect/exect_s4_residual_error_analysis_20260521.md`  
decision_scope: **operational** (research policy, not mechanism closure)

## Question

How should ExECT S4 treat `onset`, `when_diagnosed`, `epilepsy_cause`, and `birth_history` when the model emits clinically plausible prose but gold uses sparse CUIPhrase-like annotation surfaces?

## Decision (effective 2026-05-21)

**Adopt annotation-faithful extraction with deterministic CUIPhrase-surface bridges as the default path.** Do not spend cap-25 model budget on these four families until at least one bridge scaffold exists and is preregistered. Full ontology/CUI Table 1 reproduction remains deferred to Card 19.

| Path | Status | Rationale |
| --- | --- | --- |
| **Annotation-faithful + post bridges** | **Selected** | Matches Card 18 string-surface diagnostics, S3 overlap policy, and existing S1/S4 bridge pattern |
| Clinically normalized free-text outputs | Rejected as primary objective | Conflicts with audited gold loaders; unstable scorer without explicit canonicalization tables |
| Defer all sparse-family work until CUI reproduction | Partial — for ontology only | CUIPhrase-surface bridges are in scope now; UMLS/CUI graph lookup is not |

This is **not** a claim that sparse families are solved. It fixes the **target surface** before any Axis 3 sweep.

## Families and target surfaces

Gold sources and normalization follow `docs/experiments/exect/exect_s3_phase1_overlap_policy.md` and `docs/datasets/exect/exect_gold_label_audit.md`.

| Family | Validation support (GPT full) | Gold surface | Typical model failure | Bridge vs prompt |
| --- | ---: | --- | --- | --- |
| `onset` | 3 | Affirmed `Onset` CUIPhrase (`epilepsy`, seizure-type phrases) | Ages/dates (`teenage years`, `10 months ago`) | **Bridge-first** — map note cues to audited CUIPhrase set |
| `when_diagnosed` | 4 | Affirmed `WhenDiagnosed` CUIPhrase (often `epilepsy`) | Visit dates, ages, clinic phrases | **Bridge-first** — same slot policy as onset |
| `epilepsy_cause` | 7 | Affirmed `EpilepsyCause` CUIPhrase | Near-synonym surfaces (`stroke`/`strokes`, `traumatic`/`traumatic brain injury`) | **Bridge-first** — audited synonym/plural normalization |
| `birth_history` | 8 | Affirmed `BirthHistory` CUIPhrase | Paraphrase/granularity (`his birth was normal` vs `birth was normal`) | **Bridge-first** — surface canonicalization + negation handling |

Age, year, and `TimePeriod` JSON attributes are **not** benchmark labels in the current phase (S3 Phase 1 policy).

## Overlap rules (unchanged)

Families score independently per `exect_s3_phase1_overlap_policy.md`:

- Same phrase may appear in `diagnosis`, `onset`, `when_diagnosed`, `epilepsy_cause`, and `comorbidity`.
- Bridges must **not** deduplicate across families.
- Extraction policy: prefer slot-appropriate surfaces when note framing supports it; duplicate predictions across families remain valid until prompt policy narrows scope.

## Metrics and gates

Do **not** use pooled S4 micro F1 as the primary objective for sparse-family work.

| Metric | Role |
| --- | --- |
| Per-family F1 on full validation (40) | Primary when support ≥ 8 labels on split |
| Qualitative error-read queue | Required when support < 8 |
| Pooled S4 micro | Diagnostic only — unstable and confounded by high-support families |
| Evidence quote support | Gate ≥ 85% if model-facing changes are tested |

Promotion gate for any sparse-family **model** variant: ≥ +3pp family F1 on full validation vs frozen v1.2 baseline **or** qualitative clearance on preregistered queue with no ≥2pp regression on frozen medication/frequency/investigation families.

## Mechanism placement (Axis 3 order)

1. **Deterministic CUIPhrase bridges** (`exect.*.cui_phrase_bridge.v1`, planned in taxonomy catalog) — post-module, same interleaving lane as S1 inline bridges.
2. **Prompt/example policy** — only after bridge baseline exists; new `implementation_variant` IDs required.
3. **No verify-repair second pass** on sparse families until a winning single-pass bridge is identified.

Do **not** rerun H2 pre-vocab or broad post-merge patterns from frequency/medication negative probes.

## Qualitative queue (cross-family reads)

Use these documents for error tagging before any sparse-family prereg:

| Document | FP+FN | Primary read |
| --- | ---: | --- |
| EA0150 | 17 | Cross-family scope; when_diagnosed + frequency + temporality |
| EA0016 | 15 | Onset + cause + medication scope |
| EA0137 | 13 | Birth + onset + when_diagnosed overlap |
| EA0143 | 13 | When_diagnosed + cause + frequency |
| EA0059 | 12 | Cause + frequency multi-surface |

Extended queue: EA0052, EA0136, EA0153, EA0109, EA0179.

Tag each residual as: **scorer-surface**, **clinical-semantics**, **over-extraction**, or **missing-evidence**. Scorer-surface tags justify bridge work; clinical-semantics tags may remain out of scope under annotation-faithful policy. Cross-level ladder tags (S1–S3) and shared queue docs: `docs/experiments/exect/exect_s1_s3_residual_qualitative_queue_and_taxonomy_20260521.md`.

## Explicit non-goals

- Not Gan monthly frequency normalization
- Not ExECTv2 Table 1 / CUI-feature reproduction (Card 19)
- Not pooled-S4-driven prompt sweeps on 3–8 label families
- Not mechanism closure for “sparse S4 families are unsolvable” from current null F1 alone

## Unblocks hybrid plan

With this memo recorded:

- Item 24 **model spend** stays deferred until bridge scaffolds are preregistered.
- **Bridge design + fixture tests** for `epilepsy_cause` and `birth_history` may proceed without model calls (parallel-safe).
- Frequency (`seizure_frequency`) and medication temporality tracks remain independent and higher priority.

## Open cells

- Which family gets the first bridge scaffold (recommend `epilepsy_cause` — highest support, clearest synonym table)
- Whether onset/when_diagnosed share one bridge primitive or split by entity type
- Card 19 timeline for full CUI reproduction vs local string-surface ladder

## References

- `docs/taxonomy/taxonomy_ontology_cui_scope_decision_20260520.md`
- `docs/experiments/exect/exect_s4_gold_policy.md`
- `docs/experiments/exect/exect_s4_medication_precision_guard_design_20260521.md` (high-support parallel track)

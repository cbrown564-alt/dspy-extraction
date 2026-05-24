# Experiment Inspection Draft

**Topic:** No-model ExECT S4/S5 seizure-frequency gold-template audit  
**Status:** Review-only draft — audit not executed; no run directory supplied  
**Kanban card:** `S4/S5 frequency gold-template audit` (`docs/planning/kanban_plan.md`, Ready)  
**Decision scopes preserved:** operational · arm · mechanism · open · blocked · stale_check  
**Evidence tier:** This draft is guidance only. It does not constitute benchmark evidence or a paper claim unless backed by primary audit artifacts listed under Required Inputs.

---

## Scope

| Dimension | Value |
| --- | --- |
| **Dataset** | ExECTv2 (`data/raw/exect_v2/` per loader; policy doc also references `data/ExECTv2 (2025)/`) |
| **Split** | `exectv2_fixed_v1` — validation 40, test 40, train 120 (`data/splits/exectv2_splits.json`) |
| **Model / provider** | **None** — no-model deterministic audit |
| **Schema level / field group** | `seizure_frequency` only (S4 family; included in S5 core surface) |
| **DSPy program variant** | **None** — audit compares gold loader output vs note-anchored candidate primitives |
| **Scorer mode** | Gold reference: `canonical_seizure_frequency_label` → `load_exect_gold_document` (`src/clinical_extraction/datasets/exect.py`); S4 scorer `exect_s4_field_family_deterministic_v1`; S5 scorer `exect_s5_core_field_family_deterministic_v1` (`docs/experiments/exect/exect_s5_core_surface_design_20260524.md`) |
| **Normalization rules** | Gold: S4 policy in `docs/experiments/exect/exect_s4_gold_policy.md` and `canonical_seizure_frequency_label` (`exect.py:308–336`); candidates: `_build_exect_frequency_label_set` + `repair_exect_frequency_surface` (`primitives.py:1486–1560`, `1291–1311`) |
| **Evidence policy** | Diagnostic only; candidates carry `source_span_text` / optional char offsets; benchmark F1 does not require evidence quotes (`docs/policies/deterministic_scorer_semantics.md`; `primitives.py:1255–1259`) |
| **Comparison group** | **Not yet defined** — this is pre-arm audit gating E5/E6 (`docs/planning/kanban_plan.md` Backlog) |

**Audit question (from Kanban):** Can validation-gold seizure-frequency labels be represented by deterministic, note-anchored candidate surfaces *before* candidate-adjudication or structured-slot model arms?

---

## Sources Read

| Path | Role |
| --- | --- |
| `docs/planning/kanban_plan.md` | Active card definition, E4 completion, E5/E6 deferral gates |
| `docs/datasets/exect/exect_gold_label_audit.md` | Historical Bug 1 (frequency ≠ seizure type), Q4 multi-type frequency |
| `docs/experiments/exect/exect_s4_gold_policy.md` | Gold normalization taxonomy, multi-row policy, scorer caveats |
| `docs/experiments/exect/exect_s5_core_surface_design_20260524.md` | S5 inclusion of `seizure_frequency`, support counts, regression guards |
| `src/clinical_extraction/datasets/exect.py` | Gold loader, `canonical_seizure_frequency_label`, quality flags |
| `src/clinical_extraction/exect/primitives.py` | `build_exect_frequency_candidate_payloads`, bridge/recovery, audited template gate |
| `data/splits/exectv2_splits.json` | Split IDs and policy |
| `docs/templates/experiment_decision_template.md` | Decision doc shape reference |
| `docs/policies/deterministic_scorer_semantics.md` | Scorer semantics guardrails |
| `tests/test_exect_s4_gold_loader.py` | Gold examples EA0008, EA0011 |
| `tests/test_exect_frequency_primitives.py` | Candidate/bridge behavior contracts |
| `tests/test_exect_s5_scoring.py` | S5 frequency scoring smoke (EA0008) |
| `configs/experiments/exect_s4_frequency_*.json` | Existing S4 frequency arm configs (not executed in this draft) |

**Not read (missing / out of scope for this draft):** Per-document JSON raw annotations, corpus-wide audit script output, model run artifacts, `docs/experiments/synthesis/experiment_registry.json`.

---

## Run Summary

**No run directory supplied.** Metrics below are **design/support facts** from docs and code, not audit results.

### Support inventory (documented, not re-counted)

| Metric | Corpus (200 docs) | Validation (40 docs) | Source |
| --- | ---: | ---: | --- |
| Frequency label instances | 207 | 43 | `exect_s5_core_surface_design_20260524.md` |
| Docs with ≥1 frequency label | 129 | 24 | same |
| Raw `SeizureFrequency` JSON rows | 263 | unknown | `exect_s4_gold_policy.md` |

### Gold-template taxonomy (loader output classes)

From `canonical_seizure_frequency_label` and S4 policy:

| Template class | Example gold label | Loader rule | Source |
| --- | --- | --- | --- |
| **Quantified rate** | `1 per 3 week` | `NumberOfTimePeriods` + `TimePeriod` present | `exect.py:330–334`, `exect_s4_gold_policy.md:48–50` |
| **Qualitative change** | `frequency increased`, `frequency decreased`, `infrequent` | Non-null `FrequencyChange` | `exect.py:324–328`, `_FREQUENCY_CHANGE_LABELS` |
| **Seizure free** | `seizure free` | `CUIPhrase == seizure free` or `NumberOfSeizures == 0` with qualifying phrase | `exect.py:313–319` |
| **Seizure free since year** | `seizure free since 2017` | `NumberOfSeizures == 0` + `YearDate` | `exect.py:321–322`, EA0011 test |
| **Unmapped (no gold label)** | — | Entities failing all branches return `None` | `exect.py:336`, S4 policy:54–55 |

**Fact (multi-label):** EA0008 gold = `{1 per 3 week, frequency increased}`; EA0011 gold = `{1 per 2 week, seizure free since 2017}` (`tests/test_exect_s4_gold_loader.py:73–92`).

### Candidate-template taxonomy (note-anchored)

From `_build_exect_frequency_label_set` (`primitives.py:1486–1548`):

| Candidate source | Detection mechanism | Audited? |
| --- | --- | --- |
| Qualitative change cues | Substring match on `_FREQUENCY_CO_LABEL_CUES` | Yes, if passes `_accept_exect_frequency_candidate_label` |
| Seizure-free surfaces | `seizure free` + optional `_SEIZURE_FREE_SINCE_RE` | Yes |
| Quantified regex | `_QUANTIFIED_FREQUENCY_NOTE_RE`, zero-rate, every-N-period | Yes, after repair |
| Gan temporal (filtered) | `build_temporal_frequency_candidates_from_note` → ExECT template filter | Partial — only labels mapping to audited templates |
| Blocked / non-audited | `_NON_AUDITED_FREQUENCY_RES`, unsupported templates | Rejected |

**Audited template gate:** `_is_audited_exect_frequency_template` accepts qualitative set, `seizure free since YYYY`, and `_QUANTIFIED_FREQUENCY_RE` (`primitives.py:1563–1568`).

### Proposed missed-template taxonomy (for human audit execution)

Use these buckets when comparing gold labels ↔ candidate sets per document:

| Code | Definition | Example / hypothesis | Primary sources |
| --- | --- | --- | --- |
| **M1 — Candidate miss, gold present** | Gold label ∉ candidate set | Prose phrasing not matched by note regex (see post-merge test: `"Frequency is about fifteen per four months"`) | `tests/test_exect_frequency_primitives.py:148–155` |
| **M2 — Gold unmapped, note may support** | JSON `SeizureFrequency` entity → `None`, but note has frequency language | Rows with only type CUIPhrase, `During` without counts (S4 policy exclusion) | `exect_s4_gold_policy.md:54–55` |
| **M3 — Gold present, note unsupported** | Gold label exists; `note_has_exect_frequency_support` false | Annotator tagged span not recoverable from letter text alone | `primitives.py:1314–1317` |
| **M4 — Multi-label asymmetry** | Gold has co-labels; candidate set partial | EA0008-style quantified + change; bridge co-label augmentation policy differs by arm | `exect_s4_gold_policy.md:57–60`, `primitives.py:1579–1636` |
| **M5 — Multi-type frequency (Q4)** | Multiple gold frequencies for different seizure types; no CUI link in flat schema | EA0011: ongoing biweekly + type-resolved since 2017 | `exect_gold_label_audit.md:354–397`, EA0011 test |
| **M6 — Template repair mismatch** | Candidate or model surface needs bridge repair to match gold | `1 per day` → `1 per 1 day`; prose `seizure free for …` → `seizure free` | `primitives.py:1291–1311`, tests |
| **M7 — Seizure-type confusion** | Type wording in frequency channel | Blocked by `_looks_like_seizure_type_not_frequency` | `primitives.py:1646–1653` |
| **M8 — Gan/ExECT policy gap** | Gan temporal hints that do not map to ExECT templates | `multiple per week`, cluster labels filtered out | `tests/test_exect_frequency_primitives.py:46–55` |

### Evidence quote availability (design facts)

| Layer | Quote / span behavior | Caveat |
| --- | --- | --- |
| **Gold** | JSON annotations include entity span text and offsets in `raw_annotations` | Loader emits normalized labels only; offsets not surfaced in `ExectGoldDocument` scoring view |
| **Candidates** | `PrimitiveCandidate.source_span_text`, optional `start`/`end` via `_frequency_label_span` | Span lookup can return `None` for some quantified labels (`primitives.py:1659–1677`) |
| **Scorer evidence_support** | Categorical diagnostic metric | Not prediction-affecting; can misclassify if gold spans wrong (audit Bug 6) | `exect_gold_label_audit.md:184–198` |

**Uncertainty:** Corpus-wide % of gold labels with recoverable candidate spans is **unknown** until audit script runs.

### Comparison controls (when model arms follow)

| Control | Intended value | Source |
| --- | --- | --- |
| Split for routine eval | validation | `exectv2_splits.json` split_policy |
| S5 guard families | diagnosis, seizure_type, annotated_medication, investigation | `exect_s5_core_surface_design_20260524.md:88–95` |
| Frozen S4 frequency baseline | GPT full 65.5% micro (11-family); frequency weak | `kanban_plan.md:112` |
| Deferred arms | E5 grid, E6 implementation iteration | gated on this audit |

---

## Interpretation

**Scoped to no-model gold-vs-candidate representability (not model performance):**

1. **Gold surface is stable and documented.** Seizure frequency gold comes exclusively from JSON `SeizureFrequency` entities via `canonical_seizure_frequency_label`, decoupled from seizure-type gold (Bug 1 fix confirmed in audit doc and loader). This is the benchmark-facing reference for both S4 and S5.

2. **Candidate primitives exist and are registry-implemented** (`exect.frequency.rate_candidates.v1`, `exect.frequency.benchmark_bridge.v1`; `tests/test_exect_frequency_primitives.py:122–130`). They intentionally mirror S4 audited templates, not Gan monthly normalization.

3. **Known structural tension (Q4):** Multi-type documents can carry multiple gold frequency labels (EA0011) while S4 extraction policy still prefers a single clinically current rate for programs (`exect_s4_gold_policy.md:62–64`). A high gold-template coverage number alone does not resolve which label(s) a single-output arm should target.

4. **Bridge variants change scored predictions without changing gold** (post-merge, multi-label retention, co-label augmentation). Audit must separate **representability** (candidates ⊇ gold) from **arm-specific recovery policy** (bridge flags).

5. **S5 inclusion is support-justified** (24 validation docs, 43 labels) but S5 pooled micro remains non-comparable to S4 11-family headlines.

**What this draft does *not* establish:** Corpus recall/precision of candidates vs gold, validation-only coverage %, or whether E5/E6 should proceed. Those require executed audit artifacts.

---

## Caveats

### Scorer

- Set-based per-document F1; multiple gold labels per doc are expected (`exect_s4_gold_policy.md:57–60`).
- S5 `seizure_frequency` reuses S4 semantics unchanged (`exect_s5_core_surface_design_20260524.md:68–70`).
- Do **not** compare S5 pooled micro to S1–S4 pooled micro without family-set caveat.
- Gan monthly-frequency normalization and `no_reference` abstention semantics do **not** transfer (`primitives.py:1257–1258`, `1464–1465`; `deterministic_scorer_semantics.md:49–72`).
- Bridge recovery (`recover_exect_frequency_benchmark_values*`) can add labels not in raw model output — arm decision, not gold audit.

### Dataset / gold

- 263 JSON rows vs 207 scored label instances — row-to-label mapping and unmapped-row count **not verified** in this draft.
- Q4 per-type frequency-by-CUI linking remains deferred (`exect_s4_gold_policy.md:128–129`).
- `missing_gold` quality flag uses diagnosis/seizure_type/medication only, not frequency (`exect.py:384–393`) — frequency-only docs may lack that flag.
- Historical CSV `MarkupSeizureFrequency.csv` is reference-only; loader uses JSON (`exect_gold_label_audit.md:217–219`).

### Cap / full / test

- Audit should report **validation first** (S5 support rule); test holdout reporting deferred per split policy unless explicitly unlocked.
- Existing S4 frequency configs are cap-25 GPT (`configs/experiments/exect_s4_frequency_*.json`) — not inputs to this no-model audit.

### Validation / billing

- No model calls required for core audit.
- Any follow-on cap-25/full runs are separate arms (E5/E6), blocked until audit completes.

---

## Decision Recommendation

**`needs-review`**

**Rationale:**

- Kanban marks the card Ready with validation criterion “audit reports gold-template coverage, missed-template taxonomy, evidence quote availability, and scorer caveats” (`kanban_plan.md:45`).
- E4 (S5 scaffold) is complete; E5/E6 explicitly deferred pending this audit (`kanban_plan.md:77–79`).
- Source docs and primitives define **what** to measure, but **no corpus-wide audit artifact** or run directory was supplied.
- Promoting to `hold`, `promote`, or `reject-as-tested` would require primary counts and exemplar tables not available here.

**Decision scope mapping:**

| Scope | Status |
| --- | --- |
| **operational** | Audit card is Ready; next recommended pull (`kanban_plan.md:90`) |
| **arm** | No arm tested — pre-arm gate |
| **mechanism** | Candidate primitive exists; corpus representability **open** |
| **open** | Q4 multi-type frequency selection rule |
| **blocked** | E5, E6 until audit output |
| **stale_check** | Support counts from 2026-05-24 S5 design; re-verify if loader changes |

---

## Required Human Checks

Before promoting this draft into `docs/experiments/exect/`:

### Required inputs (missing)

| Input | Purpose |
| --- | --- |
| **Audit script or notebook output** (CSV/JSON) | Per-doc: `document_id`, split, gold labels, candidate labels, symmetric diff, taxonomy code M1–M8 |
| **Corpus paths confirmed** | `EXECT_ROOT` resolution: `Json/`, `Gold1-200_corrected_spelling/` |
| **Unmapped entity inventory** | All `SeizureFrequency` JSON entities where `canonical_seizure_frequency_label` returns `None`, with raw attrs |
| **Validation-subset metrics** | Coverage %, missed-label count, spurious-candidate count on 40 validation IDs |
| **Evidence span table** | For each gold label: JSON span text, candidate `source_span_text`, span-found boolean |
| **Exemplar pack (≥5 docs)** | Must include EA0008 (multi-label), EA0011 (multi-type Q4), at least one M2 unmapped case if present |
| **Split attribution** | Join via `data/splits/exectv2_splits.json` |

### Execution checklist

1. **Gold inventory:** Run `load_exect_gold_documents()`; collect `seizure_frequencies` per doc (`exect.py:214–219`).
2. **Candidate inventory:** Run `build_exect_frequency_candidate_payloads(gold.text)` per doc (`primitives.py:1232–1267`).
3. **Compute coverage:** For each gold label `g`, ∃ candidate `c` with `c.benchmark_value == g` (exact match post-normalization).
4. **Compute precision of candidates:** For each candidate label not in gold, classify M2/M3/M6/M8.
5. **Evidence quotes:** For matched pairs, record whether `_frequency_label_span` or JSON span text aligns with note substring.
6. **Tabulate by split:** Report validation primary; corpus secondary; test holdout optional.
7. **Scorer sanity:** Confirm S5 scorer frequency F1 == 1.0 on perfect gold-as-prediction for EA0008 (`tests/test_exect_s5_scoring.py`).
8. **Do not change:** scorer semantics, registry rows, Kanban status, or gold loader without separate promotion.

### Promotion gates (suggested thresholds — human to confirm)

| Gate | Suggested criterion | If fail |
| --- | --- | --- |
| Validation gold coverage | ≥90% gold labels matched by candidates | E6 (implementation iteration) before E5 |
| M5 prevalence | Document Q4 conflict rate and selection policy need | Reopen Q4 simple guidance (`exect_gold_label_audit.md:441–445`) |
| M2 unmapped rate | List explicitly; do not silently fold into model error | Loader/policy decision separate from arm decision |
| Evidence span rate | Report % only; do not gate benchmark F1 | Diagnostic for H2/H4 arms |

### Artifact targets on promotion

- `docs/experiments/exect/exect_s4_s5_frequency_gold_template_audit_YYYYMMDD.md`
- Optional machine-readable: `artifacts/audits/exect_frequency_gold_template_audit_v1.json`
- Update Kanban Completed row only after human review of primary tables
- Register comparison group only if proceeding to E5 (`experiment_decision_template.md`)

---

## Audit Output Template (fill when inputs available)

```markdown
### Corpus summary
- validation_docs_with_frequency: __ / 24
- validation_gold_labels: __ / 43
- validation_coverage (gold → candidate): __%
- validation_candidate_precision (candidate → gold): __%
- unmapped_json_entities (M2): __

### Missed-template breakdown (validation)
| Code | Count | Example doc IDs |
| M1 | | |
| M2 | | |
| ... | | |

### Evidence quote availability (validation)
- gold_labels_with_json_span: __%
- gold_labels_with_candidate_span: __%
- matched_with_overlapping_text: __%

### Exemplar: EA____ 
- gold: [...]
- candidates: [...]
- taxonomy: M_
- note excerpt: "..."
- json span: "..."
- candidate span: "..."
```

---

**Bottom line:** Sources define a coherent no-model audit protocol and a clear missed-template taxonomy, but the audit has not been executed. Treat all coverage numbers as **unknown** until Required Inputs are produced. Decision remains **`needs-review`** at **operational / open** scope; **arm** and **mechanism** promotion stay **blocked** pending primary artifacts.
# ExECT S5 Frequency Residual Audit

Date: 2026-05-24
Kanban card: A1 - Frequency residual audit
Status: Completed source-backed inspection
Decision scope: residual taxonomy for next S5 `seizure_frequency` arms

## Orchestration Frame

This audit follows the `cursor-implementation-orchestration` workflow as a Codex-reviewed implementation card. The working branch is `codex/a1-frequency-residual-audit`. No Cursor-authored mutation was promoted for this card because the available local Cursor command did not expose a non-interactive SDK/agent interface; Codex performed the source-backed inspection directly and kept the write surface to this note plus the Kanban status row.

Allowed write surfaces: this inspection note and the active Kanban card status.

Forbidden changes: raw ExECT data, split definitions, gold labels, scorer semantics, model outputs, run artifacts, configs, operational defaults, and paper claims.

Validation gate: the note must cite the primary run ID, split, scorer mode, metric caveats, and per-document residual categories.

## Primary Run

| Field | Value |
| --- | --- |
| Run ID | `exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z` |
| Run path | `runs/exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z` |
| Config | `configs/experiments/exect_s5_frequency_pre_vocab_full_gpt4_1_mini.json` |
| Dataset / split | ExECTv2, `exectv2_fixed_v1:validation` |
| Model / provider | `gpt-4.1-mini`, OpenAI |
| Schema level | `exect_s5_core_field_family` |
| Program variant | `exect_s4_field_family_frequency_pre_vocab_single_pass` |
| Scorer mode | `exect_s5_core_field_family_deterministic_v1` |

Run caveats inherited from the artifact:

- S5 is a partial five-family diagnostic surface, not published ExECTv2 Table 1 reproduction.
- S5 scores diagnosis, seizure type, annotated medication, investigation, and seizure frequency.
- Medication temporality is excluded from S5 because ExECT prescription gold has no native temporality column.
- Seizure-frequency gold uses ExECT annotation-facing surfaces, not Gan monthly-frequency normalization.
- Evidence quote support is diagnostic and is not part of benchmark-facing field-family F1.

## Headline Metrics

Full-validation `seizure_frequency` is the active S5 bottleneck:

| Metric | Value |
| --- | ---: |
| Support | 43 gold labels |
| Precision | 46.3% |
| Recall | 86.0% |
| F1 | 60.2% |

The residual shape is precision-dominated: 27 documents have frequency residuals, with 43 false positives and 6 false negatives.

False-positive concentration:

| FP label | Count |
| --- | ---: |
| `infrequent` | 12 |
| `frequency same` | 8 |
| `frequency increased` | 4 |
| `seizure free` | 3 |
| `frequency decreased` | 1 |
| Quantified-rate labels | 15 |

False-negative concentration:

| FN label | Count |
| --- | ---: |
| `seizure free` | 3 |
| `2 per 1 day` | 1 |
| `infrequent` | 1 |
| `0 per 3 year` | 1 |

## Residual Taxonomy

| Category | Documents | Read |
| --- | ---: | --- |
| Qualitative over-emission | 17 | The model often emits `infrequent`, `frequency same`, or `frequency increased` from weak or missing evidence, especially when those labels appear in the candidate list. |
| Gold-empty clinical-frequency extraction | 10 | The model extracts plausible frequency statements in documents with no scored frequency gold. These are false positives under current scorer semantics, but several are useful gold-policy review examples. |
| Temporal/current-scope mismatch | 7 | Historical rates or limited seizure-free intervals are emitted alongside, or instead of, the benchmark-facing current/resolved label. |
| Multi-type or range normalization mismatch | 6 | The model splits or rounds multi-type/range mentions differently from the annotation-facing gold, or collapses zero-rate windows to generic `seizure free`. |
| Evidence mismatch / candidate echo | 12 | Several residuals have no evidence spans, quote the injected candidate prompt, or cite text that supports a looser clinical inference but not the normalized label. |
| Gold-policy ambiguity | 9 | Residuals expose annotation-surface limits, including gold-empty documents with clear note frequencies and JSON `SeizureFrequency` rows that do not map to scored labels. |

Categories overlap; counts describe documents touched by each mechanism, not mutually exclusive buckets.

## Per-Document Residuals

| Doc | FP | FN | Primary category | Notes |
| --- | --- | --- | --- | --- |
| EA0008 | `infrequent` | - | Qualitative over-emission | Gold is `1 per 3 week` plus `frequency increased`; `infrequent` is a high-recall candidate with no predicted evidence. |
| EA0016 | `1 per 12 month`, `frequency increased` | - | Temporal/gold-empty | No frequency annotations; driving-clearance and prior-seizure context were converted into benchmark labels. |
| EA0018 | `2 per 1 week`, `infrequent`, `frequency same` | - | Gold-empty clinical-frequency | Note mentions twice-weekly episodes, but no scored frequency gold exists. |
| EA0029 | `frequency decreased` | - | Evidence mismatch | Medication-control language was interpreted as seizure-frequency decrease; no frequency gold. |
| EA0045 | `1 per 1 week`, `infrequent` | - | Gold-empty clinical-frequency | Event descriptions were converted to frequency labels without scored frequency annotations. |
| EA0047 | `3 per 1 day`, `frequency increased`, `infrequent`, `frequency same` | `2 per 1 day` | Multi-type/range mismatch | Gold has weekly generalized seizures and twice-daily absences; model over-normalized "several times a day" and over-emitted qualitative labels. |
| EA0048 | `3 per 1 day`, `frequency same` | - | Per-type scope mismatch | Gold is zero-rate tonic-clonic frequency; model also extracted current daily jerks and a qualitative same label. |
| EA0052 | `1 per 6 month` | - | Gold-empty clinical-frequency | "4 more attacks since last appointment" became a rate, but there is no scored frequency gold. |
| EA0053 | `infrequent` | - | Qualitative over-emission | Dropped-things/jerks context was treated as an infrequent frequency label with no gold. |
| EA0059 | - | `infrequent` | Qualitative omission | Historical seizure-free labels were captured, but the qualitative `infrequent` annotation was missed. |
| EA0061 | `infrequent`, `seizure free` | - | Zero-rate surface mismatch | Gold has two exact zero-rate windows; model added generic `seizure free` and `infrequent`. |
| EA0069 | `seizure free` | - | Temporal scope mismatch | Current weekly / four-in-three-weeks labels were captured, but a limited "up to five weeks seizure free" interval became generic `seizure free`. |
| EA0090 | `1 per 1 year`, `infrequent`, `frequency same` | - | Gold-policy ambiguity | JSON has a `SeizureFrequency` row with `PointInTime=Birthday` that normalizes to no scored label; model extracted note frequency context anyway. |
| EA0098 | `2 per 1 day` | - | Candidate normalization mismatch | "Most recent seizure September 2019" was converted into a daily rate; gold is `frequency increased` and `seizure free since 2019`. |
| EA0109 | `3 per 1 week`, `frequency increased`, `infrequent` | - | Gold-empty clinical-frequency | Note contains explicit 2-3/week worsening, but current scored frequency gold is empty. |
| EA0116 | `infrequent` | - | Gold-empty clinical-frequency | "A few episodes" was converted to qualitative frequency with no scored gold. |
| EA0131 | `infrequent` | - | Qualitative over-emission | Gold has `frequency increased`; model added `infrequent` from broad clinical wording. |
| EA0136 | `seizure free`, `infrequent` | `0 per 3 year` | Multi-window zero-rate mismatch | Gold has `frequency same`, `0 per 3 year`, and `0 per 5 year`; model collapsed one window to generic seizure freedom and missed the three-year label. |
| EA0137 | `frequency same` | `seizure free` | Zero-rate surface mismatch | Gold maps a zero-rate row to `seizure free` plus `2 per 1 year`; model kept the rate but emitted `frequency same` instead of seizure-free. |
| EA0142 | `3 per 1 month`, `frequency increased`, `frequency same` | - | Temporal scope mismatch | Historical 3/month rate was emitted alongside current `seizure free`; qualitative labels are unsupported by gold. |
| EA0143 | `frequency same` | `seizure free` | Zero-rate surface mismatch | Model captured `0 per 5 year` but missed generic `seizure free` and added `frequency same`. |
| EA0150 | `2 per 1 year`, `infrequent` | - | Range/evidence mismatch | Gold normalizes "1-2 per year" to `1 per 1 year`; model also emitted `2 per 1 year`, and inferred `infrequent` from rescue-medication wording. |
| EA0153 | `1 per 1 month` | - | Gold-empty clinical-frequency | Note says episodes occur about 1-2/month, but there is no scored frequency gold. |
| EA0170 | `frequency same` | - | Qualitative over-emission | Gold has `infrequent` and `1 per 1 month`; `frequency same` is an extra qualitative label. |
| EA0173 | - | `seizure free` | Omission despite candidate | `seizure free` appears in candidates and gold, but no prediction was emitted. |
| EA0174 | `2 per 1 day` | - | Candidate echo / evidence mismatch | Gold has `frequency increased`; the model emitted a rate from "more frequent and different" and cited the injected candidate prompt for `frequency increased`. |
| EA0185 | `4 per 1 month`, `5 per 1 month` | - | Gold-empty clinical-frequency | Note states present frequency is 4 to 5 episodes/month, but there is no scored frequency gold. |

## Interpretation

The next S5 lift should not narrow the high-recall candidate list; the high-precision cap-25 arm already showed recall loss without precision gain. A1 instead points to post-candidate decision discipline:

1. A verifier or prompt-policy arm should require local evidence for qualitative labels and should reject candidate-list labels with no independent note support.
2. The model needs temporal/current-scope rules for historical rates, limited seizure-free intervals, and current-vs-resolved multi-type cases.
3. Range and multi-type normalization should be treated carefully: ExECT annotation-facing labels are not Gan-style monthly normalizations, and scorer semantics should remain unchanged.
4. Several gold-empty documents are clinically interesting but remain false positives under the current benchmark. These should become caveats or review examples, not silent scorer changes.

## Recommended Next Pull

- Pull A2 as a candidate-constrained verifier prototype, but make the verifier evidence-sensitive rather than candidate-pruning-heavy.
- Pull A3 only after the verifier design names explicit policies for qualitative labels, historical rates, and limited seizure-free windows.
- Keep high-recall pre-vocab candidates as the baseline input surface.
- Do not alter ExECT frequency gold, split membership, or scorer normalization for this workstream.

## Validation

Commands / checks run:

- Inspected `metrics.json`, `errors.json`, `predictions.json`, `metadata.json`, and `config.json` for `exect_s5_frequency_pre_vocab_full_gpt4_1_mini_20260524T142823Z`.
- Loaded ExECT gold documents through `clinical_extraction.datasets.exect.load_exect_gold_documents()`.
- Cross-checked residual labels against predicted values, precomputed candidates, evidence snippets, and raw `SeizureFrequency` annotations.

Scorer semantics changed: no.

Normalization rules added or reused: none added; reused current ExECT loader/scorer normalization for inspection only.

Remaining risk: this is a qualitative residual audit, not an adjudicated annotation correction pass. Gold-empty frequency examples should be treated as policy caveats unless a separate benchmark-facing gold review is explicitly opened.

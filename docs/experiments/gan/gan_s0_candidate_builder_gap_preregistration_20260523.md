# Gan S0 Candidate Builder Gap Preregistration

Date: 2026-05-23  
Status: G12 preregistration before code changes  
Parent audit: `docs/experiments/gan/gan_s0_candidate_builder_gap_audit_20260523.md`  
Dataset/split: Gan 2026 synthetic validation enriched 25-record slice  
Program skeleton: `g2_candidates_adjudicate` / `gan_frequency_s0_temporal_candidates_single_pass`  
Scorer: `gan_frequency_deterministic_v1`

## Hypothesis

The next useful Gan S0 lift should come from deterministic candidate recall, not from another prompt, verifier, example pack, or model transfer. A narrow builder expansion should increase exact gold-label coverage on the enriched 25-record slice above the current **5/25** baseline while preserving existing temporal-candidate tests and scorer semantics.

## Variant

Variant ID: `gan_s0_candidate_builder_gap_v1`

Implementation scope:

- Add deterministic temporal-candidate builders in `src/clinical_extraction/gan/temporal_candidates.py`.
- Add focused regression tests in `tests/test_gan_temporal_candidates.py`.
- Do not change `src/clinical_extraction/gan/frequency.py`, `src/clinical_extraction/gan/scoring.py`, or benchmark metric semantics.
- Do not change prompt text, model config, few-shot examples, verifier policy, or run selection.

## Included Candidate Families

| Family | Target records | Target labels | Inclusion rule |
| --- | --- | --- | --- |
| Long-window quantified breakthrough counts | `gan_13058`, `gan_13149`, `gan_15127`, `gan_16645`, `gan_16750` | `2 per 7 month`, `3 per year`, `5 per 13 month`, `5 per 7 month`, `6 per 7 month` | Counted seizure events after an explicitly stated seizure-free or elapsed observation window. |
| Exact short-window quantified rates | `gan_14214`, `gan_14689`, `gan_16529` | `2 to 4 per month`, `3 per 2 month`, `1 per 5 day` | The note states the count and denominator directly enough to emit a simple rate without inventing a cluster structure. |
| Month/window aggregation | `gan_14562`, `gan_14628`, `gan_14792`, `gan_14821`, `gan_14965`, `gan_14973` | `3 per 6 month`, `2 per 2 month`, `1 per month`, `1 per 3 month` | Recent or elapsed-window counts where the denominator is anchored by clinic date, named month, or explicit "since" phrasing. |
| Vague multiple with anchored denominator | `gan_15168`, `gan_15193` | `multiple per 15 month`, `multiple per 13 month` | Only emit `multiple` rates when the count is explicitly vague and the observation window is textually anchored. |
| Cluster spacing plus per-cluster count | `gan_15442` | `1 cluster per 4 day, 2 per cluster` | Cluster cadence and per-cluster count are both explicitly recoverable from nearby evidence. |

## Excluded Patterns

- Do not emit seizure-free labels in G13 unless the note has a clear duration phrase that maps to the exact Gan label surface. The two uncovered seizure-free records (`gan_13574`, `gan_13598`) need a policy boundary review because their exact gold is `seizure free for multiple year`.
- Do not infer denominators from clinical plausibility, medication duration, or appointment interval unless the note gives a textual anchor.
- Do not add deterministic repairs for `unknown` versus quantified labels.
- Do not emit incomplete cluster labels such as `1 cluster per week` or labels with `unknown per cluster`.
- Do not use `reference[0]` as gold. It remains a secondary cross-check and difficulty signal.

## Regression Cases

Must remain covered:

- `gan_13123` -> `1 per year`
- `gan_14250` -> `2 per month`
- `gan_14485` -> `2 per 3 month`
- `gan_14881` -> `1 per month`
- `gan_15302` -> `1 to 2 per 14 month`
- Existing 30-record residual queue coverage test must remain at or above its current threshold.

Must newly cover if implementation is accepted:

- At least three long-window quantified records from the included set.
- `gan_15442` cluster label if the evidence supports both spacing and per-cluster count.
- At least one frequent quantified simple-rate record without introducing a cluster label.

## Acceptance Criteria

No-model validation:

- `uv run pytest tests/test_gan_temporal_candidates.py`
- `uv run python scripts/validate_primitives.py --errors-only`
- `uv run python scripts/audit_gan_candidate_builder_gap.py`

Promotion gate:

- Exact candidate coverage on the enriched 25-record slice must improve above **5/25**.
- Existing residual-slice coverage threshold in `tests/test_gan_temporal_candidates.py` must still pass.
- Scorer semantics and gold-source policy remain unchanged.

Model gate:

Only after the no-model gate passes, run one GPT 4.1-mini slice comparing the v1.4 control against `gan_s0_candidate_builder_gap_v1`. Qwen transfer remains blocked unless the GPT slice beats v1.4 or answers a separately preregistered transferability question.

## Research Caveat

The enriched 25-record slice is a diagnostic search surface selected from Qwen 35B pragmatic mismatches. Any coverage or GPT-slice lift on this slice is a mechanism signal, not a full-validation performance estimate.

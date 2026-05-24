# Gan S0 Unknown-Overuse Targeted Arm Preregistration

Date: 2026-05-24
Kanban Card: C2 - Unknown-overuse targeted arm design
Decision Scope: arm
Status: Preregistered

---

## 1. Hypothesis

The current operational default (`gan_s0_candidate_builder_gap_v1` on GPT-4.1-mini) has 58 benchmark-severe misses at 80.6% monthly accuracy on the full validation split. The consolidated residual taxonomy (C1) identified unknown-overuse as a primary failure cluster.

**Hypothesis:** Injecting explicit abstention-boundary policy into the extractor prompt—covering quantified-window preservation, seizure-free/no-reference disambiguation, and candidate-override discipline—will reduce the benchmark-severe unknown-overuse misses (currently ~6 records: `unknown_as_quantified_rate` × 3 + `unknown_vs_seizure_free` × 2 + `unknown_vs_no_reference` × 1) without introducing new frequent-undercalled or other-semantic-mismatch regressions.

**Decision question:** Does this prompt-only intervention lift cap-25 monthly accuracy above the 84% preregistration gate relative to the baseline v1.4 control on the same cap-25 slice?

---

## 2. Scope and Controls

### 2.1 Frozen controls

- **Candidate builder:** `gan_s0_candidate_builder_gap_v1` implementation variant frozen. `temporal_candidates.py` builder patterns, variant mapping, and coverage remain unchanged.
- **Program variant:** `gan_frequency_s0_temporal_candidates_single_pass` frozen.
- **Schema level:** `gan_frequency_s0` frozen.
- **Scorer:** `gan_frequency_deterministic_v1` frozen. Gold is `seizure_frequency_number[0]` throughout.
- **Split:** `gan_2026_fixed_v1:validation`, cap-25 subset using existing fixture.
- **Model:** GPT-4.1-mini (`configs/models/gan_s0_gpt4_1_mini.json`).
- **Repair policy:** artifact-bridge surface normalization only (same as baseline).

### 2.2 Varied factor

- **Prompt version:** New policy-extended prompt `gan_frequency_s0_temporal_candidates_single_pass_v1_5_unknown_overuse_guard` targeting the unknown-overuse subcategories defined below.

### 2.3 Comparison group

- **Baseline:** `gan_s0_candidate_builder_gap_v1` (80.6% monthly, full validation). Cap-25 control from the same baseline program and prompt version v1.4 (`gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation`).

---

## 3. Unknown-Overuse Subcategories and Policy Targets

The taxonomy (C1) defines four unknown-overuse failure shapes, and the full-validation error analysis supplies concrete example records:

### Subcategory A: `unknown_as_quantified_rate` (3 records on full validation)

The model emits `unknown` when the note contains a usable time-bounded event count.

| Record | Gold | Predicted |
| --- | --- | --- |
| `gan_14081` | `unknown` | `1 to 3 per 3 month` |
| `gan_6077` | `unknown` | `1 per 8 month` |
| `gan_14146` | `unknown` | `3 per 2 month` |

> Note: these records have gold=unknown but the model emits a rate. This is the *inverse* shape — the model is **under**using unknown, not overusing it. The taxonomy naming in the error analysis reflects "unknown-overuse" from the *gold* distribution perspective; for these three cases the model emitted a spurious rate where the gold is `unknown`.

**Policy target:** Add a rule defining when a count-without-stable-denominator or trigger-conditioned count should remain `unknown`. Example: counts since a diet change, medication adjustment, or single event cluster with no established recurrence window.

### Subcategory B: `unknown_vs_seizure_free` (2 records)

The model emits `unknown` when the note has an explicit seizure-free/no-events statement, or vice versa.

| Record | Gold | Predicted |
| --- | --- | --- |
| `gan_11216` | `unknown` | `seizure free for 4 month` |

**Policy target:** Clarify the seizure-free threshold (≥ 6 months of documented freedom triggers a seizure-free label; shorter remissions or ambiguous "no further events" should use the preceding count or `unknown` depending on window availability).

### Subcategory C: `unknown_vs_no_reference` (1 record)

The model emits `unknown` when the note has zero current seizure frequency context (gold: `no seizure frequency reference`), or the reverse.

| Record | Gold | Predicted |
| --- | --- | --- |
| `gan_7894` | `seizure free for multiple year` | `no seizure frequency reference` |

**Policy target:** Add a policy distinguishing `unknown` (seizure activity present but rate unclear) from `no seizure frequency reference` (no current or recent seizure events described, or only remote childhood febrile seizures). Key example: `gan_7894` — childhood febrile seizures only; the gold is seizure-free-for-many-years, not `unknown`.

### Subcategory D: `other_semantic_mismatch` involving unknown emission (subset of 17)

A subset of the 17 `other_semantic_mismatch` records involves the model emitting `unknown` when a quantified rate is present.

Examples from the record index where gold is a rate and predicted is `unknown`:
- `gan_4709`: gold `multiple per day`, predicted `unknown`
- `gan_12465`: gold `1 per day`, predicted `unknown`
- `gan_4100`: gold `1 per 2 to 3 week`, predicted `unknown`
- `gan_15771`: gold `3 per week`, predicted `unknown`
- `gan_3623`: gold `7 per week`, predicted `unknown`
- `gan_3630`: gold `7 per week`, predicted `unknown`
- `gan_6094`: gold `3 per month`, predicted `unknown`
- `gan_16883`: gold `4 per 3 month`, predicted `unknown`
- `gan_16780`: gold `3 per 7 month`, predicted `unknown`
- `gan_4602`: gold `1 per 7 to 10 day`, predicted `unknown`

**Policy target:** Candidate-override discipline — when a deterministic temporal candidate providing a quantified rate is present, the model must either accept it or emit a structured override reason from a small enum (`no_current_evidence`, `historical_only`, `trigger_conditioned_only`).

---

## 4. Prompt Policy Block to Add

The new prompt version (`v1.5`) extends the existing v1.4 policy with the following additions:

1. **Quantified-window preservation rule:** If the note gives a count of events in an explicit calendar window (e.g., `N seizures in the past M months`, `N per M weeks`), preserve the rate label even if the note also says `no further events since`. Override to `unknown` only if the window is trigger-conditioned (e.g., after medication withdrawal, following a single febrile episode), explicitly stated as exceptional, or shorter than two weeks with no follow-up window.

2. **Seizure-free vs unknown boundary:** Use a `seizure free for N unit` label when the note states documented freedom for ≥ 6 months with no intercurrent breakthrough event. Use `unknown` when the note mentions seizure activity but no usable frequency denominator. If the note says `no further events` without a duration, and no prior window count is available, use `unknown`.

3. **No seizure frequency reference vs unknown:** Use `no seizure frequency reference` only when the note has no current or recent epileptic seizure events at all (only remote history, childhood events, or non-epileptic episodes). Use `unknown` when seizure activity is described but frequency cannot be quantified. Do not use `unknown` as a fallback for notes with zero seizure context.

4. **Candidate-override discipline:** If a deterministic temporal candidate is present, either select it as the answer or emit a structured override reason from: `no_current_evidence` (candidate evidence is historical, not current), `historical_only` (note clearly marks the event as past, not active), or `trigger_conditioned_only` (event was tied to a medication change or acute provocation).

---

## 5. Decision Gates

| Gate | Threshold | Action if met | Action if missed |
| --- | --- | --- | --- |
| Cap-25 monthly accuracy ≥ 84% | Primary gate | Proceed to full-validation run | Terminate; document unknown-overuse as a hard extraction bottleneck |
| No regression on `no_seizure_information` pragmatic class | Secondary gate | Required for promotion | If `no_seizure_information` drops, revert candidate-override rule first |
| Unknown-overuse class count reduced by ≥ 3 records on cap-25 slice | Diagnostic gate | Confirms mechanistic effect; needed for paper claim | Document but do not block on this alone |

---

## 6. Config Draft

Config file: `configs/experiments/gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini.json`

```json
{
  "controls": {
    "abstention_policy": "allow_explicit_abstain_flag_with_unknown_overuse_guard_v1_5",
    "context_policy": "full_note_plus_deterministic_temporal_candidates",
    "few_shot_policy": "none",
    "repair_policy": "artifact_bridge_surface_normalization_only",
    "verifier_policy": "none"
  },
  "dataset": "gan_2026",
  "experiment_id": "gan_s0_unknown_overuse_guard_cap25_gpt4_1_mini",
  "hypothesis": "Prompt-only unknown-overuse guard targeting abstention-boundary, seizure-free-vs-unknown, no-reference-vs-unknown, and candidate-override discipline on a cap-25 slice enriched for unknown-overuse misses from the full-validation error analysis. Gate: cap-25 monthly accuracy >= 84% before proceeding to full validation.",
  "max_records": 25,
  "metric_caveats": [
    "Cap-25 enriched slice; results are not full-validation claims.",
    "Comparison group: gan_s0_candidate_builder_gap_v1 on v1.4 prompt.",
    "Varied factor: prompt_version only. All other controls frozen.",
    "Scorer semantics unchanged: gold is seizure_frequency_number[0].",
    "Evidence support is diagnostic only."
  ],
  "model_config_path": "configs/models/gan_s0_gpt4_1_mini.json",
  "output_root": "runs",
  "program_variant": "gan_frequency_s0_temporal_candidates_single_pass",
  "prompt_version": "gan_frequency_s0_temporal_candidates_single_pass_v1_5_unknown_overuse_guard",
  "record_ids": null,
  "report_on_test_split": false,
  "schema_level": "gan_frequency_s0",
  "scorer_mode": "gan_frequency_deterministic_v1",
  "split_file": "data/splits/gan_2026_splits.json",
  "split_name": "gan_2026_fixed_v1:validation",
  "structured_output_strategy": "provider_json_schema_with_pydantic_validation",
  "taxonomy": {
    "clinical_task_family": "frequency",
    "comparison_group": "gan_s0_candidate_builder_gap_v1",
    "dataset": "gan_2026",
    "hybrid_balance_class": [
      "H2_pre_deterministic",
      "H4_deterministic_first_llm_adjudicates"
    ],
    "implementation_variant": "gan_s0_candidate_builder_gap_v1",
    "intended_decision": "pending",
    "interleaving_positions": ["pre", "during"],
    "program_architecture": "temporal_candidates_single_pass",
    "schema_complexity": "gan_s0",
    "stage_executor": "det_candidates_llm_adjudicate",
    "stage_graph_id": "g2_candidates_adjudicate",
    "varied_factor": "prompt_version"
  }
}
```

---

## 7. Slice Selection

The cap-25 slice for this arm should be enriched for unknown-overuse failures. Source records:

- All records with `failure_class` in `{unknown_as_quantified_rate, unknown_vs_seizure_free, unknown_vs_no_reference}` from the full-validation error analysis (6 records).
- Highest-count `other_semantic_mismatch` records where gold is a quantified rate and predicted is `unknown` (10 records from the list in Section 3D above).
- Remaining 9 records drawn from `frequent_undercalled` and `pragmatic_match_monthly_divergence` failures (general coverage).

Target fixture path: `data/fixtures/gan_s0_unknown_overuse_guard_cap25_slice.json`.

---

## 8. Preregistration Checklist

- [x] Hypothesis is specific and falsifiable.
- [x] Varied factor is a single change (prompt version only).
- [x] Controls are frozen: candidate builder, program, schema, scorer, split, model, repair policy.
- [x] Decision gate is explicit with a numeric threshold (≥ 84% cap-25 monthly accuracy).
- [x] Scorer semantics are unchanged; gold label source is unchanged.
- [x] No silent scorer change: any change to normalization or label interpretation must update tests and be documented separately.
- [x] No test/holdout spend: this is cap-25 validation enriched slice only.
- [x] Decision scope is `arm`. Rejection of this arm does not constitute mechanism closure on the unknown-overuse failure mode.

---

## 9. Relationship to Taxonomy (C1)

| Taxonomy category | This arm targets | Risk |
| --- | --- | --- |
| A. Unknown-overuse / abundance | Yes (subcategories A, B, C, D above) | Candidate-override rule may introduce new seizure-free over-application |
| B. Pragmatic monthly divergence | No | Out of scope for this arm |
| C. Multi-type and cluster spacing | No | Out of scope |
| D. Temporal scope/window mismatches | Partially (seizure-free threshold policy) | Low; boundary rule is explicit |

---

## 10. Caveats

- Unknown-overuse benchmark-severe errors (6 direct records) are a minority of the 58 total failures. This arm cannot be expected to close the gap to 90%+ Pragmatic accuracy; it is a targeted hypothesis test, not a comprehensive fix.
- The `other_semantic_mismatch` class (17 records) likely contains heterogeneous causes beyond unknown emission; some will not respond to this prompt patch.
- The Qwen 35b operational transfer uses a separate prompt that may or may not inherit this policy. Cross-model transfer is a separate experiment and is not part of this preregistration.

# Deterministic Rule Variants In The Hybrid Pipeline

Date: 2026-05-22  
Status: Research synthesis  
Related:

- `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
- `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`
- `docs/taxonomy/taxonomy_primitive_catalog.md`
- `docs/taxonomy/taxonomy_tool_interface_decision_20260520.md`
- `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`
- `docs/planning/kanban_plan.md`

---

## Purpose

This report names the main deterministic-rule variants tested in the wider DSPy clinical extraction program, and shows where each variant enters the pipeline by responsibility class.

The central research question is not "did rules help?" in the abstract. The useful question is:

> Which deterministic clinical knowledge should be used before, during, after, or only during evaluation of an LLM extraction pipeline, and what responsibility should remain with the LLM?

The project now tracks that question through three dimensions:

1. **Responsibility class**: `D1`, `L0`, `L1`, `H1`, `H2`, `H3`, `H4`.
2. **Interleaving position**: `pre`, `during`, `tool_during`, `post`, `eval_only`.
3. **Rule family**: temporal rules, benchmark label policy, controlled vocabularies, evidence guards, schema validators, bridges, repair policies, and inspection fixtures.

This document is a synthesis, not a mechanism-closing decision. Operational defaults are not proof that a mechanism class is solved, and arm rejects are not global mechanism rejects.

---

## Pipeline Positions

| Position | Meaning | Typical deterministic rule forms |
| --- | --- | --- |
| `pre` | Code runs before the LLM sees the task | candidate generation, section selection, controlled-vocabulary hints, temporal windows |
| `during` | Rules are included in the LLM task surface | prompt policy, schema constraints, allowed fields, examples, benchmark policy text |
| `tool_during` | LLM can call deterministic helpers while reasoning | ReAct-style temporal tools, lookup tools, future normalizer tools |
| `post` | Code changes or filters model output after extraction | benchmark bridges, repair, abstention, precision guards, canonicalization |
| `eval_only` | Code diagnoses or scores behavior without changing predictions | scorer canonicalization, evidence diagnostics, fixture checks, primitive inspection |

---

## Responsibility Classes At A Glance

| Class | Plain-language role | Pipeline entry | Key tested variants | Current reading |
| --- | --- | --- | --- | --- |
| `D1_deterministic_only` | Rules do extraction without an LLM | `pre`, `post`, `eval_only` | substring anchoring, fixture/scorer baselines | Useful floor and diagnostics, not current benchmark-facing ceiling |
| `L0_llm_only` | LLM extracts with minimal deterministic structure | `during` | bare extraction ladder rungs | Useful baseline for measuring schema/policy gains |
| `L1_llm_constrained` | LLM extracts under schema and prompt constraints | `during` | JSON schema, Pydantic validation, label-policy prompts | Current backbone for ExECT; not enough alone for benchmark alignment |
| `H1_post_deterministic` | LLM extracts first; rules repair, normalize, or filter after | `post`, sometimes `eval_only` | ExECT bridges, medication temporality post-classifier, non-ASM guard, Gan verify-repair | Strong for benchmark bridges and narrow guards; broad filters can collapse recall |
| `H2_pre_deterministic` | Rules prepare context or candidates before extraction | `pre` | Gan temporal candidates, ExECT pre-vocab, section-aware routing | Gan temporal pre-candidates help; broad/static ExECT pre-hints mostly arm-rejected |
| `H3_interleaved_tool_hybrid` | LLM calls deterministic tools during reasoning | `tool_during` | Gan ReAct temporal tools | One implementation arm rejected; mechanism remains open |
| `H4_deterministic_first_llm_adjudicates` | Rules propose candidates; LLM selects/adjudicates | `pre` + `during`, often `post` | Gan candidates-adjudicate, expanded builders, temporal candidates + verify-repair | Best-known Gan shape; operationally frozen, mechanism still open |

---

## D1: Deterministic-Only Rules

### What Enters The Pipeline

In `D1`, deterministic code tries to perform the task without model judgment. Rules may segment text, match substrings, map labels, validate fixtures, or score predictions.

**Pipeline sketch**

```text
note -> deterministic matcher / validator / scorer -> prediction or diagnostic
```

### Rich Example

An ExECT note contains:

```text
She has focal epilepsy. Current medication is lamotrigine.
```

A deterministic-only baseline may match surfaces such as `focal`, `epilepsy`, and `lamotrigine`, then emit diagnosis, seizure-type, or medication candidates based on string rules. This is useful because it shows what is recoverable from surface form alone.

The weakness is that the same approach struggles when surface text is ambiguous:

```text
No evidence of focal seizures since surgery.
```

The substring `focal seizures` is present, but the clinical status is negated or historical. The LLM is still needed for semantic interpretation, temporality, and field assignment.

### Concrete Project Use

- ExECT S1 deterministic feasibility floor in the ladder work.
- Primitive fixture cases under `shared.fixtures.primitive_cases.v1`.
- Scorer and bridge diagnostics where deterministic code checks benchmark-facing equivalence without claiming clinical extraction.

### Research Interpretation

`D1` is mostly a calibration layer: it gives feasibility bounds, validates primitive behavior, and catches scorer/normalizer drift. It is not the current target architecture for ExECT or Gan.

---

## L0: Bare LLM Extraction

### What Enters The Pipeline

`L0` minimizes deterministic structure. The LLM receives the note and a task, but little schema or benchmark policy.

**Pipeline sketch**

```text
note -> LLM extraction -> raw prediction
```

### Rich Example

For Gan, a note says:

```text
The patient has been seizure-free since levetiracetam was increased.
Before that, he had four seizures in six weeks.
```

A bare LLM may understand the prose but choose the wrong temporal window: it might report `4 seizures per 6 weeks` even though the current status is seizure-free. This is exactly the kind of temporal selection error that motivated deterministic temporal-candidate work.

For ExECT, a bare LLM may emit plausible fields, but not in the benchmark's expected label surface:

```text
diagnosis: epilepsy syndrome
```

when the scorer expects a more specific audited field-family representation.

### Concrete Project Use

- ExECT S1 ladder rung `L0` used to estimate the gain from adding schema and policy.
- Comparison baseline for testing whether deterministic components add value beyond general model semantics.

### Research Interpretation

`L0` is essential as a baseline. It should not be confused with the project goal. It tells us what the model can do before we add reproducibility, schema, audit policy, or deterministic clinical scaffolding.

---

## L1: LLM-Constrained Extraction

### What Enters The Pipeline

`L1` uses deterministic structure as a hard or semi-hard constraint, usually through JSON schema, allowed fields, Pydantic validation, and prompt policy.

**Pipeline sketch**

```text
note -> schema / field-family task -> LLM extraction -> validated structured output
```

### Rich Example

For ExECT S1, the model is constrained to produce field-family outputs for diagnosis, seizure type, and medication rather than free-form prose. A note like:

```text
The history is consistent with focal impaired awareness seizures.
She currently takes lamotrigine.
```

is routed into a structured output surface:

```json
{
  "diagnosis": [...],
  "seizure_type": [...],
  "medication": [...]
}
```

This reduces malformed output and forces the model to think in benchmark families. However, schema alone does not fully teach the benchmark's label policy. The project repeatedly found that ExECT S1 performance depended heavily on label-policy prompts and bridge behavior in addition to schema.

### Concrete Project Use

- ExECT S1/S2/S3/S4 frozen single-pass field-family programs.
- JSON/Pydantic schema integrity and retry/repair contracts.
- Model suite replays on frozen S1/S4/Gan F0 surfaces.

### Research Interpretation

`L1` is the backbone for broad ExECT extraction. It improves over bare extraction, but the strongest ExECT S1 anchor is `L1` plus benchmark policy and bridges, not schema alone.

---

## H1: Post-Deterministic Rules

### What Enters The Pipeline

`H1` lets the LLM extract first, then applies deterministic code to normalize, bridge, filter, abstain, repair, or diagnose the output.

**Pipeline sketch**

```text
note -> LLM extraction -> deterministic bridge / guard / repair -> final prediction
```

### Rich Example: ExECT Benchmark Bridges

Suppose the model extracts a seizure-type phrase:

```text
"focal seizures with impaired awareness"
```

The benchmark-facing scorer may expect a canonical representation that differs from the raw phrase. A deterministic benchmark bridge maps the model's surface into the audited label space while preserving the distinction between raw output and scored output.

This can improve measured F1 without proving the model became more clinically capable. It may instead mean the system got better at translating model output into benchmark policy.

### Rich Example: Medication Temporality Post-Classifier

An ExECT S4 note says:

```text
Lamotrigine was increased to 100 mg twice daily.
```

A broad post-classifier might classify this as `planned` or `unknown` because it sees a dose-change cue, even when the line is actually evidence of current medication. That broad H1 design improved precision but collapsed recall on full validation, so it was rejected as an arm.

A narrower post-guard is different:

```text
She takes omeprazole and levothyroxine.
```

If the model emits these as anti-seizure medications, a non-ASM guard can remove obvious non-antiepileptic leakage without changing valid ASM temporality labels.

### Concrete Project Use

- `exect.medication.benchmark_bridge.v1`
- `exect.seizure_type.benchmark_bridge.v1`
- `exect.diagnosis.benchmark_bridge.v1`
- `exect.frequency.benchmark_bridge.v1`
- `exect.medication_temporality.post_classifier.v1`
- `exect.medication_temporality.non_asm_guard.v1`
- `gan.frequency.verify_repair_policy.v1`
- `gan.frequency.label_policy_bridge.v1`

### Research Interpretation

`H1` is powerful but risky. It is strongest when the rule encodes a narrow, audited mapping or removes a high-confidence false positive. Broad post-hoc abstention can destroy recall. ExECT bridges are operational infrastructure; they should not be overread as a new clinical extraction mechanism.

---

## H2: Pre-Deterministic Rules

### What Enters The Pipeline

`H2` applies deterministic rules before the LLM extracts. It may select sections, inject candidates, provide controlled vocabularies, or expose temporal windows as hints.

**Pipeline sketch**

```text
note -> deterministic context/candidate generator -> LLM extraction -> prediction
```

### Rich Example: Gan Temporal Candidates

A Gan note says:

```text
She had three seizures in the month before medication change.
Since starting lacosamide, she has had one seizure every two months.
```

The deterministic candidate builder can expose candidate windows:

| Candidate | Window | Rationale |
| --- | --- | --- |
| `3 per 1 month` | before medication change | historical period |
| `1 per 2 months` | since lacosamide | current period |

The LLM then adjudicates which candidate matches the benchmark's target current seizure-frequency policy. This helps because the bottleneck is temporal bookkeeping, not merely recognizing that seizures are mentioned.

### Rich Example: ExECT Static Pre-Vocab

For ExECT medication or seizure-type extraction, pre-injecting a static list can backfire:

```text
Candidate medications: lamotrigine, levetiracetam, valproate, ...
```

If the note mentions valproate only as a historical allergy or family history item, the candidate list may anchor the model toward unsupported extraction. Several ExECT H2 pre-vocab/pre-candidate arms regressed on their primary family metrics.

### Rich Example: Section-Aware Routing

An ExECT sectioner may select only a "Medication" section before calling the medication extractor. That sounds appealing, but the tested section-aware S0/S1 arm lost useful cross-section context and worsened evidence grounding. This is an arm result, not proof that all section-aware methods are bad.

### Concrete Project Use

- `gan.frequency.temporal_candidates.v1`
- `exect.frequency.rate_candidates.v1`
- `exect.medication.rx_candidates.v1`
- `exect.sections.family_spans.v1` planned
- ExECT section-aware cap-25 architecture
- ExECT S1/S4 pre-vocab and pre-candidate slices

### Research Interpretation

`H2` is highly task-dependent. It is the right shape for Gan frequency because deterministic temporal candidates match the structural bottleneck. It has been brittle on ExECT when candidates are static, broad, or weakly tied to benchmark policy.

---

## H3: Tool-During Rules

### What Enters The Pipeline

`H3` exposes deterministic knowledge as a callable tool while the LLM reasons. The LLM decides when to call the helper, how to interpret the result, and how to integrate it into the final answer.

**Pipeline sketch**

```text
note -> LLM reasoning loop <-> deterministic tool -> final prediction
```

### Rich Example: Gan ReAct Temporal Tool

The tool-facing variant gives the LLM access to deterministic temporal helpers during a ReAct-style interaction. For a note with multiple windows:

```text
No seizures for the last year, but five seizures occurred during a medication taper two years ago.
```

The model can call a temporal helper and receive structured candidate information. In the tested Gan ReAct implementation, this did not replace precomputed candidate injection: schema validity fell and monthly accuracy on valid predictions was weak.

The negative result is still useful because it isolates interleaving position. The same broad knowledge source, temporal rules, performed much better when computed before extraction and shown as candidates than when made available as a tool in a reasoning loop.

### Concrete Project Use

- `gan.frequency.temporal_tool.v1`
- `gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails`
- Minimal adapter-level tool interface retained in `src/clinical_extraction/interleaving_adapters.py`

### Research Interpretation

`H3` is an arm reject for the tested Gan ReAct tool surface, not a mechanism reject for all tool-during hybrids. Future H3 work should only reopen with a specific comparison group and a clearer tool interface hypothesis.

---

## H4: Deterministic First, LLM Adjudicates

### What Enters The Pipeline

`H4` is a stronger form of pre-deterministic scaffolding. Deterministic code proposes structured candidates, and the LLM's main job is to select, adjudicate, verify, or explain among them.

**Pipeline sketch**

```text
note -> deterministic candidate builders -> LLM adjudication -> optional post repair/evidence guard -> prediction
```

### Rich Example: Gan Expanded Builders + Prose Candidate Presentation

A Gan note says:

```text
He had weekly seizures last year. He now has one seizure every three months.
The family also reports a cluster of two seizures during a febrile illness.
```

The candidate builder can produce multiple plausible frequency interpretations:

| Candidate | Source cue | Candidate type |
| --- | --- | --- |
| `1 per 1 week` | weekly seizures last year | historical |
| `1 per 3 months` | now has one seizure every three months | current |
| `2 per febrile illness cluster` | cluster during illness | event cluster |

The LLM adjudicator is then asked to choose the benchmark-facing current seizure frequency, not invent a value from scratch. This is a better division of labor for Gan: deterministic code enumerates temporal possibilities; the LLM handles current-vs-historical judgment, ambiguity, and evidence explanation.

### Rich Example: Temporal Candidates + Verify-Repair

In the older promoted Gan default, temporal candidates were paired with verification/repair. The LLM first selected a candidate, then a follow-up verifier/repair policy checked support and repaired inconsistent outputs. This bundled H2/H4/H1 shape became the engineering baseline, while later F0 expanded-builder adjudication became the monthly leader for model-suite replay.

### Concrete Project Use

- Gan temporal-candidates + verify-repair v1.1 operational default.
- Gan `g2_candidates_adjudicate` / F0 expanded builders + prose, frozen for model-suite comparison.
- Candidate presentation sweeps: JSON vs table vs prose.
- Stage executor grid: deterministic candidates vs LLM-generated candidates vs hybrid merge.

### Research Interpretation

`H4` is currently the clearest positive deterministic-rule pattern for Gan S0. It should be described as an operationally promoted arm, not as mechanism closure. The open mechanism question remains whether deterministic, LLM-generated, or hybrid candidate generation wins once presentation and downstream adjudication are fully controlled.

---

## Eval-Only And Diagnostic Rule Variants

Some important deterministic rules are deliberately not prediction-affecting. They exist to make research conclusions honest.

### Evidence Diagnostics

Evidence span checks can answer:

- Did the model quote text that exists in the note?
- Does the quote support the raw extracted value?
- Does the quote support the normalized benchmark-facing interpretation?

Those are different questions. Exact substring support can validate a quote without validating the canonical label.

### Scorer Canonicalization

Gan scoring preserves raw, canonical, benchmark-facing, monthly, Purist, and Pragmatic interpretations separately. This prevents the system from silently mixing clinical semantics with benchmark convenience.

### Primitive Fixtures

Fixture tests validate that deterministic primitives behave as expected on controlled cases. They support implementation quality but do not prove model-backed performance.

### Concrete Project Use

- `shared.evidence.substring_support.v1`
- `gan.frequency.evidence_guard.v1`
- `shared.fixtures.primitive_cases.v1`
- `shared.reporting.primitive_inspection.v1`
- `docs/policies/deterministic_scorer_semantics.md`

---

## Rule Families Mapped To Responsibility Classes

| Rule family | Typical classes | Typical positions | Representative project examples |
| --- | --- | --- | --- |
| Temporal/frequency rules | `H2`, `H4`, `H3`, `H1` | `pre`, `during`, `tool_during`, `post` | Gan temporal candidates, expanded builders, ReAct temporal tools, verify-repair |
| Benchmark label policy | `L1`, `H1`, `eval_only` | `during`, `post`, `eval_only` | ExECT v4_10 policy, ExECT bridges, Gan label-policy bridge |
| Controlled vocabularies | `H2`, future `H3`, `H1` | `pre`, `tool_during`, `post` | ExECT medication candidates, seizure pre-vocab, planned ontology/CUI work |
| Section/context rules | `H2` | `pre` | ExECT section-aware context selection |
| Evidence support | `H1`, `eval_only` | `post`, `eval_only` | substring support, evidence guard, verified-quote planned primitive |
| Verification/repair | `H1`, `H4` | `post`, sometimes `during` | Gan verify-repair, ExECT S1 verify-repair arm |
| Schema validation | `L1`, `eval_only` | `during`, `post`, `eval_only` | JSON schema, Pydantic validation, retry/repair contracts |
| Precision guards | `H1` | `post` | ExECT non-ASM guard, planned-scan guard, investigation ECG drop guard |
| Sparse-family bridges | `H1` | `post` | ExECT cause CUIPhrase bridge, planned onset/when-diagnosed bridges |
| Optimizer/example strategy | `L1`, sometimes hybrid variants | `during` | labeled few-shot, bootstrap, GEPA; not deterministic rules exactly but tracked beside rule placement |

---

## What The Experiments Currently Suggest

### Stronger Signals

1. **Gan frequency benefits from deterministic temporal structure before LLM adjudication.**  
   The best-known Gan arms use deterministic candidate builders and LLM selection.

2. **ExECT S1 benefits from constrained LLM extraction plus benchmark policy and bridges.**  
   The bridge/policy layer is load-bearing for local benchmark-facing diagnostics.

3. **The same knowledge source can succeed or fail depending on position.**  
   Temporal rules worked as precomputed candidates; one ReAct tool-during implementation failed.

4. **Narrow post-guards are more plausible than broad post-classifiers.**  
   Broad medication temporality abstention over-pruned; non-ASM precision guards are more targeted.

### Negative Or Cautionary Signals

1. **Broad/static ExECT pre-vocab arms have mostly regressed.**
2. **Verify-repair is not automatically useful across tasks.**
3. **Evidence filters can introduce abstention confounds.**
4. **Benchmark bridges can improve measured F1 without improving clinical validity.**
5. **Cap-25 arm rejects should not be upgraded to mechanism rejects without a mechanism review.**

---

## Practical Decision Guide

When adding a new deterministic rule, classify it before implementation:

| Design question | If yes, likely class |
| --- | --- |
| Does the rule extract without an LLM? | `D1` |
| Does it constrain the model's output shape? | `L1` |
| Does it prepare context or candidates before the call? | `H2` |
| Does it provide candidates that the LLM must choose among? | `H4` |
| Does it expose a callable helper during reasoning? | `H3` |
| Does it repair, filter, bridge, or abstain after extraction? | `H1` |
| Does it only diagnose or score behavior? | `eval_only` diagnostic |

Then state:

- `stage_graph_id`
- `stage_executor`
- `interleaving_positions`
- `control_modes`
- `knowledge_sources`
- prediction-affecting vs diagnostic-only behavior
- expected failure mode it targets
- what would count as an arm win, hold, or reject

---

## Open Questions

1. **Gan candidate generation mechanism:** deterministic vs LLM vs hybrid candidate source remains open despite the operational F0 default.
2. **ExECT pre-context mechanism:** section-aware and static-list arms failed, but other presentations or long-letter settings remain open.
3. **Tool-during mechanism:** only one Gan ReAct surface has been tested.
4. **Post-guard granularity:** narrow precision guards need more evidence before becoming defaults.
5. **Bridge interpretation:** ExECT benchmark bridges need continued separation between benchmark-facing score recovery and clinical validity.

---

## Source Artifacts Used

- Hybrid doctrine: `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
- Taxonomy ontology: `docs/workstreams/hybrid/hybrid_component_taxonomy_decision_20260520.md`
- Mechanism status: `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- Prior synthesis: `docs/workstreams/hybrid/hybrid_deterministic_placement_research_synthesis_20260521.md`
- Primitive catalog: `docs/taxonomy/taxonomy_primitive_catalog.md`
- Tool boundary: `docs/taxonomy/taxonomy_tool_interface_decision_20260520.md`
- Primitive workstream: `docs/taxonomy/taxonomy_primitives_workstream_plan_20260520.md`
- Active Kanban: `docs/planning/kanban_plan.md`
- ExECT section-aware inspection: `docs/experiments/exect/exect_section_aware_cap25_inspection.md`
- ExECT S1 stage executor inspection: `docs/experiments/exect/exect_s1_stage_executor_gpt_cap25_v1_inspection.md`
- ExECT S4 temporality inspection: `docs/experiments/exect/exect_s4_temporality_deterministic_gpt_inspection_20260520.md`
- ExECT S4 medication precision guard docs: `docs/experiments/exect/exect_s4_medication_precision_guard_design_20260521.md`
- Gan validation ladder and stage-executor docs under `docs/experiments/gan/`


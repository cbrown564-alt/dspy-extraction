---
name: clinical-schema-design
description: Use when designing or editing clinical schemas, Pydantic models, JSON schemas, DSPy signatures, field groups, validators, or structured extraction outputs for this project.
---

# Clinical Schema Design

The schema is the contract between clinical text, model output, validation, and scoring. Keep it explicit and auditable.

Follow this workflow:

1. Identify the target task and schema level:
   - Gan seizure-frequency extraction
   - ExECTv2 broad epilepsy extraction
   - shared clinical extraction infrastructure
   - schema ladder level S0-S4 from `docs/outline.md`
2. Read the relevant project context:
   - `docs/outline.md`
   - `docs/datasets/exect/exect_gold_label_audit.md` for ExECTv2 fields
   - `docs/datasets/gan/gan_2026_label_audit.md` for Gan frequency labels
3. Search for existing schema, validation, scorer, and primitive payload patterns before adding new types.
4. Design fields so validators and scorers can tell the difference between absent, unknown, negated, historical, planned, and present facts.

Deterministic hint and bridge payloads should align with shared primitive contracts when applicable:

- `PrimitiveCandidate` for note-anchored hints and candidate generation
- `NormalizationResult` for raw, canonical, and benchmark-facing values
- `EvidenceSupportResult` for quote and span support checks

## Schema Rules

- Require evidence for extracted clinical facts unless the field is explicitly metadata or administrative.
- Keep raw text, normalized value, status, temporality, evidence, and confidence separate when they have different semantics.
- Prefer constrained enums for known clinical states, but do not over-constrain values that must preserve source text.
- Do not collapse current, historical, planned, and resolved facts unless the experiment explicitly calls for a flat schema.
- Do not encode clinical uncertainty only in prose. Use explicit fields where uncertainty affects scoring or review.
- Make schema breadth an experimental parameter rather than letting fields accrete casually.

## Benchmark-Facing Versus Clinically Rich Schemas

Separate annotation-policy alignment from clinical expressiveness when they conflict.

- Benchmark-facing schemas should expose the label surface that the audited scorer expects, even if a richer clinical label would be reasonable.
- Clinically rich schemas may preserve finer-grained source concepts, but reports must not score them directly against coarse benchmark labels unless a mapping layer is explicit and tested.
- For ExECT S0/S1, be especially careful not to infer diagnosis labels from seizure-type evidence or emit ILAE-specific seizure surfaces when the benchmark-facing view expects a coarser label.
- For Gan S0, the schema should preserve the canonical Gan label and evidence quote separately from any normalized monthly-frequency value.

## Clinical Pitfalls

- Seizure frequency can refer to a specific seizure type, historical period, or current status.
- Medication mentions can be current, previous, planned, refused, stopped, or adverse-effect related.
- Diagnosis mentions can be generic, specific, negated, uncertain, historical, or family-history only.
- Evidence spans can support a raw mention without supporting the normalized interpretation.
- A model can be clinically plausible and still wrong under the benchmark annotation policy.

## Completion Criteria

Before finishing, summarize:

- schema level or task targeted
- fields added or changed
- whether the schema is benchmark-facing, clinically rich, or a bridge between the two
- how evidence, uncertainty, negation, and temporality are represented
- scorer or validator changes needed next

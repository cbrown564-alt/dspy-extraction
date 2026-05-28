# ExECT S1 Evidence Policy — Clean GPT Ablation Pre-Registration

Date: 2026-05-21  
Status: **Cap-25 configs ready — runs pending**  
Comparison group: `exect_s1_evidence_policy_gpt_validation_v1`  
Kanban: `docs/planning/kanban_plan.md` (Lane A, Phase 2)

## Research question

On ExECT S1 with **GPT 4.1-mini**, how does **evidence strategy** (standard contiguous quotes vs stricter seizure-evidence policy vs diagnostic-only/no hard evidence requirement) affect micro F1 and evidence diagnostics, when prompt label policy, verification, bridges, split, model, and scorer are fixed?

## Hypothesis

Stricter evidence policy (v3-style) improves evidence support and reduces unsupported quotes with minimal micro F1 change. Relaxing evidence requirements may increase recall at the cost of evidence diagnostics without improving benchmark-facing F1.

## Fixed controls (all arms)

| Control | Value |
| --- | --- |
| Dataset | `exect_v2` |
| Split | `exectv2_fixed_v1:validation` |
| Schema | `exect_s0_s1_field_family` |
| Scorer | `exect_field_family_deterministic_v1` (unchanged) |
| Model | GPT 4.1-mini |
| Program | `exect_s0_s1_field_family_single_pass` |
| `repair_policy` | `none` |
| Verification | `none` |
| Label policy baseline | v4_10 family rules (except evidence-specific deltas) |

## Varied factor

`evidence_strategy`

## Arms

| Arm | `evidence_strategy` | `prompt_version` | Description | Config (planned) |
| --- | --- | --- | --- | --- |
| **Standard quote** | `model_quote` | `exect_s0_s1_field_family_v4_10_label_policy` | Current production — exact contiguous quotes per field | `exect_s1_evidence_standard_cap25_gpt4_1_mini.json` |
| **Stricter evidence** | `verified_quote` | `exect_s0_s1_field_family_v4_10_evidence_strict_v1` | v4_10 label policy + strict evidence-only signature addendum | `exect_s1_evidence_strict_cap25_gpt4_1_mini.json` |
| **Soft diagnostic quote** | `model_quote_with_diagnostic_span_check` | `exect_s0_s1_field_family_v4_10_evidence_soft_v1` | v4_10 label policy + soft evidence-only signature addendum | `exect_s1_evidence_soft_cap25_gpt4_1_mini.json` |

Strict/soft arms use evidence-only signature addenda on v4_10 — not a full v3 prompt restore (v3 mixed label and evidence policy).

## Historical priors (bundled — not clean evidence)

| Arm | Reference | Micro F1 | Notes |
| --- | --- | ---: | --- |
| v3 full (legacy) | `docs/experiments/exect/exect_s0_s1_validation_full_v4_1_inspection.md` | 67.8% | Predates v4 ladder — motivation only |
| v4_10 full | `…221944Z` | 92.3% | Production freeze |

## Run order

1. Implement soft-evidence variant if not config-only.
2. Audit v3 vs v4_10 diff scope (label vs evidence only).
3. Dry-run → cap-25 three arms.
4. Full validation for arms within −1pp micro of standard arm on cap-25.
5. Inspection `docs/exect_s1_evidence_policy_gpt_validation_v1_inspection_<date>.md`.
6. Registry rows.

## Primary metrics

- **Pooled micro F1** (must not regress > 2pp vs standard arm)
- **Evidence quote support rate** (headline for this group)

## Diagnostic metrics

- Per-family F1
- Unsupported-quote / ellipsis-bridge counts
- Schema-valid rate

## Cap-25 gate

| Outcome | Rule |
| --- | --- |
| **Promote evidence policy** | Evidence support ≥ +5pp vs soft arm **and** micro within −1pp of standard |
| **Hold** | Evidence gain with micro −1pp to −2pp |
| **Reject** | Micro regression > 2pp vs standard **or** no evidence improvement |

## Artifacts checklist

- [ ] Three cap-25 configs
- [ ] v3 vs v4_10 diff audit note (1 paragraph in inspection)
- [ ] Soft-evidence implementation if needed
- [ ] Inspection doc
- [ ] Registry rows with `varied_factor: evidence_strategy`

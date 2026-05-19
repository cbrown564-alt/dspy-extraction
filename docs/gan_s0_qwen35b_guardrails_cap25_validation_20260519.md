# Gan S0 Qwen3.6:35b Post-Guardrails Cap-25 Validation

Date: 2026-05-19

## Research Question

After adding Gan S0 artifact-bridge canonicalization (`few`/`several`, hyphen/`or`
ranges, `quarter`/`fortnight`) and evidence-length guardrails, does a fresh
Qwen3.6:35b direct validation cap show fewer `normalization.invalid_label` failures
and stable or improved evidence quote support without changing
`gan_frequency_deterministic_v1` scorer semantics?

## Experiment Contract

- Config: `configs/experiments/gan_s0_qwen35b_direct_cap25_guardrails_validation.json`
- Model: `configs/models/gan_s0_qwen35b_ollama.json` (`max_tokens=256`)
- Dataset/split: `gan_2026_fixed_v1:validation` (first 25 validation records)
- Program variant: `gan_frequency_s0_direct_single_pass`
- Prompt version: `gan_frequency_s0_direct_guardrails_v1`
- Scorer: `gan_frequency_deterministic_v1`
- Run artifact: `runs/gan_s0_qwen35b_direct_cap25_guardrails_validation_20260519T071524Z`

## Results

| Metric | Post-guardrails cap-25 (this run) |
| --- | ---: |
| Records predicted | 25 |
| Schema-valid prediction rate | 84.0% |
| Valid / invalid predictions | 21 / 4 |
| `normalization.invalid_label` | 4 |
| Normalized-label accuracy (on valid) | 28.6% |
| Monthly-frequency accuracy (on valid) | 33.3% |
| Purist category accuracy (on valid) | 33.3% |
| Pragmatic category accuracy (on valid) | 61.9% |
| Evidence quote support (on valid) | **100.0%** |
| Evidence offsets present / valid | 100.0% / 100.0% |
| Prediction seconds / record | 12.43 |
| Model residency | 74%/26% CPU/GPU (context=4096) |
| Token usage (Ollama via LiteLLM) | 34,017 prompt / 1,216 completion |

## Invalid-Label Shape (Unchanged Failure Modes)

All four invalid predictions are semantic or structural, not repaired by the new
surface guardrails:

| Record | Predicted | Reason |
| --- | --- | --- |
| `gan_10052` | `4 cluster per 3 month` | Incomplete cluster (gold requires `multiple per cluster`) |
| `gan_1794` | `"6 per 2 month"` | Quoted numeric label still invalid after strip attempt |
| `gan_4702` | `4 per hour` | Forbidden `hour` unit |
| `gan_4709` | `6 per hour` | Forbidden `hour` unit |

No `few`, `several`, `quarter`, `fortnight`, or hyphen-range invalid labels
appeared on this cap slice.

## Evidence Guardrails

- Zero `evidence_support_errors` on valid predictions.
- No `evidence_repaired:prompt_footer_stripped` or
  `evidence_repaired:truncated_to_note_span` flags were needed on this slice,
  which suggests the cap did not hit the long-evidence / prompt-footer failure mode
  observed in the full-validation `max_tokens=1024` comparison.
- 100% evidence quote support on valid predictions is the main positive signal from
  this rerun: direct Qwen outputs on this slice were source-grounded when schema-valid.

## Interpretation

The post-guardrail direct path did not eliminate invalid labels on this cap, but
the invalid set matches the documented semantic boundary (clusters, forbidden
units, quoted surfaces) rather than the surface forms the new bridge targets.

Evidence support reached 100% on valid predictions for this cap, which supports
keeping the evidence-length guardrails as default direct-path behavior even when
they do not fire on every record.

Label-quality metrics remain low on this slice (`28.6%` normalized-label exact),
consistent with the overnight full-validation finding that Qwen3.6:35b's main gap
is temporal/window reasoning and abstention boundaries, not evidence span repair
alone.

## Comparison Caveat

The pre-guardrail overnight cap-25 artifact
(`runs/gan_s0_overnight_qwen35b_direct_cap25_20260518T222114Z`) is not present in
this workspace, so a direct metric delta was not computed here. A full-validation
rerun remains the stronger comparison if artifact parity is required.

## Next Steps

1. Optional: rerun Qwen3.6:35b direct full validation with the same guardrails to
   quantify invalid-label and evidence deltas against
   `runs/gan_s0_overnight_qwen35b_direct_full_validation_20260518T223713Z`.
2. Proceed with hosted-path Gan GEPA capped comparison against the synthesis-backed
   baseline before opening the ReAct temporal-tools probe.
3. Decide whether semantic Gan work should move to verifier/repair or abstention
   calibration rather than additional deterministic bridge rules.

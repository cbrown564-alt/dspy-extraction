# Gan S0 ReAct Temporal-Tools Slice — H3 Interleaving Probe

Date: 2026-05-20  
Status: **Reject** for default Gan S0 path; keep as interleaving-position negative control  
Run: `runs/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails_20260520T173943Z`

## Taxonomy

- **Hybrid balance class:** `H3_interleaved_tool_hybrid`
- **Interleaving positions:** `tool_during`, `during`
- **Comparison group:** `gan_s0_hard_slice_qwen_architecture_v1`
- **Varied factor:** `interleaving_position` (tools during reasoning vs pre-injected candidates)

## Hypothesis tested

Bounded `dspy.ReAct` with deterministic temporal tools (max 4 iterations) + ChainOfThought
extract would improve the 14-record hard slice versus direct guardrails, without collapsing
schema validity or evidence support.

## Headline results (14-record slice, same scorer)

| Metric | ReAct H3 | Direct v2.2 (L1) | Temporal-candidates B1 (H2/H4) |
| --- | ---: | ---: | ---: |
| Schema-valid predictions | **7/14 (50%)** | 14/14 | 14/14 |
| Monthly (valid only) | **3/7 (42.9%)** | 10/14 (71.4%) | 14/14 (100%) |
| Purist (valid only) | 4/7 (57.1%) | — | 14/14 |
| Evidence support (valid) | 7/7 (100%) | 100% | 100% |
| ~Seconds / record | **~93** | lower (single pass) | higher (verify-repair) |

Benchmark-facing metrics use valid-prediction denominators only. ReAct invalid rate
dominates the story: half of records never reached scorable canonical labels.

## Interleaving-position interpretation

**Pre-injected deterministic candidates (H2/H4) beat tool-during reasoning (H3) on this slice.**

Temporal-candidates v1.1 supplies structured candidate context *before* LLM verify/repair
and achieves perfect slice monthly accuracy. ReAct exposes the same temporal rules as
callable tools *during* the loop but:

1. **Tool loop did not substitute for preconditioning** — `find_temporal_frequency_candidates`
   often returned empty; the agent then improvised labels without full `N per M unit` format.
2. **Tool API friction** — 6/14 trajectories include `extract_temporal_anchors` failures
   (`Arg spans is not in the tool's args`), burning iterations without usable anchors.
3. **Structured-output gap** — no provider JSON schema; extract step emitted bare counts
   (`5`, `9`, `3 to 4`) that fail Gan label validation.
4. **Latency** — ~93 s/record with ~3.7 tool calls/record (max 4); poor cost/quality vs B1.

Evidence support on *valid* predictions remains 100%, so failures are primarily **label surface /
schema**, not quote grounding — unlike early direct paths before guardrails.

## Failure modes (invalid / miss)

| Pattern | Records (examples) | Count |
| --- | --- | ---: |
| Unsupported partial label | `gan_10410` (`3 to 4`), `gan_12810` (`5`), `gan_12823` (`9`) | 5 invalid |
| Abstain / missing value | `gan_10509`, `gan_14881` | 2 invalid |
| Semantic miss (valid) | `gan_10003`, `gan_11221`, `gan_12130`, `gan_15306` | 4 monthly misses |

Infrequent-quantified targets (`gan_13123`, `gan_14485`, `gan_14881`, `gan_15306`) did not
show the B1-style unlock; ReAct did not outperform direct on infrequent quantification.

## Runtime

- Total: ~21.7 min for 14 records
- Model residency: 74%/26% CPU/GPU
- Tokens (history): ~48k total

## Decision

**Reject** as a Gan S0 architecture candidate. Do not scale to full validation.

**Research conclusion:** For Gan temporal frequency on Qwen35b, deterministic temporal
knowledge belongs **before** LLM adjudication (H2/H4), not as an interleaved tool loop (H3)
under strict JSON/Pydantic label constraints. A follow-up engineering fix (tool signatures,
post-tool structured extract, or pre-loop candidate injection into ReAct context) is optional
forensics, not a promotion path unless slice schema validity recovers to ≥90%.

## Artifacts

- Config: `configs/experiments/gan_s0_qwen35b_react_temporal_tools_regression_slice_guardrails.json`
- Compare: `docs/experiments/gan/gan_s0_qwen_regression_slice_three_way_walkthrough_20260519.md`
- B1 slice: `runs/gan_s0_qwen35b_temporal_candidates_verify_repair_regression_slice_guardrails_20260519T232514Z`

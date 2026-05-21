# Gan S0 Verify-Repair Cap-25 v2 Inspection (2026-05-19)

## Purpose

Compare extraction-only direct extraction against verifier/repair **v2** (`gan_frequency_s0_direct_verify_repair_v2`) on the same 25-record GPT 4.1-mini validation cap used in the v1 inspection.

## Artifacts

- Direct extraction-only: `runs/gan_s0_direct_cap25_gpt4_1_mini_20260519T081439Z`
- Verify-repair v1: `runs/gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T081441Z`
- Verify-repair v2: `runs/gan_s0_verify_repair_cap25_gpt4_1_mini_20260519T084511Z`

## Headline Comparison (v2 vs direct)

| Metric | Direct | Verify-Repair v1 | Verify-Repair v2 | v2 vs direct |
|--------|--------|------------------|------------------|--------------|
| Schema validity | 92.0% | 92.0% | 92.0% | 0.0 pp |
| Normalized-label exact | 26.1% | 21.7% | **26.1%** | **0.0 pp** |
| Monthly-frequency accuracy | 34.8% | 39.1% | 34.8% | 0.0 pp |
| Purist category accuracy | 47.8% | 52.2% | 47.8% | 0.0 pp |
| Pragmatic category accuracy | 69.6% | 69.6% | 69.6% | 0.0 pp |
| Evidence quote support | 34.8% | 31.8% | **91.3%** | **+56.5 pp** |
| Unsupported evidence errors | 15 | — | **2** | −13 |

## Promotion Gate (kanban)

| Criterion | Met? |
|-----------|------|
| Exact-label accuracy ≥ direct | Yes (tied at 26.1%) |
| Evidence support ≥ direct | Yes (91.3% vs 34.8%) |
| Zero correct→wrong regressions | Yes — `gan_4956` now **confirmed** (`seizure free for 7 month`) instead of v1 repair to `no seizure frequency reference` |

v2 clears the stated promotion gate on this cap. Monthly/Purist gains from v1 were not retained in v2, but v2 no longer regresses exact-label accuracy versus direct extraction.

## Key v2 Behavioral Changes

- **`gan_4956`**: v1 destroyed a correct `seizure free for 7 month` label; v2 **confirms** it unchanged.
- **Evidence**: v2 strips wrapper quotes and preserves note-contained spans far more often (unsupported-quote count 15 → 2 vs direct).
- **Verifier activity**: fewer aggressive repairs to `unknown` / `no seizure frequency reference`; more `confirm` decisions on already-valid labels.

## Remaining Issues

- Label accuracy remains low on both paths (~26% exact on this hard cap); verify-repair is not yet a label-accuracy lever.
- `gan_14485`, `gan_14881`, `gan_15306` still show semantic/temporal errors similar to direct extraction.
- Two invalid predictions persist (`gan_10052` incomplete cluster repair, `gan_1584` unsupported cluster suffix).

## Conclusion

Prompt v2 fixes the highest-priority v1 failure modes (seizure-free canonicality, evidence preservation) and meets the kanban promotion gate on this cap. Verify-repair is still **not** promoted as the default Gan S0 path until a larger validation rerun confirms the evidence and regression gains hold at scale.

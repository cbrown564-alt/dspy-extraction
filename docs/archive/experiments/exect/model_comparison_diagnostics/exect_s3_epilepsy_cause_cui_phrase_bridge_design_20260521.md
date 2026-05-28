# ExECT S3 Epilepsy Cause CUIPhrase Bridge — Design (First Sparse-Family Scaffold)

Date: 2026-05-21  
Status: Fixture-first design (no cap-25 model spend until tests pass)  
Parent: `exect_s1_s3_residual_targeted_actions_20260521.md` (P0)  
Policy: `exect_s4_sparse_family_surface_policy_20260521.md` — annotation-faithful + bridges before sweeps  
Primitive ID: `exect.epilepsy_cause.cui_phrase_bridge.v1` (`family_backlog.py`, status planned)

## Question

What deterministic mappings improve `epilepsy_cause` surfaces on the qualitative queue **without** changing scorer overlap semantics or deduplicating across comorbidity?

## Why this family first

| Criterion | `epilepsy_cause` | `onset` | `when_diagnosed` | `birth_history` |
| --- | --- | --- | --- | --- |
| Validation support | 7 | 3 | 4 | 8 |
| Overlap complexity | High (cause vs comorbidity) | High (timing leakage) | High (`epilepsy` slot) | Medium |
| Queue coverage | EA0150, EA0016, EA0137, EA0059 | EA0137, EA0143 | EA0143, EA0150 | EA0137, EA0188 |
| Existing partial logic | S3 prompt overlap policy | `_ONSET_TIMING_PHRASES`, reroute | timing-slot leakage | paraphrase |

Cause has the **clearest synonym-table wins** (stroke/strokes, meningitis variants, TBI vs traumatic) with preregistered overlap rules in `exect_s3_phase1_overlap_policy.md`.

## No-model residual taxonomy (GPT S3 full, cause family)

| Bucket | Tag | Examples (queue docs) |
| --- | --- | --- |
| Surface expansion | scorer-surface | `early life meningitis` vs gold `meningitis` (EA0059) |
| Composite vs atomized | atomization | `traumatic brain injury` vs `traumatic` (EA0150) |
| Modifier specificity | scorer-surface | `recurrent right hemisphere intracerebral haemorrhage` vs `intracerebral haemorrhage` (EA0170) |
| Cross-family placement | cross-family-overlap | Phrase in comorbidity vs cause (EA0016 stroke/CVA) |
| Template prose | scorer-surface | `secondary to measles` vs `measles` (EA0124) |

**Do not** use pooled S3 micro (72.1%) as promotion metric. Per-family F1 on 7 labels is unstable; require **fixture clearance + qualitative queue**.

## Bridge contract (draft)

**Input:** raw `epilepsy_cause` labels + note text (optional evidence quote)  
**Output:** list of affirmed CUIPhrase surfaces present in gold loader vocabulary for validation split  
**Flags:** `s3_bridge:cause_surface_mapped`, `s3_bridge:cause_atomized`, `s3_bridge:cause_overlap_preserved`

**Non-goals:**

- Remove duplicate predictions in comorbidity when gold scores both
- Infer cause from diagnosis subtype alone (per backlog caveat)
- Map age/year attributes (not benchmark labels in Phase 1)

## Tiered mapping tables (fixture-driven)

| Tier | ID | Rule class | Example mapping |
| --- | --- | --- | --- |
| **K0** | `cause_synonym_plural_v1` | Singular/plural + British/American | `strokes`→`stroke`, `haemorrhage`→`hemorrhage` where gold uses US |
| **K1** | `cause_modifier_strip_v1` | Drop non-gold modifiers when base in note | `early life meningitis`→`meningitis` if gold `meningitis` |
| **K2** | `cause_tbi_atomized_v1` | When gold atomized `traumatic`, emit atom not composite | EA0150 |
| **K3** | `cause_template_strip_v1` | `secondary to X`→`X` when gold is bare entity | EA0124 measles |

Implement **K0 + K1** first in `src/clinical_extraction/programs/exect_s3.py` `_recover_s3_epilepsy_cause_raw_values` (new function mirroring comorbidity recovery).

## Fixture cases (required before any model run)

| case_id | Doc | Input label(s) | Expected output | Tags |
| --- | --- | --- | --- | --- |
| EC-0150-tbi | EA0150 | `traumatic brain injury` | `traumatic` (not composite) if note supports atomized gold | atomization |
| EC-0016-cva | EA0016 | `cerebrovascular accident` | map toward `cva` / `stroke` per gold atoms | scorer-surface |
| EC-0059-meningitis | EA0059 | `early life meningitis` | `meningitis` | K1 |
| EC-0124-measles | EA0124 | `secondary to measles` | `measles` | K3 |
| EC-0170-ich | EA0170 | long ICH phrase | `intracerebral hemorrhage` (gold spelling) | K0+K1 |
| EC-overlap-keep | EA0016 | same phrase in comorbidity + cause | comorbidity list unchanged; cause mapped independently | cross-family-overlap |

Store under `tests/fixtures/exect_s3_epilepsy_cause_bridge/` or inline in `test_exect_s3_epilepsy_cause_bridge.py`.

## Promotion gates

| Stage | Gate |
| --- | --- |
| Fixtures | All EC-* cases pass; no comorbidity field changes unless preregistered |
| S3 cap-25 | `epilepsy_cause` F1 ≥ +3pp vs `…235439Z` **or** ≥3 net label fixes on queue with investigation/seizure regression guards |
| S4 port | Same bridge on S4 artifact path; per-family F1 on 7 labels + no ≥2pp regression on MT/frequency/investigation |
| Model sweep | Deferred until K0+K1 promote on deterministic path |

## Overlap policy (unchanged)

From `exect_s3_phase1_overlap_policy.md`:

- Prefer `epilepsy_cause` when note frames aetiology of epilepsy
- Prefer `comorbidity` for ongoing PatientHistory conditions
- `exect.comorbidity.overlap_policy.v1` is a **separate** follow-on primitive — do not merge into K0–K3

## Open cells

- Gold vocabulary extraction script from validation JSON (affirmed EpilepsyCause CUIPhrases)
- birth_history / onset / when_diagnosed bridge order after cause promotes
- Whether K2 TBI rules share code with S2 comorbidity C0

## Next steps

1. `tdd`: fixtures EC-* → implement `_recover_s3_epilepsy_cause_raw_values` with K0+K1.
2. Wire into S3 program artifact builder (post-LLM, pre-score).
3. Qualitative re-tag EA0150, EA0016, EA0137 on dry-run predictions.
4. Prereg S3 cap-25 only after fixtures green — `implementation_variant: cause_bridge_k0_k1_v1`.
5. Update `taxonomy_primitive_catalog.md` status planned → `diagnostic_only` when implemented.

**No model API calls** until step 4 prereg exists.

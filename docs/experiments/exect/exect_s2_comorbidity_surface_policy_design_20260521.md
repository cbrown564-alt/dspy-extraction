# ExECT S2 Comorbidity Surface Policy — Design

Date: 2026-05-21  
Status: Design ready for fixture tests + cap-25 prereg  
Parent: `exect_s1_s3_residual_targeted_actions_20260521.md` (P0)  
Residual queue: EA0150, EA0179, EA0170, EA0136, EA0090, EA0148, EA0188  
Anchor: `runs/exect_s2_validation_full_gpt4_1_mini_20260519T231223Z` (comorbidity **69.3%** F1, 18 FP / 13 FN)  
Existing repair: S2 v1.3 `jerk` removal in `_recover_s2_comorbidity_raw_values`

## Question

Can deterministic **post-module comorbidity bridges** improve comorbidity F1 on S2 without regressing seizure_type or investigation — by addressing atomization and surface mismatch rather than broad prompt churn?

## No-model FP/FN taxonomy (GPT full validation)

| Bucket | Share of burden | Tag | Examples | Notes |
| --- | --- | --- | --- | --- |
| Composite vs atomized gold | ~35% | atomization | EA0150: `traumatic brain injury` FP vs `traumatic`, `brain injury` FN | Semantically close; scorer exact-match |
| British/American + plural | ~15% | scorer-surface | EA0170: haemorrhage/hemorrhage | |
| Modifier stripping | ~10% | scorer-surface | EA0179: `mild learning disabilities` vs `learning disabilities` | Partially fixed in code for learning difficulties |
| Scope / symptom leakage | ~15% | over-extraction | EA0090: `headache`; EA0148: reflux/smoking | |
| Large recall blocks | ~20% | scorer-surface | EA0179: episodes/syncope/febrile block | Prompt recall risky |
| Missing-gold | — | gold-quality-caveat | EA0078, EA0100 | Exclude from training |

**Partial infrastructure:** `_recover_s2_comorbidity_raw_values` already atomizes `stroke` → cva/hemiparesis/infarct when note supports (`s2_bridge:stroke_atomized`). Extend this pattern; do not replace with LLM repair.

## Proposed primitive

**ID:** `exect.comorbidity.atomization_bridge.v1` (new; distinct from planned `exect.comorbidity.overlap_policy.v1` which handles cause vs comorbidity framing)

**Placement:** post-module after LLM extract, same lane as S1 inline bridges (`H1_post_deterministic`).

## Tiered `implementation_variant` arms

| Tier | ID | Action | Target docs | Recall risk |
| --- | --- | --- | --- | --- |
| **C0** | `comorbidity_atomization_stroke_v1` | Extend stroke atomization (existing) + add TBI split: `traumatic brain injury` → `traumatic`, `brain injury` when note affirms trauma lexicon | EA0150, EA0016 | Low if both atoms in note |
| **C1** | `comorbidity_surface_plural_v1` | Map hemorrhage↔haemorrhage, infarct↔infarcts for affirmed mentions | EA0170 | Low |
| **C2** | `comorbidity_modifier_strip_v1` | Strip mild/moderate/severe before learning difficulties (generalize existing rule) | EA0179 | Medium |
| **C3** | `comorbidity_symptom_scope_v1` | Drop isolated headache/gastroesophageal reflux/smoking unless PatientHistory-affirmed patterns match | EA0090, EA0148 | Medium — needs affirmed mention regex |

**First grid:** L1 vs C0 vs C0+C1 only. Add C3 only if F1 guard passes.

### C0 TBI atomization (draft rules)

When canonical == `traumatic brain injury` (or `tbi`):

- If note contains `traumatic` and (`brain injury` or `head injury` or `tbi`): emit atomized labels present in gold audit set
- Do **not** remove composite if gold uses composite only (check per-doc in fixtures)

### Overlap with S3/S4

- `exect.comorbidity.overlap_policy.v1` (planned): routes aetiology phrases to `epilepsy_cause` vs comorbidity — run **after** C0 atomization is baselined
- Same queue docs (EA0150, EA0016) feed both tracks; tag separately in qualitative queue

## Cap-25 prereg gates (draft)

| Metric | Gate |
| --- | --- |
| Primary | `comorbidity` F1 vs S2 v1.3 cap-25 or full baseline prefix |
| F1 guard | Comorbidity F1 ≥ +3pp vs L1 on cap-25 **or** ≥2 net label fixes on 6-doc queue with zero regressions |
| Regression | seizure_type, investigation, diagnosis each within −2pp vs L1 |
| Proceed to full | Cap-25 winner + qualitative clearance on EA0150, EA0170 |

Comparison group: `exect_s2_comorbidity_surface_bridge_gpt_cap25_v1`

## Fixture documents (required before model spend)

| Doc | Must demonstrate |
| --- | --- |
| EA0150 | TBI atomization improves comorbidity without dropping seizure labels |
| EA0170 | hemorrhage plural canonicalization |
| EA0179 | modifier strip does not delete affirmed `learning disabilities` |
| EA0148 | C3 does not remove affirmed `head injuries` when note supports |

## Open cells

- Note-level `_augment_s2_comorbidity_from_note` interaction with bridges
- Whether C0 rules promote to S3 program unchanged or S3-specific overlap pass
- Recall-block FNs (EA0179) — likely need prompt/example policy, not bridge-only

## Next steps

1. Implement C0 + tests (`tdd`) in `exect_s2.py` recovery path.
2. Prereg comparison group with `decision_scope: arm`.
3. Cap-25 L1 vs C0 vs C0+C1; inspection doc.
4. Full validation only for cap-25 winner.

**Do not** broad S2 prompt retuning on validation as first move.

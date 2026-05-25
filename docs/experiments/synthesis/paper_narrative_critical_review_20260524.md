# Paper Critical Review — Current Narrative

Date: 2026-05-24  
Reviewed artifact: [paper_narrative_current_20260524.md](paper_narrative_current_20260524.md)  
Skill: `paper-critical-review`  
Evidence checked: D1/D2/D3 freeze pack, `paper_result_table_pack_20260524.md`, v2b promotion review, `kanban_plan.md`, `docs/outline.md`

---

## Apparent Thesis

Hybrid clinical extraction pipelines must place deterministic and LLM stages according to **task bottleneck shape** (Gan = pre-LLM candidate recall; ExECT = broad LLM extraction + post-LLM benchmark bridges), and rigorous progress requires **arm-vs-mechanism discipline** with frozen scorers and explicit negative results—not a universal hybrid recipe or benchmark-beating claim on synthetic validation.

---

## Strongest Parts

1. **Traceability discipline.** Run IDs, splits, scorers, and config paths travel with headline numbers. The companion freeze pack (D1–D3, table pack) is unusually strong for an early manuscript skeleton.

2. **Honest benchmark distance.** The narrative repeatedly blocks published Gan Real(300) and CUI-aware ExECT reproduction claims. That protects credibility.

3. **Negative results as first-class evidence.** The 24-row arm-reject table and Tier 1 Pathway A/C closures give the paper a control structure many extraction papers lack.

4. **Cross-dataset interpretive frame.** The Gan vs ExECT placement contrast (pre-LLM vs post-LLM determinism) is the clearest empirical theme and is well supported by operational defaults plus rejected decomposition arms.

5. **Claim readiness matrix.** Pre-emptive labeling of risky claims (`Qwen matches GPT`, clinical deployment) reduces accidental overclaim during drafting.

---

## Major Risks

| Risk | Severity | Evidence | Fix |
| --- | --- | --- | --- |
| **Result–story mismatch with original project goal** | P1 | `docs/outline.md` Goal 1: "Beat the benchmarks"; paper correctly says that is blocked/unsupported | **Scope loop:** Reframe as a *methods + controlled negative-evidence* paper; move benchmark-beating to future work explicitly in abstract/intro |
| **Gan mechanism claim outruns isolation** | P1 | Mid-60s → 80.6% compares eras with multiple moving parts (builders, adjudication policy, program surface); no single-factor ablation isolating builders alone | Soften to "consistent with recall bottleneck"; add ablation table or name confounds in Methods |
| **ExECT n=40 validation for broad phenotyping claims** | P1 | All ExECT ladder/S5 numbers on fixed 40-record split | State n prominently in every ExECT table; avoid population-level wording; discuss variance/bootstrap or holdout need |
| **S5 vs S4 ladder confuses readers** | P1 | S4 pooled micro 65.5% vs S5 85.8% on overlapping but non-equivalent surfaces (S5 excludes MT, adds verifier stack, different program) | Dedicated subsection defining S5 as a **diagnostic five-family surface**, not "S4 improved" |
| **Local-model story incomplete at newest promoted stack** | P1 | Kanban P0: zero Qwen runs on S5 v2b; narrative notes this but still lists local transfer as Contribution 5 | Run L1.1 before drafting Results local-model subsection; or demote local-model to Discussion future work |
| **Evidence support 100% misread risk** | P1 | Gan GPT row: 100% evidence support; metric is deterministic quote grounding | Define metric once in Methods; never imply clinical evidence adequacy |
| **Arm-vs-mechanism as contribution may feel internal** | P2 | Valuable to project; external reviewers may ask "so what for readers?" | One worked example figure: failed arm → revised hypothesis → promoted default |
| **Model suite underrepresented** | P2 | Frozen model-suite synthesis exists but narrative centers GPT 4.1-mini + Qwen only | Add compact model-profile table (S1/S4/Gan F0) to support "surface-dependent" claim |
| **GPT 4.1-mini vs original Qwen-primary plan** | P2 | Outline centers Qwen3.6:35b; most promoted arms are GPT-validated | Explain iteration economics in Methods; don't imply Qwen was primary evaluation model |
| **Schema ladder framed as difficulty curve** | P2 | Narrative says "breadth pressure, not learning curve" but tables still invite curve reading | Rename axis in figures: "field-family scope" not "level difficulty" |

---

## Claim Audit

| Claim | Support | Problem | Needed revision |
| --- | --- | --- | --- |
| Task-dependent hybrid placement is the main empirical finding | **Strong** | Cross-dataset table + rejected opposite placements (section split, prompt-only Gan repair) | Keep; make this the title-level claim |
| Gan builder-gap v1 is best internal Gan S0 surface (80.6% monthly) | **Strong** | Full validation, promotion review, run ID verified | Keep with synthetic-validation caveat every time |
| Deterministic pre-candidates *caused* Gan lift from mid-60s | **Thin** | Historical anchors confounded; no isolated builder-only ablation on same program | Rewrite: "coincided with" or cite specific recall audit + builder coverage stats |
| ExECT S1 single-pass + bridges is best decomposition | **Strong** locally | cap-25 grid evidence stronger than n=40 full validation for decomposition | Report both scopes; cap-25 as search, full as anchor |
| Schema breadth increases difficulty S1→S4 | **Strong with caveat** | Field sets change; not same task with more fields | Keep caveat in table captions |
| S5 v2b stack (85.8% micro, 73.9% freq) is operational best | **Strong** | v2b promotion review + metrics.json | Keep; note incremental +1.6pp freq gain vs v1 |
| Qwen transfers some surfaces | **Strong** | Gan + S1–S4 runs exist | Keep non-parity wording |
| Qwen viable for deployment | **Overclaim** | S1 −13.3pp seizure type; S5 untested | Remove deployment implication |
| Arm-vs-mechanism improves interpretability | **Unclear externally** | Process contribution; needs reader-facing payoff | Add 1-page case study from D2 Tier 1 |
| Negative arms prove optimizers/decomposition don't help generally | **Overclaim** | Arm-level only; mechanism classes open per pivot doc | Always pair with `decision_scope: arm` |
| Project beats published benchmarks | **Overclaim** | Explicitly blocked | Keep out of abstract entirely |
| 100% evidence support means extraction is evidence-grounded | **Overclaim** | Diagnostic metric | Define and downgrade wording |

---

## Narrative Coherence

**What works.** The document is organized around decisions (Gan mechanism closure, ExECT decomposition probes, S5 verifier promotion) rather than raw chronology. The cross-dataset bridge table is the strongest structural device.

**Coherence leaks.**

1. **Two papers in one outline.** The original outline promises benchmark superiority and broad ablation science; the frozen evidence supports hybrid methodology, task-specific placement, and negative controls on synthetic splits. The current narrative partially resolves this by emphasizing methodology, but the Introduction/Section Plan still reads like a full benchmark paper. Pick one primary venue story.

2. **S5 insertion breaks the ladder narrative.** A reader progressing S1→S4→S5 will infer monotonic improvement. S5 is a different experimental surface (five core families, verifier stack, no medication temporality). Without upfront definition, the 85.8% figure looks like "problem solved" after S4's 65.5%.

3. **Frequency appears in three incompatible frames.** Gan monthly accuracy (80.6%), ExECT S4 frequency F1 (45.7%), ExECT S5 frequency F1 (73.9%). The narrative warns metrics aren't comparable, but the Results section plan does not force separate subsections with distinct scorers and label policies. High risk of reader conflation.

4. **Local model thread starts strong, ends incomplete.** Gan and S1–S4 Qwen rows support "surface-dependent transfer," but the newest promoted stack (S5 v2b) is GPT-only. The local-model contribution should not headline until L1.1 runs.

5. **Methodological contribution vs engineering volume.** "204 registry experiments" impresses internally but may read as sprawl. The narrative needs 2–3 canonical decision arcs, not registry scale, as the persuasion unit.

---

## Methodological Rigor

**Strengths**

- Frozen deterministic scorers and explicit split names.
- Preregistered gates and cap-25 vs full-validation distinction (when honored in prose).
- Promotion reviews with gate tables (v2b exemplar).
- Dataset audits referenced at claim points.

**Weaknesses**

| Issue | Rigor impact |
| --- | --- |
| No test holdout (D4 deferred) | External validity unknown |
| ExECT n=40 | Wide confidence intervals; family F1 unstable |
| Gan n=299 but single synthetic domain | Better than ExECT but still not Real benchmark |
| Confounded historical Gan comparisons | Mechanism inference weak |
| S1 bridge vs prompt policy bundled | Causal attribution incomplete (acknowledged in weak points) |
| Cap-25 optimistic bias | Must never appear unlabeled in Results |
| Model comparison limited to 2 local/closed models on most surfaces | GPT 5.5 / Gemini suite frozen but not integrated into main argument |
| No human evaluation of evidence quality | Evidence metric is necessary but insufficient |

---

## Recommended Revision Loop

**Primary loop type:** `Scope loop` + `Writing loop` (narrow thesis before drafting prose)

1. **Narrow the thesis in abstract and intro** to: controlled hybrid exploration under benchmark policy on synthetic validation, with task-dependent placement as the empirical finding. Demote benchmark-beating to explicit non-claim.

2. **Add one "S5 is not S4" exposition box** in Data/Methods: five-family diagnostic surface, excluded fields, verifier stack, scorer mode. Prevent ladder misread.

3. **Soften Gan causal language** unless a single-factor builder ablation exists. Pair performance story with Pathway C residual taxonomy (semantic mismatch vs builder coverage).

4. **Run Qwen S5 v2b transfer (L1.1)** before writing the local-model Results subsection—or move entire local-model block to Discussion as "in progress."

5. **Promote n=40 and synthetic-only warnings** into table captions and abstract, not only Limitations.

**Secondary loops (if time permits)**

- `Analysis loop`: one figure — three canonical decision arcs (Gan builder-gap, ExECT S1 decomposition reject, S5 v2b isolation).
- `Experiment loop`: only if Gan mechanism causality is central; otherwise narrowing prose is cheaper.
- `Traceability loop`: pre-submission `metrics.json` reverification (already listed).

---

## Highest-Risk Unsupported Claim

**"Deterministic candidate builders closed documented recall gaps" as the Gan mechanism explanation** — performance lift is well documented, but the manuscript currently implies causal closure from historically confounded comparisons. A skeptical reviewer will ask for an isolated ablation (builders on/off with fixed adjudication) or demand softer wording.

---

## Next Loop

**Writing + scope control** first; **one experiment** (Qwen S5 v2b) only if the local-model thread stays in Contributions.

### Three concrete next actions

1. Rewrite abstract/thesis to lead with **synthetic validation + methodology**, not benchmark superiority.
2. Insert **S5 surface definition** and **frequency metric separation** before any Results tables.
3. Execute **L1.1 Qwen S5 v2b full validation** or remove local-model parity from Contributions until it completes.

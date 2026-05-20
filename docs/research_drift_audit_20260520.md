# Research Drift Audit — Status Update

Date: 2026-05-20  
Audit type: alignment check against core research plan  
Active tracker: `docs/kanban_plan.md`  
Prior audit: `docs/research_drift_audit_20260519.md` (May 19 dual-track refresh)  
Frozen-thread anchors: `docs/kanban_frozen_threads_history.md`  
Narrative archive: `docs/research_status_recap_20260519.md`

## Research Question

Is the project still aligned with the hybrid deterministic + DSPy clinical extraction research plan in `docs/outline.md`, or has recent work drifted toward distractions, premature breadth, or ungoverned experimentation?

## Motivation

Since the May 19 audit, Gan temporal v1.1 completed Tier 1 promotion, the hosted GPT ExECT schema ladder (S1–S4) was frozen, and a pre-registered Qwen3.6:35b replication track started. A large working tree and live Ollama runs accumulated before the next commit. This refresh confirms alignment after the phase shift and flags operational risks (traceability, Ollama scheduling).

## Method

This audit followed the project `research-drift-audit` workflow:

1. **Core direction documents**
   - `docs/outline.md` — research goals, architecture layers, ablation plan
   - `docs/kanban_plan.md` — active tracker (refreshed 2026-05-20)
   - `docs/kanban_frozen_threads_history.md` — frozen Threads A–E
   - `docs/exect_qwen35b_ladder_replication_plan.md` — Qwen replication gates
   - `docs/research_drift_audit_20260519.md` — prior verdict and risks

2. **Recent git history** — HEAD `bfb157b` (May 19 Gan temporal + ExECT v4.2 sprint); May 20 work largely uncommitted at audit time.

3. **Run artifacts** — `runs/exect_s2_validation_full_qwen35b_ollama_20260520T073552Z`, `runs/exect_s4_validation_full_gpt4_1_mini_20260520T071248Z`, `runs/overnight_logs/exect_qwen35b_ladder_resume_20260520_083549.log`.

4. **Alignment axes** (from `docs/outline.md`):
   - benchmark reproduction and improvement
   - deterministic infrastructure before model complexity
   - Gan versus ExECT sequencing
   - reproducible experiments and ablations
   - local versus closed-model comparison
   - downstream use-case exploration

## Current Position

The project operates on **three coordinated threads** (see `docs/kanban_plan.md` § Execution Model):

| Track | Model | Role | Status (2026-05-20) |
| --- | --- | --- | --- |
| **A — Gan S0** | Qwen3.6:35b (local) | Temporal-candidates v1.1 + post–tier-1 engineering | Tier 1 signed; B1/B2 slice gates cleared; **ReAct probe pending** |
| **B — ExECT S1–S4** | GPT 4.1-mini (hosted) | Schema ladder frozen | **Frozen** — S1 v4.10, S2 v1.3, S3 v1.2, S4 v1.2 |
| **C — ExECT S1–S4** | Qwen3.6:35b (local) | Replicate frozen GPT ladder | **In progress** — Phase 0 pass; S2 full done; S3 cap-25/full queued |

**Do not compare across tracks as one experiment.** Same deterministic scorers within each dataset; anchors documented per track in `docs/kanban_frozen_threads_history.md`.

### Quality anchors (unchanged for cross-run claims)

| Path | Split | Headline | Notes |
| --- | --- | ---: | --- |
| Gan temporal v1.1 full (promoted) | 299 validation | 65.8% monthly | `…230324Z`; Tier 1 |
| GPT verify-repair v2 (Gan) | 299 validation | 65.4% monthly | Hosted quality ceiling |
| Qwen direct guardrails (Gan) | 299 validation | 55.9% monthly | Local baseline |
| ExECT S1 v4.10 full (GPT) | 40 validation | 92.3% micro F1 | Thread B frozen |
| ExECT S4 v1.2 full (GPT) | 40 validation | 65.5% micro F1 (11 fam) | Thread E frozen `…071248Z` |
| ExECT S2 full (Qwen) | 40 validation | **82.6%** micro F1 (5 fam) | `…073552Z`; vs GPT 80.9% — **separate track** |

Gan scorer: `gan_frequency_deterministic_v1`. ExECT scorers: `exect_s*_field_family_deterministic_v1`. Do not compare Gan monthly % to ExECT micro F1.

## Alignment Assessment

### Aligned with core objectives

**Deterministic infrastructure before model complexity.** Loaders, gold-source policies, normalization, splits, scorers, run artifacts, and evidence diagnostics remain stable. Runs carry explicit caveats (partial field families, not CUI-aware Table 1 reproduction).

**Modular specialization across tasks.** Gan (temporal frequency) and ExECT (broad schema ladder) remain distinct proving grounds with separate programs, promotion gates, and inspection docs.

**Gan as local optimization gate.** Tier 1 temporal path promoted; B1/B2 engineering bounded to regression slice with documented exits.

**Hosted GPT for rapid iteration; Qwen for local deployment.** ExECT label-policy micro-iteration on hosted GPT is **stopped** at frozen ladder versions; active ExECT model work is replication-only on Qwen per `docs/exect_qwen35b_ladder_replication_plan.md`.

**Reproducible experiments and ablations.** Dead-end paths remain closed (GEPA, section-aware, diagnosis-recall). New work is pre-registered (Qwen ladder phases, ReAct exit criteria, GPT temporal cap-25 tier gate).

**Local versus closed-model comparison.** Qwen S2 full exceeds frozen GPT S2 anchor on the same scorer/split — a useful separate-track finding for the local-model thesis; must not be reported as a single combined experiment.

### Appropriately deferred

| Item | Blocker / policy |
| --- | --- |
| Published benchmark reproduction | CUI-aware ExECT scorer; Gan Real(300)/Real(150) access |
| Architecture comparison matrix | Gan ReAct doc + GPT temporal cap-25 + Qwen Phase 0–1 reads |
| Downstream use cases | Outline Phase 6 — no implementation |
| GEPA / Gemini verify-repair scale-up | Deprioritized with negative evidence |
| Hosted ExECT S4 v1.3+ micro-iteration | Ladder frozen at v1.2 |

### Useful detour (evidence-backed)

| Detour | Outcome | Assessment |
| --- | --- | --- |
| ExECT S2→S4 schema ladder (hosted GPT) | Frozen threads C–E with inspection docs | **Aligned** — outline broad-schema path |
| Gan B1/B2 after Tier 1 | 14/14 slice gates | **Aligned** — pre-registered engineering fork |
| Qwen S2 full > GPT S2 full (+1.7pp micro F1) | `…073552Z` vs `…231223Z` | **Useful** — document per-track |
| S1 v4.3–v4.10 implementation docs | Ladder to v4.10 freeze | **Traceability** — not active iteration |

## Drift Signals

| Signal | Present? | Assessment |
| --- | --- | --- |
| Implementation without Kanban card | No | Gan fork + Qwen ladder + frozen threads mapped |
| Model runs before scorer/data contracts stable | No | Scorers held constant per dataset |
| UI/tooling dominating | No | No review UI work |
| Narrow task expanding into broad architecture | No | S2–S4 ladder was planned; architecture ablation deferred |
| Cross-run claims without scorer caveats | Mostly no | Replication plan and run caveats enforce separation |
| Optimizer path persisting after negative evidence | No | GEPA deprioritized |
| **Large uncommitted working tree** | **Yes** | Traceability risk until this commit |
| **Ollama scheduling vs sprint order** | **Mild** | Qwen resume queue ran while ReAct pending; operational, not policy drift |

## Divergences vs May 19 Audit

| May 19 issue | May 20 status |
| --- | --- |
| Gan full validation incomplete | **Resolved** — Tier 1 signed (`…230324Z`) |
| Parallel ExECT during Gan run | **Evolved** — hosted ladder **complete and frozen**; active ExECT = Qwen replication only |
| ExECT v4.2 as anchor | **Superseded** by v4.10 + S2–S4 ladder (frozen threads) |
| Documentation lag | Partially improved — slim kanban + frozen-thread archive |

## Unresolved Risks

### 1. Ollama contention (operational)

Kanban sprint order: Gan ReAct slice (dedicated Ollama) before parallel Qwen + GPT temporal. Resume queue consumed GPU for ExECT Qwen while ReAct remains pending. Risk: delayed Gan fork exit, not invalid cross-track comparison.

### 2. Qwen ladder incomplete reads

S3 cap-25/full and S4 replication may still be in flight at commit time. Phase 1 S1 Qwen (cap-25, slice, full) may be pending in queue. Promotion-style claims require completed runs + inspection docs.

### 3. Cap-25 optimism (interpretive)

S4 v1.2: 69.2% cap-25 vs 65.5% full. Full validation remains anchor for cross-version claims on hosted GPT; same discipline applies to Qwen reads.

### 4. Published benchmark gap (strategic)

In-repo best Gan monthly (~65.8%) and partial ExECT field-family F1 do not constitute ExECTv2 Table 1 or Gan Real(300) reproduction. Goal 1 in `docs/outline.md` remains open.

## Interpretation

**Verdict: the project remains aligned with the core research plan.**

Work has shifted from **optimization** (May 19: Gan temporal + parallel ExECT label-policy) to **freeze + replicate** (May 20: hosted ExECT ladder frozen; Qwen replication; bounded Gan engineering fork). That matches `docs/outline.md` and the refreshed kanban. The main alignment gap is still **beating published benchmarks**, which requires CUI-aware scoring and external Gan data.

**Dual- and triple-track execution is intentional** — provided each track keeps its own anchors, scorers, and promotion gates.

## Limitations of This Audit

- Based on artifacts and git/working-tree state as of 2026-05-20; live runs may advance after refresh.
- Did not re-run experiments; metrics from run artifacts and inspection docs.
- Uncommitted code assessed at file-list scope; not a line-by-line review of every module.

## Recommended Next Pull

**Continue (in order):**

1. Let ExECT Qwen S3/S4 queue finish — read vs frozen GPT anchors; report schema validity and evidence separately from F1.
2. **Gan ReAct slice** on dedicated Ollama — exit = non-regression + E-guard vs B2 `…235058Z`.
3. **GPT temporal-candidates cap-25** after ReAct pass — tiered gate per kanban.

**Do not start yet:**

- ExECT architecture ablation
- Hosted S4 v1.3+ or S1 v4.11+ micro-iteration
- Hosted Gan ReAct unless slice shows clear tool lift

**Pause / reframe if:**

- Qwen smoke/scale JSON contract fails — halt queue; try `strict_json_prompt` per replication plan
- ReAct regresses on E-guard — probe pass only; default to hosted temporal port

## Artifact References

### Planning and policy

- `docs/outline.md`
- `docs/kanban_plan.md`
- `docs/kanban_frozen_threads_history.md`
- `docs/exect_qwen35b_ladder_replication_plan.md`
- `docs/deterministic_foundation_decisions.md`
- `docs/deterministic_scorer_semantics.md`

### Prior audit

- `docs/research_drift_audit_20260519.md`

### Key runs (2026-05-20)

| Track | Run | Headline |
| --- | --- | --- |
| Gan Tier 1 full | `…230324Z` | 65.8% monthly |
| Gan B2 slice | `…235058Z` | 14/14 |
| ExECT S4 full GPT v1.2 | `…071248Z` | 65.5% micro F1 (11 fam) |
| ExECT S2 full Qwen | `…073552Z` | 82.6% micro F1 (5 fam) |

### Code (active workstream)

- `src/clinical_extraction/programs/exect_s2.py` — `exect_s3.py` — `exect_s4.py`
- `src/clinical_extraction/gan/react_tools.py`, `temporal_events.py`
- `scripts/run_overnight_exect_qwen35b_queue.ps1`, `run_overnight_exect_qwen35b_queue_resume.ps1`

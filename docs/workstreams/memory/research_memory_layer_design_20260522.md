# Research Memory Layer Design

Date: 2026-05-22
Status: Phase 2 template added
Related:

- `docs/outline.md`
- `docs/planning/kanban_plan.md`
- `docs/workstreams/hybrid/hybrid_pipeline_research_pivot_20260521.md`
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- `docs/experiments/synthesis/experiment_registry.json`
- `docs/research_atlas/evidence_matrix.md`
- `.agents/skills/skill-system-review/SKILL.md`
- `.agents/skills/research-synthesis/SKILL.md`

## Research Question

Can a Claude-Dreams-style memory consolidation layer add useful cross-session research memory to this repo without duplicating the existing Kanban, registry, inspection docs, or skills?

## Summary

Yes, but the memory layer should be a derived review surface, not a new source of truth.

The repo already has strong primary artifacts:

- session-level steering in `docs/planning/kanban_plan.md`
- experiment-level preregistration and inspection docs
- task-level skills under `.agents/skills`
- structured experiment inventory in `docs/experiments/synthesis/experiment_registry.json`
- visual/navigation exports in `docs/research_atlas/`
- policy and audit guardrails under `docs/policies/` and `docs/datasets/`

The missing layer is not another plan. The missing layer is compact, periodically regenerated memory that answers:

- What changed since the last session?
- Which decisions are operational defaults vs arm rejects vs open mechanisms?
- Which workflows keep recurring?
- Which docs must be read before touching a topic?
- Which claims are stale, duplicated, or overgeneralized?
- What should a future agent remember before doing new work?

The memory layer should therefore consolidate across existing artifacts and produce candidate memory files that are reviewed before promotion.

## Existing Repeated Workflows

### Skill-Guided Domain Workflows

The repo already uses project skills to route high-risk work:

| Workflow | Existing skill(s) | Memory implication |
| --- | --- | --- |
| Dataset or gold-label changes | `dataset-audit-first`, `gold-scorer-integrity` | Memory should point to the right audit and never summarize gold policy without source links. |
| Scorer, metric, and evaluation changes | `gold-scorer-integrity` | Memory should flag scorer-semantics changes and warn against cross-scorer comparisons. |
| DSPy program or experiment design | `dspy-experiment-design`, `experiment-run-lifecycle`, `hybrid-pipeline-exploration` | Memory should track active comparison groups, frozen controls, and current run gates. |
| ExECT benchmark-facing prompt/scoring work | `exect-label-policy-alignment` | Memory should preserve label-policy caveats and field-family boundaries. |
| Gan seizure-frequency analysis | `gan-frequency-error-forensics` | Memory should preserve recurring error classes and current F0/F1-style arm decisions. |
| Taxonomy and deterministic primitives | `taxonomy-primitive-design` | Memory should track primitive contracts, open primitive gaps, and validation commands. |
| Model/provider config work | `model-config-compatibility`, `windows-portability` | Memory should track provider quirks, local model constraints, and smoke-test status. |
| Planning and research synthesis | `plan-to-kanban`, `research-synthesis`, `research-drift-audit`, `research-supervisor-review` | Memory should reuse these outputs rather than creating a parallel planning doctrine. |
| Skill/process review | `skill-system-review`, `workstream-value-assessment` | Memory layer design and tuning should happen here. |

Recent git history reinforces these repeated clusters: model-suite configs and smokes, registry and Kanban updates, inspection/preregistration docs, taxonomy/primitive edits, skill edits, and research synthesis docs recur together. That is exactly the shape of work where memory consolidation can help.

### Repeated Experiment Lifecycle

The dominant lifecycle is:

1. identify a research question and comparison group
2. preregister fixed controls, arms, gates, scorer/evidence policy
3. add configs and sometimes scripts
4. run smoke/cap/full validation
5. inspect metrics and errors
6. write an inspection decision
7. update registry, Kanban, mechanism status, and sometimes skills
8. export or synthesize research-facing views

This lifecycle is already partially enforced by:

- `docs/templates/experiment_decision_template.md`
- `docs/templates/primitive_inspection_template.md`
- `src/clinical_extraction/experiments/inspection_templates.py`
- `src/clinical_extraction/experiments/registry_validation.py`
- `scripts/export_experiment_registry_matrix.py`
- `scripts/export_research_atlas.py`
- tests such as `tests/test_inspection_templates.py`, `tests/test_experiment_registry_validation.py`, and `tests/test_export_research_atlas.py`

The memory layer should not replace these. It should read their outputs and identify what a new session needs to know.

## Existing Documentation by Level

### Session-Level Sources

| Source | Role | Strength | Gap memory can fill |
| --- | --- | --- | --- |
| `docs/planning/kanban_plan.md` | Active execution board and next pulls | Excellent current-state steering | Long and operational; hard to quickly see "what changed since last time". |
| `docs/planning/kanban_frozen_threads_history.md` | Frozen run tables/history | Preserves prior decisions | Not optimized for fresh agent onboarding. |
| `docs/planning/research_status_recap_20260519.md` | Narrative archive | Good synthesis snapshot | Date-bound; can go stale without warning. |
| `docs/planning/research_drift_audit_*.md` | Alignment checks | Prevents scope drift | Not a daily compact memory. |

Memory add-on: `docs/memory/session_brief.md`, regenerated or reviewed after meaningful work, with current queue, changed decisions, blockers, and source pointers.

### Experiment-Level Sources

| Source | Role | Strength | Gap memory can fill |
| --- | --- | --- | --- |
| Preregistration docs | Experiment intent, controls, gates | Strong reproducibility contract | Hard to scan across many experiments. |
| Inspection docs | Outcomes and interpretation | Strong decision record | Distributed across folders and dates. |
| `experiment_registry.json` | Structured experiment rows | Machine-readable, validated | Dense; not enough narrative on stale claims or open mechanism questions. |
| `docs/research_atlas/*` | Registry-derived navigation | Good high-level map | Generated views summarize evidence, not workflow memory. |
| `runs/*` | Raw artifacts | Reproducibility anchor | Too low-level for session start. |

Memory add-on: derived decision caches such as `docs/memory/decision_cache.md`, `docs/memory/open_questions.md`, and `docs/memory/rejected_arms.md`.

### Task-Level Sources

| Source | Role | Strength | Gap memory can fill |
| --- | --- | --- | --- |
| `.agents/skills/*/SKILL.md` | Procedural guardrails | Excellent trigger-specific behavior | Skills know how to act, not always current status. |
| `docs/policies/*` | Stable semantics and reporting rules | Strong guardrails | Not enough "when this matters now" context. |
| `docs/datasets/*/*audit*.md` | Dataset-specific truth constraints | Essential for scorer/gold work | Large and specific; memory should cite, not rephrase loosely. |
| scripts/tests | Workflow automation | Good enforcement | Do not explain recent research meaning. |

Memory add-on: `docs/memory/workflow_index.md` mapping task types to skills, required docs, validation commands, and current caveats.

## Proposed Memory Layer

### Principle

Memory files are generated or manually curated summaries of source artifacts. They are not authoritative if they conflict with source docs, registry rows, audits, or run artifacts.

Each memory item should include:

- source paths
- last observed date
- status: `operational`, `arm`, `mechanism`, `open`, `blocked`, or `stale_check`
- confidence: `direct_source`, `inferred_from_sources`, or `needs_review`
- next action or "none"

### Suggested Directory

```text
docs/memory/
  README.md
  session_brief.md
  workflow_index.md
  decision_cache.md
  open_questions.md
  rejected_arms.md
  model_suite_status.md
  recurring_failure_modes.md
  dreams/
    20260522_initial_memory_review.md
```

### File Roles

| File | Purpose | Primary inputs |
| --- | --- | --- |
| `session_brief.md` | Short onboarding note for a new agent session | Kanban, mechanism status, recent git history |
| `workflow_index.md` | Task-to-skill/doc/validation map | `.agents/skills`, AGENTS, templates, policies |
| `decision_cache.md` | Compact current decisions with scope labels | Kanban, registry, inspection docs |
| `open_questions.md` | Live research uncertainties and blockers | Kanban, mechanism status, drift audits |
| `rejected_arms.md` | Do-not-rerun list with comparison group and caveat | registry, negative-probe syntheses, inspection docs |
| `model_suite_status.md` | Model-track matrix and provider quirks | Kanban, model-suite prereg/inspections, configs |
| `recurring_failure_modes.md` | Cross-run error classes and repeated fix patterns | error analyses, inspection caveats, Gan/ExECT residual docs |
| `dreams/YYYYMMDD_*.md` | Candidate consolidation output for review | all above |

## Additive Value Over Existing Work

### 1. Fast Session Boot

Current session startup requires reading Kanban, pivot, mechanism status, model-suite docs, and sometimes recent git history. A memory brief can reduce this to one page while preserving links to source artifacts.

Value test: a future session should be able to identify the active next pull, required skills, blocked items, and comparison caveats in under five minutes.

### 2. Stale-Claim Detection

The repo has repeatedly corrected language around arm rejects vs mechanism rejects. Memory can explicitly surface stale-risk phrases:

- "closed"
- "best"
- "rejected"
- "default"
- "benchmark"
- "leader"

The memory process should flag claims that lack `decision_scope` or source paths.

Value test: catches at least one overbroad or stale claim before a Kanban or synthesis update lands.

### 3. Skill Freshness

Skills are working, but recent git history shows skills are periodically updated after doctrine changes. A memory layer can record when a workflow has drifted beyond current skill instructions.

Value test: identifies whether an existing skill needs a small tune before proposing a new skill.

### 4. Research-to-Paper Continuity

Paper-oriented skills now exist, but paper claims need a clean bridge from experiments to narrative. Memory can keep "claims we can make" separate from "interesting observations".

Value test: every paper-facing claim in memory points to a run, config, inspection doc, or policy caveat.

### 5. Better Agent Handoffs

Most task failures here would come from missing context, not missing code. Memory should reduce failures like:

- rerunning an arm that was already rejected
- treating Gemini model-suite evidence as operational promotion
- comparing stale Gan VR/direct runs against frozen F0 architecture
- touching scorer semantics without dataset audits
- running two Ollama jobs at once on the Windows laptop

Value test: memory contains enough warnings that a fresh agent avoids these traps without reading every historical doc.

## What Not To Build

Do not build:

- a second Kanban
- a second registry
- an automatic source-doc rewriter
- a hidden scorer/policy updater
- a vector-memory store with opaque retrieval
- a memory layer that summarizes dataset audits without preserving exact source links

The repo's current problem is not lack of documentation. It is the cost of selecting the right documentation at the right moment.

## Pilot Plan

### Phase 1: Manual Memory Seed

Create the directory and three hand-curated files:

1. `README.md` with rules and source precedence
2. `session_brief.md` for the current active state
3. `workflow_index.md` mapping task types to skills/docs/validation

No automation yet.

Success criterion: the memory seed is useful for the next real task and does not contradict Kanban or registry.

### Phase 2: Dream Candidate Template

Add a template for `docs/memory/dreams/YYYYMMDD_<topic>.md`:

```markdown
# Memory Consolidation Candidate

Date:
Scope:
Sources:

## Proposed Updates

## Stale or Conflicting Claims Found

## Decisions Reaffirmed

## New Open Questions

## Skill or Workflow Updates Suggested

## Promotion Checklist

- Source paths included
- Decision scopes labeled
- No source docs modified automatically
- Human/Codex review complete
```

Success criterion: dream candidates can be reviewed like inspection docs.

### Phase 3: Lightweight Export Script

Add `scripts/export_research_memory.py` after the manual shape is stable. It should read:

- `docs/planning/kanban_plan.md`
- `docs/workstreams/hybrid/hybrid_pipeline_mechanism_status_20260521.md`
- `docs/experiments/synthesis/experiment_registry.json`
- `.agents/skills/*/SKILL.md`
- recent git history, if available

Initial output should be deterministic Markdown, not LLM-generated prose.

Success criterion: script output is boring, traceable, and useful.

### Phase 4: LLM-Assisted Dream Review

Only after deterministic exports are useful, use an LLM to produce a dream candidate that proposes:

- stale-claim flags
- duplicate or conflicting memory notes
- missing source links
- skill update suggestions

The LLM output should be a candidate file under `docs/memory/dreams/`, never direct edits to source docs.

Success criterion: LLM adds synthesis value that deterministic export cannot, while leaving source-of-truth files untouched.

## Recommended New Skill

Add a `research-memory-consolidation` skill only after Phase 1 proves useful. It should trigger when the user asks for repo memory, handoff, dream, session brief, stale-claim detection, or consolidation.

The skill should require:

1. read `docs/memory/README.md`
2. read `docs/planning/kanban_plan.md`
3. read relevant source docs for the topic
4. produce candidate memory updates with source paths and decision scopes
5. never rewrite audits, scorers, registry, or Kanban without explicit request

This should be a new skill rather than overloading `research-synthesis` because it is not ordinary research prose. Its job is cross-artifact memory hygiene.

## Risks

| Risk | Mitigation |
| --- | --- |
| Memory becomes stale | Keep source precedence explicit and date each memory file. |
| Memory duplicates Kanban | Make memory brief shorter and source-linked; no task board semantics. |
| Memory overclaims from summarized docs | Require decision scope and source paths. |
| LLM dream invents facts | Treat output as candidate only; source paths required for promotion. |
| Adds maintenance burden | Start manual and small; automate only after a file proves useful. |
| Skills and memory diverge | Include skill freshness checks in each dream candidate. |

## Initial Recommendation

Proceed with Phase 1.

The first useful deliverable should be a small `docs/memory/` seed, not a full automation. The seed should make future sessions faster and safer by pointing to existing source docs, not replacing them.

Once the manual files are used in two or three real sessions, add a deterministic export script. Only then add LLM-assisted dream candidates.

## Phase 1 Seed Result

Created:

- `docs/memory/README.md`
- `docs/memory/session_brief.md`
- `docs/memory/workflow_index.md`

The seed records source precedence, allowed decision/confidence labels, current active pulls, operational defaults, non-claims, workflow routing, and validation caveats. It is intentionally short and source-linked rather than a second Kanban or experiment registry.

Next recommended memory work:

1. Use the seed in at least two real sessions.
2. Fix or explicitly document the current registry controlled-vocabulary validation drift.
3. Add the dream candidate template only after the seed proves useful.

## Phase 2 Template Result

Created:

- `docs/memory/dreams/TEMPLATE.md`

The template turns a consolidation pass into a reviewable candidate with explicit sources, proposed target files, stale/conflicting claims, reaffirmed decisions, open questions, skill/workflow suggestions, and a promotion checklist. It keeps candidate synthesis separate from promoted memory and from source-of-truth docs.

Next recommended memory work:

1. Use `docs/memory/dreams/TEMPLATE.md` for the next stale-claim or handoff consolidation pass.
2. Promote only reviewed updates into `docs/memory/session_brief.md`, `docs/memory/workflow_index.md`, or future cache files.
3. Defer `scripts/export_research_memory.py` until the manual candidate flow has been used at least once.

## Validation To Run

For the design note itself:

- `uv run pytest tests/test_inspection_templates.py tests/test_experiment_registry_validation.py tests/test_export_research_atlas.py`

For future memory automation:

- add tests that generated memory links only to existing files
- add tests that decision scopes are drawn from the allowed set
- add tests that memory generation does not modify source-of-truth docs

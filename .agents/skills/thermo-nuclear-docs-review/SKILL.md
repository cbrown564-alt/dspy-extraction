---
name: thermo-nuclear-docs-review
description: Use when performing a strict documentation, research-memory, archive, stale-authority, or docs-architecture review of this repo, especially after major synthesis docs, research pivots, experiment cleanup, archive passes, or when the user asks to dramatically simplify, refocus, clean up, or thermonuclear-review documentation.
---

# Thermo-Nuclear Docs Review

Use this skill for a strict review of documentation structure and research memory. The goal is to make the repo easier to reason about without destroying provenance.

Be severe about ambiguity, duplication, stale authority, and misleading navigation. Be conservative about deleting evidence. This is a research repo: old experiment notes are often not active guidance, but they may still be the only provenance for a claim, rejected arm, scorer decision, or caveat.

## Desired End State

The docs tree should have a small set of active truth surfaces and a larger, well-indexed archive.

Active docs should clearly answer:

- What is the current research question?
- What are the current dataset and scorer policies?
- Which baselines are active for Gan and ExECT?
- Which mechanisms are open, rejected, promoted, diagnostic, blocked, or superseded?
- Which docs should a future agent read first?
- Which experiment notes are only historical evidence?

## Review Workflow

1. Start from `AGENTS.md`, `docs/outline.md`, `docs/planning/kanban_plan.md`, dataset audits, scorer/policy docs, and the newest synthesis or deep-dive docs relevant to the request.
2. Inventory the target docs by role:
   - `entrypoint`
   - `active steering`
   - `policy`
   - `dataset audit`
   - `current synthesis`
   - `component ceiling / status registry`
   - `experiment evidence`
   - `paper artifact`
   - `template`
   - `archive`
3. Identify authority conflicts:
   - current baseline or promoted config;
   - scorer mode and benchmark comparison surface;
   - validation versus holdout interpretation;
   - rejected arm versus rejected mechanism;
   - active priority versus historical plan;
   - benchmark-facing versus clinical diagnostic claim.
4. Collapse repeated narratives into a current synthesis or index page.
5. Archive by decision boundary, not just by age. A doc should move out of active navigation when its decision has been absorbed into a newer steering doc, synthesis, registry, or archive index.
6. Leave redirects or index entries so future agents can trace why a doc was moved and what replaced it.
7. Update entrypoints and cross-links after moving, merging, or archiving docs.

## Repo-Specific Guardrails

Do not hide or rewrite provenance needed for:

- ExECT or Gan dataset quirks;
- gold-label interpretation;
- scorer semantics or benchmark reproduction;
- run IDs, configs, model/provider, split, scorer mode, and metrics;
- rejected arms that prevent repeated failed work;
- paper-supporting evidence and caveats;
- holdout warnings and validation-to-test transfer risks.

If a doc contains stale guidance but valuable evidence, archive it with a status note instead of deleting it.

If a doc contains active guidance mixed with historical evidence, split conceptually:

- move the guidance into an active steering/synthesis/status page;
- leave the original as historical evidence or archive it with a pointer.

## Status Labels

Use explicit labels when reviewing or rewriting docs:

- `active guidance`
- `current synthesis`
- `promoted baseline`
- `operational default`
- `mechanism open`
- `rejected arm`
- `mechanism rejected`
- `diagnostic only`
- `benchmark-facing`
- `clinical diagnostic`
- `superseded`
- `blocked`
- `paper evidence`
- `archive`

Be especially strict about the distinction between `rejected arm` and `mechanism rejected`.

## Preferred Remedies

Prefer:

- a top-level `docs/README.md` or research map when navigation is unclear;
- per-domain maps such as `docs/experiments/gan/README.md` and `docs/experiments/exect/README.md`;
- current synthesis docs that absorb repeated learning-log material;
- component ceiling/status registries when the research question has moved from arm wins to component decomposition;
- archive indexes with short reasons for why files moved;
- link updates that point future agents to active truth surfaces first.

Avoid:

- deleting research evidence without an index;
- leaving multiple active docs that disagree;
- burying scorer-policy changes in a dated experiment note;
- keeping old plans visible as if they are still active;
- archiving by date alone when decision status is the real organizing principle;
- replacing nuanced caveats with tidy but false summaries.

## Output Format

Lead with the documentation risks or structural findings. For each finding include:

- affected docs or directories;
- what is stale, duplicated, conflicting, or hard to navigate;
- why it matters for research validity or future agent behavior;
- the recommended action: keep active, rewrite, merge, index, archive, or delete only if truly disposable;
- any links or entrypoints that must be updated.

When proposing a cleanup plan, end with a concrete target architecture: active entrypoints, archived areas, registries/indexes to create, and unresolved provenance risks.

from pathlib import Path

from clinical_extraction.kanban import parse_kanban_markdown, render_mermaid, write_visual_artifacts


def test_parse_kanban_plan_extracts_standard_cards() -> None:
    plan = parse_kanban_markdown(Path("docs/kanban_plan.md").read_text(encoding="utf-8"))

    titles = {card.title for card in plan.cards}

    assert "Inspect post-repair Gan S0 validation behavior" in titles
    assert "Draft ExECT S0/S1 baseline design" in titles
    assert "Gan extract-verify-repair ablation" in titles
    assert "Design section-aware versus monolithic ExECT ablation" in titles
    assert plan.recommended_next_pull[0].startswith("Run Qwen Gan S0 smoke tests")
    assert plan.roadmap["Phase 1: Consolidate Gan S0 Into A Reliable Reference Task"]


def test_parse_card_dependencies_are_split_on_semicolons() -> None:
    markdown = """
# Test Board

## Ready

### First

- Outcome: First card.
- Dependencies: none.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: test.
- Notes: none.

### Second

- Outcome: Second card.
- Dependencies: First; External blocker.
- Parallelizable: after First.
- Owner: unassigned.
- Validation: test.
- Notes: none.
"""

    plan = parse_kanban_markdown(markdown)

    second = next(card for card in plan.cards if card.title == "Second")
    assert second.dependencies == ["First", "External blocker"]


def test_render_mermaid_contains_resolvable_dependency_edge() -> None:
    markdown = """
# Test Board

## Ready

### First

- Outcome: First card.
- Dependencies: none.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: test.
- Notes: none.

### Second

- Outcome: Second card.
- Dependencies: First.
- Parallelizable: after First.
- Owner: unassigned.
- Validation: test.
- Notes: none.
"""
    plan = parse_kanban_markdown(markdown)

    mermaid = render_mermaid(plan)

    assert 'C1["First"]' in mermaid
    assert "C1 --> C2" in mermaid


def test_write_visual_artifacts_creates_json_mermaid_and_html(tmp_path: Path) -> None:
    plan_path = tmp_path / "kanban.md"
    plan_path.write_text(
        """
# Test Board

## Ready

### First

- Outcome: First card.
- Dependencies: none.
- Parallelizable: yes.
- Owner: unassigned.
- Validation: test.
- Notes: none.

## Long-Term Plan

### Phase 1

- Keep going.
""",
        encoding="utf-8",
    )

    outputs = write_visual_artifacts(plan_path, tmp_path / "out")

    assert outputs["json"].exists()
    assert outputs["mermaid"].exists()
    assert outputs["html"].exists()
    html = outputs["html"].read_text(encoding="utf-8")
    assert "Visual monitoring generated from" in html
    assert "Active Dependency Map" in html

"""Parse the project Kanban Markdown into reusable monitoring artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
import json
import re
from pathlib import Path
from typing import Iterable


BOARD_SECTIONS = {
    "Ready",
    "In Progress",
    "Review",
    "Done",
    "Blocked",
    "Backlog",
    "Questions",
    "Experiments",
}

ROADMAP_SECTION = "Long-Term Plan"


@dataclass(frozen=True)
class KanbanCard:
    title: str
    section: str
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def dependencies(self) -> list[str]:
        value = self.fields.get("Dependencies", "").strip()
        if not value or value.lower() == "none":
            return []
        return [
            item.strip().strip("`").rstrip(".")
            for item in re.split(r";|\n", value)
            if item.strip() and item.strip().lower() != "none"
        ]

    @property
    def owner(self) -> str:
        return self.fields.get("Owner", "unassigned")

    @property
    def outcome(self) -> str:
        return self.fields.get("Outcome", "")


@dataclass(frozen=True)
class KanbanPlan:
    title: str
    cards: list[KanbanCard]
    roadmap: dict[str, list[str]]
    recommended_next_pull: list[str]
    dependency_notes: list[str]
    parallelization_opportunities: list[str]

    def as_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "cards": [
                {
                    "title": card.title,
                    "section": card.section,
                    "fields": card.fields,
                    "dependencies": card.dependencies,
                    "owner": card.owner,
                    "outcome": card.outcome,
                }
                for card in self.cards
            ],
            "roadmap": self.roadmap,
            "recommended_next_pull": self.recommended_next_pull,
            "dependency_notes": self.dependency_notes,
            "parallelization_opportunities": self.parallelization_opportunities,
        }


def parse_kanban_markdown(markdown: str) -> KanbanPlan:
    title = "Clinical Extraction Kanban Plan"
    current_section: str | None = None
    current_card_title: str | None = None
    current_card_fields: dict[str, str] = {}
    cards: list[KanbanCard] = []
    roadmap: dict[str, list[str]] = {}
    current_roadmap_phase: str | None = None
    recommended_next_pull: list[str] = []
    dependency_notes: list[str] = []
    parallelization_opportunities: list[str] = []

    def flush_card() -> None:
        nonlocal current_card_title, current_card_fields
        if current_section in BOARD_SECTIONS and current_card_title:
            cards.append(
                KanbanCard(
                    title=current_card_title,
                    section=current_section,
                    fields=dict(current_card_fields),
                )
            )
        current_card_title = None
        current_card_fields = {}

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            flush_card()
            current_section = line[3:].strip()
            current_roadmap_phase = None
            continue
        if line.startswith("### "):
            flush_card()
            heading = line[4:].strip()
            if current_section == ROADMAP_SECTION:
                current_roadmap_phase = heading
                roadmap[current_roadmap_phase] = []
            elif current_section in BOARD_SECTIONS:
                current_card_title = heading
                current_card_fields = {}
            continue

        if current_section == ROADMAP_SECTION and current_roadmap_phase:
            bullet = _parse_bullet(line)
            if bullet:
                roadmap[current_roadmap_phase].append(bullet)
            continue

        if current_section == "Recommended Next Pull":
            numbered = re.match(r"^\d+\.\s+(.*)$", line)
            if numbered:
                recommended_next_pull.append(numbered.group(1).strip())
            continue

        if current_section == "Dependency Notes":
            bullet = _parse_bullet(line)
            if bullet:
                dependency_notes.append(bullet)
            continue

        if current_section == "Parallelization Opportunities":
            bullet = _parse_bullet(line)
            if bullet:
                parallelization_opportunities.append(bullet)
            continue

        if current_card_title:
            field_match = re.match(r"^-\s+([A-Z][A-Za-z ]+):\s*(.*)$", line)
            if field_match:
                current_card_fields[field_match.group(1).strip()] = field_match.group(2).strip()

    flush_card()
    return KanbanPlan(
        title=title,
        cards=cards,
        roadmap=roadmap,
        recommended_next_pull=recommended_next_pull,
        dependency_notes=dependency_notes,
        parallelization_opportunities=parallelization_opportunities,
    )


def write_visual_artifacts(
    plan_path: Path,
    output_dir: Path,
    *,
    json_name: str = "kanban_board.json",
    mermaid_name: str = "kanban_dependencies.mmd",
    html_name: str = "kanban_board.html",
) -> dict[str, Path]:
    plan = parse_kanban_markdown(plan_path.read_text(encoding="utf-8"))
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / json_name
    mermaid_path = output_dir / mermaid_name
    html_path = output_dir / html_name

    json_path.write_text(json.dumps(plan.as_dict(), indent=2) + "\n", encoding="utf-8")
    mermaid_path.write_text(render_mermaid(plan), encoding="utf-8")
    html_path.write_text(render_html(plan), encoding="utf-8")

    return {"json": json_path, "mermaid": mermaid_path, "html": html_path}


def render_mermaid(plan: KanbanPlan) -> str:
    lines = ["flowchart LR"]
    card_ids = {card.title: f"C{index}" for index, card in enumerate(plan.cards, start=1)}
    for card in plan.cards:
        lines.append(f'  {card_ids[card.title]}["{_mermaid_label(card.title)}"]')
        lines.append(f"  {card_ids[card.title]}:::{_mermaid_class(card.section)}")
    for card in plan.cards:
        for dependency in card.dependencies:
            dep_id = card_ids.get(dependency)
            if dep_id:
                lines.append(f"  {dep_id} --> {card_ids[card.title]}")
    lines.extend(
        [
            "  classDef Ready fill:#e8f7ef,stroke:#2f8f5b,color:#153b27",
            "  classDef InProgress fill:#eaf2ff,stroke:#2f67c6,color:#14294f",
            "  classDef Review fill:#fff4d6,stroke:#b38210,color:#473609",
            "  classDef Done fill:#eef0f3,stroke:#77808c,color:#29313b",
            "  classDef Blocked fill:#ffe9e7,stroke:#c7463d,color:#5a1712",
            "  classDef Backlog fill:#f0ecff,stroke:#7259c8,color:#2f255e",
            "  classDef Questions fill:#e8f5f8,stroke:#238096,color:#113d49",
            "  classDef Experiments fill:#f8eef6,stroke:#b25498,color:#4d1f3f",
        ]
    )
    return "\n".join(lines) + "\n"


def render_html(plan: KanbanPlan) -> str:
    data = json.dumps(plan.as_dict(), indent=2)
    sections = ["Ready", "In Progress", "Review", "Blocked", "Questions", "Backlog", "Experiments", "Done"]
    cards_by_section = {
        section: [card for card in plan.cards if card.section == section] for section in sections
    }
    dependency_edges = _dependency_edges(plan.cards)
    focus_cards = cards_by_section["Ready"][:3]
    cards_markup = "\n".join(
        _render_column(section, cards_by_section[section]) for section in sections
    )
    roadmap_markup = "\n".join(
        f"""
        <article class="phase">
          <h3>{escape(title)}</h3>
          <ul>{''.join(f'<li>{escape(item)}</li>' for item in items)}</ul>
        </article>
        """
        for title, items in plan.roadmap.items()
    )
    next_pull = "".join(f"<li>{escape(item)}</li>" for item in plan.recommended_next_pull)
    focus_markup = "".join(
        f"""
        <article class="focus-card {_section_class(card.section)}">
          <span>{escape(card.section)}</span>
          <h3>{escape(card.title)}</h3>
          <p>{escape(card.outcome)}</p>
        </article>
        """
        for card in focus_cards
    )
    dependency_rows = "\n".join(
        f"""
        <div class="edge">
          <span>{escape(source)}</span>
          <b>→</b>
          <span>{escape(target)}</span>
        </div>
        """
        for source, target in dependency_edges
    )
    if not dependency_rows:
        dependency_rows = '<p class="muted">No resolvable card-to-card dependencies found.</p>'
    dag_svg = _render_dag_svg(plan.cards, dependency_edges)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(plan.title)}</title>
  <style>
    :root {{
      --bg: #f4f6f8;
      --bg-strong: #e8edf2;
      --panel: #ffffff;
      --panel-soft: #fafbfc;
      --ink: #17202c;
      --muted: #637084;
      --line: #d8dee8;
      --line-strong: #b9c3d2;
      --ready: #237a57;
      --progress: #2e62b6;
      --review: #a87406;
      --blocked: #bf4139;
      --backlog: #7152bd;
      --questions: #247f91;
      --experiments: #ab4d8f;
      --done: #707b89;
      --shadow: 0 14px 34px rgba(22, 31, 46, .08);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--ink); }}
    header.hero {{
      display: grid;
      grid-template-columns: minmax(0, 1.1fr) minmax(340px, .9fr);
      gap: 22px;
      padding: 22px 32px 20px;
      border-bottom: 1px solid var(--line);
      background:
        linear-gradient(135deg, rgba(35, 122, 87, .09), transparent 42%),
        linear-gradient(90deg, #fff, #f7f9fb);
    }}
    h1 {{ margin: 0 0 10px; font-size: 30px; line-height: 1.12; letter-spacing: 0; }}
    h2 {{ margin: 0; font-size: 17px; line-height: 1.2; }}
    h3 {{ margin: 0; font-size: 14px; line-height: 1.35; }}
    p {{ line-height: 1.5; }}
    .subhead {{ margin: 0; color: var(--muted); max-width: 820px; }}
    .hero-copy {{ align-self: center; }}
    .hero-copy code {{ background: rgba(255,255,255,.72); border: 1px solid var(--line); border-radius: 5px; padding: 1px 5px; }}
    .next-panel {{
      background: rgba(255, 255, 255, .82);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 14px 16px;
      box-shadow: var(--shadow);
    }}
    .next-panel h2 {{ margin-bottom: 10px; }}
    .next-pull {{ margin: 0; padding-left: 20px; }}
    .next-pull li, .phase li {{ margin: 6px 0; line-height: 1.35; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(8, minmax(92px, 1fr));
      gap: 10px;
      padding: 14px 32px 0;
    }}
    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 13px;
      border-top: 4px solid var(--accent);
    }}
    .metric strong {{ display: block; font-size: 24px; line-height: 1; }}
    .metric span {{ color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .06em; }}
    main {{ padding: 18px 32px 40px; }}
    .focus-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(220px, 1fr));
      gap: 14px;
      margin-bottom: 14px;
    }}
    .focus-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-left: 5px solid var(--accent);
      border-radius: 8px;
      padding: 14px;
      box-shadow: 0 10px 24px rgba(22, 31, 46, .06);
    }}
    .focus-card > span {{
      color: var(--accent);
      font-size: 11px;
      font-weight: 750;
      text-transform: uppercase;
      letter-spacing: .08em;
    }}
    .focus-card h3 {{ margin-top: 7px; font-size: 16px; }}
    .focus-card p {{ margin: 7px 0 0; color: var(--muted); font-size: 13px; }}
    .map-panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 14px;
      box-shadow: var(--shadow);
    }}
    .map-header {{
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: baseline;
      margin-bottom: 12px;
    }}
    .map-header p {{ margin: 0; color: var(--muted); font-size: 13px; }}
    .dag-wrap {{
      overflow-x: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: linear-gradient(180deg, #fbfcfd, #f5f7fa);
    }}
    .dag {{ display: block; min-width: 1000px; }}
    .dag-node rect {{ fill: #fff; stroke: var(--line-strong); stroke-width: 1; rx: 8; }}
    .dag-node text {{ fill: var(--ink); font-size: 12px; font-weight: 650; }}
    .dag-node .node-section {{ fill: var(--muted); font-size: 10px; font-weight: 760; text-transform: uppercase; }}
    .dag-edge {{ stroke: #7c8797; stroke-width: 1.4; fill: none; marker-end: url(#arrow); }}
    .dag-lane {{ fill: #eef2f6; }}
    .dag-lane-label {{ fill: var(--muted); font-size: 11px; font-weight: 760; letter-spacing: .06em; text-transform: uppercase; }}
    .toolbar {{
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: 18px;
      flex-wrap: wrap;
    }}
    input, select {{
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 6px;
      padding: 10px 12px;
      min-height: 40px;
      font: inherit;
    }}
    input {{ min-width: min(360px, 100%); flex: 1; }}
    .board {{
      display: grid;
      grid-template-columns: repeat(4, minmax(250px, 1fr));
      gap: 14px;
      align-items: start;
    }}
    .column {{
      background: rgba(255, 255, 255, .66);
      border: 1px solid var(--line);
      border-radius: 8px;
      min-height: 140px;
      overflow: hidden;
    }}
    .column-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
      border-top: 4px solid var(--accent);
    }}
    .count {{ color: var(--muted); font-size: 13px; }}
    .cards {{ display: grid; gap: 10px; padding: 12px; }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 0;
      overflow: hidden;
      box-shadow: 0 8px 18px rgba(25, 33, 48, .05);
    }}
    .card-main {{ padding: 12px 12px 10px; }}
    .card p {{ margin: 8px 0 0; color: var(--muted); font-size: 12.5px; }}
    .card-title-row {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: start;
    }}
    .status-dot {{
      width: 10px;
      height: 10px;
      border-radius: 99px;
      background: var(--accent);
      margin-top: 5px;
    }}
    .chip-row {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
    .chip {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 3px 8px;
      background: var(--panel-soft);
      color: var(--muted);
      font-size: 11px;
      line-height: 1.2;
    }}
    .chip strong {{ color: var(--ink); font-weight: 720; }}
    .dependency-list {{
      margin: 8px 0 0;
      padding: 0;
      list-style: none;
      display: grid;
      gap: 5px;
    }}
    .dependency-list li {{
      border-left: 3px solid var(--accent);
      padding-left: 7px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.25;
    }}
    details.card-details {{
      margin: 0;
      border-top: 1px solid var(--line);
      background: #fbfcfd;
    }}
    details.card-details summary {{
      cursor: pointer;
      padding: 8px 12px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }}
    .detail-body {{
      display: grid;
      gap: 8px;
      padding: 0 12px 12px;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
    }}
    .detail-body div {{ padding-top: 8px; border-top: 1px solid var(--line); }}
    .detail-body div:first-child {{ border-top: 0; padding-top: 0; }}
    .note {{
      display: block;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 9px;
      background: #fafbfc;
      color: var(--muted);
      font-size: 12px;
      line-height: 1.35;
      margin-top: 10px;
    }}
    .Ready, .metric-Ready {{ --accent: var(--ready); }}
    .InProgress, .metric-InProgress {{ --accent: var(--progress); }}
    .Review {{ --accent: var(--review); }}
    .metric-Review {{ --accent: var(--review); }}
    .Blocked, .metric-Blocked {{ --accent: var(--blocked); }}
    .Backlog, .metric-Backlog {{ --accent: var(--backlog); }}
    .Questions, .metric-Questions {{ --accent: var(--questions); }}
    .Experiments, .metric-Experiments {{ --accent: var(--experiments); }}
    .Done, .metric-Done {{ --accent: var(--done); }}
    .panel-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 24px; }}
    .panel {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 18px; box-shadow: 0 8px 18px rgba(25, 33, 48, .04); }}
    .edges {{ display: grid; gap: 8px; }}
    .edge {{ display: grid; grid-template-columns: 1fr auto 1fr; gap: 10px; align-items: center; color: var(--muted); font-size: 13px; }}
    .edge span {{ padding: 8px 10px; background: #f7f8fa; border-radius: 6px; border: 1px solid var(--line); }}
    .phase {{ border-top: 1px solid var(--line); padding-top: 14px; margin-top: 14px; }}
    .phase:first-of-type {{ border-top: 0; padding-top: 0; margin-top: 0; }}
    .muted {{ color: var(--muted); }}
    details.raw-data {{ margin-top: 24px; }}
    pre {{ overflow: auto; background: #151922; color: #f4f6fb; border-radius: 8px; padding: 16px; }}
    .empty {{ padding: 18px 14px; }}
    @media (max-width: 820px) {{
      header.hero {{ grid-template-columns: 1fr; }}
      .metrics {{ grid-template-columns: repeat(4, minmax(110px, 1fr)); }}
      .focus-grid {{ grid-template-columns: 1fr; }}
      .board {{ grid-template-columns: repeat(2, minmax(250px, 1fr)); }}
      .panel-grid {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 680px) {{
      header.hero, main {{ padding-left: 18px; padding-right: 18px; }}
      .metrics {{ padding-left: 18px; padding-right: 18px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(120px, 1fr)); }}
      .board {{ grid-template-columns: 1fr; }}
      .edge {{ grid-template-columns: 1fr; }}
      .edge b {{ display: none; }}
    }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-copy">
      <h1>{escape(plan.title)}</h1>
      <p class="subhead">Visual monitoring generated from <code>docs/kanban_plan.md</code>. The foreground is the next research choice: consolidate Gan S0, open ExECT S0/S1, or use both as complementary testbeds.</p>
    </div>
    <aside class="next-panel">
      <h2>Recommended Next Pull</h2>
      <ol class="next-pull">{next_pull}</ol>
    </aside>
  </header>
  <section class="metrics" aria-label="Board summary">
    {_render_metrics(cards_by_section)}
  </section>
  <main>
    <section class="map-panel" aria-label="Active dependency map">
      <div class="map-header">
        <h2>Active Dependency Map</h2>
        <p>Only resolvable card-to-card dependencies are drawn; background context stays in the Markdown.</p>
      </div>
      <div class="dag-wrap">{dag_svg}</div>
    </section>
    <section class="focus-grid" aria-label="Immediate focus cards">
      {focus_markup}
    </section>
    <section class="toolbar" aria-label="Filters">
      <input id="search" type="search" placeholder="Filter cards by title, outcome, owner, or notes">
      <select id="sectionFilter" aria-label="Section filter">
        <option value="all">All sections</option>
        {''.join(f'<option value="{escape(section)}">{escape(section)}</option>' for section in sections)}
      </select>
    </section>
    <section class="board" id="board">
      {cards_markup}
    </section>
    <section class="panel-grid">
      <article class="panel">
        <h2>Dependency Edges</h2>
        <div class="edges">{dependency_rows}</div>
      </article>
      <article class="panel">
        <h2>Parallelization Notes</h2>
        <ul class="next-pull">{''.join(f'<li>{escape(item)}</li>' for item in plan.parallelization_opportunities)}</ul>
      </article>
    </section>
    <section class="panel" style="margin-top: 18px;">
      <h2>Long-Term Plan</h2>
      {roadmap_markup}
    </section>
    <details class="raw-data">
      <summary>Embedded board JSON</summary>
      <pre id="boardData">{escape(data)}</pre>
    </details>
  </main>
  <script type="application/json" id="kanban-json">{escape(data)}</script>
  <script>
    const search = document.getElementById('search');
    const sectionFilter = document.getElementById('sectionFilter');
    const cards = Array.from(document.querySelectorAll('.card'));
    function applyFilters() {{
      const query = search.value.trim().toLowerCase();
      const section = sectionFilter.value;
      cards.forEach((card) => {{
        const haystack = card.textContent.toLowerCase();
        const sectionMatches = section === 'all' || card.dataset.section === section;
        const queryMatches = !query || haystack.includes(query);
        card.hidden = !(sectionMatches && queryMatches);
      }});
      document.querySelectorAll('.column').forEach((column) => {{
        const visible = Array.from(column.querySelectorAll('.card')).filter((card) => !card.hidden).length;
        column.querySelector('.count').textContent = visible;
      }});
    }}
    search.addEventListener('input', applyFilters);
    sectionFilter.addEventListener('change', applyFilters);
  </script>
</body>
</html>
"""


def _parse_bullet(line: str) -> str | None:
    match = re.match(r"^-\s+(.*)$", line)
    if match:
        return match.group(1).strip()
    return None


def _render_metrics(cards_by_section: dict[str, list[KanbanCard]]) -> str:
    return "\n".join(
        f"""
        <div class="metric metric-{_section_class(section)}">
          <strong>{len(cards)}</strong>
          <span>{escape(section)}</span>
        </div>
        """
        for section, cards in cards_by_section.items()
    )


def _render_column(section: str, cards: list[KanbanCard]) -> str:
    class_name = _section_class(section)
    card_markup = "\n".join(_render_card(card, class_name) for card in cards)
    if not card_markup:
        card_markup = '<p class="muted empty">No cards currently claimed.</p>'
    return f"""
    <article class="column {class_name}" data-section="{escape(section)}">
      <div class="column-header">
        <h2>{escape(section)}</h2>
        <span class="count">{len(cards)}</span>
      </div>
      <div class="cards">{card_markup}</div>
    </article>
    """


def _render_card(card: KanbanCard, class_name: str) -> str:
    deps = card.dependencies
    validation = card.fields.get("Validation", "")
    notes = card.fields.get("Notes", "")
    parallelizable = card.fields.get("Parallelizable", "")
    dep_markup = _render_dependency_list(deps)
    compact_validation = _compact_text(validation, 120)
    compact_parallel = _compact_text(parallelizable, 50)
    return f"""
      <article class="card {class_name}" data-section="{escape(card.section)}">
        <div class="card-main">
          <div class="card-title-row">
            <h3>{escape(card.title)}</h3>
            <span class="status-dot" aria-hidden="true"></span>
          </div>
          {_paragraph(_compact_text(card.outcome, 145))}
          <div class="chip-row">
            <span class="chip"><strong>Owner</strong>&nbsp;{escape(card.owner)}</span>
            <span class="chip"><strong>Deps</strong>&nbsp;{len(deps)}</span>
            {_chip("Parallel", compact_parallel)}
          </div>
          {dep_markup}
        </div>
        <details class="card-details">
          <summary>Details</summary>
          <div class="detail-body">
            {_detail_line("Outcome", card.outcome)}
            {_detail_line("Validation", validation)}
            {_detail_line("Parallelizable", parallelizable)}
            {_detail_line("Notes", notes)}
          </div>
        </details>
      </article>
    """


def _paragraph(value: str) -> str:
    if not value:
        return ""
    return f"<p>{escape(value)}</p>"


def _meta_line(label: str, value: str) -> str:
    if not value:
        return ""
    return f"<span><strong>{escape(label)}:</strong> {escape(value)}</span>"


def _chip(label: str, value: str) -> str:
    if not value:
        return ""
    return f'<span class="chip"><strong>{escape(label)}</strong>&nbsp;{escape(value)}</span>'


def _detail_line(label: str, value: str) -> str:
    if not value:
        return ""
    return f"<div><strong>{escape(label)}:</strong> {escape(value)}</div>"


def _render_dependency_list(dependencies: list[str]) -> str:
    if not dependencies:
        return ""
    items = "".join(f"<li>{escape(_compact_text(item, 72))}</li>" for item in dependencies[:3])
    if len(dependencies) > 3:
        items += f"<li>+{len(dependencies) - 3} more</li>"
    return f'<ul class="dependency-list" aria-label="Dependencies">{items}</ul>'


def _compact_text(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return value[: max(0, limit - 1)].rstrip() + "…"


def _dependency_edges(cards: Iterable[KanbanCard]) -> list[tuple[str, str]]:
    by_title = {card.title for card in cards}
    edges: list[tuple[str, str]] = []
    for card in cards:
        for dependency in card.dependencies:
            if dependency in by_title:
                edges.append((dependency, card.title))
    return edges


def _mermaid_label(label: str) -> str:
    return label.replace('"', "'")


def _mermaid_class(section: str) -> str:
    return _section_class(section)


def _section_class(section: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", section)


def _render_dag_svg(cards: list[KanbanCard], edges: list[tuple[str, str]]) -> str:
    if not edges:
        return '<p class="muted empty">No resolvable card-to-card dependencies found.</p>'

    cards_by_title = {card.title: card for card in cards}
    involved_titles = {title for edge in edges for title in edge}
    involved_cards = [card for card in cards if card.title in involved_titles]
    lanes = ["Ready", "Questions", "Backlog", "Experiments"]
    lane_x = {section: 30 + index * 250 for index, section in enumerate(lanes)}
    lane_counts = {section: 0 for section in lanes}
    positions: dict[str, tuple[int, int]] = {}

    for card in involved_cards:
        lane = card.section if card.section in lane_x else "Backlog"
        x = lane_x[lane]
        y = 56 + lane_counts[lane] * 96
        positions[card.title] = (x, y)
        lane_counts[lane] += 1

    height = max(260, max((y for _, y in positions.values()), default=0) + 92)
    width = 1040
    lane_markup = "\n".join(
        f"""
        <rect class="dag-lane" x="{x - 12}" y="20" width="224" height="{height - 40}" rx="10"></rect>
        <text class="dag-lane-label" x="{x}" y="42">{escape(section)}</text>
        """
        for section, x in lane_x.items()
    )
    edge_markup = "\n".join(
        _render_svg_edge(positions[source], positions[target])
        for source, target in edges
        if source in positions and target in positions
    )
    node_markup = "\n".join(
        _render_svg_node(card, positions[card.title])
        for card in involved_cards
        if card.title in positions
    )
    return f"""
      <svg class="dag" viewBox="0 0 {width} {height}" role="img" aria-label="Active dependency graph">
        <defs>
          <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
            <path d="M0,0 L8,4 L0,8 Z" fill="#7c8797"></path>
          </marker>
        </defs>
        {lane_markup}
        {edge_markup}
        {node_markup}
      </svg>
    """


def _render_svg_edge(source: tuple[int, int], target: tuple[int, int]) -> str:
    sx, sy = source
    tx, ty = target
    start_x = sx + 196
    start_y = sy + 32
    end_x = tx - 4
    end_y = ty + 32
    mid_x = (start_x + end_x) / 2
    return (
        f'<path class="dag-edge" d="M {start_x} {start_y} '
        f'C {mid_x} {start_y}, {mid_x} {end_y}, {end_x} {end_y}"></path>'
    )


def _render_svg_node(card: KanbanCard, position: tuple[int, int]) -> str:
    x, y = position
    lines = _wrap_svg_label(card.title, 25)[:2]
    text_lines = "\n".join(
        f'<text x="{x + 12}" y="{y + 36 + index * 15}">{escape(line)}</text>'
        for index, line in enumerate(lines)
    )
    return f"""
      <g class="dag-node">
        <rect x="{x}" y="{y}" width="196" height="72"></rect>
        <text class="node-section" x="{x + 12}" y="{y + 20}">{escape(card.section)}</text>
        {text_lines}
      </g>
    """


def _wrap_svg_label(label: str, limit: int) -> list[str]:
    words = label.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if len(lines) > 2:
        lines = [lines[0], _compact_text(" ".join(lines[1:]), limit)]
    return lines or [label]

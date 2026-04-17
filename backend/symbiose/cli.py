"""Symbiose CLI — commands to drive the MVP end-to-end.

Usage:
  symbiose demo "Brief client..."
  symbiose skills list
  symbiose skills validate
  symbiose serve            # lance FastAPI
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from . import __version__
from .config import CONFIG
from .models.brief import RawBriefInput
from .models.talent import TalentProfile
from .agents import BriefParserAgent, MatchingAgent, MissionCopilotAgent
from .models.mission import Mission
from .skills import get_registry
from .skills.validator import validate_manifest, ManifestValidationError


app = typer.Typer(add_completion=False, help="Symbiose MVP CLI")
skills_app = typer.Typer(help="Skill registry commands")
app.add_typer(skills_app, name="skills")

console = Console()


# ---------------------------------------------------------------------------
# skills
# ---------------------------------------------------------------------------

@skills_app.command("list")
def skills_list() -> None:
    """List every skill indexed in the registry."""
    reg = get_registry()
    table = Table(title="Skills indexés", box=box.SIMPLE_HEAD)
    table.add_column("id")
    table.add_column("ver")
    table.add_column("domains")
    table.add_column("phases")
    table.add_column("cert", justify="center")
    table.add_column("tokens", justify="right")
    for s in reg.summaries():
        table.add_row(
            s.id,
            s.version,
            ", ".join(s.domains[:2]),
            ", ".join(s.mission_phases[:3]),
            (s.certification_level or "—")[:6],
            str(s.price_tokens),
        )
    console.print(table)


@skills_app.command("validate")
def skills_validate() -> None:
    """Validate every skill.yaml under skills/ against the JSON-Schema."""
    import yaml
    root = CONFIG.skills_root
    ok, ko = 0, 0
    for yml in root.rglob("skill.yaml"):
        try:
            raw = yaml.safe_load(yml.read_text(encoding="utf-8"))
            validate_manifest(raw)
            console.print(f"[green]OK[/] {yml.relative_to(CONFIG.repo_root)}")
            ok += 1
        except (ManifestValidationError, Exception) as e:
            console.print(f"[red]KO[/] {yml.relative_to(CONFIG.repo_root)}\n    {e}")
            ko += 1
    console.print(f"\n[bold]Résumé.[/] {ok} OK · {ko} KO")
    if ko:
        raise typer.Exit(code=1)


# ---------------------------------------------------------------------------
# demo — run brief → matching → copilot events
# ---------------------------------------------------------------------------

DEFAULT_BRIEF = (
    "On a une boutique Shopify qui convertit mal, surtout sur mobile. Budget 5000€, "
    "il nous faut un regard extérieur UX sous 10 jours, livrable un rapport d'audit et "
    "un plan d'action priorisé. On parle français."
)


@app.command()
def demo(
    brief: Annotated[str, typer.Argument(help="Brief client (défaut : scénario e-commerce)")] = DEFAULT_BRIEF,
    budget_tokens: int = typer.Option(500, help="Budget tokens du talent"),
    seniority: str = typer.Option("confirmed", help="Séniorité du talent (junior|confirmed|senior|expert)"),
    execute: bool = typer.Option(False, "--execute", help="Déroule aussi l'exécution du plan par le Mission Copilot"),
) -> None:
    """Lance la démo bout-en-bout : parsing → matching → (optionnel) exécution."""
    console.rule(f"[bold]Symbiose {__version__} — démo bout-en-bout")

    # 1. Parse
    parser = BriefParserAgent()
    parsed = parser.parse(RawBriefInput(raw_brief=brief))
    console.print(Panel.fit(
        _render_brief(parsed),
        title="[bold cyan]1. Brief-Parser Agent",
        border_style="cyan",
    ))

    # 2. Talent profile
    talent = TalentProfile(
        talent_id="t_demo",
        display_name="Talent démo",
        seniority=seniority,  # type: ignore[arg-type]
        domains=parsed.domains[:2],
        strengths=["audit", "synthèse"],
        gaps=["analytics"],
        languages=["fr"],
        budget_tokens=budget_tokens,
    )

    # 3. Match
    matcher = MatchingAgent()
    result = matcher.match(parsed, talent)
    console.print(Panel.fit(
        _render_matching(result),
        title="[bold magenta]2. Matching Agent",
        border_style="magenta",
    ))

    if not execute:
        console.print("\n[dim]Relance avec [bold]--execute[/bold] pour voir le Mission Copilot exécuter le plan.[/dim]")
        return

    # 4. Mission + Copilot execution
    mission = Mission.from_matching(
        mission_id="m_demo",
        need_id="n_demo",
        brief=parsed,
        selected=result.selected_skills,
        plan_outline=result.mission_plan_outline,
        workspace_path=str(CONFIG.workspace_root / "demo"),
    )
    copilot = MissionCopilotAgent(mission)
    console.rule("[bold yellow]3. Mission Copilot — exécution")
    for event in copilot.run_plan():
        _print_event(event)

    console.print(f"\n[dim]Workspace : {mission.workspace_path}[/dim]")


# ---------------------------------------------------------------------------
# serve — FastAPI
# ---------------------------------------------------------------------------

@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = CONFIG.http_port,
    reload: bool = False,
) -> None:
    """Lance le serveur HTTP (FastAPI + Jinja + HTMX)."""
    import uvicorn
    uvicorn.run("symbiose.main:app", host=host, port=port, reload=reload)


# ---------------------------------------------------------------------------
# render helpers
# ---------------------------------------------------------------------------

def _render_brief(b) -> str:
    lines = [
        f"[bold]Titre.[/] {b.title}",
        f"[bold]Domaines.[/] {', '.join(b.domains)}",
        f"[bold]Sous-domaines.[/] {', '.join(b.sub_domains) or '—'}",
        f"[bold]Livrables.[/] {', '.join(b.deliverables)}",
        f"[bold]Phases.[/] {', '.join(b.phase_hints)}",
        f"[bold]Contraintes.[/] budget={b.constraints.budget_eur}€ · délai={b.constraints.deadline_days}j · langue={b.constraints.language}",
        f"[bold]Confiance.[/] {b.confidence:.2f}",
    ]
    if b.red_flags:
        lines.append(f"[red]Red flags.[/] {', '.join(b.red_flags)}")
    if b.missing_info:
        lines.append(f"[yellow]À clarifier.[/] {', '.join(q.question for q in b.missing_info)}")
    return "\n".join(lines)


def _render_matching(r) -> str:
    if not r.selected_skills:
        return "[red]Aucun skill sélectionné.[/]\n" + r.explanation_fr
    lines: list[str] = []
    for s in r.selected_skills:
        lines.append(f"[bold green]• {s.skill_id}[/] [dim]v{s.version}[/] — {s.estimated_cost_tokens} tokens")
        lines.append(f"  [italic]{s.rationale_fr}[/]")
    lines.append("")
    lines.append(f"[bold]Plan.[/]")
    for step in r.mission_plan_outline:
        lines.append(f"  ↳ {step.phase}: {', '.join(step.skills)}")
    lines.append("")
    lines.append(f"[bold]Coût total.[/] {r.total_estimated_cost_tokens} tokens")
    lines.append(f"[bold]Explication.[/] {r.explanation_fr}")
    if r.unmet_needs:
        lines.append("")
        lines.append("[yellow]Besoins non couverts[/]")
        for u in r.unmet_needs:
            lines.append(f"  ⚠︎ {u.need} — {u.reason}")
    return "\n".join(lines)


def _print_event(ev) -> None:
    color = {
        "assistant_message": "cyan",
        "plan_update": "blue",
        "skill_run_start": "yellow",
        "skill_run_result": "green",
        "quality_warning": "red",
    }.get(ev.kind, "white")
    console.print(f"[{color}][{ev.kind}][/] {json.dumps(ev.payload, ensure_ascii=False)[:220]}")


if __name__ == "__main__":
    app()

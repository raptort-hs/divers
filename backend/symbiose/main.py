"""FastAPI application — HTTP entry point for Symbiose MVP.

Mounts both JSON API routes (/api/v1/*) and HTMX-driven web routes (/, /onboarding,
/mission/{id}, ...). In-memory state at MVP (no DB) — sufficient for demo.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from pathlib import Path

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import __version__
from .config import CONFIG
from .agents import BriefParserAgent, MatchingAgent, MissionCopilotAgent
from .models.brief import RawBriefInput
from .models.mission import Mission
from .models.talent import TalentProfile
from .skills import get_registry


app = FastAPI(title="Symbiose MVP", version=__version__)


_WEB_DIR = Path(__file__).parent / "web"
templates = Jinja2Templates(directory=str(_WEB_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(_WEB_DIR / "static")), name="static")


# ---- in-memory stores (MVP) -------------------------------------------------

_MISSIONS: dict[str, Mission] = {}
_PARSED: dict[str, dict] = {}  # need_id -> parsed brief dict


# ---- web routes -------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    return templates.TemplateResponse(request, "landing.html")


@app.get("/onboarding", response_class=HTMLResponse)
async def onboarding_form(request: Request):
    return templates.TemplateResponse(request, "onboarding.html")


@app.post("/onboarding", response_class=HTMLResponse)
async def onboarding_submit(
    request: Request,
    raw_brief: str = Form(...),
    budget_eur: int | None = Form(None),
    deadline_days: int | None = Form(None),
):
    parser = BriefParserAgent()
    parsed = parser.parse(RawBriefInput(
        raw_brief=raw_brief,
        budget_eur=budget_eur,
        deadline_days=deadline_days,
    ))

    talent = TalentProfile(
        talent_id="t_demo",
        display_name="Talent démo",
        seniority="confirmed",
        domains=parsed.domains[:2],
        strengths=["audit", "synthèse"],
        gaps=["analytics"],
        languages=["fr"],
        budget_tokens=500,
    )
    matcher = MatchingAgent()
    result = matcher.match(parsed, talent)

    mission_id = f"m_{uuid.uuid4().hex[:10]}"
    workspace = CONFIG.workspace_root / mission_id
    mission = Mission.from_matching(
        mission_id=mission_id,
        need_id=f"n_{uuid.uuid4().hex[:10]}",
        brief=parsed,
        selected=result.selected_skills,
        plan_outline=result.mission_plan_outline,
        workspace_path=str(workspace),
    )
    _MISSIONS[mission_id] = mission
    _PARSED[mission.need_id] = parsed.model_dump()

    return RedirectResponse(url=f"/mission/{mission_id}", status_code=303)


@app.get("/mission/{mission_id}", response_class=HTMLResponse)
async def mission_view(request: Request, mission_id: str):
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="mission not found")
    return templates.TemplateResponse(request, "mission.html", {"mission": mission})


@app.post("/mission/{mission_id}/start")
async def mission_start(mission_id: str):
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="mission not found")
    mission.status = "running"
    return RedirectResponse(url=f"/mission/{mission_id}/live", status_code=303)


@app.get("/mission/{mission_id}/live", response_class=HTMLResponse)
async def mission_live(request: Request, mission_id: str):
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="mission not found")
    return templates.TemplateResponse(request, "mission_live.html", {"mission": mission})


@app.get("/mission/{mission_id}/events")
async def mission_events(mission_id: str):
    mission = _MISSIONS.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="mission not found")
    copilot = MissionCopilotAgent(mission)

    async def streamer():
        for ev in copilot.run_plan():
            yield f"event: {ev.kind}\ndata: {ev.to_json()}\n\n"
            await asyncio.sleep(0.2)

    return StreamingResponse(streamer(), media_type="text/event-stream")


@app.get("/skills", response_class=HTMLResponse)
async def skills_page(request: Request):
    reg = get_registry()
    return templates.TemplateResponse(request, "skills.html", {"skills": reg.summaries()})


# ---- JSON API ---------------------------------------------------------------

@app.get("/api/v1/skills")
async def api_skills():
    reg = get_registry()
    return [s.model_dump() for s in reg.summaries()]


@app.get("/api/v1/skills/{skill_id}")
async def api_skill(skill_id: str):
    reg = get_registry()
    m = reg.get(skill_id)
    if not m:
        raise HTTPException(status_code=404)
    return m.model_dump()


@app.get("/api/v1/missions/{mission_id}")
async def api_mission(mission_id: str):
    m = _MISSIONS.get(mission_id)
    if not m:
        raise HTTPException(status_code=404)
    return m.model_dump(mode="json")


@app.get("/api/v1/health")
async def health():
    reg = get_registry()
    return {
        "status": "ok",
        "version": __version__,
        "skills_loaded": len(reg.all()),
        "llm_mode": CONFIG.llm_mode,
    }

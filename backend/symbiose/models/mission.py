"""Mission domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field
from .brief import MissionBrief
from .skill import SelectedSkill, PlanOutlineStep


AutonomyLevel = Literal["manual", "guided", "auto"]
MissionStatus = Literal["proposed", "accepted", "running", "review", "closed", "cancelled"]
PlanPhase = Literal["discovery", "audit", "design", "build", "review", "handover"]


class MissionPlanStep(BaseModel):
    phase: PlanPhase
    skills: list[str]
    rationale: str
    status: Literal["pending", "running", "done", "skipped"] = "pending"


class SkillActivation(BaseModel):
    skill_id: str
    version: str
    rationale_fr: str
    activated_at: datetime = Field(default_factory=datetime.utcnow)


class Mission(BaseModel):
    id: str
    need_id: str
    talent_id: str | None = None
    status: MissionStatus = "proposed"
    brief: MissionBrief
    plan: list[MissionPlanStep]
    activations: list[SkillActivation]
    budget_eur: int | None = None
    deadline_days: int | None = None
    autonomy_level: AutonomyLevel = "guided"
    workspace_path: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_matching(
        cls,
        *,
        mission_id: str,
        need_id: str,
        brief: MissionBrief,
        selected: list[SelectedSkill],
        plan_outline: list[PlanOutlineStep],
        workspace_path: str,
    ) -> "Mission":
        plan = [
            MissionPlanStep(phase=step.phase, skills=step.skills, rationale=step.rationale)
            for step in plan_outline
        ]
        activations = [
            SkillActivation(
                skill_id=s.skill_id,
                version=s.version,
                rationale_fr=s.rationale_fr,
            )
            for s in selected
        ]
        return cls(
            id=mission_id,
            need_id=need_id,
            brief=brief,
            plan=plan,
            activations=activations,
            budget_eur=brief.constraints.budget_eur,
            deadline_days=brief.constraints.deadline_days,
            workspace_path=workspace_path,
        )

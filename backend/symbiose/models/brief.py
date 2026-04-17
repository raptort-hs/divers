"""MissionBrief: the structured output of the Brief-Parser Agent."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class BriefConstraints(BaseModel):
    budget_eur: int | None = None
    deadline_days: int | None = None
    language: Literal["fr", "en"] = "fr"


class BriefClarification(BaseModel):
    """A question the Brief-Parser asks the client to resolve ambiguity."""
    id: str
    question: str
    why: str | None = None


class MissionBrief(BaseModel):
    """Structured brief — output of Brief-Parser Agent, input of Matching Agent."""

    title: str
    domains: list[str]
    sub_domains: list[str] = Field(default_factory=list)
    deliverables: list[str]
    constraints: BriefConstraints
    phase_hints: list[str] = Field(default_factory=list)
    persona_hints: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    missing_info: list[BriefClarification] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    raw_brief: str


class RawBriefInput(BaseModel):
    """What the PME onboarding form sends."""
    raw_brief: str
    language: Literal["fr", "en"] = "fr"
    budget_eur: int | None = None
    deadline_days: int | None = None

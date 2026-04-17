"""Talent profile model."""

from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


Seniority = Literal["junior", "confirmed", "senior", "expert"]


class TalentProfile(BaseModel):
    talent_id: str
    display_name: str
    seniority: Seniority
    domains: list[str]
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=lambda: ["fr"])
    budget_tokens: int = 500
    preferred_llm: str = "claude-opus-4-7"

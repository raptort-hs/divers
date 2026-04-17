"""Skill manifest models (Pydantic) + matching result models."""

from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


Seniority = Literal["junior", "confirmed", "senior", "expert"]
MissionPhase = Literal["discovery", "audit", "design", "build", "review", "handover"]
CertificationLevel = Literal["bronze", "silver", "gold"]


class I18nString(BaseModel):
    model_config = ConfigDict(extra="allow")
    fr: str
    en: str | None = None


class SkillAuthor(BaseModel):
    type: Literal["native", "community", "external"]
    id: str
    handle: str | None = None
    display_name: str


class SkillSource(BaseModel):
    kind: Literal["native", "community", "claude-skill", "mcp-server", "github", "web"]
    origin_url: str | None = None
    adapter: str | None = None
    license: str | None = None


class SkillDescription(BaseModel):
    short: I18nString
    long: I18nString
    intended_for: I18nString | None = None
    non_goals: I18nString | None = None


class SkillTaxonomy(BaseModel):
    domains: list[str]
    sub_domains: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    seniority_target: list[Seniority]
    mission_phases: list[MissionPhase]
    languages: list[str]


class SkillIOField(BaseModel):
    name: str
    type: str
    required: bool = False
    description: str | None = None


class SkillInterface(BaseModel):
    inputs: list[SkillIOField]
    outputs: list[SkillIOField]
    preconditions: list[str] = Field(default_factory=list)
    side_effects: list[str] = Field(default_factory=list)


class SkillRuntime(BaseModel):
    model_config = ConfigDict(extra="allow")
    offline: bool = False
    estimated_cost_per_run: str | None = None


class SkillSafety(BaseModel):
    pii_handling: Literal["none", "processes-pii", "stores-pii"]
    data_egress: Literal["none", "workspace-only", "external-api", "internet"]
    injection_risk: Literal["low", "medium", "high"]
    sandbox_level: Literal["strict", "moderate", "trusted"]
    review_status: Literal[
        "unreviewed", "community-reviewed", "certified-v1", "deprecated", "blocked"
    ]
    human_oversight_required: bool = False


class SkillGovernance(BaseModel):
    certified: bool = False
    certification_level: CertificationLevel | None = None
    usage_count: int = 0
    success_rate: float | None = None
    avg_rating: float | None = None
    disable_rate: float | None = None
    deprecated: bool = False


class SkillEconomics(BaseModel):
    price_model: Literal["per-run", "per-mission", "flat", "free"]
    price_tokens: int = 0
    author_share_pct: int = 0
    platform_share_pct: int = 100


class SkillManifest(BaseModel):
    """Full skill manifest — parsed from skill.yaml."""
    model_config = ConfigDict(extra="allow")

    manifest_version: str
    id: str
    name: str
    version: str
    author: SkillAuthor
    source: SkillSource
    description: SkillDescription
    taxonomy: SkillTaxonomy
    interface: SkillInterface
    runtime: SkillRuntime = Field(default_factory=SkillRuntime)
    safety: SkillSafety
    governance: SkillGovernance = Field(default_factory=SkillGovernance)
    economics: SkillEconomics | None = None
    tools: dict[str, Any] = Field(default_factory=dict)
    lifecycle: dict[str, Any] = Field(default_factory=dict)
    system_prompt: str = ""           # loaded from system_prompt.md
    examples: list[dict[str, Any]] = Field(default_factory=list)
    bundle_path: str = ""              # filled by the registry


class SkillSummary(BaseModel):
    """Lightweight skill info — what search returns."""
    id: str
    version: str
    name: str
    short_description: str
    domains: list[str]
    mission_phases: list[MissionPhase]
    seniority_target: list[Seniority]
    languages: list[str]
    certified: bool
    certification_level: CertificationLevel | None
    price_tokens: int
    offline: bool


# -- Matching Agent output -----------------------------------------------------

class ScoreBreakdown(BaseModel):
    skill_id: str
    subscores: dict[str, float]
    weighted_total: float
    weights_used: dict[str, float]


class SelectedSkill(BaseModel):
    skill_id: str
    version: str
    rationale_fr: str
    covers_deliverables: list[str] = Field(default_factory=list)
    covers_phases: list[str] = Field(default_factory=list)
    complements_talent_gaps: list[str] = Field(default_factory=list)
    estimated_cost_tokens: int
    confidence: float = Field(ge=0.0, le=1.0)


class PlanOutlineStep(BaseModel):
    phase: str
    skills: list[str]
    rationale: str


class UnmetNeed(BaseModel):
    need: str
    reason: str


class MatchingResult(BaseModel):
    selected_skills: list[SelectedSkill]
    mission_plan_outline: list[PlanOutlineStep]
    unmet_needs: list[UnmetNeed] = Field(default_factory=list)
    total_estimated_cost_tokens: int
    explanation_fr: str

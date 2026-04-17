from __future__ import annotations

from symbiose.agents import BriefParserAgent, MatchingAgent
from symbiose.models.brief import RawBriefInput
from symbiose.models.talent import TalentProfile


def _talent(budget=500, seniority="confirmed"):
    return TalentProfile(
        talent_id="t_test",
        display_name="Test talent",
        seniority=seniority,  # type: ignore[arg-type]
        domains=["design", "ux"],
        strengths=["audit"],
        gaps=["analytics"],
        languages=["fr"],
        budget_tokens=budget,
    )


def test_ux_brief_selects_audit_ux_express():
    raw = (
        "Boutique Shopify qui convertit mal, audit UX sous 10 jours, "
        "livrable rapport d'audit. Budget 5000€."
    )
    brief = BriefParserAgent().parse(RawBriefInput(raw_brief=raw))
    result = MatchingAgent().match(brief, _talent())
    ids = {s.skill_id for s in result.selected_skills}
    assert "audit-ux-express" in ids
    assert result.total_estimated_cost_tokens <= 500


def test_selection_respects_budget():
    raw = "Audit UX express rapport d'audit."
    brief = BriefParserAgent().parse(RawBriefInput(raw_brief=raw))
    result = MatchingAgent().match(brief, _talent(budget=20))
    # only skills ≤ 20 tokens eligible: meeting-notes (5), exec-summary (15)
    for s in result.selected_skills:
        assert s.estimated_cost_tokens <= 20


def test_plan_is_phase_ordered():
    raw = (
        "Synthèse exécutive de notre audit + deck client pour restitution. "
        "Budget 5000€ sous 1 semaine."
    )
    brief = BriefParserAgent().parse(RawBriefInput(raw_brief=raw))
    result = MatchingAgent().match(brief, _talent())
    phase_order = ["discovery", "audit", "design", "build", "review", "handover"]
    indices = [phase_order.index(step.phase) for step in result.mission_plan_outline if step.phase in phase_order]
    assert indices == sorted(indices)


def test_rationale_never_empty():
    brief = BriefParserAgent().parse(RawBriefInput(
        raw_brief="Audit UX boutique e-commerce, livrable rapport, budget 3000€, 2 semaines."
    ))
    result = MatchingAgent().match(brief, _talent())
    for s in result.selected_skills:
        assert s.rationale_fr and s.rationale_fr.strip()

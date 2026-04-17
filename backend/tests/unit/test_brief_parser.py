from __future__ import annotations

from symbiose.agents import BriefParserAgent
from symbiose.models.brief import RawBriefInput


def test_parser_extracts_budget_and_deadline_from_fr_brief():
    raw = (
        "On a une boutique Shopify qui convertit mal, surtout sur mobile. "
        "Budget 5000€, il nous faut un audit UX sous 10 jours, livrable un "
        "rapport d'audit et un plan d'action priorisé."
    )
    parsed = BriefParserAgent().parse(RawBriefInput(raw_brief=raw))
    assert parsed.constraints.budget_eur == 5000
    assert parsed.constraints.deadline_days == 10
    assert "ux" in parsed.domains or "design" in parsed.domains
    # deliverables captured
    assert any("audit" in d.lower() for d in parsed.deliverables)
    assert parsed.confidence >= 0.5


def test_parser_flags_missing_info():
    raw = "J'ai besoin d'un audit UX."  # no budget, no deadline
    parsed = BriefParserAgent().parse(RawBriefInput(raw_brief=raw))
    ids = {q.id for q in parsed.missing_info}
    assert "budget" in ids
    assert "deadline" in ids


def test_parser_flags_unrealistic_budget():
    raw = "Refonte complète du site avec un budget de 100€ sous 1 jour."
    parsed = BriefParserAgent().parse(RawBriefInput(raw_brief=raw))
    assert parsed.red_flags

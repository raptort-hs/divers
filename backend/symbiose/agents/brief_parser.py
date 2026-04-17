"""Brief-Parser Agent — raw client text → structured MissionBrief.

Spec: docs/tech/04-brief-parser-agent.md.

Strategy:
1. Try LLM (if anthropic mode).
2. Fall back to a deterministic heuristic parser that handles typical FR briefs.
   This guarantees the MVP demo runs without an API key.
"""

from __future__ import annotations

import re
from ..llm import get_llm_client, LLMMessage
from ..models.brief import MissionBrief, BriefConstraints, RawBriefInput


SYSTEM_PROMPT = """You are Symbiose's Brief-Parser Agent.
You convert a raw client brief into a strict JSON MissionBrief.
Never fabricate constraints. Language follows the brief.
Output ONLY valid JSON matching the MissionBrief schema."""


DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "ux": ["ux", "ergonomie", "parcours utilisateur", "heuristique", "audit"],
    "design": ["design", "maquette", "wireframe", "figma", "ui"],
    "ecommerce": ["e-commerce", "ecommerce", "boutique", "panier", "checkout", "shopify"],
    "product": ["produit", "roadmap", "product management", "po"],
    "engineering": ["api", "backend", "refactor", "architecture", "spec technique"],
    "software": ["code", "développement", "refonte technique", "framework"],
    "marketing": ["marketing", "campagne", "growth", "seo", "ads"],
    "sales": ["sales", "commercial", "lead", "prospection"],
    "copywriting": ["copy", "rédaction", "cold email", "newsletter"],
    "consulting": ["conseil", "audit stratégique", "diagnostic"],
    "project-management": ["réunion", "planning", "gestion de projet", "comité"],
    "writing": ["synthèse", "rédaction", "rapport"],
    "mobile": ["mobile", "smartphone", "application mobile"],
    "conversion": ["conversion", "taux", "crom"],
    "analytics": ["analytics", "ga4", "matomo", "tracking"],
}


PHASE_KEYWORDS: dict[str, list[str]] = {
    "discovery": ["diagnostic", "découvrir", "comprendre", "état des lieux"],
    "audit": ["audit", "revue", "évaluation"],
    "design": ["maquette", "design", "prototype", "wireframe"],
    "build": ["développer", "implémenter", "coder", "construire"],
    "review": ["revue", "relecture", "validation"],
    "handover": ["livrer", "livraison", "restitution", "plan d'action", "présentation"],
}


class BriefParserAgent:
    def __init__(self) -> None:
        self.llm = get_llm_client()

    def parse(self, raw: RawBriefInput) -> MissionBrief:
        """Return a structured MissionBrief for a raw input."""
        from ..llm.client import FixtureLLMClient
        try:
            if not isinstance(self.llm, FixtureLLMClient):
                return self._parse_via_llm(raw)
        except Exception:
            pass
        return self._parse_heuristic(raw)

    def _parse_via_llm(self, raw: RawBriefInput) -> MissionBrief:
        resp = self.llm.complete_json(
            system=SYSTEM_PROMPT,
            messages=[LLMMessage(role="user", content=raw.raw_brief)],
        )
        resp.setdefault("raw_brief", raw.raw_brief)
        resp.setdefault("confidence", 0.8)
        constraints = resp.get("constraints") or {}
        if raw.budget_eur is not None:
            constraints.setdefault("budget_eur", raw.budget_eur)
        if raw.deadline_days is not None:
            constraints.setdefault("deadline_days", raw.deadline_days)
        constraints.setdefault("language", raw.language)
        resp["constraints"] = constraints
        return MissionBrief.model_validate(resp)

    def _parse_heuristic(self, raw: RawBriefInput) -> MissionBrief:
        text = raw.raw_brief.lower()

        domains = [d for d, kws in DOMAIN_KEYWORDS.items() if any(k in text for k in kws)]
        if not domains:
            domains = ["consulting"]
        # promote primary domain to front
        if "ux" in domains and "design" in domains:
            domains.remove("design")
            domains.insert(1, "design")

        phase_hints = [p for p, kws in PHASE_KEYWORDS.items() if any(k in text for k in kws)]

        budget = raw.budget_eur
        if budget is None:
            m = re.search(r"(\d+[\s.]?\d*)\s*(k€|keur|000 *€|€|eur)", text)
            if m:
                n = m.group(1).replace(" ", "").replace(".", "")
                try:
                    budget = int(n) * (1000 if "k" in m.group(2).lower() else 1)
                except ValueError:
                    budget = None

        deadline = raw.deadline_days
        if deadline is None:
            m = re.search(r"(\d+)\s*(jours?|semaines?|mois)", text)
            if m:
                n = int(m.group(1))
                unit = m.group(2)
                if "semaine" in unit:
                    deadline = n * 7
                elif "mois" in unit:
                    deadline = n * 30
                else:
                    deadline = n

        deliverables = _extract_deliverables(raw.raw_brief)

        title = _build_title(raw.raw_brief, domains)

        red_flags: list[str] = []
        if budget is not None and budget < 500:
            red_flags.append("budget très faible (<500€) — vérifier la faisabilité")
        if deadline is not None and deadline < 2:
            red_flags.append("délai extrêmement court (<2j)")

        missing_info = []
        confidence = 0.75
        if budget is None:
            missing_info.append({
                "id": "budget",
                "question": "Quel budget envisagez-vous pour cette mission ?",
            })
            confidence -= 0.1
        if deadline is None:
            missing_info.append({
                "id": "deadline",
                "question": "Quelle est votre échéance cible (jours / semaines) ?",
            })
            confidence -= 0.1

        return MissionBrief(
            title=title,
            domains=domains,
            sub_domains=[d for d in ["mobile", "conversion", "analytics"] if d in text],
            deliverables=deliverables or ["synthèse d'analyse"],
            constraints=BriefConstraints(
                budget_eur=budget,
                deadline_days=deadline,
                language=raw.language,
            ),
            phase_hints=phase_hints or ["audit"],
            persona_hints=[],
            red_flags=red_flags,
            missing_info=[
                {"id": mi["id"], "question": mi["question"]} for mi in missing_info
            ],
            confidence=max(0.3, confidence),
            raw_brief=raw.raw_brief,
        )


def _extract_deliverables(text: str) -> list[str]:
    """Heuristic: look for 'livrable', 'rapport', 'deck', 'plan d'action', 'spec'."""
    t = text.lower()
    out: list[str] = []
    mapping = {
        "rapport": "rapport d'analyse",
        "audit": "rapport d'audit",
        "plan d'action": "plan d'action priorisé",
        "deck": "deck de présentation",
        "présentation": "deck de présentation",
        "synthèse": "synthèse exécutive",
        "spec": "spec technique",
        "cahier des charges": "cahier des charges technique",
        "compte-rendu": "compte-rendu de réunion",
    }
    for k, v in mapping.items():
        if k in t and v not in out:
            out.append(v)
    return out


def _build_title(raw: str, domains: list[str]) -> str:
    head = raw.strip().split(".")[0].split("\n")[0]
    head = head[:80].strip()
    if not head:
        head = f"Mission {' / '.join(domains[:2])}"
    return head[0].upper() + head[1:] if head else "Mission sans titre"

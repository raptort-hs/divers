"""Matching Agent — MissionBrief + TalentProfile → MatchingResult.

Spec: docs/tech/03-matching-agent.md.

MVP implementation is **deterministic** (no LLM call). Scoring is done with the weighted
formula from §5 of the spec, on taxonomy + governance + budget signals. Rationales are
template-driven in French. This makes the demo reproducible and API-key-free.

The LLM-augmented path (adds `deliverable_fit` via LLM judge + free-form explanation)
is gated behind `SYMBIOSE_LLM_MODE=anthropic`.
"""

from __future__ import annotations

from ..models.brief import MissionBrief
from ..models.skill import (
    MatchingResult,
    PlanOutlineStep,
    SelectedSkill,
    SkillManifest,
    UnmetNeed,
)
from ..models.talent import TalentProfile
from ..skills import get_registry


WEIGHTS: dict[str, float] = {
    "domain_fit":        0.25,
    "phase_fit":         0.15,
    "deliverable_fit":   0.20,
    "seniority_fit":     0.05,
    "language_fit":      0.05,
    "quality_signal":    0.15,
    "budget_fit":        0.10,
    "talent_complement": 0.05,
}


CERT_SCORE = {"gold": 1.0, "silver": 0.8, "bronze": 0.6, None: 0.3}


class MatchingAgent:
    def __init__(self) -> None:
        self.registry = get_registry()

    def match(self, brief: MissionBrief, talent: TalentProfile) -> MatchingResult:
        # 1. Shortlist candidates via registry search.
        candidates = self.registry.search(
            domains=brief.domains,
            phases=brief.phase_hints or None,
            seniority=talent.seniority,
            certified_only=False,
        )
        if not candidates:
            return MatchingResult(
                selected_skills=[],
                mission_plan_outline=[],
                unmet_needs=[UnmetNeed(
                    need="Aucun skill du registre ne couvre les domaines demandés",
                    reason="Le Skill-Importer Agent doit enrichir le registre.",
                )],
                total_estimated_cost_tokens=0,
                explanation_fr="Registre insuffisant pour cette mission.",
            )

        # 2. Score every candidate.
        scored: list[tuple[float, SkillManifest, dict[str, float]]] = []
        for summary in candidates:
            manifest = self.registry.get(summary.id, summary.version)
            if manifest is None:
                continue
            sub = self._score_subscores(manifest, brief, talent)
            total = sum(sub[k] * WEIGHTS[k] for k in WEIGHTS)
            scored.append((total, manifest, sub))

        scored.sort(key=lambda t: t[0], reverse=True)

        # 3. Compose a minimal non-redundant set, respecting budget.
        selected: list[SelectedSkill] = []
        used_phases: set[str] = set()
        used_deliverables: set[str] = set()
        budget = talent.budget_tokens
        cost_running = 0
        for total, manifest, sub in scored:
            if len(selected) >= 7:
                break
            if total < 0.45:
                continue  # floor
            price = manifest.economics.price_tokens if manifest.economics else 0
            if cost_running + price > budget:
                continue
            # redundancy check: skip if 100% of phases already covered by selected
            this_phases = set(manifest.taxonomy.mission_phases)
            this_delivs = {o.name for o in manifest.interface.outputs}
            if (this_phases - used_phases) == set() and (this_delivs - used_deliverables) == set() and selected:
                continue
            selected.append(self._to_selected(manifest, brief, sub, price, total))
            used_phases.update(this_phases)
            used_deliverables.update(this_delivs)
            cost_running += price

        # 4. Build the plan outline grouped by phase order.
        plan = _build_plan_outline(selected, brief)

        # 5. Unmet needs: deliverables not covered by any selected skill.
        covered_delivs = set()
        for s in selected:
            covered_delivs.update(s.covers_deliverables)
        unmet = []
        for want in brief.deliverables:
            if not any(_fuzzy_in(want, c) for c in covered_delivs):
                unmet.append(UnmetNeed(
                    need=want,
                    reason="Aucun skill sélectionné ne couvre explicitement ce livrable. "
                           "À envisager : import via Skill-Importer Agent.",
                ))

        explanation = _compose_explanation(selected, unmet, cost_running, budget)

        return MatchingResult(
            selected_skills=selected,
            mission_plan_outline=plan,
            unmet_needs=unmet,
            total_estimated_cost_tokens=cost_running,
            explanation_fr=explanation,
        )

    # -- scoring -------------------------------------------------------------

    def _score_subscores(
        self, m: SkillManifest, brief: MissionBrief, talent: TalentProfile
    ) -> dict[str, float]:
        b_domains = _lc(brief.domains)
        b_sub = _lc(brief.sub_domains)
        b_phases = _lc(brief.phase_hints)
        s_domains = _lc(m.taxonomy.domains + m.taxonomy.sub_domains)
        s_phases = _lc(m.taxonomy.mission_phases)
        s_tags = _lc(m.taxonomy.tags)

        domain_fit = _overlap(b_domains | b_sub, s_domains) if b_domains else 0.5
        phase_fit = _overlap(b_phases, s_phases) if b_phases else 0.5

        # deliverable_fit: rough keyword overlap between brief.deliverables and skill outputs/tags
        delivs_text = " ".join(brief.deliverables).lower()
        outputs_text = " ".join(o.name for o in m.interface.outputs) + " " + " ".join(s_tags)
        deliverable_fit = _keyword_overlap(delivs_text, outputs_text.lower())

        seniority_fit = 1.0 if talent.seniority in m.taxonomy.seniority_target else 0.3

        lang_ok = brief.constraints.language in m.taxonomy.languages
        language_fit = 1.0 if lang_ok else 0.3

        quality_signal = CERT_SCORE.get(m.governance.certification_level if m.governance.certified else None, 0.3)
        if m.governance.avg_rating is not None:
            quality_signal = 0.6 * quality_signal + 0.4 * (m.governance.avg_rating / 5.0)

        price = m.economics.price_tokens if m.economics else 0
        if talent.budget_tokens <= 0:
            budget_fit = 1.0
        elif price <= talent.budget_tokens:
            budget_fit = 1.0
        else:
            budget_fit = max(0.0, 1.0 - (price - talent.budget_tokens) / talent.budget_tokens)

        t_gaps = _lc(talent.gaps)
        talent_complement = 1.0 if (t_gaps & s_domains) else 0.5

        return {
            "domain_fit": domain_fit,
            "phase_fit": phase_fit,
            "deliverable_fit": deliverable_fit,
            "seniority_fit": seniority_fit,
            "language_fit": language_fit,
            "quality_signal": quality_signal,
            "budget_fit": budget_fit,
            "talent_complement": talent_complement,
        }

    def _to_selected(
        self,
        m: SkillManifest,
        brief: MissionBrief,
        sub: dict[str, float],
        price: int,
        total: float,
    ) -> SelectedSkill:
        covers_delivs = []
        delivs_text = " ".join(brief.deliverables).lower()
        for o in m.interface.outputs:
            if o.name.replace("_", " ") in delivs_text or any(
                t in delivs_text for t in m.taxonomy.tags
            ):
                covers_delivs.append(o.description or o.name)

        rationale = _compose_rationale(m, sub, brief)

        return SelectedSkill(
            skill_id=m.id,
            version=m.version,
            rationale_fr=rationale,
            covers_deliverables=covers_delivs or [m.description.short.fr],
            covers_phases=list(m.taxonomy.mission_phases),
            complements_talent_gaps=[],
            estimated_cost_tokens=price,
            confidence=min(1.0, total),
        )


# -- helpers -------------------------------------------------------------------

def _lc(xs) -> set[str]:
    return {str(x).lower() for x in (xs or [])}


def _overlap(a: set[str], b: set[str]) -> float:
    if not a:
        return 0.0
    return len(a & b) / len(a)


def _keyword_overlap(a: str, b: str) -> float:
    a_words = {w for w in re.findall(r"\w+", a) if len(w) >= 4}
    b_words = {w for w in re.findall(r"\w+", b) if len(w) >= 4}
    if not a_words:
        return 0.5
    return len(a_words & b_words) / len(a_words)


def _fuzzy_in(needle: str, hay: str) -> bool:
    n_words = {w for w in re.findall(r"\w+", needle.lower()) if len(w) >= 4}
    h_words = {w for w in re.findall(r"\w+", hay.lower()) if len(w) >= 4}
    return bool(n_words & h_words)


PHASE_ORDER = ["discovery", "audit", "design", "build", "review", "handover"]


def _build_plan_outline(selected: list[SelectedSkill], brief: MissionBrief) -> list[PlanOutlineStep]:
    by_phase: dict[str, list[str]] = {}
    for s in selected:
        for p in s.covers_phases:
            by_phase.setdefault(p, []).append(s.skill_id)
    phases_sorted = sorted(by_phase.keys(), key=lambda p: PHASE_ORDER.index(p) if p in PHASE_ORDER else 99)
    out: list[PlanOutlineStep] = []
    for p in phases_sorted:
        skills = by_phase[p]
        rationale = f"Phase {p} : {', '.join(skills)}."
        out.append(PlanOutlineStep(phase=p, skills=skills, rationale=rationale))
    return out


def _compose_rationale(m: SkillManifest, sub: dict[str, float], brief: MissionBrief) -> str:
    bits = []
    if sub["domain_fit"] > 0.5:
        bits.append(f"couvre les domaines demandés ({', '.join(m.taxonomy.domains[:2])})")
    if sub["phase_fit"] > 0.5:
        bits.append(f"aligné sur les phases {', '.join(m.taxonomy.mission_phases[:2])}")
    if sub["quality_signal"] >= 0.8:
        level = m.governance.certification_level or "certifié"
        bits.append(f"skill {level}")
    if sub["budget_fit"] == 1.0:
        price = m.economics.price_tokens if m.economics else 0
        bits.append(f"coût {price} tokens dans le budget")
    if sub["language_fit"] == 1.0:
        bits.append(f"langue {brief.constraints.language} supportée")
    if not bits:
        bits.append("pertinence générale sur le brief")
    return " · ".join(bits).capitalize() + "."


def _compose_explanation(
    selected: list[SelectedSkill],
    unmet: list[UnmetNeed],
    cost: int,
    budget: int,
) -> str:
    if not selected:
        return "Aucun skill compatible n'a pu être sélectionné dans le budget imparti."
    bits = [
        f"{len(selected)} skill(s) sélectionné(s) pour un coût total de {cost}/{budget} tokens.",
    ]
    if unmet:
        bits.append(f"{len(unmet)} besoin(s) non couvert(s) — import à envisager.")
    else:
        bits.append("Tous les livrables du brief sont couverts.")
    return " ".join(bits)


# late import to avoid top-level regex cost before other imports resolved
import re

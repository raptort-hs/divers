"""Mission Copilot Agent — runtime assistant inside a mission workspace.

Spec: docs/tech/05-mission-copilot-agent.md.

MVP implementation is a thin, event-emitting runner. It executes skills by pairing the
skill's system prompt with an input payload and calling the LLM client (or returns a
canned simulated result when the LLM is in fixture mode without a matching fixture).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

from ..config import CONFIG
from ..llm import get_llm_client, LLMMessage
from ..models.mission import Mission
from ..models.skill import SkillManifest
from ..skills import get_registry


@dataclass
class CopilotEvent:
    kind: str
    payload: dict[str, Any]
    ts: datetime = field(default_factory=datetime.utcnow)

    def to_json(self) -> str:
        return json.dumps({"kind": self.kind, "ts": self.ts.isoformat() + "Z", **self.payload}, ensure_ascii=False)


class MissionCopilotAgent:
    def __init__(self, mission: Mission) -> None:
        self.mission = mission
        self.registry = get_registry()
        self.llm = get_llm_client()
        self.workspace = Path(mission.workspace_path)
        self.workspace.mkdir(parents=True, exist_ok=True)

    # --- public driver ------------------------------------------------------

    def run_kickoff(self) -> list[CopilotEvent]:
        """Emit the initial event stream: plan summary + first assistant message."""
        events: list[CopilotEvent] = []
        events.append(CopilotEvent("assistant_message", {
            "text": self._welcome_message(),
        }))
        events.append(CopilotEvent("plan_update", {
            "plan": [step.model_dump() for step in self.mission.plan],
        }))
        return events

    def run_plan(self) -> Iterable[CopilotEvent]:
        """Execute every plan step in order. Yields events as they happen.
        Each skill is run at most once per mission — its first occurrence in the plan."""
        yield from self.run_kickoff()
        executed: set[str] = set()
        for idx, step in enumerate(self.mission.plan):
            for skill_id in step.skills:
                if skill_id in executed:
                    continue
                executed.add(skill_id)
                manifest = self.registry.get(skill_id)
                if manifest is None:
                    yield CopilotEvent("quality_warning", {
                        "severity": "high",
                        "message": f"Skill {skill_id} introuvable dans le registre.",
                    })
                    continue
                yield from self._run_skill(manifest, step_phase=step.phase, step_idx=idx)
        yield CopilotEvent("assistant_message", {
            "text": "Exécution du plan terminée. Relis les livrables dans le workspace avant envoi client.",
        })

    # --- internals ----------------------------------------------------------

    def _welcome_message(self) -> str:
        brief = self.mission.brief
        skills = ", ".join(a.skill_id for a in self.mission.activations)
        return (
            f"Mission « {brief.title} » activée. "
            f"{len(self.mission.activations)} skill(s) prêt(s) : {skills}. "
            f"Plan en {len(self.mission.plan)} phase(s). "
            "Je t'accompagne à chaque étape."
        )

    def _run_skill(self, manifest: SkillManifest, *, step_phase: str, step_idx: int):
        inputs = self._compose_inputs(manifest)
        yield CopilotEvent("skill_run_start", {
            "skill_id": manifest.id,
            "version": manifest.version,
            "inputs": inputs,
            "phase": step_phase,
        })
        started = datetime.utcnow()
        try:
            outputs = self._invoke_skill(manifest, inputs)
            status = "succeeded"
            error = None
        except Exception as e:
            outputs = {}
            status = "failed"
            error = str(e)
        duration_ms = int((datetime.utcnow() - started).total_seconds() * 1000)
        self._persist_outputs(manifest, outputs)
        yield CopilotEvent("skill_run_result", {
            "skill_id": manifest.id,
            "version": manifest.version,
            "status": status,
            "outputs_preview": _preview(outputs),
            "duration_ms": duration_ms,
            "cost_tokens": manifest.economics.price_tokens if manifest.economics else 0,
            "error": error,
        })

    def _compose_inputs(self, manifest: SkillManifest) -> dict[str, Any]:
        """Fill the skill's declared inputs with values drawn from the brief / workspace."""
        brief = self.mission.brief
        filled: dict[str, Any] = {}
        for field_ in manifest.interface.inputs:
            filled[field_.name] = _demo_value_for(field_.name, brief)
        return filled

    def _invoke_skill(self, manifest: SkillManifest, inputs: dict[str, Any]) -> dict[str, Any]:
        """Call the LLM with the skill's system prompt + inputs.
        In fixture mode without a matching fixture, returns a simulated placeholder.
        """
        from ..llm.client import FixtureLLMClient
        user_payload = json.dumps({"inputs": inputs, "mission_brief": self.mission.brief.model_dump()}, ensure_ascii=False)
        try:
            return self.llm.complete_json(
                system=manifest.system_prompt,
                messages=[LLMMessage(role="user", content=user_payload)],
                fixture_key=f"skill_{manifest.id}",
            )
        except FileNotFoundError:
            if isinstance(self.llm, FixtureLLMClient):
                return _simulated_output(manifest, inputs)
            raise

    def _persist_outputs(self, manifest: SkillManifest, outputs: dict[str, Any]) -> None:
        target_dir = self.workspace / "skill_runs" / manifest.id
        target_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        (target_dir / f"{stamp}.json").write_text(
            json.dumps(outputs, ensure_ascii=False, indent=2), encoding="utf-8"
        )


# -- helpers -------------------------------------------------------------------

def _demo_value_for(field_name: str, brief) -> Any:
    fn = field_name.lower()
    if "url" in fn:
        return "https://exemple-boutique.fr"
    if "goal" in fn:
        return brief.title
    if "persona" in fn:
        return brief.persona_hints or ["visiteur standard"]
    if "audience" in fn:
        return brief.persona_hints[0] if brief.persona_hints else "dirigeant PME"
    if "angle" in fn:
        return "restitution + décision budget"
    if "attendees" in fn:
        return []
    if "raw_notes" in fn:
        return "Notes de mission (non fournies dans ce run démo)."
    if "source" in fn or "document" in fn or "content" in fn:
        return f"Document de référence de la mission « {brief.title} »."
    if "need" in fn:
        return brief.raw_brief
    if "tech_constraints" in fn:
        return []
    if "slide_count_target" in fn:
        return 10
    if "meeting_context" in fn:
        return "Réunion d'équipe"
    if "decision_required" in fn:
        return "Décider des prochaines étapes"
    return ""


def _simulated_output(manifest: SkillManifest, inputs: dict[str, Any]) -> dict[str, Any]:
    """Produce a placeholder that reflects the declared output schema — keeps the demo
    runnable without LLM credentials or fixtures."""
    out: dict[str, Any] = {"_simulated": True, "skill_id": manifest.id}
    for o in manifest.interface.outputs:
        if o.type.startswith("markdown"):
            out[o.name] = f"# {manifest.name} — résultat simulé\n\nGénéré depuis {list(inputs.keys())}."
        elif o.type.startswith("structured:table"):
            out[o.name] = [{"col_a": "exemple", "col_b": "exemple"}]
        elif o.type.startswith("structured:list"):
            out[o.name] = [{"id": "x1", "text": "Point simulé"}]
        elif o.type.startswith("file:"):
            out[o.name] = f"/workspace/{manifest.id}/{o.name}.placeholder"
        else:
            out[o.name] = "résultat simulé"
    return out


def _preview(outputs: dict[str, Any]) -> dict[str, Any]:
    """Truncate long strings for display in the event stream."""
    out: dict[str, Any] = {}
    for k, v in outputs.items():
        if isinstance(v, str) and len(v) > 200:
            out[k] = v[:200] + "…"
        else:
            out[k] = v
    return out

"""Test that every skill under skills/native validates and loads cleanly."""
from __future__ import annotations

import yaml
from pathlib import Path

from symbiose.config import CONFIG
from symbiose.skills import SkillRegistry
from symbiose.skills.validator import validate_manifest


def test_json_schema_exists():
    assert CONFIG.schema_path.exists(), f"missing schema at {CONFIG.schema_path}"


def test_every_native_skill_yaml_validates():
    root = CONFIG.skills_root / "native"
    yamls = list(root.rglob("skill.yaml"))
    assert yamls, "no skill bundle found"
    for y in yamls:
        raw = yaml.safe_load(y.read_text(encoding="utf-8"))
        validate_manifest(raw)


def test_registry_loads_all_native_skills():
    reg = SkillRegistry()
    loaded = reg.load_directory(CONFIG.skills_root / "native")
    assert len(loaded) == 5
    ids = {m.id for m in loaded}
    assert ids == {
        "audit-ux-express",
        "executive-summary-generator",
        "meeting-notes-to-actions",
        "client-deck-builder",
        "technical-spec-writer",
    }


def test_registry_search_by_domain():
    reg = SkillRegistry()
    reg.load_directory(CONFIG.skills_root / "native")
    results = reg.search(domains=["ux"])
    ids = {s.id for s in results}
    assert "audit-ux-express" in ids


def test_registry_search_filters_by_phase():
    reg = SkillRegistry()
    reg.load_directory(CONFIG.skills_root / "native")
    handover = reg.search(phases=["handover"])
    ids = {s.id for s in handover}
    assert "executive-summary-generator" in ids
    assert "client-deck-builder" in ids

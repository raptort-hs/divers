"""Skill registry — loads bundles from disk, validates them, exposes search.

The filesystem (skills/native/<id>/, skills/community/, skills/external/) is the
source of truth. The registry caches manifests in memory at process start.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Iterable
import yaml

from ..config import CONFIG
from ..models.skill import SkillManifest, SkillSummary
from .validator import validate_manifest


class SkillLoadError(Exception):
    """Raised when a skill bundle cannot be loaded."""


class SkillRegistry:
    """In-memory index of validated skill manifests."""

    def __init__(self) -> None:
        self._skills: dict[str, SkillManifest] = {}
        self._by_version: dict[tuple[str, str], SkillManifest] = {}

    # --- loading ------------------------------------------------------------

    def load_directory(self, root: Path) -> list[SkillManifest]:
        """Load every skill bundle under `root` (recursive 2 levels)."""
        loaded: list[SkillManifest] = []
        if not root.exists():
            return loaded
        for bundle_dir in _iter_bundle_dirs(root):
            try:
                manifest = self._load_bundle(bundle_dir)
            except SkillLoadError as e:
                # Skip bad bundles, surface on stderr
                import sys
                print(f"[registry] skipping {bundle_dir}: {e}", file=sys.stderr)
                continue
            self._skills[manifest.id] = manifest
            self._by_version[(manifest.id, manifest.version)] = manifest
            loaded.append(manifest)
        return loaded

    def _load_bundle(self, bundle_dir: Path) -> SkillManifest:
        skill_yaml = bundle_dir / "skill.yaml"
        prompt_md = bundle_dir / "system_prompt.md"
        if not skill_yaml.exists() or not prompt_md.exists():
            raise SkillLoadError(
                f"missing skill.yaml or system_prompt.md in {bundle_dir}"
            )
        raw = yaml.safe_load(skill_yaml.read_text(encoding="utf-8"))
        validate_manifest(raw)
        manifest = SkillManifest.model_validate(raw)
        manifest.system_prompt = prompt_md.read_text(encoding="utf-8")
        manifest.bundle_path = str(bundle_dir)
        examples_dir = bundle_dir / "examples"
        if examples_dir.exists():
            for ex_file in sorted(examples_dir.glob("*.yaml")):
                manifest.examples.append(yaml.safe_load(ex_file.read_text(encoding="utf-8")))
        return manifest

    # --- query --------------------------------------------------------------

    def all(self) -> list[SkillManifest]:
        return list(self._skills.values())

    def get(self, skill_id: str, version: str | None = None) -> SkillManifest | None:
        if version:
            return self._by_version.get((skill_id, version))
        return self._skills.get(skill_id)

    def summaries(self) -> list[SkillSummary]:
        return [_to_summary(m) for m in self._skills.values()]

    def search(
        self,
        *,
        query: str | None = None,
        domains: Iterable[str] | None = None,
        phases: Iterable[str] | None = None,
        seniority: str | None = None,
        certified_only: bool = False,
        max_cost_tokens: int | None = None,
    ) -> list[SkillSummary]:
        domains_set = {d.lower() for d in (domains or [])}
        phases_set = {p.lower() for p in (phases or [])}
        q = (query or "").lower().strip()
        results: list[SkillSummary] = []
        for m in self._skills.values():
            if certified_only and not m.governance.certified:
                continue
            if max_cost_tokens is not None and m.economics and m.economics.price_tokens > max_cost_tokens:
                continue
            m_domains = {d.lower() for d in m.taxonomy.domains}
            m_phases = {p.lower() for p in m.taxonomy.mission_phases}
            if domains_set and m_domains.isdisjoint(domains_set):
                continue
            if phases_set and m_phases.isdisjoint(phases_set):
                continue
            if seniority and seniority not in m.taxonomy.seniority_target:
                continue
            if q:
                hay = " ".join([
                    m.name.lower(),
                    m.description.short.fr.lower(),
                    " ".join(m.taxonomy.tags),
                    " ".join(m.taxonomy.domains),
                    " ".join(m.taxonomy.sub_domains),
                ])
                if q not in hay:
                    continue
            results.append(_to_summary(m))
        return results


def _iter_bundle_dirs(root: Path) -> Iterable[Path]:
    """Yield directories that look like skill bundles (contain skill.yaml)."""
    for skill_yaml in root.rglob("skill.yaml"):
        yield skill_yaml.parent


def _to_summary(m: SkillManifest) -> SkillSummary:
    return SkillSummary(
        id=m.id,
        version=m.version,
        name=m.name,
        short_description=m.description.short.fr,
        domains=m.taxonomy.domains,
        mission_phases=m.taxonomy.mission_phases,
        seniority_target=m.taxonomy.seniority_target,
        languages=m.taxonomy.languages,
        certified=m.governance.certified,
        certification_level=m.governance.certification_level,
        price_tokens=m.economics.price_tokens if m.economics else 0,
        offline=m.runtime.offline,
    )


@lru_cache(maxsize=1)
def get_registry() -> SkillRegistry:
    """Get the process-wide registry, lazily initialized from disk."""
    reg = SkillRegistry()
    reg.load_directory(CONFIG.skills_root)
    return reg

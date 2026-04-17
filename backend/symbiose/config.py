"""Runtime configuration. Resolved once at process start."""

from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Config:
    repo_root: Path
    skills_root: Path
    schema_path: Path
    workspace_root: Path
    llm_mode: str  # "anthropic" | "fixture"
    anthropic_api_key: str | None
    anthropic_model: str
    session_secret: str
    http_port: int


def load_config() -> Config:
    repo = REPO_ROOT
    return Config(
        repo_root=repo,
        skills_root=repo / "skills",
        schema_path=repo / "docs" / "tech" / "schemas" / "skill.schema.json",
        workspace_root=repo / "backend" / ".workspace",
        llm_mode=os.environ.get("SYMBIOSE_LLM_MODE", "fixture"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        anthropic_model=os.environ.get("SYMBIOSE_MODEL", "claude-opus-4-7"),
        session_secret=os.environ.get("SYMBIOSE_SESSION_SECRET", "dev-secret-change-me"),
        http_port=int(os.environ.get("SYMBIOSE_PORT", "8000")),
    )


CONFIG = load_config()

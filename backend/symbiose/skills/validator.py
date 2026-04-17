"""Validate skill manifests against docs/tech/schemas/skill.schema.json."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from ..config import CONFIG


class ManifestValidationError(Exception):
    """Raised when a skill manifest fails JSON-Schema validation."""


@lru_cache(maxsize=1)
def _load_schema() -> dict[str, Any]:
    path: Path = CONFIG.schema_path
    if not path.exists():
        raise FileNotFoundError(f"skill.schema.json not found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict[str, Any]) -> None:
    """Raises `ManifestValidationError` on failure."""
    schema = _load_schema()
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(manifest), key=lambda e: list(e.absolute_path))
    if errors:
        msg_lines = [
            f"- {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
            for e in errors[:10]
        ]
        raise ManifestValidationError(
            f"{len(errors)} validation error(s):\n" + "\n".join(msg_lines)
        )

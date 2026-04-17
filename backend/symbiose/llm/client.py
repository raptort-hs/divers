"""LLM client abstraction.

Two implementations:
- `AnthropicLLMClient`: calls the Anthropic API (used when ANTHROPIC_API_KEY is set and
  SYMBIOSE_LLM_MODE=anthropic).
- `FixtureLLMClient`: returns deterministic responses from `tests/fixtures/llm/`. Default
  mode for the MVP demo — makes it fully runnable without an API key.

Agents should only ever talk to `LLMClient` — never import anthropic directly.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

from ..config import CONFIG


@dataclass
class LLMMessage:
    role: str  # "user" | "assistant" | "system"
    content: str


class LLMClient(Protocol):
    def complete_json(
        self,
        *,
        system: str,
        messages: list[LLMMessage],
        fixture_key: str | None = None,
    ) -> dict[str, Any]:
        """Return a JSON dict. `fixture_key` lets the caller override fixture lookup."""


class FixtureLLMClient:
    """Returns canned JSON from `tests/fixtures/llm/<key>.json`.

    The `fixture_key` is either explicit or derived from a stable hash of the prompt.
    Missing fixtures raise FileNotFoundError — caller decides whether to fallback.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or (CONFIG.repo_root / "backend" / "tests" / "fixtures" / "llm")

    def complete_json(
        self,
        *,
        system: str,
        messages: list[LLMMessage],
        fixture_key: str | None = None,
    ) -> dict[str, Any]:
        key = fixture_key or self._derive_key(system, messages)
        path = self.root / f"{key}.json"
        if not path.exists():
            raise FileNotFoundError(
                f"LLM fixture not found: {path}. Set SYMBIOSE_LLM_MODE=anthropic "
                f"(with ANTHROPIC_API_KEY) or add the fixture."
            )
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _derive_key(system: str, messages: list[LLMMessage]) -> str:
        raw = system + "||" + "||".join(f"{m.role}:{m.content}" for m in messages)
        return "auto_" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


class AnthropicLLMClient:
    """Wraps anthropic.Anthropic. Import is lazy so the package works without it installed."""

    def __init__(self, *, api_key: str, model: str) -> None:
        try:
            from anthropic import Anthropic  # type: ignore
        except ImportError as e:
            raise RuntimeError(
                "anthropic SDK not installed. `pip install 'symbiose[llm]'`"
            ) from e
        self._client = Anthropic(api_key=api_key)
        self._model = model

    def complete_json(
        self,
        *,
        system: str,
        messages: list[LLMMessage],
        fixture_key: str | None = None,  # ignored
    ) -> dict[str, Any]:
        resp = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=system + "\n\nReturn ONLY valid JSON. No markdown fences.",
            messages=[{"role": m.role, "content": m.content} for m in messages],
        )
        text = resp.content[0].text if resp.content else "{}"
        # Tolerate ```json fences
        text = text.strip()
        if text.startswith("```"):
            text = text.strip("`").lstrip("json").strip()
        return json.loads(text)


@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    if CONFIG.llm_mode == "anthropic" and CONFIG.anthropic_api_key:
        return AnthropicLLMClient(
            api_key=CONFIG.anthropic_api_key, model=CONFIG.anthropic_model
        )
    return FixtureLLMClient()

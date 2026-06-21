"""OpenRouter LLM / embedder shims (requires OPENROUTER_API_KEY)."""

from __future__ import annotations

from typing import Any


class OpenRouterLlm:
    def __init__(self, api_key: str | None = None, model: str = "anthropic/claude-3.5-sonnet") -> None:
        self.api_key = api_key
        self.model = model

    def complete(self, prompt: str, **kwargs: Any) -> str:
        # TODO: real httpx call to OpenRouter
        return f"[stub-llm] {prompt[:100]}"


class OpenRouterEmbedder:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key

    def embed(self, text: str) -> list[float]:
        # TODO: real embedding
        return [0.0] * 1536

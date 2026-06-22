"""OpenRouter LLM / embedder (OpenAI-compatible endpoint).

Requires OPENROUTER_API_KEY. Falls back to deterministic stub when key unset.
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from openai import OpenAI


class OpenRouterLlm:
    def __init__(self, api_key: str | None = None, model: str = "anthropic/claude-3.5-sonnet") -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model
        self._client: OpenAI | None = None
        if self.api_key:
            self._client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key)

    def complete(self, prompt: str, **kwargs: Any) -> str:
        if not self._client:
            return f"[stub-llm] {prompt[:100]}"
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        return resp.choices[0].message.content or ""


class OpenRouterEmbedder:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self._client: OpenAI | None = None
        if self.api_key:
            self._client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=self.api_key)

    def embed(self, text: str) -> list[float]:
        if not self._client:
            return [0.0] * 1536
        resp = self._client.embeddings.create(model="text-embedding-3-small", input=text)
        return resp.data[0].embedding

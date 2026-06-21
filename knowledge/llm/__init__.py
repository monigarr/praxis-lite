"""LLM and embedder ABCs + OpenRouter + fake variants."""

from .openrouter import OpenRouterLlm, OpenRouterEmbedder

__all__ = ["OpenRouterLlm", "OpenRouterEmbedder"]

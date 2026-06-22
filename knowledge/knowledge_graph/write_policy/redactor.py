"""PII / secret redactor (regex + optional LLM)."""

import re

from knowledge.llm.openrouter import OpenRouterLlm


class Redactor:
    _PATTERNS = [
        (re.compile(r"sk-[A-Za-z0-9]{20,}"), "[REDACTED-API-KEY]"),
        (re.compile(r"AKIA[0-9A-Z]{16}"), "[REDACTED-AWS-KEY]"),
        (re.compile(r"ghp_[A-Za-z0-9]{36}"), "[REDACTED-GH-TOKEN]"),
    ]

    def __init__(self, llm: OpenRouterLlm | None = None) -> None:
        self.llm = llm

    def redact(self, text: str) -> str:
        out = text
        for pat, repl in self._PATTERNS:
            out = pat.sub(repl, out)
        if self.llm:
            hint = self.llm.complete(f"Redact any emails, tokens, or secrets in: {out[:200]}")
            if hint and len(hint) < len(out) * 1.2:
                out = hint
        return out

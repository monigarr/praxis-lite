"""PII / secret redactor stub."""

class Redactor:
    def redact(self, text: str) -> str:
        # TODO: real regex + LLM redaction
        return text.replace("sk-", "[REDACTED]")

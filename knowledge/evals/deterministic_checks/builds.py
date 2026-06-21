"""Deterministic build/compile checks for coding tasks."""

from __future__ import annotations


def check_builds(files: dict[str, str]) -> bool:
    """Return True if Python files in the workspace have no syntax errors."""
    import ast

    for path, content in files.items():
        if path.endswith(".py"):
            try:
                ast.parse(content)
            except SyntaxError:
                return False
    return True

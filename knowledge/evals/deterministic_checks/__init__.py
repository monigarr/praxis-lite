"""Deterministic check registry."""

from __future__ import annotations

from .builds import check_builds
from .poetry import check_iambic_poem

REGISTRY = {
    "builds": check_builds,
    "iambic_poem": check_iambic_poem,
}

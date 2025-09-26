"""Lightweight adapters that re-export core types from the monolith.

This allows gradual extraction without changing import sites.
"""
from __future__ import annotations

# Import from the monolith, renaming to short aliases for new imports.
try:
    from e8_mind_server_M24 import E8Mind as Mind  # noqa: F401
except Exception:  # pragma: no cover - keep import-safe in smoke runs
    Mind = object  # type: ignore[assignment]

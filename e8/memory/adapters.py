"""Re-export memory types from the monolith for compatibility."""
from __future__ import annotations

try:
    from e8_mind_server_M24 import MemoryManager as MemoryManager  # noqa: F401
except Exception:  # pragma: no cover
    MemoryManager = object  # type: ignore[assignment]

"""Re-export scheduler types from the monolith for compatibility."""
from __future__ import annotations

try:
    from e8_mind_server_M24 import CognitiveScheduler as CognitiveScheduler  # noqa: F401
except Exception:  # pragma: no cover
    CognitiveScheduler = object  # type: ignore[assignment]

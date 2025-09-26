"""Re-export LLM gateway helpers from the monolith for compatibility."""
from __future__ import annotations

try:
    from e8_mind_server_M24 import _async_call_llm_internal as async_call_llm_internal  # noqa: F401
except Exception:  # pragma: no cover
    async def async_call_llm_internal(*args, **kwargs):  # type: ignore[empty-body]
        pass

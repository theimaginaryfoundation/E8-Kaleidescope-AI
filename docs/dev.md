# Developer Notes

## Linting (Ruff)

- Install dev tools (once): `uv sync --extra dev`
- Run lint (non-blocking): `uv run ruff check --exit-zero .`

Notes:
- The monolith `e8_mind_server_M24.py` is excluded from lint by default to avoid large diffs.
- We’ll enable stricter rules and CI gates after modularization lands.


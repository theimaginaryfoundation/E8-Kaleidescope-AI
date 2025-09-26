## Protocol Checklist (STRICT MODE)

- [ ] Session log committed under `docs/sessions/`
  - Path: <!-- docs/sessions/YYYYMMDDThhmmssZ-<slug>.md -->
  - Includes: `prompt_path`, `prompt_sha256`, and embedded prompt snapshot
- [ ] Prompt archived under `prompts/backlog/done/YYYY/mm/` (untracked locally)
- [ ] Smoke test verification noted (`uv run python scripts/smoke_memory.py`)
- [ ] Acceptance: human approved (“accept” captured in session log)

Context / Summary

- What changed:
- Why now:

Notes

- Any risk flags or follow-ups:


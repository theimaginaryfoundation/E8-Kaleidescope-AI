# Session Log
- date: 20250926T140623ZZ
- orchestrator_model: gpt-5-high
- codex_model: gpt-5-codex
- prompt: prompts/backlog/now/BL-20250926-protocol-strict-mode.md
- prompt_sha256: bc00d97f5d47c8c77fe49fe6152dd76329b777e906f5ace8ace69746b019eab2

## Changes Summary
- key files:
  - AGENTS.md: add STRICT MODE policy and enforcement aids
  - .github/PULL_REQUEST_TEMPLATE.md: add protocol checklist
  - scripts/protocol_guard.md: optional local guard instructions
- rationale:
  - Enforce the orchestration protocol across all edits and capture intent explicitly.

## Prompt Snapshot (do not edit)
```
---
id: BL-20250926-protocol-strict-mode
title: Enforce strict-mode protocol (AGENTS.md update + PR template)
owner: @ty
created_utc: 2025-09-26T00:00:00Z
acceptance:
  - AGENTS.md updated to require protocol for ALL changes (including docs/config)
  - Add .github/PULL_REQUEST_TEMPLATE.md requiring session log + prompt SHA details
  - Optional: add scripts/protocol_guard.md with hook instructions (no auto-install)
  - Smoke test passes
risk: low
notes: |
  Tighten rules to avoid manual edits and make expectations explicit.
---

# Context

We want strict mode across the board: every change must flow through the codex_orchestration protocol, with session logs and prompt hashes.

# Task

- Update AGENTS.md to add a Strict Mode section that applies to all edits.
- Add a PR template that requires linking the session log and capturing prompt SHA.
- Document optional local git hook installation instructions.

# Acceptance

- PR template visible under .github/PULL_REQUEST_TEMPLATE.md and referenced in AGENTS.md.
- AGENTS.md explicitly states strict-mode applies to all code, docs, and config changes.

# Out of scope

- CI enforcement; we will add it later when the team is ready.
```

## Verification
- smoke: pass
- greps:
  - 34:> Protocol Policy (STRICT MODE): ALL edits must flow through the codex_orchestration protocol (see §5). This includes code, docs, configs, and scripts. Every change requires:
  - 1:## Protocol Checklist (STRICT MODE)

## Decision
- accept: yes

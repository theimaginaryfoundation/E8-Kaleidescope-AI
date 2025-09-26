# Agent Playbook: E8 Overview & Protocol

This file tracks our shared mental model, the ongoing cleanup of the Python codebase, and the orchestration protocol for making changes via Codex. Think of it as a mission brief for any human or AI “agent” touching the project.

## 1. Current System Snapshot (Python)
- **Kernel:** `e8_mind_server_M24.py` instantiates `E8Mind` and hosts the HTTP API. Control loop lives in `E8Mind.run_cognitive_cycle`.
- **Scheduler:** `CognitiveScheduler` (same file) orchestrates teacher/explorer/dream tasks via cadence gates and queue pressure checks.
- **Memory graph:** `MemoryManager` holds the knowledge graph (`GraphDB`), vector store, KD-tree/FAISS index, and retrolink logic.
- **LLM gateway:** `_async_call_llm_internal` builds prompts, dispatches to the primary provider, and optionally blends a local model.
- **Physics add-ons:** Electromagnetic/curvature modules are optional; disable with `E8_SPACETIME_CURVATURE=0`, `E8_EW_MODE=off` when they get noisy.
- **Telemetry:** aiohttp app at the tail of `main()` exposes `/api/state`, `/api/telemetry`, `/metrics/*`, feeding the static dashboard.

_See `docs/architecture.md` for a structured overview._

## 2. Immediate Cleanup Goals
Status: Completed
1. **Normalize env knobs** – documented in `docs/env.md` (covers `E8_PROVIDER`, `E8_USE_LOCAL_MIX`, cadence knobs, `E8_QUIET`).
2. **Quieten console** – implemented via `E8_QUIET` (panels/logging gated; defaulted to quiet in smoke runs).
3. **Seeded smoke tests** – `scripts/smoke_memory.py` seeds 5 concepts and asserts KD‑tree/population; current result: SMOKE PASS.

## 3. Collaboration Notes
- Source of truth right now: `docs/architecture.md` and this `AGENTS.md`.
- Default Python workflow uses `uv`: run `uv sync` to provision, `uv run python scripts/smoke_memory.py` for smoke tests, and `uv add <package>` when adding dependencies.
- Track open questions in a TODO block at the bottom so any contributor can pick them up.
- When adding new experiments, gate them behind env flags and document defaults here.

- Backlog via prompts (CLI-first, untracked):
  - Use `prompts/backlog/` as the local backlog; do not commit it to git.
  - Buckets: `now/`, `next/`, `later/`, `done/YYYY/mm/` (UTC). Example: `prompts/backlog/done/2025/09/...`.
  - Only execute prompts from `prompts/backlog/now/`.
  - On accept, move the prompt to `prompts/backlog/done/YYYY/mm/` and record a snapshot + hash in the session log.
  - Listing is via `ls`; visibility comes from committed session logs under `docs/sessions/`.

> Protocol Policy (STRICT MODE): ALL edits must flow through the codex_orchestration protocol (see §5). This includes code, docs, configs, and scripts. Every change requires:
> - a prompt under `prompts/backlog/now/` (untracked),
> - a committed session log under `docs/sessions/` that embeds the exact prompt snapshot and `prompt_sha256`, and
> - a passing smoke test: `uv run python scripts/smoke_memory.py`.
>
> Acceptance always requires explicit human approval (“accept”). After acceptance, archive the prompt to `prompts/backlog/done/YYYY/mm/` (UTC). No exceptions without a documented MANUAL_OVERRIDE note in the session log.

### Strict Mode Enforcement Aids
- PRs MUST include a link to the session log and the `prompt_sha256`. Use the PR template at `.github/PULL_REQUEST_TEMPLATE.md`.
- Optional local guard (no auto-install): see `scripts/protocol_guard.md` for a pre-push hook that warns if a commit modifies source without a corresponding session log change.
## 4. TODO / Open Questions
- [ ] Extract a clean schema for memory nodes (fields, types) to freeze before porting.
- [x] Draft `quiet` mode env variable and implement in Python so future comparisons are less noisy. (Implemented as `E8_QUIET`; console panels gated.)
- [x] Build a Python smoke test that seeds 5 concepts and verifies KD-tree size > 0. (`scripts/smoke_memory.py` passes.)

Proposed next steps
- [ ] Freeze and document the canonical memory node schema; codify with a Python `TypedDict`/`dataclass` and validation in `MemoryManager.add_entry`.
- [ ] Add a minimal CI job to run `uv run python scripts/smoke_memory.py` on PRs.
- [ ] Create `docs/sessions/` with a checked-in stub (and start committing session logs per the protocol template).
- [ ] Add a `.env.example` that mirrors `docs/env.md` quick starts (stub quiet, OpenAI, Ollama) if not already covered.

Add to this list as discoveries happen. The goal is to keep every agent aligned without rereading the 30k lines in `e8_mind_server_M24.py` each time.

## 5. Protocol (Compressed)
- Full YAML spec and examples live in `docs/protocol.md`.
- This repo uses a CLI-first, prompts-as-backlog workflow.

### Golden Rules
- Only execute prompts from `prompts/backlog/now/`.
- Session log must include `prompt_path`, `prompt_sha256`, and an embedded prompt snapshot.
- Smoke test passes before acceptance: `uv run python scripts/smoke_memory.py`.
- Acceptance requires explicit human approval (“accept”).
- Backlog is untracked under `prompts/backlog/`; archive accepted prompts to `prompts/backlog/done/YYYY/mm/` (UTC).
- Keep NOW small (≤5 items); prune weekly.

### Roles
- Human: intent via chat only; choose which NOW prompt to run; approve/decline acceptance; request priority moves.
- Agent: handle files/logs/moves; run/verify/enforce gates; compute `prompt_sha256`; embed prompt snapshot; archive on accept.

### Backlog Flow
- Buckets (local, untracked): `prompts/backlog/{now,next,later,done/YYYY/mm}`.
- List and pick work with `ls`. Visibility is via committed session logs in `docs/sessions/`.
- Prompt format: use `prompts/backlog/_template.md` for front matter (no bucket field; folder is the bucket).

### Runbook
- Run prompt: `cat <prompt> | codex exec -m gpt-5-codex -C . --full-auto`
- Smoke test: `uv run python scripts/smoke_memory.py`
- Hash prompt: `shasum -a 256 <prompt> | awk '{print $1}'`
- Archive on accept (UTC): `DEST="prompts/backlog/done/$(date -u +%Y/%m)"; mkdir -p "$DEST"; mv <prompt> "$DEST/$(date -u +%F)-<slug>.md"`

### Separation of Concerns
- You (human): chat-only intent, pick NOW item, approve acceptance, steer priorities.
- Me (agent): do all file ops, hashing, snapshots, runs, verification, and archival; enforce the gates above.

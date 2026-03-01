# Implementation Plan: Bronze Vault Foundation

**Branch**: `001-bronze-vault-foundation` | **Date**: 2026-02-28 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-bronze-vault-foundation/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Generate a dependency-aware, phase-based implementation plan for the **Personal AI Employee — Autonomous FTE (Bronze Tier)**. This plan establishes the foundation: an Obsidian-based knowledge vault, a skill-driven architecture (5 core skills), and a safe autonomous execution environment using Python watchers and PM2 on Windows 10.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: `pm2` (with `pm2-startup-windows`), `python-dotenv`, `watchdog`, `gemini-cli`  
**Storage**: Obsidian Vault (Local Markdown), JSON (State/Logs)  
**Testing**: `pytest`  
**Target Platform**: Windows 10  
**Project Type**: Single project (Python runtime)  
**Performance Goals**: Watcher detection < 10s, Audit log entry < 5s  
**Constraints**: `DRY_RUN=true` default, local-only, Windows paths, no external APIs (Bronze)  
**Scale/Scope**: 1 Vault, 9 Folders, 3 Seed Files, 5 Skills, 4 Runtime Scripts, 1 Orchestrator

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Core Principles:**
- [x] **Local-First:** All sensitive data stays on the local machine.
- [x] **Human-in-the-loop (HITL):** Sensitive/irreversible actions require approval via file-move.
- [x] **Skill-driven intelligence:** AI functionality is encapsulated in `SKILL.md` files.
- [x] **Autonomy with safety:** The agent acts proactively but defaults to `DRY_RUN`.
- [x] **Transparency:** All agent actions are logged and auditable.
- [x] **Privacy by design:** Credentials are not stored in plain text or committed.

**Key Standards:**
- [x] Every AI capability is defined in a `SKILL.md` before implementation.
- [x] `SKILL.md` includes purpose, I/O, steps, success criteria, and error handling.
- [x] Watcher scripts follow the `BaseWatcher` pattern.
- [x] Action scripts support a `DRY_RUN` mode (default: true).
- [x] Credentials are in `.env` and added to `.gitignore`.
- [x] Audit logs are written to `/Vault/Logs/YYYY-MM-DD.json`.
- [x] Human approval is required for specified sensitive actions.
- [x] Rate limits are enforced.

**Constraints:**
- [x] OS is Windows 10; Windows-compatible paths are used.
- [x] No hardcoded secrets.
- [x] No auto-approval for payments.
- [x] No autonomous action on emotional, legal, or medical contexts.
- [x] Watcher scripts are managed by PM2.
- [x] `DEV_MODE` is true by default.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

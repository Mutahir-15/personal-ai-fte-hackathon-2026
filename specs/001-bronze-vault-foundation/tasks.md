# Tasks: Bronze Vault Foundation

**Input**: Design documents from `/specs/001-bronze-vault-foundation/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure (`src/`, `tests/`, `config/`) per implementation plan
- [x] T002 Create `.env` from `.env.example` with `DRY_RUN=true` and `VAULT_ROOT` in root directory
- [x] T003 Update `.gitignore` to include `.env`, `__pycache__`, and `.pm2` logs in root directory
- [x] T004 Initialize Python project with `pip install python-dotenv watchdog filelock` in root directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Implement `Config` class to load environment variables in `src/config/settings.py`
- [x] T006 Implement `FileLockManager` using `filelock` for safe vault access in `src/lib/locking.py`
- [x] T007 [P] Create `BaseWatcher` abstract class for standard watcher patterns in `src/lib/base_watcher.py`
- [x] T008 [P] Create `BaseAction` abstract class for skill-based actions in `src/lib/base_action.py`
- [x] T009 Implement `SkillLoader` to validate and load `SKILL.md` metadata in `src/lib/skill_loader.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 & 2 - Vault Initialization & Skills (Priority: P1) 🎯 MVP

**Goal**: Initialize the Obsidian vault structure and define core AI skills.

**Independent Test**: Verify existence of 9 folders and 3 seed files in `VAULT_ROOT`. Verify 5 `SKILL.md` files in `.specify/skills/`.

### Implementation for US1 & US2

- [x] T010 [P] [US2] Create `SKILL.md` for `vault-setup` in `.specify/skills/vault-setup/SKILL.md`
- [x] T011 [P] [US2] Create `SKILL.md` for `filesystem-watcher` in `.specify/skills/filesystem-watcher/SKILL.md`
- [x] T012 [P] [US2] Create `SKILL.md` for `needs-action-processor` in `.specify/skills/needs-action-processor/SKILL.md`
- [x] T013 [P] [US2] Create `SKILL.md` for `hitl-approval` in `.specify/skills/hitl-approval/SKILL.md`
- [x] T014 [P] [US2] Create `SKILL.md` for `audit-logger` in `.specify/skills/audit-logger/SKILL.md`
- [x] T015 [US1] Implement `VaultInitializer` to create folders and seed files in `src/services/vault_initializer.py`
- [x] T016 [US1] Create CLI entry point for vault initialization in `src/cli/init_vault.py`
- [x] T017 [US1] Create seed markdown templates (`Dashboard.md`, `Company_Handbook.md`, `Business_Goals.md`) in `src/templates/`

**Phase Verification Gate (US1/US2)**:
- [x] Run `python -m src.cli.init_vault`
- [x] Confirm all 9 folders exist in `VAULT_ROOT`
- [x] Confirm seed files are populated and readable in Obsidian

---

## Phase 4: User Story 6 - Audit Logging (Priority: P3)

**Goal**: Implement comprehensive logging of all agent actions.

**Independent Test**: Trigger a dummy action and verify JSON entry in `VAULT_ROOT/Logs/YYYY-MM-DD.json`.

### Implementation for US6

- [x] T018 [P] [US6] Implement `AuditLogger` service for JSON logging in `src/services/audit_logger.py`
- [x] T019 [US6] Add file locking to `AuditLogger` to prevent concurrent write corruption in `src/services/audit_logger.py`
- [x] T020 [US6] Implement log rotation/retention check (90 days) in `src/services/audit_logger.py`

---

## Phase 5: User Story 3 - Filesystem Watcher (Priority: P2)

**Goal**: Detect file drops and create `.md` entries in `/Needs_Action`.

**Independent Test**: Drop a `.txt` file into a monitored folder; verify `.md` appears in `VAULT_ROOT/Needs_Action/`.

### Implementation for US3

- [x] T021 [US3] Implement `FilesystemWatcher` using `watchdog` in `src/services/filesystem_watcher.py`
- [x] T022 [US3] Implement `NeedsActionProcessor` to wrap detected files in markdown metadata in `src/services/action_processor.py`
- [x] T023 [US3] Integrate `AuditLogger` into `FilesystemWatcher` in `src/services/filesystem_watcher.py`
- [x] T024 [US3] Implement watcher state persistence in `VAULT_ROOT/.watcher_state/processed_files.json`

---

## Phase 6: User Story 5 - HITL Approval (Priority: P3)

**Goal**: Implement human-in-the-loop approval via file-move pattern.

**Independent Test**: Move file from `/Pending_Approval/` to `/Approved/`; verify system detects approval.

### Implementation for US5

- [x] T025 [US5] Implement `ApprovalWatcher` to monitor `/Approved/` folder in `src/services/approval_watcher.py`
- [x] T026 [US5] Implement `ApprovalQueue` manager for `VAULT_ROOT/.watcher_state/approved_actions.json` in `src/lib/approval_manager.py`
- [x] T027 [US5] Create utility to generate approval request markdown in `src/lib/approval_manager.py`

---

## Phase 7: User Story 4 - Orchestration & PM2 (Priority: P2)

**Goal**: System integration, safe execution (`DRY_RUN`), and persistence via PM2.

**Independent Test**: Run system via PM2; verify `DRY_RUN` prevents file moves in logs.

### Implementation for US4

- [x] T028 [US4] Implement `Orchestrator` to manage lifecycle of all watchers in `src/orchestrator.py`
- [x] T029 [US4] Implement `DRY_RUN` check in all action-performing methods across services
- [x] T030 [US4] Create `ecosystem.config.js` for PM2 process management in root directory
- [x] T031 [US4] Implement graceful shutdown and health reporting in `src/orchestrator.py`
- [x] T032 [US4] Configure PM2 Windows startup using `pm2-startup` in root directory

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation and validation.

- [x] T033 Generate comprehensive `README.md` with Windows setup and skill index in root directory
- [x] T034 [P] Implement unit tests for `FileLockManager` in `tests/unit/test_locking.py`
- [x] T035 [P] Implement integration test for Vault Setup in `tests/integration/test_vault_setup.py`
- [x] T036 Final validation of PHR logging in `history/prompts/` (manual check)

---

## Dependencies & Execution Order

### Phase Dependencies

1. **Setup (Phase 1)** -> **Foundational (Phase 2)**
2. **Foundational (Phase 2)** -> **US1/US2 (Phase 3)**
3. **Phase 3** -> **Audit Logging (Phase 4)** (Foundation for all subsequent logs)
4. **Phase 4** -> **Watcher (Phase 5)** & **HITL (Phase 6)**
5. **Phase 5 & 6** -> **Orchestrator (Phase 7)**

### Parallel Opportunities

- **T010-T014**: All `SKILL.md` definitions can be written in parallel.
- **T018, T021, T025**: Core service logic can be drafted in parallel once Phase 2 is complete.
- **Phase 8**: Tests and documentation can run in parallel with final polish.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)
1. Complete Setup and Foundation.
2. Implement Vault Initialization and Skill Definitions.
3. **STOP**: Verify Obsidian vault is ready for human/agent use.

### Incremental Delivery
1. Add Audit Logging (essential for debugging the next steps).
2. Add Filesystem Watcher (enable "Input" capability).
3. Add HITL & Orchestration (enable "Safe Autonomy").

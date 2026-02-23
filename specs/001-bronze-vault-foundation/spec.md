# Feature Specification: Bronze Vault Foundation

**Feature Branch**: `001-bronze-vault-foundation`  
**Created**: 2026-02-23  
**Status**: Draft  
**Input**: User description: "Personal AI Employee — Autonomous FTE (Bronze Tier) Feature: bronze-vault-foundation Platform: Windows 10, local-first, agent-driven, human-in-the-loop Reasoning Agent: Gemini CLI Spec & Planning Tool: Spec-kit plus Knowledge Base: Obsidian (AI_Employee_Vault) Target audience: Developer building their first autonomous AI agent for personal and business automation, intermediate technical proficiency, comfortable with CLI and file systems. Focus: - Bronze tier completion as a fully functional foundation - Skill-driven architecture (every AI capability as a SKILL.md) - Vault-first design (Obsidian as the single source of truth) - Safe autonomy (DRY_RUN default, HITL for all sensitive actions) - Prompt History Record (PHR) maintained at history/prompts.md for every action Success Criteria: - Obsidian vault (AI_Employee_Vault) created with correct folder structure - All 9 required folders exist and are verified - All 3 seed markdown files created with fully populated templates (Dashboard.md, Company_Handbook.md, Business_Goals.md) - At least 5 SKILL.md files written and saved to .specify/skills/<skill>/SKILL.md before any implementation code is generated: 1. vault-setup 2. filesystem-watcher 3. needs-action-processor 4. hitl-approval 5. audit-logger - Filesystem watcher detects a dropped file and creates a .md in /Needs_Action - Gemini CLI successfully reads from and writes to the vault - DRY_RUN mode verified working (default: true) before any live integration - All watcher scripts running persistently via PM2 on Windows 10 - Every agent action logged to /Vault/Logs/YYYY-MM-DD.json - PHR maintained at history/prompts.md with an entry for every prompt issued - Zero credentials committed to Git - Zero hardcoded secrets anywhere in the codebase Constraints: - OS: Windows 10 only (Task Scheduler not cron, Windows-compatible paths) - Vault root: C:\Users\<name>\AI_Employee_Vault (user-configurable) - Reasoning engine: Gemini CLI only (no Claude Code, no OpenAI) - All AI functionality must be a SKILL.md before implementation begins - DRY_RUN must default to true in all action scripts - .env file mandatory, added to .gitignore before first commit - PM2 required for process persistence (not manual terminal runs) - No external APIs in Bronze tier except Gmail (optional, if time permits) - Audit logs retained minimum 90 days - PHR entries must be appended only, never overwritten or deleted Deliverables (in order of implementation): 1. constitution.md — Project governance and principles (already complete) 2. SKILL.md files — One per capability, saved to .specify/skills/<name>/SKILL.md 3. Vault structure — All folders and seed files created via vault-setup skill 4. Base watcher — filesystem_watcher.py following BaseWatcher pattern 5. Orchestrator — orchestrator.py (master process, folder watching, scheduling) 6. PM2 configuration — ecosystem.config.js for Windows 10 persistence 7. Audit logger — writes JSON logs to /Vault/Logs/YYYY-MM-DD.json 8. HITL workflow — file-move approval pattern (Pending_Approval → Approved) 9. README.md — Setup instructions, architecture overview, skill index 10. history/prompts.md — PHR maintained throughout entire build Architecture Decisions (already locked in constitution): - Vault-first: Obsidian is single source of truth, not a database - File-move pattern: Agent communicates via folder structure, not APIs - Skill-first: No code written without a corresponding SKILL.md - PHR-always: Every prompt logged to history/prompts.md without exception - HITL-always: No irreversible action without human file-move approval - DRY_RUN-default: All scripts safe by default, production requires explicit opt-in Not Building (Bronze Tier): - Gmail watcher (Silver tier) - WhatsApp watcher (Silver tier) - LinkedIn/social media posting (Silver tier) - Email MCP server (Silver tier) - Odoo accounting integration (Gold tier) - CEO briefing automation (Gold tier) - Ralph Wiggum / Gemini loop equivalent (Gold tier) - Cloud VM deployment (Platinum tier) - Any payment or banking integration (Gold tier and above) - Multi-agent coordination (Platinum tier) Security Non-Negotiables: - .env file created before any credential is used - .gitignore configured before first git commit - DRY_RUN=true enforced in all scripts by default - No auto-approval for any action during Bronze tier - Audit log written for every agent action, successful or failed PHR Format (mandatory for every prompt): --- ## [YYYY-MM-DD HH:MM] — <skill or task name> **Prompt Summary:** <one line description> **Skill:** <skill name or N/A> **File Written:** <path or N/A> **Triggered By:** Human **Status:** Completed / Failed **Notes:** <brief note> --- Timeline: Bronze tier complete before progressing to Silver Next Tier Trigger: All Bronze success criteria checked and verified"

## User Scenarios & Testing

### User Story 1 - Initial Vault Setup (Priority: P1)

As a developer, I want to initialize a new Obsidian vault with the correct folder structure and seed files, so that I have a ready-to-use knowledge base for the AI employee.

**Why this priority**: This is the foundational step for the entire system, as the vault is the single source of truth. Without it, no other component can function.

**Independent Test**: The vault structure can be fully tested by verifying the existence of all required folders and the content of the three seed markdown files.

**Acceptance Scenarios**:

1.  **Given** a specified vault root directory, **When** the vault setup skill is executed, **Then** an Obsidian vault named `AI_Employee_Vault` is created.
2.  **Given** an `AI_Employee_Vault` exists, **When** the vault setup skill is executed, **Then** all 9 required subfolders are created within the vault.
3.  **Given** the required vault folders exist, **When** the vault setup skill is executed, **Then** `Dashboard.md`, `Company_Handbook.md`, and `Business_Goals.md` are created with fully populated templates.

---

### User Story 2 - Skill Definition and Integration (Priority: P1)

As a developer, I want to define core AI capabilities as `SKILL.md` files, so that I can systematically implement and integrate AI functionalities.

**Why this priority**: This establishes the skill-driven architecture, which is a core principle for the project, enabling modular development.

**Independent Test**: The existence and proper formatting of `SKILL.md` files can be verified in the `.specify/skills/<skill>/` directory.

**Acceptance Scenarios**:

1.  **Given** the project setup, **When** new AI capabilities are identified, **Then** at least 5 `SKILL.md` files (`vault-setup`, `filesystem-watcher`, `needs-action-processor`, `hitl-approval`, `audit-logger`) are created and saved to `.specify/skills/<skill>/SKILL.md`.

---

### User Story 3 - Filesystem Watching and Action Triggering (Priority: P2)

As a developer, I want the system to detect new files in specific locations and trigger actions, so that the AI employee can respond to external inputs.

**Why this priority**: This is crucial for the "local-first, agent-driven" aspect, enabling the AI to react to changes in its environment.

**Independent Test**: A test file can be dropped into a watched directory, and the creation of a corresponding `.md` file in `/Needs_Action` can be observed.

**Acceptance Scenarios**:

1.  **Given** a filesystem watcher is active and monitoring a designated input directory, **When** a new file is dropped into the input directory, **Then** the filesystem watcher detects the new file.
2.  **Given** a new file is detected by the watcher, **When** the system processes the file, **Then** a new markdown file is created in the `/Needs_Action` folder within the `AI_Employee_Vault`.

---

### User Story 4 - Safe Autonomous Execution (Priority: P2)

As a developer, I want all AI actions to default to a safe `DRY_RUN` mode, so that I can prevent unintended modifications and ensure human oversight before live execution.

**Why this priority**: This directly addresses the "Safe autonomy (DRY_RUN default, HITL for all sensitive actions)" mandate, preventing errors and building trust.

**Independent Test**: Any action script can be run in `DRY_RUN` mode, and its output can be verified to confirm no actual system changes occurred.

**Acceptance Scenarios**:

1.  **Given** any agent action script is executed, **When** the `DRY_RUN` flag is set to `true` (default), **Then** the script simulates its actions without making any permanent changes to the system.
2.  **Given** an agent action script completes in `DRY_RUN` mode, **When** observing system state, **Then** no side effects are visible (e.g., no files created, modified, or deleted).

---

### User Story 5 - Human-in-the-Loop Approval (Priority: P3)

As a developer, I want critical actions to require human approval via a file-move pattern, so that sensitive operations have explicit consent.

**Why this priority**: This is a key safety mechanism ensuring "human-in-the-loop for all sensitive actions."

**Independent Test**: A simulated sensitive action can generate a file in `Pending_Approval`, and moving it to `Approved` can trigger the actual action.

**Acceptance Scenarios**:

1.  **Given** a sensitive agent action is proposed, **When** the system requires human approval, **Then** a request for approval is represented as a file in a `Pending_Approval` directory.
2.  **Given** a file is present in `Pending_Approval`, **When** a human moves the file to an `Approved` directory, **Then** the system recognizes the approval and proceeds with the sensitive action.

---

### User Story 6 - Audit Logging (Priority: P3)

As a developer, I want every agent action to be comprehensively logged, so that I can track system behavior, debug issues, and maintain an audit trail.

**Why this priority**: Essential for observability, debugging, and meeting the security non-negotiable of auditing all actions.

**Independent Test**: Perform an agent action, then verify the existence and content of the corresponding log entry in the audit log file.

**Acceptance Scenarios**:

1.  **Given** any agent action is performed (successful or failed), **When** the action completes, **Then** a JSON log entry is written to `/Vault/Logs/YYYY-MM-DD.json` containing details of the action.
2.  **Given** audit logs are generated, **When** reviewing the logs, **Then** log entries are retained for a minimum of 90 days.

---

### Edge Cases

- What happens when a watched directory is deleted or becomes inaccessible?
- How does the system handle concurrent file drops in a watched directory?
- What if a `SKILL.md` file is malformed or invalid?
- How does the system recover from an interrupted `DRY_RUN` process?

## Requirements

### Functional Requirements

-   **FR-001**: The system MUST create an Obsidian vault named `AI_Employee_Vault` at a user-configurable root path (e.g., `C:\Users\<name>\AI_Employee_Vault`).
-   **FR-002**: The system MUST ensure the `AI_Employee_Vault` contains 9 specific subfolders upon initialization.
-   **FR-003**: The system MUST create and fully populate `Dashboard.md`, `Company_Handbook.md`, and `Business_Goals.md` within the `AI_Employee_Vault`.
-   **FR-004**: The system MUST provide a mechanism for defining AI capabilities as `SKILL.md` files located in `.specify/skills/<skill>/SKILL.md`.
-   **FR-005**: The system MUST implement a filesystem watcher capable of detecting new files dropped into a configured directory.
-   **FR-006**: Upon detection of a new file, the system MUST create a corresponding markdown file in the `/Needs_Action` folder of the `AI_Employee_Vault`.
-   **FR-007**: The Gemini CLI MUST be able to successfully read from and write to the `AI_Employee_Vault`.
-   **FR-008**: All agent action scripts MUST default to a `DRY_RUN=true` mode, preventing actual execution.
-   **FR-009**: The system MUST manage persistent execution of all watcher scripts using PM2 on Windows 10.
-   **FR-010**: The system MUST log every agent action (successful or failed) as a JSON entry to `/Vault/Logs/YYYY-MM-DD.json`.
-   **FR-011**: The system MUST maintain a Prompt History Record (PHR) at `history/prompts.md` for every prompt issued, appending new entries.
-   **FR-012**: The system MUST implement a Human-in-the-Loop (HITL) approval mechanism where sensitive actions are approved by moving a file from a `Pending_Approval` directory to an `Approved` directory.

### Key Entities

-   **AI_Employee_Vault**: The central Obsidian knowledge base for the AI employee, containing structured information and acting as the primary interface.
-   **SKILL.md**: Markdown files defining individual AI capabilities, including their purpose, inputs, outputs, and usage instructions.
-   **PHR (Prompt History Record)**: A log of all interactions and prompts issued to the Gemini CLI, maintained for auditing and historical context.
-   **Audit Log**: A chronological record of all agent actions, their outcomes, and relevant metadata, stored in JSON format within the vault.
-   **Watcher Scripts**: Automated processes that monitor specified filesystem locations for changes, triggering downstream AI actions.

## Success Criteria

### Measurable Outcomes

-   **SC-001**: The `AI_Employee_Vault` is successfully initialized with all required folders and seed files within 1 minute of executing the vault setup skill.
-   **SC-002**: All 5 initial `SKILL.md` files are present and correctly formatted in their designated locations prior to any implementation code generation.
-   **SC-003**: A new file dropped into a watched directory results in a corresponding markdown file appearing in `/Needs_Action` within 10 seconds.
-   **SC-004**: The Gemini CLI can read from and write to any location within the `AI_Employee_Vault` without errors.
-   **SC-005**: All agent action scripts, when executed with `DRY_RUN=true`, complete without making any persistent changes to the system.
-   **SC-006**: All watcher scripts run persistently on Windows 10, maintaining 99.9% uptime over a 24-hour period (excluding system reboots).
-   **SC-007**: Every agent action generates a valid JSON audit log entry within 5 seconds of completion.
-   **SC-008**: The `history/prompts.md` file is consistently updated with a new PHR entry for every user prompt, with zero entries overwritten or deleted.
-   **SC-009**: No credentials or hardcoded secrets are committed to the Git repository or found anywhere in the codebase.

---
## Assumptions

-   The user has a Windows 10 operating system.
-   Obsidian is installed and accessible for vault creation and management, though the system will primarily interact with it via file system operations.
-   PM2 is available and properly configured on the Windows 10 system for process persistence.
-   The user is comfortable with CLI and file system operations.
-   The `AI_Employee_Vault` root path can be configured by the user.

## Constraints

-   **Operating System**: Windows 10 only.
-   **Vault Root**: Configurable, but defaults to `C:\Users\<name>\AI_Employee_Vault`.
-   **Reasoning Engine**: Gemini CLI only (no Claude Code, no OpenAI).
-   **AI Functionality**: All AI capabilities MUST be defined as `SKILL.md` files before implementation begins.
-   **Safety**: `DRY_RUN` MUST default to `true` in all action scripts. No auto-approval for any action.
-   **Environment Configuration**: `.env` file mandatory, added to `.gitignore` before first commit.
-   **Process Persistence**: PM2 required for process persistence (not manual terminal runs).
-   **External APIs**: No external APIs in Bronze tier except Gmail (optional, if time permits).
-   **Audit Logs**: Retained minimum 90 days.
-   **PHR**: Entries must be appended only, never overwritten or deleted.
-   **Security**: Zero credentials committed to Git. Zero hardcoded secrets anywhere in the codebase.

## Non-Goals (Bronze Tier)

-   Gmail watcher
-   WhatsApp watcher
-   LinkedIn/social media posting
-   Email MCP server
-   Odoo accounting integration
-   CEO briefing automation
-   Ralph Wiggum / Gemini loop equivalent
-   Cloud VM deployment
-   Any payment or banking integration
-   Multi-agent coordination

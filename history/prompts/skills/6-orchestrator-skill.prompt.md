
---
## [2026-02-26 17:09] — orchestrator SKILL.md
**Skill:** orchestrator
**File Written:** .specify/skills/orchestrator/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
```
You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **orchestrator**

Save the file at this exact path: .specify/skills/orchestrator/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — orchestrator SKILL.md
**Skill:** orchestrator
**File Written:** .specify/skills/orchestrator/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
<Paste the entire prompt that was given to you here, verbatim,
inside a markdown code block>

**Notes:** <brief note on what was created>
---

## Context & Constraints
- OS: Windows 10 (use Windows-compatible paths, backslashes where needed)
- Vault name: AI_Employee_Vault
- Vault root: Configurable via .env as VAULT_PATH
- Reasoning agent: Gemini CLI
- Process manager: PM2 (script must be PM2-compatible)
- Must support DRY_RUN mode (default: true)
- Must be idempotent and crash-safe
- This is the MASTER PROCESS — it coordinates all other skills
- All other skills are called by or report to the Orchestrator

## What This Skill Does
This skill implements the master Orchestrator process for the Personal AI
Employee. It is the central nervous system that ties all Bronze tier skills
together. It:
1. Starts up and initializes all required components
2. Generates a unique session_id for the current run
3. Loads configuration from .env file
4. Verifies vault structure is intact (calls vault-setup skill if not)
5. Starts and monitors all watcher processes via PM2
6. Watches /Needs_Action/ for new files and triggers needs-action-processor
7. Watches /Approved/ for approved files and triggers action execution
8. Watches /Rejected/ for rejected files and triggers archival
9. Monitors /Pending_Approval/ for expired requests
10. Runs scheduled tasks (e.g., Dashboard.md refresh every 5 minutes)
11. Calls audit-logger for every system event
12. Handles graceful shutdown on SIGTERM/SIGINT
13. Writes health status to /Vault/.watcher_state/orchestrator_health.json
14. Restarts failed components automatically

## Orchestrator Startup Sequence
The Orchestrator must follow this exact startup sequence:

STEP 1 — Environment Check:
- Load .env file
- Verify all required environment variables are present:
  VAULT_PATH, DROP_FOLDER_PATH, DRY_RUN,
  WATCHER_INTERVAL_SECONDS, LOG_RETENTION_DAYS
- If any variable missing: log CRITICAL error and exit with code 1

STEP 2 — Vault Integrity Check:
- Verify all 9 required folders exist in vault
- Verify Dashboard.md, Company_Handbook.md, Business_Goals.md exist
- If any missing: invoke vault-setup skill to repair
- Log result to audit-logger

STEP 3 — Session Initialization:
- Generate session_id: AI_EMP_<YYYYMMDD>_<6-char-random-alphanumeric>
- Write session_id to /Vault/.watcher_state/current_session.json
- Log session start to audit-logger

STEP 4 — Component Startup:
- Verify PM2 is running
- Start filesystem-watcher via PM2 if not already running
- Verify all watchers are healthy
- Log component status to audit-logger

STEP 5 — Main Loop Start:
- Begin watching all trigger folders
- Start scheduled task timer
- Log "Orchestrator ready" to audit-logger
- Update Dashboard.md status to "Active"

## Main Processing Loop
The Orchestrator main loop must handle these events:

EVENT 1 — New file in /Needs_Action/:
- Wait 2 seconds (allow file write to complete)
- Trigger needs-action-processor for new file
- Log event to audit-logger

EVENT 2 — New file in /Approved/:
- Read approval file
- Verify not expired
- Retrieve corresponding Plan.md
- Execute planned action (DRY_RUN aware)
- Move approval file to /Done/
- Log event to audit-logger

EVENT 3 — New file in /Rejected/:
- Read rejection file
- Update corresponding Plan.md status to "rejected"
- Move to /Done/rejected/
- Log event to audit-logger

EVENT 4 — Scheduled task (every 5 minutes):
- Refresh Dashboard.md with latest stats
- Check /Pending_Approval/ for expired requests
- Write health status to orchestrator_health.json
- Log event to audit-logger

EVENT 5 — Component failure detected:
- Log WARNING to audit-logger
- Attempt restart via PM2
- If restart fails after 3 attempts: log CRITICAL
- Notify human via Dashboard.md alert section

## Health Status File
Write to /Vault/.watcher_state/orchestrator_health.json:

{
  "session_id": "<current session_id>",
  "status": "healthy | degraded | critical",
  "last_updated": "<ISO 8601 timestamp>",
  "uptime_seconds": <count>,
  "components": {
    "filesystem_watcher": "running | stopped | error",
    "needs_action_processor": "idle | processing | error",
    "hitl_approval": "watching | error",
    "audit_logger": "healthy | error"
  },
  "stats": {
    "files_processed_today": <count>,
    "approvals_pending": <count>,
    "approvals_completed_today": <count>,
    "errors_today": <count>
  }
}

## Dashboard.md Refresh Pattern
Every 5 minutes update Dashboard.md with this structure:

---
last_updated: <ISO 8601 timestamp>
session_id: <current session_id>
status: Active | Degraded | Offline
---

# AI Employee Dashboard

## System Status
- **Orchestrator:** Active | Degraded | Offline
- **Filesystem Watcher:** Running | Stopped
- **Session ID:** <session_id>
- **Uptime:** <HH:MM:SS>

## Pending Actions
- **Needs Action:** <count> items
- **Pending Approval:** <count> items
- **Plans In Progress:** <count> items

## Today's Stats
- **Files Processed:** <count>
- **Approvals Completed:** <count>
- **Errors:** <count>

## Recent Activity
| Time | Action | Actor | Result |
|------|--------|-------|--------|
<last 10 entries from audit logger>

## Alerts
<Any CRITICAL or WARNING events that need human attention>

## Graceful Shutdown
On SIGTERM or SIGINT the Orchestrator must:
1. Stop accepting new events
2. Complete any in-progress processing
3. Write final health status to orchestrator_health.json
4. Update Dashboard.md status to "Offline"
5. Log shutdown event to audit-logger
6. Exit with code 0

## Required Environment Variables
All must be present in .env:

VAULT_PATH=C:\Users\<name>\AI_Employee_Vault
DROP_FOLDER_PATH=C:\Users\<name>\Desktop\AI_Drop
DRY_RUN=true
WATCHER_INTERVAL_SECONDS=30
LOG_RETENTION_DAYS=90
GEMINI_API_KEY=<your_gemini_api_key>
SESSION_PREFIX=AI_EMP

## PM2 Ecosystem Configuration
The Orchestrator must include a complete ecosystem.config.js:

module.exports = {
  apps: [
    {
      name: 'orchestrator',
      script: 'orchestrator.py',
      interpreter: 'python3',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        DRY_RUN: 'true',
        VAULT_PATH: 'C:\Users\<name>\AI_Employee_Vault',
        DROP_FOLDER_PATH: 'C:\Users\<name>\Desktop\AI_Drop',
        WATCHER_INTERVAL_SECONDS: '30',
        LOG_RETENTION_DAYS: '90'
      }
    },
    {
      name: 'filesystem-watcher',
      script: 'filesystem_watcher.py',
      interpreter: 'python3',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        DRY_RUN: 'true',
        VAULT_PATH: 'C:\Users\<name>\AI_Employee_Vault',
        DROP_FOLDER_PATH: 'C:\Users\<name>\Desktop\AI_Drop',
        WATCHER_INTERVAL_SECONDS: '30'
      }
    }
  ]
}

## DRY_RUN Behavior
- DRY_RUN=true (default):
  Log all detected events
  Do not trigger any skill execution
  Do not move any files
  Do not update Dashboard.md
  Do not write health status
  Print all intended actions to console
- DRY_RUN=false:
  Execute all events fully
  Trigger skill execution
  Move files
  Update Dashboard.md
  Write health status

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what problem this skill solves and why it is the
   master process
3. **Inputs** — .env variables, vault structure, PM2
4. **Outputs** — running system, Dashboard.md, health status file
5. **Pre-conditions** — vault exists, PM2 installed, all skills written
6. **Startup Sequence** — exact 5-step startup with verification
7. **Main Processing Loop** — all 5 event types with handling logic
8. **Health Status File Structure** — complete JSON schema
9. **Dashboard.md Refresh Pattern** — complete template
10. **Graceful Shutdown Sequence** — exact shutdown steps
11. **Full Python Implementation** — complete, ready-to-run
    orchestrator.py embedded directly in the skill
12. **Complete ecosystem.config.js** — all components configured
    for Windows 10
13. **Required .env Template** — all variables with descriptions
14. **DRY_RUN Verification Steps** — how to confirm DRY_RUN is working
15. **Post-conditions / Verification** — how to confirm skill ran
    successfully
16. **Error Handling** — component failures, vault corruption, PM2
    unavailable, .env missing, graceful degradation
17. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI without
  human clarification
- Full Python implementation must be included, not pseudocode
- Must coordinate all Bronze tier skills correctly
- Startup sequence must be strictly ordered — no skipping steps
- Graceful shutdown must always complete — no abrupt exits
- Health status must update every 5 minutes without fail
- DRY_RUN must default to true — never false
- Must handle Windows 10 signal handling (no SIGTERM on Windows —
  use atexit and KeyboardInterrupt instead)
- ecosystem.config.js must be complete and Windows 10 compatible
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills,
  never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/orchestrator/SKILL.md
2. Append the PHR entry to: history/prompts/skills

Return a brief confirmation of both file paths written. No other output.
```

**Notes:** Created the complete SKILL.md for the master Orchestrator skill. This includes the main event loop logic, component management via PM2, health status reporting, and a graceful shutdown sequence.
---

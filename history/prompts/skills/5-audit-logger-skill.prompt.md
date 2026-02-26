
---
## [2026-02-26 17:01] — audit-logger SKILL.md
**Skill:** audit-logger
**File Written:** .specify/skills/audit-logger/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
```
You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **audit-logger**

Save the file at this exact path: .specify/skills/audit-logger/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — <skill-name> SKILL.md
**Skill:** <skill-name>
**File Written:** .specify/skills/<skill-name>/SKILL.md
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
- Logs must be retained for minimum 90 days
- This skill is called by ALL other skills — it is a shared utility

## What This Skill Does
This skill is the centralized audit logging utility for the entire Personal
AI Employee system. Every action taken by any skill or agent must pass
through this logger. It:
1. Accepts a structured log entry from any calling skill
2. Validates the log entry against the required schema
3. Appends the entry to the correct daily log file:
   /Vault/Logs/YYYY-MM-DD.json
4. Creates a new daily log file automatically at midnight
5. Maintains a log index at /Vault/Logs/index.json
6. Enforces 90-day log retention (auto-deletes logs older than 90 days)
7. Supports log level filtering: INFO, WARNING, ERROR, CRITICAL
8. Never overwrites existing log entries — append only
9. Handles concurrent writes safely (file locking)
10. Updates Dashboard.md with latest activity summary

## Required Log Entry Schema
Every log entry must follow this exact JSON structure:

{
  "timestamp": "<ISO 8601 timestamp>",
  "log_level": "INFO | WARNING | ERROR | CRITICAL",
  "action_type": "<file_drop | plan_created | approval_requested |
                   approved | rejected | expired | email_sent |
                   file_moved | error | system_event>",
  "actor": "<skill_name that triggered this log>",
  "target": "<file, folder, email, or system component affected>",
  "parameters": {
    "<key>": "<value>"
  },
  "approval_status": "not_required | pending | approved | rejected | expired",
  "approved_by": "human | system | N/A",
  "dry_run": true | false,
  "result": "success | failure | skipped",
  "error_message": "<null or error description>",
  "session_id": "<unique session identifier>"
}

## Daily Log File Structure
Each daily log file at /Vault/Logs/YYYY-MM-DD.json must follow this structure:

{
  "date": "YYYY-MM-DD",
  "total_entries": <count>,
  "summary": {
    "INFO": <count>,
    "WARNING": <count>,
    "ERROR": <count>,
    "CRITICAL": <count>
  },
  "entries": [
    <log entry 1>,
    <log entry 2>,
    ...
  ]
}

## Log Index File
Maintain /Vault/Logs/index.json with this structure:

{
  "last_updated": "<ISO 8601 timestamp>",
  "total_log_files": <count>,
  "oldest_log": "YYYY-MM-DD",
  "newest_log": "YYYY-MM-DD",
  "total_entries_all_time": <count>,
  "log_files": [
    {
      "date": "YYYY-MM-DD",
      "file": "YYYY-MM-DD.json",
      "entry_count": <count>,
      "size_bytes": <size>
    }
  ]
}

## Dashboard.md Update
After every log write, update the Recent Activity section of Dashboard.md:

## Recent Activity
| Time | Action | Actor | Result |
|------|--------|-------|--------|
| <HH:MM> | <action_type> | <actor> | <result> |
(Keep last 10 entries only)

## Retention Policy
- Retain logs for exactly 90 days
- On every logger invocation check for logs older than 90 days
- Delete expired log files and update index.json
- Log the deletion event itself before deleting
- Never delete logs that contain CRITICAL entries without
  writing a summary to /Vault/Logs/critical_archive.json first

## File Locking Strategy
- Use Python's fcntl (Linux) or msvcrt (Windows 10) for file locking
- Acquire lock before write, release immediately after
- If lock cannot be acquired within 5 seconds, retry 3 times
- If all retries fail, write to /Vault/Logs/failed_writes.json instead
- Never silently drop a log entry

## Session ID Generation
- Generate a unique session_id at Orchestrator startup
- Pass session_id to all skills via .env or shared state file
- All log entries within one Orchestrator run share the same session_id
- Format: AI_EMP_<YYYYMMDD>_<6-char-random-alphanumeric>

## DRY_RUN Behavior
- DRY_RUN=true (default):
  Validate log entry schema
  Print log entry to console
  Do NOT write to any file
  Do NOT update Dashboard.md
  Do NOT update index.json
  Do NOT enforce retention policy
- DRY_RUN=false:
  Execute all actions fully
  Write to daily log file
  Update index.json
  Update Dashboard.md
  Enforce 90-day retention

## Python Implementation Requirements
The implementation must include:
- AuditLogger class with these public methods:
  - log(entry: dict) -> bool
  - get_todays_log() -> dict
  - get_log_summary(date: str) -> dict
  - rotate_logs() -> int (returns count of deleted files)
- log() method must validate schema before writing
- All methods must be safe to call from any other skill
- Must be importable as a module: from audit_logger import AuditLogger
- Must also be runnable standalone for testing

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what problem this skill solves and why centralized
   logging is critical
3. **Inputs** — log entry dict schema with all required fields
4. **Outputs** — daily log file, index.json, Dashboard.md update
5. **Pre-conditions** — vault exists, /Logs/ folder exists
6. **Step-by-Step Execution Instructions** — detailed enough for
   Gemini CLI to follow without ambiguity
7. **Full Log Entry Schema** — complete JSON schema embedded in skill
8. **Daily Log File Structure** — complete structure with example
9. **Log Index Structure** — complete index.json format
10. **Retention Policy Logic** — exact 90-day deletion implementation
11. **File Locking Strategy** — Windows 10 compatible locking
12. **Full Python Implementation** — complete, ready-to-run
    audit_logger.py embedded directly in the skill
13. **Dashboard.md Update Pattern** — exact update logic
14. **DRY_RUN Verification Steps** — how to confirm DRY_RUN is working
15. **Post-conditions / Verification** — how to confirm skill ran
    successfully
16. **Error Handling** — file locking failures, corrupted log files,
    disk full, retention policy errors
17. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI without
  human clarification
- Full Python implementation must be included, not pseudocode
- Must be importable as a shared module by all other skills
- File locking must be Windows 10 compatible (msvcrt not fcntl)
- Schema validation must be strict — reject malformed entries
- Retention policy must be tested with edge cases: exactly 90 days,
  91 days, CRITICAL entries, empty log files
- DRY_RUN must default to true — never false
- Never silently drop a log entry under any circumstance
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills, never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/audit-logger/SKILL.md
2. Append the PHR entry to: history/prompts/skills

Return a brief confirmation of both file paths written. No other output.
```

**Notes:** Created the complete SKILL.md file for the centralized `audit-logger` utility, including a Python class with Windows-compatible file locking, log rotation, and dashboard update logic.
---

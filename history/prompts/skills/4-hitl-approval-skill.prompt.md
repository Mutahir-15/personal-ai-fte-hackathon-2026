
---
## [2026-02-26 16:50] — hitl-approval SKILL.md
**Prompt:**You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **hitl-approval**

Save the file at this exact path: .specify/skills/hitl-approval/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — hitl-approval SKILL.md
**Prompt Summary:** Write the hitl-approval SKILL.md for the
Personal AI Employee project
**Skill:** hitl-approval
**File Written:** .specify/skills/hitl-approval/SKILL.md
**Triggered By:** Human
**Status:** Completed
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
- No action is ever auto-approved during Bronze tier

## What This Skill Does
This skill implements the Human-in-the-Loop (HITL) approval workflow.
It is the safety layer of the entire Personal AI Employee system. It:
1. Watches /Pending_Approval/ for new approval request .md files
2. Presents the approval request details clearly in the vault
3. Waits for the human to move the file to either:
   - /Approved/ → to authorize the action
   - /Rejected/ → to deny the action
4. Once a file is detected in /Approved/:
   - Updates the corresponding Plan.md status to "approved"
   - Notifies the Orchestrator to execute the planned action
   - Logs the approval to /Vault/Logs/YYYY-MM-DD.json
5. Once a file is detected in /Rejected/:
   - Updates the corresponding Plan.md status to "rejected"
   - Archives the rejection reason
   - Logs the rejection to /Vault/Logs/YYYY-MM-DD.json
6. Handles expired approval requests (default expiry: 24 hours)

## Approval Request File Format
Files created in /Pending_Approval/ must follow this exact structure:

---
type: approval_request
action_type: <email_send | file_delete | payment | social_post | other>
plan_file: <path to corresponding Plan.md in /Plans/>
created: <ISO 8601 timestamp>
expires: <ISO 8601 timestamp — 24 hours after created>
status: pending
priority: high | medium | low
requested_by: gemini_cli
---

## Action Details
- Action: <clear one-line description of what will happen>
- Target: <who or what will be affected>
- Reason: <why this action is needed>
- Risk Level: <low | medium | high>

## To Approve
Move this file to: /Approved/

## To Reject
Move this file to: /Rejected/

## Expiry Warning
This request expires at: <expiry timestamp>
After expiry it will be automatically archived to /Done/

## Approved File Format
When human moves file to /Approved/, the skill must:
1. Verify file is a valid approval request
2. Check it has not expired
3. Update status field to "approved"
4. Add approved_at timestamp
5. Notify Orchestrator via state file

## Rejected File Format
When human moves file to /Rejected/, the skill must:
1. Update status field to "rejected"
2. Add rejected_at timestamp
3. Add rejection_reason field (default: "Human rejected without reason")
4. Archive to /Done/rejected/

## Expiry Handling
- Check all /Pending_Approval/ files every 5 minutes
- If current time > expires timestamp:
  - Update status to "expired"
  - Move file to /Done/expired/
  - Log expiry event to /Vault/Logs/YYYY-MM-DD.json
  - Update corresponding Plan.md status to "expired"

## Orchestrator Notification Pattern
After approval detected, notify Orchestrator by writing a state file:

/Vault/.watcher_state/approved_actions.json
{
  "timestamp": "<ISO 8601>",
  "approval_file": "<filename>",
  "plan_file": "<path to Plan.md>",
  "action_type": "<type>",
  "status": "ready_to_execute"
}

## DRY_RUN Behavior
- DRY_RUN=true (default):
  Log all detected file movements
  Do not update any file statuses
  Do not write to approved_actions.json
  Do not notify Orchestrator
- DRY_RUN=false:
  Execute all status updates
  Write approved_actions.json
  Notify Orchestrator

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what problem this skill solves and why HITL is critical
3. **Inputs** — what the agent needs before running this skill
4. **Outputs** — what this skill produces
5. **Pre-conditions** — what must be true before execution
6. **Step-by-Step Execution Instructions** — detailed enough for Gemini CLI
   to follow without ambiguity
7. **Approval Request Template** — complete template embedded in the skill
8. **File Movement Decision Tree** — exact logic for Approved/Rejected/Expired
9. **Full Python Implementation** — complete, ready-to-run hitl_approval.py
   embedded directly in the skill
10. **Orchestrator Notification Pattern** — exact state file format
11. **Expiry Handling Logic** — complete expiry check implementation
12. **DRY_RUN Verification Steps** — how to confirm DRY_RUN is working
13. **Post-conditions / Verification** — how to confirm skill ran successfully
14. **Error Handling** — missing files, expired requests, corrupted .md files,
    duplicate approvals
15. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI without
  human clarification
- Full Python implementation must be included, not pseudocode
- File movement detection must be polling-based (watchdog library)
- Expiry logic must be precise to the minute
- Must handle edge cases: file moved to wrong folder, file deleted instead
  of moved, duplicate approval files, corrupted frontmatter
- DRY_RUN must default to true — never false
- No action is ever auto-approved — human file move is always required
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills, never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/hitl-approval/SKILL.md
2. Append the PHR entry to: history/prompts/skills

Return a brief confirmation of both file paths written. No other output.
Personal AI Employee project
**Skill:** hitl-approval
**File Written:** .specify/skills/hitl-approval/SKILL.md
**Triggered By:** Human
**Status:** Completed
**Notes:** Created the complete SKILL.md file for the Human-in-the-Loop approval workflow, including a watchdog-based Python implementation.
---

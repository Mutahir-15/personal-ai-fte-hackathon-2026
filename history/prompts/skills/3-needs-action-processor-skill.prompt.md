
---
## [2026-02-26 16:39] — needs-action-processor SKILL.md
**Prompt:** You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **needs-action-processor**

Save the file at this exact path: .specify/skills/needs-action-processor/SKILL.md
Create the directories if they do not exist.

## Context & Constraints
- OS: Windows 10 (use Windows-compatible paths, backslashes where needed)
- Vault name: AI_Employee_Vault
- Vault root: Configurable via .env as VAULT_PATH
- Reasoning agent: Gemini CLI
- Process manager: PM2 (script must be PM2-compatible)
- Must support DRY_RUN mode (default: true)
- Must read Company_Handbook.md as the rules of engagement
- Must be idempotent and crash-safe

## What This Skill Does
This skill is the core reasoning loop of the Personal AI Employee. It:
1. Scans /Needs_Action/ for any unprocessed .md files
2. Reads each file to understand the context and required action
3. Reads Company_Handbook.md for rules of engagement
4. Uses Gemini CLI to reason about the required action
5. Creates a structured Plan.md file in /Plans/ for each item
6. Updates the status field in the original .md file to "processing"
7. Logs every action to /Vault/Logs/YYYY-MM-DD.json
8. If action requires human approval, creates an approval request
   in /Pending_Approval/ instead of acting directly
9. Moves processed .md files to /Done/ after Plan.md is created

## Plan.md File Format
For each item in /Needs_Action/, create a Plan.md with this exact structure:

---
created: <ISO 8601 timestamp>
source_file: <original filename from /Needs_Action/>
status: pending_approval | ready_to_execute | blocked
requires_approval: true | false
priority: high | medium | low
---

## Objective
<One clear sentence describing what needs to be done>

## Context
<Brief summary of the source file content>

## Steps
- [ ] Step 1: <first action>
- [ ] Step 2: <second action>
- [ ] Step 3: <third action>

## Rules Applied
<Which rules from Company_Handbook.md influenced this plan>

## Approval Required
<If requires_approval is true, explain what needs approval and why>
<If false, state "No approval required for this action">

## Risks
<Any potential risks or edge cases identified>

## Implementation Details
- Language: Python 3.13+
- Trigger: Called by Orchestrator.py when new files appear in /Needs_Action/
- Gemini CLI command: gemini -p "<prompt constructed from file content>"
- State tracking: Update status field in source .md file
- Duplicate prevention: Skip files with status != "pending"
- Logging: Append to /Vault/Logs/YYYY-MM-DD.json on every action

## Processing Logic
The skill must follow this exact decision tree:

1. Scan /Needs_Action/ for .md files where status = "pending"
2. For each pending file:
   a. Read file content
   b. Read Company_Handbook.md
   c. Construct Gemini CLI prompt combining both
   d. Run Gemini CLI and capture output
   e. Parse output into Plan.md structure
   f. Check if action requires approval (per Company_Handbook.md rules)
   g. If requires approval:
      - Create approval request in /Pending_Approval/
      - Set Plan.md status = "pending_approval"
   h. If no approval needed:
      - Set Plan.md status = "ready_to_execute"
   i. Update source file status = "processing"
   j. Write Plan.md to /Plans/
   k. Log action to /Vault/Logs/YYYY-MM-DD.json
3. After all files processed, output summary

## Approval Trigger Rules (from Company_Handbook.md)
These action types ALWAYS require approval:
- Any email to a new/unknown contact
- Any file deletion
- Any payment or financial action
- Any public post or social media action
- Any action marked priority: high

These action types NEVER require approval:
- Reading files
- Creating Plan.md files
- Writing to /Logs/
- Moving files within the vault

## DRY_RUN Behavior
- DRY_RUN=true (default): 
  Log intended actions only
  Do not write Plan.md files
  Do not update source file status
  Do not create approval requests
  Do not move files
- DRY_RUN=false:
  Execute all actions fully

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what problem this skill solves
3. **Inputs** — what the agent needs before running this skill
4. **Outputs** — what this skill produces
5. **Pre-conditions** — what must be true before execution
6. **Step-by-Step Execution Instructions** — detailed enough for Gemini CLI
   to follow without ambiguity
7. **Decision Tree** — full processing logic with approval routing
8. **Plan.md Template** — complete template embedded in the skill
9. **Full Python Implementation** — complete, ready-to-run
   needs_action_processor.py embedded directly in the skill
10. **Gemini CLI Integration** — exact command pattern for invoking Gemini
11. **DRY_RUN Verification Steps** — how to confirm DRY_RUN is working
12. **Post-conditions / Verification** — how to confirm skill ran successfully
13. **Error Handling** — empty folder, malformed files, Gemini CLI failure
14. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI without
  human clarification
- Full Python implementation must be included, not pseudocode
- Decision tree must be explicit — no ambiguous branching
- Gemini CLI command pattern must be exact and tested
- Must handle edge cases: empty /Needs_Action/, malformed .md files,
  Gemini CLI timeout, duplicate processing
- DRY_RUN must default to true — never false
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended, never overwritten

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts.md
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — needs-action-processor SKILL.md
**Prompt Summary:** Write the needs-action-processor SKILL.md for the
Personal AI Employee project
**Skill:** needs-action-processor
**File Written:** .specify/skills/needs-action-processor/SKILL.md
**Triggered By:** Human
**Status:** Completed
**Notes:** <brief note on what was created>
---

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/needs-action-processor/SKILL.md
2. Append the PHR entry to: history/prompts.md

Return a brief confirmation of both file paths written. No other output.
Personal AI Employee project
**Skill:** needs-action-processor
**File Written:** .specify/skills/needs-action-processor/SKILL.md
**Triggered By:** Human
**Status:** Completed
**Notes:** Created the complete SKILL.md file, including a full Python implementation for the core reasoning loop of the AI Employee.
---

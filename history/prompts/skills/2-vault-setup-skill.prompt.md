---
## 2026-02-24 10:00 — vault-setup SKILL.md
**Prompt:** You are an expert AI agent engineer. Your task is to write a professional, 
production-quality SKILL.md file for a "Personal AI Employee" project built 
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the 
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **vault-setup**

Save the file at this exact path: .specify/skills/vault-setup/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, you must also maintain the Prompt History Record.
Append an entry to: history/prompts.md

Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — vault-setup SKILL.md
**Prompt Summary:** Write the vault-setup SKILL.md for the Personal AI Employee project
**Skill:** vault-setup
**File Written:** .specify/skills/vault-setup/SKILL.md
**Triggered By:** Human
**Status:** Completed
**Notes:** <brief note on what was created>
---

## What This Skill Does
This skill sets up the complete Obsidian vault folder structure and seeds all 
required markdown files for the Personal AI Employee (Bronze Tier). It is the 
foundational skill — everything else depends on this vault existing correctly.

## Context & Constraints
- OS: Windows 10 (use Windows-compatible paths, backslashes where needed)
- Vault name: AI_Employee_Vault
- Vault location: User defines the root path (e.g., C:\Users\<name>\AI_Employee_Vault)
- Reasoning agent: Gemini CLI
- No external APIs or credentials required for this skill
- Must be idempotent (safe to run multiple times without breaking existing files)

## Required Vault Structure to Create
Folders:
- /Needs_Action/
- /Plans/
- /Done/
- /Pending_Approval/
- /Approved/
- /Rejected/
- /Logs/
- /Accounting/
- /Briefings/

Seed Markdown Files:
- Dashboard.md (with template: bank balance, pending messages, active projects sections)
- Company_Handbook.md (with template: rules of engagement for the AI agent)
- Business_Goals.md (with template: Q1 objectives, revenue targets, key metrics table)

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what problem this skill solves
3. **Inputs** — what the agent needs before running this skill
4. **Outputs** — what this skill produces
5. **Pre-conditions** — what must be true before execution
6. **Step-by-Step Execution Instructions** — detailed enough for Gemini CLI to follow 
   without ambiguity
7. **Seed File Templates** — full markdown templates for Dashboard.md, 
   Company_Handbook.md, and Business_Goals.md embedded directly in the skill
8. **Post-conditions / Verification** — how to confirm the skill ran successfully
9. **Error Handling** — what to do if a folder exists, file exists, or path is invalid
10. **Success Criteria** — clear, checkable definition of done

## Quality Standards
- Instructions must be unambiguous and executable by an AI agent without human 
  clarification
- Must be idempotent — running twice should not duplicate or corrupt files
- Seed file templates must be fully filled out, not placeholders like "[INSERT HERE]"
- Error handling must be explicit, not generic
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended, never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/vault-setup/SKILL.md
2. Append the PHR entry to: history/prompts.md

Return a brief confirmation of both file paths written. No other output.
**Skill:** vault-setup
**File Written:** .specify/skills/vault-setup/SKILL.md
**Triggered By:** Human
**Status:** Completed
**Notes:** Created the SKILL.md file for the vault-setup skill, including Python implementation and seed file templates.
---

---
id: 1
title: Create Bronze Vault Foundation Spec
stage: spec
date: 2026-02-23
surface: agent
model: gemini-1.5-flash-latest
feature: 001-bronze-vault-foundation
branch: 001-bronze-vault-foundation
user: Gemini CLI User
command: /sp.specify "Personal AI Employee — Autonomous FTE (Bronze Tier) Feature: bronze-vault-foundation Platform: Windows 10, local-first, agent-driven, human-in-the-loop Reasoning Agent: Gemini CLI Spec & Planning Tool: Spec-kit plus Knowledge Base: Obsidian (AI_Employee_Vault) Target audience: Developer building their first autonomous AI agent for personal and business automation, intermediate technical proficiency, comfortable with CLI and file systems. Focus: - Bronze tier completion as a fully functional foundation - Skill-driven architecture (every AI capability as a SKILL.md) - Vault-first design (Obsidian as the single source of truth) - Safe autonomy (DRY_RUN default, HITL for all sensitive actions) - Prompt History Record (PHR) maintained at history/prompts.md for every action Success Criteria: - Obsidian vault (AI_Employee_Vault) created with correct folder structure - All 9 required folders exist and are verified - All 3 seed markdown files created with fully populated templates (Dashboard.md, Company_Handbook.md, Business_Goals.md) - At least 5 SKILL.md files written and saved to .specify/skills/<skill>/SKILL.md before any implementation code is generated: 1. vault-setup 2. filesystem-watcher 3. needs-action-processor 4. hitl-approval 5. audit-logger - Filesystem watcher detects a dropped file and creates a .md in /Needs_Action - Gemini CLI successfully reads from and writes to the vault - DRY_RUN mode verified working (default: true) before any live integration - All watcher scripts running persistently via PM2 on Windows 10 - Every agent action logged to /Vault/Logs/YYYY-MM-DD.json - PHR maintained at history/prompts.md with an entry for every prompt issued - Zero credentials committed to Git - Zero hardcoded secrets anywhere in the codebase Constraints: - OS: Windows 10 only (Task Scheduler not cron, Windows-compatible paths) - Vault root: C:\Users\<name>\AI_Employee_Vault (user-configurable) - Reasoning engine: Gemini CLI only (no Claude Code, no OpenAI) - All AI functionality must be a SKILL.md before implementation begins - DRY_RUN must default to true in all action scripts - .env file mandatory, added to .gitignore before first commit - PM2 required for process persistence (not manual terminal runs) - No external APIs in Bronze tier except Gmail (optional, if time permits) - Audit logs retained minimum 90 days - PHR entries must be appended only, never overwritten or deleted Deliverables (in order of implementation): 1. constitution.md — Project governance and principles (already complete) 2. SKILL.md files — One per capability, saved to .specify/skills/<name>/SKILL.md 3. Vault structure — All folders and seed files created via vault-setup skill 4. Base watcher — filesystem_watcher.py following BaseWatcher pattern 5. Orchestrator — orchestrator.py (master process, folder watching, scheduling) 6. PM2 configuration — ecosystem.config.js for Windows 10 persistence 7. Audit logger — writes JSON logs to /Vault/Logs/YYYY-MM-DD.json 8. HITL workflow — file-move approval pattern (Pending_Approval → Approved) 9. README.md — Setup instructions, architecture overview, skill index 10. history/prompts.md — PHR maintained throughout entire build Architecture Decisions (already locked in constitution): - Vault-first: Obsidian is single source of truth, not a database - File-move pattern: Agent communicates via folder structure, not APIs - Skill-first: No code written without a corresponding SKILL.md - PHR-always: Every prompt logged to history/prompts.md without exception - HITL-always: No irreversible action without human file-move approval - DRY_RUN-default: All scripts safe by default, production requires explicit opt-in Not Building (Bronze Tier): - Gmail watcher (Silver tier) - WhatsApp watcher (Silver tier) - LinkedIn/social media posting (Silver tier) - Email MCP server (Silver tier) - Odoo accounting integration (Gold tier) - CEO briefing automation (Gold tier) - Ralph Wiggum / Gemini loop equivalent (Gold tier) - Cloud VM deployment (Platinum tier) - Any payment or banking integration (Gold tier and above) - Multi-agent coordination (Platinum tier) Security Non-Negotiables: - .env file created before any credential is used - .gitignore configured before first git commit - DRY_RUN=true enforced in all scripts by default - No auto-approval for any action during Bronze tier - Audit log written for every agent action, successful or failed PHR Format (mandatory for every prompt): --- ## [YYYY-MM-DD HH:MM] — <skill or task name> **Prompt Summary:** <one line description> **Skill:** <skill name or N/A> **File Written:** <path or N/A> **Triggered By:** Human **Status:** Completed / Failed **Notes:** <brief note> --- Timeline: Bronze tier complete before progressing to Silver Next Tier Trigger: All Bronze success criteria checked and verified"
labels: ["specification", "bronze-tier", "vault-foundation"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-bronze-vault-foundation/spec.md
 - specs/001-bronze-vault-foundation/checklists/requirements.md
tests:
 - N/A
---

## Prompt

$ARGUMENTS

## Response snapshot

Successfully generated a detailed feature specification for "Bronze Vault Foundation" and validated it against a quality checklist. The new feature branch `001-bronze-vault-foundation` was created.

## Outcome

- ✅ Impact: Successfully created feature specification and validation checklist.
- 🧪 Tests: N/A
- 📁 Files: Created spec.md and requirements.md.
- 🔁 Next prompts: Proceed to /sp.plan.
- 🧠 Reflection: Encountered and resolved issues with PowerShell script execution by switching to agent-native PHR creation.

## Evaluation notes (flywheel)

- Failure modes observed: PowerShell script execution policy/pathing issues in `run_shell_command`.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Investigate robust PowerShell script execution within `run_shell_command` or rely on agent-native PHR creation.

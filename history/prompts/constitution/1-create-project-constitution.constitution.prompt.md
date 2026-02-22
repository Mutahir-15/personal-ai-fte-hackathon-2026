---
id: 1
title: Create Project Constitution
stage: constitution
date: 2026-02-22
surface: agent
model: gemini-cli
feature: none
branch: main
user: unknown
command: /sp.constitution
labels: [constitution, setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - .specify/templates/plan-template.md
tests:
 - none
---

## Prompt

/sp.constitution Project: Personal AI Employee — Autonomous FTE (Bronze Tier, Windows 10)
Tagline: Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

Core Principles:
- Local-first: All sensitive data stays on the local machine; nothing syncs to cloud without explicit approval
- Human-in-the-loop (HITL): No sensitive or irreversible action executes without human approval
- Skill-driven intelligence: All AI functionality must be encapsulated in reusable SKILL.md files
- Autonomy with safety: The agent acts proactively but degrades gracefully on failure
- Transparency: Every action the agent takes must be logged and auditable
- Privacy by design: Credentials never stored in plain text, never committed to version control

Tech Stack:
- Reasoning/Coding Agent: Gemini CLI (primary executor, replaces Claude Code)
- Spec & Planning: Spec-kit plus (constitutions, specs, task breakdowns, implementation plans)
- Knowledge Base & GUI: Obsidian (local markdown vault — AI_Employee_Vault)
- Watcher Scripts: Python 3.13+ (filesystem, Gmail, WhatsApp monitoring)
- MCP Servers: Node.js v24+ LTS (external actions — email, browser, calendar)
- Process Management: PM2 (keeping watcher daemons alive on Windows 10)
- Orchestration: Python Orchestrator.py (master process — scheduling, folder watching)
- Version Control: GitHub Desktop

Key Standards:
- Every AI capability must be written as a SKILL.md before implementation begins
- Every SKILL.md must include: purpose, inputs, outputs, steps, success criteria, and error handling
- All watcher scripts must follow the BaseWatcher pattern (check → create_action_file → sleep)
- All action scripts must support a DRY_RUN mode (default: true during development)
- All credentials must live in .env files, added to .gitignore immediately
- Audit logs must be written to /Vault/Logs/YYYY-MM-DD.json for every agent action
- Human approval required for: emails to new contacts, any payment, bulk social posts, file deletion
- Rate limits enforced: max 10 emails/hour, max 3 payments/day

Vault Folder Structure (Bronze Tier):
- /Needs_Action/       → Watchers drop incoming items here
- /Plans/              → Claude/Gemini writes Plan.md files here
- /Done/               → Completed tasks archived here
- /Pending_Approval/   → Sensitive actions awaiting human review
- /Approved/           → Human-approved actions ready to execute
- /Rejected/           → Human-rejected actions archived here
- /Logs/               → Audit trail (JSON, 90-day retention)
- /Accounting/         → Financial transaction logs
- /Briefings/          → Weekly CEO briefing outputs
- Dashboard.md         → Real-time summary (balance, pending, active projects)
- Company_Handbook.md  → Rules of engagement for the AI agent
- Business_Goals.md    → KPIs, targets, active projects

Tiered Delivery Plan:
- Bronze (current): Vault structure + Company_Handbook + Dashboard + filesystem watcher + Gemini CLI reads/writes vault
- Silver (next): Gmail watcher + WhatsApp watcher + LinkedIn posting skill + email MCP + HITL approval workflow
- Gold (future): Full cross-domain integration + Odoo accounting + CEO briefing automation + Ralph Wiggum loop equivalent for Gemini CLI
- Platinum (future): Always-on cloud VM + dual agent (cloud drafts, local approves) + synced vault via Git

Constraints:
- OS: Windows 10 (use Task Scheduler, not cron; use Windows-compatible paths)
- No hardcoded secrets anywhere in the codebase
- No auto-approval for payments regardless of amount
- No autonomous action on emotional, legal, or medical contexts
- Watcher scripts must be managed by PM2 for persistence across reboots
- DEV_MODE must be true by default; must be explicitly set to false for production

Success Criteria (Bronze Tier):
- Obsidian vault created with correct folder structure and all seed markdown files
- At least one SKILL.md written and validated before any code is generated
- Filesystem watcher successfully detects a dropped file and creates a .md in /Needs_Action
- Gemini CLI successfully reads from and writes to the vault
- DRY_RUN mode verified working before any live integrations
- All scripts running persistently via PM2 on Windows 10
- Zero credentials committed to Git

Ethics & Responsibility:
- The agent acts on behalf of the human; the human remains fully accountable
- AI involvement must be disclosed in outbound communications where appropriate
- Weekly 15-minute log review is mandatory to catch agent drift
- The agent must never act on irreversible actions (delete, pay, post publicly) without approval
- Contacts must have a way to request human-only communication

## Response snapshot

I have successfully created the project constitution and updated the relevant templates to ensure consistency. The new constitution is at `.specify/memory/constitution.md`.

## Outcome

- ✅ Impact: The project constitution was created, defining the core principles and standards for the project.
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md, .specify/templates/plan-template.md
- 🔁 Next prompts: /sp.specify "I want to build..."
- 🧠 Reflection: Creating a constitution is a crucial first step in a spec-driven development workflow. It ensures that all subsequent artifacts and code align with the project's core principles.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): null

<!--
Sync Impact Report:
- Version change: 1.0.0
- List of modified principles: None
- Added sections: Tech Stack, Key Standards, Vault Folder Structure (Bronze Tier), Tiered Delivery Plan, Constraints, Success Criteria (Bronze Tier), Ethics & Responsibility
- Removed sections: None
- Templates requiring updates:
- Follow-up TODOs: RATIFICATION_DATE
-->

# Personal AI Employee — Autonomous FTE (Bronze Tier, Windows 10) Constitution
Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.

## Core Principles

### I. Local-First
All sensitive data stays on the local machine; nothing syncs to cloud without explicit approval.

### II. Human-in-the-loop (HITL)
No sensitive or irreversible action executes without human approval.

### III. Skill-driven intelligence
All AI functionality must be encapsulated in reusable SKILL.md files.

### IV. Autonomy with safety
The agent acts proactively but degrades gracefully on failure.

### V. Transparency
Every action the agent takes must be logged and auditable.

### VI. Privacy by design
Credentials never stored in plain text, never committed to version control.

## Tech Stack
- Reasoning/Coding Agent: Gemini CLI (primary executor, replaces Claude Code)
- Spec & Planning: Spec-kit plus (constitutions, specs, task breakdowns, implementation plans)
- Knowledge Base & GUI: Obsidian (local markdown vault — AI_Employee_Vault)
- Watcher Scripts: Python 3.13+ (filesystem, Gmail, WhatsApp monitoring)
- MCP Servers: Node.js v24+ LTS (external actions — email, browser, calendar)
- Process Management: PM2 (keeping watcher daemons alive on Windows 10)
- Orchestration: Python Orchestrator.py (master process — scheduling, folder watching)
- Version Control: GitHub Desktop

## Key Standards
- Every AI capability must be written as a SKILL.md before implementation begins.
- Every SKILL.md must include: purpose, inputs, outputs, steps, success criteria, and error handling.
- All watcher scripts must follow the BaseWatcher pattern (check → create_action_file → sleep).
- All action scripts must support a DRY_RUN mode (default: true during development).
- All credentials must live in .env files, added to .gitignore immediately.
- Audit logs must be written to /Vault/Logs/YYYY-MM-DD.json for every agent action.
- Human approval required for: emails to new contacts, any payment, bulk social posts, file deletion.
- Rate limits enforced: max 10 emails/hour, max 3 payments/day.
- **Quality Review**: All generated content (emails, reports, plans) MUST be reviewed for clarity, accuracy, and tone before being finalized, following the checklist in Company_Handbook.md.
- **Agent Drift Definition**: "Agent drift" is defined as any of the following: (1) deviation from established operational patterns defined in `SKILL.md` files, (2) unapproved execution of sensitive actions, or (3) a statistically significant change in communication style or tone over a 30-day period.

## Vault Folder Structure (Bronze Tier)
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

## Tiered Delivery Plan
- Bronze (current): Vault structure + Company_Handbook + Dashboard + filesystem watcher + Gemini CLI reads/writes vault
- Silver (next): Gmail watcher + WhatsApp watcher + LinkedIn posting skill + email MCP + HITL approval workflow
- Gold (future): Full cross-domain integration + Odoo accounting + CEO briefing automation + Ralph Wiggum loop equivalent for Gemini CLI
- Platinum (future): Always-on cloud VM + dual agent (cloud drafts, local approves) + synced vault via Git

## Constraints
- OS: Windows 10 (use Task Scheduler, not cron; use Windows-compatible paths)
- No hardcoded secrets anywhere in the codebase
- No auto-approval for payments regardless of amount
- No autonomous action on emotional, legal, or medical contexts
- Watcher scripts must be managed by PM2 for persistence across reboots
- DEV_MODE must be true by default; must be explicitly set to false for production

## Success Criteria (Bronze Tier)
- Obsidian vault created with correct folder structure and all seed markdown files
- At least one SKILL.md written and validated before any code is generated
- Filesystem watcher successfully detects a dropped file and creates a .md in /Needs_Action
- Gemini CLI successfully reads from and writes to the vault
- DRY_RUN mode verified working before any live integrations
- All scripts running persistently via PM2 on Windows 10
- Zero credentials committed to Git

## Ethics & Responsibility
- The agent acts on behalf of the human; the human remains fully accountable
- AI involvement MUST be disclosed in all external outbound communications by default. A standard footer will be used, as defined in Company_Handbook.md. Exceptions to this rule must be explicitly documented and approved.
- Weekly 15-minute log review is mandatory to catch agent drift (see Key Standards for definition).
- The agent must never act on irreversible actions (delete, pay, post publicly) without approval
- Contacts must have a way to request human-only communication

## Governance
This Constitution is the single source of truth for project principles, standards, and architecture. It must be adhered to in all development and operational activities. Amendments require a documented proposal, review, and approval from the project owner. All pull requests and reviews must verify compliance with this Constitution.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE) | **Last Amended**: 2026-02-22

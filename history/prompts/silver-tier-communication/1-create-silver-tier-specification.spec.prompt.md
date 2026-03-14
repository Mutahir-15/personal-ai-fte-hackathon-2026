---
id: 1
title: Create Silver Tier Specification
stage: spec
date: 2026-03-14
surface: agent
model: Gemini CLI
feature: silver-tier-communication
branch: 002-silver-tier-communication
user: ADMINS
command: /sp.specify
labels: [spec, silver-tier, communication]
links:
  spec: specs/002-silver-tier-communication/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-silver-tier-communication/spec.md
  - specs/002-silver-tier-communication/checklists/requirements.md
tests: []
---

## Prompt

---
description: Create or update the feature specification from a natural language feature description.
handoffs: 
  - label: Build Technical Plan
    agent: sp.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: sp.clarify
    prompt: Clarify specification requirements
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/sp.specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `Personal AI Employee — Autonomous FTE (Silver Tier) Platform: Windows 10, local-first, agent-driven, human-in-the-loop Reasoning Agent: Gemini CLI Spec & Planning Tool: Spec-kit plus Knowledge Base: Obsidian (AI_Employee_Vault) Tier: Silver — builds directly on top of completed Bronze tier Target audience: Developer extending their Bronze tier Personal AI Employee with communication and social media automation capabilities. Intermediate technical proficiency. Comfortable with OAuth2 flows, API integrations, and Playwright browser automation. Focus: - Silver tier completion as a fully functional communication layer - Gmail inbox monitoring and email action automation - WhatsApp Web message detection via Playwright - LinkedIn post generation and publishing via Gemini CLI - Email sending and drafting via local MCP server - Enhanced HITL approval workflow for all Silver action types - All new AI functionality encapsulated in SKILL.md files - Full backward compatibility with Bronze tier - PHR maintained at history/prompts/skills for every prompt Bronze Tier Prerequisite: All Bronze verification gates must have passed before Silver begins: - Vault structure intact and verified - All Bronze scripts running via PM2 - DRY_RUN=true confirmed working - audit-logger importable as shared module - End-to-end Bronze flow verified - Git commit tagged: bronze-complete Success Criteria: - gmail-watcher detects new unread important emails and creates .md files in /Needs_Action/ within 120 seconds of arrival - gmail-watcher correctly classifies email priority as high/medium/low based on keyword and label rules - gmail-watcher never processes the same email twice (processed_emails.json deduplication verified) - gmail-watcher OAuth token refresh works silently without crash - whatsapp-watcher detects keyword-matched messages and creates .md files in /Needs_Action/ within 30 seconds of receipt - whatsapp-watcher session persists across PM2 restarts - whatsapp-watcher handles QR code re-authentication gracefully - whatsapp-watcher never creates duplicate .md files (SHA256 deduplication verified) - linkedin-poster generates professional post content via Gemini CLI using Business_Goals.md context - linkedin-poster never publishes without human HITL approval - linkedin-poster respects 1 post per day limit - linkedin-poster token expiry alert appears in Dashboard.md when token expires within 7 days - email-mcp server starts and all 5 tools are discoverable by Gemini CLI via MCP protocol - email-mcp send_email requires valid approval file in /Approved/ - email-mcp draft_email works without approval requirement - email-mcp never sends to new contact without HITL approval - email-mcp respects Gmail daily send limit (100 emails/day) - silver-hitl-approval handles all 5 approval types correctly - silver-hitl-approval priority queue orders approvals correctly - silver-hitl-approval escalation alerts appear in Dashboard.md at correct time thresholds (4h/8h/20h) - silver-hitl-approval batch approval processes all valid files - silver-hitl-approval approval metrics tracked accurately - All Bronze tier verification gates still pass after Silver implementation (full backward compatibility confirmed) - All new scripts running persistently via PM2 - PHR maintained with full prompt content for every Silver prompt - Zero credentials committed to Git New State Files Required (Silver adds to Bronze): - /Vault/.watcher_state/processed_emails.json - /Vault/.watcher_state/gmail_token.json - /Vault/.watcher_state/linkedin_token.json - /Vault/.watcher_state/linkedin_posts.json - /Vault/.watcher_state/linkedin_queue.json - /Vault/.watcher_state/processed_whatsapp.json - /Vault/.watcher_state/whatsapp_session/ (folder) - /Vault/.watcher_state/approval_metrics.json - /Vault/.watcher_state/approval_queue.json - /Vault/.watcher_state/email_send_count.json New Scripts Required (Silver adds to Bronze): - gmail_watcher.py - whatsapp_watcher.py - linkedin_poster.py - silver_hitl_approval.py - email-mcp/index.js - email-mcp/gmail_client.js - email-mcp/audit_bridge.js - email-mcp/templates.js - email-mcp/package.json Bronze Scripts Extended (Silver modifies): - orchestrator.py (add Silver event handlers) - hitl_approval.py (replaced by silver_hitl_approval.py) - ecosystem.config.js (add Silver PM2 processes) - .env (add Silver credentials and config) - .gitignore (add Silver secrets) Constraints: - OS: Windows 10 only (Windows paths, msvcrt file locking) - Vault root: Configurable via .env as VAULT_PATH - Reasoning engine: Gemini CLI only - All AI functionality must have a SKILL.md before implementation - DRY_RUN must default to true in all scripts - .env file must contain all credentials — never hardcoded - PM2 required for all persistent processes - WhatsApp automation for personal use only - LinkedIn API must be v2 ugcPosts endpoint - Gmail OAuth scopes must be minimal - email-mcp must be Node.js v24+ LTS - All Silver scripts must import audit-logger from Bronze - No database — all state as JSON files in vault - Audit logs retained minimum 90 days - PHR entries append-only, never overwritten New .env Variables Required (Silver): - GMAIL_CREDENTIALS_PATH - GMAIL_TOKEN_PATH - GMAIL_POLL_INTERVAL_SECONDS - GMAIL_MAX_EMAILS_PER_POLL - GMAIL_PRIORITY_SENDERS - GMAIL_FILTER - WHATSAPP_SESSION_PATH - WHATSAPP_POLL_INTERVAL_SECONDS - WHATSAPP_KEYWORDS - WHATSAPP_PRIORITY_CONTACTS - WHATSAPP_MAX_MESSAGES_PER_POLL - LINKEDIN_CLIENT_ID - LINKEDIN_CLIENT_SECRET - LINKEDIN_AUTHOR_URN - LINKEDIN_TOKEN_PATH - LINKEDIN_POSTS_PATH - LINKEDIN_QUEUE_PATH - LINKEDIN_POST_TOPICS - LINKEDIN_PREFERRED_POST_TIMES - LINKEDIN_MAX_POSTS_PER_DAY - TRUSTED_CONTACTS - EMAIL_DAILY_LIMIT - EMAIL_SEND_COUNT_PATH - APPROVAL_EXPIRY_HOURS - ESCALATION_WARNING_HOURS - ESCALATION_URGENT_HOURS - ESCALATION_CRITICAL_HOURS - APPROVAL_METRICS_PATH - APPROVAL_QUEUE_PATH - BATCH_APPROVAL_ENABLED Security Non-Negotiables: - credentials.json added to .gitignore before first use - gmail_token.json added to .gitignore before first use - linkedin_token.json added to .gitignore before first use - whatsapp_session/ folder added to .gitignore before first use - All API keys in .env only — never in code - WhatsApp session tokens treated as sensitive credentials - LinkedIn client secret never logged or printed - email-mcp audit bridge never logs full email body - DRY_RUN=true enforced until explicitly switched off - No auto-approval for any Silver action type Deliverables (in implementation order): 1. Updated .env with all Silver variables 2. Updated .gitignore with all Silver secrets 3. gmail_watcher.py — OAuth2 Gmail inbox monitor 4. whatsapp_watcher.py — Playwright WhatsApp Web monitor 5. linkedin_poster.py — Gemini CLI post generator + publisher 6. email-mcp/ folder — complete Node.js MCP server 7. silver_hitl_approval.py — enhanced HITL approval handler 8. Updated orchestrator.py — Silver event handlers added 9. Updated ecosystem.config.js — Silver PM2 processes added 10. Silver verification checklist — all gates documented 11. Updated README.md — Silver setup instructions added 12. history/prompts/skills — Silver PHR entries appended Not Building (Silver Tier): - Odoo accounting integration (Gold tier) - Facebook/Instagram posting (Gold tier) - Twitter/X posting (Gold tier) - CEO briefing automation (Gold tier) - Gemini loop equivalent (Gold tier) - Weekly business audit (Gold tier) - Cloud VM deployment (Platinum tier) - Dual agent coordination (Platinum tier) - WhatsApp autonomous replies (Gold tier and above) - Payment or banking integration (Gold tier and above) - Any database engine - Any cloud storage or sync Timeline: Silver tier complete before progressing to Gold Bronze Compatibility: All Bronze gates must pass after Silver Next Tier Trigger: All Silver success criteria verified and all Bronze gates still passing` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

## Response snapshot

Generated the Silver Tier communication specification and validated it against the quality checklist. The feature includes Gmail monitoring, WhatsApp detection, LinkedIn automation, and an enhanced HITL approval system.

## Outcome

- ✅ Impact: Silver Tier specification defined and ready for technical planning.
- 🧪 Tests: None.
- 📁 Files: Created spec.md and requirements.md checklist.
- 🔁 Next prompts: /sp.plan to build the technical plan.
- 🧠 Reflection: The specification correctly captures all Silver Tier requirements while maintaining Bronze Tier compatibility.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): 1
- Next experiment (smallest change to try): none

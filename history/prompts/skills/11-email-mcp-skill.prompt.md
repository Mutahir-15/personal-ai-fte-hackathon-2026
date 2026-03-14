---
## [2026-03-14 11:25] — email-mcp SKILL.md
**Skill:** email-mcp
**File Written:** .specify/skills/email-mcp/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
```
You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **email-mcp**

Save the file at this exact path: .specify/skills/email-mcp/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — email-mcp SKILL.md
**Skill:** email-mcp
**File Written:** .specify/skills/email-mcp/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
[... full prompt content ...]

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
- Implemented as a local Node.js MCP server
- Exposes email capabilities to Gemini CLI via MCP protocol
- ALL email sends require human HITL approval
- Uses Gmail API for sending and drafting
- Never sends email autonomously without approval

## What This Skill Does
This skill implements a local Model Context Protocol (MCP) server
that exposes Gmail capabilities to Gemini CLI. It acts as the
"hands" for email actions. It:
1. Runs as a local Node.js MCP server on localhost
2. Exposes these MCP tools to Gemini CLI:
   - send_email: Send approved email via Gmail API
   - draft_email: Create Gmail draft without sending
   - search_emails: Search Gmail inbox
   - get_email: Retrieve full email by ID
   - reply_email: Reply to existing email thread
3. All send/reply actions require prior HITL approval
4. Drafts can be created without approval
5. Logs every action to audit-logger via file write
6. Supports email templates from Company_Handbook.md
7. Handles attachments from /Vault/Invoices/ folder
8. Never sends to unknown contacts without approval

## MCP Server Architecture
The email-mcp server must follow this architecture:

COMPONENT 1 — MCP Server (Node.js):
- File: email-mcp/index.js
- Protocol: MCP over stdio
- Port: stdio (not HTTP — MCP uses stdio transport)
- Exposes 5 tools to Gemini CLI

COMPONENT 2 — Gmail Client (Node.js):
- File: email-mcp/gmail_client.js
- Uses: googleapis npm package
- Handles: OAuth2, token refresh, API calls

COMPONENT 3 — Audit Bridge (Node.js):
- File: email-mcp/audit_bridge.js
- Writes audit entries to:
  /Vault/Logs/YYYY-MM-DD.json
- Bridges Node.js MCP server to Python audit-logger

COMPONENT 4 — Configuration:
- File: email-mcp/.env (separate from root .env)
- Contains Gmail credentials for MCP server

## MCP Server Setup Requirements

STEP 1 — Initialize Node.js Project:
cd email-mcp
npm init -y
npm install @modelcontextprotocol/sdk googleapis dotenv

STEP 2 — MCP Server Registration:
Register in Gemini CLI MCP configuration:
File: %APPDATA%\gemini-cli\mcp.json (Windows 10)

{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["C:\\path\\to\\email-mcp\\index.js"],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "C:\\path\\to\\credentials.json",
        "GMAIL_TOKEN_PATH": "C:\\path\\to\\gmail_token.json"
      }
    }
  ]
}

STEP 3 — Gmail OAuth2 Setup:
- Reuse credentials.json from gmail-watcher skill
- Reuse gmail_token.json from gmail-watcher skill
- Same OAuth scopes required:
  gmail.send, gmail.compose, gmail.readonly

STEP 4 — Verify MCP Connection:
- Start MCP server: node email-mcp/index.js
- Test tool listing via Gemini CLI
- Verify all 5 tools are discoverable

## MCP Tools Specification

### TOOL 1: send_email
Description: Send an approved email via Gmail API
Input Schema:
{
  "to": "string (required) — recipient email",
  "subject": "string (required) — email subject",
  "body": "string (required) — email body (plain text or HTML)",
  "cc": "string (optional) — CC recipients comma separated",
  "bcc": "string (optional) — BCC recipients comma separated",
  "attachment_path": "string (optional) — path to attachment file",
  "approval_file": "string (required) — path to approval .md file",
  "thread_id": "string (optional) — Gmail thread ID for threading",
  "reply_to_id": "string (optional) — message ID being replied to"
}
Pre-condition: approval_file must exist in /Approved/ folder
Returns: Gmail message ID on success

### TOOL 2: draft_email
Description: Create a Gmail draft without sending
Input Schema:
{
  "to": "string (required) — recipient email",
  "subject": "string (required) — email subject",
  "body": "string (required) — email body",
  "cc": "string (optional)",
  "attachment_path": "string (optional)",
  "source_file": "string (required) — /Needs_Action/ source file"
}
Pre-condition: None — drafts do not require approval
Returns: Gmail draft ID on success

### TOOL 3: search_emails
Description: Search Gmail inbox with a query
Input Schema:
{
  "query": "string (required) — Gmail search query",
  "max_results": "number (optional, default 10)",
  "include_body": "boolean (optional, default false)"
}
Returns: Array of email metadata objects

### TOOL 4: get_email
Description: Retrieve full email content by Gmail message ID
Input Schema:
{
  "message_id": "string (required) — Gmail message ID",
  "include_attachments": "boolean (optional, default false)"
}
Returns: Full email object with headers and body

### TOOL 5: reply_email
Description: Reply to an existing Gmail thread
Input Schema:
{
  "thread_id": "string (required) — Gmail thread ID",
  "message_id": "string (required) — message being replied to",
  "body": "string (required) — reply body",
  "approval_file": "string (required) — path to approval .md file"
}
Pre-condition: approval_file must exist in /Approved/ folder
Returns: Gmail message ID on success

## Email Approval Request Format
Before any send or reply, create approval request in
/Pending_Approval/ with this exact structure:

---
type: email_approval
action: send_email | reply_email
approval_id: <UUID>
created: <ISO 8601 timestamp>
expires: <ISO 8601 timestamp — 24 hours>
status: pending
to: <recipient email>
subject: <email subject>
has_attachment: true | false
attachment_name: <filename or null>
is_new_contact: true | false
thread_id: <Gmail thread ID or null>
source_file: <originating /Needs_Action/ file>
---

## Email Preview
**To:** <recipient>
**Subject:** <subject>
**CC:** <cc or none>

<email body preview — full content>

## Attachment
<attachment filename and size or "No attachment">

## Contact Status
<Known contact | NEW CONTACT — extra caution required>

## To Approve
Move this file to: /Approved/

## To Reject
Move this file to: /Rejected/

## Audit Bridge Format
The audit_bridge.js must write this JSON to vault logs:

{
  "timestamp": "<ISO 8601>",
  "log_level": "INFO | WARNING | ERROR",
  "action_type": "email_send | email_draft | email_search |
                  email_get | email_reply",
  "actor": "email-mcp",
  "target": "<recipient email>",
  "parameters": {
    "subject": "<subject>",
    "has_attachment": "<boolean>",
    "approval_id": "<UUID or null>"
  },
  "approval_status": "not_required | approved | pending",
  "approved_by": "human | N/A",
  "dry_run": "<boolean>",
  "result": "success | failure | skipped",
  "error_message": "<null or error>",
  "session_id": "<session_id from current_session.json>"
}

## Email Templates
Load templates from Company_Handbook.md:

Template types to support:
- invoice_email: For sending invoices to clients
- follow_up_email: For following up on pending items
- introduction_email: For new client introductions
- acknowledgment_email: For acknowledging received messages

Template variables:
{client_name}, {invoice_number}, {amount},
{due_date}, {project_name}, {sender_name}

## Contact Safety Rules
Apply these rules for every send/reply:

KNOWN CONTACT (in TRUSTED_CONTACTS .env list):
- Still requires HITL approval
- Approval request marked: is_new_contact: false

NEW CONTACT (not in TRUSTED_CONTACTS):
- Requires HITL approval
- Approval request marked: is_new_contact: true
- Dashboard.md alert: "⚠️ Email to new contact pending approval"
- Extra warning in approval request file

BULK SEND (more than 1 recipient):
- Always requires HITL approval
- Always flagged as high priority in approval request

## Rate Limiting
Gmail sending limits:
- Maximum 100 emails per day (free Gmail)
- Maximum 500 emails per day (Google Workspace)
- Track daily send count in:
  /Vault/.watcher_state/email_send_count.json
- If daily limit approached (80%): alert via Dashboard.md
- Never exceed daily limit — block sends at 95% of limit

## Required .env Variables
Add to root .env:
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=AI_Employee_Vault\.watcher_state\gmail_token.json
TRUSTED_CONTACTS=contact1@email.com,contact2@email.com
EMAIL_DAILY_LIMIT=100
EMAIL_SEND_COUNT_PATH=AI_Employee_Vault\.watcher_state\email_send_count.json

Add to email-mcp/.env:
GMAIL_CREDENTIALS_PATH=..\credentials.json
GMAIL_TOKEN_PATH=..\AI_Employee_Vault\.watcher_state\gmail_token.json
VAULT_PATH=..\AI_Employee_Vault
DRY_RUN=true

## DRY_RUN Behavior
- DRY_RUN=true (default):
  Validate all tool inputs (real)
  Check approval file exists (real)
  Log intended action to console
  Do NOT call Gmail API
  Do NOT send any email
  Do NOT create any draft
  Do NOT update email_send_count.json
  Return mock success response with dry_run: true
- DRY_RUN=false:
  Execute all actions fully

## PM2 Compatibility
The MCP server runs on demand (started by Gemini CLI).
Add a persistent PM2 entry for always-on availability:

{
  name: 'email-mcp',
  script: 'index.js',
  cwd: 'C:\\path\\to\\email-mcp',
  interpreter: 'node',
  watch: false,
  autorestart: true,
  max_restarts: 10,
  restart_delay: 5000,
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\<name>\\AI_Employee_Vault',
    GMAIL_CREDENTIALS_PATH: 'C:\\path\\to\\credentials.json',
    GMAIL_TOKEN_PATH:
      'C:\\Users\\<name>\\AI_Employee_Vault\\.watcher_state\\gmail_token.json'
  }
}

## Folder Structure
email-mcp/
├── index.js           — MCP server entry point
├── gmail_client.js    — Gmail API wrapper
├── audit_bridge.js    — Audit logging bridge
├── templates.js       — Email template loader
├── package.json       — Node.js dependencies
├── .env               — MCP server credentials
└── README.md          — MCP server setup guide

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what MCP is and why email needs an MCP server
3. **Inputs** — Gmail credentials, approval files, vault path
4. **Outputs** — sent emails, Gmail drafts, audit log entries
5. **Pre-conditions** — Node.js v24+, Gmail API enabled,
   gmail-watcher credentials reusable, Silver vault intact
6. **MCP Server Architecture** — all 4 components explained
7. **Setup Instructions** — complete 4-step setup
8. **MCP Tools Specification** — all 5 tools with full schemas
9. **Email Approval Request Template** — complete template
10. **Audit Bridge Format** — complete JSON schema
11. **Email Templates** — all 4 templates with variables
12. **Contact Safety Rules** — known, new, bulk contact handling
13. **Rate Limiting Strategy** — daily limit tracking
14. **Complete index.js Implementation** — full MCP server code
15. **Complete gmail_client.js** — full Gmail API wrapper
16. **Complete audit_bridge.js** — full audit bridge code
17. **Complete templates.js** — all 4 email templates
18. **MCP Registration** — exact mcp.json for Gemini CLI
19. **PM2 Configuration** — Windows 10 compatible entry
20. **DRY_RUN Verification** — confirm no Gmail API calls
21. **Security Checklist** — credentials, HITL, rate limits
22. **Post-conditions / Verification** — confirm skill works
23. **Error Handling** — OAuth failure, rate limit, approval
    missing, attachment not found, unknown contact,
    Gmail API down, MCP connection failure
24. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI
  without human clarification
- Full Node.js implementation must be included, not pseudocode
- All 5 MCP tools must have complete input schemas
- Contact safety rules must be strictly enforced
- Rate limiting must prevent exceeding Gmail daily limits
- Audit bridge must write correct schema to vault logs
- DRY_RUN must default to true — never false
- credentials.json and gmail_token.json must never be committed
- HITL approval is mandatory for all send/reply actions
- MCP server must be compatible with Gemini CLI MCP protocol
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills,
  never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/email-mcp/SKILL.md
2. Append the PHR entry to: history/prompts/skills
```

**Notes:** Created a production-quality `SKILL.md` for the `email-mcp` skill, implementing a Node.js MCP server with Gmail integration and HITL enforcement.
---

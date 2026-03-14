---
## [2026-03-14 10:45] — gmail-watcher SKILL.md
**Skill:** gmail-watcher
**File Written:** .specify/skills/gmail-watcher/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
```
You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **gmail-watcher**

Save the file at this exact path: .specify/skills/gmail-watcher/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — gmail-watcher SKILL.md
**Skill:** gmail-watcher
**File Written:** .specify/skills/gmail-watcher/SKILL.md
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
- Must follow the BaseWatcher pattern from Bronze tier
- Extends Bronze tier filesystem-watcher pattern to Gmail
- OAuth2 credentials must never be hardcoded

## What This Skill Does
This skill monitors a Gmail inbox for new unread important emails.
When a new email is detected, the watcher:
1. Authenticates with Gmail API using OAuth2 credentials
2. Polls for unread emails labeled as important every 120 seconds
3. Extracts email metadata and snippet from each new email
4. Creates a structured .md file in /Needs_Action/ for each email
5. Marks the email as read in Gmail after processing
6. Tracks processed email IDs in processed_emails.json
7. Logs every detection event to audit-logger
8. Handles OAuth token refresh automatically
9. Never processes the same email twice
10. Supports keyword-based priority filtering

## Gmail API Setup Requirements
The skill must include complete setup instructions for:

STEP 1 — Google Cloud Console Setup:
- Create a new project in Google Cloud Console
- Enable Gmail API for the project
- Create OAuth 2.0 credentials (Desktop App type)
- Download credentials.json to project root
- Add credentials.json to .gitignore immediately

STEP 2 — Required OAuth Scopes:
- https://www.googleapis.com/auth/gmail.readonly
- https://www.googleapis.com/auth/gmail.modify
  (needed to mark emails as read)

STEP 3 — First Run Authentication:
- On first run, browser opens for OAuth consent
- Token saved to /Vault/.watcher_state/gmail_token.json
- Subsequent runs use saved token automatically
- Token refresh handled automatically by google-auth library

STEP 4 — Required Python Libraries:
- google-auth-oauthlib
- google-auth-httplib2
- google-api-python-client
- Install via: pip install google-auth-oauthlib
  google-auth-httplib2 google-api-python-client

## Email Detection Logic
Poll Gmail API with these exact filters:

Primary filter (important unread):
q='is:unread is:important'

Secondary filter (all unread if primary empty):
q='is:unread'

Polling interval: 120 seconds (configurable via
GMAIL_POLL_INTERVAL_SECONDS in .env)

Max emails per poll: 10 (configurable via
GMAIL_MAX_EMAILS_PER_POLL in .env)

## Priority Classification
Classify each email by priority using these rules:

HIGH priority if any condition met:
- Gmail label: IMPORTANT
- Subject contains: urgent, asap, invoice, payment,
  deadline, critical, immediately
- Sender is in PRIORITY_SENDERS list in .env

MEDIUM priority if any condition met:
- Gmail label: STARRED
- Subject contains: follow up, reminder, action required

LOW priority:
- All other emails

## Email .md File Format
Create in /Needs_Action/ with this exact structure:

---
type: email
email_id: <Gmail message ID>
thread_id: <Gmail thread ID>
from: <sender email and name>
to: <recipient email>
subject: <email subject>
received: <ISO 8601 timestamp>
priority: high | medium | low
status: pending
processed: false
labels: <comma separated Gmail labels>
has_attachments: true | false
attachment_count: <count>
---

## Email Content
<email snippet — first 500 characters>

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create task from email
- [ ] Archive after processing

## Raw Metadata
- Message ID: <id>
- Thread ID: <thread_id>
- Size: <size_estimate> bytes

## Token Refresh Handling
The skill must handle token expiry gracefully:
- Check token validity before each poll
- If token expired: refresh automatically using
  refresh_token from gmail_token.json
- If refresh fails: log CRITICAL to audit-logger,
  pause operations, alert human via Dashboard.md
- Never crash on token expiry — always attempt refresh first

## Duplicate Prevention
Track processed emails in:
/Vault/.watcher_state/processed_emails.json

Structure:
{
  "last_updated": "<ISO 8601 timestamp>",
  "processed_count": <count>,
  "processed_ids": [
    "<email_id_1>",
    "<email_id_2>"
  ]
}

Rules:
- Check processed_ids before creating any .md file
- Add email_id immediately after .md file created
- On restart: load processed_emails.json to restore state
- Never process an email_id already in processed_ids

## Rate Limiting
Gmail API has usage limits. Implement these safeguards:
- Maximum 10 API calls per poll cycle
- Minimum 120 seconds between polls
- If API returns 429 (rate limit): back off exponentially
  starting at 60 seconds, max 30 minutes
- Log all rate limit events to audit-logger as WARNING

## Required .env Variables
Add these to .env:

GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=AI_Employee_Vault\.watcher_state\gmail_token.json
GMAIL_POLL_INTERVAL_SECONDS=120
GMAIL_MAX_EMAILS_PER_POLL=10
GMAIL_PRIORITY_SENDERS=boss@company.com,client@example.com
GMAIL_FILTER=is:unread is:important

## BaseWatcher Pattern Extension
The implementation must extend the Bronze tier BaseWatcher:

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path, credentials_path, token_path):
        super().__init__(vault_path,
            check_interval=GMAIL_POLL_INTERVAL_SECONDS)
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.processed_ids = self.load_processed_ids()

    def authenticate(self) -> bool:
        '''Authenticate with Gmail API, return True if successful'''
        pass

    def check_for_updates(self) -> list:
        '''Return list of new unread important emails'''
        pass

    def create_action_file(self, email) -> Path:
        '''Create .md file in /Needs_Action/ for email'''
        pass

    def load_processed_ids(self) -> set:
        '''Load processed email IDs from processed_emails.json'''
        pass

    def save_processed_ids(self) -> None:
        '''Save processed email IDs to processed_emails.json'''
        pass

    def refresh_token(self) -> bool:
        '''Refresh OAuth token, return True if successful'''
        pass

    def classify_priority(self, email) -> str:
        '''Classify email as high/medium/low priority'''
        pass

## DRY_RUN Behavior
- DRY_RUN=true (default):
  Authenticate with Gmail API (real)
  Fetch emails (real)
  Log detected emails to console
  Do NOT create .md files in /Needs_Action/
  Do NOT mark emails as read
  Do NOT update processed_emails.json
  Do NOT call audit-logger file writes
- DRY_RUN=false:
  Execute all actions fully

## PM2 Compatibility
The script must be startable via PM2:
pm2 start gmail_watcher.py --interpreter python3
  --name gmail-watcher

ecosystem.config.js entry to add:
{
  name: 'gmail-watcher',
  script: 'gmail_watcher.py',
  interpreter: 'python3',
  watch: false,
  autorestart: true,
  max_restarts: 10,
  restart_delay: 10000,
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\<name>\\AI_Employee_Vault',
    GMAIL_CREDENTIALS_PATH: 'credentials.json',
    GMAIL_TOKEN_PATH:
      'C:\\Users\\<name>\\AI_Employee_Vault\\.watcher_state\\gmail_token.json',
    GMAIL_POLL_INTERVAL_SECONDS: '120',
    GMAIL_MAX_EMAILS_PER_POLL: '10'
  }
}

## Security Requirements
- credentials.json must be in .gitignore
- gmail_token.json must be in .gitignore
- GMAIL_PRIORITY_SENDERS must be in .env, never hardcoded
- OAuth scopes must be minimal (readonly + modify only)
- Never log full email body to audit-logger
  (snippet only, max 200 characters)
- Never store full email content in vault
  (metadata and snippet only)

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what problem this skill solves
3. **Inputs** — credentials, token, vault path, .env variables
4. **Outputs** — .md files in /Needs_Action/, processed_emails.json,
   audit log entries
5. **Pre-conditions** — Gmail API enabled, credentials.json exists,
   Bronze vault structure intact
6. **Google Cloud Console Setup** — complete step-by-step OAuth setup
7. **Step-by-Step Execution Instructions** — agent-executable
8. **Priority Classification Rules** — exact keyword and label rules
9. **Email .md File Template** — complete template embedded in skill
10. **Token Refresh Handling** — complete refresh logic
11. **Duplicate Prevention Logic** — processed_emails.json management
12. **Rate Limiting Strategy** — exponential backoff implementation
13. **Full Python Implementation** — complete, ready-to-run
    gmail_watcher.py embedded directly in the skill
14. **PM2 ecosystem.config.js entry** — Windows 10 compatible
15. **DRY_RUN Verification Steps** — how to confirm DRY_RUN working
16. **Security Checklist** — credentials, gitignore, scope minimization
17. **Post-conditions / Verification** — how to confirm skill ran
    successfully
18. **Error Handling** — OAuth failure, rate limiting, API down,
    token expiry, network timeout
19. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI
  without human clarification
- Full Python implementation must be included, not pseudocode
- OAuth flow must be complete and handle first-run browser auth
- Token refresh must be automatic and silent on normal operation
- Must handle Windows 10 path separators correctly
- Must handle edge cases: empty inbox, API timeout, revoked token,
  duplicate emails, malformed email headers
- DRY_RUN must default to true — never false
- credentials.json and gmail_token.json must never be committed
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills,
  never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/gmail-watcher/SKILL.md
2. Append the PHR entry to: history/prompts/skills
```

**Notes:** Created a production-quality `SKILL.md` for the `gmail-watcher` skill, including a full Python implementation, OAuth2 setup instructions, and PM2 integration.
---

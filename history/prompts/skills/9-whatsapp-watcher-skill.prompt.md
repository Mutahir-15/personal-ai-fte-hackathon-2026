---
## [2026-03-14 11:05] — whatsapp-watcher SKILL.md
**Skill:** whatsapp-watcher
**File Written:** .specify/skills/whatsapp-watcher/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
```
You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **whatsapp-watcher**

Save the file at this exact path: .specify/skills/whatsapp-watcher/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — whatsapp-watcher SKILL.md
**Skill:** whatsapp-watcher
**File Written:** .specify/skills/whatsapp-watcher/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
[... full prompt content ...]
---

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
- Uses Playwright for WhatsApp Web automation
- WhatsApp session must persist across restarts
- WARNING: This skill uses WhatsApp Web automation.
  User must be aware of WhatsApp Terms of Service.
  Use responsibly and only for personal automation.

## What This Skill Does
This skill monitors WhatsApp Web for new incoming messages
containing priority keywords. When a matching message is detected:
1. Launches Playwright with a persistent browser context
2. Loads WhatsApp Web using saved session
3. Scans chat list for unread messages every 30 seconds
4. Filters messages by priority keywords
5. Creates a structured .md file in /Needs_Action/ for each match
6. Tracks processed messages in processed_whatsapp.json
7. Logs every detection event to audit-logger
8. Never sends any message autonomously (read-only in Bronze/Silver)
9. Handles session expiry and QR code re-authentication gracefully
10. Supports contact-based priority filtering

## Playwright Setup Requirements
The skill must include complete setup instructions:

STEP 1 — Install Playwright:
pip install playwright
playwright install chromium

STEP 2 — First Run Session Setup:
- Launch browser in headful mode (headless: false)
- Navigate to https://web.whatsapp.com
- Wait for user to scan QR code manually
- Session saved to WHATSAPP_SESSION_PATH automatically
- Subsequent runs use saved session (headless: true)

STEP 3 — Session Path Configuration:
- Store session at:
  C:\Users\<name>\AI_Employee_Vault\.watcher_state\whatsapp_session\
- Add whatsapp_session\ to .gitignore immediately
- Session folder contains browser profile — never commit

STEP 4 — Required .env Variables:
WHATSAPP_SESSION_PATH=AI_Employee_Vault\.watcher_state\whatsapp_session
WHATSAPP_POLL_INTERVAL_SECONDS=30
WHATSAPP_KEYWORDS=urgent,asap,invoice,payment,help,pricing,quote
WHATSAPP_PRIORITY_CONTACTS=+1234567890,+0987654321
WHATSAPP_MAX_MESSAGES_PER_POLL=20

## Message Detection Logic
The watcher must follow this exact detection flow:

STEP 1 — Launch Browser:
- Use persistent context with WHATSAPP_SESSION_PATH
- headless=True for normal operation
- headless=False only for first-run QR scan

STEP 2 — Load WhatsApp Web:
- Navigate to https://web.whatsapp.com
- Wait for selector: [data-testid="chat-list"]
  timeout: 30 seconds
- If timeout: assume session expired, trigger re-auth flow

STEP 3 — Scan for Unread Messages:
- Query all chats with unread indicators:
  selector: [data-testid="icon-unread-count"]
- For each unread chat:
  - Extract contact name
  - Extract message preview text
  - Extract timestamp
  - Check against keyword filter
  - Check against priority contacts list

STEP 4 — Keyword Filtering:
- Convert message text to lowercase
- Check if any keyword from WHATSAPP_KEYWORDS present
- Check if sender in WHATSAPP_PRIORITY_CONTACTS
- If match found: create action file
- If no match: log as INFO and skip

STEP 5 — Deduplication:
- Generate message_id from:
  SHA256(contact_name + timestamp + message_preview)
- Check against processed_whatsapp.json
- Skip if already processed

## Priority Classification
HIGH priority if any condition met:
- Sender in WHATSAPP_PRIORITY_CONTACTS
- Message contains: urgent, asap, payment, invoice,
  critical, immediately, emergency

MEDIUM priority if any condition met:
- Message contains: follow up, reminder, pricing,
  quote, meeting, call

LOW priority:
- Keyword match but no high/medium indicators

## WhatsApp .md File Format
Create in /Needs_Action/ with this exact structure:

---
type: whatsapp_message
message_id: <SHA256 hash>
contact_name: <sender name from WhatsApp>
contact_number: <phone if available>
received: <ISO 8601 timestamp>
priority: high | medium | low
status: pending
processed: false
is_group: true | false
group_name: <group name if is_group is true>
keyword_matched: <which keyword triggered detection>
---

## Message Content
<message preview text — max 500 characters>

## Suggested Actions
- [ ] Reply to contact
- [ ] Create task from message
- [ ] Forward to relevant party
- [ ] Archive after processing

## Raw Metadata
- Message ID: <hash>
- Detection Time: <ISO 8601>
- Keyword Matched: <keyword>

## Session Management
The skill must handle these session states:

STATE 1 — Valid Session (normal operation):
- Launch headless browser
- Load saved session from WHATSAPP_SESSION_PATH
- Proceed with message scanning

STATE 2 — Expired Session (QR code needed):
- Detect session expiry via:
  selector timeout on [data-testid="chat-list"]
- Switch to headful mode (headless: false)
- Navigate to https://web.whatsapp.com
- Wait for QR code scan (timeout: 120 seconds)
- After successful scan: save new session
- Switch back to headless mode
- Log session refresh to audit-logger
- Alert human via Dashboard.md:
  "WhatsApp session refreshed — QR scan required"

STATE 3 — Browser Crash:
- PM2 auto-restarts the script
- On restart: attempt to load saved session
- If session invalid: trigger STATE 2 flow

## Deduplication State File
Track processed messages in:
/Vault/.watcher_state/processed_whatsapp.json

Structure:
{
  "last_updated": "<ISO 8601 timestamp>",
  "processed_count": <count>,
  "processed_ids": [
    "<message_id_1>",
    "<message_id_2>"
  ]
}

Rules:
- Check processed_ids before creating any .md file
- Add message_id immediately after .md file created
- Trim to last 1000 entries to prevent unbounded growth
- On restart: load file to restore state

## BaseWatcher Pattern Extension
The implementation must extend Bronze tier BaseWatcher:

class WhatsAppWatcher(BaseWatcher):
    def __init__(self, vault_path, session_path):
        super().__init__(vault_path,
            check_interval=WHATSAPP_POLL_INTERVAL_SECONDS)
        self.session_path = Path(session_path)
        self.keywords = self.load_keywords()
        self.priority_contacts = self.load_priority_contacts()
        self.processed_ids = self.load_processed_ids()
        self.playwright = None
        self.browser = None
        self.page = None

    def authenticate(self) -> bool:
        '''Launch browser with saved session, return True if valid'''
        pass

    def check_for_updates(self) -> list:
        '''Scan WhatsApp Web for unread keyword messages'''
        pass

    def create_action_file(self, message) -> Path:
        '''Create .md file in /Needs_Action/ for message'''
        pass

    def is_session_valid(self) -> bool:
        '''Check if WhatsApp Web session is still active'''
        pass

    def refresh_session(self) -> bool:
        '''Trigger QR code re-authentication flow'''
        pass

    def generate_message_id(self, message) -> str:
        '''Generate SHA256 deduplication hash'''
        pass

    def classify_priority(self, message) -> str:
        '''Classify message as high/medium/low priority'''
        pass

    def load_processed_ids(self) -> set:
        '''Load processed message IDs from JSON state file'''
        pass

    def save_processed_ids(self) -> None:
        '''Save processed message IDs, trim to last 1000'''
        pass

## DRY_RUN Behavior
- DRY_RUN=true (default):
  Launch browser (real)
  Load WhatsApp Web session (real)
  Scan for unread messages (real)
  Log detected messages to console
  Do NOT create .md files in /Needs_Action/
  Do NOT update processed_whatsapp.json
  Do NOT call audit-logger file writes
  Do NOT alert Dashboard.md
- DRY_RUN=false:
  Execute all actions fully

## PM2 Compatibility
ecosystem.config.js entry to add:

{
  name: 'whatsapp-watcher',
  script: 'whatsapp_watcher.py',
  interpreter: 'python3',
  watch: false,
  autorestart: true,
  max_restarts: 10,
  restart_delay: 15000,
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\<name>\\AI_Employee_Vault',
    WHATSAPP_SESSION_PATH:
      'C:\\Users\\<name>\\AI_Employee_Vault\\.watcher_state\\whatsapp_session',
    WHATSAPP_POLL_INTERVAL_SECONDS: '30',
    WHATSAPP_KEYWORDS: 'urgent,asap,invoice,payment,help,pricing,quote',
    WHATSAPP_MAX_MESSAGES_PER_POLL: '20'
  }
}

## Security Requirements
- whatsapp_session/ folder must be in .gitignore
- WHATSAPP_PRIORITY_CONTACTS must be in .env, never hardcoded
- Never log full message content to audit-logger
  (preview only, max 200 characters)
- Never store full message content in vault
  (metadata and preview only)
- Never send any message autonomously
  (this skill is READ-ONLY)
- Browser profile contains session tokens —
  treat as sensitive credential

## Terms of Service Notice
Include this warning prominently in the SKILL.md:

WARNING: This skill automates WhatsApp Web using Playwright.
WhatsApp's Terms of Service prohibit unauthorized automation.
This skill is intended for personal productivity use only.
Use at your own risk. Do not use for bulk messaging,
spam, or commercial automation without WhatsApp's permission.
The author is not responsible for account restrictions
resulting from use of this skill.

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — what problem this skill solves
3. **Terms of Service Warning** — prominently placed at top
4. **Inputs** — session path, keywords, vault path, .env variables
5. **Outputs** — .md files in /Needs_Action/,
   processed_whatsapp.json, audit log entries
6. **Pre-conditions** — Playwright installed, Chromium installed,
   WhatsApp account active, Bronze vault intact
7. **Playwright Setup Instructions** — complete first-run QR flow
8. **Step-by-Step Execution Instructions** — agent-executable
9. **Message Detection Logic** — exact 5-step detection flow
10. **Priority Classification Rules** — keyword and contact rules
11. **WhatsApp .md File Template** — complete template in skill
12. **Session Management** — all 3 session states with handling
13. **Deduplication Logic** — SHA256 hashing, JSON state file
14. **Full Python Implementation** — complete, ready-to-run
    whatsapp_watcher.py embedded directly in the skill
15. **PM2 ecosystem.config.js entry** — Windows 10 compatible
16. **DRY_RUN Verification Steps** — how to confirm DRY_RUN working
17. **Security Checklist** — session path, gitignore, read-only rule
18. **Post-conditions / Verification** — how to confirm skill ran
    successfully
19. **Error Handling** — session expiry, browser crash, QR timeout,
    selector not found, network timeout, PM2 restart recovery
20. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI
  without human clarification
- Full Python implementation must be included, not pseudocode
- Session management must handle all 3 states explicitly
- SHA256 deduplication must be implemented correctly
- Must handle Windows 10 Playwright path and browser install
- Must handle edge cases: no unread messages, QR timeout,
  browser crash mid-scan, group messages, status updates
- DRY_RUN must default to true — never false
- whatsapp_session/ must never be committed to Git
- Skill is READ-ONLY — never sends messages autonomously
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills,
  never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/whatsapp-watcher/SKILL.md
2. Append the PHR entry to: history/prompts/skills
```

**Notes:** Created a production-quality `SKILL.md` for the `whatsapp-watcher` skill, including a full Python implementation using Playwright, session management, and SHA256 deduplication.
---

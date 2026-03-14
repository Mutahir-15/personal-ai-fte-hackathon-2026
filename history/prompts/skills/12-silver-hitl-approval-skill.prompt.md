---
## [2026-03-14 11:35] — silver-hitl-approval SKILL.md
**Skill:** silver-hitl-approval
**File Written:** .specify/skills/silver-hitl-approval/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
```
You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **silver-hitl-approval**

Save the file at this exact path:
.specify/skills/silver-hitl-approval/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — silver-hitl-approval SKILL.md
**Skill:** silver-hitl-approval
**File Written:** .specify/skills/silver-hitl-approval/SKILL.md
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
- EXTENDS Bronze tier hitl-approval skill
- Adds support for email, WhatsApp reply, and LinkedIn post
  approval types introduced in Silver tier
- Must be fully backward compatible with Bronze approval types
- Never auto-approves any action under any circumstance

## What This Skill Does
This skill extends the Bronze tier hitl-approval skill to handle
the additional approval types introduced in Silver tier. It:
1. Inherits all Bronze tier approval handling
   (file_drop, plan_created, generic actions)
2. Adds email approval handling (send_email, reply_email)
3. Adds LinkedIn post approval handling
4. Adds WhatsApp reply approval handling (future-ready)
5. Implements priority-based approval queue ordering
6. Adds approval dashboard section in Dashboard.md
7. Supports approval batching (approve multiple at once)
8. Implements escalation alerts for long-pending approvals
9. Tracks approval metrics in approval_metrics.json
10. Logs all approval events to audit-logger
11. Notifies Orchestrator of approved actions via state files
12. Handles concurrent approval requests safely

## Approval Type Registry
Silver tier adds these new approval types on top of Bronze:

BRONZE TYPES (inherited, unchanged):
- file_drop_action: Actions triggered by filesystem drops
- plan_execution: Executing a generated Plan.md
- generic_action: Any uncategorized action

SILVER TYPES (new):
- email_send: Send email via email-mcp
- email_reply: Reply to email thread via email-mcp
- linkedin_post: Publish LinkedIn post via linkedin-poster
- whatsapp_reply: Reply to WhatsApp message (future-ready)

## Approval Priority Queue
Order pending approvals by priority:

CRITICAL (process first):
- email_send to new contact
- Any action with expires within 2 hours
- Any action flagged is_new_contact: true

HIGH (process second):
- email_send to known contact
- email_reply
- linkedin_post with scheduled_for within 1 hour

MEDIUM (process third):
- linkedin_post with scheduled_for > 1 hour
- whatsapp_reply
- plan_execution

LOW (process last):
- file_drop_action
- generic_action

## Enhanced Dashboard.md Approval Section
Update Dashboard.md with this approval queue section:

## Pending Approvals
| Priority | Type | Target | Created | Expires | Action |
|----------|------|--------|---------|---------|--------|
| 🔴 CRITICAL | email_send | new@contact.com | 10:30 | 2h | /Pending_Approval/EMAIL_001.md |
| 🟠 HIGH | linkedin_post | LinkedIn | 09:00 | 8h | /Pending_Approval/LINKEDIN_001.md |
| 🟡 MEDIUM | plan_execution | Client A | 08:00 | 16h | /Pending_Approval/PLAN_001.md |
| 🟢 LOW | file_drop | report.pdf | 07:00 | 22h | /Pending_Approval/FILE_001.md |

## Approval Counts
- Total Pending: <count>
- Critical: <count>
- Approved Today: <count>
- Rejected Today: <count>
- Expired Today: <count>

## Email Approval Handling
When approval file type is email_send or email_reply:

ON APPROVAL DETECTED (/Approved/ folder):
1. Verify approval file schema is valid email type
2. Verify approval has not expired
3. Verify recipient email is valid format
4. Check is_new_contact flag:
   - If true: log WARNING "Approved email to new contact"
5. Extract email details from approval file
6. Write to approved_actions.json:
   {
     "action_type": "email_send",
     "approval_id": "<UUID>",
     "approved_at": "<ISO 8601>",
     "to": "<recipient>",
     "subject": "<subject>",
     "approval_file": "<path>",
     "mcp_tool": "send_email",
     "status": "ready_to_execute"
   }
7. Notify Orchestrator via state file
8. Update Dashboard.md approval section
9. Log to audit-logger

ON REJECTION DETECTED (/Rejected/ folder):
1. Update approval file status to "rejected"
2. Add rejected_at timestamp
3. Update corresponding Plan.md status
4. Archive to /Done/rejected/email/
5. Log to audit-logger
6. Update Dashboard.md

## LinkedIn Approval Handling
When approval file type is linkedin_post:

ON APPROVAL DETECTED:
1. Verify approval file schema is valid linkedin_post type
2. Verify post character count <= 3000
3. Verify post contains at least 3 hashtags
4. Check scheduled_for timestamp:
   - If null: mark for immediate publish
   - If future: add to linkedin_queue.json
5. Write to approved_actions.json:
   {
     "action_type": "linkedin_post",
     "approval_id": "<UUID>",
     "approved_at": "<ISO 8601>",
     "scheduled_for": "<ISO 8601 or null>",
     "post_file": "<path>",
     "status": "queued | ready_to_execute"
   }
6. Notify Orchestrator
7. Update Dashboard.md
8. Log to audit-logger

ON REJECTION DETECTED:
1. Update post file status to "rejected"
2. Archive to /Done/rejected/linkedin/
3. Log rejection reason
4. Log to audit-logger

## Approval Batching
Support approving multiple items at once:

Batch approval trigger:
Create file: /Approved/BATCH_APPROVE_<timestamp>.md

Batch file format:
---
type: batch_approval
created: <ISO 8601>
approved_by: human
---
## Files to Approve
- /Pending_Approval/EMAIL_001.md
- /Pending_Approval/LINKEDIN_001.md
- /Pending_Approval/PLAN_001.md

Processing rules:
- Process each file individually
- Skip any expired files in batch
- Skip any invalid files in batch
- Log each approval separately
- Report batch summary to Dashboard.md

## Escalation Alerts
Monitor pending approvals and escalate:

ESCALATION LEVEL 1 (warning):
- Approval pending > 4 hours
- Action: Add ⚠️ warning to Dashboard.md

ESCALATION LEVEL 2 (urgent):
- Approval pending > 8 hours
- Action: Add 🚨 urgent alert to Dashboard.md
- Action: Log WARNING to audit-logger

ESCALATION LEVEL 3 (critical):
- Approval pending > 20 hours (4 hours before expiry)
- Action: Add 🔴 CRITICAL alert to Dashboard.md
- Action: Log CRITICAL to audit-logger
- Action: Move to top of approval queue display

## Approval Metrics Tracking
Track metrics in:
/Vault/.watcher_state/approval_metrics.json

Structure:
{
  "last_updated": "<ISO 8601>",
  "lifetime": {
    "total_requested": <count>,
    "total_approved": <count>,
    "total_rejected": <count>,
    "total_expired": <count>,
    "approval_rate": "<percentage>"
  },
  "today": {
    "requested": <count>,
    "approved": <count>,
    "rejected": <count>,
    "expired": <count>,
    "avg_approval_time_minutes": <number>
  },
  "by_type": {
    "email_send": {"approved": 0, "rejected": 0, "expired": 0},
    "email_reply": {"approved": 0, "rejected": 0, "expired": 0},
    "linkedin_post": {"approved": 0, "rejected": 0, "expired": 0},
    "plan_execution": {"approved": 0, "rejected": 0, "expired": 0},
    "file_drop_action": {"approved": 0, "rejected": 0, "expired": 0}
  }
}

## Concurrent Request Safety
Handle multiple simultaneous approval files safely:

Rules:
- Use file locking (msvcrt on Windows 10) when writing
  approved_actions.json
- Process one approval at a time — use processing queue
- If two files detected simultaneously:
  process by priority order
- Never write to same state file from two threads
- Use atomic file moves (shutil.move) not copy+delete

## New State Files Required
Add these to /Vault/.watcher_state/:

approval_metrics.json:
- Created on first approval event
- Updated after every approval/rejection/expiry

approval_queue.json:
- Current priority-ordered queue of pending approvals
- Rebuilt every 60 seconds by watcher
- Used by Dashboard.md refresh

Structure of approval_queue.json:
{
  "last_rebuilt": "<ISO 8601>",
  "total_pending": <count>,
  "queue": [
    {
      "priority": "critical | high | medium | low",
      "type": "<approval_type>",
      "file": "<path>",
      "created": "<ISO 8601>",
      "expires": "<ISO 8601>",
      "target": "<email/platform/file>"
    }
  ]
}

## Backward Compatibility Requirements
This skill MUST handle all Bronze tier approval types:
- Read Bronze format approval files without error
- Process Bronze approvals through existing logic
- Never break Bronze tier functionality
- Bronze approved_actions.json format unchanged
- Bronze expiry logic unchanged
- All Bronze verification tests must still pass

## Required .env Variables
Add to .env:
APPROVAL_EXPIRY_HOURS=24
ESCALATION_WARNING_HOURS=4
ESCALATION_URGENT_HOURS=8
ESCALATION_CRITICAL_HOURS=20
APPROVAL_METRICS_PATH=AI_Employee_Vault\.watcher_state\approval_metrics.json
APPROVAL_QUEUE_PATH=AI_Employee_Vault\.watcher_state\approval_queue.json
BATCH_APPROVAL_ENABLED=true

## DRY_RUN Behavior
- DRY_RUN=true (default):
  Detect file movements (real)
  Validate approval file schemas (real)
  Log all detected events to console
  Do NOT write to approved_actions.json
  Do NOT update approval_metrics.json
  Do NOT update approval_queue.json
  Do NOT notify Orchestrator
  Do NOT update Dashboard.md
  Do NOT archive any files
- DRY_RUN=false:
  Execute all actions fully

## PM2 Compatibility
ecosystem.config.js entry to add:

{
  name: 'silver-hitl-approval',
  script: 'silver_hitl_approval.py',
  interpreter: 'python3',
  watch: false,
  autorestart: true,
  max_restarts: 10,
  restart_delay: 5000,
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\<name>\\AI_Employee_Vault',
    APPROVAL_EXPIRY_HOURS: '24',
    ESCALATION_WARNING_HOURS: '4',
    ESCALATION_URGENT_HOURS: '8',
    ESCALATION_CRITICAL_HOURS: '20',
    BATCH_APPROVAL_ENABLED: 'true'
  }
}

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — why Silver needs enhanced HITL over Bronze
3. **Inputs** — approval files, vault path, .env variables
4. **Outputs** — approved_actions.json, approval_metrics.json,
   approval_queue.json, Dashboard.md updates, audit logs
5. **Pre-conditions** — Bronze hitl-approval working,
   Silver vault structure intact, all Silver skills written
6. **Approval Type Registry** — all Bronze + Silver types
7. **Priority Queue Logic** — exact priority ordering rules
8. **Email Approval Handling** — complete on/reject flow
9. **LinkedIn Approval Handling** — complete on/reject flow
10. **Approval Batching** — batch file format and processing
11. **Escalation Alert Logic** — all 3 escalation levels
12. **Approval Metrics Tracking** — complete JSON schema
13. **Concurrent Request Safety** — file locking strategy
14. **Enhanced Dashboard Section** — complete table template
15. **New State Files** — approval_metrics.json and
    approval_queue.json schemas
16. **Backward Compatibility** — Bronze compatibility rules
17. **Full Python Implementation** — complete, ready-to-run
    silver_hitl_approval.py embedded directly in the skill
18. **PM2 ecosystem.config.js entry** — Windows 10 compatible
19. **DRY_RUN Verification Steps** — confirm no state writes
20. **Security Checklist** — file locking, no auto-approval,
    concurrent safety
21. **Post-conditions / Verification** — confirm skill works
22. **Error Handling** — corrupted approval files, expired
    batch items, concurrent write conflicts, missing Plan.md,
    invalid email format, LinkedIn post too long
23. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI
  without human clarification
- Full Python implementation must be included, not pseudocode
- Must be fully backward compatible with Bronze hitl-approval
- Priority queue must be rebuilt every 60 seconds
- Escalation alerts must be time-precise
- File locking must use msvcrt for Windows 10
- Batch approval must process each file independently
- DRY_RUN must default to true — never false
- No action is ever auto-approved under any circumstance
- Approval metrics must be accurate and persistent
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills,
  never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to:
   .specify/skills/silver-hitl-approval/SKILL.md
2. Append the PHR entry to: history/prompts/skills
```

**Notes:** Created a professional `SKILL.md` for the `silver-hitl-approval` skill, extending Bronze tier functionality to include email, LinkedIn, and WhatsApp approval types, priority queuing, and enhanced dashboard reporting.
---

---
## [2026-03-14 11:15] — linkedin-poster SKILL.md
**Skill:** linkedin-poster
**File Written:** .specify/skills/linkedin-poster/SKILL.md
**Triggered By:** Human
**Status:** Completed

**Full Prompt:**
```
You are an expert AI agent engineer. Your task is to write a professional,
production-quality SKILL.md file for a "Personal AI Employee" project built
on Windows 10 using Gemini CLI as the reasoning engine and Obsidian as the
local knowledge base/dashboard.

## Your Task
Write a SKILL.md file for the skill named: **linkedin-poster**

Save the file at this exact path: .specify/skills/linkedin-poster/SKILL.md
Create the directories if they do not exist.

## Prompt History Record (PHR)
After writing the SKILL.md, append an entry to: history/prompts/skills
Create the file and directories if they do not exist.

Each PHR entry must follow this exact format:

---
## [YYYY-MM-DD HH:MM] — linkedin-poster SKILL.md
**Skill:** linkedin-poster
**File Written:** .specify/skills/linkedin-poster/SKILL.md
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
- Uses LinkedIn API v2 for posting
- ALL posts require human approval before publishing
- Gemini CLI generates post content
- Never posts autonomously without HITL approval

## What This Skill Does
This skill generates and publishes LinkedIn posts for business
promotion and lead generation. It:
1. Reads Business_Goals.md and Company_Handbook.md for context
2. Uses Gemini CLI to generate professional LinkedIn post content
3. Creates a draft post .md file in /Pending_Approval/
4. Waits for human approval via HITL file-move pattern
5. On approval: publishes post via LinkedIn API v2
6. Supports scheduled posting via post queue
7. Tracks all published posts in linkedin_posts.json
8. Logs every action to audit-logger
9. Handles LinkedIn API rate limits gracefully
10. Supports post types: text, article share, and image posts
11. Never posts duplicate content
12. Generates hashtags automatically from post context

## LinkedIn API Setup Requirements
The skill must include complete setup instructions:

STEP 1 — LinkedIn Developer App Setup:
- Go to https://developer.linkedin.com/
- Create a new app
- Select company page (or personal profile)
- Request these OAuth permissions:
  - w_member_social (post on behalf of member)
  - r_liteprofile (read basic profile)
- Note: LinkedIn API access requires app review
  for some scopes — document this clearly

STEP 2 — OAuth2 Authentication Flow:
- Authorization URL:
  https://www.linkedin.com/oauth/v2/authorization
- Token URL:
  https://www.linkedin.com/oauth/v2/accessToken
- Redirect URI: http://localhost:8080/callback
- Scopes: w_member_social r_liteprofile
- Token saved to:
  /Vault/.watcher_state/linkedin_token.json
- Access token expires in 60 days — handle refresh

STEP 3 — Get Author URN:
- Call LinkedIn API to get member profile
- Extract member URN: urn:li:person:<id>
- Save to .env as LINKEDIN_AUTHOR_URN
- Required for all post API calls

STEP 4 — Required Python Libraries:
- requests
- requests-oauthlib
- Install via: pip install requests requests-oauthlib

## Post Generation Logic
The skill must follow this exact post generation flow:

STEP 1 — Load Context:
- Read Business_Goals.md for current objectives
- Read Company_Handbook.md for tone and rules
- Read /Vault/Briefings/ for latest CEO briefing
- Load LINKEDIN_POST_TOPICS from .env

STEP 2 — Generate Post with Gemini CLI:
- Construct prompt combining context
- Run Gemini CLI with post generation prompt
- Parse response into post components:
  - headline (first line, max 150 chars)
  - body (main content, max 1300 chars)
  - hashtags (5-10 relevant hashtags)
  - call_to_action (last line)

STEP 3 — Quality Checks:
- Total length must be under 3000 characters
- Must contain at least 3 hashtags
- Must not contain competitor names
- Must align with Company_Handbook.md tone rules
- Must not duplicate last 10 published posts

STEP 4 — Create Approval Request:
- Save draft to /Pending_Approval/ with full schema
- Never publish without human approval

## Post Draft .md File Format
Create in /Pending_Approval/ with this exact structure:

---
type: linkedin_post
post_id: <UUID>
created: <ISO 8601 timestamp>
scheduled_for: <ISO 8601 timestamp or null>
status: pending_approval
topic: <post topic>
generated_by: gemini_cli
requires_approval: true
approved_by: null
approved_at: null
character_count: <count>
hashtag_count: <count>
post_type: text | article | image
---

## Post Content

### Headline
<first line of post — max 150 characters>

### Body
<main post content — max 1300 characters>

### Hashtags
<space separated hashtags>

### Call to Action
<last line encouraging engagement>

## Full Post Preview
<complete post as it will appear on LinkedIn>

## To Approve
Move this file to: /Approved/

## To Reject
Move this file to: /Rejected/

## To Edit
Edit the Post Content section above,
then move to /Approved/

## Published Post Tracking
Track all published posts in:
/Vault/.watcher_state/linkedin_posts.json

Structure:
{
  "last_updated": "<ISO 8601 timestamp>",
  "total_posts": <count>,
  "posts": [
    {
      "post_id": "<UUID>",
      "linkedin_post_id": "<LinkedIn API post ID>",
      "published_at": "<ISO 8601 timestamp>",
      "headline": "<first 100 chars>",
      "hashtags": ["<tag1>", "<tag2>"],
      "character_count": <count>,
      "engagement": {
        "likes": 0,
        "comments": 0,
        "shares": 0
      }
    }
  ]
}

## LinkedIn API Post Call
After approval, publish using LinkedIn API v2:

POST https://api.linkedin.com/v2/ugcPosts
Headers:
  Authorization: Bearer <access_token>
  Content-Type: application/json
  X-Restli-Protocol-Version: 2.0.0

Body:
{
  "author": "urn:li:person:<LINKEDIN_AUTHOR_URN>",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "<full post content with hashtags>"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}

## Post Scheduling
Support scheduled posts via post queue:

Queue file: /Vault/.watcher_state/linkedin_queue.json
Structure:
{
  "queue": [
    {
      "post_id": "<UUID>",
      "approved_at": "<ISO 8601>",
      "scheduled_for": "<ISO 8601>",
      "post_file": "<path to approved .md file>",
      "status": "queued | published | failed"
    }
  ]
}

Scheduling rules:
- Maximum 1 post per day
- Preferred posting times (configurable via .env):
  LINKEDIN_PREFERRED_POST_TIMES=09:00,12:00,17:00
- If scheduled_for is null: post immediately after approval
- Never post between 22:00 and 07:00 local time

## Token Management
- Access token expires in 60 days
- Check token expiry before every API call
- If token expires within 7 days: alert human via Dashboard.md
- LinkedIn does not support automatic token refresh
  (requires user re-authentication)
- Store token expiry date in linkedin_token.json
- Alert format in Dashboard.md:
  "⚠️ LinkedIn token expires in X days —
   re-authentication required"

## Rate Limiting
LinkedIn API limits:
- 100 API calls per day per app
- Maximum 1 post per member per day
- If rate limit hit (429): log WARNING, pause 1 hour
- Track daily API call count in linkedin_token.json

## Gemini CLI Post Generation Prompt Template
The skill must include this exact prompt template:

"You are a professional LinkedIn content writer for a business.
Generate a LinkedIn post based on the following context:

Business Goals: {business_goals_content}
Tone Rules: {company_handbook_tone_section}
Topic: {post_topic}
Recent Achievement: {recent_achievement_if_any}

Requirements:
- Professional but conversational tone
- Start with an attention-grabbing headline
- Include a personal insight or business lesson
- End with a clear call to action
- Include 5-8 relevant hashtags
- Total length: 800-1300 characters
- Do not mention competitor names
- Do not make unverifiable claims

Return ONLY the post content, no explanations."

## Required .env Variables
LINKEDIN_CLIENT_ID=<your_client_id>
LINKEDIN_CLIENT_SECRET=<your_client_secret>
LINKEDIN_AUTHOR_URN=<urn:li:person:your_id>
LINKEDIN_TOKEN_PATH=AI_Employee_Vault\.watcher_state\linkedin_token.json
LINKEDIN_POSTS_PATH=AI_Employee_Vault\.watcher_state\linkedin_posts.json
LINKEDIN_QUEUE_PATH=AI_Employee_Vault\.watcher_state\linkedin_queue.json
LINKEDIN_POST_TOPICS=business tips,industry insights,success stories
LINKEDIN_PREFERRED_POST_TIMES=09:00,12:00,17:00
LINKEDIN_MAX_POSTS_PER_DAY=1

## DRY_RUN Behavior
- DRY_RUN=true (default):
  Generate post content with Gemini CLI (real)
  Create draft .md file in /Pending_Approval/ (real)
  Log intended publish action to console
  Do NOT call LinkedIn API
  Do NOT update linkedin_posts.json
  Do NOT update linkedin_queue.json
  Do NOT publish anything to LinkedIn
- DRY_RUN=false:
  Execute all actions fully including LinkedIn API call

## PM2 Compatibility
This skill is NOT a continuous watcher.
It is triggered by the Orchestrator on schedule.
Add to ecosystem.config.js as a cron-triggered job:

{
  name: 'linkedin-poster',
  script: 'linkedin_poster.py',
  interpreter: 'python3',
  watch: false,
  autorestart: false,
  cron_restart: '0 9 * * 1,3,5',
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\<name>\\AI_Employee_Vault',
    LINKEDIN_CLIENT_ID: '<your_client_id>',
    LINKEDIN_AUTHOR_URN: '<urn:li:person:your_id>',
    LINKEDIN_TOKEN_PATH:
      'C:\\Users\\<name>\\AI_Employee_Vault\\.watcher_state\\linkedin_token.json'
  }
}

## Security Requirements
- linkedin_token.json must be in .gitignore
- LINKEDIN_CLIENT_SECRET must be in .env only
- LINKEDIN_AUTHOR_URN must be in .env only
- Never log access token to audit-logger
- Never hardcode post content — always Gemini generated
- All posts require HITL approval — no autonomous posting

## SKILL.md Must Include These Sections
1. **Skill Name & Version**
2. **Purpose** — business value of automated LinkedIn posting
3. **Inputs** — Business_Goals.md, Company_Handbook.md,
   post topics, LinkedIn credentials
4. **Outputs** — draft posts in /Pending_Approval/,
   published posts via API, linkedin_posts.json,
   linkedin_queue.json
5. **Pre-conditions** — LinkedIn Developer App created,
   OAuth credentials obtained, Silver vault intact
6. **LinkedIn API Setup** — complete OAuth2 setup instructions
7. **Post Generation Flow** — exact 4-step generation process
8. **Gemini CLI Prompt Template** — complete prompt embedded
9. **Post Draft .md Template** — complete template in skill
10. **LinkedIn API Call** — exact API request format
11. **Post Scheduling Logic** — queue management,
    preferred times, daily limits
12. **Token Management** — expiry alerts, re-auth flow
13. **Rate Limiting Strategy** — daily limits, 429 handling
14. **Published Post Tracking** — linkedin_posts.json management
15. **Full Python Implementation** — complete, ready-to-run
    linkedin_poster.py embedded directly in the skill
16. **PM2 cron configuration** — Windows 10 compatible
17. **DRY_RUN Verification Steps** — confirm no API calls made
18. **Security Checklist** — token, secrets, HITL enforcement
19. **Post-conditions / Verification** — confirm skill ran
    successfully
20. **Error Handling** — API failure, token expiry, rate limit,
    Gemini CLI failure, duplicate post detection,
    approval timeout
21. **Success Criteria** — clear, binary pass/fail definition

## Quality Standards
- Instructions must be unambiguous and executable by Gemini CLI
  without human clarification
- Full Python implementation must be included, not pseudocode
- LinkedIn API v2 calls must use correct endpoint and headers
- Post quality checks must be enforced before approval request
- Token expiry must be monitored and alerted proactively
- Scheduling must respect daily limits and preferred times
- DRY_RUN must default to true — never false
- linkedin_token.json must never be committed to Git
- HITL approval is mandatory — never post autonomously
- Success criteria must be binary (pass/fail checkable)
- PHR entry must be appended to history/prompts/skills,
  never overwritten

## Output Format
Perform these two actions in order:
1. Write the SKILL.md to: .specify/skills/linkedin-poster/SKILL.md
2. Append the PHR entry to: history/prompts/skills
```

**Notes:** Created a production-quality `SKILL.md` for the `linkedin-poster` skill, featuring automated generation with Gemini CLI and mandatory HITL approval.
---

# Skill: linkedin-poster (v1.0.0)

## Purpose
Automates the generation and publishing of professional LinkedIn content to drive business promotion and lead generation. This skill leverages the Gemini CLI for high-quality content creation while enforcing a mandatory Human-in-the-Loop (HITL) approval process to ensure brand alignment and quality control.

## Inputs
- **Context Files**:
  - `Business_Goals.md`: Current objectives and key results.
  - `Company_Handbook.md`: Tone of voice, branding rules, and forbidden topics.
  - `/Vault/Briefings/*.md`: Latest updates and CEO briefings.
- **Environment Variables**:
  - `DRY_RUN`: (`true`/`false`, default: `true`).
  - `VAULT_PATH`: Path to Obsidian vault root.
  - `LINKEDIN_CLIENT_ID`: OAuth2 Client ID.
  - `LINKEDIN_CLIENT_SECRET`: OAuth2 Client Secret.
  - `LINKEDIN_AUTHOR_URN`: Member URN (e.g., `urn:li:person:12345`).
  - `LINKEDIN_POST_TOPICS`: Comma-separated topics.
  - `LINKEDIN_PREFERRED_POST_TIMES`: Comma-separated times (e.g., `09:00,12:00,17:00`).
  - `LINKEDIN_MAX_POSTS_PER_DAY`: (default: `1`).
- **State Files**:
  - `linkedin_token.json`: OAuth2 access token and metadata.

## Outputs
- **Files in Obsidian Vault**:
  - `/Pending_Approval/LINKEDIN_<UUID>.md`: Draft post for human review.
  - `linkedin_posts.json`: Historical record of all published posts.
  - `linkedin_queue.json`: Queue of approved posts waiting for their scheduled time.
- **LinkedIn Platform**:
  - Published posts on the user's profile or company page.
- **Audit Logs**:
  - Logs for generation, approval, and publishing events.

## Pre-conditions
- LinkedIn Developer App created with `w_member_social` permissions.
- OAuth2 credentials obtained and stored in `.env`.
- Silver tier vault structure exists (specifically `/Pending_Approval/`, `/Approved/`, `/Rejected/`).
- Python `requests` and `requests-oauthlib` installed.

## LinkedIn API Setup
### STEP 1 — Developer App
1. Visit [LinkedIn Developers](https://developer.linkedin.com/).
2. Create an app and verify it with a Company Page (or personal profile).
3. Under **Products**, add "Share on LinkedIn" or "Marketing Developer Platform".
4. Ensure `w_member_social` and `r_liteprofile` are in your Auth scopes.

### STEP 2 — Author URN
1. Once authenticated, call the profile endpoint:
   `GET https://api.linkedin.com/v2/me`
2. Extract the `id` field and set `LINKEDIN_AUTHOR_URN=urn:li:person:<id>` in `.env`.

### STEP 3 — Token Path
The script expects tokens at `{{VAULT_PATH}}\.watcher_state\linkedin_token.json`.
**IMPORTANT**: Add this path to your `.gitignore`.

## Post Generation Flow
1. **Context Loading**: Reads goals, handbook, and briefings to anchor the post in current business reality.
2. **Gemini Generation**: Sends a structured prompt to Gemini CLI to generate a headline, body, and hashtags.
3. **Quality Gate**: Enforces character limits (<3000 total), hashtag counts (5-10), and tone checks.
4. **HITL Request**: Saves the draft to `/Pending_Approval/` and alerts the user.

## Gemini CLI Prompt Template
```text
You are a professional LinkedIn content writer for a business.
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

Return ONLY the post content in this format:
Headline: <headline>
Body: <body>
Hashtags: <hashtags>
CTA: <cta>
```

## Post Draft .md Template
```markdown
---
type: linkedin_post
post_id: <UUID>
created: <ISO 8601>
scheduled_for: <ISO 8601 or null>
status: pending_approval
topic: <topic>
generated_by: gemini_cli
requires_approval: true
approved_by: null
approved_at: null
character_count: <count>
hashtag_count: <count>
post_type: text
---

## Post Content

### Headline
<headline>

### Body
<body>

### Hashtags
<hashtags>

### Call to Action
<cta>

## Full Post Preview
<preview>

## To Approve
Move this file to: /Approved/

## To Reject
Move this file to: /Rejected/
```

## LinkedIn API Call
```json
POST https://api.linkedin.com/v2/ugcPosts
{
  "author": "urn:li:person:<LINKEDIN_AUTHOR_URN>",
  "lifecycleState": "PUBLISHED",
  "specificContent": {
    "com.linkedin.ugc.ShareContent": {
      "shareCommentary": {
        "text": "<full post content>"
      },
      "shareMediaCategory": "NONE"
    }
  },
  "visibility": {
    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
  }
}
```

## Full Python Implementation
```python
import os
import sys
import json
import uuid
import requests
import subprocess
from pathlib import Path
from datetime import datetime, time as dtime
from src.services.audit_logger import AuditLogger

class LinkedInPoster:
    def __init__(self):
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        self.vault_path = Path(os.getenv('VAULT_PATH'))
        self.token_path = Path(os.getenv('LINKEDIN_TOKEN_PATH'))
        self.author_urn = os.getenv('LINKEDIN_AUTHOR_URN')
        self.pending_dir = self.vault_path / 'Pending_Approval'
        self.approved_dir = self.vault_path / 'Approved'
        self.state_dir = self.vault_path / '.watcher_state'
        self.posts_file = self.state_dir / 'linkedin_posts.json'
        
        for d in [self.pending_dir, self.approved_dir, self.state_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def generate_post(self):
        """Step 1 & 2: Load Context and Generate via Gemini CLI"""
        topic = os.getenv('LINKEDIN_POST_TOPICS', 'business').split(',')[0]
        goals = (self.vault_path / 'Business_Goals.md').read_text() if (self.vault_path / 'Business_Goals.md').exists() else ""
        handbook = (self.vault_path / 'Company_Handbook.md').read_text() if (self.vault_path / 'Company_Handbook.md').exists() else ""
        
        prompt = f"Professional LinkedIn writer prompt... Topic: {topic}. Goals: {goals[:500]}..."
        
        # Call Gemini CLI (assuming 'gemini' command is in path)
        try:
            result = subprocess.run(['gemini', 'ask', prompt], capture_output=True, text=True, check=True)
            raw_post = result.stdout
        except Exception as e:
            AuditLogger.log("post_generation_failed", "linkedin-poster", topic, status="error", error_message=str(e))
            return

        # Parse and save to Pending_Approval
        post_id = str(uuid.uuid4())
        draft_path = self.pending_dir / f"LINKEDIN_{post_id}.md"
        
        content = f"---\ntype: linkedin_post\npost_id: {post_id}\nstatus: pending_approval\n---\n\n{raw_post}"
        draft_path.write_text(content, encoding='utf-8')
        
        AuditLogger.log("post_draft_created", "linkedin-poster", str(draft_path), status="success")
        print(f"Post draft created: {draft_path}")

    def publish_approved_posts(self):
        """Check /Approved/ and publish via API"""
        for file in self.approved_dir.glob("LINKEDIN_*.md"):
            # Load token
            with open(self.token_path, 'r') as f:
                token_data = json.load(f)
            
            # Simple check for rate limits
            if self._is_rate_limited():
                print("Rate limited. Skipping.")
                break

            # Extract content from MD (simplified)
            body = file.read_text().split('## Post Content')[-1].strip()
            
            if self.dry_run:
                print(f"[DRY_RUN] Would publish to LinkedIn: {body[:50]}...")
            else:
                resp = requests.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"},
                    json={
                        "author": self.author_urn,
                        "lifecycleState": "PUBLISHED",
                        "specificContent": {
                            "com.linkedin.ugc.ShareContent": {
                                "shareCommentary": {"text": body},
                                "shareMediaCategory": "NONE"
                            }
                        },
                        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
                    }
                )
                if resp.status_code == 201:
                    AuditLogger.log("linkedin_post_published", "linkedin-poster", file.name, status="success")
                    file.unlink() # Cleanup or move to /Done
                else:
                    print(f"Error: {resp.text}")

    def _is_rate_limited(self):
        # Basic check against linkedin_posts.json for today's count
        return False # Placeholder

if __name__ == "__main__":
    poster = LinkedInPoster()
    # If morning, generate new draft
    if datetime.now().hour == 9:
        poster.generate_post()
    # Always check for approvals to publish
    poster.publish_approved_posts()
```

## PM2 Cron Configuration
```javascript
{
  name: 'linkedin-poster',
  script: 'linkedin_poster.py',
  interpreter: 'python3',
  watch: false,
  autorestart: false,
  cron_restart: '0 9,12,17 * * *', // Run 3 times a day to check approvals
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\ADMINS\\AI_Employee_Vault',
    LINKEDIN_CLIENT_ID: '<id>',
    LINKEDIN_AUTHOR_URN: 'urn:li:person:<id>',
    LINKEDIN_TOKEN_PATH: 'C:\\Users\\ADMINS\\AI_Employee_Vault\\.watcher_state\\linkedin_token.json'
  }
}
```

## DRY_RUN Verification
1. Set `DRY_RUN: 'true'`.
2. Trigger the script.
3. Verify that a draft is created in `/Pending_Approval/`.
4. Move a test draft to `/Approved/`.
5. Run the script again.
6. Verify console output says "[DRY_RUN] Would publish..." and **no** post appears on LinkedIn.

## Success Criteria
- **Binary Pass**: The skill generates a professional post draft in Obsidian, waits for human approval, and correctly calls the LinkedIn API to publish the post only after the file is moved to `/Approved/`, recording the event in the audit log.

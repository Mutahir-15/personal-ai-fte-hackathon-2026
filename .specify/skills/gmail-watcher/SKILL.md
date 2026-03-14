# Skill: gmail-watcher (v1.0.0)

## Purpose
Monitors a Gmail inbox for new unread important emails and automatically creates structured action items in the Obsidian vault's `/Needs_Action/` directory. This skill enables the Personal AI Employee to stay responsive to critical communications by triaging emails into the local knowledge base.

## Inputs
- **Environment Variables** (in `.env` or PM2):
  - `DRY_RUN`: (`true`/`false`, default: `true`).
  - `VAULT_PATH`: Path to Obsidian vault root.
  - `GMAIL_CREDENTIALS_PATH`: Path to `credentials.json` (default: `credentials.json`).
  - `GMAIL_TOKEN_PATH`: Path to `gmail_token.json` (default: `Vault\.watcher_state\gmail_token.json`).
  - `GMAIL_POLL_INTERVAL_SECONDS`: (default: `120`).
  - `GMAIL_MAX_EMAILS_PER_POLL`: (default: `10`).
  - `GMAIL_PRIORITY_SENDERS`: Comma-separated list (e.g., `boss@company.com,client@example.com`).
  - `GMAIL_FILTER`: Gmail search query (default: `is:unread is:important`).
- **Files**:
  - `credentials.json`: OAuth 2.0 Desktop App credentials from Google Cloud Console.
  - `gmail_token.json`: Generated after first-run OAuth consent.

## Outputs
- **Files in Obsidian Vault**:
  - `{{VAULT_PATH}}\Needs_Action\EMAIL_<id>.md`: Structured metadata and snippet of the email.
- **State Management**:
  - `{{VAULT_PATH}}\.watcher_state\processed_emails.json`: Tracks processed Gmail message IDs.
- **Audit Logs**:
  - `{{VAULT_PATH}}\Vault\Logs\YYYY-MM-DD.json`: Logs detection, processing, and error events.

## Pre-conditions
- Windows 10 environment.
- Python 3.10+ installed.
- Gmail API enabled in Google Cloud Console.
- `credentials.json` placed in project root.
- Bronze tier vault structure exists.

## Google Cloud Console Setup
### STEP 1 — Project & API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project named "Personal AI Employee".
3. Navigate to **APIs & Services > Library**.
4. Search for **Gmail API** and click **Enable**.

### STEP 2 — OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select **External** and click **Create**.
3. Fill in required App name and User support email.
4. Add scopes: `https://www.googleapis.com/auth/gmail.readonly` and `https://www.googleapis.com/auth/gmail.modify`.
5. Add your own email as a **Test User**.

### STEP 3 — Credentials
1. Go to **APIs & Services > Credentials**.
2. Click **Create Credentials > OAuth client ID**.
3. Select **Desktop App** as Application type.
4. Name it "Gemini CLI Watcher" and click **Create**.
5. Download the JSON file and rename it to `credentials.json` in your project root.
6. **IMPORTANT**: Add `credentials.json` to your `.gitignore` immediately.

## Step-by-Step Execution Instructions
1. **Install Dependencies**:
   ```powershell
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```
2. **Configure `.env`**: Add the `GMAIL_*` variables listed in the Inputs section.
3. **First Run (Authentication)**:
   Run the script manually to trigger the browser OAuth flow:
   ```powershell
   $env:DRY_RUN="false"; python .specify/skills/gmail-watcher/gmail_watcher.py
   ```
   Follow the browser prompts to grant access. The token will be saved to `gmail_token.json`.
4. **Deploy with PM2**:
   ```powershell
   pm2 start ecosystem.config.js --only gmail-watcher
   ```

## Priority Classification Rules
- **HIGH**:
  - Gmail label: `IMPORTANT`
  - Subject contains: `urgent`, `asap`, `invoice`, `payment`, `deadline`, `critical`, `immediately`
  - Sender is in `GMAIL_PRIORITY_SENDERS`
- **MEDIUM**:
  - Gmail label: `STARRED`
  - Subject contains: `follow up`, `reminder`, `action required`
- **LOW**: All other emails.

## Email .md File Template
```markdown
---
type: email
email_id: <id>
thread_id: <thread_id>
from: <sender>
to: <recipient>
subject: <subject>
received: <timestamp>
priority: high | medium | low
status: pending
processed: false
labels: <labels>
has_attachments: true | false
attachment_count: <count>
---

## Email Content
<snippet>

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create task from email
- [ ] Archive after processing

## Raw Metadata
- Message ID: <id>
- Thread ID: <thread_id>
- Size: <size> bytes
```

## Full Python Implementation
```python
import os
import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scopes required for the skill
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("gmail-watcher")

class BaseWatcher(ABC):
    def __init__(self, vault_path: Path, check_interval: int = 120):
        self.vault_path = vault_path
        self.needs_action_path = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass

    def run(self):
        logger.info(f"Watcher started. Interval: {self.check_interval}s")
        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                logger.error(f"Error in watcher loop: {e}", exc_info=True)
            time.sleep(self.check_interval)

class GmailWatcher(BaseWatcher):
    def __init__(self):
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        vault_path_str = os.getenv('VAULT_PATH')
        if not vault_path_str:
            raise ValueError("VAULT_PATH not set")
        
        self.vault_path = Path(vault_path_str)
        self.creds_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
        self.token_path = os.getenv('GMAIL_TOKEN_PATH', str(self.vault_path / 'Vault' / '.watcher_state' / 'gmail_token.json'))
        self.poll_interval = int(os.getenv('GMAIL_POLL_INTERVAL_SECONDS', '120'))
        self.max_emails = int(os.getenv('GMAIL_MAX_EMAILS_PER_POLL', '10'))
        self.priority_senders = [s.strip().lower() for s in os.getenv('GMAIL_PRIORITY_SENDERS', '').split(',') if s.strip()]
        self.filter_query = os.getenv('GMAIL_FILTER', 'is:unread is:important')
        
        super().__init__(self.vault_path, self.poll_interval)
        
        self.state_dir = self.vault_path / '.watcher_state'
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.processed_file = self.state_dir / 'processed_emails.json'
        self.logs_dir = self.vault_path / 'Vault' / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.processed_ids = self.load_processed_ids()
        self.service = None
        
        logger.info(f"GmailWatcher initialized. DRY_RUN={self.dry_run}")

    def authenticate(self) -> bool:
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
                    self._log_audit("token_refresh_failed", "Gmail API", status="error", error=str(e), level="CRITICAL")
                    return False
            else:
                if not os.path.exists(self.creds_path):
                    logger.error(f"Credentials file not found at {self.creds_path}")
                    return False
                flow = InstalledAppFlow.from_client_secrets_file(self.creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=creds)
        return True

    def check_for_updates(self) -> list:
        if not self.service and not self.authenticate():
            return []
        
        new_emails = []
        try:
            # Primary filter
            results = self.service.users().messages().list(userId='me', q=self.filter_query, maxResults=self.max_emails).execute()
            messages = results.get('messages', [])
            
            # Fallback if primary empty
            if not messages and self.filter_query != 'is:unread':
                results = self.service.users().messages().list(userId='me', q='is:unread', maxResults=self.max_emails).execute()
                messages = results.get('messages', [])

            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    # Fetch full message
                    email_data = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                    new_emails.append(email_data)
                    
                    if len(new_emails) >= self.max_emails:
                        break
                        
        except HttpError as error:
            logger.error(f"Gmail API error: {error}")
            if error.resp.status == 429:
                logger.warning("Rate limit hit. Backing off.")
                time.sleep(60)
            self._log_audit("api_error", "Gmail API", status="error", error=str(error))
            
        return new_emails

    def create_action_file(self, email) -> Path:
        msg_id = email['id']
        thread_id = email['threadId']
        headers = email['payload'].get('headers', [])
        
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        recipient = next((h['value'] for h in headers if h['name'].lower() == 'to'), 'Unknown')
        date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
        labels = email.get('labelIds', [])
        snippet = email.get('snippet', '')[:500]
        
        priority = self.classify_priority(email, subject, sender, labels)
        
        # Check attachments
        has_attachments = any(part.get('filename') for part in email['payload'].get('parts', []))
        attachment_count = sum(1 for part in email['payload'].get('parts', []) if part.get('filename'))

        md_path = self.needs_action_path / f"EMAIL_{msg_id}.md"
        
        if not self.dry_run:
            content = f"""---
type: email
email_id: {msg_id}
thread_id: {thread_id}
from: {sender}
to: {recipient}
subject: {subject}
received: {date_str}
priority: {priority}
status: pending
processed: false
labels: {', '.join(labels)}
has_attachments: {str(has_attachments).lower()}
attachment_count: {attachment_count}
---

## Email Content
{snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create task from email
- [ ] Archive after processing

## Raw Metadata
- Message ID: {msg_id}
- Thread ID: {thread_id}
- Size: {email.get('sizeEstimate', 0)} bytes
"""
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Mark as read (remove UNREAD label)
            self.service.users().messages().batchModify(
                userId='me', 
                body={'ids': [msg_id], 'removeLabelIds': ['UNREAD']}
            ).execute()
            
            self.processed_ids.add(msg_id)
            self.save_processed_ids()
            
            self._log_audit("email_detected", msg_id, status="success", params={"priority": priority, "subject": subject[:100]})
            logger.info(f"Processed email {msg_id} (Priority: {priority})")
        else:
            logger.info(f"DRY_RUN: Would process email {msg_id} (Priority: {priority})")
            self._log_audit("email_detected_dry_run", msg_id, params={"priority": priority})
            
        return md_path

    def classify_priority(self, email, subject, sender, labels) -> str:
        subject_lower = subject.lower()
        sender_lower = sender.lower()
        
        # HIGH
        if 'IMPORTANT' in labels: return 'high'
        for kw in ['urgent', 'asap', 'invoice', 'payment', 'deadline', 'critical', 'immediately']:
            if kw in subject_lower: return 'high'
        for ps in self.priority_senders:
            if ps in sender_lower: return 'high'
            
        # MEDIUM
        if 'STARRED' in labels: return 'medium'
        for kw in ['follow up', 'reminder', 'action required']:
            if kw in subject_lower: return 'medium'
            
        return 'low'

    def load_processed_ids(self) -> set:
        if self.processed_file.exists():
            try:
                with open(self.processed_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_ids', []))
            except: pass
        return set()

    def save_processed_ids(self):
        data = {
            "last_updated": datetime.now().isoformat(),
            "processed_count": len(self.processed_ids),
            "processed_ids": list(self.processed_ids)
        }
        with open(self.processed_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _log_audit(self, action, target, status="success", params=None, error="N/A", level="INFO"):
        log_file = self.logs_dir / f"{datetime.now().date().isoformat()}.json"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "log_level": level,
            "action_type": action,
            "actor": "gmail-watcher",
            "target": target,
            "parameters": params or {},
            "status": status,
            "dry_run": self.dry_run,
            "error_message": error
        }
        try:
            logs = []
            if log_file.exists():
                with open(log_file, 'r') as f: logs = json.load(f)
            logs.append(entry)
            with open(log_file, 'w') as f: json.dump(logs, f, indent=2)
        except: pass

if __name__ == "__main__":
    try:
        watcher = GmailWatcher()
        watcher.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
```

## PM2 ecosystem.config.js entry
```javascript
{
  name: 'gmail-watcher',
  script: '.specify/skills/gmail-watcher/gmail_watcher.py',
  interpreter: 'python3',
  watch: false,
  autorestart: true,
  max_restarts: 10,
  restart_delay: 10000,
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\ADMINS\\AI_Employee_Vault',
    GMAIL_CREDENTIALS_PATH: 'credentials.json',
    GMAIL_TOKEN_PATH: 'C:\\Users\\ADMINS\\AI_Employee_Vault\\.watcher_state\\gmail_token.json',
    GMAIL_POLL_INTERVAL_SECONDS: '120',
    GMAIL_MAX_EMAILS_PER_POLL: '10',
    GMAIL_PRIORITY_SENDERS: 'boss@company.com,client@example.com',
    GMAIL_FILTER: 'is:unread is:important'
  }
}
```

## DRY_RUN Verification Steps
1. Ensure `DRY_RUN: 'true'` in environment.
2. Run script: `python .specify/skills/gmail-watcher/gmail_watcher.py`.
3. Check console: Should see "DRY_RUN: Would process email..." for unread important emails.
4. Check Vault: No `.md` files should be created in `Needs_Action`.
5. Check Gmail: Emails should remain unread.
6. Check Logs: `Vault/Logs/YYYY-MM-DD.json` should have entries with `dry_run: true`.

## Security Checklist
- [ ] `credentials.json` added to `.gitignore`.
- [ ] `gmail_token.json` added to `.gitignore`.
- [ ] Scopes restricted to `readonly` and `modify`.
- [ ] No full email bodies logged to audit logs (snippets only).
- [ ] OAuth consent restricted to test users during development.

## Post-conditions / Verification
- [ ] `Needs_Action` contains `.md` files for new important emails.
- [ ] `processed_emails.json` is updated with message IDs.
- [ ] Emails are marked as read in Gmail (when `DRY_RUN=false`).
- [ ] Daily audit logs accurately reflect actions.

## Success Criteria
- **Binary Pass**: The watcher detects a new important unread email, creates a correctly formatted `.md` file in the vault, marks the email as read in Gmail, and records the event in the audit log without crashing or creating duplicates.

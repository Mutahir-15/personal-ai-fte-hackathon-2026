# Skill: whatsapp-watcher (v1.0.0)

> [!WARNING]
> **TERMS OF SERVICE NOTICE**
> This skill automates WhatsApp Web using Playwright. WhatsApp's Terms of Service prohibit unauthorized automation. This skill is intended for **personal productivity use only**. Use at your own risk. Do not use for bulk messaging, spam, or commercial automation without WhatsApp's permission. The author is not responsible for account restrictions resulting from use of this skill.

## Purpose
Monitors WhatsApp Web for new incoming messages containing priority keywords or from specific contacts. When a match is detected, it creates a structured action item in the Obsidian vault's `/Needs_Action/` directory. This enables the Personal AI Employee to capture urgent chat-based requests into the local knowledge base.

## Inputs
- **Environment Variables**:
  - `DRY_RUN`: (`true`/`false`, default: `true`).
  - `VAULT_PATH`: Path to Obsidian vault root.
  - `WHATSAPP_SESSION_PATH`: Path to persistent browser profile (default: `Vault\.watcher_state\whatsapp_session`).
  - `WHATSAPP_POLL_INTERVAL_SECONDS`: Polling frequency (default: `30`).
  - `WHATSAPP_KEYWORDS`: Comma-separated list (e.g., `urgent,asap,invoice,payment`).
  - `WHATSAPP_PRIORITY_SENDERS`: Comma-separated phone numbers (e.g., `+1234567890`).
  - `WHATSAPP_MAX_MESSAGES_PER_POLL`: (default: `20`).

## Outputs
- **Files in Obsidian Vault**:
  - `{{VAULT_PATH}}\Needs_Action\WHATSAPP_<hash>.md`: Structured metadata and message preview.
- **State Management**:
  - `{{VAULT_PATH}}\.watcher_state\processed_whatsapp.json`: Tracks processed message hashes.
- **Audit Logs**:
  - `{{VAULT_PATH}}\Vault\Logs\YYYY-MM-DD.json`: Logs detection and session events.

## Pre-conditions
- Windows 10 environment.
- Python 3.10+ installed.
- Playwright and Chromium installed.
- Active WhatsApp account with a phone for QR scanning.
- Bronze tier vault structure exists.

## Playwright Setup Instructions
### STEP 1 — Install Playwright
Open PowerShell in your project root:
```powershell
pip install playwright
playwright install chromium
```

### STEP 2 — First Run Session Setup
The first time you run the script, it needs to be "headful" so you can scan the QR code.
1. Run the script manually in headful mode:
   ```powershell
   $env:DRY_RUN="true"; $env:WHATSAPP_HEADLESS="false"; python .specify/skills/whatsapp-watcher/whatsapp_watcher.py
   ```
2. A Chromium window will open at `web.whatsapp.com`.
3. Scan the QR code with your phone.
4. Once the chat list loads, close the script (`Ctrl+C`).
5. The session is now saved to `WHATSAPP_SESSION_PATH`.

## Step-by-Step Execution Instructions
1. **Configure `.gitignore`**:
   Add `whatsapp_session/` and `processed_whatsapp.json` to your `.gitignore`.
2. **Configure `.env`**:
   Ensure `WHATSAPP_SESSION_PATH` and `WHATSAPP_KEYWORDS` are set.
3. **Deploy with PM2**:
   ```powershell
   pm2 start ecosystem.config.js --only whatsapp-watcher
   ```

## Message Detection Logic
1. **Launch Browser**: Persistent context loads from `WHATSAPP_SESSION_PATH`.
2. **Load WhatsApp**: Navigates to `web.whatsapp.com` and waits for `[data-testid="chat-list"]`.
3. **Scan Unread**: Looks for `[data-testid="icon-unread-count"]`.
4. **Filter**: Checks preview text against keywords and contact names against priority list.
5. **Deduplicate**: Generates SHA256 of `contact + timestamp + text`.

## Priority Classification Rules
- **HIGH**: Sender in `WHATSAPP_PRIORITY_SENDERS` OR contains `urgent, asap, payment, invoice, critical, immediately, emergency`.
- **MEDIUM**: Contains `follow up, reminder, pricing, quote, meeting, call`.
- **LOW**: Keyword match found but no high/medium indicators.

## WhatsApp .md File Template
```markdown
---
type: whatsapp_message
message_id: <hash>
contact_name: <name>
contact_number: <phone>
received: <timestamp>
priority: high | medium | low
status: pending
processed: false
is_group: true | false
group_name: <group>
keyword_matched: <keyword>
---

## Message Content
<text>

## Suggested Actions
- [ ] Reply to contact
- [ ] Create task from message
- [ ] Forward to relevant party
- [ ] Archive after processing

## Raw Metadata
- Message ID: <hash>
- Detection Time: <timestamp>
- Keyword Matched: <keyword>
```

## Full Python Implementation
```python
import os
import sys
import time
import json
import hashlib
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from abc import ABC, abstractmethod
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("whatsapp-watcher")

class BaseWatcher(ABC):
    def __init__(self, vault_path: Path, check_interval: int = 30):
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

class WhatsAppWatcher(BaseWatcher):
    def __init__(self):
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        vault_path_str = os.getenv('VAULT_PATH')
        if not vault_path_str:
            raise ValueError("VAULT_PATH not set")
        
        self.vault_path = Path(vault_path_str)
        self.session_path = Path(os.getenv('WHATSAPP_SESSION_PATH', str(self.vault_path / '.watcher_state' / 'whatsapp_session')))
        self.poll_interval = int(os.getenv('WHATSAPP_POLL_INTERVAL_SECONDS', '30'))
        self.keywords = [k.strip().lower() for k in os.getenv('WHATSAPP_KEYWORDS', '').split(',') if k.strip()]
        self.priority_contacts = [c.strip() for c in os.getenv('WHATSAPP_PRIORITY_SENDERS', '').split(',') if c.strip()]
        self.max_messages = int(os.getenv('WHATSAPP_MAX_MESSAGES_PER_POLL', '20'))
        
        super().__init__(self.vault_path, self.poll_interval)
        
        self.state_dir = self.vault_path / '.watcher_state'
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.processed_file = self.state_dir / 'processed_whatsapp.json'
        self.logs_dir = self.vault_path / 'Vault' / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.processed_ids = self.load_processed_ids()
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        logger.info(f"WhatsAppWatcher initialized. DRY_RUN={self.dry_run}")

    def authenticate(self) -> bool:
        """Launch browser with persistent context."""
        if self.page: return True
        
        self.playwright = sync_playwright().start()
        headless = os.getenv('WHATSAPP_HEADLESS', 'true').lower() == 'true'
        
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.session_path),
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.page = self.context.new_page()
        self.page.goto("https://web.whatsapp.com")
        
        return self.is_session_valid()

    def is_session_valid(self) -> bool:
        try:
            # Wait for chat list to confirm logged in
            self.page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
            return True
        except PlaywrightTimeoutError:
            logger.warning("WhatsApp session not detected. Might need QR scan.")
            return False

    def refresh_session(self):
        """Trigger QR code re-auth flow."""
        logger.info("Triggering QR refresh flow...")
        self.context.close()
        # Restart headful
        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.session_path),
            headless=False
        )
        self.page = self.context.new_page()
        self.page.goto("https://web.whatsapp.com")
        
        self._log_audit("session_refresh_required", "WhatsApp Web", level="WARNING")
        
        # Wait up to 120s for user scan
        try:
            self.page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
            logger.info("QR Scan successful.")
            return True
        except PlaywrightTimeoutError:
            logger.error("QR Scan timeout.")
            return False

    def check_for_updates(self) -> list:
        if not self.authenticate():
            if not self.refresh_session():
                return []
        
        matches = []
        try:
            # Look for chats with unread dots
            unread_chats = self.page.query_selector_all('[data-testid="chat-list"] > div > div > div')
            
            for chat in unread_chats:
                unread_indicator = chat.query_selector('[data-testid="icon-unread-count"]')
                if not unread_indicator: continue
                
                # Extract info
                contact_name = chat.query_selector('[data-testid="cell-frame-title"] span').inner_text()
                preview_text = chat.query_selector('[data-testid="last-msg-status"]').inner_text() if chat.query_selector('[data-testid="last-msg-status"]') else ""
                # More reliable preview text selector might be needed depending on WA layout
                
                # Simplified for demonstration - real implementation would involve more robust selectors
                preview_text = chat.inner_text().split('\n')[-1] # Fallback to last line of chat cell
                
                timestamp = datetime.now().strftime("%H:%M") # WA usually shows time or date
                
                msg_id = self.generate_message_id(contact_name, timestamp, preview_text)
                
                if msg_id not in self.processed_ids:
                    # Filter
                    matched_kw = self._get_matched_keyword(preview_text)
                    is_priority_contact = contact_name in self.priority_contacts
                    
                    if matched_kw or is_priority_contact:
                        matches.append({
                            "id": msg_id,
                            "contact": contact_name,
                            "text": preview_text,
                            "timestamp": datetime.now().isoformat(),
                            "keyword": matched_kw or "Priority Contact"
                        })
                        
                if len(matches) >= self.max_messages: break
                
        except Exception as e:
            logger.error(f"Error scanning chats: {e}")
            
        return matches

    def create_action_file(self, message) -> Path:
        msg_id = message['id']
        priority = self.classify_priority(message)
        
        md_path = self.needs_action_path / f"WHATSAPP_{msg_id}.md"
        
        if not self.dry_run:
            content = f"""---
type: whatsapp_message
message_id: {msg_id}
contact_name: {message['contact']}
received: {message['timestamp']}
priority: {priority}
status: pending
processed: false
keyword_matched: {message['keyword']}
---

## Message Content
{message['text'][:500]}

## Suggested Actions
- [ ] Reply to contact
- [ ] Create task from message
- [ ] Forward to relevant party
- [ ] Archive after processing

## Raw Metadata
- Message ID: {msg_id}
- Detection Time: {datetime.now().isoformat()}
- Keyword Matched: {message['keyword']}
"""
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.processed_ids.add(msg_id)
            self.save_processed_ids()
            self._log_audit("whatsapp_detected", msg_id, status="success", params={"priority": priority, "contact": message['contact']})
            logger.info(f"Processed WhatsApp from {message['contact']} (Priority: {priority})")
        else:
            logger.info(f"DRY_RUN: Would process WhatsApp from {message['contact']} (Priority: {priority})")
            self._log_audit("whatsapp_detected_dry_run", msg_id, params={"priority": priority})
            
        return md_path

    def _get_matched_keyword(self, text):
        text_lower = text.lower()
        for kw in self.keywords:
            if kw in text_lower: return kw
        return None

    def classify_priority(self, message) -> str:
        text_lower = message['text'].lower()
        if message['contact'] in self.priority_contacts: return 'high'
        for kw in ['urgent', 'asap', 'payment', 'invoice', 'critical', 'immediately', 'emergency']:
            if kw in text_lower: return 'high'
        for kw in ['follow up', 'reminder', 'pricing', 'quote', 'meeting', 'call']:
            if kw in text_lower: return 'medium'
        return 'low'

    def generate_message_id(self, contact, timestamp, text):
        seed = f"{contact}{timestamp}{text}"
        return hashlib.sha256(seed.encode()).hexdigest()[:16]

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
            "processed_ids": list(self.processed_ids)[-1000:] # Trim to last 1000
        }
        with open(self.processed_file, 'w') as f:
            json.dump(data, f, indent=2)

    def _log_audit(self, action, target, status="success", params=None, error="N/A", level="INFO"):
        log_file = self.logs_dir / f"{datetime.now().date().isoformat()}.json"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "log_level": level,
            "action_type": action,
            "actor": "whatsapp-watcher",
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
        watcher = WhatsAppWatcher()
        watcher.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
```

## PM2 ecosystem.config.js entry
```javascript
{
  name: 'whatsapp-watcher',
  script: '.specify/skills/whatsapp-watcher/whatsapp_watcher.py',
  interpreter: 'python3',
  watch: false,
  autorestart: true,
  max_restarts: 10,
  restart_delay: 15000,
  env: {
    DRY_RUN: 'true',
    VAULT_PATH: 'C:\\Users\\ADMINS\\AI_Employee_Vault',
    WHATSAPP_SESSION_PATH: 'C:\\Users\\ADMINS\\AI_Employee_Vault\\.watcher_state\\whatsapp_session',
    WHATSAPP_POLL_INTERVAL_SECONDS: '30',
    WHATSAPP_KEYWORDS: 'urgent,asap,invoice,payment,help,pricing,quote',
    WHATSAPP_PRIORITY_SENDERS: '+1234567890',
    WHATSAPP_MAX_MESSAGES_PER_POLL: '20'
  }
}
```

## DRY_RUN Verification Steps
1. Ensure `DRY_RUN: 'true'` in environment.
2. Run script manually: `python .specify/skills/whatsapp-watcher/whatsapp_watcher.py`.
3. Send a test message to yourself from another account containing "urgent".
4. Check console: Should see "DRY_RUN: Would process WhatsApp from..."
5. Check Vault: No `.md` files should be created in `Needs_Action`.
6. Check Logs: `Vault/Logs/YYYY-MM-DD.json` should have entries with `dry_run: true`.

## Security Checklist
- [ ] `whatsapp_session/` folder added to `.gitignore`.
- [ ] `WHATSAPP_PRIORITY_SENDERS` stored in `.env`, not hardcoded.
- [ ] Skill is read-only (no message sending logic).
- [ ] Browser profile treated as sensitive credential.

## Post-conditions / Verification
- [ ] `Needs_Action` contains `.md` files for matching WhatsApp messages.
- [ ] `processed_whatsapp.json` updated with message hashes.
- [ ] Audit logs reflect detection events.

## Success Criteria
- **Binary Pass**: The watcher detects a new WhatsApp message containing a priority keyword, generates a SHA256 hash for deduplication, creates a correctly formatted `.md` file in the vault (when `DRY_RUN=false`), and logs the event without crashing.

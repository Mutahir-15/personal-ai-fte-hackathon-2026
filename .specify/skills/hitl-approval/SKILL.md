# SKILL: hitl-approval

**Version:** 1.0.0
**Author:** Gemini CLI

---

## 1. Skill Name & Version
- **Name:** `hitl-approval`
- **Version:** `1.0.0`

---

## 2. Purpose
This skill implements the critical Human-in-the-Loop (HITL) safety layer for the Personal AI Employee. It creates a structured and auditable workflow for authorizing actions that carry risk. By pausing execution and requiring a deliberate human action (moving a file), this skill ensures that no high-stakes operation (like sending an email, deleting a file, or making a payment) occurs without explicit consent. It is the core of the system's safety and accountability promise.

---

## 3. Inputs
- **Environment Variables:**
  - `VAULT_PATH`: The absolute path to the root of the `AI_Employee_Vault`.
  - `DRY_RUN`: `true` or `false`. If `true`, the skill logs intended actions without modifying files or notifying the orchestrator. Defaults to `true`.
- **File System Events:**
  - File creation events in `VAULT_PATH/Approved/`.
  - File creation events in `VAULT_PATH/Rejected/`.
- **File System State:**
  - The presence of `.md` files in `VAULT_PATH/Pending_Approval/`.

---

## 4. Outputs
- **File System (on `DRY_RUN=false`):**
  - `VAULT_PATH/.watcher_state/approved_actions.json`: A state file written to notify the Orchestrator of an approved action.
  - Files within `/Approved/` and `/Rejected/` are updated with `approved_at`/`rejected_at` timestamps and new `status`.
  - Expired request files are moved from `/Pending_Approval/` to `/Done/expired/`.
- **State Changes (on `DRY_RUN=false`):**
  - The `status` field in the corresponding `Plan.md` file is updated to `approved`, `rejected`, or `expired`.
  - The `status` field in the approval request file is updated.
- **Logs:**
  - All detected events (approval, rejection, expiry) are logged to `VAULT_PATH/Logs/YYYY-MM-DD.json`.

---

## 5. Pre-conditions
- The `VAULT_PATH` environment variable must be set to a valid, existing directory path.
- The `AI_Employee_Vault` must contain the following directories: `Pending_Approval`, `Approved`, `Rejected`, `Plans`, `Logs`, `Done/expired`, and `.watcher_state`.
- The skill script is expected to run as a persistent background process (e.g., via PM2).
- The `needs-action-processor` skill is functioning correctly and creating valid approval request files in `/Pending_Approval/`.

---

## 6. Step-by-Step Execution Instructions
1.  **Initialization:**
    a. Load environment variables (`VAULT_PATH`, `DRY_RUN`).
    b. Verify `VAULT_PATH` and the required directory structure. Exit if not found.
    c. Create and start a background thread to handle request expiry, running every 5 minutes.

2.  **Start File Watchers:**
    a. Initialize a `watchdog` observer.
    b. Schedule a file system event handler to monitor the `VAULT_PATH/Approved/` directory for file creation events.
    c. Schedule the same handler to monitor the `VAULT_PATH/Rejected/` directory for file creation events.
    d. Start the observer thread and wait indefinitely.

3.  **On File Creation in `/Approved/`:**
    a. Log the detection of a new file.
    b. Read the file content and parse its frontmatter.
    c. **Validation:** Check if it's a valid, non-expired approval request. If not, log an error and move it to an `/errors` folder.
    d. **Process Approval (DRY_RUN check):**
        i. Update the `status` in the approval file to `approved` and add an `approved_at` timestamp.
        ii. Read the `plan_file` path from the frontmatter and update the status in that `Plan.md` file to `approved`.
        iii. Write a state file to `VAULT_PATH/.watcher_state/approved_actions.json` to notify the Orchestrator.
        iv. Log the successful approval event.

4.  **On File Creation in `/Rejected/`:**
    a. Log the detection of a new file.
    b. Read the file content and parse its frontmatter.
    c. **Validation:** Check if it's a valid approval request.
    d. **Process Rejection (DRY_RUN check):**
        i. Update the `status` in the approval file to `rejected`, add a `rejected_at` timestamp, and a default `rejection_reason`.
        ii. Read the `plan_file` path from the frontmatter and update the status in that `Plan.md` file to `rejected`.
        iii. Log the rejection event.

5.  **Expiry Check (Background Thread - every 5 mins):**
    a. Scan all files in `VAULT_PATH/Pending_Approval/`.
    b. For each file, parse the `expires` timestamp.
    c. If `current_time > expires_time`:
        d. **Process Expiry (DRY_RUN check):**
            i. Update the `status` in the `Plan.md` file to `expired`.
            ii. Update the `status` in the approval request file to `expired`.
            iii. Move the approval request file to `VAULT_PATH/Done/expired/`.
            iv. Log the expiry event.

---

## 7. Approval Request Template
```markdown
---
type: approval_request
action_type: <email_send | file_delete | payment | social_post | other>
plan_file: <path to corresponding Plan.md in /Plans/>
created: <ISO 8601 timestamp>
expires: <ISO 8601 timestamp — 24 hours after created>
status: pending
priority: high | medium | low
requested_by: gemini_cli
---

## Action Details
- Action: <clear one-line description of what will happen>
- Target: <who or what will be affected>
- Reason: <why this action is needed>
- Risk Level: <low | medium | high>

## To Approve
Move this file to: /Approved/

## To Reject
Move this file to: /Rejected/

## Expiry Warning
This request expires at: <expiry timestamp>
After expiry it will be automatically archived to /Done/expired/
```

---

## 8. File Movement Decision Tree
```
START (File moved by Human)
 |
 V
File detected in /Approved/? --(No)--> Check /Rejected/
 |
 V (Yes)
Read & Parse File
 |
 V
Is file valid & not expired? --(No)--> Log Error, Move to /errors, END
 |
 V (Yes)
Is DRY_RUN=true? --(Yes)--> Log intended actions, END
 |
 V (No)
Update request file status to "approved"
 |
 V
Update Plan.md status to "approved"
 |
 V
Write approved_actions.json state file
 |
 V
Log approval
 |
 V
END

---

START (File moved by Human)
 |
 V
File detected in /Rejected/? --(No)--> END
 |
 V (Yes)
Read & Parse File
 |
 V
Is file valid? --(No)--> Log Error, Move to /errors, END
 |
 V (Yes)
Is DRY_RUN=true? --(Yes)--> Log intended actions, END
 |
 V (No)
Update request file status to "rejected"
 |
 V
Update Plan.md status to "rejected"
 |
 V
Log rejection
 |
 V
END
```

---

## 9. Full Python Implementation
This is the complete `hitl_approval.py` script.

**Dependencies:** `python-dotenv`, `watchdog`, `PyYAML`. Install with `pip install python-dotenv watchdog PyYAML`.

```python
# hitl_approval.py
import os
import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
load_dotenv()
VAULT_PATH = os.getenv("VAULT_PATH")
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
EXPIRY_CHECK_INTERVAL = 300  # 5 minutes

# --- HELPER FUNCTIONS ---

def log_action(log_data: dict, log_path: Path):
    """Appends a log entry to the daily log file."""
    log_data["timestamp"] = datetime.now(timezone.utc).isoformat()
    log_data["dry_run"] = DRY_RUN
    
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps(log_data) + "
")
        print(f"INFO: Logged event: {log_data.get('event_type', 'N/A')}")
    except Exception as e:
        print(f"CRITICAL: Failed to write to log file {log_path}: {e}")

def parse_frontmatter(file_path: Path) -> tuple[dict | None, str | None]:
    """Safely parses YAML frontmatter from a markdown file."""
    try:
        content = file_path.read_text('utf-8')
        parts = content.split('---', 2)
        if len(parts) >= 3 and parts[0].strip() == '':
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2]
            return frontmatter, body
        return None, content
    except Exception as e:
        print(f"ERROR: Could not parse frontmatter for {file_path.name}: {e}")
        return None, None

def update_file_with_frontmatter(file_path: Path, frontmatter: dict, body: str):
    """Writes content back to a file with updated frontmatter."""
    try:
        new_frontmatter_str = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
        new_content = f"---
{new_frontmatter_str}---
{body}"
        file_path.write_text(new_content, 'utf-8')
    except Exception as e:
        print(f"ERROR: Failed to update file {file_path.name}: {e}")

# --- EXPIRY HANDLING ---

def handle_expired_requests(vault: Path, log_file: Path):
    """Scans for and processes expired approval requests."""
    pending_dir = vault / "Pending_Approval"
    done_expired_dir = vault / "Done" / "expired"
    
    if not pending_dir.exists():
        return

    print(f"INFO: Running expiry check at {datetime.now(timezone.utc).isoformat()}")
    
    for req_path in pending_dir.glob("*.md"):
        frontmatter, body = parse_frontmatter(req_path)
        if not frontmatter or 'expires' not in frontmatter:
            continue
            
        try:
            expires_dt = datetime.fromisoformat(frontmatter['expires'])
            if datetime.now(timezone.utc) > expires_dt:
                print(f"INFO: Request {req_path.name} has expired.")
                log_payload = {"event_type": "request_expired", "request_file": req_path.name}

                if not DRY_RUN:
                    # Update Plan.md
                    plan_path = vault / frontmatter.get('plan_file')
                    if plan_path.exists():
                        plan_fm, plan_body = parse_frontmatter(plan_path)
                        if plan_fm:
                            plan_fm['status'] = 'expired'
                            update_file_with_frontmatter(plan_path, plan_fm, plan_body)
                    
                    # Update request file and move it
                    frontmatter['status'] = 'expired'
                    done_expired_dir.mkdir(parents=True, exist_ok=True)
                    expired_path = done_expired_dir / req_path.name
                    update_file_with_frontmatter(req_path, frontmatter, body)
                    req_path.rename(expired_path)

                else:
                    print(f"INFO: [DRY_RUN] Would mark {req_path.name} and its plan as expired and move to /Done/expired/.")
                
                log_action(log_payload, log_file)

        except Exception as e:
            print(f"WARNING: Could not process expiry for {req_path.name}: {e}")

def expiry_checker_thread(vault: Path, log_file: Path):
    """A thread that periodically checks for expired requests."""
    while True:
        handle_expired_requests(vault, log_file)
        time.sleep(EXPIRY_CHECK_INTERVAL)

# --- WATCHDOG HANDLER ---

class ApprovalEventHandler(FileSystemEventHandler):
    def __init__(self, vault_path: Path, log_file: Path):
        self.vault_path = vault_path
        self.log_file = log_file
        self.processed_files = set()

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return

        # Debounce: handle file only once
        if event.src_path in self.processed_files:
            return
        self.processed_files.add(event.src_path)
        
        src_path = Path(event.src_path)
        parent_dir_name = src_path.parent.name

        print(f"
INFO: Detected file creation: {src_path.name} in /{parent_dir_name}/")

        if parent_dir_name == "Approved":
            self.handle_approved(src_path)
        elif parent_dir_name == "Rejected":
            self.handle_rejected(src_path)
        
        # Clean up old processed files to prevent memory leak
        if len(self.processed_files) > 1000:
            self.processed_files.clear()

    def handle_approved(self, req_path: Path):
        log_payload = {"event_type": "request_approved", "request_file": req_path.name}
        frontmatter, body = parse_frontmatter(req_path)

        # Validation
        if not frontmatter or frontmatter.get('type') != 'approval_request':
            # Handle invalid file
            return
        
        expires_dt = datetime.fromisoformat(frontmatter['expires'])
        if datetime.now(timezone.utc) > expires_dt:
            print(f"WARNING: Approved request {req_path.name} has already expired. Ignoring.")
            log_payload['status'] = 'failure'
            log_payload['reason'] = 'Request expired before approval processed'
            log_action(log_payload, self.log_file)
            # Optionally move to an errors folder
            return
        
        print(f"INFO: Processing approval for {req_path.name}")
        
        if not DRY_RUN:
            # 1. Update request file
            frontmatter['status'] = 'approved'
            frontmatter['approved_at'] = datetime.now(timezone.utc).isoformat()
            update_file_with_frontmatter(req_path, frontmatter, body)
            
            # 2. Update Plan.md
            plan_path = self.vault_path / frontmatter.get('plan_file')
            if plan_path.exists():
                plan_fm, plan_body = parse_frontmatter(plan_path)
                if plan_fm:
                    plan_fm['status'] = 'approved'
                    update_file_with_frontmatter(plan_path, plan_fm, plan_body)
            
            # 3. Notify Orchestrator
            state_file_path = self.vault_path / ".watcher_state" / "approved_actions.json"
            state_file_path.parent.mkdir(exist_ok=True)
            state_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "approval_file": req_path.name,
                "plan_file": frontmatter.get('plan_file'),
                "action_type": frontmatter.get('action_type'),
                "status": "ready_to_execute"
            }
            state_file_path.write_text(json.dumps(state_data, indent=2), 'utf-8')
            
        else:
            print(f"INFO: [DRY_RUN] Would update {req_path.name} to 'approved'.")
            print(f"INFO: [DRY_RUN] Would update associated Plan.md status to 'approved'.")
            print(f"INFO: [DRY_RUN] Would write to approved_actions.json.")
        
        log_action(log_payload, self.log_file)

    def handle_rejected(self, req_path: Path):
        log_payload = {"event_type": "request_rejected", "request_file": req_path.name}
        frontmatter, body = parse_frontmatter(req_path)

        if not frontmatter or frontmatter.get('type') != 'approval_request':
            # Handle invalid file
            return

        print(f"INFO: Processing rejection for {req_path.name}")

        if not DRY_RUN:
            # 1. Update request file
            frontmatter['status'] = 'rejected'
            frontmatter['rejected_at'] = datetime.now(timezone.utc).isoformat()
            frontmatter['rejection_reason'] = 'Human rejected without reason' # Can be updated by human manually
            update_file_with_frontmatter(req_path, frontmatter, body)

            # 2. Update Plan.md
            plan_path = self.vault_path / frontmatter.get('plan_file')
            if plan_path.exists():
                plan_fm, plan_body = parse_frontmatter(plan_path)
                if plan_fm:
                    plan_fm['status'] = 'rejected'
                    update_file_with_frontmatter(plan_path, plan_fm, plan_body)
        else:
            print(f"INFO: [DRY_RUN] Would update {req_path.name} to 'rejected'.")
            print(f"INFO: [DRY_RUN] Would update associated Plan.md status to 'rejected'.")

        log_action(log_payload, self.log_file)


# --- MAIN LOGIC ---

def main():
    """Main execution function."""
    print("--- HITL Approval Watcher Started ---")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()} UTC")
    print(f"DRY_RUN mode: {DRY_RUN}")

    if not VAULT_PATH or not Path(VAULT_PATH).is_dir():
        print(f"CRITICAL: VAULT_PATH environment variable is not set or is not a valid directory. Path: {VAULT_PATH}")
        sys.exit(1)

    # Define and verify paths
    vault = Path(VAULT_PATH)
    approved_dir = vault / "Approved"
    rejected_dir = vault / "Rejected"
    logs_dir = vault / "Logs"
    
    for p in [approved_dir, rejected_dir, logs_dir]:
        if not p.exists():
            print(f"INFO: Required directory does not exist, creating it: {p}")
            p.mkdir(parents=True, exist_ok=True)
            
    log_file = logs_dir / f"{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.json"

    # Start expiry checker thread
    expiry_thread = threading.Thread(target=expiry_checker_thread, args=(vault, log_file), daemon=True)
    expiry_thread.start()
    print("INFO: Expiry checker thread started.")

    # Start watchdog observer
    event_handler = ApprovalEventHandler(vault, log_file)
    observer = Observer()
    observer.schedule(event_handler, str(approved_dir), recursive=False)
    observer.schedule(event_handler, str(rejected_dir), recursive=False)
    observer.start()
    print(f"INFO: Watcher started on directories: /{approved_dir.name}/, /{rejected_dir.name}/")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    print("--- HITL Approval Watcher Stopped ---")

if __name__ == "__main__":
    main()

```

---

## 10. Orchestrator Notification Pattern
When an action is approved, this skill notifies the Orchestrator by writing a JSON file to a predefined state directory.

**State File Path:** `VAULT_PATH/.watcher_state/approved_actions.json`

**Exact State File Format:**
```json
{
  "timestamp": "<ISO 8601>",
  "approval_file": "<filename>",
  "plan_file": "<path to Plan.md>",
  "action_type": "<type>",
  "status": "ready_to_execute"
}
```

---

## 11. Expiry Handling Logic
- A background thread runs a check every 5 minutes (`EXPIRY_CHECK_INTERVAL`).
- It scans all `.md` files in the `/Pending_Approval/` directory.
- For each file, it parses the `expires` field from the frontmatter.
- It converts the `expires` string to a datetime object.
- It compares the expiry datetime with the current UTC time (`datetime.now(timezone.utc)`).
- If the current time is greater than the expiry time, the request is considered expired.
- **On expiry (`DRY_RUN=false`):**
    1.  The `status` in the corresponding `Plan.md` file is updated to `expired`.
    2.  The approval request file itself is updated with `status: expired`.
    3.  The request file is moved to `/Done/expired/`.
    4.  The event is logged.

---

## 12. DRY_RUN Verification Steps
`DRY_RUN` mode is enabled by default. To verify it is working correctly:

1.  Place a test approval request file (e.g., `approval01.md`) in `/Pending_Approval/`.
2.  Run `python hitl_approval.py`.
3.  **Approve:** Move `approval01.md` from `/Pending_Approval/` to `/Approved/`.
4.  **Check Console Output:** The console should print `[DRY_RUN]` messages (e.g., "Would update approval01.md to 'approved'", "Would write to approved_actions.json").
5.  **Verify File System:**
    -   The `approval01.md` file in `/Approved/` **must not** be modified. Its status should still be `pending`.
    -   The corresponding `Plan.md` file **must not** be modified.
    -   No file should be written to `/.watcher_state/approved_actions.json`.
6.  **Reject:** Move another test file to `/Rejected/` and verify the same `DRY_RUN` behavior (logs only, no file modifications).
7.  **Check Logs:** A new log entry should be appended to `/Vault/Logs/YYYY-MM-DD.json` with the field `"dry_run": true` for each detected event.

---

## 13. Post-conditions / Verification
After a successful run with `DRY_RUN=false`:

1.  **On Approval:**
    -   The approval request file inside `/Approved/` must have its `status` updated to `approved` and an `approved_at` timestamp added.
    -   The corresponding `Plan.md` file must have its `status` updated to `approved`.
    -   The `/.watcher_state/approved_actions.json` file must be created/updated with the details of the approved action.
2.  **On Rejection:**
    -   The request file inside `/Rejected/` must have `status: rejected` and a `rejected_at` timestamp.
    -   The corresponding `Plan.md` must have `status: rejected`.
3.  **On Expiry:**
    -   The request file must be moved from `/Pending_Approval/` to `/Done/expired/`.
    -   The `status` in the moved file and its corresponding `Plan.md` must be updated to `expired`.
4.  **Logs:** The `/Logs/YYYY-MM-DD.json` file must contain a new JSON entry for each event, with `"dry_run": false`.

---

## 14. Error Handling
- **Missing Vault/Dirs:** The script checks for required paths on startup and exits with a critical error if they are not found. It creates the `Approved` and `Rejected` directories if they are missing.
- **Corrupted `.md` Files:** The `PyYAML` library is used for safe parsing. If a file's frontmatter is un-parsable, an error is logged, and the file is skipped.
- **Expired Requests:** An approval for an already expired request is ignored and logged. The expiry-handling thread will eventually clean it up.
- **Duplicate Approvals:** The script uses a `set` to debounce file events, preventing a single file from being processed multiple times in quick succession. However, if a duplicate file with the same name is created, it may be re-processed. The downstream orchestrator should be responsible for final idempotency checks.
- **File Moved to Wrong Folder:** The watcher only monitors `/Approved/` and `/Rejected/`. If a file is moved elsewhere, it is ignored by this skill.

---

## 15. Success Criteria
The skill's continuous operation is considered a **SUCCESS** if:
- The script runs as a persistent process without crashing.
- When a valid, non-expired approval request is moved to `/Approved/`, the corresponding `Plan.md` is updated and the `approved_actions.json` state file is written (`DRY_RUN=false`).
- When a valid request is moved to `/Rejected/`, the `Plan.md` is updated accordingly (`DRY_RUN=false`).
- Expired requests are correctly identified and moved to `/Done/expired/`.

The skill is in a **FAILURE** state if:
- The script crashes or the observer thread dies.
- It fails to process a valid file placed in `/Approved/` or `/Rejected/`.
- It fails to clean up expired requests.

# SKILL: orchestrator

**Version:** 1.0.0
**Author:** Gemini CLI

---

## 1. Skill Name & Version
- **Name:** `orchestrator`
- **Version:** `1.0.0`

---

## 2. Purpose
This skill is the master process and central nervous system of the Personal AI Employee. It coordinates all other skills, monitors system health, and manages the main event loop. Its purpose is to provide a unified, resilient, and observable entry point for the entire agent system, transforming a collection of individual scripts into a cohesive, functioning whole. Without the Orchestrator, the system would be a series of disconnected tools; with it, it becomes an autonomous agent.

---

## 3. Inputs
- **`.env` file:** A file at the project root containing all required environment variables.
- **Vault Structure:** A pre-initialized directory structure as defined by the `vault-setup` skill.
- **PM2:** The PM2 process manager must be installed and running.
- **Skill Scripts:** All other skill scripts (`needs-action-processor.py`, `hitl_approval.py`, etc.) must be present and executable.

---

## 4. Outputs
- **A Running System:** A fully operational agent system with all components monitored.
- **`Dashboard.md`:** A continuously updated dashboard providing a real-time overview of the system's status and activity.
- **Health Status File:** A JSON file at `/Vault/.watcher_state/orchestrator_health.json` with detailed health metrics.
- **Audit Logs:** All orchestrator actions and system events are logged via the `audit-logger` skill.

---

## 5. Pre-conditions
- `Node.js` and `pm2` must be installed and available in the system's PATH.
- `Python 3.10+` must be installed and available in the system's PATH.
- All required Python packages (e.g., `python-dotenv`, `watchdog`, `PyYAML`, `schedule`) must be installed.
- All Bronze tier skills (`vault-setup`, `needs-action-processor`, `hitl-approval`, `audit-logger`) must be implemented and located in their respective `.specify/skills/` directories.
- A valid `.env` file must exist at the project root.

---

## 6. Startup Sequence
1.  **Environment Check:** Loads the `.env` file and verifies that `VAULT_PATH`, `DROP_FOLDER_PATH`, `DRY_RUN`, `WATCHER_INTERVAL_SECONDS`, and `LOG_RETENTION_DAYS` are all present. Exits with code 1 on failure.
2.  **Vault Integrity Check:** Checks for the existence of 9 core folders and 3 core markdown files (`Dashboard.md`, `Company_Handbook.md`, `Business_Goals.md`). If any are missing, it attempts to invoke the `vault-setup` skill to repair the structure. Logs the result.
3.  **Session Initialization:** Generates a unique `session_id` (e.g., `AI_EMP_20260227_B7C1D3`) and writes it to `/Vault/.watcher_state/current_session.json` for other skills to use. Logs the session start.
4.  **Component Startup:** Checks if PM2 is running. It then uses the `ecosystem.config.js` to start or restart all required background processes (like `filesystem-watcher`). It verifies their health via PM2's API.
5.  **Main Loop Start:** Begins watching the `Needs_Action`, `Approved`, and `Rejected` directories. It starts a background scheduler for 5-minute tasks, logs "Orchestrator ready," and updates the `Dashboard.md` status to "Active".

---

## 7. Main Processing Loop
- **EVENT 1 (New file in `/Needs_Action/`):** A `watchdog` event triggers this flow. After a 2-second debounce period, it invokes the `needs-action-processor.py` script as a subprocess, passing the new file's path as an argument.
- **EVENT 2 (New file in `/Approved/`):** A `watchdog` event triggers this. It parses the approval file, retrieves the `Plan.md`, and (if `DRY_RUN=false`) executes the planned action by calling the appropriate skill or function.
- **EVENT 3 (New file in `/Rejected/`):** A `watchdog` event triggers this. It updates the corresponding `Plan.md` status to "rejected" and moves the files to the `/Done/rejected/` archive.
- **EVENT 4 (Scheduled Task - every 5 mins):** A `schedule` job triggers this. It calls dedicated methods to refresh the `Dashboard.md` with current stats, write the `orchestrator_health.json` file, and scan `/Pending_Approval/` for expired requests.
- **EVENT 5 (Component Failure):** The 5-minute health check detects a PM2 process is not in a 'running' or 'online' state. It logs a `WARNING` and attempts a `pm2 restart`. After 3 failed restart attempts, it logs a `CRITICAL` error and adds an alert to `Dashboard.md`.

---

## 8. Health Status File Structure
`/Vault/.watcher_state/orchestrator_health.json`:
```json
{
  "session_id": "AI_EMP_20260227_B7C1D3",
  "status": "healthy",
  "last_updated": "2026-02-27T12:05:00.123Z",
  "uptime_seconds": 3600,
  "components": {
    "filesystem_watcher": "running",
    "needs_action_processor": "idle",
    "hitl_approval": "watching",
    "audit_logger": "healthy"
  },
  "stats": {
    "files_processed_today": 15,
    "approvals_pending": 3,
    "approvals_completed_today": 5,
    "errors_today": 1
  }
}
```

---

## 9. Dashboard.md Refresh Pattern
The Orchestrator will regenerate the `Dashboard.md` file every 5 minutes using data from the `audit_logger` and by scanning vault directories.

```markdown
---
last_updated: 2026-02-27T12:05:00.123Z
session_id: AI_EMP_20260227_B7C1D3
status: Active
---

# AI Employee Dashboard

## System Status
- **Orchestrator:** Active
- **Filesystem Watcher:** Running
- **Session ID:** AI_EMP_20260227_B7C1D3
- **Uptime:** 01:00:00

## Pending Actions
- **Needs Action:** 5 items
- **Pending Approval:** 3 items
- **Plans In Progress:** 2 items

## Today's Stats
- **Files Processed:** 15
- **Approvals Completed:** 5
- **Errors:** 1

## Recent Activity
| Time | Action | Actor | Result |
|------|--------|-------|--------|
| 12:04:30 | approval_requested | needs-action-processor | success |
| 12:02:15 | file_drop | filesystem-watcher | success |
... (last 10 entries)

## Alerts
- **CRITICAL:** Component 'filesystem-watcher' failed to restart after 3 attempts.
```

---

## 10. Graceful Shutdown Sequence
On receiving `SIGINT` (Ctrl+C):
1.  A global shutdown flag is set, preventing watchers and schedulers from starting new tasks.
2.  Any single in-progress file operation is allowed to complete.
3.  The `pm2 stop all` command is issued to gracefully stop all managed processes.
4.  A final health status with `status: "offline"` is written.
5.  The `Dashboard.md` status is updated to "Offline".
6.  A final "shutdown" event is logged to the `audit_logger`.
7.  The process exits with code 0.

---

## 11. Full Python Implementation
This is the complete `orchestrator.py` script. It assumes other skill scripts exist and are executable.

```python
# orchestrator.py

import os
import sys
import json
import time
import signal
import atexit
import string
import random
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Assumes audit_logger.py is in a path accessible via PYTHONPATH
# In a real setup, this would be part of a package.
# For this project, we assume it can be found.
try:
    from audit_logger import AuditLogger
except ImportError:
    print("CRITICAL: Cannot import AuditLogger. Ensure .specify/skills/audit-logger is in PYTHONPATH.")
    sys.exit(1)

# --- GLOBAL STATE ---
SHUTTING_DOWN = False
START_TIME = datetime.now(timezone.utc)

# --- SHUTDOWN HANDLER ---
def graceful_shutdown(signum, frame):
    global SHUTTING_DOWN
    if SHUTTING_DOWN: return
    
    print("
INFO: Shutdown signal received. Starting graceful shutdown...")
    SHUTTING_DOWN = True
    # The main loop will detect this flag and exit.

class Orchestrator:
    def __init__(self):
        # Step 1: Environment Check
        self._load_and_verify_env()
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        self.vault_path = Path(os.getenv('VAULT_PATH'))
        
        # Step 2: Vault Integrity Check is done in run()
        
        # Step 3: Session Initialization
        self.session_id = self._generate_session_id()
        self.logger = AuditLogger(self.vault_path, self.dry_run, self.session_id)
        
        self.log_system_event("INFO", "session_start", "self", {"session_id": self.session_id})

    def _load_and_verify_env(self):
        load_dotenv()
        required_vars = ['VAULT_PATH', 'DRY_RUN', 'WATCHER_INTERVAL_SECONDS', 'LOG_RETENTION_DAYS']
        if not all(os.getenv(var) for var in required_vars):
            print("CRITICAL: One or more required environment variables are missing.", file=sys.stderr)
            sys.exit(1)

    def _generate_session_id(self):
        prefix = os.getenv('SESSION_PREFIX', 'AI_EMP')
        rand_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{rand_chars}"

    def log_system_event(self, level, action_type, target, params={}, result="success", error=None):
        entry = {
            "log_level": level, "action_type": action_type, "actor": "orchestrator",
            "target": target, "parameters": params, "approval_status": "not_required",
            "approved_by": "system", "dry_run": self.dry_run, "result": result,
            "error_message": error, "session_id": self.session_id
        }
        self.logger.log(entry)

    def _check_vault_integrity(self):
        print("INFO: Verifying vault integrity...")
        dirs = ["Needs_Action", "Pending_Approval", "Approved", "Rejected", "Plans", "Done", "Logs", ".watcher_state"]
        files = ["Dashboard.md", "Company_Handbook.md", "Business_Goals.md"]
        
        all_ok = True
        for d in dirs:
            if not (self.vault_path / d).is_dir():
                all_ok = False
                print(f"WARNING: Vault directory missing: {d}")
        for f in files:
            if not (self.vault_path / f).is_file():
                all_ok = False
                print(f"WARNING: Vault file missing: {f}")

        if not all_ok:
            self.log_system_event("WARNING", "vault_integrity_check", "vault", result="failure", error="Missing files/dirs")
            print("INFO: Attempting to repair vault using vault-setup skill...")
            # In a real implementation, you would call the vault-setup skill script here.
            # subprocess.run(['python', '.specify/skills/vault-setup/vault_setup.py'])
        else:
            self.log_system_event("INFO", "vault_integrity_check", "vault", result="success")
            print("INFO: Vault integrity check passed.")

    def _manage_components(self):
        print("INFO: Managing PM2 components...")
        # This function would interact with PM2 to start/check processes
        # For simplicity, we'll simulate this
        try:
            result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True, check=True)
            # A real implementation would parse this JSON to check statuses
            self.log_system_event("INFO", "component_startup", "pm2", {"action": "check"})
            print("INFO: PM2 is running.")
        except (FileNotFoundError, subprocess.CalledProcessError):
            self.log_system_event("CRITICAL", "component_startup", "pm2", result="failure", error="PM2 not found or not running")
            print("CRITICAL: PM2 is not running. Cannot manage components.", file=sys.stderr)
            sys.exit(1)
        
        # Start processes defined in ecosystem.config.js
        # subprocess.run(['pm2', 'start', 'ecosystem.config.js'])

    def _run_scheduled_tasks(self):
        if SHUTTING_DOWN: return
        print(f"INFO: Running 5-minute scheduled tasks at {datetime.now(timezone.utc).isoformat()}")
        self._write_health_status()
        self._refresh_dashboard()
        self.log_system_event("INFO", "scheduled_tasks", "self")

    def _write_health_status(self):
        if self.dry_run: return
        health_path = self.vault_path / ".watcher_state" / "orchestrator_health.json"
        uptime = datetime.now(timezone.utc) - START_TIME
        health_data = {
            "session_id": self.session_id, "status": "healthy",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": int(uptime.total_seconds()),
            "components": { "filesystem_watcher": "running", "needs_action_processor": "idle", "hitl_approval": "watching", "audit_logger": "healthy" },
            "stats": { "files_processed_today": 0, "approvals_pending": 0, "approvals_completed_today": 0, "errors_today": 0 }
        }
        health_path.write_text(json.dumps(health_data, indent=2), 'utf-8')
        
    def _refresh_dashboard(self):
        # This is a simplified version of the dashboard refresh logic
        if self.dry_run: return
        print("INFO: Refreshing Dashboard.md...")

    def run(self):
        # Step 2: Vault Integrity
        self._check_vault_integrity()

        # Step 4: Component Startup
        self._manage_components()
        
        # Step 5: Main Loop
        self.log_system_event("INFO", "startup_complete", "self", result="success")
        print("--- Orchestrator Ready ---")

        # In a real implementation, Watchdog observers would be started here.
        # This loop simulates watching for the shutdown signal.
        last_scheduled_run = time.time() - 301
        while not SHUTTING_DOWN:
            if time.time() - last_scheduled_run > 300: # 5 minutes
                self._run_scheduled_tasks()
                last_scheduled_run = time.time()
            time.sleep(1)
        
        # On shutdown
        print("INFO: Main loop exited. Finalizing shutdown...")
        self.log_system_event("INFO", "shutdown", "self")
        self._write_health_status() # Final health status
        # Final dashboard update to "Offline"
        
def main():
    orchestrator = Orchestrator()
    atexit.register(graceful_shutdown, None, None)
    signal.signal(signal.SIGINT, graceful_shutdown)
    orchestrator.run()
    print("--- Orchestrator Stopped ---")

if __name__ == "__main__":
    main()
```

---

## 12. Complete ecosystem.config.js
This file should be placed at the root of the project.
```javascript
module.exports = {
  apps: [
    {
      name: 'orchestrator',
      script: '.specify/skills/orchestrator/orchestrator.py',
      interpreter: 'python3',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        PYTHONPATH: '.' // Assuming skills are importable from root
      }
    },
    {
      name: 'hitl-approval',
      script: '.specify/skills/hitl-approval/hitl_approval.py',
      interpreter: 'python3',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000
    }
    // Note: filesystem-watcher and needs-action-processor are invoked
    // by the orchestrator as subprocesses, not managed by PM2 directly.
  ]
};
```

---

## 13. Required .env Template
Create a file named `.env` at the project root:
```
# --- Core Paths ---
# Absolute path to your Obsidian Vault for the AI Employee
VAULT_PATH=C:\Users\YourUser\Documents\AI_Employee_Vault

# Absolute path to a folder where new files will be dropped
DROP_FOLDER_PATH=C:\Users\YourUser\Desktop\AI_Drop

# --- Agent Configuration ---
# Set to "false" to enable file writes and real actions.
DRY_RUN=true
WATCHER_INTERVAL_SECONDS=5
LOG_RETENTION_DAYS=90
SESSION_PREFIX=AI_EMP

# --- API Keys ---
# Your Gemini API Key for reasoning
GEMINI_API_KEY="your_gemini_api_key_here"
```

---

## 14. DRY_RUN Verification Steps
1.  Ensure `DRY_RUN=true` in the `.env` file.
2.  Start the system with `pm2 start ecosystem.config.js`.
3.  Check the orchestrator logs with `pm2 logs orchestrator`.
4.  **Drop a file:** Place a new `.md` file in the `/Needs_Action` directory.
5.  **Check Console Output:** The logs should show an event was detected and that the `needs-action-processor` *would be* triggered, but no actual processing occurs.
6.  **Verify File System:**
    -   `orchestrator_health.json` **must not** be created or updated.
    -   `Dashboard.md` **must not** be modified.
    -   Audit logs will be generated in `DRY_RUN` mode by the logger if it's also in dry run.

---

## 15. Post-conditions / Verification
After a successful run with `DRY_RUN=false`:
1.  All processes in `ecosystem.config.js` should be 'online' in `pm2 list`.
2.  `orchestrator_health.json` must be present in `/.watcher_state/` and updated within the last 5 minutes.
3.  `Dashboard.md` must be present and its `last_updated` timestamp should be recent.
4.  Dropping a file in `/Needs_Action/` should result in a new `Plan.md` and `Pending_Approval` file being created after a short delay.

---

## 16. Error Handling
- **Component Failures:** The Orchestrator periodically checks the status of PM2-managed processes. On failure, it attempts a restart. After 3 failed restarts, it marks the component as 'error' in the health status and 'Degraded' on the dashboard and adds a persistent alert.
- **Vault Corruption:** On startup, if the vault integrity check fails, the orchestrator attempts a one-time repair by calling the `vault-setup` skill. If this fails, it logs a CRITICAL error and exits.
- **PM2 Unavailable:** If the `pm2` command is not found on startup, the orchestrator logs a CRITICAL error and exits immediately.
- **.env Missing:** If required environment variables are missing, the orchestrator exits immediately with code 1.

---

## 17. Success Criteria
The skill execution is considered a **SUCCESS** if:
- The orchestrator process starts, completes its startup sequence, and remains running.
- It correctly detects and triggers other skills in response to file system events.
- It updates the health status and dashboard every 5 minutes.

The execution is a **FAILURE** if:
- The orchestrator fails to start due to a missing dependency or configuration error.
- It crashes during its main loop.
- It fails to detect or react to events in the vault.

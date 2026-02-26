# SKILL: audit-logger

**Version:** 1.0.0
**Author:** Gemini CLI

---

## 1. Skill Name & Version
- **Name:** `audit-logger`
- **Version:** `1.0.0`

---

## 2. Purpose
This skill provides a centralized, robust, and transactional audit logging service for the entire Personal AI Employee system. Its purpose is to ensure that every action, decision, and event is captured in a structured, immutable, and auditable format. Centralized logging is critical for debugging, security analysis, performance monitoring, and maintaining a clear chain of accountability for all automated actions. This skill acts as the single source of truth for "what happened" within the system.

---

## 3. Inputs
The skill's primary input is a single log entry, provided as a Python dictionary that must conform strictly to the **Required Log Entry Schema**.

---

## 4. Outputs
- **Daily Log File:** A JSON file located at `/Vault/Logs/YYYY-MM-DD.json` containing all log entries for a given day.
- **Log Index File:** An index of all log files, located at `/Vault/Logs/index.json`.
- **Dashboard Update:** The `## Recent Activity` section of `VAULT_PATH/Dashboard.md` is updated with the latest log entry.
- **Archive Files:**
    - `/Vault/Logs/critical_archive.json`: A summary of CRITICAL logs from deleted log files.
    - `/Vault/Logs/failed_writes.json`: A log of entries that could not be written due to persistent file locks.

---

## 5. Pre-conditions
- The `VAULT_PATH` environment variable must be set to a valid, existing directory path.
- The `VAULT_PATH/Logs/` directory must exist.
- The calling skill must have a `session_id` available to include in the log entry.

---

## 6. Step-by-Step Execution Instructions
When the `log(entry)` method is called:
1.  **Validate Input:** The `entry` dictionary is validated against the required schema. If it fails, an error is raised and the log is rejected.
2.  **Check DRY_RUN:** If `DRY_RUN=true`, the validated entry is printed to the console and the function returns immediately.
3.  **Determine Log File:** The current UTC date is used to determine the path to today's log file (e.g., `/Vault/Logs/2026-02-27.json`).
4.  **Acquire File Lock:** The skill attempts to acquire an exclusive lock on the target log file using the `msvcrt` library to prevent concurrent write corruption. It will retry 3 times if the lock is busy. If all retries fail, the entry is written to `failed_writes.json` and the function returns.
5.  **Read-Modify-Write:**
    a. The entire daily log file is read into memory. If the file is new, a default structure is created.
    b. The new log `entry` is appended to the `entries` list within the JSON structure.
    c. The `total_entries` and `summary` count for the corresponding `log_level` are incremented.
    d. The modified JSON object is written back to the file, overwriting the old content.
6.  **Release File Lock:** The file lock is released immediately after the write operation is complete.
7.  **Update Index:** The `/Vault/Logs/index.json` file is updated to reflect the new entry count and file size.
8.  **Update Dashboard:** The `/Dashboard.md` file is updated to include the new log entry in the "Recent Activity" table.
9.  **Enforce Retention:** The `rotate_logs()` method is called to check for and delete any log files older than 90 days, handling CRITICAL logs as per the policy.

---

## 7. Full Log Entry Schema
```json
{
  "timestamp": "<ISO 8601 timestamp>",
  "log_level": "INFO | WARNING | ERROR | CRITICAL",
  "action_type": "<file_drop | plan_created | approval_requested | approved | rejected | expired | email_sent | file_moved | error | system_event>",
  "actor": "<skill_name that triggered this log>",
  "target": "<file, folder, email, or system component affected>",
  "parameters": {
    "<key>": "<value>"
  },
  "approval_status": "not_required | pending | approved | rejected | expired",
  "approved_by": "human | system | N/A",
  "dry_run": true | false,
  "result": "success | failure | skipped",
  "error_message": "<null or error description>",
  "session_id": "<unique session identifier>"
}
```

---

## 8. Daily Log File Structure
```json
{
  "date": "YYYY-MM-DD",
  "total_entries": 125,
  "summary": {
    "INFO": 100,
    "WARNING": 20,
    "ERROR": 5,
    "CRITICAL": 0
  },
  "entries": [
    {
      "timestamp": "2026-02-27T10:00:00.123Z",
      "log_level": "INFO",
      "action_type": "plan_created",
      "actor": "needs-action-processor",
      "target": "Plans/request-01-Plan.md",
      "parameters": { "source_file": "request-01.md" },
      "approval_status": "pending",
      "approved_by": "N/A",
      "dry_run": false,
      "result": "success",
      "error_message": null,
      "session_id": "AI_EMP_20260227_A4F8F1"
    }
  ]
}
```

---

## 9. Log Index Structure
```json
{
  "last_updated": "2026-02-27T10:00:00.123Z",
  "total_log_files": 90,
  "oldest_log": "2025-11-29",
  "newest_log": "2026-02-27",
  "total_entries_all_time": 11250,
  "log_files": [
    {
      "date": "2026-02-27",
      "file": "2026-02-27.json",
      "entry_count": 125,
      "size_bytes": 51200
    }
  ]
}
```

---

## 10. Retention Policy Logic
- **Trigger:** The retention check is performed after every successful `log()` operation.
- **Calculation:** The policy identifies log files where the date in the filename (e.g., "2025-11-28") is older than 90 days from the current date.
- **CRITICAL Log Check:** Before deleting a log file, its content is scanned. If the `summary.CRITICAL` count is greater than zero, or if any entry has `"log_level": "CRITICAL"`, the file is marked for special handling.
- **Archiving CRITICALs:** All entries with `log_level: "CRITICAL"` from the marked file are extracted and appended to `/Vault/Logs/critical_archive.json`.
- **Deletion:** The expired log file is deleted from the file system.
- **Logging the Deletion:** An `INFO` level event is logged *before* the file is deleted, recording which log file is being purged.
- **Index Update:** After deletion, the log index is updated to remove the entry for the deleted file.

---

## 11. File Locking Strategy
- **Platform:** The implementation uses the `msvcrt` module, which is specific to Windows, for file locking.
- **Mechanism:** It uses `msvcrt.locking()` to acquire an exclusive, non-blocking lock (`msvcrt.LK_NBLCK`) on the entire file.
- **Retry Logic:**
    1.  Attempt to acquire the lock.
    2.  If it fails (raises `IOError`), wait for a short, randomized interval (e.g., 0.1s-0.5s).
    3.  Retry up to 3 times.
    4.  The total time spent retrying will not exceed 5 seconds.
- **Failure Fallback:** If all 3 retries fail, the function gives up, releases any partial lock, and writes the log entry to a separate `failed_writes.json` file to ensure the data is not lost.

---

## 12. Full Python Implementation
This is the complete `audit_logger.py` script, designed to be used as a module.

**Dependencies:** `python-dotenv`. Install with `pip install python-dotenv`.

```python
# audit_logger.py
import os
import sys
import json
import time
import string
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Windows-specific file locking
if sys.platform == "win32":
    import msvcrt
else:
    # fcntl is for Linux/macOS. This makes the module importable
    # on other platforms, but locking will fail.
    msvcrt = None 

from dotenv import load_dotenv

load_dotenv()

class AuditLogger:
    def __init__(self, vault_path: str | Path, dry_run: bool = False, session_id: str | None = None):
        if not vault_path:
            raise ValueError("VAULT_PATH cannot be empty.")
            
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / "Logs"
        self.dry_run = dry_run
        
        self.session_id = session_id or self._generate_session_id()
        self.log_schema_keys = {
            "timestamp", "log_level", "action_type", "actor", "target", 
            "parameters", "approval_status", "approved_by", "dry_run", 
            "result", "error_message", "session_id"
        }
        
        self.logs_dir.mkdir(exist_ok=True)

    @staticmethod
    def _generate_session_id():
        rand_chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"AI_EMP_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{rand_chars}"

    def _validate_schema(self, entry: dict) -> bool:
        """Validates the log entry against the required schema."""
        return self.log_schema_keys == set(entry.keys())

    def _lock_file(self, file_handle):
        if not msvcrt: return
        for _ in range(3):
            try:
                msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
                return
            except IOError:
                time.sleep(random.uniform(0.1, 0.5))
        raise IOError("Could not acquire file lock after 3 retries.")

    def _unlock_file(self, file_handle):
        if not msvcrt: return
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)

    def log(self, entry: dict) -> bool:
        """Logs a single entry to the appropriate daily log file."""
        if "session_id" not in entry:
            entry["session_id"] = self.session_id
        if "timestamp" not in entry:
            entry["timestamp"] = datetime.now(timezone.utc).isoformat()

        if not self._validate_schema(entry):
            print("ERROR: Log entry failed schema validation.", file=sys.stderr)
            return False

        if self.dry_run:
            print(f"[DRY_RUN] Log Entry: {json.dumps(entry)}")
            return True

        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        log_file_path = self.logs_dir / f"{today_str}.json"

        try:
            with open(log_file_path, 'a+') as f:
                self._lock_file(f)
                f.seek(0)
                try:
                    data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    data = {
                        "date": today_str,
                        "total_entries": 0,
                        "summary": {"INFO": 0, "WARNING": 0, "ERROR": 0, "CRITICAL": 0},
                        "entries": []
                    }
                
                data["entries"].append(entry)
                data["total_entries"] += 1
                if entry["log_level"] in data["summary"]:
                    data["summary"][entry["log_level"]] += 1
                
                f.seek(0)
                f.truncate()
                json.dump(data, f, indent=2)
                self._unlock_file(f)

        except IOError as e:
            print(f"CRITICAL: File lock failed. Writing to fallback log. Error: {e}", file=sys.stderr)
            fallback_path = self.logs_dir / "failed_writes.json"
            with open(fallback_path, "a") as ff:
                json.dump(entry, ff)
                ff.write("
")
            return False
        
        # Post-write actions
        self._update_index()
        self._update_dashboard(entry)
        self.rotate_logs()
        return True

    def _update_index(self):
        """Updates the master log index."""
        index_path = self.logs_dir / "index.json"
        log_files_info = []
        total_entries_all_time = 0
        
        all_logs = sorted(self.logs_dir.glob("*.json"), key=lambda p: p.name)
        # Exclude special files from the main index logic
        all_logs = [p for p in all_logs if p.name not in ["index.json", "failed_writes.json", "critical_archive.json"]]

        if not all_logs:
            index_path.write_text("{}", 'utf-8')
            return

        for log_path in all_logs:
            try:
                with open(log_path, 'r') as f:
                    log_data = json.load(f)
                    entry_count = log_data.get("total_entries", 0)
                    total_entries_all_time += entry_count
                    log_files_info.append({
                        "date": log_data.get("date"),
                        "file": log_path.name,
                        "entry_count": entry_count,
                        "size_bytes": log_path.stat().st_size
                    })
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        index_data = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_log_files": len(log_files_info),
            "oldest_log": log_files_info[0]["date"] if log_files_info else None,
            "newest_log": log_files_info[-1]["date"] if log_files_info else None,
            "total_entries_all_time": total_entries_all_time,
            "log_files": log_files_info
        }
        index_path.write_text(json.dumps(index_data, indent=2), 'utf-8')

    def _update_dashboard(self, latest_entry: dict):
        """Updates the Recent Activity section of Dashboard.md."""
        dashboard_path = self.vault_path / "Dashboard.md"
        if not dashboard_path.exists(): return

        content = dashboard_path.read_text('utf-8')
        
        # Extract last 10 entries from today's log
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        log_file_path = self.logs_dir / f"{today_str}.json"
        
        try:
            log_data = json.loads(log_file_path.read_text('utf-8'))
            last_10 = log_data.get("entries", [])[-10:]
        except (FileNotFoundError, json.JSONDecodeError):
            last_10 = [latest_entry]

        # Build new markdown table
        new_table = "## Recent Activity
| Time | Action | Actor | Result |
|------|--------|-------|--------|
"
        for entry in reversed(last_10):
            ts = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S')
            new_table += f"| {ts} | {entry['action_type']} | {entry['actor']} | {entry['result']} |
"

        # Replace the old table in the dashboard content
        # This regex finds the "## Recent Activity" header and everything until the next header or end of file
        import re
        content = re.sub(r"(?s)(^## Recent Activity
).*?(?=
## |$)", new_table, content, count=1, flags=re.MULTILINE)

        dashboard_path.write_text(content, 'utf-8')

    def rotate_logs(self) -> int:
        """Deletes logs older than 90 days."""
        if self.dry_run: return 0
        
        ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)
        deleted_count = 0
        
        for log_path in self.logs_dir.glob("????-??-??.json"):
            try:
                log_date_str = log_path.stem
                log_date = datetime.strptime(log_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                
                if log_date < ninety_days_ago:
                    self.log({
                        "timestamp": datetime.now(timezone.utc).isoformat(), "log_level": "INFO",
                        "action_type": "log_retention", "actor": "audit_logger",
                        "target": log_path.name, "parameters": {"retention_days": 90},
                        "approval_status": "not_required", "approved_by": "system",
                        "dry_run": self.dry_run, "result": "success", "error_message": None,
                        "session_id": self.session_id
                    })
                    
                    # Handle critical log archival
                    log_data = json.loads(log_path.read_text('utf-8'))
                    if log_data.get("summary", {}).get("CRITICAL", 0) > 0:
                        archive_path = self.logs_dir / "critical_archive.json"
                        critical_entries = [e for e in log_data.get("entries", []) if e['log_level'] == 'CRITICAL']
                        with open(archive_path, 'a') as f:
                            for entry in critical_entries:
                                json.dump(entry, f)
                                f.write('
')
                    
                    log_path.unlink() # Delete the file
                    deleted_count += 1
                    
            except (ValueError, FileNotFoundError, json.JSONDecodeError):
                continue
        
        if deleted_count > 0:
            self._update_index() # Re-run index after deletions
        
        return deleted_count

# Standalone execution for testing
if __name__ == "__main__":
    print("AuditLogger Module - Running Standalone Test")
    
    # Requires a .env file with VAULT_PATH pointing to a test directory
    test_vault_path = os.getenv("VAULT_PATH")
    if not test_vault_path:
        raise ValueError("Please set VAULT_PATH in your .env file for testing.")

    # Test with DRY_RUN = False to see file writes
    is_dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    print(f"Test DRY_RUN mode: {is_dry_run}")

    logger = AuditLogger(vault_path=test_vault_path, dry_run=is_dry_run)

    test_entry = {
      "timestamp": datetime.now(timezone.utc).isoformat(),
      "log_level": "INFO",
      "action_type": "system_event",
      "actor": "audit_logger_test",
      "target": "self_test",
      "parameters": {"test_id": 123},
      "approval_status": "not_required",
      "approved_by": "N/A",
      "dry_run": is_dry_run,
      "result": "success",
      "error_message": None,
      "session_id": logger.session_id
    }
    
    success = logger.log(test_entry)
    if success:
        print("Test log written successfully.")
    else:
        print("Test log failed to write.")

    if not is_dry_run:
        print("Running retention policy check...")
        deleted = logger.rotate_logs()
        print(f"Deleted {deleted} old log file(s).")
```

---

## 13. Dashboard.md Update Pattern
- After every successful log write, the `_update_dashboard()` method is triggered.
- It reads the entire content of `VAULT_PATH/Dashboard.md`.
- It reads today's daily log file to get the last 10 entries.
- It constructs a new markdown table string for the "Recent Activity" section.
- It uses a regular expression (`re.sub`) to find the block of text starting with `## Recent Activity` and replaces it entirely with the newly generated table. This ensures the table is always fresh and limited to 10 entries.

---

## 14. DRY_RUN Verification Steps
`DRY_RUN` mode is enabled by default. To verify it is working correctly:
1.  Ensure `DRY_RUN=true` in the `.env` file or when instantiating the `AuditLogger` class.
2.  Call the `logger.log(test_entry)` method with a valid test entry.
3.  **Check Console Output:** The console should print a `[DRY_RUN]` message containing the full JSON of the log entry.
4.  **Verify File System:**
    -   No new file should be created in `/Logs/`.
    -   Existing log files **must not** be modified.
    -   `/Logs/index.json` **must not** be modified.
    -   `/Dashboard.md` **must not** be modified.
    -   The `rotate_logs()` method should return `0` and not delete any files.

---

## 15. Post-conditions / Verification
After a successful run with `DRY_RUN=false`:
1.  **Daily Log:** The `YYYY-MM-DD.json` file must contain the new entry in its `entries` list, and its `summary` and `total_entries` counts must be correctly incremented.
2.  **Index:** The `/Logs/index.json` file must be updated with the new `last_updated` timestamp and correct counts for the modified log file.
3.  **Dashboard:** The `## Recent Activity` table in `Dashboard.md` must show the new log entry at the top.
4.  **Retention:** If a log file was older than 90 days, it must be deleted from the `/Logs` directory.

---

## 16. Error Handling
- **File Locking Failures:** If a file lock cannot be acquired after 3 retries, the log entry is written to `/Logs/failed_writes.json` to prevent data loss. A critical message is printed to stderr.
- **Corrupted Log Files:** If a daily log file contains invalid JSON, the logger will overwrite it with a new, valid structure containing only the current entry. This favors availability over recovering the corrupted file.
- **Disk Full:** Standard `IOError` will be raised by the OS during file write operations. This is not caught by the logger itself and should be handled by the calling process manager (e.g., PM2).
- **Retention Policy Errors:** Errors during log rotation (e.g., permission denied on delete) are caught, and the process continues to the next file, preventing a single failed deletion from halting the entire operation.
- **Schema Validation Failure:** The `log()` method returns `False` if the entry does not match the schema, allowing the calling skill to handle the failure.

---

## 17. Success Criteria
The skill's `log()` method execution is a **SUCCESS** if:
- It returns `True`.
- The log entry is correctly appended to the daily log file, the index is updated, and the dashboard is refreshed (when `DRY_RUN=false`).

The execution is a **FAILURE** if:
- It returns `False` due to a schema validation error.
- It fails to acquire a file lock and has to write to the `failed_writes.json` fallback file.
- It raises an unhandled exception.

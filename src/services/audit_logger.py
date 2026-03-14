import json
import logging
from datetime import datetime, date, timedelta
from pathlib import Path
from src.config.settings import Config
from src.lib.locking import FileLockManager

logger = logging.getLogger(__name__)

class AuditLogger:
    """Manages JSON-based audit logging for agent actions."""

    @staticmethod
    def get_log_path(log_date: date = None) -> Path:
        """Returns the path to the audit log file for a specific date."""
        if log_date is None:
            log_date = date.today()
        return Config.LOGS_DIR / f"{log_date.isoformat()}.json"

    @classmethod
    def log(cls, action_type: str, actor: str, target: str, parameters: dict = None, 
            status: str = "success", log_level: str = "INFO", approval_status: str = "N/A",
            approved_by: str = "N/A", result: str = "N/A", error_message: str = "N/A",
            session_id: str = "N/A"):
        """Appends a new entry to the daily audit log using the required schema."""
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "log_level": log_level,
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters or {},
            "status": status,
            "approval_status": approval_status,
            "approved_by": approved_by,
            "dry_run": Config.DRY_RUN,
            "result": result,
            "error_message": error_message,
            "session_id": session_id
        }

        log_path = cls.get_log_path()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with FileLockManager.with_lock(log_path):
            data = []
            if log_path.exists():
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON from {log_path}, starting new log.")
            
            data.append(entry)
            
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        # Update index.json
        cls._update_index(entry)
        
        # Update Dashboard.md
        cls._update_dashboard(entry)

    @classmethod
    def _update_index(cls, entry: dict):
        """Updates the central index.json with the latest log entry."""
        index_path = Config.LOGS_DIR / "index.json"
        with FileLockManager.with_lock(index_path):
            index_data = []
            if index_path.exists():
                try:
                    with open(index_path, 'r', encoding='utf-8') as f:
                        index_data = json.load(f)
                except json.JSONDecodeError:
                    pass
            
            # Keep only last 100 entries in index
            index_data.insert(0, entry)
            index_data = index_data[:100]
            
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2)

    @classmethod
    def _update_dashboard(cls, entry: dict):
        """Updates the Recent Activity section in Dashboard.md."""
        dashboard_path = Config.VAULT_ROOT / "Dashboard.md"
        if not dashboard_path.exists():
            return

        with FileLockManager.with_lock(dashboard_path):
            try:
                with open(dashboard_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                activity_header = "## Recent Activity"
                new_activity = f"- [{entry['timestamp']}] {entry['actor']} -> {entry['action_type']} on {entry['target']} ({entry['status']})"
                
                if activity_header in content:
                    parts = content.split(activity_header)
                    # Insert new activity at the top of the section
                    lines = parts[1].strip().split('\n')
                    # Keep last 10 activities
                    filtered_lines = [l for l in lines if l.strip().startswith('-')]
                    filtered_lines.insert(0, new_activity)
                    parts[1] = "\n" + "\n".join(filtered_lines[:10]) + "\n"
                    new_content = activity_header.join(parts)
                else:
                    new_content = content + f"\n\n{activity_header}\n{new_activity}\n"

                with open(dashboard_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            except Exception as e:
                logger.error(f"Failed to update Dashboard.md: {e}")

    @classmethod
    def rotate_logs(cls, retention_days: int = 90):
        """Deletes audit logs older than the retention period."""
        if Config.DRY_RUN:
            logger.info("[DRY_RUN] Would rotate logs (retention: %d days)", retention_days)
            return

        cutoff_date = date.today() - timedelta(days=retention_days)
        
        if not Config.LOGS_DIR.exists():
            return

        for log_file in Config.LOGS_DIR.glob("*.json"):
            try:
                # Expecting filename format YYYY-MM-DD.json
                file_date_str = log_file.stem
                file_date = date.fromisoformat(file_date_str)
                
                if file_date < cutoff_date:
                    logger.info(f"Rotating (deleting) old log file: {log_file.name}")
                    log_file.unlink()
                    # Also remove the lock file if it exists
                    lock_file = log_file.with_suffix(".json.lock")
                    if lock_file.exists():
                        lock_file.unlink()
            except (ValueError, OSError) as e:
                logger.warning(f"Skipping file {log_file.name} during rotation: {e}")

if __name__ == "__main__":
    # Test logging
    AuditLogger.log(
        action_type="test_entry",
        actor="audit-logger-test",
        target="audit-log-file",
        parameters={"test": True},
        status="success"
    )
    print(f"Test entry written to {AuditLogger.get_log_path()}")

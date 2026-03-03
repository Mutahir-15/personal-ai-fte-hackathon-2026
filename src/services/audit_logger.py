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
    def log(cls, skill: str, action: str, status: str, input_data=None, output_data=None, metadata=None):
        """Appends a new entry to the daily audit log."""
        
        # Include global DRY_RUN status in metadata for transparency
        metadata = metadata or {}
        if "dry_run" not in metadata:
            metadata["dry_run"] = Config.DRY_RUN

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "agent_id": "gemini-cli-1",  # Fixed for Bronze tier
            "skill": skill,
            "action": action,
            "status": status,
            "input": input_data,
            "output": output_data,
            "metadata": metadata
        }

        log_path = cls.get_log_path()
        
        # Ensure directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Use file lock for safe concurrent writes
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
        skill="audit-logger",
        action="test_entry",
        status="success",
        metadata={"test": True}
    )
    print(f"Test entry written to {AuditLogger.get_log_path()}")

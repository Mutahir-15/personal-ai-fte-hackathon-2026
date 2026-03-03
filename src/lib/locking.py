from filelock import FileLock
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FileLockManager:
    """Manages file-based locks for safe concurrent access to vault files."""
    
    @staticmethod
    def get_lock(file_path: str | Path, timeout: int = 10) -> FileLock:
        """
        Returns a FileLock instance for the given file path.
        Appends .lock to the original path.
        """
        lock_path = Path(file_path).with_suffix(Path(file_path).suffix + ".lock")
        return FileLock(lock_path, timeout=timeout)

    @classmethod
    def with_lock(cls, file_path: str | Path, timeout: int = 10):
        """
        Context manager helper for locking a file.
        Example:
            with FileLockManager.with_lock("audit.json"):
                # do work
        """
        return cls.get_lock(file_path, timeout)

import pytest
from pathlib import Path
from src.lib.locking import FileLockManager
from filelock import Timeout

def test_file_lock_manager_get_lock(tmp_path):
    test_file = tmp_path / "test.txt"
    lock = FileLockManager.get_lock(test_file)
    assert lock.lock_file == str(tmp_path / "test.txt.lock")

def test_file_lock_manager_with_lock(tmp_path):
    test_file = tmp_path / "test.txt"
    with FileLockManager.with_lock(test_file) as lock:
        assert lock.is_locked
    assert not lock.is_locked

def test_file_lock_concurrent_access(tmp_path):
    test_file = tmp_path / "test.txt"
    
    # First lock
    with FileLockManager.with_lock(test_file) as lock1:
        assert lock1.is_locked
        
        # Try to get second lock on same file, should fail on timeout
        with pytest.raises(Timeout):
            with FileLockManager.with_lock(test_file, timeout=1) as lock2:
                pass

import pytest
import time
import shutil
from pathlib import Path
from src.services.filesystem_watcher import FilesystemWatcher
from src.config.settings import Config

@pytest.fixture
def clean_test_env():
    """Setup and cleanup test directories."""
    # Ensure directories exist
    Config.VAULT_ROOT.mkdir(parents=True, exist_ok=True)
    Config.DROP_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
    Config.NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)
    Config.STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Clear state file if exists
    state_file = Config.STATE_DIR / "processed_files.json"
    if state_file.exists():
        state_file.unlink()
        
    yield
    
    # Optional: cleanup (commented out to preserve logs/state for inspection if needed)
    # shutil.rmtree(Config.VAULT_ROOT)

def test_filesystem_watcher_integration(clean_test_env, monkeypatch):
    """Verifies that the watcher detects and processes a new file."""
    # Force DRY_RUN=false for integration test
    monkeypatch.setattr(Config, "DRY_RUN", False)
    
    watcher = FilesystemWatcher()
    watcher.start()
    
    try:
        # 1. Create a test file
        test_filename = f"test_{int(time.time())}.txt"
        test_file_path = Config.DROP_FOLDER_PATH / test_filename
        with open(test_file_path, "w", encoding='utf-8') as f:
            f.write("Integration test file.")
            
        # 2. Wait for detection
        time.sleep(5)
        
        # 3. Verify processing
        found_md = False
        found_copy = False
        for item in Config.NEEDS_ACTION_DIR.iterdir():
            if item.is_file() and test_filename in item.name:
                if item.suffix == ".md":
                    found_md = True
                else:
                    found_copy = True
                    
        assert found_md, "Metadata file not created"
        assert found_copy, "Original file not copied"
        
    finally:
        watcher.stop()

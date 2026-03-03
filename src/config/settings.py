import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Central configuration management for the Bronze Vault agent."""
    
    DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
    VAULT_ROOT = Path(os.getenv("VAULT_ROOT", "C:/Users/ADMINS/Obsidian/Agent_Vault"))
    DROP_FOLDER_PATH = Path(os.getenv("DROP_FOLDER_PATH", "C:/Users/ADMINS/Desktop/AI_Drop"))
    
    # Path derived from VAULT_ROOT
    LOGS_DIR = VAULT_ROOT / "Logs"
    STATE_DIR = VAULT_ROOT / ".watcher_state"
    NEEDS_ACTION_DIR = VAULT_ROOT / "Needs_Action"
    PENDING_APPROVAL_DIR = VAULT_ROOT / "Pending_Approval"
    APPROVED_DIR = VAULT_ROOT / "Approved"

    @classmethod
    def validate(cls):
        """Ensures critical configuration is present."""
        if not cls.VAULT_ROOT:
            raise ValueError("VAULT_ROOT environment variable is not set.")
        return True

if __name__ == "__main__":
    print(f"DRY_RUN: {Config.DRY_RUN}")
    print(f"VAULT_ROOT: {Config.VAULT_ROOT}")

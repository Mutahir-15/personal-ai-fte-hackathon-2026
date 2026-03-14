import os
import shutil
from pathlib import Path
import logging
from src.config.settings import Config
from src.lib.base_action import BaseAction

class VaultInitializer(BaseAction):
    """Initializes the Obsidian vault structure and seed files."""
    
    FOLDERS = [
        "Needs_Action",
        "Plans",
        "Done",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Logs",
        "Accounting",
        "Briefings",
        ".watcher_state"
    ]

    SEED_FILES = {
        "Dashboard.md": "Dashboard.md",
        "Company_Handbook.md": "Company_Handbook.md",
        "Business_Goals.md": "Business_Goals.md",
        "PM2_Cheatsheet.md": "PM2_Cheatsheet.md"
    }

    STATE_FILES = {
        "processed_files.json": "[]",
        "current_session.json": "{}",
        "approved_actions.json": "{}",
        "orchestrator_health.json": "{}"
    }

    def execute(self):
        """Creates the vault structure and populates seed files."""
        vault_root = Config.VAULT_ROOT
        self.logger.info(f"Initializing vault at: {vault_root}")

        # 1. Create Folders
        for folder in self.FOLDERS:
            folder_path = vault_root / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Ensured folder exists: {folder}")

        # 2. Create Seed Files
        template_dir = Path(__file__).parent.parent / "templates"
        for seed_name, template_name in self.SEED_FILES.items():
            target_path = vault_root / seed_name
            if not target_path.exists():
                template_path = template_dir / template_name
                if template_path.exists():
                    shutil.copy(template_path, target_path)
                    self.logger.info(f"Created seed file: {seed_name}")
                else:
                    # Fallback if template missing
                    with open(target_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {seed_name.replace('.md', '').replace('_', ' ')}\n")
                    self.logger.warning(f"Template {template_name} not found. Created empty seed file: {seed_name}")
            else:
                self.logger.info(f"Seed file already exists: {seed_name}")

        # 3. Create State Files
        state_dir = vault_root / ".watcher_state"
        for state_name, initial_content in self.STATE_FILES.items():
            target_path = state_dir / state_name
            if not target_path.exists():
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(initial_content)
                self.logger.info(f"Created state file: {state_name}")
            else:
                self.logger.info(f"State file already exists: {state_name}")

        return {"status": "success", "message": f"Vault initialized at {vault_root}"}

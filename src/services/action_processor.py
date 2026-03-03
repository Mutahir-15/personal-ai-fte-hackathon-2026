import shutil
import json
from pathlib import Path
from datetime import datetime
from src.lib.base_action import BaseAction
from src.config.settings import Config
from src.services.audit_logger import AuditLogger
from src.lib.locking import FileLockManager

class NeedsActionProcessor(BaseAction):
    """Processes a detected file by wrapping it in markdown metadata and moving it to /Needs_Action/."""

    def __init__(self, dry_run: bool = None):
        super().__init__(dry_run)
        self.state_file = Config.STATE_DIR / "processed_files.json"
        
        # Ensure state directory exists
        Config.STATE_DIR.mkdir(parents=True, exist_ok=True)
        Config.NEEDS_ACTION_DIR.mkdir(parents=True, exist_ok=True)

    def _get_processed_files(self) -> dict:
        """Reads the processed files state from JSON."""
        if not self.state_file.exists():
            return {"files": {}}
        
        with FileLockManager.with_lock(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                self.logger.error(f"Failed to read state file: {self.state_file}. Returning empty state.")
                return {"files": {}}

    def _update_processed_files(self, file_path: Path):
        """Adds a file to the processed files list in the state file."""
        if self.dry_run:
            return

        state = self._get_processed_files()
        
        # Add entry per data-model.md
        state["files"][str(file_path.absolute())] = {
            "hash": "sha256_placeholder", # For Bronze, we use path as unique key
            "detected_at": datetime.now().isoformat(),
            "processed_at": datetime.now().isoformat()
        }

        with FileLockManager.with_lock(self.state_file):
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)

    def execute(self, source_path: Path):
        """Moves file to Needs_Action and creates metadata."""
        source_path = Path(source_path)
        if not source_path.exists():
            self.logger.error(f"Source path does not exist: {source_path}")
            return {"status": "error", "message": "File not found"}

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        sanitized_name = source_path.name.replace(" ", "_")
        dest_filename = f"{timestamp}_{sanitized_name}"
        dest_path = Config.NEEDS_ACTION_DIR / dest_filename
        metadata_path = Config.NEEDS_ACTION_DIR / f"FILE_{sanitized_name}_{timestamp}.md"

        self.logger.info(f"Processing file: {source_path.name}")

        try:
            # 1. Copy file to Needs_Action
            shutil.copy2(source_path, dest_path)
            
            # 2. Create metadata file
            metadata_content = f"""---
type: file_drop
original_name: {source_path.name}
original_path: {str(source_path.absolute())}
size_bytes: {source_path.stat().st_size}
detected_at: {datetime.now().isoformat()}
status: pending
processed: false
---

## Summary
New file detected and queued for processing.

## Suggested Actions
- [ ] Review file contents
- [ ] Determine required action
- [ ] Move to /Done when complete
"""
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write(metadata_content)

            # 3. Update state
            self._update_processed_files(source_path)

            # 4. Log action
            AuditLogger.log(
                skill="needs-action-processor",
                action="process_file",
                status="success",
                input_data={"source": str(source_path)},
                output_data={"dest": str(dest_path), "metadata": str(metadata_path)},
                metadata={"file_size": source_path.stat().st_size}
            )

            return {
                "status": "success",
                "dest_path": str(dest_path),
                "metadata_path": str(metadata_path)
            }

        except Exception as e:
            self.logger.error(f"Failed to process file {source_path}: {e}")
            AuditLogger.log(
                skill="needs-action-processor",
                action="process_file",
                status="error",
                input_data={"source": str(source_path)},
                metadata={"error": str(e)}
            )
            return {"status": "error", "message": str(e)}

import re
import time
import logging
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from src.lib.base_watcher import BaseWatcher
from src.config.settings import Config
from src.lib.approval_manager import ApprovalManager
from src.services.audit_logger import AuditLogger

logger = logging.getLogger(__name__)

class ApprovalHandler(FileSystemEventHandler):
    """Handles file system events in the Approved folder."""
    
    def __init__(self, manager: ApprovalManager, logger):
        self.manager = manager
        self.logger = logger

    def on_moved(self, event):
        """Detects files moved into the Approved folder."""
        if event.is_directory:
            return
        
        dest_path = Path(event.dest_path)
        self.logger.info(f"File moved to Approved: {dest_path.name}")
        self._process_approval(dest_path)

    def on_created(self, event):
        """Detects files created directly in the Approved folder."""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        self.logger.info(f"File created in Approved: {file_path.name}")
        self._process_approval(file_path)

    def _process_approval(self, file_path: Path):
        """Parses the approval file and updates the queue."""
        # Wait for file to be fully written/available
        time.sleep(1)
        
        if not file_path.exists() or file_path.suffix != ".md":
            return

        # Extract Request ID from filename (e.g., REQ_SKILL_TIMESTAMP.md)
        match = re.search(r"(REQ_.+)_\d+\.md", file_path.name)
        if not match:
            # Fallback for ID without trailing timestamp
            match = re.search(r"(REQ_.+)\.md", file_path.name)
        
        if not match:
            self.logger.warning(f"Could not extract Request ID from filename: {file_path.name}")
            return

        request_id = match.group(1)
        
        # If the ID already contains the timestamp, use it as is
        # The goal is to match whatever is in the 'pending' queue.
        # Let's try to be smart about it.
        request_id = file_path.stem # Just use the filename without extension as ID

        self.logger.info(f"Processing approval for Request ID: {request_id}")

        # Mark as approved in the manager
        action_details = self.manager.mark_approved(request_id)
        
        if action_details:
            self.logger.info(f"Approval confirmed for {action_details['skill']} - {action_details['action']}")
            
            # Bronze Execution: If it's a FILE_DROP, move source to Done
            if action_details['skill'] == "FILE_DROP":
                self._execute_file_drop_completion(action_details)

            AuditLogger.log(
                action_type="confirm_approval",
                actor="approval-watcher",
                target=request_id,
                parameters={"file": file_path.name, "skill": action_details['skill'], "action": action_details['action']},
                status="success",
                result=f"Approval confirmed and executed for {action_details['skill']}"
            )
            
            # Clean up: Delete approval file from Approved folder
            if not Config.DRY_RUN:
                try:
                    file_path.unlink()
                    self.logger.info(f"Cleaned up approval file: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to delete approval file: {e}")
        else:
            self.logger.warning(f"No pending request found in manager for ID: {request_id}")
            # Log current pending keys to help debug
            queue = self.manager._get_queue()
            self.logger.info(f"Currently pending: {list(queue.get('pending', {}).keys())}")

    def _execute_file_drop_completion(self, details: dict):
        """Moves source file to /Done/ and updates related metadata."""
        try:
            input_data = details.get("input_data", {})
            source_path = Path(input_data.get("source"))
            dest_path = Path(input_data.get("dest"))
            metadata_path = Path(input_data.get("metadata"))
            plan_path = Path(input_data.get("plan"))
            
            if Config.DRY_RUN:
                self.logger.info(f"[DRY_RUN] Would move {source_path.name} to Done/")
                return

            # 1. Ensure Done directory exists (with year/month subfolders per spec)
            now = datetime.now()
            done_dir = Config.VAULT_ROOT / "Done" / str(now.year) / f"{now.month:02d}"
            done_dir.mkdir(parents=True, exist_ok=True)
            
            # 2. Move original file to Done
            if source_path.exists():
                shutil_dest = done_dir / source_path.name
                import shutil
                shutil.move(str(source_path), str(shutil_dest))
                self.logger.info(f"Moved source file to Done: {shutil_dest}")
            else:
                self.logger.warning(f"Source file not found at {source_path}")

            # 3. Update Plan.md status to 'ready_to_execute' (since it's approved)
            if plan_path.exists():
                content = plan_path.read_text(encoding='utf-8')
                content = content.replace("status: pending_approval", "status: ready_to_execute")
                plan_path.write_text(content, encoding='utf-8')
                self.logger.info(f"Updated plan status: {plan_path.name}")

            # 4. Update health stats
            self._update_health_stats(success=True)
            
        except Exception as e:
            self.logger.error(f"Failed to execute file drop completion: {e}")
            self._update_health_stats(success=False)

    def _update_health_stats(self, success: bool):
        """Updates the orchestrator_health.json file."""
        health_file = Config.STATE_DIR / "orchestrator_health.json"
        try:
            from src.lib.locking import FileLockManager
            import json
            with FileLockManager.with_lock(health_file):
                stats = {"success_count": 0, "failure_count": 0, "last_action": ""}
                if health_file.exists():
                    try:
                        with open(health_file, 'r', encoding='utf-8') as f:
                            stats = json.load(f)
                    except:
                        pass
                
                if success:
                    stats["success_count"] = stats.get("success_count", 0) + 1
                else:
                    stats["failure_count"] = stats.get("failure_count", 0) + 1
                
                stats["last_update"] = datetime.now().isoformat()
                
                with open(health_file, 'w', encoding='utf-8') as f:
                    json.dump(stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update health stats: {e}")


class ApprovalWatcher(BaseWatcher):
    """Monitors the Approved folder for human-authorized actions."""

    def __init__(self, watch_path: str = None, dry_run: bool = None):
        watch_path = watch_path or str(Config.APPROVED_DIR)
        super().__init__(watch_path)
        self.manager = ApprovalManager(dry_run=dry_run)
        
        # Ensure Approved folder exists
        Path(self.watch_path).mkdir(parents=True, exist_ok=True)

    def start(self):
        """Starts the approval observer."""
        event_handler = ApprovalHandler(self.manager, self.logger)
        self.observer.schedule(event_handler, self.watch_path, recursive=False)
        self.observer.start()
        self.logger.info(f"ApprovalWatcher started monitoring: {self.watch_path}")
        
        AuditLogger.log(
            action_type="start_watcher",
            actor="approval-watcher",
            target=str(self.watch_path),
            status="success"
        )
        
        # Initial scan for existing approvals
        self._scan_existing_approvals()

    def stop(self):
        """Stops the approval observer."""
        self.observer.stop()
        self.observer.join()
        self.logger.info("ApprovalWatcher stopped.")

    def _scan_existing_approvals(self):
        """Scans for approval files that were moved while the watcher was offline."""
        self.logger.info("Scanning for existing approvals...")
        approved_path = Path(self.watch_path)
        
        for item in approved_path.iterdir():
            if item.is_file() and item.suffix == ".md":
                self.logger.info(f"Found existing approval file: {item.name}")
                # We reuse the handler's logic
                handler = ApprovalHandler(self.manager, self.logger)
                handler._process_approval(item)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    watcher = ApprovalWatcher()
    watcher.start()
    watcher.run_forever()

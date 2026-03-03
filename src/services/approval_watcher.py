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
        match = re.search(r"(REQ_[A-Z0-9_\-]+_\d+)\.md", file_path.name)
        if not match:
            self.logger.warning(f"Could not extract Request ID from filename: {file_path.name}")
            return

        request_id = match.group(1)
        self.logger.info(f"Processing approval for Request ID: {request_id}")

        # Mark as approved in the manager
        action_details = self.manager.mark_approved(request_id)
        
        if action_details:
            self.logger.info(f"Approval confirmed for {action_details['skill']} - {action_details['action']}")
            
            AuditLogger.log(
                skill="hitl-approval",
                action="confirm_approval",
                status="success",
                input_data={"request_id": request_id, "file": file_path.name},
                output_data={"skill": action_details['skill'], "action": action_details['action']}
            )
        else:
            self.logger.warning(f"No pending request found in manager for ID: {request_id}")
            # Log current pending keys to help debug
            queue = self.manager._get_queue()
            self.logger.info(f"Currently pending: {list(queue.get('pending', {}).keys())}")

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
            skill="hitl-approval",
            action="start_watcher",
            status="success",
            metadata={"watch_path": self.watch_path}
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

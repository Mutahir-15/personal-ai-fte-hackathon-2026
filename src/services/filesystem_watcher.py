import json
import time
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from src.lib.base_watcher import BaseWatcher
from src.config.settings import Config
from src.services.action_processor import NeedsActionProcessor
from src.services.audit_logger import AuditLogger

class FileDropHandler(FileSystemEventHandler):
    """Handles file system events by triggering the NeedsActionProcessor."""
    
    def __init__(self, processor: NeedsActionProcessor, logger):
        self.processor = processor
        self.logger = logger
        self.state_file = Config.STATE_DIR / "processed_files.json"

    def _is_processed(self, file_path: Path) -> bool:
        """Checks if the file has already been processed."""
        if not self.state_file.exists():
            return False
        
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                return str(file_path.absolute()) in state.get("files", {})
        except (json.JSONDecodeError, IOError):
            return False

    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        self.logger.info(f"Detected new file: {file_path.name}")
        
        # Debounce/Wait for file to be fully written
        time.sleep(1)
        
        if not self._is_processed(file_path):
            self.processor.perform(file_path)
        else:
            self.logger.info(f"File already processed: {file_path.name}")

class FilesystemWatcher(BaseWatcher):
    """Monitors a drop folder for new files and triggers processing."""

    def __init__(self, watch_path: str = None):
        watch_path = watch_path or str(Config.DROP_FOLDER_PATH)
        super().__init__(watch_path)
        self.processor = NeedsActionProcessor()
        
        # Ensure drop folder exists
        Path(self.watch_path).mkdir(parents=True, exist_ok=True)

    def start(self):
        """Starts the filesystem observer."""
        event_handler = FileDropHandler(self.processor, self.logger)
        self.observer.schedule(event_handler, self.watch_path, recursive=False)
        self.observer.start()
        self.logger.info(f"FilesystemWatcher started monitoring: {self.watch_path}")
        
        AuditLogger.log(
            action_type="start_watcher",
            actor="filesystem-watcher",
            target=str(self.watch_path),
            status="success"
        )
        
        # Initial scan for existing files
        self._scan_existing_files()

    def stop(self):
        """Stops the filesystem observer."""
        self.observer.stop()
        self.observer.join()
        self.logger.info("FilesystemWatcher stopped.")

    def _scan_existing_files(self):
        """Scans the drop folder for files that were added while the watcher was offline."""
        self.logger.info("Scanning for existing files...")
        drop_path = Path(self.watch_path)
        
        state_file = Config.STATE_DIR / "processed_files.json"
        processed = set()
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    processed = set(state.get("files", {}).keys())
            except (json.JSONDecodeError, IOError):
                pass

        for item in drop_path.iterdir():
            if item.is_file() and str(item.absolute()) not in processed:
                self.logger.info(f"Found unprocessed existing file: {item.name}")
                self.processor.perform(item)

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    watcher = FilesystemWatcher()
    watcher.start()
    watcher.run_forever()

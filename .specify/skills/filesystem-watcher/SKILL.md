# Skill:     (v1.0.0)

## Purpose
Monitors a user-defined "drop folder" for new files, automatically copying them into the Obsidian vault's `/Needs_Action/` directory and creating companion metadata files. This skill streamlines the intake of new information for the Personal AI Employee, ensuring no new files are missed and are properly triaged.

## Inputs
This skill relies on several environment variables for configuration. These should be set in the PM2 ecosystem file or directly in the environment where the Python script is executed.

- `DRY_RUN`: (`true`/`false`, default: `true`). If `true`, the watcher will only log intended actions without performing any file operations or state changes.
- `VAULT_PATH`: (e.g., `C:\\Users\\<YOUR_USERNAME>\\AI_Employee_Vault`). The absolute path to the root of the Obsidian vault.
- `DROP_FOLDER_PATH`: (e.g., `C:\\Users\\<YOUR_USERNAME>\\Desktop\\AI_Drop`). The absolute path to the folder that the watcher will monitor for new files.
- `WATCHER_INTERVAL_SECONDS`: (integer, default: `30`). The polling interval in seconds for checking the drop folder.

## Outputs
- **Files in Obsidian Vault**:
  - `{{VAULT_PATH}}\Needs_Action\<timestamp>_<original_filename>`: A copy or move of the detected file.
  - `{{VAULT_PATH}}\Needs_Action\FILE_<original_filename>_<timestamp>.md`: A Markdown metadata file describing the detected file.
- **Logs**:
  - `{{VAULT_PATH}}\Vault\Logs\YYYY-MM-DD.json`: JSON-formatted log entries for each detection event.
- **State Management**:
  - `{{VAULT_PATH}}\.watcher_state\processed_files.json`: A JSON file tracking already processed files to prevent duplicates across restarts.

## Pre-conditions
- **Operating System**: Windows 10.
- **Python**: Python 3.13+ installed and accessible via `python3` command.
- **PM2**: PM2 (Node.js process manager) installed globally (`npm install -g pm2`).
- **Dependencies**: Python `watchdog` library installed (`pip install watchdog`).
- **Obsidian Vault**: An Obsidian vault must exist at the specified `VAULT_PATH`.
- **Drop Folder**: The `DROP_FOLDER_PATH` must exist and be accessible to the script.
- **Vault Structure**: The following directories will be created if they don't exist: `{{VAULT_PATH}}\Needs_Action`, `{{VAULT_PATH}}\Vault\Logs`, `{{VAULT_PATH}}\.watcher_state`.

## Step-by-Step Execution Instructions
To deploy and run the `filesystem-watcher` skill:

1.  **Create Skill Directory**: Ensure the directory `.specify/skills/filesystem-watcher/` exists.
2.  **Save Python Script**: Save the `filesystem_watcher.py` content (provided below) into the directory: `{{YOUR_PROJECT_ROOT}}\.specify\skills\filesystem-watcher\filesystem_watcher.py`.
3.  **Install Python Dependencies**: Open a PowerShell terminal in your project root and run:
    ```powershell
    pip install watchdog
    ```
4.  **Configure PM2 (optional but recommended)**:
    a.  Create or update your `ecosystem.config.js` file (example provided below) in your project root or a suitable location, ensuring `VAULT_PATH`, `DROP_FOLDER_PATH`, and `WATCHER_INTERVAL_SECONDS` are correctly set for your environment. Remember to replace `<YOUR_USERNAME>` with your actual Windows username.
    b.  Start the PM2 process from the directory where `ecosystem.config.js` is located:
        ```powershell
        pm2 start ecosystem.config.js
        ```
5.  **Manual Start (for testing)**:
    Alternatively, for manual testing without PM2, open a PowerShell terminal and navigate to `{{YOUR_PROJECT_ROOT}}\.specify\skills\filesystem-watcher\`. Then run:
    ```powershell
    $env:DRY_RUN="true" # or "false"
    $env:VAULT_PATH="C:\Users\<YOUR_USERNAME>\AI_Employee_Vault"
    $env:DROP_FOLDER_PATH="C:\Users\<YOUR_USERNAME>\Desktop\AI_Drop"
    $env:WATCHER_INTERVAL_SECONDS="10" # example shorter interval
    python -u filesystem_watcher.py
    ```
    (Note: `python -u` is used to unbuffer output, which is useful for real-time logging in terminals.)
6.  **Verify PM2 Status**: After starting with PM2, check its status:
    ```powershell
    pm2 list
    pm2 logs filesystem-watcher
    ```

## Full Python Implementation
```python
import os
import sys
import time
import json
import shutil
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
import logging

# Configure basic logging for console output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseWatcher(ABC):
    """
    Abstract base class for a watcher pattern.
    Defines the contract for checking updates and creating action files.
    """
    def __init__(self, vault_path: Path, check_interval: int = 30):
        self.vault_path = vault_path
        self.needs_action_path = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        # Ensure base directories exist
        self.needs_action_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Checks for new items to process and returns a list of them.
        """
        pass

    @abstractmethod
    def create_action_file(self, item: Path) -> Path:
        """
        Processes an item and creates a corresponding action/metadata file.
        Returns the path to the created metadata file.
        """
        pass

    def run(self):
        """
        Main loop for the watcher.
        """
        logger.info(f"Starting watcher with interval {self.check_interval} seconds...")
        while True:
            try:
                items = self.check_for_updates()
                if items:
                    logger.info(f"Detected {len(items)} new item(s).")
                for item in items:
                    self.create_action_file(item)
            except Exception as e:
                logger.error(f'Unhandled error in watcher loop: {e}', exc_info=True)
            finally:
                time.sleep(self.check_interval)

class FilesystemWatcher(BaseWatcher):
    """
    Monitors a specified drop folder for new files, processes them,
    and creates metadata files in an Obsidian vault.
    """
    def __init__(self):
        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'
        vault_path_str = os.getenv('VAULT_PATH')
        drop_folder_path_str = os.getenv('DROP_FOLDER_PATH')
        check_interval_str = os.getenv('WATCHER_INTERVAL_SECONDS', '30')

        if not vault_path_str:
            raise ValueError("Environment variable 'VAULT_PATH' is not set.")
        if not drop_folder_path_str:
            raise ValueError("Environment variable 'DROP_FOLDER_PATH' is not set.")

        try:
            check_interval = int(check_interval_str)
        except ValueError:
            raise ValueError(f"Invalid value for WATCHER_INTERVAL_SECONDS: {check_interval_str}. Must be an integer.")

        self.vault_path = Path(vault_path_str)
        self.drop_folder_path = Path(drop_folder_path_str)
        
        # Call base class constructor
        super().__init__(self.vault_path, check_interval)

        # Additional paths specific to FilesystemWatcher
        self.logs_path = self.vault_path / 'Vault' / 'Logs'
        self.watcher_state_path = self.vault_path / '.watcher_state'
        self.processed_files_state_file = self.watcher_state_path / 'processed_files.json'
        
        # Ensure all necessary directories exist
        self.drop_folder_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self.watcher_state_path.mkdir(parents=True, exist_ok=True)

        self.processed_files = self._load_processed_files()
        logger.info(f"Filesystem Watcher initialized. DRY_RUN: {self.dry_run}")
        logger.info(f"Vault Path: {self.vault_path}")
        logger.info(f"Drop Folder Path: {self.drop_folder_path}")
        logger.info(f"Check Interval: {self.check_interval} seconds")
        if self.dry_run:
            logger.warning("DRY_RUN mode is active. No files will be moved/copied, no .md files created, and state will not be saved.")

    def _load_processed_files(self) -> set:
        """Loads the set of processed file paths from state file."""
        if self.processed_files_state_file.exists():
            try:
                with open(self.processed_files_state_file, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except json.JSONDecodeError:
                logger.error(f"Error decoding JSON from {self.processed_files_state_file}. Starting with empty processed files list.", exc_info=True)
                return set()
        return set()

    def _save_processed_files(self):
        """Saves the set of processed file paths to state file."""
        if not self.dry_run:
            try:
                with open(self.processed_files_state_file, 'w', encoding='utf-8') as f:
                    json.dump(list(self.processed_files), f, indent=2)
            except IOError as e:
                logger.error(f"Failed to save processed files state to {self.processed_files_state_file}: {e}", exc_info=True)
        else:
            logger.debug("DRY_RUN: Not saving processed files state.")

    def _log_action(self, event_type: str, message: str, details: dict = None):
        """Appends a log entry to the daily JSON log file."""
        log_file = self.logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "dry_run": self.dry_run,
            "details": details if details else {}
        }
        
        try:
            # Read existing logs, append, and write back
            if log_file.exists():
                with open(log_file, 'r+', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = [] # Start fresh if file is corrupted
                    data.append(log_entry)
                    f.seek(0)
                    json.dump(data, f, indent=2)
                    f.truncate()
            else:
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump([log_entry], f, indent=2)
        except IOError as e:
            logger.error(f"Failed to write log entry to {log_file}: {e}", exc_info=True)

    def check_for_updates(self) -> list:
        """
        Scans the drop folder for new files that haven't been processed yet.
        """
        new_files = []
        try:
            for item in self.drop_folder_path.iterdir():
                if item.is_file() and str(item) not in self.processed_files:
                    new_files.append(item)
                    if not self.dry_run:
                        self.processed_files.add(str(item))
                        self._save_processed_files() # Save state immediately after adding to prevent re-processing on crash
                    else:
                        logger.debug(f"DRY_RUN: Would mark '{item.name}' as processed.")
        except FileNotFoundError:
            logger.error(f"Drop folder not found: {self.drop_folder_path}. Please ensure it exists.", exc_info=True)
        except PermissionError:
            logger.error(f"Permission denied for drop folder: {self.drop_folder_path}. Check folder permissions.", exc_info=True)
        except Exception as e:
            logger.error(f"Error checking for updates in {self.drop_folder_path}: {e}", exc_info=True)
        
        return new_files

    def create_action_file(self, original_file_path: Path) -> Path:
        """
        Copies/moves the detected file and creates a companion markdown metadata file.
        """
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        original_filename = original_file_path.name
        
        # Ensure file name is safe for paths and Obsidian links
        sanitized_filename = original_filename.replace(' ', '_').replace('&', '').replace('/', '_').replace('\\', '_')
        
        # Destination file name will include a timestamp to avoid collisions
        dest_filename = f"{timestamp}_{sanitized_filename}"
        dest_file_path = self.needs_action_path / dest_filename
        
        # Metadata markdown file name
        metadata_md_filename = f"FILE_{original_filename}_{timestamp}.md"
        metadata_md_path = self.needs_action_path / metadata_md_filename

        details = {
            "original_name": original_filename,
            "original_full_path": str(original_file_path),
            "size_bytes": original_file_path.stat().st_size if original_file_path.exists() else 0,
            "detected_at": datetime.now().isoformat(),
            "destination_path": str(dest_file_path),
            "metadata_path": str(metadata_md_path),
        }

        if not self.dry_run:
            try:
                # Copy the file to Needs_Action
                shutil.copy2(original_file_path, dest_file_path)
                logger.info(f"Copied '{original_filename}' to '{dest_file_path}'.")
                
                # Create the metadata .md file
                metadata_content = f"""---
type: file_drop
original_name: {original_filename}
original_path: {original_file_path}
size_bytes: {details['size_bytes']}
detected_at: {details['detected_at']}
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
                with open(metadata_md_path, 'w', encoding='utf-8') as f:
                    f.write(metadata_content)
                logger.info(f"Created metadata file: '{metadata_md_path}'.")

                self._log_action(
                    event_type="file_detected_and_processed",
                    message=f"File '{original_filename}' processed and moved to Needs_Action.",
                    details=details
                )
                return metadata_md_path

            except FileNotFoundError:
                logger.error(f"Original file not found during processing: {original_file_path}", exc_info=True)
            except PermissionError:
                logger.error(f"Permission denied during file operation for '{original_file_path}'. Check permissions on drop folder and vault.", exc_info=True)
            except IOError as e:
                logger.error(f"I/O error during file operation for '{original_file_path}': {e}", exc_info=True)
            except Exception as e:
                logger.error(f"Unexpected error processing file '{original_file_path}': {e}", exc_info=True)
            return Path() # Return an empty path on error
        else:
            logger.info(f"DRY_RUN: Would copy '{original_filename}' to '{dest_file_path}' and create metadata '{metadata_md_path}'.")
            self._log_action(
                event_type="file_detected_dry_run",
                message=f"DRY_RUN: File '{original_filename}' would be processed.",
                details=details
            )
            return metadata_md_path # Return intended path even in dry run

if __name__ == "__main__":
    try:
        watcher = FilesystemWatcher()
        watcher.run()
    except ValueError as ve:
        logger.critical(f"Configuration error: {ve}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Watcher terminated due to unexpected error: {e}", exc_info=True)
        sys.exit(1)
```

## PM2 Configuration
```javascript
// ecosystem.config.js
module.exports = {
  apps : [{
    name   : 'filesystem-watcher',
    script : '.specify/skills/filesystem-watcher/filesystem_watcher.py', // Adjust path if needed
    interpreter: 'python3', // Or 'python' depending on your system's alias
    watch  : false, // PM2 should not restart on file changes for this process
    autorestart: true, // Automatically restart if it crashes
    max_restarts: 10, // Max restarts in a short period
    min_uptime: 5000, // Consider online if it stays up for at least 5 seconds
    restart_delay: 5000, // Delay before restarting
    env: {
      DRY_RUN: 'true', // Set to 'false' to enable actual file operations
      VAULT_PATH: 'C:\\Users\\<YOUR_USERNAME>\\AI_Employee_Vault',
      DROP_FOLDER_PATH: 'C:\\Users\\<YOUR_USERNAME>\\Desktop\\AI_Drop',
      WATCHER_INTERVAL_SECONDS: '30'
    }
  }]
};
```

## DRY_RUN Verification Steps
To verify `DRY_RUN` functionality:

1.  **Set `DRY_RUN=true`**: Ensure the environment variable `DRY_RUN` is set to `"true"` (this is the default).
2.  **Start the Watcher**: Start the `filesystem-watcher` skill (either via PM2 or manually as described above).
3.  **Place a Test File**: Place a new file (e.g., `test.txt`) into your configured `DROP_FOLDER_PATH`.
4.  **Check Logs**:
    -   Monitor the console output or PM2 logs (`pm2 logs filesystem-watcher`). You should see messages indicating that files *would be* copied and metadata *would be* created, without actual file movements.
    -   Check `{{VAULT_PATH}}\Vault\Logs\YYYY-MM-DD.json`. You should find log entries with `"dry_run": true` and `event_type: "file_detected_dry_run"`.
5.  **Verify No File Changes**: Confirm that no new files appeared in `{{VAULT_PATH}}\Needs_Action` and that `{{VAULT_PATH}}\.watcher_state\processed_files.json` has *not* been updated. The original file in the drop folder should remain untouched.

## Post-conditions / Verification
To verify the skill is working correctly (with `DRY_RUN=false`):

1.  **Set `DRY_RUN=false`**: Change the environment variable `DRY_RUN` to `"false"` in your PM2 ecosystem file or manual execution command. Restart the watcher if using PM2.
2.  **Place a New Test File**: Place a *new, unique* file (e.g., `another_test.pdf`) into your `DROP_FOLDER_PATH`.
3.  **Check Obsidian Vault**:
    -   Verify that the `another_test.pdf` (with a timestamp prefix) has appeared in `{{VAULT_PATH}}\Needs_Action`.
    -   Verify that a companion markdown file named `FILE_another_test.pdf_<timestamp>.md` has also appeared in `{{VAULT_PATH}}\Needs_Action`.
    -   Open the `.md` file and confirm its content matches the specified metadata format.
4.  **Check Logs**:
    -   Monitor console/PM2 logs. You should see messages indicating actual file copying and metadata creation.
    -   Check `{{VAULT_PATH}}\Vault\Logs\YYYY-MM-DD.json`. You should find log entries with `"dry_run": false` and `event_type: "file_detected_and_processed"`.
5.  **Check State File**: Open `{{VAULT_PATH}}\.watcher_state\processed_files.json` and confirm that the full path of the `another_test.pdf` is listed.
6.  **Duplicate Check**: Place the *same* `another_test.pdf` file into the `DROP_FOLDER_PATH` again. The watcher should *not* re-process it, and no new copies or metadata files should be created in `Needs_Action`. Logs should indicate it was skipped.

## Error Handling
The `filesystem-watcher` is designed with the following error handling and robustness features:

-   **Crash Safety & Idempotency**: The `processed_files.json` state file tracks all processed files. If the watcher crashes or restarts, it will load this state and avoid re-processing files that were already handled, ensuring idempotency.
-   **Permission Errors**: File operations are wrapped in `try-except PermissionError` blocks. If the script lacks necessary read/write permissions for the `DROP_FOLDER_PATH` or `VAULT_PATH` directories, it will log an error and continue, rather than crashing.
-   **File Not Found**: If an original file unexpectedly disappears during processing, `FileNotFoundError` is caught, an error is logged, and the watcher continues.
-   **Vault/Drop Folder Not Found**: If `VAULT_PATH` or `DROP_FOLDER_PATH` do not exist, critical errors are logged at startup, and the script exits gracefully, preventing an infinite crash loop.
-   **Corrupt State File**: If `processed_files.json` is corrupted (e.g., malformed JSON), the watcher will log an error, reinitialize `processed_files` as an empty set, and continue operation, preventing crashes due to bad state.
-   **Robust Logging**: All significant actions and errors are logged to a daily JSON file within the vault (`{{VAULT_PATH}}\Vault\Logs\YYYY-MM-DD.json`), providing an audit trail and aid for debugging. Logging failures are also handled gracefully.
-   **PM2 Autorestart**: When managed by PM2, the script will automatically restart if it encounters an unhandled exception, ensuring high availability.

## Success Criteria
The `filesystem-watcher` skill is deemed successful if:

-   **Files are Detected**: New files placed in `DROP_FOLDER_PATH` are detected within `WATCHER_INTERVAL_SECONDS`.
-   **Files are Processed (DRY_RUN=false)**:
    -   The detected file is copied (with a timestamp prefix) to `{{VAULT_PATH}}\Needs_Action`.
    -   A companion `.md` metadata file (following the specified format) is created in `{{VAULT_PATH}}\Needs_Action`.
    -   The file's original full path is recorded in `{{VAULT_PATH}}\.watcher_state\processed_files.json`.
    -   The action is logged to `{{VAULT_PATH}}\Vault\Logs\YYYY-MM-DD.json` with `dry_run: false`.
-   **DRY_RUN Mode (DRY_RUN=true)**:
    -   The watcher detects files and logs intended actions without performing file copies/moves or state updates.
    -   Log entries in `{{VAULT_PATH}}\Vault\Logs\YYYY-MM-DD.json` correctly reflect `dry_run: true`.
-   **No Duplicates**: Files already processed (as recorded in `processed_files.json`) are correctly skipped on subsequent checks.
-   **Stability**: The watcher runs continuously without crashing due to expected operational errors (e.g., permissions, empty folders).
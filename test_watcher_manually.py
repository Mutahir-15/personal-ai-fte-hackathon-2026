import time
import os
from pathlib import Path
from src.services.filesystem_watcher import FilesystemWatcher
from src.config.settings import Config

def test_watcher():
    print("--- Starting Manual Watcher Test ---")
    
    # Ensure drop folder exists
    drop_folder = Config.DROP_FOLDER_PATH
    drop_folder.mkdir(parents=True, exist_ok=True)
    print(f"Monitoring Drop Folder: {drop_folder}")
    print(f"Vault Needs_Action: {Config.NEEDS_ACTION_DIR}")
    
    watcher = FilesystemWatcher()
    watcher.start()
    
    try:
        # 1. Create a test file in the drop folder
        test_file_path = drop_folder / "test_file.txt"
        with open(test_file_path, "w", encoding='utf-8') as f:
            f.write("Hello, this is a test file for the filesystem watcher.")
        print(f"Created test file: {test_file_path.name}")
        
        # 2. Wait for watcher to detect and process
        print("Waiting 3 seconds for detection...")
        time.sleep(3)
        
        # 3. Check if .md file exists in Needs_Action
        print("Checking Needs_Action directory...")
        found_md = False
        for item in Config.NEEDS_ACTION_DIR.iterdir():
            if item.is_file() and item.suffix == ".md" and "test_file" in item.name:
                print(f"SUCCESS: Found metadata file: {item.name}")
                found_md = True
                
        if not found_md:
            print("FAILURE: No metadata file found for test_file.")
            
        # 4. Check if the original file was copied
        found_copy = False
        for item in Config.NEEDS_ACTION_DIR.iterdir():
            if item.is_file() and "test_file" in item.name and item.suffix != ".md":
                print(f"SUCCESS: Found copied file: {item.name}")
                found_copy = True
                
        if not found_copy:
            print("FAILURE: No copy of the original file found.")

    finally:
        watcher.stop()
        print("--- Manual Watcher Test Finished ---")

if __name__ == "__main__":
    test_watcher()

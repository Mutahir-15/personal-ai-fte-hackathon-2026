import sys
import os
import logging

# Add current directory to path so it can find src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.filesystem_watcher import FilesystemWatcher
from src.config.settings import Config

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    Config.validate()
    print(f"Starting Filesystem Watcher (DRY_RUN={Config.DRY_RUN})...")
    watcher = FilesystemWatcher()
    watcher.start()
    try:
        watcher.run_forever()
    except KeyboardInterrupt:
        watcher.stop()

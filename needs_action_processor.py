import sys
import os
from pathlib import Path

# Add current directory to path so it can find src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.action_processor import NeedsActionProcessor
from src.config.settings import Config

if __name__ == "__main__":
    Config.validate()
    processor = NeedsActionProcessor()
    if len(sys.argv) > 1:
        file_to_process = Path(sys.argv[1])
        print(f"Processing: {file_to_process} (DRY_RUN={Config.DRY_RUN})...")
        result = processor.perform(file_to_process)
        print(f"Result: {result}")
    else:
        print("Usage: python needs_action_processor.py <file_path>")

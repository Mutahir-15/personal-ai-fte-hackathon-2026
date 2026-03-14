import sys
import os

# Add current directory to path so it can find src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.orchestrator import Orchestrator
from src.config.settings import Config

if __name__ == "__main__":
    try:
        Config.validate()
        orchestrator = Orchestrator()
        orchestrator.start()
    except Exception as e:
        print(f"Failed to start Orchestrator: {e}")
        sys.exit(1)

import sys
import os

# Add current directory to path so it can find src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.audit_logger import AuditLogger
from src.config.settings import Config

if __name__ == "__main__":
    Config.validate()
    AuditLogger.log(
        action_type="standalone_test",
        actor="root-script",
        target="audit-system",
        status="success",
        result="Standalone test passed"
    )
    print(f"Audit log test entry written to {AuditLogger.get_log_path()}")

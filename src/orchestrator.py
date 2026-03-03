import time
import signal
import sys
import logging
from src.services.filesystem_watcher import FilesystemWatcher
from src.services.approval_watcher import ApprovalWatcher
from src.services.audit_logger import AuditLogger
from src.config.settings import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Orchestrator")

class Orchestrator:
    """Manages the lifecycle of all watcher services."""
    
    def __init__(self):
        self.watchers = []
        self.running = True
        
        # Initialize watchers
        self.watchers.append(FilesystemWatcher())
        self.watchers.append(ApprovalWatcher())
        
        # Register signals for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def handle_exit(self, signum, frame):
        """Signal handler for exit signals."""
        logger.info(f"Received exit signal ({signum}). Initiating shutdown...")
        self.running = False

    def start(self):
        """Starts all watchers and maintains the heartbeat loop."""
        logger.info("Starting Bronze Vault Orchestrator...")
        logger.info(f"DRY_RUN mode: {Config.DRY_RUN}")
        logger.info(f"Vault Root: {Config.VAULT_ROOT}")
        
        try:
            AuditLogger.log(
                skill="orchestrator",
                action="start_orchestrator",
                status="success",
                metadata={"dry_run": Config.DRY_RUN, "vault_root": str(Config.VAULT_ROOT)}
            )
        except Exception as e:
            logger.error(f"Initial audit logging failed: {e}")

        for watcher in self.watchers:
            try:
                watcher.start()
            except Exception as e:
                logger.error(f"Failed to start {watcher.__class__.__name__}: {e}")

        logger.info("All watchers initialized. Entering heartbeat loop.")
        
        try:
            while self.running:
                # Health reporting / heartbeat
                # In a more advanced version, we could check watcher.observer.is_alive()
                time.sleep(1)
        except Exception as e:
            logger.error(f"Orchestrator heartbeat loop interrupted: {e}")
            AuditLogger.log(
                skill="orchestrator",
                action="runtime_error",
                status="error",
                metadata={"error": str(e)}
            )
        finally:
            self.stop()

    def stop(self):
        """Stops all watchers and exits."""
        logger.info("Stopping all watchers...")
        for watcher in self.watchers:
            try:
                watcher.stop()
            except Exception as e:
                logger.error(f"Error stopping {watcher.__class__.__name__}: {e}")
        
        try:
            AuditLogger.log(
                skill="orchestrator",
                action="stop_orchestrator",
                status="success"
            )
        except Exception as e:
            logger.error(f"Final audit logging failed: {e}")
            
        logger.info("Orchestrator shutdown complete.")
        # Ensure we exit even if threads are lingering
        os._exit(0)

if __name__ == "__main__":
    import os
    try:
        Config.validate()
        orchestrator = Orchestrator()
        orchestrator.start()
    except Exception as e:
        logger.critical(f"Failed to initialize Orchestrator: {e}")
        sys.exit(1)

from abc import ABC, abstractmethod
import logging
from src.config.settings import Config

class BaseAction(ABC):
    """Abstract base class for skill-driven actions."""
    
    def __init__(self, dry_run: bool = None):
        # Use provided dry_run or default to Config.DRY_RUN
        self.dry_run = dry_run if dry_run is not None else Config.DRY_RUN
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def execute(self, *args, **kwargs):
        """Executes the core logic of the action."""
        pass

    def perform(self, *args, **kwargs):
        """Entry point that respects the DRY_RUN flag."""
        if self.dry_run:
            self.logger.info(f"[DRY_RUN] Would execute {self.__class__.__name__}")
            
            # Log dry run to audit log for transparency
            try:
                from src.services.audit_logger import AuditLogger
                AuditLogger.log(
                    action_type="simulated_execution",
                    actor=self.__class__.__name__,
                    target=str(args[0]) if args else "N/A",
                    parameters={"args": str(args), "kwargs": str(kwargs)},
                    status="dry_run",
                    result="Dry run simulation complete"
                )
            except Exception as e:
                self.logger.error(f"Failed to log dry run to audit log: {e}")

            return {"status": "dry_run", "action": self.__class__.__name__}
        
        return self.execute(*args, **kwargs)

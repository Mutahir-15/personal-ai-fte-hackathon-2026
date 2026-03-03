from abc import ABC, abstractmethod
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import logging

class BaseWatcher(ABC):
    """Abstract base class for all filesystem watchers."""
    
    def __init__(self, watch_path: str, observer: Observer = None):
        self.watch_path = watch_path
        self.observer = observer or Observer()
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def start(self):
        """Starts the watcher."""
        pass

    @abstractmethod
    def stop(self):
        """Stops the watcher."""
        pass
        
    def run_forever(self):
        """Keeps the process alive."""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

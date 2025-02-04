import logging
import signal
import subprocess
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    pass

@contextmanager
def timeout_handler(seconds):
    def handler(signum, frame):
        raise TimeoutError("Operation timed out")
    original_handler = signal.signal(signal.SIGALRM, handler)
    try:
        signal.alarm(seconds)
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, original_handler)

class BaseModel(ABC):
    TIMEOUT = 30

    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self.cache_dir = Path.home() / ".cache" / "bourguibagpt" / "models"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _run_subprocess(self, command: str) -> None:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Command '{command}' failed: {result.stderr}")
    
    def is_model_cached(self) -> bool:
        model_path = self.cache_dir / self.config["model_name"].replace("/", "_")
        return model_path.exists()

    @abstractmethod
    def install_model(self):
        pass

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def generate_answer(self, prompt: str) -> str:
        pass
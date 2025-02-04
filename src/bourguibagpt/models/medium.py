import logging
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch
from rich.progress import Progress
from .base import BaseModel
from ..config import MODEL_CONFIG

class GPTNeo1_3B(BaseModel):
    def __init__(self):
        super().__init__(MODEL_CONFIG["medium"])
        torch.set_grad_enabled(False)  # Disable gradients
        if not self.is_model_cached():
            self.install_model()
        self.load_model()

    def install_model(self):
        self._run_subprocess("pip install transformers")
        try:
            # Download and cache model and tokenizer
            model = AutoModelForCausalLM.from_pretrained(self.config["model_name"])
            tokenizer = AutoTokenizer.from_pretrained(self.config["model_name"])
        except Exception as e:
            logging.error(f"Failed to download model: {e}")
            raise
        model_path = self.cache_dir / self.config["model_name"].replace("/", "_")
        try:
            model.save_pretrained(str(model_path))
            tokenizer.save_pretrained(str(model_path))
        except Exception as e:
            logging.error(f"Failed to save model/tokenizer: {e}")
            raise

    def load_model(self):
        if not self.model:
            model_path = self.cache_dir / self.config["model_name"].replace("/", "_")
            try:
                self.model = pipeline("text-generation", model=str(model_path))
            except Exception as e:
                logging.error(f"Failed to load model from {model_path}: {e}")
                raise

    def generate_answer(self, prompt: str, max_length: int = 50) -> str:
        try:
            result = self.model(prompt, max_length=max_length)
            return result[0]["generated_text"]
        except Exception as e:
            logging.error(f"Failed to generate answer: {e}")
            raise
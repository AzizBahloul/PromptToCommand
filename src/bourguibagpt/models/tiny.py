import logging
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from .base import BaseModel
from ..config import MODEL_CONFIG

class GPTNeo125M(BaseModel):
    def __init__(self):
        super().__init__(MODEL_CONFIG["tiny"])
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
            import os
            # Force using PyTorch and disable TensorFlow to avoid Keras errors.
            os.environ["TRANSFORMERS_NO_TF"] = "1"
            try:
                self.model = pipeline("text-generation", model=str(model_path), device=-1, framework="pt")
            except Exception as e:
                logging.error(f"Failed to load model from {model_path}: {e}")
                raise

    def generate_answer(self, prompt: str, max_length: int = 50) -> str:
        try:
            result = self.model(prompt, max_length=max_length)
            return result[0]["generated_text"]
        except Exception as e:
            logging.error(f"Error generating answer: {e}")
            raise
# Uses bartowski/Phi-3.5-mini-instruct-GGUF for systems with <=8GB RAM and no CPU/GPU
import sys
import subprocess
from transformers import pipeline
from llama_cpp import Llama
from pathlib import Path

class BourguibaT:
    def __init__(self):
        self.model_name = "bartowski/Phi-3.5-mini-instruct-GGUF"
        self.model_file = "Phi-3.5-mini-instruct.Q4_K_M.gguf"  # Specific quantized version
        self.llm = None

    def install_model(self):
        try:
            subprocess.run("pip install llama-cpp-python", shell=True, check=True)
            if not Path(self.model_file).exists():
                subprocess.run(
                    f"huggingface-cli download {self.model_name} {self.model_file}",
                    shell=True, check=True
                )
        except Exception as e:
            print(f"Install failed: {e}")

    def generate_answer(self, prompt: str):
        if not self.llm:
            self.llm = Llama(
                model_path=self.model_file,
                n_ctx=2048,
                n_threads=4,
                n_gpu_layers=0  # CPU only
            )
        output = self.llm(
            f"<|user|>\n{prompt}<|assistant|>",
            max_tokens=50,
            temperature=0.7
        )
        return output['choices'][0]['text']
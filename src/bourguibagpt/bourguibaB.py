# For GPU only. If VRAM 4-6GB -> mistralai/Mistral-7B-Instruct-v0.3, else >6GB -> bigcode/starcoder2-7b
import sys
import subprocess
from transformers import pipeline

class BourguibaB:
    def __init__(self, gpu_vram_gb: int):
        if 4 <= gpu_vram_gb <= 6:
            self.model_name = "mistralai/Mistral-7B-Instruct-v0.3"
        else:
            self.model_name = "bigcode/starcoder2-7b"

    def install_model(self):
        try:
            subprocess.run(
                f"pip install git+https://github.com/huggingface/transformers.git",
                shell=True, check=True
            )
            # Additional installs for starcoder2 or Mistral as needed
        except Exception as e:
            print(f'Error installing model: {e}')

    def generate_answer(self, prompt: str):
        gen = pipeline("text-generation", model=self.model_name)
        return gen(prompt, max_length=50)[0]["generated_text"]
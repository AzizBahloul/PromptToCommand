# Uses mistralai/Mistral-7B-Instruct-v0.3 for CPU or GPU
import sys
import subprocess
from transformers import pipeline

class BourguibaM:
    def __init__(self):
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.3"

    def install_model(self):
        try:
            subprocess.run(
                f"pip install git+https://github.com/huggingface/transformers.git",
                shell=True, check=True
            )
            # Possibly more steps for Mistral
        except Exception as e:
            print(f'Error installing or pulling Mistral: {e}')

    def generate_answer(self, prompt: str):
        gen = pipeline("text-generation", model=self.model_name)
        return gen(prompt, max_length=50)[0]["generated_text"]
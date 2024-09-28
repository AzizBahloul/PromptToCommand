import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def download_model():
    model_name = "distilgpt2"
    model_dir = os.path.join(os.path.expanduser("~"), ".bourguiba_model")

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    if not os.path.exists(os.path.join(model_dir, "pytorch_model.bin")):
        print(f"Downloading model '{model_name}' to '{model_dir}'...")
        model = AutoModelForCausalLM.from_pretrained(model_name)
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model.save_pretrained(model_dir)
        tokenizer.save_pretrained(model_dir)
        print("Model downloaded and saved.")
    else:
        print("Model already exists. Loading from local directory.")

    return model_dir
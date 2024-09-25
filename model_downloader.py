import os
from transformers import GPT2Tokenizer, GPT2LMHeadModel

def download_model(model_name="gpt2"):
    if not os.path.exists(model_name):
        print(f"Downloading model '{model_name}'...")
        model = GPT2LMHeadModel.from_pretrained(model_name)
        tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        model.save_pretrained(model_name)
        tokenizer.save_pretrained(model_name)
    else:
        print(f"Model '{model_name}' is already downloaded.")

if __name__ == "__main__":
    download_model()

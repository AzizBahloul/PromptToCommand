import os
from transformers import T5ForConditionalGeneration, T5Tokenizer

def download_model(model_dir):
    # Check if the model is already downloaded
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        
        try:
            # Download the model and tokenizer
            print("Downloading T5 small model...")
            tokenizer = T5Tokenizer.from_pretrained('t5-small', cache_dir=model_dir)
            model = T5ForConditionalGeneration.from_pretrained('t5-small', cache_dir=model_dir)
            print(f"Model downloaded and saved in {model_dir}")

            # Check if the expected files are present
            if not os.path.exists(os.path.join(model_dir, "config.json")):
                raise EnvironmentError("Model files not found in the directory.")
        except Exception as e:
            print(f"An error occurred while downloading the model: {e}")
            raise
    else:
        print(f"Model already exists in {model_dir}.")

import os
import sys
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer
from bourguiba.model_downloader import download_model

class Bourguiba:
    def __init__(self, model_dir):
        # Load the model and tokenizer from the specified directory
        try:
            self.tokenizer = T5Tokenizer.from_pretrained('t5-small', cache_dir=model_dir)
            self.model = T5ForConditionalGeneration.from_pretrained('t5-small', cache_dir=model_dir)
        except Exception as e:
            print(f"Failed to load the model: {e}")
            raise

    def generate_command(self, description):
        # Prepare the input for the model
        input_text = f"generate command: {description}"
        input_ids = self.tokenizer.encode(input_text, return_tensors='pt')

        # Generate the command
        with torch.no_grad():
            output = self.model.generate(input_ids)

        # Decode the generated command
        command = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return command


def main():
    # Set the custom model directory
    model_dir = os.path.join(os.path.expanduser("~"), ".bourguiba_model")
    
    # Download the model if not already present
    download_model(model_dir)

    # Initialize the Bourguiba class with the downloaded model
    bourguiba = Bourguiba(model_dir)

    if len(sys.argv) < 2:
        print("Usage: bourguiba <command_description>")
        sys.exit(1)

    description = " ".join(sys.argv[1:])
    command = bourguiba.generate_command(description)
    print(f"Generated command: {command}")

if __name__ == "__main__":
    main()

import os
import sys
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer

class Bourguiba:
    def __init__(self):
        model_dir = os.path.join(os.path.expanduser("~"), ".bourguiba_model")
        self.tokenizer = T5Tokenizer.from_pretrained('t5-small', cache_dir=model_dir)
        self.model = T5ForConditionalGeneration.from_pretrained('t5-small', cache_dir=model_dir)

    def generate_command(self, description):
        input_text = f"generate command: {description}"
        input_ids = self.tokenizer.encode(input_text, return_tensors='pt')

        with torch.no_grad():
            output = self.model.generate(input_ids, max_length=100)

        command = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return command

def main():
    if len(sys.argv) < 2:
        print("Usage: bourguiba <command_description>")
        sys.exit(1)

    bourguiba = Bourguiba()
    description = " ".join(sys.argv[1:])
    command = bourguiba.generate_command(description)
    print(f"Generated command: {command}")

if __name__ == "__main__":
    main()
import sys
import re
import os
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from instruction import generate_instruction  # Ensure this matches your file structure

class Bourguiba:
    def __init__(self, model_name="t5-small"):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    def generate_command(self, description):
        # Generate instruction using the modified function
        instruction = generate_instruction(description)
        input_ids = self.tokenizer.encode(instruction, return_tensors="pt")

        generated_ids = self.model.generate(input_ids, max_length=50)
        generated_text = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)

        return self.extract_command(generated_text)

    def extract_command(self, generated_text):
        # Enhanced command extraction logic to return only valid commands
        generated_text = generated_text.strip()
        # Regex to match valid shell command patterns
        command_matches = re.findall(r'^(.*)$', generated_text)
        if command_matches:
            command = command_matches[0].strip()
            # Check if it's a valid shell command (simple heuristic)
            if command.startswith(('ls', 'mkdir', 'touch', 'rm', 'cp', 'mv', 'cat', 'echo', 'man')):
                return command
        return "Could not generate a valid command."

def main():
    bourguiba = Bourguiba()
    try:
        description = input("Enter your command description: ")
        command = bourguiba.generate_command(description)
        print(f"Generated command: {command}")
        # Uncomment the following line to actually execute the command
        # os.system(command)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

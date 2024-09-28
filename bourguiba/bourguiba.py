import os
from transformers import T5Tokenizer, T5ForConditionalGeneration
import subprocess
import platform

class Bourguiba:
    def __init__(self):
        self.model_name = 'google/flan-t5-small'
        self.model_dir = os.path.expanduser("~/.bourguiba_model")

        # Download and cache the model locally
        self.tokenizer = T5Tokenizer.from_pretrained(self.model_name, cache_dir=self.model_dir)
        self.model = T5ForConditionalGeneration.from_pretrained(self.model_name, cache_dir=self.model_dir)

    def generate_command(self, description):
        # Prepare the input for the model
        input_text = f"Generate command: {description}"
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")

        # Generate the command
        output_ids = self.model.generate(input_ids, max_length=50)
        command = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        
        # Clean up the generated command for execution
        cleaned_command = self.clean_command(command)
        return cleaned_command

    def clean_command(self, command):
        # Implement basic cleaning logic to make the command valid
        command = command.strip()

        # Platform-specific command adjustments
        system_platform = platform.system()

        if system_platform == 'Linux':
            # Ubuntu-specific adjustments (add any custom command mappings here)
            if command.startswith("Create a folder"):
                command = command.replace("Create a folder", "mkdir")
        elif system_platform == 'Darwin':
            # macOS-specific adjustments
            if command.startswith("Create a folder"):
                command = command.replace("Create a folder", "mkdir")
        elif system_platform == 'Windows':
            # Windows-specific adjustments
            if command.startswith("Create a folder"):
                command = command.replace("Create a folder", "mkdir")
                command += " -Force"  # Windows might need force for certain operations

        return command

def main():
    bourguiba = Bourguiba()
    print("Enter your command description (or 'quit' to exit):")
    
    while True:
        description = input("> ")
        if description.lower() == 'quit':
            break
        
        command = bourguiba.generate_command(description)
        print(f"Generated command: {command}")

        # Execute the command and capture output
        try:
            result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
            print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("Error executing command:", e.stderr)

if __name__ == "__main__":
    main()

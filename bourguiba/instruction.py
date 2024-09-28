import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class CommandGenerator:
    def __init__(self, model_dir):
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForCausalLM.from_pretrained(model_dir)
        self.model.eval()

    def generate_command(self, description):
        input_text = f"Generate shell commands for Linux, Mac, and Windows:\n{description}\n"
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")

        with torch.no_grad():
            output_ids = self.model.generate(
                input_ids,
                max_length=150,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )

        commands = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return self.clean_commands(commands)

    def clean_commands(self, commands):
        lines = commands.split('\n')
        cleaned = []
        for line in lines:
            if line.startswith(('Linux:', 'Mac:', 'Windows:')):
                cleaned.append(line.strip())
        return '\n'.join(cleaned)
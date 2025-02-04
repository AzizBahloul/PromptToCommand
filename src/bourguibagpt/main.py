# Set the environment variable before any transformers import to disable TensorFlow.
import os
os.environ["TRANSFORMERS_NO_TF"] = "1"

import platform
import re
import sys
import logging
import argparse
import time
import signal
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress
from rich.text import Text
from rich.layout import Layout
from rich import box
import subprocess
from datetime import datetime

# Import Hugging Face transformers components
from transformers import pipeline, set_seed

# Import MODEL_CONFIG from config.py
from .config import MODEL_CONFIG

# Import model classes
from .models import GPTNeo125M, GPTNeo1_3B, GPTNeo2_7B

def get_model_download_path(model_name: str) -> Path:
    """Get path where model files are stored."""
    cache_dir = Path.home() / ".cache" / "bourguibagpt" / "models"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{model_name.replace('/', '_')}"

def is_model_downloaded(model_name: str) -> bool:
    """Check if model is already downloaded."""
    model_path = get_model_download_path(model_name)
    return model_path.exists()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

console = Console()

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║  ____                            _ _           ____ ____ _____ ║
║ | __ ) ___  _   _ _ __ __ _ _  (_) |__   __ / ___|  _ \\_   _|║
║ |  _ \\/ _ \\| | | | '__/ _` | | | | '_ \\ / _` | |  | |_) || |  ║
║ | |_) | (_) | |_| | | | (_| | |_| | |_) | (_| | |__| __/ | |  ║
║ |____/\\___/ \\__,_|_|  \\__, |\\__,_|_.__/ \\__,_|\\____|_|   |_|  ║
║                          |_|                                    ║
║              Your Tunisian Shell Command Assistant             ╚══════════════════════════════════════════════════════════════╝
"""

VERSION = "3.0.0"

def get_system_memory() -> float:
    """Retrieve total system memory in GB."""
    import psutil
    mem = psutil.virtual_memory()
    return mem.total / (1024 ** 3)

def get_os_info() -> str:
    """Detect the operating system and, if Linux, the distribution."""
    os_name = platform.system()
    if os_name == "Linux":
        try:
            with open("/etc/os-release", "r") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        return line.split("=")[1].strip().strip('"')
        except Exception as e:
            logging.warning(f"Could not detect Linux distribution: {e}")
    return os_name

def recommend_model(system_ram: float) -> str:
    """
    Recommend a model key based on available RAM.
    
    :param system_ram: The amount of system RAM in GB
    :return: Model key recommendation (tiny, medium, large)
    """
    if system_ram <= 0:
        raise ValueError("System RAM must be positive.")
    if system_ram <= 8:
        return "tiny"
    elif system_ram <= 16:
        return "medium"
    else:
        return "large"

class ShellCommandGenerator:
    """
    Shell command generator that outputs a generated command.
    
    :param model_name: The model name to use
    :param temperature: Controls randomness of the output
    :param history_file: Path to the command history file
    :param output_command_only: If True, prints only the command
    """
    def __init__(
        self,
        model_name: str,
        temperature: float = 0.7,
        history_file: Optional[Path] = None,
        output_command_only: bool = False,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.history_file = history_file or Path.home() / ".shell_command_history.json"
        self.command_history: List[Dict[str, Any]] = []
        self.output_command_only = output_command_only
        self.max_retries = 3
        self.timeout = 30
        self._load_history()

    def _load_history(self) -> None:
        """Load command history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.command_history = json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load history: {e}")
            self.command_history = []

    def _save_history(self) -> None:
        """Save command history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.command_history, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save history: {e}")

    def _call_hf(self, prompt: str) -> Dict[str, Any]:
        """
        Call Hugging Face text generation pipeline to generate a shell command.
        Returns a dict with key 'command'.
        """
        try:
            from transformers import pipeline, set_seed

            system_instruction = (
                "Generate a single valid Unix shell command for the given task. "
                "Output ONLY the command itself without any explanations, descriptions, or formatting. "
                "The command must be properly escaped and follow POSIX standards."
            )
            full_prompt = f"{system_instruction}\nTask: {prompt}\nCommand:"

            generator = pipeline("text-generation", model=self.model_name, device=-1)
            set_seed(42)
            results = generator(
                full_prompt,
                max_new_tokens=50,
                num_return_sequences=1,
                temperature=0.3,
                top_p=0.95,
                repetition_penalty=1.2,
                do_sample=True,
                clean_up_tokenization_spaces=True,
                truncation=True
            )
            raw_text = results[0]["generated_text"].strip()

            # Enhanced command extraction logic
            command = None
            command_pattern = re.compile(
                r'(?:^|\n)'
                r'\s*'
                r'(?P<command>'
                r'(?:sudo\s+)?'
                r'(?:mkdir|cd|ls|echo|cp|mv|rm|chmod|grep|find|tar|curl|wget|git|'
                r'\./|/[\w/\.-]+|[\w+-]+)'
                r'(?:\s+[^\n]*)?)'
                r'\s*$',
                re.IGNORECASE
            )

            # First try to find command after the last "Command:" prompt
            command_sections = re.split(r'Command:\s*', raw_text, flags=re.IGNORECASE)
            if len(command_sections) > 1:
                last_command_section = command_sections[-1]
                match = command_pattern.search(last_command_section)
                if match:
                    command = match.group('command').split('\n')[0].strip()

            # If not found, search entire text
            if not command:
                match = command_pattern.search(raw_text)
                if match:
                    command = match.group('command').split('\n')[0].strip()

            # Final validation
            if not command or not re.match(r'^\s*(sudo\s+)?[\w/\.+-]+', command):
                raise ValueError("No valid shell command detected in response")

            # Basic security check
            dangerous_patterns = [
                r'rm\s+-(rf|r\s+f|f\s+r)',
                r':\(\)\{\s*:|\s*\|\s*:\s*\}\s*;',
                r'wget\s+http://',
                r'curl\s+http://',
                r'\s/dev/null\s*',
            ]
            for pattern in dangerous_patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    raise ValueError(f"Potentially dangerous command detected: {command}")

            return {"command": command}
        except Exception as e:
            raise ValueError(f"Hugging Face generation error: {e}")

    def generate_command(self, prompt: str) -> Dict[str, Any]:
        """Generate a shell command based on the given prompt using Hugging Face."""
        try:
            result = self._call_hf(prompt)
            command = result.get('command', '').strip()
            if not command:
                raise ValueError("Generated command is empty")
            record = {
                'prompt': prompt,
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'error': None
            }
            self.command_history.append(record)
            self._save_history()
            return record
        except Exception as e:
            record = {
                'prompt': prompt,
                'command': None,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
            self.command_history.append(record)
            self._save_history()
            console.print(f"[red]Error generating command: {e}[/red]")
            return record

    def run(self) -> None:
        """
        If output_command_only is True, ask for a prompt, generate the command,
        output only the command line, and exit.
        Otherwise, proceed with interactive mode.
        """
        if self.output_command_only:
            user_input = sys.stdin.read().strip()
            result = self.generate_command(user_input)
            if cmd := result.get("command"):
                print(cmd.split("#")[0].split("//")[0].strip())
            sys.exit(0)
        else:
            console.print(f"[bold cyan]{BANNER}[/bold cyan]")
            console.print(f"[bold blue]BourguibaGPT[/bold blue] [cyan]v{VERSION}[/cyan]")
            console.print(f"[dim]Powered by Hugging Face - Model: {self.model_name}[/dim]")
            console.print("\n[italic]Type 'help' for available commands or 'exit' to quit[/italic]\n")
        
            while True:
                try:
                    user_input = Prompt.ask("\n[bold magenta]🇹🇳 BourguibaGPT[/bold magenta] [bold blue]→[/bold blue]")
                    if user_input.lower() in ['exit', 'quit']:
                        break
                    elif user_input.lower() == 'help':
                        self._show_help()
                    elif user_input.lower() == 'history':
                        self.show_history()
                    elif user_input.lower().startswith('execute '):
                        command = user_input[8:].strip()
                        self.execute_command(command)
                    else:
                        result = self.generate_command(user_input)
                        if result.get("command"):
                            console.print(f"\n[green]Generated command:[/green]")
                            console.print(Panel(result["command"], style="bold white"))
                            
                            choice = Prompt.ask(
                                "\n[yellow]Type 'e' to execute the generated command and exit, or 'n' to return to the prompt:[/yellow]",
                                choices=["e", "n"],
                                default="n"
                            )
                            if choice.lower() == "e":
                                self.execute_command(result["command"], confirm_execution=False)
                                console.print("[green]Exiting...[/green]")
                                sys.exit(0)
                        else:
                            console.print("[red]Failed to generate a valid command[/red]")
                            
                except KeyboardInterrupt:
                    console.print("\n[yellow]Exiting...[/yellow]")
                    break
                except Exception as e:
                    logging.error(f"Error in command loop: {e}")

    def execute_command(self, command: str, confirm_execution: bool = True) -> bool:
        """Safely execute a shell command with confirmation."""
        try:
            if confirm_execution:
                confirm = Prompt.ask(
                    "\n[yellow]Do you want to execute this command?[/yellow]",
                    choices=["yes", "no"],
                    default="no"
                )
                if confirm.lower() != "yes":
                    return False
            console.print("\n[cyan]Executing command...[/cyan]")
            result = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                console.print("[green]Command executed successfully[/green]")
                if result.stdout:
                    console.print(Panel(result.stdout, title="Output", border_style="green"))
            else:
                console.print("[red]Command failed[/red]")
                if result.stderr:
                    console.print(Panel(result.stderr, title="Error", border_style="red"))
            return result.returncode == 0
        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")
        return False

    def show_history(self, limit: int = 10) -> None:
        """Display command history."""
        if not self.command_history:
            console.print("[yellow]No command history available[/yellow]")
            return
        console.print("\n[bold]Command History:[/bold]")
        for entry in reversed(self.command_history[-limit:]):
            console.print(Panel(
                f"Prompt: {entry['prompt']}\nCommand: {entry['command']}\nTime: {entry['timestamp']}",
                border_style="blue"
            ))

    def _show_help(self) -> None:
        """Display help information."""
        help_text = """[bold]Available Commands:[/bold]
        
[cyan]help[/cyan] - Show this help message
[cyan]history[/cyan] - Show command history
[cyan]execute <command>[/cyan] - Execute a specific command
[cyan]exit or quit[/cyan] - Exit BourguibaGPT

[bold]Tips:[/bold]
• Be specific in your command requests
• Use natural language to describe what you want to do
• Commands are validated for safety
• History is saved automatically
        """
        console.print(Panel(
            help_text,
            title="[bold]BourguibaGPT Help[/bold]",
            border_style="blue",
            box=box.DOUBLE
        ))

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Enhanced Shell Command Generator using Hugging Face")
    parser.add_argument("--model", default="mistral-openorca", help="Hugging Face model name")
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Generation temperature (0.0-1.0)",
        choices=[x/10 for x in range(11)]
    )
    parser.add_argument("--history-file", type=Path, help="Custom history file location")
    parser.add_argument("--output-command-only", action="store_true", help="Output only the generated command")
    return parser.parse_args()

def main() -> None:
    """Main entry point with error handling."""
    try:
        args = parse_arguments()
        system_ram = get_system_memory()
        os_info = get_os_info()
        recommended = recommend_model(system_ram)
        
        console.print(f"[bold cyan]System Information:[/bold cyan]")
        console.print(f"• OS: {os_info}")
        console.print(f"• RAM: {system_ram:.1f} GB")
        console.print(f"• Recommended Model: {MODEL_CONFIG[recommended]['description']}")
        
        console.print("\n[bold]Available Models:[/bold]")
        for key, config in MODEL_CONFIG.items():
            downloaded = "✓" if is_model_downloaded(config["model_name"]) else " "
            console.print(f"• {key.capitalize()} [{downloaded}]: {config['description']}")

        selected_model_key = Prompt.ask(
            "\n[bold]Select a model[/bold] (t=Tiny / m=Medium / l=Large)",
            choices=["t", "m", "l"],
            default="m"
        )

        model_map = {"t": ("tiny", GPTNeo125M), "m": ("medium", GPTNeo1_3B), "l": ("large", GPTNeo2_7B)}
        selected_model, model_class = model_map.get(selected_model_key, ("medium", GPTNeo1_3B))
        
        model = model_class()
        model_name = MODEL_CONFIG[selected_model]["model_name"]

        if not is_model_downloaded(model_name):
            console.print(f"\n[yellow]Downloading {model_name} model...[/yellow]")
            model.install_model()
            console.print("[green]Model downloaded successfully![/green]")
        else:
            console.print(f"\n[green]Using existing {model_name} model[/green]")

        console.print("\n[yellow]Loading model...[/yellow]")
        shell_generator = ShellCommandGenerator(
            model_name=MODEL_CONFIG[selected_model]["model_name"],
            temperature=args.temperature,
            history_file=args.history_file,
            output_command_only=args.output_command_only
        )
        console.print("[green]Model loaded successfully![/green]")
        
        shell_generator.run()

    except Exception as e:
        console.print(f"[red]Initialization error: {e}[/red]")
        logging.error("Initialization error", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
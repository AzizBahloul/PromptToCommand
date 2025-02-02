import platform
import re
import sys
import os
import logging
import argparse
import time
import signal
import json
from pathlib import Path
from typing import Optional, List, Dict, Union
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress
from rich.text import Text
from rich.layout import Layout
from rich import box
import requests
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Initialize console for rich output
console = Console()

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║  ____                            _ _           ____ ____ _____ ║
║ | __ ) ___  _   _ _ __ __ _ _  (_) |__   __ / ___|  _ \_   _|║
║ |  _ \/ _ \| | | | '__/ _` | | | | '_ \ / _` | |  | |_) || |  ║
║ | |_) | (_) | |_| | | | (_| | |_| | |_) | (_| | |__| __/ | |  ║
║ |____/\___/ \__,_|_|  \__, |\__,_|_.__/ \__,_|\____|_|   |_|  ║
║                          |_|                                    ║
║              Your Tunisian Shell Command Assistant             ║
╚══════════════════════════════════════════════════════════════╝
"""

VERSION = "1.0.0"

class ShellCommandGenerator:
    def __init__(
        self,
        model_name: str = "deepseek-r1:1.5b",  # Updated default model name
        temperature: float = 0.7,
        auto_execute: bool = False,
        history_file: Optional[Path] = None,
        max_retries: int = 3,
        timeout: int = 30
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.auto_execute = auto_execute
        self.max_retries = max_retries
        self.timeout = timeout
        self.command_history: List[Dict] = []
        self.ollama_api = "http://localhost:11434/api/generate"
        self.history_file = history_file or Path.home() / ".shell_command_history.json"
        
        # Load command history
        self._load_history()
        # Verify Ollama is running
        self._check_ollama_status()
        
    def _load_history(self) -> None:
        """Load command history from file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.command_history = json.load(f)
        except Exception as e:
            logging.warning(f"Failed to load history: {e}")
            self.command_history = []

    def _save_history(self) -> None:
        """Save command history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.command_history, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save history: {e}")

    def _check_ollama_status(self) -> None:
        """Verify Ollama is running and model is available"""
        with Progress() as progress:
            task = progress.add_task("[cyan]Checking Ollama status...", total=1)
            
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=self.timeout)
                if response.status_code != 200:
                    raise ConnectionError("Ollama service not running")
                
                progress.update(task, advance=0.5)
                
                models = response.json().get("models", [])
                if not any(self.model_name in model.get("name", "") for model in models):
                    console.print(f"[yellow]Model {self.model_name} not found. Downloading...[/yellow]")
                    subprocess.run(["ollama", "pull", self.model_name], check=True)
                
                progress.update(task, advance=0.5)
                
            except requests.exceptions.ConnectionError:
                console.print("[red]Error: Ollama service not running[/red]")
                if platform.system() == "Linux":
                    console.print("[yellow]Start Ollama with: systemctl start ollama[/yellow]")
                else:
                    console.print("[yellow]Please start the Ollama application[/yellow]")
                sys.exit(1)
            except subprocess.CalledProcessError:
                console.print(f"[red]Failed to download model {self.model_name}[/red]")
                sys.exit(1)
            except Exception as e:
                console.print(f"[red]Error checking Ollama status: {e}[/red]")
                sys.exit(1)

    def generate_command(self, prompt: str) -> Optional[str]:
        """Generate shell command using Ollama with retry logic"""
        system_prompt = (
            "You are an expert in shell commands. Generate exactly one safe Linux/Unix command that fulfills the request.\n"
            "Return ONLY the valid command as a single line without ANY explanation, comments, formatting, or punctuation.\n"
            "The command must: \n"
            "- Be safe to execute, operating in the current working directory unless an absolute path is provided\n"
            "- Not contain destructive operations\n"
            "- Be properly escaped if needed\n"
            "- Use only basic utilities\n"
            f"User Request: {prompt}\n"
            "Command:"
        )
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.ollama_api,
                    json={
                        "model": self.model_name,
                        "prompt": system_prompt,
                        "temperature": self.temperature,
                        "stream": False
                    },
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    generated_text = response_data.get('response', '').strip()
                    
                    command = self.extract_command(generated_text)
                    
                    if command and self.validate_command(command):
                        self._add_to_history(prompt, command)
                        return command
                        
                logging.warning(f"Attempt {attempt + 1} failed to generate valid command")
                
            except requests.exceptions.Timeout:
                logging.error("Request timed out")
            except Exception as e:
                logging.error(f"Generation error: {e}")
                
            if attempt < self.max_retries - 1:
                time.sleep(1)  # Wait before retry
                
        return None

    def extract_command(self, generated_text: str) -> Optional[str]:
        """Improved command extraction by selecting the most relevant command.
           If multiple commands are concatenated, it trims off dangerous parts.
        """
        lines = [line.strip() for line in generated_text.splitlines() if line.strip()]
        command_pattern = r'^[\w\./-]+(?:\s+[\w\./-]+)*$'
        for line in reversed(lines):
            if re.fullmatch(command_pattern, line):
                # Special handling for mkdir commands: remove dangerous trailing parts
                if line.startswith("mkdir") and "rm" in line:
                    line = line.split("rm")[0].strip()
                # Special handling for docker commands: remove dangling or incomplete flags
                if line.startswith("docker run") and line.endswith("-u"):
                    line = line[:-2].strip()
                return line
        return None

    def validate_command(self, command: str) -> bool:
        """Enhanced validation with command structure check"""
        if not command or len(command.strip()) == 0:
            return False
            
        # Basic command structure validation (now allowing dots and slashes)
        if not re.match(r'^[\w\./-]+(?:\s+[\w\./-]+)*$', command):
            return False

        # Check for potentially dangerous patterns
        dangerous_patterns = [
            r'rm\s+-rf\s+[/\*]',  # Dangerous rm commands
            r':(){ :|:& };:',     # Fork bomb
            r'>[^>]\s*/dev/',     # Writing to device files
            r'mkfs',              # Filesystem formatting
            r'dd\s+if=',          # Direct disk operations
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                logging.warning(f"Dangerous command pattern detected: {pattern}")
                return False
                
        # Disallow multiple commands and placeholders
        if any(char in command for char in [';', '&&', '||', '`']):
            return False
        if command.strip() == "<think>" or (command.startswith("<") and command.endswith(">")):
            return False
            
        return True

    def _add_to_history(self, prompt: str, command: str) -> None:
        """Add command to history with metadata"""
        self.command_history.append({
            "prompt": prompt,
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "system": platform.system(),
            "executed": False
        })
        self._save_history()

    def execute_command(self, command: str) -> bool:
        """Safely execute a shell command"""
        try:
            if not self.validate_command(command):
                return False
                
            confirm = Prompt.ask(
                "\n[yellow]Do you want to execute this command?[/yellow]",
                choices=["yes", "no"],
                default="no"
            )
            
            if confirm.lower() == "yes":
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
        """Display command history"""
        if not self.command_history:
            console.print("[yellow]No command history available[/yellow]")
            return
            
        console.print("\n[bold]Command History:[/bold]")
        for entry in reversed(self.command_history[-limit:]):
            console.print(Panel(
                f"Prompt: {entry['prompt']}\nCommand: {entry['command']}\nTime: {entry['timestamp']}",
                border_style="blue"
            ))

    def run(self) -> None:
        """Interactive command generation loop with enhanced features"""
        # Display banner and welcome message
        console.print(f"[bold cyan]{BANNER}[/bold cyan]")
        console.print(f"[bold blue]BourguibaGPT[/bold blue] [cyan]v{VERSION}[/cyan]")
        console.print("[dim]Powered by Ollama - Model: {self.model_name}[/dim]")
        console.print("\n[italic]Type 'help' for available commands or 'exit' to quit[/italic]\n")
        
        while True:
            try:
                user_input = Prompt.ask(
                    "\n[bold magenta]🇹🇳 BourguibaGPT[/bold magenta] [bold blue]→[/bold blue]"
                )
                
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
                    command = self.generate_command(user_input)
                    if command:
                        console.print(f"\n[green]Generated command:[/green]")
                        console.print(Panel(command, style="bold white"))
                        
                        if self.auto_execute:
                            self.execute_command(command)
                    else:
                        console.print("[red]Failed to generate a valid command[/red]")
                        
            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                logging.error(f"Error in command loop: {e}")

    def _show_help(self) -> None:
        """Display help information"""
        help_text = """[bold]Available Commands:[/bold]
        
        [cyan]help[/cyan] - Show this help message
        [cyan]history[/cyan] - Show command history
        [cyan]execute <command>[/cyan] - Execute a specific command
        [cyan]exit/quit[/cyan] - Exit BourguibaGPT
        
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
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Enhanced Shell Command Generator")
    parser.add_argument("--model", default="deepseek-r1:1.5b", help="Ollama model name")
    parser.add_argument("--temperature", type=float, default=0.7, help="Generation temperature")
    parser.add_argument("--auto-execute", action="store_true", help="Auto-execute generated commands")
    parser.add_argument("--history-file", type=Path, help="Custom history file location")
    return parser.parse_args()

def main() -> None:
    """Main entry point with improved error handling"""
    try:
        args = parse_arguments()
        generator = ShellCommandGenerator(
            model_name=args.model,
            temperature=args.temperature,
            auto_execute=args.auto_execute,
            history_file=args.history_file
        )
        generator.run()
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()

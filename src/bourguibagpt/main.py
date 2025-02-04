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
from typing import Optional, List, Dict, Any
import requests
import subprocess
import shutil
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress
from rich.text import Text
from rich.layout import Layout
from rich import box

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Initialize console for rich output
console = Console()

# Fix banner alignment
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

VERSION = "2.0.0"

# Import MODEL_CONFIG from config.py
from .config import MODEL_CONFIG

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

def ensure_ollama_installed() -> None:
    """Ensure that Ollama is installed; auto-install on Linux, macOS, and Windows if not present."""
    if shutil.which("ollama") is None:
        console.print("[yellow]Ollama CLI not found. Installing Ollama...[/yellow]")
        system = platform.system()
        if system == "Linux":
            try:
                subprocess.run("curl -fsSL https://ollama.ai/install.sh | sh", shell=True, check=True)
                console.print("[green]Ollama installed successfully.[/green]")
            except Exception as e:
                console.print(f"[red]Failed to install Ollama on Linux: {e}[/red]")
                sys.exit(1)
        elif system == "Darwin":
            try:
                subprocess.run("brew install --cask ollama", shell=True, check=True)
                console.print("[green]Ollama installed successfully on macOS.[/green]")
            except Exception as e:
                console.print(f"[red]Failed to install Ollama on macOS: {e}[/red]")
                sys.exit(1)
        elif system == "Windows":
            try:
                # Using winget to install Ollama. Adjust the package ID as needed.
                subprocess.run("winget install --id Ollama.Ollama -e", shell=True, check=True)
                console.print("[green]Ollama installed successfully on Windows.[/green]")
            except Exception as e:
                console.print(f"[red]Failed to install Ollama on Windows: {e}[/red]")
                sys.exit(1)
        else:
            console.print("[red]Automatic installation is only supported on Linux, macOS, and Windows. Please install Ollama manually.[/red]")
            sys.exit(1)

class ShellCommandGenerator:
    """Shell command generator with enhanced safety and reliability"""
    
    def __init__(
        self,
        model_name: str = "mistral-openorca:7b",
        temperature: float = 0.7,
        auto_execute: bool = False,
        history_file: Optional[Path] = None,
        max_retries: int = 3,
        timeout: int = 30
    ) -> None:
        if not isinstance(temperature, float) or not 0 <= temperature <= 1:
            raise ValueError("Temperature must be a float between 0 and 1")
        if not isinstance(max_retries, int) or max_retries < 1:
            raise ValueError("max_retries must be a positive integer")
            
        self.model_name = model_name
        self.temperature = temperature
        self.auto_execute = auto_execute
        self.max_retries = max_retries
        self.timeout = timeout
        self.command_history: List[Dict[str, Any]] = []
        self.history_file = history_file or Path.home() / ".shell_command_history.json"
        self.ollama_api = "http://localhost:11434/api/generate"
        
        self._load_history()
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
        """Verify Ollama is installed, running, and the selected model is available"""
        ensure_ollama_installed()  # Ensure Ollama is installed
        from rich.progress import Progress
        with Progress() as progress:
            task = progress.add_task("[cyan]Checking Ollama status...", total=1)
            system = platform.system()
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=self.timeout)
                progress.update(task, advance=0.3)
            except requests.exceptions.ConnectionError:
                console.print("[red]Ollama service is not running.[/red]")
                if system == "Linux":
                    try:
                        console.print("[yellow]Attempting to start Ollama service on Linux...[/yellow]")
                        try:
                            subprocess.run(["systemctl", "start", "ollama"], check=True)
                        except subprocess.CalledProcessError:
                            console.print("[yellow]systemctl failed, falling back to running 'ollama serve'...[/yellow]")
                            # Run "ollama serve" in background
                            subprocess.Popen("ollama serve", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        time.sleep(5)
                        response = requests.get("http://localhost:11434/api/tags", timeout=self.timeout)
                        console.print("[green]Ollama service started successfully on Linux.[/green]")
                    except Exception as e:
                        console.print(f"[red]Failed to start Ollama service on Linux: {e}[/red]")
                        sys.exit(1)
                elif system == "Darwin":
                    try:
                        console.print("[yellow]Attempting to start Ollama service on macOS...[/yellow]")
                        subprocess.run(["open", "-a", "Ollama"], check=True)
                        time.sleep(5)
                        response = requests.get("http://localhost:11434/api/tags", timeout=self.timeout)
                        console.print("[green]Ollama service started successfully on macOS.[/green]")
                    except Exception as e:
                        console.print(f"[red]Failed to start Ollama service on macOS: {e}[/red]")
                        sys.exit(1)
                elif system == "Windows":
                    try:
                        console.print("[yellow]Attempting to start Ollama service on Windows...[/yellow]")
                        subprocess.run("start ollama", shell=True, check=True)
                        time.sleep(5)
                        response = requests.get("http://localhost:11434/api/tags", timeout=self.timeout)
                        console.print("[green]Ollama service started successfully on Windows.[/green]")
                    except Exception as e:
                        console.print(f"[red]Failed to start Ollama service on Windows: {e}[/red]")
                        sys.exit(1)
                else:
                    console.print("[yellow]Please start the Ollama application manually.[/yellow]")
                    sys.exit(1)
            if response.status_code != 200:
                raise ConnectionError("Ollama service did not respond as expected")
            progress.update(task, advance=0.3)
            models = response.json().get("models", [])
            if not any(self.model_name in model.get("name", "") for model in models):
                console.print(f"[yellow]Model {self.model_name} not found. Downloading...[/yellow]")
                subprocess.run(["ollama", "pull", self.model_name], check=True)
            progress.update(task, advance=0.4)

    def generate_command(self, prompt: str) -> Dict[str, Any]:
        """Generate shell command from user prompt."""
        try:
            response = self._call_ollama(prompt)
            if not response or 'command' not in response:
                raise ValueError("Failed to generate valid command")
            command = response['command'].strip()
            if not command:
                raise ValueError("Generated command is empty")
            result = {
                'prompt': prompt,
                'command': command,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'error': None
            }
            self.command_history.append(result)
            self._save_history()
            return result
        except Exception as e:
            error_result = {
                'prompt': prompt,
                'command': None, 
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
            self.command_history.append(error_result)
            self._save_history()
            console.print(f"[red]Error generating command: {str(e)}[/red]")
            return error_result

    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """Call Ollama API with retry logic."""
        context = get_os_info()
        message = f"""
        Operating System: {context}
        Generate a shell command for: {prompt}
        Return only the command without explanation.
        """
        data = {
            "model": self.model_name,
            "prompt": message,
            "temperature": self.temperature,
            "stream": False
        }
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.ollama_api,
                    json=data,
                    timeout=self.timeout
                )
                response.raise_for_status()
                result = response.json()
                if "response" not in result:
                    raise ValueError("Invalid API response format")
                command = result["response"].strip()
                command = command.replace('```shell', '').replace('```', '').strip()
                lines = [line.strip() for line in command.splitlines()]
                lines = [line for line in lines if line.lower() not in ["bash", "zsh", "sh"]]
                command = " ".join(lines).strip()
                return {"command": command}
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Failed to call Ollama API after {self.max_retries} attempts: {e}")
                time.sleep(1)
        return {"command": None}

    def execute_command(self, command: str, confirm_execution: bool = True) -> bool:
        """Safely execute a shell command"""
        try:
            # Basic validation (can be extended)
            safe_pattern = r'^[\w./-]+(?:\s+(?:[\w./-]+|>>?\s*[\w./-]+))*$'
            if not re.match(safe_pattern, command):
                console.print("[red]Command validation failed.[/red]")
                return False
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

    def run(self) -> None:
        """Interactive command generation loop with enhanced features"""
        console.print(f"[bold cyan]{BANNER}[/bold cyan]")
        console.print(f"[bold blue]BourguibaGPT[/bold blue] [cyan]v{VERSION}[/cyan]")
        console.print(f"[dim]Powered by Ollama - Model: {self.model_name}[/dim]")
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
                    command = user_input[8:].trip()
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
                            console.print("[blue]Continuing with a new prompt...[/blue]")
                    else:
                        console.print("[red]Failed to generate a valid command[/red]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Exiting...[/yellow]")
                break
            except Exception as e:
                logging.error(f"Error in command loop: {e}")

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Enhanced Shell Command Generator")
    parser.add_argument("--model", default="mistral-openorca:7b", help="Ollama model name")
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Generation temperature (0.0-1.0)",
        choices=[x/10 for x in range(11)]
    )
    parser.add_argument("--auto-execute", action="store_true", help="Auto-execute generated commands")
    parser.add_argument("--history-file", type=Path, help="Custom history file location")
    return parser.parse_args()

def main() -> None:
    """Main entry point with dependency check"""
    try:
        # Ensure Ollama is installed before proceeding.
        ensure_ollama_installed()
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
            status = "✓" if system_ram >= config["ram_threshold"] else "✗"
            console.print(f"• {key.capitalize()} [{status}]: {config['description']}")
        
        selected_model_key = Prompt.ask(
            "\n[bold]Select a model[/bold] (t=Tiny / m=Medium / l=Large)",
            choices=["t", "m", "l"],
            default="m"
        )
        model_map = {
            "t": ("tiny", MODEL_CONFIG["tiny"]["model_name"]),
            "m": ("medium", MODEL_CONFIG["medium"]["model_name"]),
            "l": ("large", MODEL_CONFIG["large"]["model_name"])
        }
        selected, model_name = model_map.get(selected_model_key, ("medium", MODEL_CONFIG["medium"]["model_name"]))
        
        console.print(f"\n[green]Using model: {model_name}[/green]")
        generator = ShellCommandGenerator(
            model_name=model_name,
            temperature=args.temperature,
            auto_execute=args.auto_execute,
            history_file=args.history_file
        )
        generator.run()
    except Exception as e:
        console.print(f"[red]Initialization error: {e}[/red]")
        logging.error("Initialization error", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
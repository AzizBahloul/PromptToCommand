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
from typing import Optional, List, Dict, Any, Tuple
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

from .config import MODEL_CONFIG, load_user_preferences, save_user_preferences
from .windows import install_ollama, verify_installation, start_ollama_service
from .validators import CommandValidator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Initialize console for rich output
console = Console()

VERSION = "2.0.0"  # Version constant

def get_rainbow_colors() -> List[str]:
    return ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']

def get_terminal_size() -> Tuple[int, int]:
    return shutil.get_terminal_size()

def clear_screen() -> None:
    console.clear()

BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║  ____                            _ _           ____ ____ ____ ║
║ | __ ) ___  _   _ _ __ __ _ _  (_) |__   __ / ___|  _ \_   _| ║
║ |  _ \/ _ \| | | | '__/ _` | | | | '_ \ / _` | |  | |_) || |  ║
║ | |_) | (_) | |_| | | | (_| | |_| | |_) | (_| | |__| __/ | |  ║
║ |____/\___/ \__,_|_|  \__, |\__,_|_.__/ \__,_| \____|_|   |_| ║
║                          |_|                                  ║
║             Your Tunisian Shell Command Assistant             ║
║                                                               ║
║                     Powered by Ollama AI                      ║
 ═══════════════════════════════════════════════════════════════╝
"""

def display_animated_banner() -> None:
    # ANSI escape codes constants
    BRIGHT = '\033[1m'
    GLOW = '\033[38;5;255m'
    RESET = '\033[0m'
    try:
        colors = get_rainbow_colors()
        term_width = get_terminal_size().columns
        lines = BANNER.strip('\n').split('\n')
        # Calculate banner width and center it
        banner_width = max(len(line) for line in lines if line)
        padding = max(0, (term_width - banner_width) // 2)
        # Animate banner appearance line by line
        for i in range(len(lines)):
            clear_screen()
            color = colors[i % len(colors)]
            for j in range(i + 1):
                if lines[j].strip():
                    print(' ' * padding + f"{color}{BRIGHT}{GLOW}{lines[j]}{RESET}")
            time.sleep(0.05)
        # Animate banner glow effect
        for i in range(10):
            clear_screen()
            color = colors[i % len(colors)]
            intensity = BRIGHT if i % 2 else '\033[2m'
            for line in lines:
                if line.strip():
                    print(' ' * padding + f"{color}{intensity}{line}{RESET}")
            time.sleep(0.1)
    except Exception as e:
        logging.exception("Error during banner animation")
        print(BANNER)
    # Wait a bit before clearing the banner
    time.sleep(2)
    clear_screen()

def run() -> None:
    """Main entry point for banner display"""
    clear_screen()
    display_animated_banner()

def ensure_ollama_installed() -> None:
    """Ensure Ollama is installed before proceeding"""
    if shutil.which("ollama") is None:
        console.print("[yellow]Ollama CLI not found. Installing Ollama...[/yellow]")
        system = platform.system()
        if system == "Windows":
            install_ollama()
            if not verify_installation():
                console.print("[red]Ollama installation failed![/red]")
                sys.exit(1)
            ollama_path = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Ollama"
            os.environ["PATH"] = f"{ollama_path};{os.environ['PATH']}"
        elif system == "Linux":
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
        else:
            console.print("[red]Automatic installation is only supported on Linux, macOS, and Windows. Please install Ollama manually.[/red]")
            sys.exit(1)

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

def select_model(system_ram: float) -> str:
    """Interactive model selection with saved preference"""
    models = []
    for key, config in MODEL_CONFIG.items():
        models.append({
            'name': key.capitalize(),
            'model_name': config['model_name'],
            'ram': config['ram_threshold'],
            'description': config['description']
        })
    prefs = load_user_preferences()
    saved_model = prefs.get("preferred_model")
    default_index = 0
    if saved_model:
        for i, m in enumerate(models):
            if m['model_name'] == saved_model:
                default_index = i
                break
    console.print("[bold]Available Models:[/bold]")
    for i, model in enumerate(models):
        status = "✓" if system_ram >= model['ram'] else "✗"
        console.print(f"{i+1}. {status} {model['name']} ({model['model_name']})")
    choice = Prompt.ask(
        "\n[bold cyan]Select model[/bold cyan] (number)",
        choices=[str(i+1) for i in range(len(models))],
        default=str(default_index+1)
    )
    return models[int(choice)-1]['model_name']

def is_gpu_available() -> bool:
    """Check if NVIDIA GPU is available using nvidia-smi"""
    try:
        subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
        return True
    except Exception:
        return False

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
            logging.exception("Failed to load history")
            self.command_history = []

    def _save_history(self) -> None:
        """Save command history to file"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.command_history, f, indent=2)
        except Exception as e:
            logging.exception("Failed to save history")

    def _check_ollama_status(self) -> None:
        """Verify Ollama is installed, running, and the selected model is available"""
        ensure_ollama_installed()
        # Display GPU detection status
        if is_gpu_available():
            console.print("[green]GPU detected.[/green]")
        else:
            console.print("[yellow]No GPU detected.[/yellow]")
        
        system = platform.system()
        with Progress() as progress:
            task = progress.add_task("[cyan]Checking Ollama status...", total=1)
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=self.timeout)
                progress.update(task, advance=0.3)
            except requests.exceptions.ConnectionError:
                console.print("[red]Ollama service is not running.[/red]")
                if system == "Windows":
                    try:
                        start_ollama_service()
                        time.sleep(10)
                        response = requests.get("http://localhost:11434/api/tags", timeout=self.timeout)
                    except Exception as e:
                        console.print(f"[red]Failed to start Ollama on Windows: {e}[/red]")
                        sys.exit(1)
                elif system == "Linux":
                    try:
                        console.print("[yellow]Attempting to start Ollama service on Linux...[/yellow]")
                        try:
                            subprocess.run(["systemctl", "start", "ollama"], check=True)
                        except subprocess.CalledProcessError:
                            console.print("[yellow]systemctl failed, running 'ollama serve'...[/yellow]")
                            serve_cmd = "ollama serve --gpu" if is_gpu_available() else "ollama serve"
                            subprocess.Popen(serve_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            logging.exception("Error generating command")
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
        """Call Ollama API with retry logic, refined prompt, and improved output instructions."""
        context = get_os_info()
        examples = """
Examples of valid commands:
1) ls -la
2) grep 'pattern' file.txt
3) tar -czf archive.tar.gz folder/
4) docker build -t image:latest .
"""
        message = f"""
Operating System: {context}
You are a shell command generator that should return only the command.
No extra text.

User prompt: {prompt}
{examples}
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
                # Clean up the command output
                command = result["response"].strip()
                command = command.replace('```shell', '').replace('```', '').strip()
                lines = [line.strip() for line in command.splitlines()]
                lines = [line for line in lines if line.lower() not in ["bash", "zsh", "sh"]]
                command = " ".join(lines).strip()
                return {"command": command}
            except requests.exceptions.RequestException as e:
                logging.warning(f"Ollama API call attempt {attempt+1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Failed to call Ollama API after {self.max_retries} attempts: {e}")
                time.sleep(1)
        return {"command": None}

    def execute_command(self, command: str, confirm_execution: bool = True) -> bool:
        """Safely execute a shell command with validation, feedback, and improved output."""
        try:
            is_valid, error = CommandValidator.validate(command)
            if not is_valid:
                console.print(f"[red]Command validation failed: {error}[/red]")
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
                feedback = Prompt.ask(
                    "\n[yellow]Rate the command success on a scale of 1-5 (1=poor, 5=excellent):[/yellow]",
                    choices=["1", "2", "3", "4", "5"],
                    default="3"
                )
                self.command_history[-1]['feedback'] = feedback
                self._save_history()
                return True
            else:
                console.print("[red]Command failed[/red]")
                if result.stderr:
                    console.print(Panel(result.stderr, title="Error", border_style="red"))
                return False
        except Exception as e:
            logging.exception("Error during command execution")
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
        
[cyan]help[/cyan]          - Show this help message
[cyan]history[/cyan]       - Show command history
[cyan]execute <command>[/cyan] - Execute a specific command
[cyan]model[/cyan]/[cyan]sibourguiba[/cyan] - Change the selected model
[cyan]exit[/cyan]/[cyan]quit[/cyan]    - Exit BourguibaGPT

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
        """Interactive command generation loop with enhanced features and model change command."""
        display_animated_banner()
        console.print(f"[bold blue]BourguibaGPT[/bold blue] [cyan]v{VERSION}[/cyan]")
        console.print(f"[dim]Powered by Ollama - Model: {self.model_name}[/dim]")
        console.print("\n[italic]Type 'help' for commands or 'exit' to quit[/italic]\n")
        console.print("[yellow]Tip: You can change the model anytime by typing 'sibourguiba'.[/yellow]")
        
        # Add GPU detection status here
        if is_gpu_available():
            console.print("[green]GPU detected[/green]")
        else:
            console.print("[yellow]No GPU detected: Falling back to CPU mode.[/yellow]")
        
        system_ram = get_system_memory()
        while True:
            try:
                user_input = Prompt.ask("\n[bold magenta]🇹🇳 BourguibaGPT[/bold magenta] [bold blue]→[/bold blue]")
                if not user_input.strip():
                    console.print("[yellow]No input received. Please type a command or 'help'.[/yellow]")
                    continue
                if user_input.lower() in ['exit', 'quit']:
                    raise SystemExit
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.lower() == 'history':
                    self.show_history()
                elif user_input.lower() in ['model', 'sibourguiba']:
                    new_model = select_model(system_ram)
                    save_user_preferences(new_model)
                    self.model_name = new_model
                    console.print(f"[green]Model changed to {new_model}[/green]")
                    self._check_ollama_status()
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
            except SystemExit:
                console.print("[yellow]Goodbye![/yellow]")
                break
            except Exception as e:
                logging.exception("Error in command loop")
                console.print(f"[red]Unexpected error: {e}[/red]")
                break

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
    parser.add_argument("--change-model", action="store_true", help="Change and save a new model preference")
    return parser.parse_args()

def main() -> None:
    """Main entry with model memory feature"""
    try:
        ensure_ollama_installed()
        args = parse_arguments()
        system_ram = get_system_memory()
        os_info = get_os_info()
        
        prefs = load_user_preferences()
        saved_model = prefs.get("preferred_model")

        if args.change_model or not saved_model:
            model_name = select_model(system_ram)
            save_user_preferences(model_name)
        elif args.model:
            model_name = args.model
            save_user_preferences(model_name)
        else:
            model_name = saved_model
            console.print(f"[green]Using saved model: {model_name}[/green]")
            console.print("[yellow]Use '--change-model' to switch models[/yellow]")

        console.print(f"[bold cyan]System Information:[/bold cyan]")
        console.print(f"• OS: {os_info}")
        console.print(f"• RAM: {system_ram:.1f} GB")
        recommended = recommend_model(system_ram)
        console.print(f"• Recommended Model: {MODEL_CONFIG[recommended]['description']}")
        
        console.print("\n[bold]Available Models:[/bold]")
        for key, config in MODEL_CONFIG.items():
            status = "✓" if system_ram >= config["ram_threshold"] else "✗"
            console.print(f"• {key.capitalize()} [{status}]: {config['description']}")
        
        console.print("\n[bold yellow]Please select a model using your keyboard's arrow keys if needed:[/bold yellow]")
        generator = ShellCommandGenerator(
            model_name=model_name,
            temperature=args.temperature,
            auto_execute=args.auto_execute,
            history_file=args.history_file
        )
        generator.run()
    except Exception as e:
        logging.exception("Initialization error")
        console.print(f"[red]Initialization error: {e}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main()

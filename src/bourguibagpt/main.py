import platform
import re
import sys
import os
import logging
import argparse
import time
import signal
import json
import shlex
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
import requests
import subprocess
import shutil
from datetime import datetime
import psutil

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress
from rich.text import Text
from rich.layout import Layout
from rich import box

from .config import MODEL_NAME
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
        # Animate banner appearance line by line (reduced delay)
        for i in range(len(lines)):
            clear_screen()
            color = colors[i % len(colors)]
            for j in range(i + 1):
                if lines[j].strip():
                    print(' ' * padding + f"{color}{BRIGHT}{GLOW}{lines[j]}{RESET}")
            time.sleep(0.02)  # reduced from 0.05 seconds
        # Animate banner glow effect (faster effect)
        for i in range(5):  # reduced number of cycles
            clear_screen()
            color = colors[i % len(colors)]
            intensity = BRIGHT if i % 2 else '\033[2m'
            for line in lines:
                if line.strip():
                    print(' ' * padding + f"{color}{intensity}{line}{RESET}")
            time.sleep(0.05)  # reduced from 0.1 seconds
    except Exception as e:
        logging.exception("Error during banner animation")
        print(BANNER)
    # Wait a bit before clearing the banner
    time.sleep(1)  # reduced from 2 seconds
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
    mem = psutil.virtual_memory()
    return mem.total / (1024 ** 3)

def get_free_memory() -> float:
    """Retrieve free (available) system memory in GB."""
    mem = psutil.virtual_memory()
    return mem.available / (1024 ** 3)

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


def resolve_user_directory(target: str) -> Optional[Path]:
    """Resolve an XDG user directory without assuming a username or fixed path."""
    normalized = re.sub(r"[^a-zA-Z0-9_]", "", target).upper()
    if not normalized:
        return None

    if shutil.which("xdg-user-dir"):
        try:
            result = subprocess.run(
                ["xdg-user-dir", normalized],
                capture_output=True, text=True, check=True
            )
            configured = result.stdout.strip()
            if configured:
                return Path(configured).expanduser()
        except (OSError, subprocess.CalledProcessError):
            pass

    user_dirs = Path.home() / ".config" / "user-dirs.dirs"
    if user_dirs.exists():
        try:
            for line in user_dirs.read_text().splitlines():
                if line.startswith(f"XDG_{normalized}_DIR="):
                    configured = line.split("=", 1)[1].strip().strip('"')
                    directory = Path(os.path.expandvars(configured.replace("$HOME", str(Path.home()))))
                    return directory
        except OSError:
            pass

    return None


def resolve_navigation_target(action: str, target: str) -> Optional[Dict[str, Any]]:
    """Turn a model-identified navigation target into a local command."""
    if action.lower() not in {"navigate", "open", "change_directory"}:
        return None
    if target.strip().lower() in {"current", "current_directory", "working_directory"}:
        return {"command": "pwd", "confidence": 1.0}
    directory = resolve_user_directory(target)
    if directory is None:
        return None
    return {"command": f"cd {shlex.quote(str(directory))}", "confidence": 1.0}


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

def wait_for_service(url: str, total_timeout: int = 30, poll_interval: float = 1.0) -> bool:
    """Poll the Ollama API endpoint until it's available or timeout is reached."""
    start_time = time.time()
    while (time.time() - start_time) < total_timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(poll_interval)
    return False

class ShellCommandGenerator:
    """Shell command generator with enhanced safety and reliability"""
    
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        temperature: float = 0.0,
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
        ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        if not ollama_host.startswith(("http://", "https://")):
            ollama_host = f"http://{ollama_host}"
        self.ollama_base_url = ollama_host.rstrip("/")
        self.ollama_api = f"{self.ollama_base_url}/api/generate"
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
                response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=self.timeout)
                progress.update(task, advance=0.3)
            except requests.exceptions.ConnectionError:
                console.print("[red]Ollama service is not running.[/red]")
                if system == "Windows":
                    try:
                        start_ollama_service()
                        if wait_for_service(f"{self.ollama_base_url}/api/tags", total_timeout=15):
                            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=self.timeout)
                        else:
                            console.print("[red]Ollama service did not start in time on Windows.[/red]")
                            sys.exit(1)
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
                        if wait_for_service(f"{self.ollama_base_url}/api/tags", total_timeout=15):
                            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=self.timeout)
                            console.print("[green]Ollama service started successfully on Linux.[/green]")
                        else:
                            console.print("[red]Ollama service did not start in time on Linux.[/red]")
                            sys.exit(1)
                    except Exception as e:
                        console.print(f"[red]Failed to start Ollama service on Linux: {e}[/red]")
                        sys.exit(1)
                elif system == "Darwin":
                    try:
                        console.print("[yellow]Attempting to start Ollama service on macOS...[/yellow]")
                        subprocess.run(["open", "-a", "Ollama"], check=True)
                        if wait_for_service("http://localhost:11434/api/tags", total_timeout=15):
                            response = requests.get("http://localhost:11434/api/tags", timeout=self.timeout)
                            console.print("[green]Ollama service started successfully on macOS.[/green]")
                        else:
                            console.print("[red]Ollama service did not start in time on macOS.[/red]")
                            sys.exit(1)
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
                'confidence': response.get('confidence'),
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
                'confidence': None,
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
        message = f"""
Operating system: {context}
Current working directory: {Path.cwd()}

You convert one natural-language request into one safe shell decision.
Return exactly one JSON object with these four keys and no markdown or explanation:
{{"action":"command|navigate", "target":"", "command":"", "confidence":0.0}}

Rules:
1. Use action "command" for shell commands. Use action "navigate" only when the user
   explicitly asks to go/open/change directory. For navigation, put the requested user
   directory name in target (Desktop, Documents, Downloads, etc.) and leave command empty.
2. A request to locate, show, or identify the current folder means action "command",
   target "current_directory", command "pwd".
3. Preserve paths exactly as written. Never replace a relative path such as "src" with
   the working directory, invent paths, or add arbitrary limits.
4. Return one command or a pipeline only. Do not use explanations, aliases, placeholders,
   command substitution, chaining, redirection, or destructive operations unless explicitly requested.
5. If the request is ambiguous or unsafe, return an empty command and low confidence.

Examples:
User: locate this folder
JSON: {{"action":"command","target":"current_directory","command":"pwd","confidence":0.99}}
User: move to the desktop
JSON: {{"action":"navigate","target":"Desktop","command":"","confidence":0.99}}
User: find Python files under src
JSON: {{"action":"command","target":"","command":"find src -type f -name '*.py'","confidence":0.90}}
User: list hidden files here
JSON: {{"action":"command","target":"","command":"ls -la","confidence":0.99}}

User request: {prompt}
"""
        data = {
            "model": self.model_name,
            "prompt": message,
            "temperature": self.temperature,
            "stream": False,
            "format": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["command", "navigate"]},
                    "target": {"type": "string"},
                    "command": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["action", "target", "command", "confidence"]
            },
            "think": False,
            "keep_alive": "5m",
            "options": {"temperature": 0.0, "num_predict": 96}
        }
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.ollama_api,
                    json=data,
                    timeout=self.timeout  # you may lower self.timeout if appropriate (e.g., 10)
                )
                response.raise_for_status()
                result = response.json()
                if "response" not in result:
                    raise ValueError("Invalid API response format")
                raw_response = result["response"].strip()
                confidence = None
                try:
                    response_data = json.loads(raw_response)
                    command = response_data["command"]
                    confidence = response_data.get("confidence")
                    navigation = resolve_navigation_target(
                        response_data.get("action", "command"),
                        response_data.get("target", "")
                    )
                    if navigation:
                        return navigation
                except (json.JSONDecodeError, KeyError, TypeError):
                    # Keep compatibility with older local models that ignore format.
                    command = raw_response.replace('```shell', '').replace('```', '').strip()
                    lines = [line.strip() for line in command.splitlines()]
                    lines = [line for line in lines if line.lower() not in ["bash", "zsh", "sh"]]
                    command = " ".join(lines).strip()
                return {"command": command, "confidence": confidence}
            except requests.exceptions.RequestException as e:
                logging.warning(f"Ollama API call attempt {attempt+1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Failed to call Ollama API after {self.max_retries} attempts: {e}")
                time.sleep(0.5)  # reduced from 1 second
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
[cyan]model[/cyan]          - Show the fixed local model
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
        
        # Add GPU detection status here
        if is_gpu_available():
            console.print("[green]GPU detected[/green]")
        else:
            console.print("[yellow]No GPU detected: Falling back to CPU mode.[/yellow]")
        
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
                    console.print(f"[green]Using fixed local model: {self.model_name}[/green]")
                elif user_input.lower().startswith('execute '):
                    command = user_input[8:].strip()
                    self.execute_command(command)
                else:
                    result = self.generate_command(user_input)
                    if (result.get("command")):
                        console.print(f"\n[green]Generated command:[/green]")
                        console.print(Panel(result["command"], style="bold white"))
                        if result.get("confidence") is not None:
                            console.print(
                                f"[dim]Decision confidence: {result['confidence']:.0%}[/dim]"
                            )
                        choice = Prompt.ask(
                            "\n[yellow]Execute this generated command? (y/n)[/yellow]",
                            choices=["y", "n"],
                            default="y"
                        )
                        if (choice.lower() == "y"):
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
    parser.add_argument("--auto-execute", action="store_true", help="Auto-execute generated commands")
    parser.add_argument("--history-file", type=Path, help="Custom history file location")
    return parser.parse_args()

def main() -> None:
    """Main entry with model memory feature"""
    try:
        ensure_ollama_installed()
        args = parse_arguments()
        free_memory = get_free_memory()
        os_info = get_os_info()
        
        console.print(f"[bold cyan]System Information:[/bold cyan]")
        console.print(f"• OS: {os_info}")
        console.print(f"• Free Memory: {free_memory:.1f} GB")
        console.print(f"• Fixed local model: {MODEL_NAME}")

        generator = ShellCommandGenerator(
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

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
from typing import Optional, List, Dict, Union, Any
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

class ShellCommandGenerator:
    """Shell command generator with enhanced safety and reliability"""
    
    def __init__(
        self,
        model_name: str = "mistral-openorca",
        temperature: float = 0.7,
        auto_execute: bool = False,
        history_file: Optional[Path] = None,
        max_retries: int = 3,
        timeout: int = 30
    ) -> None:
        # Validate parameters
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
        self.ollama_api = "http://localhost:11434/api/generate"
        self.history_file = history_file or Path.home() / ".shell_command_history.json"
        
        # Load history and check Ollama status
        self._load_history()
        self._check_ollama_status()
        
    def get_os_info(self) -> str:
        """Detect the operating system and, if Linux, the distribution."""
        os_name = platform.system()
        if (os_name == "Linux"):
            try:
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME"):
                            # Format: PRETTY_NAME="Ubuntu 20.04.2 LTS"
                            return line.split("=")[1].strip().strip('"')
            except Exception as e:
                logging.warning(f"Could not detect Linux distribution: {e}")
        return os_name

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
            print(f"Error generating command: {str(e)}")
            return error_result

    def _extract_command(self, text: str) -> Optional[str]:
        """Extract command with improved parsing"""
        # Look for CMD: prefix
        if match := re.search(r'CMD:\s*(.+)$', text, re.MULTILINE):
            command = match.group(1).strip()
            # Basic command structure validation
            if re.match(r'^[\w.-]+(\s+[\w."\'*?/-]+)*$', command):
                return command
        return None

    def _validate_command(self, command: str) -> bool:
        """Simplified but strict command validation"""
        # Whitelist of safe commands
        SAFE_COMMANDS = {
            'ls': r'-[altrh]*',
            'mkdir': r'[\w.-]+',
            'touch': r'[\w.-]+',
            'cat': r'[\w.-]+',
            'echo': r'"[^"]*"',
            'pwd': '',
            'find': r'\. -name "[\w.*]+"',
            'grep': r'-[ivr]+ "[\w ]+"',
            'cd': r'[\w./-]*'  # Added cd command support
        }
        
        # Check command against whitelist
        parts = command.split(maxsplit=1)
        base_cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ''
        
        if base_cmd not in SAFE_COMMANDS:
            return False
            
        # Validate arguments against pattern
        if pattern := SAFE_COMMANDS[base_cmd]:
            return bool(re.match(pattern, args))
            
        return True

    def validate_command(self, command: str) -> bool:
        """Validates commands against dangerous patterns"""
        safe_pattern = r'^[\w./-]+(?:\s+(?:[\w./-]+|>>?\s*[\w./-]+))*$'
        dangerous_patterns = [
            r'rm\s+-[rf]{2}',
            r'rm\s+[/*]',
            r'>\s*/dev/',
            r'mkfs',
            r'dd',
            r'chmod\s+[0-7]{4}'
        ]
        if not command:
            return False
            
        # Allow safer patterns including redirects
        if not re.match(safe_pattern, command):
            return False

        # Check for dangerous patterns        
        return not any(re.search(p, command) for p in dangerous_patterns)

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

    def execute_command(self, command, confirm_execution=False):
        # Ensure command is a string and not a command history dictionary
        if isinstance(command, dict):
            command = command['command']
        elif isinstance(command, list):
            command = " ".join(command)
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            console.print(result.stdout)
        except Exception as e:
            console.print(f"[red]Error executing command: {e}[/red]")

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
        console.print(f"[dim]Powered by Ollama - Model: {self.model_name}[/dim]")
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
                    command = user_input[8:].trip()
                    self.execute_command(command)
                else:
                    command = self.generate_command(user_input)
                    if command:
                        console.print(f"\n[green]Generated command:[/green]")
                        console.print(Panel(command["command"], style="bold white"))
                        
                        choice = Prompt.ask(
                            "\n[yellow]Type 'e' to execute the generated command and exit, or 'n' to return to the prompt:[/yellow]",
                            choices=["e", "n"],
                            default="n"
                        )
                        if choice.lower() == "e":
                            self.execute_command(command, confirm_execution=False)
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

    def _call_ollama(self, prompt: str) -> Dict[str, Any]:
        """Call Ollama API with retry logic."""
        context = self.get_os_info()
        
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
                
                # Remove any standalone shell prefixes from the command
                lines = [line.strip() for line in command.splitlines()]
                lines = [line for line in lines if line.lower() not in ["bash", "zsh", "sh"]]
                command = " ".join(lines).strip()
                
                return {"command": command}
                
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise ValueError(f"Failed to call Ollama API after {self.max_retries} attempts: {e}")
                time.sleep(1)
                
        return {"command": None}

    def call_ollama_api(self, prompt: str) -> dict:
        """Call Ollama API with retry logic and better error handling"""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "temperature": self.temperature
                    },
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                if "response" in result:
                    command = result["response"].strip()
                    return {"command": command}
                else:
                    raise ValueError("Invalid response format from Ollama API")
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    logging.error(f"Failed to call Ollama API: {str(e)}")
                    return {"command": f"echo 'Error: Unable to generate command - {str(e)}'"}
                time.sleep(1)
                continue
                
            except (ValueError, KeyError) as e:
                logging.error(f"Error parsing Ollama response: {str(e)}")
                return {"command": f"echo 'Error: Invalid response from Ollama'"}
        
        return {"command": "echo 'Error: Maximum retries exceeded'"}

# Add parameter validation to parse_arguments
def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Enhanced Shell Command Generator")
    parser.add_argument("--model", default="mistral-openorca", help="Ollama model name")
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Generation temperature (0.0-1.0)",
        choices=[x/10 for x in range(11)]  # Restrict to valid range
    )
    parser.add_argument("--auto-execute", action="store_true", help="Auto-execute generated commands")
    parser.add_argument("--history-file", type=Path, help="Custom history file location")
    return parser.parse_args()

# Enhance error handling in main
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
        try:
            generator.run()
        except KeyboardInterrupt:
            console.print("\n[yellow]Gracefully shutting down...[/yellow]")
        except Exception as e:
            console.print(f"[red]Runtime error: {e}[/red]")
            logging.error("Runtime error", exc_info=True)
            sys.exit(2)
    except Exception as e:
        console.print(f"[red]Initialization error: {e}[/red]")
        logging.error("Initialization error", exc_info=True) 
        sys.exit(1)

if __name__ == '__main__':
    main()

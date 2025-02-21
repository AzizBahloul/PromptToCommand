import subprocess
import os
from pathlib import Path
import requests
import shutil
from rich.console import Console

console = Console()

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

def install_ollama() -> None:
    """Install Ollama on Windows using available methods"""
    try:
        # Try winget first
        subprocess.run("winget install --id Ollama.Ollama -e", shell=True, check=True)
    except:
        # Fallback to direct download
        url = "https://ollama.com/download/OllamaSetup.exe"
        installer = Path.home() / "Downloads" / "OllamaSetup.exe"
        with requests.get(url, stream=True) as r:
            with open(installer, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        subprocess.run(f"{installer} /S", shell=True, check=True)

def verify_installation() -> bool:
    """Verify Ollama installation and PATH"""
    ollama_path = Path(os.environ["LOCALAPPDATA"]) / "Programs" / "Ollama"
    return ollama_path.exists()

def start_ollama_service() -> None:
    """Start Ollama as a service or background process"""
    # Display GPU detection status
    if is_gpu_available():
        console.print("[green]GPU detected.[/green]")
    else:
        console.print("[yellow]No GPU detected.[/yellow]")
    try:
        # Try starting as a service first
        subprocess.run("sc query Ollama", shell=True, check=True)
        subprocess.run("net start Ollama", shell=True, check=True)
    except:
        # Fallback to running Ollama in the background without a new CMD window
        serve_cmd = "ollama serve --gpu" if is_gpu_available() else "ollama serve"
        subprocess.Popen(
            serve_cmd,
            shell=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
        )
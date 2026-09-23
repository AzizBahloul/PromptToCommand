import platform
import shutil
import subprocess
import sys
from pathlib import Path

from setuptools import setup
from setuptools.command.install import install

# config.py has no dependencies of its own, so it can be read directly
# without a full package import, keeping this in sync with the model the
# app actually uses instead of duplicating the name here.
sys.path.insert(0, str(Path(__file__).parent / "src"))
from bourguibagpt.config import MODEL_NAME

class InstallWithOllama(install):
    """Install the local Ollama runtime when the package is installed directly."""

    def run(self):
        super().run()
        if not shutil.which("ollama"):
            system = platform.system()
            if system == "Linux":
                subprocess.run(
                    "curl -fsSL https://ollama.com/install.sh | sh",
                    shell=True,
                    check=True,
                )
            elif system == "Darwin":
                subprocess.run(["brew", "install", "--cask", "ollama"], check=True)
            elif system == "Windows":
                subprocess.run(
                    ["winget", "install", "--id", "Ollama.Ollama", "-e"],
                    check=True,
                )
            else:
                raise RuntimeError(f"Automatic Ollama installation is not supported on {system}")

        subprocess.run(["ollama", "pull", MODEL_NAME], check=True)

if __name__ == "__main__":
    setup(cmdclass={"install": InstallWithOllama})
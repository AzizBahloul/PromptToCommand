import platform
import shutil
import subprocess

from setuptools import setup
from setuptools.command.install import install

MODEL_NAME = "qwen3.5:0.8b"

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
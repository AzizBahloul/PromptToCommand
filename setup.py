from setuptools import setup
from setuptools.command.install import install
import subprocess
import os
import sys

class CustomInstall(install):
    def run(self):
        # Run the standard install process first
        install.run(self)
        # Run the post-install commands only when not building distributions
        if os.environ.get("SKIP_POST_INSTALL", "0") == "1":
            return
        # Only run post-install commands when this is an installation command
        if any(arg in sys.argv for arg in ['install']):
            try:
                print("Installing Ollama...")
                subprocess.run("curl -fsSL https://ollama.com/install.sh | sh", shell=True, check=True)
                print("Pulling model deepseek-r1:1.5b...")
                subprocess.run("ollama pull deepseek-r1:1.5b", shell=True, check=True)
            except Exception as e:
                print(f"Error during post-installation: {e}")

if __name__ == "__main__":
    setup(cmdclass={'install': CustomInstall})
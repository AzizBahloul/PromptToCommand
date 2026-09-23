import re
import logging
import shlex
from typing import Tuple

class CommandValidator:
    """Validates shell commands for safety"""
    
    SAFE_COMMANDS = {
        'mkdir', 'ls', 'cd', 'pwd', 'cp', 'mv', 'rm', 'touch',
        'cat', 'echo', 'grep', 'find', 'head', 'tail', 'chmod',
        'chown', 'ln', 'ps', 'kill', 'df', 'du', 'tar', 'gzip',
        'gunzip', 'bzip2', 'bunzip2', 'zip', 'unzip', 'ping',
        'curl', 'wget', 'scp', 'ssh', 'rsync'
    }
    
    @classmethod
    def validate(cls, command: str) -> Tuple[bool, str]:
        """
        Validates a shell command
        Returns: (is_valid, error_message)
        """
        if not command or not command.strip():
            return False, "Empty command"
            
        # Permit pipelines, but validate every command in the pipeline separately.
        # Other shell operators remain blocked to prevent chaining/substitution.
        if re.search(r"[;&<>`$()]|\|\||&&", command):
            logging.warning("Shell control or substitution operator detected")
            return False, "Shell control or substitution operator is not allowed"

        safe_pattern = r'''^[a-zA-Z0-9_\-./:*?\[\]'" ]+$'''
        for pipeline_part in command.strip().split("|"):
            try:
                parts = shlex.split(pipeline_part)
            except ValueError:
                return False, "Invalid shell quoting"
            if not parts:
                return False, "Empty pipeline command"

            base_cmd = parts[0]
            if base_cmd not in cls.SAFE_COMMANDS:
                logging.warning(f"Command '{base_cmd}' not in allowed list")
                return False, f"Command '{base_cmd}' not in allowed list"

            for arg in parts[1:]:
                if not re.match(safe_pattern, arg):
                    logging.warning(f"Invalid argument format: {arg}")
                    return False, f"Invalid argument format: {arg}"
                
        return True, ""
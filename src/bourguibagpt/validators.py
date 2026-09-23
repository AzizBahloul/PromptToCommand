import re
import logging
import shlex
from typing import Tuple

class CommandValidator:
    """Validates shell commands for safety"""

    # POSIX shells (bash/zsh/fish/sh) expose these as real executables.
    POSIX_SAFE_COMMANDS = {
        'mkdir', 'ls', 'cd', 'pwd', 'cp', 'mv', 'rm', 'touch',
        'cat', 'echo', 'grep', 'find', 'head', 'tail', 'chmod',
        'chown', 'ln', 'ps', 'kill', 'df', 'du', 'tar', 'gzip',
        'gunzip', 'bzip2', 'bunzip2', 'zip', 'unzip', 'ping',
        'curl', 'wget', 'scp', 'ssh', 'rsync', 'free', 'wc'
    }
    # Windows PowerShell ships these as built-in aliases/functions (ls, cp,
    # mv, rm, cat, pwd, ps, kill, mkdir) or as real bundled executables
    # (curl, wget, ping, tar, ssh, scp on modern Windows). Set-Location and
    # Get-Location are the cmdlets the app itself emits for navigation.
    POWERSHELL_SAFE_COMMANDS = {
        'ls', 'cp', 'mv', 'rm', 'cat', 'pwd', 'ps', 'kill', 'mkdir',
        'curl', 'wget', 'ping', 'tar', 'ssh', 'scp',
        'Set-Location', 'Get-Location',
    }
    # cmd.exe has no POSIX-named builtins; only these are reachable, either
    # as native cmd verbs (cd, mkdir) or real PATH executables on modern
    # Windows (curl, tar, ssh, scp, ping).
    CMD_SAFE_COMMANDS = {'cd', 'mkdir', 'ping', 'curl', 'tar', 'ssh', 'scp'}

    SAFE_COMMANDS_BY_SHELL = {
        'posix': POSIX_SAFE_COMMANDS,
        'powershell': POWERSHELL_SAFE_COMMANDS,
        'cmd': CMD_SAFE_COMMANDS,
    }

    # Backward-compatible default (POSIX) allowlist.
    SAFE_COMMANDS = POSIX_SAFE_COMMANDS

    @classmethod
    def validate(cls, command: str, shell: str = "posix") -> Tuple[bool, str]:
        """
        Validates a shell command against the allowlist for the given shell family.
        Returns: (is_valid, error_message)
        """
        if not command or not command.strip():
            return False, "Empty command"

        # Permit pipelines, but validate every command in the pipeline separately.
        # Other shell operators remain blocked to prevent chaining/substitution.
        if re.search(r"[;&<>`$()]|\|\||&&", command):
            logging.warning("Shell control or substitution operator detected")
            return False, "Shell control or substitution operator is not allowed"

        safe_commands = cls.SAFE_COMMANDS_BY_SHELL.get(shell, cls.POSIX_SAFE_COMMANDS)
        # '+' is allowed for numeric qualifiers such as `find -size +10M`.
        safe_pattern = r'''^[a-zA-Z0-9_\-+./:*?\[\]'" ]+$'''
        for pipeline_part in command.strip().split("|"):
            try:
                parts = shlex.split(pipeline_part)
            except ValueError:
                return False, "Invalid shell quoting"
            if not parts:
                return False, "Empty pipeline command"

            base_cmd = parts[0]
            if base_cmd not in safe_commands:
                logging.warning(f"Command '{base_cmd}' not in allowed list")
                return False, f"Command '{base_cmd}' not in allowed list"

            for arg in parts[1:]:
                if not re.match(safe_pattern, arg):
                    logging.warning(f"Invalid argument format: {arg}")
                    return False, f"Invalid argument format: {arg}"

        return True, ""
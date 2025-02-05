import re
from typing import Tuple

class CommandValidator:
    """Validates shell commands for safety"""
    
    SAFE_COMMANDS = {
        'mkdir', 'ls', 'cd', 'pwd', 'cp', 'mv', 'rm', 'touch',
        'cat', 'echo', 'grep', 'find', 'head', 'tail'
    }
    
    @classmethod
    def validate(cls, command: str) -> Tuple[bool, str]:
        """
        Validates a shell command
        Returns: (is_valid, error_message)
        """
        if not command or not command.strip():
            return False, "Empty command"
            
        # Split command and arguments
        parts = command.strip().split()
        base_cmd = parts[0]
        
        # Check if base command is in whitelist
        if base_cmd not in cls.SAFE_COMMANDS:
            return False, f"Command '{base_cmd}' not in allowed list"
            
        # Basic argument validation
        safe_pattern = r'^[a-zA-Z0-9_\-./]+$'
        for arg in parts[1:]:
            if not re.match(safe_pattern, arg):
                return False, f"Invalid argument format: {arg}"
                
        return True, ""
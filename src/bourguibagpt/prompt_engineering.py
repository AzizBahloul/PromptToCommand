"""Shell-aware prompt engineering for the local command model."""

import json
import platform
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .validators import CommandValidator

SHELL_LABELS = {
    "powershell": "PowerShell",
    "cmd": "Windows Command Prompt (cmd.exe)",
    "bash": "bash",
    "zsh": "zsh",
    "fish": "fish",
    "sh": "POSIX sh",
}

# The validator keeps a separate allowlist per shell family; this maps every
# shell name the app can detect onto one of those families so the prompt and
# the validator always agree on what the model is allowed to produce.
SHELL_FAMILIES = {"powershell": "powershell", "cmd": "cmd"}


def shell_family(shell: str) -> str:
    """Map a detected shell name onto its validator/allowlist family."""
    return SHELL_FAMILIES.get(shell, "posix")


# The JSON contract returned by the model. Shared with main.py so the
# Ollama "format" constraint and the text of the prompt never drift apart.
FORMAT_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": ["command", "navigate"]},
        "target": {"type": "string"},
        "command": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["action", "target", "command", "confidence"],
}

# Curated few-shot examples, one list per shell family. Every "command"
# value here is checked at import time (see _self_check below) against
# CommandValidator so the model is never trained on an example that its own
# safety layer would then reject.
SHELL_EXAMPLES: Dict[str, List[Tuple[str, str, str, str]]] = {
    "posix": [
        ("locate this folder", "command", "current_directory", "pwd"),
        ("move to the desktop", "navigate", "Desktop", ""),
        ("open my home folder", "navigate", "home", ""),
        ("list hidden files here", "command", "", "ls -la"),
        ("find python files under src", "command", "", "find src -type f -name '*.py'"),
        ("make a new folder called backup", "command", "", "mkdir backup"),
        ("delete the file test.txt", "command", "", "rm test.txt"),
        ("rename report.txt to report_old.txt", "command", "", "mv report.txt report_old.txt"),
        ("show files bigger than 10 megabytes", "command", "", "find . -type f -size +10M"),
        ("check free memory", "command", "", "free -h"),
        ("how many lines does main.py have", "command", "", "wc -l main.py"),
        ("kill the process using port 8080", "command", "", ""),
    ],
    "powershell": [
        ("locate this folder", "command", "current_directory", "pwd"),
        ("move to the desktop", "navigate", "Desktop", ""),
        ("list hidden files here", "command", "", "ls -Force"),
        ("find python files under src", "command", "", "ls -Path src -Recurse -Filter *.py"),
        ("make a new folder called backup", "command", "", "mkdir backup"),
        ("delete the file test.txt", "command", "", "rm test.txt"),
        ("rename report.txt to report_old.txt", "command", "", "mv report.txt report_old.txt"),
        ("show disk usage of this folder", "command", "", ""),
    ],
    "cmd": [
        ("locate this folder", "command", "current_directory", "cd"),
        ("move to the desktop", "navigate", "Desktop", ""),
        ("make a new folder called backup", "command", "", "mkdir backup"),
        ("list hidden files here", "command", "", ""),
        ("ping google.com", "command", "", "ping google.com"),
    ],
}


def _self_check() -> None:
    """Fail fast in development if an example would not pass its own validator."""
    for family, examples in SHELL_EXAMPLES.items():
        for request, action, target, command in examples:
            if not command:
                continue
            is_valid, error = CommandValidator.validate(command, shell=family)
            if not is_valid:
                raise AssertionError(
                    f"Example for {family!r} ({request!r} -> {command!r}) "
                    f"fails its own validator: {error}"
                )


_self_check()


def _allowed_commands_line(family: str) -> str:
    commands = sorted(CommandValidator.SAFE_COMMANDS_BY_SHELL.get(family, CommandValidator.POSIX_SAFE_COMMANDS))
    return ", ".join(commands)


def build_system_prompt(shell: str, cwd: Path, prompt: str) -> str:
    """Build a shell-specific structured-output prompt."""
    os_info = platform.system()
    label = SHELL_LABELS.get(shell, shell)
    family = shell_family(shell)
    tools_hint = {
        "Darwin": "Use macOS/BSD command syntax.",
        "Linux": "GNU coreutils are available.",
        "Windows": "Do not use Unix commands in this shell.",
    }.get(platform.system(), "")
    examples = SHELL_EXAMPLES.get(family, SHELL_EXAMPLES["posix"])
    example_text = "\n".join(
        f"User: {request}\nJSON: " + json.dumps({
            "action": action,
            "target": target,
            "command": command,
            "confidence": 0.99 if command or action == "navigate" else 0.2,
        })
        for request, action, target, command in examples
    )
    allowed_commands = _allowed_commands_line(family)
    return f"""You translate one natural-language request into exactly one {label} command.
The command is executed as written, so it must be valid {label} syntax.

Environment:
- Operating system: {os_info}
- Shell: {label}
- Current working directory: {cwd}
- {tools_hint}

Return exactly one JSON object and nothing else:
{{"action":"command|navigate", "target":"", "command":"", "confidence":0.0}}

Rules:
1. Never mix shell syntaxes. Keep paths and filenames exactly as the user wrote them,
   including case; never invent, shorten, or guess a path, extension, or OS-specific
   system location (such as a trash/recycle-bin folder) that the user did not name.
2. Use action "navigate" only when the entire request is to go to, open, or change into a
   directory and nothing else. Put the directory name in target and leave command empty.
   Every other request (create, delete, copy, move, rename, compress, list, search, show,
   count, stop a process, ...) is action "command", even if it mentions a folder.
3. A request to locate or show the current folder is command "pwd" (or the shell equivalent).
4. When the user names a file type instead of a filename (e.g. "python files", "images",
   "log files"), translate it into the matching extension glob (e.g. *.py, *.png, *.log).
   Never use the type name itself as a literal filename or search pattern. To filter which
   files are listed, pass that glob straight to ls or find -name (e.g. ls *.md); do not pipe
   through grep with a regex anchor such as $ for this, since $ is never allowed (rule 5).
5. Use only these commands, and only one command or a pipe (|) chain of them:
   {allowed_commands}
   Arguments may contain only letters, digits, spaces, and - + . / : * ? [ ] ' " _ characters.
   Never use $, `, ;, &, &&, ||, <, >, parentheses, or backslash escapes.
6. If the request needs a command that is not in that list, needs information you do not
   have, or is ambiguous, return command "" and confidence at most 0.3. Do not invent a
   multi-step workaround. This always applies to finding a process ID, PID, or owner of a
   port, socket, or service before you could act on it.

Examples:
{example_text}

User request: {prompt}
"""


def extract_json_object(text: str) -> Optional[dict]:
    """Recover a JSON object from text that may wrap it in extra words.

    Small local models occasionally emit a stray decision word, a trailing
    remark, or a markdown fence around an otherwise-correct JSON object.
    Rather than discarding that response outright, salvage the first
    balanced {...} span and parse it.
    """
    text = text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        pass

    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        char = text[i]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                candidate = text[start:i + 1]
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    return None
    return None


_LABEL_PREFIX_RE = re.compile(r"^(JSON|Command|Answer|Output|Response)\s*:\s*", re.IGNORECASE)
_SHELL_PROMPT_RE = re.compile(r"^(PS [^>]*>|PS>|\$|>)\s*")


def clean_command(raw: str) -> str:
    """Remove markdown and prompt noise while keeping one command line."""
    text = re.sub(r"```[a-zA-Z]*", "", raw).replace("```", "").strip()
    lines = [line.strip() for line in text.splitlines()
             if line.strip() and line.strip().lower() not in SHELL_LABELS]
    line = lines[0] if lines else ""
    line = _LABEL_PREFIX_RE.sub("", line)
    return _SHELL_PROMPT_RE.sub("", line).strip()

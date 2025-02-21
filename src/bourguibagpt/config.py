import os
import json
from pathlib import Path
from datetime import datetime

VERSION = "2.0.0"

# Define user config directory and file
CONFIG_DIR = Path.home() / ".config" / "bourguibagpt"
CONFIG_FILE = CONFIG_DIR / "settings.json"

# Default model configurations
MODEL_CONFIG = {
    "tiny": {
        "model_name": "codegemma:2b",
        "description": "Lightweight model suitable for systems with limited RAM",
        "ram_threshold": 6,
        "specs": {
            "min_ram": "4GB",
            "recommended_ram": "4GB or 6GB",
            "disk_space": "2GB",
            "cpu": "2 cores"
        },
        "use_case": "Basic command-line tasks, simple queries"
    },
    "medium": {
        "model_name": "qwen2.5-coder:7b",
        "description": "Balanced model for systems with moderate RAM",
        "ram_threshold": 10,
        "specs": {
            "min_ram": "8GB",
            "recommended_ram": "12GB or 16GB",
            "disk_space": "5GB",
            "cpu": "4 cores"
        },
        "use_case": "Complex commands, script generation"
    },
    "large": {
        "model_name": "qwen2.5:14b",
        "description": "Full-size model for systems with ample RAM",
        "ram_threshold": 18,
        "specs": {
            "min_ram": "16GB",
            "recommended_ram": "24GB +",
            "disk_space": "10GB",
            "cpu": "8 cores"
        },
        "use_case": "Advanced automation, detailed explanations"
    }
}

# OS-specific configurations
OS_CONFIG = {
    "Windows": {
        "install_cmd": "winget install Ollama.Ollama",
        "service_start": "net start ollama",
        "required_packages": ["winget"]
    },
    "Arch": {
        "install_cmd": "yay -S ollama",
        "service_start": "systemctl start ollama",
        "required_packages": ["yay"]
    },
    "Fedora": {
        "install_cmd": "sudo dnf install ollama",
        "service_start": "systemctl start ollama",
        "required_packages": ["dnf"]
    }
}

# Validation rules
VALIDATION_RULES = {
    "min_ram_gb": 4,
    "min_disk_gb": 2,
    "min_cpu_cores": 2
}

def get_recommended_model(available_ram_gb):
    """Returns the recommended model based on available RAM"""
    for model_size in ["tiny", "medium", "large"]:
        if available_ram_gb >= MODEL_CONFIG[model_size]["ram_threshold"]:
            return model_size
    return "tiny"  # Fallback to tiny if RAM is very limited

def save_user_preferences(model_name: str) -> None:
    """Save user's model preference to config file"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = {
        "preferred_model": model_name,
        "last_used": datetime.now().isoformat()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_user_preferences() -> dict:
    """Load user's saved preferences with model validation"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                prefs = json.load(f)
                # Validate saved model exists in our configuration
                if any(prefs.get("preferred_model") == cfg["model_name"] 
                       for cfg in MODEL_CONFIG.values()):
                    return prefs
        except (json.JSONDecodeError, KeyError):
            pass
    return {}

def get_os_specific_config():
    """Get OS-specific configuration"""
    import platform
    system = platform.system()
    if system == "Linux":
        # Detect Linux distribution
        try:
            with open("/etc/os-release") as f:
                os_info = dict(line.strip().split('=', 1) for line in f if '=' in line)
            if "arch" in os_info.get("ID", "").lower():
                return OS_CONFIG["Arch"]
            elif "fedora" in os_info.get("ID", "").lower():
                return OS_CONFIG["Fedora"]
        except:
            pass
    elif system == "Windows":
        return OS_CONFIG["Windows"]
    return None
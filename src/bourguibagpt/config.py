# Model configuration constants
MODEL_CONFIG = {
    "tiny": {
        "model_name": "distilgpt2",
        "ram_threshold": 8,  # GB
        "description": "Lightweight model for systems with ≤8 GB RAM"
    },
    "medium": {
        "model_name": "EleutherAI/gpt-neo-1.3B",
        "ram_threshold": 16,  # GB
        "description": "Balanced model for systems with 8–16 GB RAM"
    },
    "large": {
        "model_name": "EleutherAI/gpt-j-6B",
        "ram_threshold": 32,  # GB
        "description": "Powerful model for systems with ≥32 GB RAM"
    }
}
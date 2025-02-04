# Model configuration constants updated for Ollama models
MODEL_CONFIG = {
    "tiny": {
        "model_name": "smollm2:1.7b",
        "ram_threshold": 8,  # GB
        "description": "Lightweight model (Ollama: smollm2:1.7b) for systems with ≤8 GB RAM"
    },
    "medium": {
        "model_name": "mistral-openorca:7b",
        "ram_threshold": 16,  # GB
        "description": "Balanced model (Ollama: mistral-openorca:7b) for systems with 8–16 GB RAM"
    },
    "large": {
        "model_name": "llama3.2:3b",
        "ram_threshold": 32,  # GB
        "description": "Powerful model (Ollama: llama3.2:3b) for systems with ≥32 GB RAM"
    }
}
# Model configuration constants updated for Ollama models
MODEL_CONFIG = {
    "tiny": {
        "model_name": "gemma2:2b",
        "description": "Lightweight model suitable for systems with limited RAM (4-8GB)",
        "ram_threshold": 6
    },
    "medium": {
        "model_name": "mistral-openorca:7b",
        "description": "Balanced model for systems with moderate RAM (8-16GB)",
        "ram_threshold": 10
    },
    "large": {
        "model_name": "phi4:14b",
        "description": "Full-size model for systems with ample RAM (16GB+)",
        "ram_threshold": 18
    }
}
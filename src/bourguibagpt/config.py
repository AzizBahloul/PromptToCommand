VERSION = "2.0.0"

MODEL_CONFIG = {
    "tiny": {
        "model_name": "gemma2:2b",
        "description": "Lightweight model suitable for systems with limited RAM",
        "ram_threshold": 6,
        "specs": {
            "min_ram": "4GB",
            "recommended_ram": "6GB",
            "disk_space": "2GB",
            "cpu": "2 cores"
        },
        "use_case": "Basic command-line tasks, simple queries"
    },
    "medium": {
        "model_name": "mistral-openorca:7b",
        "description": "Balanced model for systems with moderate RAM",
        "ram_threshold": 10,
        "specs": {
            "min_ram": "8GB",
            "recommended_ram": "12GB",
            "disk_space": "5GB",
            "cpu": "4 cores"
        },
        "use_case": "Complex commands, script generation"
    },
    "large": {
        "model_name": "phi4:14b",
        "description": "Full-size model for systems with ample RAM",
        "ram_threshold": 18,
        "specs": {
            "min_ram": "16GB",
            "recommended_ram": "24GB",
            "disk_space": "10GB",
            "cpu": "8 cores"
        },
        "use_case": "Advanced automation, detailed explanations"
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
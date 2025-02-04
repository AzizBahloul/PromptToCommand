import psutil

def get_system_memory() -> float:
    """
    Return total system memory in GB, rounded to 2 decimal places.
    """
    total_gb = psutil.virtual_memory().total / (1024 ** 3)
    return round(total_gb, 2)

def recommend_model(ram_gb: float) -> str:
    """
    Recommend the best model based on available system RAM.

    :param ram_gb: System memory in GB (must be positive).
    :return: Model recommendation ("tiny", "medium", or "large").
    :raises ValueError: If ram_gb is not positive.
    """
    if ram_gb <= 0:
        raise ValueError("RAM must be a positive value.")
    if ram_gb <= 8:
        return "tiny"
    elif ram_gb <= 16:
        return "medium"
    else:
        return "large"
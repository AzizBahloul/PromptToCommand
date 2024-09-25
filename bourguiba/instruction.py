def generate_instruction(description):
    """
    Generate a T5 instruction for command generation.
    
    Parameters:
    - description (str): The description of the command to generate.

    Returns:
    - str: The instruction formatted for the T5 model.
    """
    instruction = f"dont yapp jsute Generate a shell command whitout any add   juste a simple commande in a shell form  to {description}. Output only the command without any additional text."
    return instruction

"""
Utility functions for loading prompts
"""

import os
from pathlib import Path

def load_prompt(prompt_name: str, prompts_dir: str = None) -> str:
    """
    Load prompt from file
    
    Args:
        prompt_name: Name of prompt file (with or without .txt extension)
        prompts_dir: Directory containing prompt files
        
    Returns:
        Prompt content as string
    """
    if not prompt_name.endswith('.txt'):
        prompt_name = f"{prompt_name}.txt"
    
    # Use provided dir or default
    if prompts_dir:
        prompt_path = Path(prompts_dir) / prompt_name
    else:
        # Default to prompts directory in package
        prompt_path = Path(__file__).parent.parent / "prompts" / prompt_name
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    
    with open(prompt_path, 'r') as f:
        return f.read()
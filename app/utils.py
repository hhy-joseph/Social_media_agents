"""
Utility functions for the Instagram content generation workflow
"""

import json
import os
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("ig_agent.utils")


def save_content_json(content_json: Dict[str, Any], output_dir: str) -> str:
    """
    Save content JSON to output directory
    
    Args:
        content_json: Generated content to save
        output_dir: Directory to save content in
        
    Returns:
        Path to saved content file
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        content_path = os.path.join(output_dir, "content.json")
        
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(content_json, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Content saved to {content_path}")
        return content_path
        
    except Exception as e:
        logger.error(f"Failed to save content JSON: {str(e)}")
        raise


def ensure_output_directory(base_dir: str = "output") -> str:
    """
    Ensure output directory exists and return timestamped path
    
    Args:
        base_dir: Base directory name
        
    Returns:
        Path to timestamped output directory
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_folder = datetime.now().strftime("%Y-%m-%d")
    
    output_dir = Path(base_dir) / date_folder / timestamp
    os.makedirs(output_dir, exist_ok=True)
    
    return str(output_dir)


def load_prompt(prompt_name: str, prompts_dir: str = None) -> str:
    """
    Load prompt from file
    
    Args:
        prompt_name: Name of prompt file (with or without .txt extension)
        prompts_dir: Directory containing prompts
        
    Returns:
        Prompt content
    """
    if not prompts_dir:
        from .configuration import get_prompts_dir
        prompts_dir = get_prompts_dir()
    
    if not prompt_name.endswith('.txt'):
        prompt_name += '.txt'
        
    prompt_path = os.path.join(prompts_dir, prompt_name)
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")


def validate_dependencies():
    """
    Validate that all required dependencies are available
    
    Raises:
        ImportError: If required dependencies are missing
    """
    required_packages = [
        "langchain_xai",
        "langgraph",
        "langchain_community",
        "instagrapi",
        "PIL"
    ]
    
    # Optional packages
    optional_packages = [
        "cairosvg"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        raise ImportError(
            f"Missing required packages: {', '.join(missing_packages)}. "
            f"Please install them using: pip install {' '.join(missing_packages)}"
        )
    
    # Check optional packages (warn but don't fail)
    for package in optional_packages:
        try:
            __import__(package)
        except (ImportError, OSError) as e:
            logger.warning(f"Optional package '{package}' not available. Some features may be limited. Error: {e}")
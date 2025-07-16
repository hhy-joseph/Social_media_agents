"""
Configuration management for the Instagram content generation workflow
"""

import os
from pathlib import Path
from typing import Tuple, Optional
from langchain_xai import ChatXAI


def get_llm():
    """
    Get configured language model
    
    Returns:
        Configured LLM instance
    """
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        raise ValueError("XAI_API_KEY environment variable is required")
    
    return ChatXAI(
        model="grok-3-mini",
        api_key=api_key,
        temperature=0.7
    )


def get_prompts_dir() -> str:
    """
    Get prompts directory path
    
    Returns:
        Path to prompts directory
    """
    # Try app/prompts first, then ig_agent/prompts
    app_prompts = Path(__file__).parent / "prompts"
    ig_agent_prompts = Path(__file__).parent / "ig_agent" / "prompts"
    
    if app_prompts.exists():
        return str(app_prompts)
    elif ig_agent_prompts.exists():
        return str(ig_agent_prompts)
    else:
        raise FileNotFoundError("Could not find prompts directory")


def get_templates_dir() -> str:
    """
    Get templates directory path
    
    Returns:
        Path to templates directory
    """
    # Try app/static first, then ig_agent/static
    app_static = Path(__file__).parent / "static"
    ig_agent_static = Path(__file__).parent / "ig_agent" / "static"
    
    if app_static.exists():
        return str(app_static)
    elif ig_agent_static.exists():
        return str(ig_agent_static)
    else:
        raise FileNotFoundError("Could not find templates directory")


def get_email_config() -> Tuple[Optional[str], Optional[str]]:
    """
    Get email configuration
    
    Returns:
        Tuple of (email_user, email_password)
    """
    return (
        os.getenv("EMAIL_USER"),
        os.getenv("EMAIL_PASSWORD")
    )


def get_instagram_config() -> Tuple[Optional[str], Optional[str]]:
    """
    Get Instagram configuration
    
    Returns:
        Tuple of (instagram_username, instagram_password)
    """
    return (
        os.getenv("INSTAGRAM_USERNAME"),
        os.getenv("INSTAGRAM_PASSWORD")
    )
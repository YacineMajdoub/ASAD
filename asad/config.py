"""
Configuration management for API keys and LLM provider selection.
"""

import os
from typing import Literal

from dotenv import load_dotenv

# Load environment variables early
load_dotenv()


def get_llm_provider() -> Literal["together", "groq", "openai"]:
    """Get the active LLM provider from environment variables."""
    provider = os.getenv("LLM_PROVIDER").lower() 
    if provider not in ["together", "groq", "openai"]:
        raise ValueError(
            f"Invalid LLM provider: {provider}. "
            "Must be one of: together, groq, openai"
        )
    return provider


def get_api_key(provider: str) -> str:
    """Retrieve API key for the specified provider."""
    key_map = {
        "together": "TOGETHER_API_KEY",
        "groq": "GROQ_API_KEY",
        "openai": "OPENAI_API_KEY",
    }
    
    if provider not in key_map:
        raise ValueError(f"Unknown provider: {provider}")
    
    api_key = os.getenv(key_map[provider])
    if not api_key or api_key == "PUT YOUR API KEY HERE":
        raise ValueError(
            f"API key for {provider} not found or not configured in environment. "
            f"Set {key_map[provider]} in your .env file."
        )
    
    return api_key

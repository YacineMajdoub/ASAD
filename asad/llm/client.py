"""
Unified interface for calling LLMs across different providers.
"""

from typing import Optional
from .providers import TogetherProvider, GroqProvider, OpenAIProvider
from ..config import get_llm_provider


def call_llm(question: str, provider: Optional[str] = None) -> str:
    """
    Call an LLM with the given prompt using the configured provider.
    
    Args:
        question: Prompt to send to the LLM
        provider: Override active provider (together/groq/openai)
    
    Returns:
        LLM response text
    """
    if provider is None:
        provider = get_llm_provider()
    
    provider_map = {
        "together": TogetherProvider,
        "groq": GroqProvider,
        "openai": OpenAIProvider,
    }
    
    if provider not in provider_map:
        raise ValueError(f"Unsupported provider: {provider}")
    
    client = provider_map[provider]()
    return client.generate(question)

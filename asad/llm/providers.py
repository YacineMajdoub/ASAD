"""
Provider-specific LLM client implementations.
"""

import os
from abc import ABC, abstractmethod

from together import Together
from groq import Groq
from openai import OpenAI

from ..config import get_api_key


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from the given prompt."""
        pass


class TogetherProvider(LLMProvider):
    """Together.ai API client."""
    
    def __init__(self):
        api_key = get_api_key("together")
        self.client = Together(api_key=api_key)
        self.model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
    
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


class GroqProvider(LLMProvider):
    """Groq API client."""
    
    def __init__(self):
        api_key = get_api_key("groq")
        self.client = Groq(api_key=api_key)
        self.model = "groq/compound-mini"  
    
    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content


class OpenAIProvider(LLMProvider):
    """OpenAI API client."""
    
    def __init__(self):
        api_key = get_api_key("openai")
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"  
    
    def generate(self, prompt: str) -> str:
        response = self.client.chat.responses.create(
            model=self.model,
            input=prompt,
            reasoning={ "effort": "low" },
            text={ "verbosity": "low" },
        )
        return response.output_text

"""
ASAD: Adaptive Software Analysis and Debugging
An adaptive multi-agent system for automatic code debugging using LLMs.
"""

from .pipeline import adaptive_debugger
from .config import get_llm_provider

__version__ = "0.1.0"
__all__ = ["adaptive_debugger", "get_llm_provider"]

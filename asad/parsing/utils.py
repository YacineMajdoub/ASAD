"""
Utilities for cleaning LLM outputs and parsing structured responses.
"""

import json
import re
import regex
from typing import Any, Optional


def clean_code(text: str) -> str:
    """
    Extract code from markdown code blocks.
    
    Handles:
    - Triple backtick delimiters with optional language specifiers
    - Leading/trailing whitespace
    
    Args:
        text: Raw LLM response possibly containing code blocks
    
    Returns:
        Cleaned code without markdown delimiters
    """
    text = text.strip()
    
    # Remove leading ```language or ```
    if text.startswith("```"):
        lines = text.split("\n", 1)
        if len(lines) > 1:
            text = lines[1]
        else:
            text = ""
    
    # Remove trailing ```
    text = re.sub(r"\n```.*$", "", text, flags=re.MULTILINE)
    
    return text.strip()


def clean_json(text: str) -> str:
    """
    Extract the first valid JSON object from text using recursive regex.
    
    Args:
        text: Raw LLM response possibly containing JSON
    
    Returns:
        JSON substring or empty string if none found
    """
    match = regex.search(r'\{(?:[^{}]|(?R))*\}', text)
    return match.group() if match else ""


def safe_json_parse(response: str, fallback: Optional[Any] = None) -> Any:
    """
    Safely parse JSON from LLM response with error recovery.
    
    Attempts:
    1. Direct parsing of extracted JSON
    2. Fixing invalid escape sequences
    3. Returning fallback value
    
    Args:
        response: Raw LLM response
        fallback: Value to return on persistent parse failure
    
    Returns:
        Parsed JSON object or fallback value
    """
    try:
        clean_response = clean_json(response)
        if not clean_response:
            return fallback
        return json.loads(clean_response)
    except json.JSONDecodeError:
        # Fix common escape sequence issues
        clean_response = re.sub(r"\\(?!['\"\\/bfnrtu])", r"\\\\", clean_response)
        try:
            return json.loads(clean_response)
        except json.JSONDecodeError:
            return fallback

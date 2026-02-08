"""
Fast-path strategy for fixing simple bugs with a single repair pass.
"""

from typing import Dict, Any, List

from ..llm import call_llm
from ..parsing import safe_json_parse


def simple_fix(bugs: List[Any], code: str) -> Dict[str, Any]:
    """
    Fix simple bugs in a single repair pass without agent orchestration.
    
    Used when analysis determines the debugging task is SIMPLE complexity.
    
    Args:
        bugs: List of identified bugs
        code: Buggy source code
    
    Returns:
        Fixed code and explanation of repairs applied
    """
    prompt = f"""
Role:
    You are a Code Repair Expert. Your task is to fix all identified bugs in the given code
    and produce a fully corrected version.

Input:
    Buggy code: {code}
    Summary of issues: {bugs}

Instructions:
1. Fix the code to eliminate all execution-blocking bugs.
2. Provide a clear explanation of each fix applied.

Output:
Return a JSON object with all newlines and quotes escaped (e.g., \\n, \\"):

{{
  "fixed_code": "string",
  "fix_explanation": "string"
}}

Do not write any text besides the JSON.
"""
    result = call_llm(prompt)
    return safe_json_parse(
        result,
        fallback={"fixed_code": code, "fix_explanation": "Simple fix failed"}
    )

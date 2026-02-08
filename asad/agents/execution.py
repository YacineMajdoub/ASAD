"""
Execute specialized agent tasks to repair specific bug categories.
"""

from typing import Dict, Any

from ..llm import call_llm
from ..parsing import safe_json_parse


def execute_agent(agent: Dict[str, Any], code: str) -> Dict[str, Any]:
    """
    Execute a specialized agent's repair task on the given code.
    
    Args:
        agent: Agent profile with name, role, and task description
        code: Current state of code to repair
    
    Returns:
        Fixed code and explanation of changes applied
    """
    prompt = f"""
Role:
    You are a {agent["role"]}.
    Your task is to {agent["task_description"]}.

Input:
    Buggy code: {code}

Instructions:
1. Fix the code to address the issues within your responsibility.
2. Provide a clear explanation of the fix applied.

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
        fallback={"fixed_code": code, "fix_explanation": "No fix applied"}
    )


def retry_execute_agent(
    agent: Dict[str, Any],
    code: str,
    feedback: str
) -> Dict[str, Any]:
    """
    Re-execute agent task incorporating reviewer feedback from failed attempt.
    
    Args:
        agent: Agent profile
        code: Current state of code
        feedback: Specific feedback from task reviewer
    
    Returns:
        Revised fixed code and explanation
    """
    prompt = f"""
Role:
    You are a {agent["role"]}.
    Your task is to {agent["task_description"]}.
    You previously attempted a fix that failed. Now, fix the code again using the provided feedback.

Input:
    Buggy code: {code}
    Feedback: {feedback}

Instructions:
1. Fix the code, taking the feedback into account.
2. Provide a clear explanation of the fix applied.

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
        fallback={"fixed_code": code, "fix_explanation": "No fix applied"}
    )

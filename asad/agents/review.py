"""
Agents for reviewing agent outputs and validating final solutions.
"""

from typing import Dict, Any

from ..llm import call_llm
from ..parsing import safe_json_parse


def task_review(agent: Dict[str, Any], agent_report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Review an agent's repair attempt and decide whether to approve or request refinement.
    
    Args:
        agent: Agent profile with task description
        agent_report: Agent's output containing fixed code and explanation
    
    Returns:
        Review decision (APPROVE/REFINE) and optional feedback
    """
    prompt = f"""
Role:
You are the Main Agent responsible for reviewing the output of a specialized debugging agent.
Your task is to decide whether to approve or refine the agent fixes.

Input:
The agent task description: {agent["task_description"]}
The proposed fixed code: {agent_report["fixed_code"]}
The fix explanation: {agent_report["fix_explanation"]}

Instructions:
1. Check whether the agent's changes are correct and complete.
2. If yes, approve and move to the next agent.
3. If no, instruct the same agent to refine its work.

Your output in JSON format:
{{
  "decision": "APPROVE" or "REFINE",
  "feedback": "string" // required if decision is REFINE
}}

Do not write any text besides the JSON.
"""
    result = call_llm(prompt)
    return safe_json_parse(
        result,
        fallback={"decision": "REFINE", "feedback": "Review failed - retrying"}
    )


def validate_solution(code: str) -> Dict[str, Any]:
    """
    Perform final validation to determine if code is fully fixed and executable.
    
    Args:
        code: Repaired code to validate
    
    Returns:
        Validation status with summary of remaining issues if any
    """
    prompt = f"""
Role:
    You are the Master Agent responsible for final validation and closure.
    Your task is to verify whether the given code is fully fixed and executable.
    Focus only on bugs that prevent correct execution.

Input:
    Code to validate: {code}

Instructions:
1. Check whether the code is free of execution-blocking bugs.
2. If the code is fully fixed, confirm completion.
3. If not, summarize and explain all remaining bugs.

Output:
Return a JSON object with this schema:

{{
  "status": "FIXED" or "NOT FIXED",
  "summary": "string",
  "remaining_bugs": [
    {{
      "type": "string",
      "location": "string",
      "explanation": "string"
    }}
  ]
}}

Do not write any text besides the JSON.
"""
    result = call_llm(prompt)
    return safe_json_parse(
        result,
        fallback={
            "status": "NOT FIXED",
            "summary": "Validation failed due to parsing error",
            "remaining_bugs": []
        }
    )

"""
Agents responsible for problem analysis and complexity assessment.
"""

import json
from typing import Dict, Any, List

from ..llm import call_llm
from ..parsing import safe_json_parse


def analyze_problem(code: str) -> Dict[str, Any]:
    """
    Analyze buggy code to assess complexity and identify execution-blocking bugs.
    
    The agent:
    1. Classifies debugging task as SIMPLE or COMPLEX
    2. Locates all critical bugs with type/location/explanation
    3. Generates a step-by-step repair plan
    
    Args:
        code: Buggy Python source code
    
    Returns:
        Analysis report with complexity, bugs list, and repair plan
    """
    prompt = f"""
Role: You are the Main Analysis Agent. Your responsibility
is to perform a systematic static analysis of the given
code and identify defects that prevent correct execution.

Input: Buggy code: {code}

Instructions:
1. Assess the complexity of the debugging task and classify
it as SIMPLE or COMPLEX based on the following criterias:
  - Number of critical bugs
  - Degree of bug isolation
  - Clarity of control flow
  - Concurrency or resource management issues
  - Inter-function or module coupling
2. Identify and precisely locate all bugs that may prevent
the code from executing correctly. For each bug, specify:
  - Bug type (e.g., syntax error, API misuse, ...)
  - Location (function name, line number range)
  - Brief explanation of why it causes failure
3. Produce a structured, step-by-step repair plan
describing how the identified bugs should be fixed.

Output: Return a JSON object with the following schema:
{{
  "complexity": "SIMPLE" or "COMPLEX",
  "bugs": [
    {{
      "type": "string",
      "location": "string",
      "explanation": "string"
    }}
  ],
  "plan": "string"
}}
Do not write any text besides the JSON.
"""
    result = call_llm(prompt)
    return safe_json_parse(
        result,
        fallback={"complexity": "SIMPLE", "bugs": [], "plan": "No plan generated"}
    )


def new_iteration_analyze_problem(
    code: str,
    failure_log: Dict[str, Any],
    previous_plan: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Re-analyze code after a failed repair attempt to identify remaining bugs.
    
    Args:
        code: Current state of code after failed repair
        failure_log: Validation results showing remaining issues
        previous_plan: Original repair plan that failed
    
    Returns:
        Updated analysis with remaining bugs and new repair plan
    """
    prompt = f"""
Role:
    You are the Main Analysis Agent. Your responsibility is to perform a systematic review
    of the given code after a previous fix attempt has failed. Identify all remaining defects
    that prevent execution and generate a precise new repair plan. Do not provide suggestions
    or potential improvements.

Input:
    Previous repair plan: {json.dumps(previous_plan)}
    Failure summary: {failure_log.get("summary", "Unknown failure")}
    Buggy code: {code}

Instructions:
1. Assess the complexity of the remaining debugging task and classify it as SIMPLE or COMPLEX
  using the following criteria:
      - Number of critical bugs remaining
      - Degree of bug isolation
      - Clarity of control flow
      - Presence of concurrency or resource management issues
      - Dependencies between functions or modules
2. Identify all remaining bugs, specifying for each:
      - Bug type (e.g., syntax error, API misuse, logic error)
      - Location (function name, line number range)
      - Explanation of why it prevents correct execution
3. Produce a step-by-step new repair plan detailing how to fix the remaining bugs.

Output:
Return a JSON object with this schema:
{{
  "complexity": "SIMPLE" or "COMPLEX",
  "bugs": [
    {{
      "type": "string",
      "location": "string",
      "explanation": "string"
    }}
  ],
  "plan": "string"
}}
Do not write any text besides the JSON.
"""
    result = call_llm(prompt)
    return safe_json_parse(
        result,
        fallback={"complexity": "SIMPLE", "bugs": [], "plan": "No plan generated"}
    )

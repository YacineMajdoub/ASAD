"""
Agents responsible for problem analysis and complexity assessment.
"""

import json
from typing import Dict, Any

from ..llm import call_llm
from ..parsing import safe_json_parse
from ..parsing.complexity_analyzer import CodeComplexityAnalyzer



def analyze_problem(code: str) -> Dict[str, Any]:
    """
    Analyze buggy code to assess complexity and identify execution-blocking bugs.

    The agent:
    1. Classifies debugging task as SIMPLE or COMPLEX
    2. Locates all critical bugs with type/location/explanation
    3. Generates a step-by-step repair plan

    Args:
        code: Buggy C source code

    Returns:
        Analysis report with complexity, bugs list, and repair plan
    """

    analyzer = CodeComplexityAnalyzer()

    complexity_signal = analyzer.analyze(
        buggy_code=code
    )


    prompt = f"""
Role:
You are the Main Analysis Agent. Your responsibility is to perform
a systematic static analysis of the given program, identify defects
that prevent correct execution, and assess debugging complexity using
both code content and static analysis signals.

Input:

Buggy code:
{code}

Complexity signal:
{json.dumps(complexity_signal, indent=2)}


Instructions:

1. Use both the buggy code and the static analysis report to assess
the complexity of the debugging task and classify it as SIMPLE or
COMPLEX based on:

- Error severity
- Source-location difficulty
- Program-understanding difficulty
- System-level operations
- Inter-function dependencies


2. Identify and precisely locate all bugs that may prevent
correct execution of the program.

For each bug, specify:

- Bug type (e.g., syntax error, logic error, API misuse)
- Location (function name, line number range, or code region)
- Brief explanation of why it causes failure


3. Produce a structured, step-by-step repair plan describing
how the identified bugs should be fixed.


Output:

Return only a JSON object with the following schema:

{{
    "complexity": "SIMPLE" or "COMPLEX",

    "bugs": [
        {{
            "type": "string",
            "location": "string",
            "description": "string"
        }}
    ],

    "plan": "string"
}}

Do not write any text besides the JSON.
"""


    result = call_llm(prompt)


    return safe_json_parse(
        result,
        fallback={
            "complexity": "SIMPLE",
            "bugs": [],
            "plan": "No plan generated"
        }
    )



def new_iteration_analyze_problem(
        code: str,
        failure_log: Dict[str, Any],
        previous_plan: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Re-analyze code after a failed repair attempt to identify
    remaining bugs.
    """


    analyzer = CodeComplexityAnalyzer()

    complexity_signal = analyzer.analyze(
        buggy_code=code
    )


    prompt = f"""
Role:
You are the Main Analysis Agent. Your responsibility is to review
the program after a failed repair attempt. Identify remaining defects
and generate a new repair plan.

Input:

Previous repair plan:
{json.dumps(previous_plan, indent=2)}

Failure summary:
{failure_log.get("summary", "Unknown failure")}

Buggy code:
{code}

Complexity signal:
{json.dumps(complexity_signal, indent=2)}


Instructions:

1. Assess the complexity of the remaining debugging task and classify
it as SIMPLE or COMPLEX using:

- Error severity
- Source-location difficulty
- Program-understanding difficulty
- System-level operations
- Inter-function dependencies


2. Identify all remaining bugs.

For each bug, specify:

- Bug type
- Location
- Explanation of why it prevents correct execution


3. Produce a step-by-step repair plan.


Output:

Return only a JSON object:

{{
    "complexity": "SIMPLE" or "COMPLEX",

    "bugs": [
        {{
            "type": "string",
            "location": "string",
            "description": "string"
        }}
    ],

    "plan": "string"
}}

Do not write any text besides the JSON.
"""


    result = call_llm(prompt)


    return safe_json_parse(
        result,
        fallback={
            "complexity": "SIMPLE",
            "bugs": [],
            "plan": "No plan generated"
        }
    )
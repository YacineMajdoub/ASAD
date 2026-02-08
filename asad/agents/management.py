"""
Agent creation and dependency management for multi-agent repair strategy.
"""

from typing import Dict, Any, List

from ..llm import call_llm
from ..parsing import safe_json_parse


def generate_agents(bugs: List[Any], plan: str) -> Dict[str, Any]:
    """
    Create specialized agent profiles and determine their execution order.
    
    The process:
    1. Generate minimal set of agents needed to fix located bugs
    2. Analyze dependencies between fixes (e.g., syntax before logic)
    3. Prioritize agents to ensure correct execution sequence
    
    Args:
        bugs: List of identified bugs from analysis
        plan: Step-by-step repair instructions
    
    Returns:
        Agent profiles and execution order
    """
    prompt = f"""
Role:
    You are the Main Agent responsible for creating and organizing specialized agent profiles.
    Your task is twofold:
    1. Generate the set of agents required to fix the located bugs.
    2. Prioritize these agents based on their dependencies to ensure correct execution order.

Prohibited pattern: 
    Do NOT create agents whose role is only analysis, planning, coordination, or validation.

Input:
    Located bugs: {bugs}
    Repair instructions: {plan}

Instructions:

Step 1 - Agent Generation: 
    1. Generate the set of necessary agents required to fix the bugs. Make sure to minimize the number of agents .
    2. For each agent, provide:
        - name
        - role (brief description of expertise)
        - task_description (phrased as "Your task is to..." and explicitly referencing the located errors)

Step 2 - Agent Prioritization:
    1. Determine dependencies between agents (e.g., syntax must be fixed before logic errors).
    2. Order the agents based on these dependencies.

Output:
Return a JSON object with the following schema:

{{
  "agents": [
    {{
      "name": "string",
      "role": "string",
      "task_description": "string"
    }}
  ],
  "execution_order": ["Agent_1_name", "Agent_2_name", "..."]
}}

Do not write any text besides the JSON.
"""
    result = call_llm(prompt)
    return safe_json_parse(
        result,
        fallback={"agents": [], "execution_order": []}
    )

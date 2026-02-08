"""
Multi-agent strategy for complex bugs requiring coordinated repairs.
"""

from typing import Dict, Any, List
from ..agents import generate_agents, execute_agent, retry_execute_agent, task_review


def multi_agent_fix(
    bugs: List[Any],
    plan: str,
    code: str,
    max_review_attempts: int = 3
) -> Dict[str, Any]:
    """
    Orchestrate multiple specialized agents to fix complex bugs.
    
    Process:
    1. Generate specialized agents based on bug types
    2. Execute agents in dependency-aware order
    3. Review each agent's output before proceeding
    4. Allow refinement attempts for failed repairs
    
    Args:
        bugs: List of identified bugs
        plan: Step-by-step repair instructions
        code: Buggy source code
        max_review_attempts: Maximum refinement attempts per agent
    
    Returns:
        Final fixed code after all agents complete successfully
    """
    # Create specialized agents
    agent_config = generate_agents(bugs, plan)
    agent_profiles = {a["name"]: a for a in agent_config["agents"]}
    execution_order = agent_config["execution_order"]
    
    print(f"\n	Created {len(agent_profiles)} specialized agents")
    print(f"	Execution order: {' → '.join(execution_order)}")
    
    current_code = code
    
    # Execute agents in prioritized order
    for agent_name in execution_order:
        agent = agent_profiles.get(agent_name)
        if not agent:
            print(f"	⚠️  Agent {agent_name} not found - skipping")
            continue
        
        print(f"\n	🔧 Executing agent: {agent_name} ({agent['role']})")
        
        # Review loop with refinement capability
        for attempt in range(max_review_attempts):
            if attempt == 0:
                result = execute_agent(agent, current_code)
            else:
                print(f"	⟳ Refinement attempt {attempt + 1}/{max_review_attempts}")
                result = retry_execute_agent(agent, current_code, review["feedback"])
            
            # Review agent's output
            review = task_review(agent, result)
            print(f"	✓ Review decision: {review['decision']}")
            
            if review["decision"] == "APPROVE":
                current_code = result["fixed_code"]
                print(f"	✅ Agent {agent_name} approved")
                break
            
            if attempt == max_review_attempts - 1:
                print(f"	⚠️  Max refinement attempts reached for {agent_name}")
                current_code = result["fixed_code"]  # Use best attempt
    
    return {"fixed_code": current_code, "fix_explanation": "Multi-agent repair completed"}

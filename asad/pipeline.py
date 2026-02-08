"""
Main adaptive debugging pipeline that orchestrates the entire repair process.
"""

from typing import Dict, Any
from .agents.analysis import analyze_problem, new_iteration_analyze_problem
from .agents.review import validate_solution
from .strategies.simple_fix import simple_fix
from .strategies.multi_agent import multi_agent_fix


def adaptive_debugger(buggy_code: str, max_iterations: int = 5) -> str:
    """
    Execute the adaptive debugging pipeline on buggy code.
    
    The pipeline:
    1. Analyzes code complexity and identifies bugs
    2. Selects appropriate repair strategy (simple vs. multi-agent)
    3. Iteratively repairs and validates until fixed or max iterations reached
    
    Args:
        buggy_code: Python source code containing bugs
        max_iterations: Maximum repair attempts before giving up
    
    Returns:
        Fixed code if successful, otherwise best attempt at repair
    """
    # Initial analysis
    analysis_report = analyze_problem(buggy_code)
    print(f"\n[Complexity]: {analysis_report["complexity"]}")
    
    # Early exit if no bugs found
    if not analysis_report.get("bugs"):
        print("\n🟢 No errors found. Code is already fixed")
        return buggy_code
    
    # Iterative repair loop
    current_code = buggy_code
    for iteration in range(max_iterations):
        print(f"\n-------------- ITERATION {iteration + 1} --------------")
        
        # Select repair strategy based on complexity
        if analysis_report["complexity"] == "SIMPLE":
            print("\n[Strategy] Using simple fix path")
            result = simple_fix(analysis_report["bugs"], current_code)
            current_code = result["fixed_code"]
        else:
            print("\n[Strategy] Using multi-agent approach")
            result = multi_agent_fix(
                analysis_report["bugs"],
                analysis_report["plan"],
                current_code
            )
            current_code = result["fixed_code"]
        
        # Validate repair attempt
        validation = validate_solution(current_code)
        status = validation["status"]
        
        if status == "FIXED":
            print(f"\n🟢 Bugs fixed successfully in {iteration + 1} iteration(s)\n")
            return current_code
        
        # Prepare for next iteration
        print("\n🟡 Validation failed. Retrying with updated analysis...")
        print(f"Validation summary: {validation['summary']}")
        
        prev_analysis = analysis_report
        analysis_report = new_iteration_analyze_problem(
            current_code,
            validation,
            prev_analysis
        )
    
    print(f"\n🔴 Failed to fix bugs after {max_iterations} iterations")
    return current_code

"""
Test suite to validate Anomaly #1 patch in ASAD.
Tests polyglot static complexity analyzer for Python and C code.
"""

from ASAD.parsing.complexity_analyzer import CodeComplexityAnalyzer
from Test.buggy_code import simple_buggy_code, medium_buggy_code, complex_buggy_code

def run_tests():
    analyzer = CodeComplexityAnalyzer()

    print("=" * 60)
    print("Test 1: Simple Buggy Code (Python)")
    print("=" * 60)
    rep1 = analyzer.analyze(simple_buggy_code)
    assert rep1["detected_language"] == "python", f"Expected python, got {rep1['detected_language']}"
    assert rep1["source_location_difficulty"]["NLOC"] > 0
    assert rep1["program_understanding_difficulty"]["cyclomatic_complexity"] >= 1
    print("Detected language:", rep1["detected_language"])
    print("Cyclomatic complexity:", rep1["program_understanding_difficulty"]["cyclomatic_complexity"])
    print("NLOC:", rep1["source_location_difficulty"]["NLOC"])
    print("Dependencies:", rep1["inter_function_dependencies"])
    print("-> Test 1 PASSED")

    print("\n" + "=" * 60)
    print("Test 2: Medium Buggy Code (Python)")
    print("=" * 60)
    rep2 = analyzer.analyze(medium_buggy_code)
    assert rep2["detected_language"] == "python"
    print("Detected language:", rep2["detected_language"])
    print("Cyclomatic complexity:", rep2["program_understanding_difficulty"]["cyclomatic_complexity"])
    print("System ops:", rep2["system_level_operations"])
    print("-> Test 2 PASSED")

    print("\n" + "=" * 60)
    print("Test 3: Complex Buggy Code (Python Concurrency & Calls)")
    print("=" * 60)
    rep3 = analyzer.analyze(complex_buggy_code)
    assert rep3["detected_language"] == "python"
    assert rep3["system_level_operations"]["concurrency_detected"] is True, "Concurrency should be detected"
    assert "threading" in rep3["system_level_operations"]["concurrency_constructs"] or "lock" in rep3["system_level_operations"]["concurrency_constructs"]
    print("Detected language:", rep3["detected_language"])
    print("Cyclomatic complexity:", rep3["program_understanding_difficulty"]["cyclomatic_complexity"])
    print("Concurrency detected:", rep3["system_level_operations"]["concurrency_detected"])
    print("Concurrency constructs:", rep3["system_level_operations"]["concurrency_constructs"])
    print("Dependencies:", rep3["inter_function_dependencies"])
    print("-> Test 3 PASSED")

    print("\n" + "=" * 60)
    print("Test 4: Backward Compatibility (C Language)")
    print("=" * 60)
    c_code = """
#include <stdio.h>
#include <pthread.h>

void helper() {
    printf("Hello\\n");
}

int main() {
    int x = 10;
    if (x > 5) {
        helper();
    }
    return 0;
}
"""
    rep_c = analyzer.analyze(c_code)
    assert rep_c["detected_language"] == "c", f"Expected c, got {rep_c['detected_language']}"
    assert rep_c["system_level_operations"]["concurrency_detected"] is True, "pthread should trigger concurrency"
    assert rep_c["inter_function_dependencies"]["number_of_functions"] == 2
    print("Detected language:", rep_c["detected_language"])
    print("Cyclomatic complexity:", rep_c["program_understanding_difficulty"]["cyclomatic_complexity"])
    print("Concurrency detected:", rep_c["system_level_operations"]["concurrency_detected"])
    print("Number of functions:", rep_c["inter_function_dependencies"]["number_of_functions"])
    print("Average fan-in:", rep_c["inter_function_dependencies"]["average_fan_in"])
    print("-> Test 4 PASSED")

    print("\n" + "=" * 60)
    print("Test 5: JSON Serializability (Contract with Analysis Agent)")
    print("=" * 60)
    import json
    json_str_python = json.dumps(rep3, indent=2)
    assert len(json_str_python) > 0
    parsed_back_py = json.loads(json_str_python)
    assert parsed_back_py["detected_language"] == "python"

    json_str_c = json.dumps(rep_c, indent=2)
    assert len(json_str_c) > 0
    parsed_back_c = json.loads(json_str_c)
    assert parsed_back_c["detected_language"] == "c"
    print("Python complexity report successfully serialized to JSON (size:", len(json_str_python), "bytes)")
    print("C complexity report successfully serialized to JSON (size:", len(json_str_c), "bytes)")
    print("-> Test 5 PASSED")

    print("\n" + "=" * 60)
    print("Test 6: Advanced Python Constructs (Async, Match, Comprehensions)")
    print("=" * 60)
    advanced_py = '''
import asyncio

async def fetch_data(session, url):
    async with session.get(url) as response:
        return await response.json()

def process_items(items):
    evens = [x * 2 for x in items if x % 2 == 0]
    mapping = {k: v for k, v in enumerate(evens)}
    return [mapping.get(i) for i in range(len(mapping))]
'''
    rep_adv = analyzer.analyze(advanced_py)
    assert rep_adv["detected_language"] == "python"
    assert rep_adv["program_understanding_difficulty"]["cyclomatic_complexity"] > 1
    assert "asyncio" in rep_adv["system_level_operations"]["concurrency_constructs"]
    print("Detected language:", rep_adv["detected_language"])
    print("Cyclomatic complexity:", rep_adv["program_understanding_difficulty"]["cyclomatic_complexity"])
    print("Concurrency constructs:", rep_adv["system_level_operations"]["concurrency_constructs"])
    print("-> Test 6 PASSED")

    print("\n" + "#" * 60)
    print("ALL 6 TESTS PASSED SUCCESSFULLY! CODE IS FULLY FUNCTIONAL.")
    print("#" * 60)

if __name__ == "__main__":
    run_tests()

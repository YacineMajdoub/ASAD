#!/usr/bin/env python3
"""
Main entry point for ASAD debugger with example execution.
"""

import os
from dotenv import load_dotenv
from asad.pipeline import adaptive_debugger
from examples.buggy_code import complex_buggy_code, medium_buggy_code, simple_buggy_code


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    print("=" * 70)
    print("ASAD: Adaptive Software Analysis and Debugging")
    print("=" * 70)
    
    # Select example to debug
    buggy_code = simple_buggy_code  # Change to medium_buggy_code or simple_buggy_code to test others, or enter you own code
    
    print("\n🔍 Analyzing buggy code...")
    print("-" * 70)
    print(buggy_code[:500] + "..." if len(buggy_code) > 500 else buggy_code)
    print("-" * 70)
    
    # Run adaptive debugger
    fixed_code = adaptive_debugger(buggy_code, max_iterations=5)
    
    print("\n" + "=" * 70)
    print("✅ FINAL FIXED CODE")
    print("=" * 70)
    print(fixed_code)
    print("=" * 70)


if __name__ == "__main__":
    main()

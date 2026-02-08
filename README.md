# ASAD: Adaptive Software Agents for Debugging

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-red.svg)](https://www.apache.org/licenses/LICENSE-2.0)


ASAD introduces an adaptive debugging framework that dynamically selects between single-agent and multi-agent repair strategies based on static analysis of bug complexity. This approach reduces unnecessary coordination overhead while maintaining robustness for challenging debugging scenarios.

## Core Innovation

Traditional multi-agent debugging systems apply fixed coordination patterns regardless of bug characteristics. ASAD solves this inefficiency through **complexity-aware routing**:

- **SIMPLE path**: Direct repair using a single specialized agent for isolated bugs (e.g., syntax errors, single-line logic flaws)
- **COMPLEX path**: Coordinated multi-agent workflow with dependency-aware execution ordering for interdependent defects (e.g., coupled logic errors, resource management issues)

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/asad.git
cd asad

# Install dependencies
pip install -r requirements.txt
```
## Configuration
Paste you API keys in .env.test
```bash
TOGETHER_API_KEY=sk-...
GROQ_API_KEY=gsk-...
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai  # Options: together, groq, openai
```
and run
```bash
cp .env.test .env
```

## Usage
```bash
from asad.pipeline import adaptive_debugger

code_to_debug="PUT YOU CODE HERE"

fixed_code = adaptive_debugger(code_to_debug, max_iterations=5)
print(fixed_code)
```

Or run the example script:

```bash
python main.py
```









# ASAD: Adaptive Software Agents for Debugging

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


ASAD introduces an adaptive debugging framework that dynamically selects between single-agent and multi-agent repair strategies based on static analysis of bug complexity. This approach reduces unnecessary coordination overhead while maintaining robustness for challenging debugging scenarios.

> [!NOTE]
> **Fork Enhancements (`patched-by-mb`)**
> 
> This fork includes a critical patch addressing **Anomaly #1** (Polyglot Static Complexity Analysis):
> - **Issue**: The original analyzer was strictly coupled to the C language (hardcoded Tree-sitter C parser, C AST node types, and C-only concurrency/resource indicators), resulting in erroneous metrics or parsing failures when processing Python code.
> - **Solution**: Implemented a modular polyglot architecture with language profiles (Python, C, C++, Java), automatic language detection, grammar-aware metric extraction (cyclomatic complexity, fan-in/fan-out, call graphs), and graceful fallbacks.
> - **Full Remediation Details**: See [Anomaly #1 Resolution & Plan](docs/ANOMALY_1_RESOLUTION.md).

## Core Innovation

Traditional multi-agent debugging systems apply fixed coordination patterns regardless of bug characteristics. ASAD solves this inefficiency through **complexity-aware routing**:

- **SIMPLE path**: Direct repair using a single specialized agent for isolated bugs (e.g., syntax errors, single-line logic flaws)
- **COMPLEX path**: Coordinated multi-agent workflow with dependency-aware execution ordering for interdependent defects (e.g., coupled logic errors, resource management issues)

## Installation

```bash
# Clone repository
git clone https://github.com/YacineMajdoub/asad.git
cd asad

# Install dependencies
pip install -r requirements.txt
```
## Configuration

Create a .env file in the project root:

```bash 
touch .env
```

Add your API keys and provider configuration to .env:
```bash 
TOGETHER_API_KEY=sk-...
GROQ_API_KEY=gsk-...
OPENAI_API_KEY=sk-...

LLM_PROVIDER="openai"
```
LLM_PROVIDER specifies the provider to use. Supported options are:

```bash 
together
groq
openai
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









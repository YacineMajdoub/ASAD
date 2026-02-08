# ASAD: Adaptive Software Analysis and Debugging

ASAD is an adaptive multi-agent system that automatically debugs Python code using large language models. The system analyzes buggy code, creates specialized debugging agents when needed, and iteratively repairs execution-blocking defects.

## Features

- Automatic complexity assessment (simple vs. complex bugs)
- Specialized agent generation for multi-bug scenarios
- Iterative repair with validation feedback loops
- Support for multiple LLM providers (Together, Groq, OpenAI)
- JSON-safe output parsing with robust error handling

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/asad.git
cd asad

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API keys and run
cp .env.test .env
```
# Usage
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

# Architecture
```bash
asad/
├── llm/          # Unified LLM client interface
├── parsing/      # JSON/code cleaning utilities
├── agents/       # Analysis, execution, and review agents
├── strategies/   # Simple fix vs. multi-agent strategies
└── pipeline.py   # Main orchestration logic
```

# Configuration
```bash
TOGETHER_API_KEY=sk-...
GROQ_API_KEY=gsk-...
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai  # Options: together, groq, openai
```



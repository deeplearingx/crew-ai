# DevCrew: Collaborative AI Development Crew

DevCrew is a multi-agent software development prototype built around the idea of an AI development team. Instead of using a single prompt to generate code, the project separates the development workflow into multiple specialized agents that collaborate in sequence: requirement planning, implementation, verification, and execution feedback.

The repository also contains a simple Python calculator example, a FastAPI backend, a browser dashboard, tool wrappers for file/command operations, and structured runtime logs for observing how the agents work together.

## Why DevCrew

Large language models are useful for code generation, but real engineering work is not only about writing code. A reliable development workflow also needs requirement analysis, architectural planning, file-level implementation, test generation, command execution, regression verification, and bug feedback.

DevCrew is designed to model that workflow as a collaborative crew:

```text
User Requirement
      ↓
Planner Agent  → analyze requirement, inspect files, create implementation plan
      ↓
Coder Agent    → modify files, implement code, run commands, fix syntax/runtime errors
      ↓
Tester Agent   → create tests, execute test suite, report real failures and regressions
      ↓
Execution Log  → stream every step to dashboard for review and debugging
```

This makes the project more than a calculator demo. The calculator is the target application, while DevCrew is the automation layer that coordinates AI agents to build, validate, and iterate on that application.

## Core Highlight: DevCrew Collaboration

### 1. Planner: requirement decomposition and architecture planning

The planner acts as a senior software architect. It reads the current project files, analyzes the user requirement, identifies affected paths, and produces a concrete implementation plan with inputs, outputs, dependencies, and acceptance criteria.

Its job is not to write code directly. Its value is to reduce ambiguity before implementation and give the coder a clear execution path.

### 2. Coder: implementation with real file operations

The coder acts as a senior software developer. It receives the planner's output as context, writes code to disk through the file tool, inspects existing files, and runs shell commands to verify that the implementation is runnable.

The coder is explicitly required to persist source code with `write_file` instead of only describing code in text. This makes the workflow closer to a real development environment.

### 3. Tester: regression testing and failure feedback

The tester acts as a QA engineer. It creates test files, executes real commands such as `python -m pytest`, checks normal paths and edge cases, and reports actual command output instead of simulated results.

This gives the crew a verification loop: generated code must survive execution and test feedback, not just look correct in the model response.

### 4. Shared tools and observable execution

DevCrew agents share a tool layer for:

- reading project files
- writing source/test files
- listing directories
- executing shell commands
- analyzing requirements
- generating implementation guidelines
- designing test strategy
- logging every agent step

The FastAPI backend exposes the execution history and streams agent events to the frontend dashboard through Server-Sent Events. This makes the collaboration process visible: each LLM step, tool call, task start, task completion, and command result can be inspected during development.

## Token Usage Characteristics

DevCrew is a high-token-consumption workflow by design. A single development request may trigger several rounds of:

- project structure scanning
- file reading and context injection
- requirement analysis
- implementation planning
- code generation
- file writing
- command execution
- test generation
- test output analysis
- bug fixing and re-verification

Because Planner, Coder, and Tester each need their own role prompt, task context, tool outputs, and intermediate results, one user request can expand into many model calls. During active development, debugging, and repeated regression testing, this type of multi-agent workflow can consume far more tokens than a single-turn coding assistant.

## Project Structure

```text
.
├── calculator/
│   ├── __init__.py
│   ├── core.py
│   └── validator.py
├── docs/
│   └── superpowers/
├── frontend/
│   ├── dashboard.html
│   └── index.html
├── src/
│   └── dev_crew/
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       ├── tools/
│       │   ├── command_tools.py
│       │   ├── file_tools.py
│       │   ├── logger.py
│       │   └── skills.py
│       └── crew.py
├── tests/
│   └── test_calculator.py
├── api.py
├── main.py
├── terminal_server.py
├── requirements.txt
└── README.md
```

## Main Components

### Calculator application

The `calculator/` package provides the example application used by the crew workflow:

- arithmetic operations
- input validation
- division-by-zero handling
- CLI entry point through `main.py`
- unit tests under `tests/`

### DevCrew orchestration

The `src/dev_crew/crew.py` module defines the multi-agent crew. It loads agent/task configuration from YAML, initializes different LLM roles, attaches specialized tools, and runs the process sequentially.

The current collaboration chain is:

```text
plan_task  →  code_task  →  test_task
planner    →  coder      →  tester
```

### Agent configuration

`src/dev_crew/config/agents.yaml` defines the roles:

- `planner`: Senior Software Architect
- `coder`: Senior Software Developer
- `tester`: QA Engineer
- `manager`: Development Team Lead, reserved for delegation-oriented workflows

`src/dev_crew/config/tasks.yaml` defines the execution contracts for planning, coding, and testing.

### Tool layer

The tools in `src/dev_crew/tools/` are what allow agents to interact with the real project:

- `file_tools.py`: read files, write files, list directories
- `command_tools.py`: execute shell commands and collect stdout/stderr
- `skills.py`: structured requirement analysis, implementation guidance, and test strategy generation
- `logger.py`: structured step logging and SSE-friendly event broadcasting

### Dashboard and API

`api.py` provides a FastAPI backend with:

- calculator API: `/api/calculate`
- event stream: `/api/events`
- execution history: `/api/history`
- dashboard page: `/`
- calculator page: `/calc`

The dashboard is useful for observing how DevCrew agents cooperate during a task instead of treating the model as a black box.

## Installation

Clone the repository:

```bash
git clone https://github.com/deeplearingx/crew-ai.git
cd crew-ai
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install crewai crewai-tools fastapi uvicorn pydantic pyyaml
```

Set the model API key used by the DevCrew LLM configuration:

```bash
export ARK_API_KEY="your_api_key_here"
```

On Windows PowerShell:

```powershell
$env:ARK_API_KEY="your_api_key_here"
```

## Usage

Run the calculator CLI:

```bash
python main.py
```

Run the FastAPI dashboard:

```bash
python api.py
```

Then open:

```text
http://localhost:9000/
```

Calculator page:

```text
http://localhost:9000/calc
```

API docs:

```text
http://localhost:9000/docs
```

## Running Tests

```bash
python -m pytest tests/ -v
```

Expected result:

```text
10 passed
```

## Example Use Cases

DevCrew can be extended toward larger AI software engineering workflows, such as:

- automated code generation from natural language requirements
- repository scanning and technical debt analysis
- unit test generation and regression verification
- bug reproduction and repair loops
- code refactoring with execution feedback
- PR summary generation and review assistance
- multi-agent development dashboards

## Roadmap

- Add a manager-led hierarchical workflow for dynamic task delegation
- Add richer memory for previous development decisions and bug history
- Add PR generation and Git integration
- Add token usage tracking per agent/task/tool call
- Add configurable model providers for Planner, Coder, and Tester
- Add stronger sandboxing for command execution
- Add benchmark tasks for measuring development efficiency

## License

This project is provided as a learning and experimentation example for multi-agent software development workflows.

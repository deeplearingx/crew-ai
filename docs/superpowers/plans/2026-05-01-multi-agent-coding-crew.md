# Multi-Agent Coding Crew Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CrewAI-based multi-agent coding assistant with a manager + 3 specialist agents (planner, coder, tester) using hierarchical process.

**Architecture:** CrewAI Crew with `Process.hierarchical`. Manager agent delegates to specialist agents. Custom tools for file I/O and command execution. Three LLM providers (MiniMax, GLM, Kimi) configured via `LLM` class with custom `base_url`.

**Tech Stack:** CrewAI 1.13.0, crewai_tools (SerperDevTool, FileReadTool, DirectoryReadTool), custom @tool functions, Pydantic

---

## File Structure

| File | Responsibility |
|------|---------------|
| `src/dev_crew/__init__.py` | Package init, expose `DevCrew` |
| `src/dev_crew/config/agents.yaml` | 4 agent definitions (role, goal, backstory) |
| `src/dev_crew/config/tasks.yaml` | 3 task definitions (description, expected_output, context) |
| `src/dev_crew/tools/__init__.py` | Re-export tools |
| `src/dev_crew/tools/file_tools.py` | `write_file` tool (read + list are from crewai_tools) |
| `src/dev_crew/tools/command_tools.py` | `run_command` tool for shell execution |
| `src/dev_crew/crew.py` | `DevCrew` class with `@CrewBase`, agent/task factories, Crew assembly |
| `main.py` | Entry point: parse args, run crew |
| `.env` | API keys and base URLs for all 3 LLM providers |

---

### Task 1: Project scaffold and .env

**Files:**
- Create: `src/dev_crew/__init__.py`
- Create: `src/dev_crew/config/agents.yaml`
- Create: `src/dev_crew/config/tasks.yaml`
- Create: `src/dev_crew/tools/__init__.py`
- Create: `.env`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p src/dev_crew/config src/dev_crew/tools
```

- [ ] **Step 2: Create `src/dev_crew/__init__.py`**

```python
from dev_crew.crew import DevCrew

__all__ = ["DevCrew"]
```

- [ ] **Step 3: Create `src/dev_crew/tools/__init__.py`**

```python
from dev_crew.tools.file_tools import write_file
from dev_crew.tools.command_tools import run_command

__all__ = ["write_file", "run_command"]
```

- [ ] **Step 4: Create placeholder `agents.yaml` and `tasks.yaml`**

`src/dev_crew/config/agents.yaml`:
```yaml
manager:
  role: >
    Development Team Lead
  goal: >
    Decompose user requirements into subtasks, delegate to the right
    specialist agent, review results, and decide if rework is needed
  backstory: >
    You are an experienced tech lead with 10+ years managing development teams.
    You excel at breaking down complex requirements, assigning work to the
    right specialist, and ensuring quality through iterative review.
    You never do the work yourself — you delegate and validate.
    When a tester reports bugs, you send the report back to the coder for fixes.
  allow_delegation: true

planner:
  role: >
    Senior Software Architect
  goal: >
    Analyze requirements and produce a step-by-step implementation plan
    with clear inputs, outputs, and acceptance criteria for each step
  backstory: >
    You are a veteran architect with 15 years of software design experience.
    You create precise, actionable plans that developers can follow without
    ambiguity. You always check existing code before planning and include
    file paths, function signatures, and data flow in your plans.
  allow_delegation: false

coder:
  role: >
    Senior Software Developer
  goal: >
    Implement code according to the plan, following best practices
    and ensuring the code is runnable and well-structured
  backstory: >
    You are an expert developer with 12 years of hands-on coding experience.
    You write clean, well-structured code and follow the plan precisely.
    When you encounter ambiguity, you make reasonable decisions and document
    them in comments. You always verify your code runs before reporting done.
  allow_delegation: false

tester:
  role: >
    QA Engineer
  goal: >
    Run regression tests on the code, verify functional correctness,
    and report bugs with reproduction steps and severity levels
  backstory: >
    You are a detail-oriented QA engineer with 8 years of testing experience.
    You write comprehensive test cases, check edge cases, and never mark
    something as passed unless you have verified it yourself.
    When you find bugs, you provide exact reproduction steps and severity.
  allow_delegation: false
```

`src/dev_crew/config/tasks.yaml`:
```yaml
plan_task:
  description: >
    Analyze the following requirement and create a detailed implementation plan:
    {requirement}

    The plan MUST include:
    1. Files to create or modify (with full paths)
    2. Step-by-step implementation order
    3. Expected output for each step
    4. Acceptance criteria for each step
    5. Dependencies between steps
  expected_output: >
    A structured implementation plan with clear steps, file list,
    function signatures, and acceptance criteria.
  agent: planner

code_task:
  description: >
    Implement the code according to the plan provided above.
    Follow the plan step by step. Write production-quality code.
    After writing each file, verify it is syntactically correct.
  expected_output: >
    Working code that implements all steps from the plan,
    with clear file paths and function signatures.
  agent: coder
  context: [plan_task]

test_task:
  description: >
    Perform regression testing on the code produced above.

    Your responsibilities:
    1. Read the implementation plan and the code
    2. Write test cases covering normal paths and edge cases
    3. Run the tests
    4. Report results

    For each bug found, report:
    - Severity (critical/high/medium/low)
    - Reproduction steps
    - Expected vs actual behavior
    - Suggested fix
  expected_output: >
    Test report including: test cases executed, pass/fail results,
    bugs found with severity, reproduction steps, and suggested fixes.
  agent: tester
  context: [code_task]
```

- [ ] **Step 5: Create `.env` template**

```env
# MiniMax M2.7 (Manager)
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_BASE_URL=https://api.minimax.chat/v1

# GLM-5.1 (Planner)
GLM_API_KEY=your_glm_api_key_here
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4

# Kimi K2.6 (Coder & Tester)
KIMI_API_KEY=your_kimi_api_key_here
KIMI_BASE_URL=https://api.moonshot.cn/v1
```

- [ ] **Step 6: Verify file structure**

```bash
find src -type f | sort
```

Expected: all 5 files created under `src/`

- [ ] **Step 7: Commit**

```bash
git add src/ .env
git commit -m "feat: scaffold project structure with agent and task YAML configs"
```

---

### Task 2: Custom tools — file_tools.py

**Files:**
- Create: `src/dev_crew/tools/file_tools.py`

- [ ] **Step 1: Write `file_tools.py`**

```python
import os
from crewai.tools import tool


@tool("Write content to a file")
def write_file(path: str, content: str) -> str:
    """Write content to a file at the given path. Creates parent directories if needed."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing to {path}: {e}"
```

- [ ] **Step 2: Verify import works**

```bash
cd D:/workspace/crew-ai && ./venv/Scripts/python.exe -c "from dev_crew.tools.file_tools import write_file; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add src/dev_crew/tools/file_tools.py
git commit -m "feat: add write_file custom tool"
```

---

### Task 3: Custom tools — command_tools.py

**Files:**
- Create: `src/dev_crew/tools/command_tools.py`

- [ ] **Step 1: Write `command_tools.py`**

```python
import subprocess

from crewai.tools import tool


@tool("Execute a shell command")
def run_command(command: str, timeout: int = 120) -> str:
    """Execute a shell command and return its stdout and stderr. Timeout in seconds (default 120)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = ""
        if result.stdout:
            output += f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        output += f"Return code: {result.returncode}"
        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
    except Exception as e:
        return f"Error executing command: {e}"
```

- [ ] **Step 2: Verify import works**

```bash
cd D:/workspace/crew-ai && ./venv/Scripts/python.exe -c "from dev_crew.tools.command_tools import run_command; print('ok')"
```

Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add src/dev_crew/tools/command_tools.py
git commit -m "feat: add run_command custom tool"
```

---

### Task 4: DevCrew class — agent and task factories

**Files:**
- Create: `src/dev_crew/crew.py`

- [ ] **Step 1: Write `crew.py`**

```python
import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, FileReadTool, DirectoryReadTool

from dev_crew.tools.file_tools import write_file
from dev_crew.tools.command_tools import run_command


def _load_llm(provider: str) -> LLM:
    """Load an LLM instance from environment variables based on provider name."""
    if provider == "minimax":
        return LLM(
            model="minimax/MiniMax-M2.7",
            api_key=os.environ["MINIMAX_API_KEY"],
            base_url=os.environ.get("MINIMAX_BASE_URL", "https://api.minimax.chat/v1"),
        )
    elif provider == "glm":
        return LLM(
            model="glm/GLM-5.1",
            api_key=os.environ["GLM_API_KEY"],
            base_url=os.environ.get("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4"),
        )
    elif provider == "kimi":
        return LLM(
            model="kimi/kimi-k2.6",
            api_key=os.environ["KIMI_API_KEY"],
            base_url=os.environ.get("KIMI_BASE_URL", "https://api.moonshot.cn/v1"),
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


@CrewBase
class DevCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self):
        super().__init__()
        self._manager_llm = _load_llm("minimax")
        self._planner_llm = _load_llm("glm")
        self._coder_llm = _load_llm("kimi")
        self._tester_llm = _load_llm("kimi")

    @agent
    def manager(self) -> Agent:
        return Agent(
            config=self.agents_config["manager"],
            llm=self._manager_llm,
            allow_delegation=True,
            max_iter=25,
            max_execution_time=600,
            max_retry_limit=2,
            verbose=True,
        )

    @agent
    def planner(self) -> Agent:
        return Agent(
            config=self.agents_config["planner"],
            llm=self._planner_llm,
            tools=[FileReadTool(), DirectoryReadTool(), SerperDevTool()],
            max_iter=15,
            max_execution_time=600,
            max_retry_limit=2,
            verbose=True,
        )

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config["coder"],
            llm=self._coder_llm,
            tools=[FileReadTool(), DirectoryReadTool(), write_file, run_command, SerperDevTool()],
            max_iter=25,
            max_execution_time=600,
            max_retry_limit=2,
            verbose=True,
        )

    @agent
    def tester(self) -> Agent:
        return Agent(
            config=self.agents_config["tester"],
            llm=self._tester_llm,
            tools=[FileReadTool(), DirectoryReadTool(), run_command],
            max_iter=15,
            max_execution_time=600,
            max_retry_limit=2,
            verbose=True,
        )

    @task
    def plan_task(self) -> Task:
        return Task(
            config=self.tasks_config["plan_task"],
            agent=self.planner(),
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config["code_task"],
            agent=self.coder(),
            context=[self.plan_task()],
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config["test_task"],
            agent=self.tester(),
            context=[self.code_task()],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.planner(), self.coder(), self.tester()],
            tasks=[self.plan_task(), self.code_task(), self.test_task()],
            process=Process.hierarchical,
            manager_llm=self._manager_llm,
            verbose=True,
        )
```

- [ ] **Step 2: Verify import works**

```bash
cd D:/workspace/crew-ai && PYTHONPATH=src ./venv/Scripts/python.exe -c "from dev_crew.crew import DevCrew; print('import ok')"
```

Expected: `import ok`

- [ ] **Step 3: Commit**

```bash
git add src/dev_crew/crew.py src/dev_crew/__init__.py
git commit -m "feat: add DevCrew class with agent/task factories and hierarchical process"
```

---

### Task 5: Entry point — main.py

**Files:**
- Create: `main.py`

- [ ] **Step 1: Write `main.py`**

```python
import sys
from dotenv import load_dotenv
from dev_crew import DevCrew


def main():
    load_dotenv()

    if len(sys.argv) < 2:
        print("Usage: python main.py \"<your requirement>\"")
        print("Example: python main.py \"Create a FastAPI app with CRUD endpoints for a Todo model\"")
        sys.exit(1)

    requirement = " ".join(sys.argv[1:])
    print(f"Starting DevCrew with requirement: {requirement}\n")

    crew = DevCrew()
    result = crew.crew().kickoff(inputs={"requirement": requirement})

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(result.raw)

    return result


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify syntax**

```bash
cd D:/workspace/crew-ai && ./venv/Scripts/python.exe -c "import py_compile; py_compile.compile('main.py', doraise=True); print('syntax ok')"
```

Expected: `syntax ok`

- [ ] **Step 3: Commit**

```bash
git add main.py
git commit -m "feat: add main.py entry point"
```

---

### Task 6: End-to-end smoke test

**Files:**
- No new files

- [ ] **Step 1: Verify full import chain**

```bash
cd D:/workspace/crew-ai && PYTHONPATH=src ./venv/Scripts/python.exe -c "
from dev_crew import DevCrew
print('DevCrew imported successfully')
"
```

Expected: `DevCrew imported successfully`

- [ ] **Step 2: Verify crew structure without running**

```bash
cd D:/workspace/crew-ai && PYTHONPATH=src ./venv/Scripts/python.exe -c "
import os
os.environ.setdefault('MINIMAX_API_KEY', 'test')
os.environ.setdefault('GLM_API_KEY', 'test')
os.environ.setdefault('KIMI_API_KEY', 'test')
from dev_crew import DevCrew
crew_instance = DevCrew()
crew = crew_instance.crew()
print(f'Agents: {len(crew.agents)}')
print(f'Tasks: {len(crew.tasks)}')
print(f'Process: {crew.process}')
for a in crew.agents:
    print(f'  Agent: {a.role} (tools: {len(a.tools or [])})')
for t in crew.tasks:
    print(f'  Task: {t.description[:50]}...')
"
```

Expected: 3 agents, 3 tasks, hierarchical process, correct tool counts

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "feat: complete multi-agent coding crew with hierarchical process"
```

---

## Self-Review

**Spec coverage:**
- Manager agent with MiniMax-M2.7, allow_delegation=True → Task 4
- Planner agent with GLM-5.1, file read + web search → Task 4
- Coder agent with Kimi-K2.6, all tools → Task 4
- Tester agent with Kimi-K2.6, file read + command → Task 4
- 3 tasks with context chaining → Task 4
- Custom write_file tool → Task 2
- Custom run_command tool → Task 3
- .env with 3 provider configs → Task 1
- main.py entry point → Task 5
- Hierarchical process with manager_llm → Task 4
- max_execution_time, max_retry_limit → Task 4

**Placeholder scan:** No TBD, TODO, or vague references found.

**Type consistency:** All tool names, agent keys, and task keys match across YAML and Python files.

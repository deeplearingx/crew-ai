# Multi-Agent Coding Crew Design

## Overview

A CrewAI-based multi-agent system that acts as a general-purpose coding assistant. A manager agent orchestrates three specialist agents: planner, coder, and tester. The system follows a plan-code-test pipeline with iterative feedback loops.

## Architecture

**Pattern:** CrewAI Crew with `Process.hierarchical` — Manager agent auto-delegates tasks to specialist agents based on intermediate results.

**Flow:**
```
User requirement → Manager receives
                    ↓
               Planner creates plan
                    ↓
               Manager reviews, assigns to Coder
                    ↓
               Coder implements code
                    ↓
               Manager assigns Tester
                    ↓
               Tester runs regression tests
                    ↓
               Tests pass? ── Yes → Final output
                    │
                    No → Manager feeds report to Coder → Coder fixes → Re-test
```

## Agents

### Manager Agent
- **Role:** Development Team Lead
- **Goal:** Decompose requirements into subtasks, delegate to specialists, review results, decide if rework is needed
- **Backstory:** Experienced tech lead with 10+ years managing development teams. Excels at breaking down complex requirements and ensuring quality through iterative review. Never does the work — delegates and validates.
- **LLM:** MiniMax-M2.7
- **Tools:** None
- **allow_delegation:** True
- **max_iter:** 25

### Planner Agent
- **Role:** Senior Software Architect
- **Goal:** Analyze requirements and produce a step-by-step implementation plan with clear inputs, outputs, and acceptance criteria
- **Backstory:** Veteran architect with 15 years of software design experience. Creates precise, actionable plans that developers can follow without ambiguity. Always checks existing code before planning.
- **LLM:** GLM-5.1
- **Tools:** File read tools, Web search tools
- **max_iter:** 15

### Coder Agent
- **Role:** Senior Software Developer
- **Goal:** Implement code according to the plan, following best practices, ensuring the code is runnable and well-structured
- **Backstory:** Expert developer with 12 years of hands-on coding experience. Writes clean, well-tested code and follows the plan precisely. When encountering ambiguity, makes reasonable decisions and documents them.
- **LLM:** Kimi-K2.6
- **Tools:** File read/write tools, Command execution tools, Web search tools
- **max_iter:** 25

### Tester Agent
- **Role:** QA Engineer
- **Goal:** Run regression tests on the code, verify functional correctness, report bugs with reproduction steps and severity levels
- **Backstory:** Detail-oriented QA engineer with 8 years of testing experience. Writes comprehensive test cases, checks edge cases, and never marks something as passed unless verified.
- **LLM:** Kimi-K2.6
- **Tools:** File read tools, Command execution tools
- **max_iter:** 15

## Tasks

### plan_task
- **Agent:** planner
- **Description:** Analyze the requirement and create a detailed implementation plan. The plan must include: files to create/modify, step-by-step implementation order, expected output for each step, acceptance criteria.
- **Expected Output:** A structured implementation plan with clear steps, file list, and acceptance criteria.

### code_task
- **Agent:** coder
- **Description:** Implement the code according to the plan provided. Follow the plan step by step. Write production-quality code.
- **Expected Output:** Working code that implements all steps from the plan, with clear file paths and function signatures.
- **Context:** plan_task

### test_task
- **Agent:** tester
- **Description:** Perform regression testing on the code produced. Write and run test cases. Report any bugs found with severity, reproduction steps, and suggested fixes.
- **Expected Output:** Test report including: test cases executed, pass/fail results, bugs found with severity and reproduction steps.
- **Context:** code_task

## Custom Tools

### file_tools.py
- `read_file(path)` — Read file content
- `list_directory(path)` — List directory structure
- `write_file(path, content)` — Write content to file

### command_tools.py
- `run_command(command, timeout)` — Execute shell command and return output

### Tool Assignment
| Agent | File Read | File Write | Command | Web Search |
|-------|-----------|------------|---------|------------|
| Planner | Yes | No | No | Yes |
| Coder | Yes | Yes | Yes | Yes |
| Tester | Yes | No | Yes | No |

## Project Structure

```
crew-ai/
├── src/
│   └── dev_crew/
│       ├── __init__.py
│       ├── crew.py
│       ├── config/
│       │   ├── agents.yaml
│       │   └── tasks.yaml
│       └── tools/
│           ├── __init__.py
│           ├── file_tools.py
│           └── command_tools.py
├── main.py
├── pyproject.toml
└── .env
```

## LLM Configuration

All models are accessed via OpenAI-compatible API endpoints. Each model requires its own `base_url` and `api_key` configured in `.env`:

- MiniMax-M2.7 — Manager
- GLM-5.1 — Planner
- Kimi-K2.6 — Coder & Tester

CrewAI supports custom LLM endpoints via the `openai/` prefix with `base_url` override, or via direct `LLM` class instantiation with custom `api_base`.

## Error Handling

- `max_execution_time=600` on all agents (10 min timeout) to prevent hangs
- `max_retry_limit=2` on all agents
- If Tester reports failures, Manager delegates back to Coder with the test report as context
- Total iteration cap via Crew's `max_iter` prevents infinite rework loops

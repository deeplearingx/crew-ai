import os
import yaml

from crewai import Agent, Crew, Process, Task, LLM
from crewai_tools import SerperDevTool

from dev_crew.tools.file_tools import read_file, write_file, list_directory
from dev_crew.tools.command_tools import run_command
from dev_crew.tools.skills import analyze_requirements, implement_with_best_practices, design_test_strategy
from dev_crew.tools.logger import make_step_callback, log_crew_start, log_crew_done, reset_timer

_CONFIG_DIR = os.path.join(os.path.dirname(__file__), "config")


def _load_yaml(name: str) -> dict:
    with open(os.path.join(_CONFIG_DIR, name), encoding="utf-8") as f:
        return yaml.safe_load(f)


_BASE_URL = "https://ark.cn-beijing.volces.com/api/coding/v3"


def _load_llm(provider: str) -> LLM:
    common = dict(api_key=os.environ["ARK_API_KEY"], base_url=_BASE_URL, additional_params={"drop_params": True})
    if provider == "planner":
        llm = LLM(model="openai/MiniMax-M2.7", **common)
    elif provider == "coder":
        llm = LLM(model="openai/Kimi-K2.6", **common)
    elif provider == "tester":
        llm = LLM(model="openai/Kimi-K2.6", **common)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")

    # These models support function calling via the OpenAI-compatible Ark API,
    # but litellm doesn't recognize them and defaults to ReAct text mode.
    # Force native function calling to get reliable tool invocation.
    llm.supports_function_calling = lambda: True

    return llm


class DevCrew:
    def __init__(self):
        agents_cfg = _load_yaml("agents.yaml")
        tasks_cfg = _load_yaml("tasks.yaml")

        self._planner_llm = _load_llm("planner")
        self._coder_llm = _load_llm("coder")
        self._tester_llm = _load_llm("tester")

        self._agents_cfg = agents_cfg
        self._tasks_cfg = tasks_cfg

    def _make_agent(self, name: str, llm: LLM, tools: list | None = None, **overrides) -> Agent:
        cfg = dict(self._agents_cfg[name])
        return Agent(
            role=cfg["role"],
            goal=cfg["goal"],
            backstory=cfg["backstory"],
            llm=llm,
            tools=tools or [],
            step_callback=make_step_callback(cfg["role"]),
            **overrides,
        )

    def _make_task(self, name: str, agent: Agent, context: list | None = None) -> Task:
        cfg = dict(self._tasks_cfg[name])
        return Task(
            description=cfg["description"],
            expected_output=cfg["expected_output"],
            agent=agent,
            context=context or [],
        )

    def crew(self) -> Crew:
        planner = self._make_agent(
            "planner", self._planner_llm,
            tools=[read_file, list_directory, SerperDevTool(), analyze_requirements],
            max_iter=15, max_execution_time=600, max_retry_limit=2, verbose=True,
        )
        coder = self._make_agent(
            "coder", self._coder_llm,
            tools=[read_file, list_directory, write_file, run_command, SerperDevTool(), implement_with_best_practices],
            max_iter=25, max_execution_time=600, max_retry_limit=2, verbose=True,
        )
        tester = self._make_agent(
            "tester", self._tester_llm,
            tools=[read_file, list_directory, write_file, run_command, design_test_strategy],
            max_iter=20, max_execution_time=600, max_retry_limit=2, verbose=True,
        )

        plan_task = self._make_task("plan_task", planner)
        code_task = self._make_task("code_task", coder, context=[plan_task])
        test_task = self._make_task("test_task", tester, context=[code_task])

        return Crew(
            agents=[planner, coder, tester],
            tasks=[plan_task, code_task, test_task],
            process=Process.sequential,
            verbose=True,
        )

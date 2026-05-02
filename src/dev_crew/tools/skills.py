"""Agent-specific skill tools.

Each agent gets a specialized skill that enhances its core capability:
- Planner: analyze_requirements — deep requirement analysis with risk assessment
- Coder: implement_with_best_practices — code generation with quality checks
- Tester: design_test_strategy — systematic test case design and execution
"""

import json

from crewai.tools import tool


@tool("Analyze requirements and assess risks")
def analyze_requirements(requirement: str) -> str:
    """Deep analysis of a requirement: break it into sub-requirements, identify
    dependencies, risks, and suggest technology choices. Returns structured JSON."""
    analysis = {
        "original_requirement": requirement,
        "sub_requirements": [],
        "dependencies": [],
        "risks": [],
        "suggested_tech": [],
        "complexity": "medium",
    }

    # Simple keyword-based analysis to guide the planner
    req_lower = requirement.lower()

    keywords_to_subs = {
        "crud": ["Create operation", "Read operation", "Update operation", "Delete operation"],
        "api": ["Endpoint design", "Request/Response schema", "Error handling"],
        "auth": ["Authentication flow", "Session management", "Permission model"],
        "database": ["Schema design", "Migration plan", "Connection management"],
        "test": ["Unit tests", "Integration tests", "Test fixtures"],
        "ui": ["Component design", "State management", "User interaction flow"],
        "calculator": ["Core arithmetic logic", "Input validation", "Error handling", "User interface"],
    }

    for keyword, subs in keywords_to_subs.items():
        if keyword in req_lower:
            analysis["sub_requirements"].extend(subs)

    if not analysis["sub_requirements"]:
        analysis["sub_requirements"] = ["Core functionality", "Input validation", "Error handling"]

    risk_keywords = {
        "performance": "Performance bottleneck under load",
        "security": "Security vulnerability in input handling",
        "concurrent": "Race condition in shared state",
        "large": "Scalability concern with large data",
        "real-time": "Latency in real-time processing",
    }
    for keyword, risk in risk_keywords.items():
        if keyword in req_lower:
            analysis["risks"].append(risk)

    tech_keywords = {
        "web": ["FastAPI or Flask", "RESTful design"],
        "database": ["SQLite for dev", "PostgreSQL for prod"],
        "test": ["pytest", "coverage"],
        "calculator": ["Python dataclasses", "Type hints"],
    }
    for keyword, techs in tech_keywords.items():
        if keyword in req_lower:
            analysis["suggested_tech"].extend(techs)

    analysis["complexity"] = "high" if len(analysis["sub_requirements"]) > 5 else "medium"

    return json.dumps(analysis, indent=2, ensure_ascii=False)


@tool("Implement code with Karpathy guidelines")
def implement_with_best_practices(description: str) -> str:
    """Returns coding guidelines combining best practices and Karpathy principles.
    Call this BEFORE writing code. Follow every rule strictly. Returns structured guidance."""
    guidelines = {
        "task": description,
        "principle_1_think_before_coding": {
            "rule": "Don't assume. Don't hide confusion. Surface tradeoffs.",
            "steps": [
                "State assumptions explicitly. If uncertain, flag it.",
                "If multiple interpretations exist, list them — don't pick silently.",
                "If a simpler approach exists, use it. Push back on overcomplication.",
                "If something is unclear, stop and flag it. Name what's confusing.",
            ],
        },
        "principle_2_simplicity_first": {
            "rule": "Minimum code that solves the problem. Nothing speculative.",
            "steps": [
                "No features beyond what was asked.",
                "No abstractions for single-use code.",
                "No 'flexibility' or 'configurability' that wasn't requested.",
                "No error handling for impossible scenarios.",
                "If you write 200 lines and it could be 50, rewrite it.",
                "Ask: 'Would a senior engineer say this is overcomplicated?' If yes, simplify.",
            ],
        },
        "principle_3_surgical_changes": {
            "rule": "Touch only what you must. Clean up only your own mess.",
            "steps": [
                "Don't 'improve' adjacent code, comments, or formatting.",
                "Don't refactor things that aren't broken.",
                "Match existing style, even if you'd do it differently.",
                "Every changed line should trace directly to the user's request.",
            ],
        },
        "principle_4_goal_driven_execution": {
            "rule": "Define success criteria. Loop until verified.",
            "steps": [
                "Transform tasks into verifiable goals with explicit checks.",
                "State a brief plan before coding: Step → verify: check.",
                "After coding, run the code to verify it works. If it fails, fix and re-run.",
                "Strong success criteria = loop independently. Weak criteria = constant clarification.",
            ],
        },
        "code_quality_checklist": [
            "Define clear function/class signatures with type hints",
            "Handle edge cases at system boundaries only (user input, external APIs)",
            "Use descriptive variable and function names",
            "Keep functions short and focused (single responsibility)",
            "Ensure code is runnable — test imports and syntax via run_command",
            "Handle errors with specific exceptions, not bare except",
        ],
        "anti_patterns_to_avoid": [
            "Over-engineering: factories, strategies, plugins for simple cases",
            "Speculative generality: 'we might need this later'",
            "Premature optimization: caching, async, pooling before measuring",
            "Comment overuse: code should be self-documenting",
            "Wrapper functions that add no logic",
        ],
        "success_criteria": [
            "All files compile without syntax errors (verify with run_command)",
            "The code actually runs and produces correct output",
            "No code beyond what the plan requires",
            "Every function has a clear, single purpose",
        ],
    }
    return json.dumps(guidelines, indent=2, ensure_ascii=False)


@tool("Design a systematic test strategy")
def design_test_strategy(description: str) -> str:
    """Design a comprehensive test strategy for the described code.
    Covers unit, integration, edge cases, and error scenarios. Returns structured guidance."""
    strategy = {
        "target": description,
        "test_categories": {
            "happy_path": [
                "Test each public function with valid inputs",
                "Verify correct return values and types",
            ],
            "edge_cases": [
                "Empty input / zero values",
                "Very large numbers (overflow)",
                "Very small numbers (precision)",
                "Negative numbers",
                "Float vs int behavior",
            ],
            "error_handling": [
                "Invalid input types (string where number expected)",
                "Missing required arguments",
                "Division by zero",
                "Out-of-range values",
            ],
            "integration": [
                "End-to-end flow from input to output",
                "CLI argument parsing (if applicable)",
                "Module import and initialization",
            ],
        },
        "execution_order": [
            "1. Install pytest if needed",
            "2. Write test file with all categories",
            "3. Run: python -m pytest -v",
            "4. Report actual output",
        ],
        "coverage_targets": {
            "statements": ">= 80%",
            "branches": ">= 70%",
        },
    }
    return json.dumps(strategy, indent=2, ensure_ascii=False)

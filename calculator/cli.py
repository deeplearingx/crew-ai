"""
Interactive command-line interface for the Python Calculator.

Supports multiple calculations in a session with input validation
and graceful error handling.
"""

import sys

from calculator.core import calculate
from calculator.validator import validate_number, validate_operator


def get_input(prompt: str) -> str:
    """Read a line of input from the user."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye!")
        sys.exit(0)


def perform_calculation() -> bool:
    """Execute one calculation cycle.

    Returns:
        True if the calculation succeeded, False otherwise.
    """
    try:
        first_raw = get_input("Enter first number: ")
        first = validate_number(first_raw)
    except ValueError as exc:
        print(f"Error: {exc}")
        return False

    operator_raw = get_input("Enter operator (+, -, *, /): ")
    try:
        operator = validate_operator(operator_raw)
    except ValueError as exc:
        print(f"Error: {exc}")
        return False

    try:
        second_raw = get_input("Enter second number: ")
        second = validate_number(second_raw)
    except ValueError as exc:
        print(f"Error: {exc}")
        return False

    try:
        result = calculate(first, operator, second)
    except ValueError as exc:
        print(f"Error: {exc}")
        return False

    print(f"Result: {result}")
    return True


def ask_continue() -> bool:
    """Ask the user whether to perform another calculation.

    Returns:
        True if the user wants to continue, False otherwise.
    """
    while True:
        choice = get_input("\nContinue? (y/n): ").strip().lower()
        if choice in {"y", "yes"}:
            return True
        if choice in {"n", "no"}:
            return False
        print("Please enter 'y' or 'n'.")


def main() -> None:
    """Run the interactive calculator session."""
    print("=== Python Calculator ===")

    while True:
        print()
        perform_calculation()

        if not ask_continue():
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()

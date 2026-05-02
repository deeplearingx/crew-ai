"""
Input validation utilities for the Python Calculator.
"""

VALID_OPERATORS = {"+", "-", "*", "/"}


def validate_number(value: str) -> float:
    """Validate and convert a numeric string to a float.
    
    Args:
        value: A string representing a number.
    
    Returns:
        The numeric value as a float.
    
    Raises:
        ValueError: If the string cannot be converted to a float.
    """
    try:
        return float(value.strip())
    except ValueError:
        raise ValueError(f"Invalid number: {value.strip()}")


def validate_operator(value: str) -> str:
    """Validate that an operator string is one of the supported operators.
    
    Args:
        value: A string representing an operator.
    
    Returns:
        The operator string, stripped of whitespace.
    
    Raises:
        ValueError: If the operator is not supported.
    """
    cleaned = value.strip()
    if cleaned not in VALID_OPERATORS:
        raise ValueError(f"Invalid operator: {cleaned}")
    return cleaned

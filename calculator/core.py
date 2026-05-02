"""
Core arithmetic operation functions for the Python Calculator.
"""


def _to_float(value):
    """Convert value to float, raising TypeError for non-numeric types."""
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    raise TypeError(f"Operand must be a number, got {type(value).__name__}")


def add(a, b):
    """Return the sum of two numbers."""
    return _to_float(a) + _to_float(b)


def subtract(a, b):
    """Return the difference between two numbers."""
    return _to_float(a) - _to_float(b)


def multiply(a, b):
    """Return the product of two numbers."""
    return _to_float(a) * _to_float(b)


def divide(a, b):
    """Return the quotient of two numbers.

    Raises:
        ValueError: If the divisor is zero.
    """
    b_float = _to_float(b)
    if b_float == 0:
        raise ValueError("Cannot divide by zero")
    return _to_float(a) / b_float


def calculate(a, operator, b):
    """Dispatch to the appropriate arithmetic operation.

    Args:
        a: First operand.
        operator: One of '+', '-', '*', '/'.
        b: Second operand.

    Returns:
        Result of the arithmetic operation as a float.

    Raises:
        ValueError: If the operator is unknown or division by zero occurs.
        TypeError: If operands are not numeric.
    """
    operations = {
        "+": add,
        "-": subtract,
        "*": multiply,
        "/": divide,
    }

    if operator not in operations:
        raise ValueError(f"Unknown operator: {operator}")

    return operations[operator](a, b)

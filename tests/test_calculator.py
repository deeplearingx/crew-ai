"""
Unit tests for the Python Calculator.
"""

import pytest

from calculator.core import add, subtract, multiply, divide, calculate
from calculator.validator import validate_number, validate_operator


class TestCalculatorCore:
    """Tests for core arithmetic operations."""

    def test_add(self):
        assert add(2, 3) == 5.0
        assert add(-1, 1) == 0.0
        assert add(1.5, 2.5) == 4.0

    def test_subtract(self):
        assert subtract(10, 4) == 6.0
        assert subtract(5, 10) == -5.0
        assert subtract(2.5, 1.5) == 1.0

    def test_multiply(self):
        assert multiply(3, 4) == 12.0
        assert multiply(-2, 5) == -10.0
        assert multiply(0.5, 4) == 2.0

    def test_divide(self):
        assert divide(15, 3) == 5.0
        assert divide(7, 2) == 3.5
        assert divide(-6, 3) == -2.0

    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)

    def test_calculate_dispatch(self):
        assert calculate(10, "+", 5) == 15.0
        assert calculate(10, "-", 3) == 7.0
        assert calculate(4, "*", 5) == 20.0
        assert calculate(20, "/", 4) == 5.0

    def test_calculate_unknown_operator(self):
        with pytest.raises(ValueError, match="Unknown operator: %"):
            calculate(10, "%", 2)

    def test_calculate_divide_by_zero(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calculate(10, "/", 0)


class TestValidator:
    """Tests for input validation utilities."""

    def test_validate_number_valid(self):
        assert validate_number("42") == 42.0
        assert validate_number("3.14") == 3.14
        assert validate_number("  5  ") == 5.0
        assert validate_number("-7") == -7.0

    def test_validate_number_invalid(self):
        with pytest.raises(ValueError, match="Invalid number: abc"):
            validate_number("abc")

    def test_validate_operator_valid(self):
        assert validate_operator("+") == "+"
        assert validate_operator("-") == "-"
        assert validate_operator("*") == "*"
        assert validate_operator("/") == "/"
        assert validate_operator("  +  ") == "+"

    def test_validate_operator_invalid(self):
        with pytest.raises(ValueError, match="Invalid operator: %"):
            validate_operator("%")

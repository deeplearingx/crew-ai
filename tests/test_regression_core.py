"""
Regression tests for calculator.core module.
Covers normal paths, edge cases, and error scenarios.
"""
import pytest
import sys
from calculator.core import add, subtract, multiply, divide, calculate


class TestAdd:
    def test_positive_numbers(self):
        assert add(2, 3) == 5.0

    def test_negative_numbers(self):
        assert add(-2, -3) == -5.0

    def test_mixed_signs(self):
        assert add(-2, 3) == 1.0

    def test_zero(self):
        assert add(0, 5) == 5.0
        assert add(5, 0) == 5.0

    def test_floats(self):
        assert add(1.1, 2.2) == pytest.approx(3.3)

    def test_large_numbers(self):
        assert add(1e10, 1e10) == 2e10

    def test_int_input_returns_float(self):
        result = add(1, 2)
        assert isinstance(result, float)


class TestSubtract:
    def test_positive_numbers(self):
        assert subtract(5, 3) == 2.0

    def test_negative_result(self):
        assert subtract(3, 5) == -2.0

    def test_zero(self):
        assert subtract(5, 0) == 5.0
        assert subtract(0, 5) == -5.0

    def test_floats(self):
        assert subtract(5.5, 2.2) == pytest.approx(3.3)


class TestMultiply:
    def test_positive_numbers(self):
        assert multiply(3, 4) == 12.0

    def test_by_zero(self):
        assert multiply(5, 0) == 0.0
        assert multiply(0, 5) == 0.0

    def test_negative_numbers(self):
        assert multiply(-3, 4) == -12.0
        assert multiply(-3, -4) == 12.0

    def test_floats(self):
        assert multiply(0.5, 4) == 2.0


class TestDivide:
    def test_positive_numbers(self):
        assert divide(10, 2) == 5.0

    def test_negative_numbers(self):
        assert divide(-10, 2) == -5.0
        assert divide(-10, -2) == 5.0

    def test_float_result(self):
        assert divide(7, 2) == 3.5

    def test_divide_by_zero_raises(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(10, 0)

    def test_divide_by_zero_with_zero_dividend(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(0, 0)

    def test_very_small_divisor(self):
        # Edge case: very small but non-zero divisor should work
        result = divide(1, 1e-10)
        assert result == 1e10


class TestCalculateDispatcher:
    def test_add(self):
        assert calculate(1, "+", 2) == 3.0

    def test_subtract(self):
        assert calculate(5, "-", 3) == 2.0

    def test_multiply(self):
        assert calculate(3, "*", 4) == 12.0

    def test_divide(self):
        assert calculate(10, "/", 2) == 5.0

    def test_unknown_operator(self):
        with pytest.raises(ValueError, match="Unknown operator: %"):
            calculate(10, "%", 2)

    def test_empty_operator(self):
        with pytest.raises(ValueError, match="Unknown operator: "):
            calculate(10, "", 2)

    def test_divide_by_zero_via_calculate(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calculate(10, "/", 0)

    def test_non_numeric_string_operands(self):
        # calculate accepts any types that support arithmetic; str will fail at runtime
        with pytest.raises(TypeError):
            calculate("a", "+", "b")

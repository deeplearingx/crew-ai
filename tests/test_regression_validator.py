"""
Regression tests for calculator.validator module.
Covers normal paths, edge cases, and error scenarios.
"""
import pytest
from calculator.validator import validate_number, validate_operator


class TestValidateNumber:
    def test_integer_string(self):
        assert validate_number("42") == 42.0

    def test_float_string(self):
        assert validate_number("3.14") == 3.14

    def test_whitespace_stripping(self):
        assert validate_number("  5  ") == 5.0
        assert validate_number("\t7\n") == 7.0

    def test_negative_number(self):
        assert validate_number("-7") == -7.0

    def test_zero(self):
        assert validate_number("0") == 0.0

    def test_large_number(self):
        assert validate_number("1e308") == 1e308

    def test_invalid_string(self):
        with pytest.raises(ValueError, match="Invalid number: abc"):
            validate_number("abc")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="Invalid number: "):
            validate_number("")

    def test_mixed_invalid(self):
        with pytest.raises(ValueError, match="Invalid number: 12abc"):
            validate_number("12abc")

    def test_special_characters(self):
        with pytest.raises(ValueError, match="Invalid number: "):
            validate_number("$100")


class TestValidateOperator:
    def test_valid_operators(self):
        for op in ["+", "-", "*", "/"]:
            assert validate_operator(op) == op

    def test_whitespace_stripping(self):
        assert validate_operator("  +  ") == "+"
        assert validate_operator("\t-\n") == "-"

    def test_invalid_operator(self):
        with pytest.raises(ValueError, match="Invalid operator: %"):
            validate_operator("%")

    def test_empty_string(self):
        with pytest.raises(ValueError, match="Invalid operator: "):
            validate_operator("")

    def test_word_operator(self):
        with pytest.raises(ValueError, match="Invalid operator: add"):
            validate_operator("add")

    def test_multiple_chars(self):
        with pytest.raises(ValueError, match="Invalid operator: ++"):
            validate_operator("++")

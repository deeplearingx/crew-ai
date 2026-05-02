"""
Regression tests for calculator.cli module.
Uses monkeypatch to simulate user input.
"""
import sys
import pytest
from calculator.cli import get_input, perform_calculation, ask_continue, main


class TestGetInput:
    def test_normal_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "42")
        assert get_input("Enter: ") == "42"

    def test_eof_error(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt: (_ for _ in ()).throw(EOFError()))
        with pytest.raises(SystemExit):
            get_input("Enter: ")
        captured = capsys.readouterr()
        assert "Goodbye!" in captured.out

    def test_keyboard_interrupt(self, monkeypatch, capsys):
        monkeypatch.setattr("builtins.input", lambda prompt: (_ for _ in ()).throw(KeyboardInterrupt()))
        with pytest.raises(SystemExit):
            get_input("Enter: ")
        captured = capsys.readouterr()
        assert "Goodbye!" in captured.out


class TestPerformCalculation:
    def test_successful_calculation(self, monkeypatch, capsys):
        inputs = iter(["10", "+", "5"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        assert perform_calculation() is True
        captured = capsys.readouterr()
        assert "Result: 15.0" in captured.out

    def test_invalid_first_number(self, monkeypatch, capsys):
        inputs = iter(["abc", "+", "5"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        assert perform_calculation() is False
        captured = capsys.readouterr()
        assert "Invalid number: abc" in captured.out

    def test_invalid_operator(self, monkeypatch, capsys):
        inputs = iter(["10", "%", "5"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        assert perform_calculation() is False
        captured = capsys.readouterr()
        assert "Invalid operator: %" in captured.out

    def test_invalid_second_number(self, monkeypatch, capsys):
        inputs = iter(["10", "+", "xyz"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        assert perform_calculation() is False
        captured = capsys.readouterr()
        assert "Invalid number: xyz" in captured.out

    def test_divide_by_zero(self, monkeypatch, capsys):
        inputs = iter(["10", "/", "0"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        assert perform_calculation() is False
        captured = capsys.readouterr()
        assert "Cannot divide by zero" in captured.out


class TestAskContinue:
    def test_yes(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "y")
        assert ask_continue() is True

    def test_yes_full(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "yes")
        assert ask_continue() is True

    def test_no(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "n")
        assert ask_continue() is False

    def test_no_full(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "no")
        assert ask_continue() is False

    def test_invalid_then_valid(self, monkeypatch):
        inputs = iter(["maybe", "y"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(inputs))
        assert ask_continue() is True

    def test_whitespace_handling(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "  Y  ")
        assert ask_continue() is True

    def test_mixed_case(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "YeS")
        assert ask_continue() is True

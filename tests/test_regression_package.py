"""
Regression tests for package initialization and imports.
"""
import calculator


class TestPackageInit:
    def test_version(self):
        assert hasattr(calculator, "__version__")
        assert calculator.__version__ == "1.0.0"

    def test_author(self):
        assert hasattr(calculator, "__author__")
        assert calculator.__author__ == "Python Calculator Team"

    def test_all_exports(self):
        assert hasattr(calculator, "__all__")
        assert "core" in calculator.__all__
        assert "validator" in calculator.__all__

    def test_import_core(self):
        from calculator.core import add, subtract, multiply, divide, calculate
        assert callable(add)
        assert callable(calculate)

    def test_import_validator(self):
        from calculator.validator import validate_number, validate_operator
        assert callable(validate_number)
        assert callable(validate_operator)

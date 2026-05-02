# Python Calculator

A simple, clean command-line calculator supporting basic arithmetic operations.

## Features

- Addition, subtraction, multiplication, and division
- Input validation with descriptive error messages
- Graceful handling of division by zero
- Interactive CLI with the ability to perform multiple calculations in a session
- Comprehensive unit tests

## Installation

1. Clone or download this repository.
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the calculator from the command line:

```bash
python main.py
```

Example session:

```
=== Python Calculator ===
Enter first number: 10
Enter operator (+, -, *, /): +
Enter second number: 5
Result: 15.0

Continue? (y/n): y

Enter first number: 20
Enter operator (+, -, *, /): /
Enter second number: 4
Result: 5.0

Continue? (y/n): n
Goodbye!
```

## Project Structure

```
.
├── calculator/
│   ├── __init__.py      # Package initialization
│   ├── core.py          # Core arithmetic operations
│   └── validator.py     # Input validation utilities
├── tests/
│   └── test_calculator.py   # Unit tests
├── main.py              # CLI entry point
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Running Tests

Use `pytest` to run the test suite:

```bash
pytest tests/ -v
```

Expected output:

```
========================= test session starts ==========================
...
tests/test_calculator.py::TestCalculatorCore::test_add PASSED
tests/test_calculator.py::TestCalculatorCore::test_subtract PASSED
tests/test_calculator.py::TestCalculatorCore::test_multiply PASSED
tests/test_calculator.py::TestCalculatorCore::test_divide PASSED
tests/test_calculator.py::TestCalculatorCore::test_divide_by_zero PASSED
tests/test_calculator.py::TestCalculatorCore::test_calculate_dispatch PASSED
tests/test_calculator.py::TestValidator::test_validate_number_valid PASSED
tests/test_calculator.py::TestValidator::test_validate_number_invalid PASSED
tests/test_calculator.py::TestValidator::test_validate_operator_valid PASSED
tests/test_calculator.py::TestValidator::test_validate_operator_invalid PASSED
========================== 10 passed in 0.XXs ==========================
```

## Error Handling

- Invalid numbers raise a `ValueError` with a clear message.
- Division by zero raises a `ValueError: Cannot divide by zero`.
- Invalid operators raise a `ValueError: Invalid operator: {operator}`.
- Unknown operators in the `calculate()` dispatcher raise a `ValueError: Unknown operator: {operator}`.

## License

This project is provided as a learning example and is free to use.

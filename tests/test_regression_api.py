"""
Regression tests for api.py FastAPI backend.
Uses TestClient for HTTP endpoint testing.
"""
import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)


class TestCalculateEndpoint:
    def test_add(self):
        response = client.post("/api/calculate", json={"a": 2, "operator": "+", "b": 3})
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == 5.0
        # Pydantic parses ints as floats, so expression uses 2.0 and 3.0
        assert "2.0 + 3.0 = 5.0" in data["expression"]

    def test_subtract(self):
        response = client.post("/api/calculate", json={"a": 10, "operator": "-", "b": 3})
        assert response.status_code == 200
        assert response.json()["result"] == 7.0

    def test_multiply(self):
        response = client.post("/api/calculate", json={"a": 4, "operator": "*", "b": 5})
        assert response.status_code == 200
        assert response.json()["result"] == 20.0

    def test_divide(self):
        response = client.post("/api/calculate", json={"a": 20, "operator": "/", "b": 4})
        assert response.status_code == 200
        assert response.json()["result"] == 5.0

    def test_divide_by_zero(self):
        response = client.post("/api/calculate", json={"a": 10, "operator": "/", "b": 0})
        assert response.status_code == 400
        assert "Cannot divide by zero" in response.json()["detail"]

    def test_unknown_operator(self):
        response = client.post("/api/calculate", json={"a": 10, "operator": "%", "b": 2})
        assert response.status_code == 400
        assert "Invalid operator" in response.json()["detail"]

    def test_missing_field(self):
        response = client.post("/api/calculate", json={"a": 10, "operator": "+"})
        assert response.status_code == 422

    def test_invalid_number_type_string(self):
        response = client.post("/api/calculate", json={"a": "abc", "operator": "+", "b": 2})
        assert response.status_code == 422

    def test_negative_numbers(self):
        response = client.post("/api/calculate", json={"a": -5, "operator": "*", "b": -4})
        assert response.status_code == 200
        assert response.json()["result"] == 20.0

    def test_float_numbers(self):
        response = client.post("/api/calculate", json={"a": 1.5, "operator": "+", "b": 2.5})
        assert response.status_code == 200
        assert response.json()["result"] == 4.0


class TestHistoryEndpoint:
    def test_history_returns_list(self):
        response = client.get("/api/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestStaticPages:
    def test_dashboard(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_calculator_page(self):
        response = client.get("/calc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

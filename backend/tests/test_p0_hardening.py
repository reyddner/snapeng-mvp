"""Testes de hardening P0/P1: rate limit, formulas, senha."""

import pytest
from fastapi.testclient import TestClient

from app.core.rate_limit import _client_key
from app.core.safe_formula import evaluate_formula, is_formula_shape_safe, substitute_inputs
from app.main import app
from app.services.template_engine import TemplateEngine

client = TestClient(app)


class _FakeClient:
    def __init__(self, host: str):
        self.host = host


class _FakeRequest:
    def __init__(self, host: str, headers: dict | None = None):
        self.client = _FakeClient(host)
        self.headers = headers or {}


def test_client_key_ignores_forged_x_forwarded_for(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "TRUST_PROXY_HEADERS", False)
    req = _FakeRequest("10.0.0.5", {"x-forwarded-for": "1.2.3.4"})
    assert _client_key(req, "login") == "login:10.0.0.5"


def test_client_key_uses_forwarded_when_proxy_trusted(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "TRUST_PROXY_HEADERS", True)
    req = _FakeRequest("10.0.0.5", {"x-forwarded-for": "1.2.3.4, 10.0.0.5"})
    assert _client_key(req, "login") == "login:1.2.3.4"


def test_safe_formula_evaluates_basic_math():
    assert evaluate_formula("10 / 2 + 3") == 8.0


def test_safe_formula_rejects_names_and_calls():
    with pytest.raises(ValueError):
        evaluate_formula("__import__('os').system('id')")
    with pytest.raises(ValueError):
        evaluate_formula("abs(1)")


def test_substitute_inputs_uses_word_boundary():
    out = substitute_inputs("area / 2", ["a"], {"a": 10})
    # 'a' não deve substituir dentro de 'area'
    assert "area" in out
    assert evaluate_formula(substitute_inputs("a / 2", ["a"], {"a": 10})) == 5.0


def test_formula_shape_rejects_attribute_access():
    assert is_formula_shape_safe("cbr_campo / 1.5")
    assert not is_formula_shape_safe("obj.attr")
    assert not is_formula_shape_safe("x[0]")


def test_template_engine_calculations_safe():
    engine = TemplateEngine()
    results = engine._process_calculations(
        [{"name": "x", "formula": "cbr / 1.5", "inputs": ["cbr"], "unit": "%"}],
        {"cbr": 3},
    )
    assert results["x"]["value"] == 2.0


def test_register_rejects_short_password():
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "short.pass@example.com",
            "password": "curta",
            "full_name": "Teste",
        },
    )
    assert response.status_code == 422

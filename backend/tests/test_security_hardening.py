"""Testes de configuracao e rate limit."""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from app.config import Settings
from app.core.rate_limit import InMemoryRateLimiter
from app.main import app

client = TestClient(app)


def test_settings_accept_debug_dev_secret():
    settings = Settings(DEBUG=True, SECRET_KEY="dev-secret-key-change-in-production-min-32-chars-long")
    assert settings.DEBUG is True


def test_settings_reject_insecure_secret_in_production():
    with pytest.raises(ValidationError):
        Settings(DEBUG=False, SECRET_KEY="dev-secret-key-change-in-production-min-32-chars-long")


def test_settings_accept_strong_secret_in_production():
    settings = Settings(
        DEBUG=False,
        SECRET_KEY="production-grade-secret-key-with-enough-entropy-123",
    )
    assert settings.DEBUG is False


def test_in_memory_rate_limiter_blocks_excess():
    limiter = InMemoryRateLimiter(max_calls=2, period_seconds=60)
    limiter.check("k")
    limiter.check("k")
    with pytest.raises(Exception) as exc:
        limiter.check("k")
    assert exc.value.status_code == 429


def test_ingestion_rate_limit_returns_429():
    from app.core import rate_limit as rl

    original = rl.ingestion_limiter
    rl.ingestion_limiter = InMemoryRateLimiter(max_calls=2, period_seconds=60)
    try:
        payload = {"file": ("a.txt", b"texto", "text/plain")}
        assert client.post("/api/v1/ingestion/extract", files=payload).status_code == 200
        assert client.post("/api/v1/ingestion/extract", files=payload).status_code == 200
        blocked = client.post("/api/v1/ingestion/extract", files=payload)
        assert blocked.status_code == 429
    finally:
        rl.ingestion_limiter = original

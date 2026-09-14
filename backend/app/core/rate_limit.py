"""Rate limiting com Redis (preferencial) e fallback em memoria."""

from __future__ import annotations

from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from typing import Optional

from fastapi import HTTPException, Request, status

from app.config import settings

_redis_client = None
_redis_checked = False


def _get_redis():
    """Retorna cliente Redis ou None se indisponivel."""
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    try:
        import redis

        client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=0.5,
            socket_timeout=0.5,
        )
        client.ping()
        _redis_client = client
    except Exception:
        _redis_client = None
    return _redis_client


class InMemoryRateLimiter:
    def __init__(self, max_calls: int, period_seconds: float):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def check(self, key: str) -> None:
        now = monotonic()
        with self._lock:
            bucket = self._hits[key]
            while bucket and now - bucket[0] > self.period_seconds:
                bucket.popleft()
            if len(bucket) >= self.max_calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Muitas requisições. Aguarde um momento e tente novamente.",
                )
            bucket.append(now)


class HybridRateLimiter:
    """Usa Redis quando disponivel; caso contrario, memoria local."""

    def __init__(self, name: str, max_calls: int, period_seconds: float):
        self.name = name
        self.max_calls = max_calls
        self.period_seconds = int(period_seconds)
        self._memory = InMemoryRateLimiter(max_calls, period_seconds)

    def check(self, key: str) -> None:
        client = _get_redis()
        if client is None:
            self._memory.check(key)
            return
        redis_key = f"rl:{self.name}:{key}"
        try:
            count = client.incr(redis_key)
            if count == 1:
                client.expire(redis_key, self.period_seconds)
            if count > self.max_calls:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Muitas requisições. Aguarde um momento e tente novamente.",
                )
        except HTTPException:
            raise
        except Exception:
            self._memory.check(key)


generate_bundle_limiter = HybridRateLimiter("generate-bundle", max_calls=10, period_seconds=60)
ingestion_limiter = HybridRateLimiter("ingestion", max_calls=20, period_seconds=60)
template_preview_limiter = HybridRateLimiter("template-preview", max_calls=20, period_seconds=60)
template_generate_limiter = HybridRateLimiter("template-generate", max_calls=10, period_seconds=60)
auth_login_limiter = HybridRateLimiter("auth-login", max_calls=12, period_seconds=60)
auth_register_limiter = HybridRateLimiter("auth-register", max_calls=6, period_seconds=60)
draft_write_limiter = HybridRateLimiter("draft-write", max_calls=20, period_seconds=60)
ai_limiter = HybridRateLimiter("ai", max_calls=20, period_seconds=60)


def _client_key(request: Request, prefix: str) -> str:
    """
    Chave de rate limit.

    Por padrao usa apenas request.client.host (nao forjavel pelo cliente).
    X-Forwarded-For so e considerado quando TRUST_PROXY_HEADERS=true
    (proxy reverso confiavel na frente da API).
    """
    host = request.client.host if request.client else "unknown"
    if settings.TRUST_PROXY_HEADERS:
        forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if forwarded:
            host = forwarded
    return f"{prefix}:{host}"


def rate_limit_generate_bundle(request: Request) -> None:
    generate_bundle_limiter.check(_client_key(request, "generate-bundle"))


def rate_limit_ingestion(request: Request) -> None:
    ingestion_limiter.check(_client_key(request, "ingestion"))


def rate_limit_template_preview(request: Request) -> None:
    template_preview_limiter.check(_client_key(request, "template-preview"))


def rate_limit_template_generate(request: Request) -> None:
    template_generate_limiter.check(_client_key(request, "template-generate"))


def rate_limit_auth_login(request: Request) -> None:
    auth_login_limiter.check(_client_key(request, "auth-login"))


def rate_limit_auth_register(request: Request) -> None:
    auth_register_limiter.check(_client_key(request, "auth-register"))


def rate_limit_draft_write(request: Request) -> None:
    draft_write_limiter.check(_client_key(request, "draft-write"))


def rate_limit_ai(request: Request) -> None:
    ai_limiter.check(_client_key(request, "ai"))


def reset_redis_probe() -> None:
    """Utilitario de teste para forcar nova tentativa de conexao Redis."""
    global _redis_client, _redis_checked
    _redis_client = None
    _redis_checked = False

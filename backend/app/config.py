"""
Configurações da aplicação usando Pydantic Settings
Arquivo: backend/app/config.py
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.paths import default_sqlite_path, resolve_sqlite_database_url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # App
    APP_NAME: str = "SNAPENG"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database — SQLite canonico na raiz do repo (nao depende do cwd)
    DATABASE_URL: str = f"sqlite:///{default_sqlite_path().as_posix()}"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # AI Services
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Storage
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    S3_BUCKET_NAME: str = "snapeng-documents"
    AWS_REGION: str = "us-east-1"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""

    # Email
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@snapeng.com.br"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Docker Compose / Postgres (usadas pelo compose; opcionais no app)
    POSTGRES_USER: str = "snapeng_user"
    POSTGRES_PASSWORD: str = "change-me-in-prod"
    POSTGRES_DB: str = "snapeng"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000"

    # Hosts / proxy (produção)
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,testserver"
    # Só ative atrás de proxy reverso confiável; senão X-Forwarded-For é ignorado.
    TRUST_PROXY_HEADERS: bool = False

    @property
    def allowed_origins_list(self) -> List[str]:
        """Retorna lista de origens permitidas para CORS"""
        raw = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        if not raw or "*" in raw:
            return ["*"]
        return raw

    @property
    def allowed_hosts_list(self) -> List[str]:
        hosts = [h.strip() for h in self.ALLOWED_HOSTS.split(",") if h.strip()]
        if not hosts or "*" in hosts:
            return ["*"]
        return hosts

    @field_validator("SECRET_KEY")
    @classmethod
    def secret_key_min_length(cls, value: str) -> str:
        if value and len(value) < 32:
            raise ValueError("SECRET_KEY deve ter pelo menos 32 caracteres.")
        return value

    @model_validator(mode="after")
    def normalize_and_secure(self) -> "Settings":
        self.DATABASE_URL = resolve_sqlite_database_url(self.DATABASE_URL)
        if self.DEBUG:
            return self
        insecure_markers = (
            "dev-secret",
            "change-this",
            "change_this",
            "changeme",
        )
        key = (self.SECRET_KEY or "").lower()
        if not self.SECRET_KEY or any(marker in key for marker in insecure_markers):
            raise ValueError(
                "Com DEBUG=False, defina SECRET_KEY forte e distinta dos valores de desenvolvimento."
            )
        return self


@lru_cache()
def get_settings() -> Settings:
    """Retorna instância singleton das configurações"""
    return Settings()


settings = get_settings()

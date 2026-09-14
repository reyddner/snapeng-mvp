"""Schemas para rascunhos publicos."""

from datetime import datetime
from typing import Any, Dict, Literal, Optional
import json

from pydantic import BaseModel, Field, model_validator

from app.schemas.multidisciplinary import MemorialPlanRequest

# Limite de armazenamento por rascunho (proteção contra abuso de disco/DB).
MAX_DRAFT_PAYLOAD_BYTES = 512_000

DraftStatus = Literal[
    "novo",
    "em_preenchimento",
    "processando",
    "aguardando_informacao",
    "erro",
    "memorial_gerado",
    "em_revisao",
    "finalizado",
]


def _payload_size_bytes(payload: Dict[str, Any]) -> int:
    return len(json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8"))


def ensure_draft_payload_within_limit(payload: Dict[str, Any]) -> None:
    size = _payload_size_bytes(payload)
    if size > MAX_DRAFT_PAYLOAD_BYTES:
        raise ValueError(
            f"Payload do rascunho excede o limite de {MAX_DRAFT_PAYLOAD_BYTES} bytes "
            f"(atual: {size})."
        )


def normalize_draft_status(value: Optional[str]) -> str:
    allowed = {
        "novo",
        "em_preenchimento",
        "processando",
        "aguardando_informacao",
        "erro",
        "memorial_gerado",
        "em_revisao",
        "finalizado",
    }
    if value in allowed:
        return value
    return "em_preenchimento"


class DraftCreateRequest(MemorialPlanRequest):
    ttl_days: int = Field(default=7, ge=1, le=30)
    status: DraftStatus = "novo"

    @model_validator(mode="after")
    def validate_payload_size(self) -> "DraftCreateRequest":
        ensure_draft_payload_within_limit(self.model_dump(exclude={"ttl_days"}))
        return self


class DraftUpdateRequest(BaseModel):
    enterprise: Dict[str, Any] | None = None
    disciplines: list[Dict[str, Any]] | None = None
    mode: str | None = None
    professional: Dict[str, Any] | None = None
    source_documents: list[Dict[str, Any]] | None = None
    status: DraftStatus | None = None
    extend_ttl_days: int | None = Field(default=None, ge=1, le=30)


class DraftResponse(BaseModel):
    draft_id: str
    payload: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime

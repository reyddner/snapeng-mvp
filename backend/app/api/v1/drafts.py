"""Persistencia temporaria de empreendimentos sem autenticacao."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.rate_limit import rate_limit_draft_write
from app.models.draft import MemorialDraft
from app.models.user import User
from app.schemas.draft import (
    DraftCreateRequest,
    DraftResponse,
    DraftUpdateRequest,
    ensure_draft_payload_within_limit,
    normalize_draft_status,
)
from app.schemas.project import ProjectResponse
from app.services.draft_claim import claim_draft_to_project

router = APIRouter()


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _get_active_draft(draft_id: str, db: Session, *, purge: bool = True) -> MemorialDraft:
    draft = db.query(MemorialDraft).filter(MemorialDraft.draft_id == draft_id).first()
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rascunho não encontrado")
    if draft.expires_at <= _now():
        if purge:
            db.delete(draft)
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Rascunho expirado. Os dados locais do navegador podem ainda permitir recuperação parcial.",
        )
    return draft


def _payload_status(payload: dict) -> str:
    return normalize_draft_status((payload or {}).get("status"))


def _response(draft: MemorialDraft) -> DraftResponse:
    payload = dict(draft.payload or {})
    return DraftResponse(
        draft_id=draft.draft_id,
        payload=payload,
        status=_payload_status(payload),
        created_at=draft.created_at,
        updated_at=draft.updated_at,
        expires_at=draft.expires_at,
    )


@router.post("", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def create_draft(
    request: DraftCreateRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_draft_write),
):
    """Cria um rascunho temporario sem exigir conta."""
    now = _now()
    payload = request.model_dump(exclude={"ttl_days"})
    payload["status"] = normalize_draft_status(payload.get("status") or "novo")
    draft = MemorialDraft(
        draft_id=uuid4().hex,
        payload=payload,
        created_at=now,
        updated_at=now,
        expires_at=now + timedelta(days=request.ttl_days),
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return _response(draft)


@router.get("/{draft_id}", response_model=DraftResponse)
async def get_draft(draft_id: str, db: Session = Depends(get_db)):
    return _response(_get_active_draft(draft_id, db))


@router.post("/{draft_id}/claim", response_model=ProjectResponse)
async def claim_draft(
    draft_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Associa o rascunho publico a um projeto da conta autenticada."""
    draft = _get_active_draft(draft_id, db)
    return claim_draft_to_project(draft=draft, user=current_user, db=db)


@router.patch("/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: str,
    request: DraftUpdateRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_draft_write),
):
    draft = _get_active_draft(draft_id, db)
    current_payload = dict(draft.payload or {})
    updates = request.model_dump(exclude_unset=True, exclude={"extend_ttl_days"})
    for field, value in updates.items():
        if value is not None:
            current_payload[field] = value
    if "status" not in current_payload:
        current_payload["status"] = "em_preenchimento"
    elif request.status is None and current_payload.get("status") == "novo":
        current_payload["status"] = "em_preenchimento"
    else:
        current_payload["status"] = normalize_draft_status(current_payload.get("status"))

    try:
        ensure_draft_payload_within_limit(current_payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=str(exc),
        ) from exc

    draft.payload = current_payload
    draft.updated_at = _now()
    ttl_days = request.extend_ttl_days or 7
    draft.expires_at = _now() + timedelta(days=ttl_days)
    db.commit()
    db.refresh(draft)
    return _response(draft)


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(draft_id: str, db: Session = Depends(get_db)):
    draft = _get_active_draft(draft_id, db)
    db.delete(draft)
    db.commit()

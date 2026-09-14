"""API publica de projetos-modelo (demos) para showcase e validacao."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rate_limit import rate_limit_generate_bundle
from app.models.draft import MemorialDraft
from app.schemas.draft import DraftResponse, normalize_draft_status
from app.schemas.multidisciplinary import MemorialBundleRequest
from app.services.demo_catalog import build_plan_payload, get_demo, list_demos

router = APIRouter()


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.get("")
async def list_public_demos() -> Dict[str, Any]:
    return {"demos": list_demos()}


@router.get("/{slug}")
async def get_public_demo(slug: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    demo = get_demo(slug)
    if demo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo não encontrado.")
    try:
        payload = build_plan_payload(db, slug)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    return {
        "demo": {
            "slug": demo["slug"],
            "title": demo["title"],
            "subtitle": demo["subtitle"],
            "summary": demo["summary"],
            "typology": demo["typology"],
            "area_m2": demo["area_m2"],
            "highlights": demo["highlights"],
            "scope_note": demo["scope_note"],
            "discipline_count": len(payload["disciplines"]),
            "disciplines": [item["discipline"] for item in payload["disciplines"]],
        },
        "payload_preview": {
            "enterprise": payload["enterprise"],
            "professional": {
                "full_name": payload["professional"].get("full_name"),
                "crea_number": payload["professional"].get("crea_number"),
                "crea_state": payload["professional"].get("crea_state"),
                "company_name": payload["professional"].get("company_name"),
            },
            "mode": payload["mode"],
            "disciplines": [
                {
                    "discipline": item["discipline"],
                    "template_id": item["template_id"],
                    "fields_filled": len(item.get("data") or {}),
                }
                for item in payload["disciplines"]
            ],
        },
    }


@router.post("/{slug}/open-draft", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def open_demo_as_draft(slug: str, db: Session = Depends(get_db)) -> DraftResponse:
    """Cria um rascunho publico pre-preenchido a partir do projeto-modelo."""
    if get_demo(slug) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo não encontrado.")
    try:
        payload = build_plan_payload(db, slug)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    payload["status"] = normalize_draft_status("em_preenchimento")
    now = _now()
    draft = MemorialDraft(
        draft_id=uuid4().hex,
        payload=payload,
        created_at=now,
        updated_at=now,
        expires_at=now + timedelta(days=7),
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return DraftResponse(
        draft_id=draft.draft_id,
        payload=dict(draft.payload or {}),
        status=normalize_draft_status((draft.payload or {}).get("status")),
        created_at=draft.created_at,
        updated_at=draft.updated_at,
        expires_at=draft.expires_at,
    )


@router.post("/{slug}/generate-bundle")
async def generate_demo_bundle(
    slug: str,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_generate_bundle),
):
    """Gera o ZIP de demonstracao do projeto-modelo (mesma engine de producao)."""
    from app.api.v1.memorials import generate_memorial_bundle

    if get_demo(slug) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modelo não encontrado.")
    try:
        payload = build_plan_payload(db, slug)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    request = MemorialBundleRequest(
        enterprise=payload["enterprise"],
        mode=payload["mode"],
        disciplines=payload["disciplines"],
        professional=payload["professional"],
    )
    response = await generate_memorial_bundle(request=request, db=db, _=None)
    if isinstance(response, StreamingResponse):
        response.headers["Content-Disposition"] = (
            f'attachment; filename="demo_{slug}.zip"'
        )
    return response

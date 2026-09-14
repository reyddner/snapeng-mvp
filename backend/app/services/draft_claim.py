"""Converte rascunho publico em projeto autenticado."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.draft import MemorialDraft
from app.models.project import Project, ProjectStatus
from app.models.template import EngineeringTemplate
from app.models.user import User


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _anchor_template_id(payload: dict[str, Any]) -> int:
    for item in payload.get("disciplines") or []:
        raw = item.get("template_id")
        if raw is None or raw == "":
            continue
        try:
            return int(raw)
        except (TypeError, ValueError) as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="template_id inválido em uma das disciplinas.",
            ) from exc
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Selecione ao menos um modelo de memorial nas disciplinas antes de salvar na conta.",
    )


def _map_status(draft_status: str | None) -> ProjectStatus:
    if draft_status in {"memorial_gerado", "finalizado"}:
        return ProjectStatus.COMPLETED
    return ProjectStatus.IN_PROGRESS


def _find_existing_claim(db: Session, user_id: int, draft_id: str) -> Project | None:
    projects = (
        db.query(Project)
        .filter(Project.owner_id == user_id)
        .order_by(Project.id.desc())
        .limit(200)
        .all()
    )
    for project in projects:
        data = project.project_data or {}
        if data.get("kind") == "memorial_plan" and data.get("source_draft_id") == draft_id:
            return project
    return None


def claim_draft_to_project(
    *,
    draft: MemorialDraft,
    user: User,
    db: Session,
    delete_draft: bool = True,
) -> Project:
    """Persiste o plano multidisciplinar do draft como Project do usuario."""
    existing = _find_existing_claim(db, user.id, draft.draft_id)
    if existing is not None:
        return existing

    payload = dict(draft.payload or {})
    enterprise = payload.get("enterprise") or {}
    name = (enterprise.get("name") or "").strip() or f"Memorial {draft.draft_id[:8]}"
    description = enterprise.get("description")
    template_id = _anchor_template_id(payload)

    template = (
        db.query(EngineeringTemplate)
        .filter(EngineeringTemplate.id == template_id)
        .first()
    )
    if template is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Modelo de memorial referenciado no rascunho não existe mais.",
        )

    draft_status = str(payload.get("status") or "em_preenchimento")
    project_status = _map_status(draft_status)
    project_data = {
        "kind": "memorial_plan",
        "source_draft_id": draft.draft_id,
        "enterprise": enterprise,
        "disciplines": payload.get("disciplines") or [],
        "mode": payload.get("mode") or "individual",
        "professional": payload.get("professional") or {},
        "source_documents": payload.get("source_documents") or [],
        "draft_status": draft_status,
    }

    project = Project(
        name=name[:200],
        description=description,
        project_data=project_data,
        status=project_status,
        owner_id=user.id,
        template_id=template_id,
        completed_at=_now() if project_status == ProjectStatus.COMPLETED else None,
    )
    db.add(project)
    db.flush()

    if delete_draft:
        db.delete(draft)

    db.commit()
    db.refresh(project)
    return project

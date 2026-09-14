"""
Endpoints para CRUD de Templates
Arquivo: backend/app/api/v1/templates.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.rate_limit import (
    rate_limit_template_generate,
    rate_limit_template_preview,
)
from app.models.user import User
from app.models.template import EngineeringTemplate
from app.schemas.template import (
    TemplateCreate,
    MemorialGenerationRequest,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
    TemplateResponse,
    TemplateUpdate,
)
from app.services.template_engine import TemplateEngine
from app.services.document_generator import DocumentGenerator
import io
import re

router = APIRouter()


def _template_structure(template: EngineeringTemplate) -> dict:
    structure = dict(template.structure or {})
    structure.setdefault("variables", template.variables or [])
    return structure


def _get_public_template_or_404(template_id: int, db: Session) -> EngineeringTemplate:
    template = (
        db.query(EngineeringTemplate)
        .filter(EngineeringTemplate.id == template_id)
        .filter(EngineeringTemplate.is_public == 1)
        .first()
    )
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template não encontrado")
    return template


def _validate_template_payload_safe(template_payload: dict) -> None:
    from app.core.safe_formula import is_formula_shape_safe

    unsafe_markers = ("{%", "%}", "{#", "#}")
    sections = template_payload.get("sections", [])
    for section in sections:
        content = str(section.get("content", ""))
        if any(marker in content for marker in unsafe_markers):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Template contém sintaxe não permitida. Use apenas placeholders no formato {{variavel}}.",
            )
        for subsection in section.get("subsections", []):
            sub_content = str(subsection.get("content", ""))
            if any(marker in sub_content for marker in unsafe_markers):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Template contém sintaxe não permitida. Use apenas placeholders no formato {{variavel}}.",
                )

    for calc in template_payload.get("calculations", []) or []:
        formula = str(calc.get("formula", ""))
        if formula and not is_formula_shape_safe(formula):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fórmula de cálculo contém tokens não permitidos.",
            )


@router.get("/{template_id}/questionnaire")
async def get_template_questionnaire(template_id: int, db: Session = Depends(get_db)):
    """Retorna as perguntas necessárias para iniciar um memorial sem autenticação."""
    template = _get_public_template_or_404(template_id, db)

    return {
        "template_id": template.id,
        "name": template.name,
        "description": template.description,
        "category": template.category.value,
        "questions": template.variables or [],
    }


@router.post("/{template_id}/preview", response_model=TemplatePreviewResponse)
async def preview_template(
    template_id: int,
    request: TemplatePreviewRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_template_preview),
):
    """Valida respostas e renderiza uma prévia sem criar usuário ou projeto."""
    template = _get_public_template_or_404(template_id, db)

    engine = TemplateEngine()
    structure = _template_structure(template)
    errors = engine.validate_user_data(structure, request.project_data)
    content = {}
    if not errors:
        try:
            content = engine.render_template(structure, request.project_data)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

    return TemplatePreviewResponse(
        template_id=template.id,
        template_name=template.name,
        valid=not errors,
        errors=errors,
        content=content,
    )


@router.post("/{template_id}/generate")
async def generate_memorial_without_auth(
    template_id: int,
    request: MemorialGenerationRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_template_generate),
):
    """Gera um DOCX a partir do questionário, sem exigir autenticação."""
    template = _get_public_template_or_404(template_id, db)

    engine = TemplateEngine()
    structure = _template_structure(template)
    errors = engine.validate_user_data(structure, request.project_data)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Respostas inválidas", "fields": errors},
        )

    try:
        rendered_content = engine.render_template(structure, request.project_data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    professional = request.professional.model_dump() if request.professional else {}
    document = DocumentGenerator().generate_docx(
        rendered_content,
        {
            "title": f"MEMORIAL DESCRITIVO - {request.project_name}",
            "obra": request.project_name,
            "local": request.project_data.get("localizacao", "N/A"),
            "responsavel": professional.get("full_name", "A definir"),
            "crea": " / ".join(
                value for value in [
                    professional.get("crea_number"),
                    professional.get("crea_state"),
                ] if value
            ) or "A definir",
            "professional": professional,
        },
    )
    safe_name = re.sub(r"[^A-Za-z0-9_-]+", "_", request.project_name).strip("_")
    filename = f"{safe_name or 'memorial_descritivo'}.docx"
    return StreamingResponse(
        io.BytesIO(document.getvalue()),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/", response_model=List[TemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db),
):
    """Lista apenas templates públicos prontos para geração (quality gate)."""
    from app.services.template_quality import assess_template

    query = db.query(EngineeringTemplate).filter(EngineeringTemplate.is_public == 1)

    if category:
        query = query.filter(EngineeringTemplate.category == category)

    # Busca um pouco além do limite para compensar filtros de qualidade.
    candidates = query.offset(skip).limit(max(limit * 3, limit)).all()
    ready: list[EngineeringTemplate] = []
    for template in candidates:
        structure = dict(template.structure or {})
        structure.setdefault("variables", template.variables or [])
        if assess_template(structure).get("ready"):
            ready.append(template)
        if len(ready) >= limit:
            break
    return ready


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """
    Obtém um template específico

    Args:
        template_id: ID do template
        db: Sessão do banco de dados

    Returns:
        Template encontrado

    Raises:
        HTTPException: Se template não encontrado
    """
    return _get_public_template_or_404(template_id, db)


@router.post("/", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Cria um novo template (requer autenticação)

    Args:
        template_data: Dados do template
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Template criado
    """
    _validate_template_payload_safe(template_data.structure or {})
    db_template = EngineeringTemplate(
        **template_data.dict(),
        author_id=current_user.id,
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Atualiza um template (apenas o autor)

    Args:
        template_id: ID do template
        template_data: Dados atualizados
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Template atualizado

    Raises:
        HTTPException: Se template não encontrado ou sem permissão
    """
    template = db.query(EngineeringTemplate).filter(EngineeringTemplate.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado",
        )

    if template.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para editar este template",
        )

    # Atualizar campos
    update_data = template_data.dict(exclude_unset=True)
    if "structure" in update_data and update_data["structure"] is not None:
        _validate_template_payload_safe(update_data["structure"])
    for field, value in update_data.items():
        setattr(template, field, value)

    db.commit()
    db.refresh(template)

    return template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Deleta um template (apenas o autor)

    Args:
        template_id: ID do template
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Raises:
        HTTPException: Se template não encontrado ou sem permissão
    """
    template = db.query(EngineeringTemplate).filter(EngineeringTemplate.id == template_id).first()

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template não encontrado",
        )

    if template.author_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para deletar este template",
        )

    db.delete(template)
    db.commit()

    return None


"""Planejamento publico de memoriais individuais e multidisciplinares."""

from typing import Any, Dict
import io
import re
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.rate_limit import rate_limit_generate_bundle
from app.models.template import EngineeringTemplate
from app.schemas.multidisciplinary import (
    MemorialBundleRequest,
    MemorialPlanRequest,
    MemorialPlanResponse,
)
from app.services.questionnaire_catalog import get_questionnaire
from app.services.document_generator import DocumentGenerator
from app.services.template_engine import TemplateEngine
from app.services.template_quality import assess_template
from app.services.discipline_compatibility import validate_discipline_compatibility
from app.services.discipline_rules import validate_discipline_rules
from app.services.memorial_preflight import run_memorial_preflight

router = APIRouter()


DISCIPLINE_CATEGORY_MAP = {
    "eletrica": ["eletrica"],
    "hidraulica": ["hidraulica"],
    "pluvial": ["hidraulica", "civil_infra"],
    "sanitario": ["hidraulica"],
    "spda": ["eletrica", "edificacoes", "estruturas"],
    "corpo_bombeiros": ["edificacoes", "eletrica"],
    "arquitetura": ["edificacoes"],
    "estrutura_metalica": ["estruturas"],
    "estrutura_concreto": ["estruturas"],
    "fundacoes": ["estruturas", "civil_infra"],
}


def _structure_with_questions(template: EngineeringTemplate) -> dict:
    structure = dict(template.structure or {})
    structure.setdefault("variables", template.variables or [])
    return structure


def _professional_metadata(request: MemorialBundleRequest) -> Dict[str, Any]:
    professional = request.professional.model_dump() if request.professional else {}
    crea = " / ".join(
        value
        for value in [professional.get("crea_number"), professional.get("crea_state")]
        if value
    )
    return {
        "responsavel": professional.get("full_name", "A definir"),
        "crea": crea or "A definir",
        "professional": professional,
    }


@router.get("/template-options/{discipline}")
async def list_template_options(discipline: str, db: Session = Depends(get_db)):
    """Lista templates geradores compatíveis com uma disciplina."""
    categories = DISCIPLINE_CATEGORY_MAP.get(discipline.lower().strip())
    if categories is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Disciplina não encontrada")

    templates = (
        db.query(EngineeringTemplate)
        .filter(EngineeringTemplate.category.in_(categories))
        .filter(EngineeringTemplate.is_public == 1)
        .all()
    )
    return {
        "discipline": discipline.lower().strip(),
        "templates": [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "subcategory": template.subcategory,
                "ready": True,
            }
            for template in templates
            if assess_template(
                {
                    **(template.structure or {}),
                    "variables": (template.structure or {}).get("variables")
                    or template.variables
                    or [],
                }
            )["ready"]
        ],
    }


@router.post("/plan", response_model=MemorialPlanResponse)
async def plan_memorials(
    request: MemorialPlanRequest,
    db: Session = Depends(get_db),
):
    """Monta um empreendimento e seus memoriais sem criar conta ou projeto."""
    if not request.disciplines:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Selecione ao menos uma disciplina.",
        )

    conflicts = validate_discipline_compatibility(
        request.enterprise.shared_data,
        [selection.model_dump() for selection in request.disciplines],
    )
    if conflicts:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": "Existem conflitos entre disciplinas.", "conflicts": conflicts},
        )

    seen = set()
    planned = []
    for selection in request.disciplines:
        discipline = selection.discipline.lower().strip()
        if discipline in seen:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"A disciplina '{discipline}' foi selecionada mais de uma vez.",
            )
        seen.add(discipline)

        questionnaire = get_questionnaire(discipline)
        if questionnaire is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Disciplina '{discipline}' não encontrada.",
            )

        template = None
        if selection.template_id is not None:
            template = (
                db.query(EngineeringTemplate)
                .filter(EngineeringTemplate.id == selection.template_id)
                .filter(EngineeringTemplate.is_public == 1)
                .first()
            )
            if template is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Template {selection.template_id} não encontrado.",
                )

        planned.append(
            {
                "discipline": discipline,
                "label": questionnaire["label"],
                "status": "not_started" if not selection.data else "in_progress",
                "template_id": selection.template_id,
                "document_types": questionnaire["document_types"],
                "questions": questionnaire["questions"],
                "data": selection.data,
                "missing_fields": [
                    question["name"]
                    for question in questionnaire["questions"]
                    if question.get("required")
                    and not selection.data.get(question["name"])
                ],
                "rule_warnings": validate_discipline_rules(discipline, selection.data),
                "template_name": template.name if template else None,
            }
        )

    signature_notice = (
        "Os dados profissionais serão exibidos no bloco técnico do documento. "
        "A assinatura eletrônica com validade jurídica depende de integração posterior "
        "com um provedor certificado."
    )
    return MemorialPlanResponse(
        enterprise=request.enterprise,
        mode=request.mode,
        disciplines=planned,
        professional=request.professional,
        signature_notice=signature_notice,
    )


@router.post("/preflight")
async def memorial_preflight(request: MemorialPlanRequest, db: Session = Depends(get_db)):
    """Relatório de prontidão: o que falta, conflitos e templates antes de gerar."""
    return run_memorial_preflight(
        db,
        enterprise=request.enterprise.model_dump(),
        disciplines=[selection.model_dump() for selection in request.disciplines],
        shared_data=request.enterprise.shared_data,
    )


@router.post("/generate-bundle")
async def generate_memorial_bundle(
    request: MemorialBundleRequest,
    db: Session = Depends(get_db),
    _: None = Depends(rate_limit_generate_bundle),
):
    """Gera memoriais individuais, combinado ou ambos em um ZIP, sem login."""
    preflight = run_memorial_preflight(
        db,
        enterprise=request.enterprise.model_dump(),
        disciplines=[selection.model_dump() for selection in request.disciplines],
        shared_data=request.enterprise.shared_data,
    )
    if not preflight["can_generate"]:
        discipline_errors = {
            item["discipline"]: item["errors"] or ["Disciplina incompleta."]
            for item in preflight["disciplines"]
            if not item["ok"]
        }
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Não é possível gerar o memorial ainda. Corrija os itens bloqueantes.",
                "blocking": preflight["blocking"],
                "warnings": preflight["warnings"],
                "conflicts": preflight["conflicts"],
                "disciplines": discipline_errors,
                "summary": preflight["summary"],
            },
        )

    engine = TemplateEngine()
    generated = []
    professional_metadata = _professional_metadata(request)
    for selection in request.disciplines:
        discipline = selection.discipline.lower().strip()
        questionnaire = get_questionnaire(discipline)
        template = (
            db.query(EngineeringTemplate)
            .filter(EngineeringTemplate.id == selection.template_id)
            .filter(EngineeringTemplate.is_public == 1)
            .first()
        )
        # Preflight já validou; falha aqui seria inconsistência rara.
        if questionnaire is None or template is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Falha interna ao carregar disciplina/template '{discipline}'.",
            )

        structure = _structure_with_questions(template)
        try:
            rendered = engine.render_template(
                structure,
                {**request.enterprise.shared_data, **selection.data},
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Falha ao montar o conteúdo do memorial.",
                    "blocking": [str(exc)],
                    "disciplines": {discipline: str(exc)},
                },
            ) from exc
        generated.append((discipline, questionnaire["label"], rendered))

    metadata_base = {
        "title": f"MEMORIAIS - {request.enterprise.name}",
        "obra": request.enterprise.name,
        "local": request.enterprise.shared_data.get("localizacao", "N/A"),
        **professional_metadata,
    }
    combined_content = {"sections": [], "calculations": {}, "normas": []}
    for discipline, label, rendered in generated:
        for section in rendered.get("sections", []):
            combined_content["sections"].append(
                {**section, "title": f"{label} - {section['title']}"}
            )
        combined_content["calculations"].update(rendered.get("calculations", {}))
        combined_content["normas"].extend(rendered.get("normas", []))

    archive = io.BytesIO()
    generator = DocumentGenerator()
    with ZipFile(archive, "w", ZIP_DEFLATED) as bundle:
        if request.mode in {"individual", "both"}:
            for discipline, label, rendered in generated:
                meta = {**metadata_base, "title": f"{label} - {request.enterprise.name}"}
                filename = re.sub(r"[^A-Za-z0-9_-]+", "_", discipline)
                bundle.writestr(f"{filename}.docx", generator.generate_docx(rendered, meta).getvalue())
                bundle.writestr(f"{filename}.pdf", generator.generate_pdf(rendered, meta).getvalue())
        if request.mode in {"combined", "both"}:
            bundle.writestr(
                "memorial_completo.docx",
                generator.generate_docx(combined_content, metadata_base).getvalue(),
            )
            bundle.writestr(
                "memorial_completo.pdf",
                generator.generate_pdf(combined_content, metadata_base).getvalue(),
            )

    archive.seek(0)
    return StreamingResponse(
        archive,
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="memoriais_snapeng.zip"'
        },
    )


@router.post("/compatibility")
async def check_compatibility(request: MemorialPlanRequest):
    """Retorna conflitos entre dados compartilhados e disciplinas sem gerar documentos."""
    conflicts = validate_discipline_compatibility(
        request.enterprise.shared_data,
        [selection.model_dump() for selection in request.disciplines],
    )
    return {"compatible": not conflicts, "conflicts": conflicts}

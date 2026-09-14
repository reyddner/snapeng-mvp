"""
Endpoints para funcionalidades de IA
Arquivo: backend/app/api/v1/ai.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, List
from app.core.dependencies import get_current_active_user
from app.core.rate_limit import rate_limit_ai
from app.models.user import User
from app.services.ai_assistant import AIAssistant

router = APIRouter()


class SuggestContentRequest(BaseModel):
    section_title: str
    context: Dict[str, Any]
    template_type: str


class ValidateNormRequest(BaseModel):
    content: str
    applicable_norms: List[str]


@router.post("/suggest-content")
async def suggest_content(
    request: SuggestContentRequest,
    _current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_ai),
):
    """Sugere conteúdo para uma seção do memorial usando IA."""
    assistant = AIAssistant()

    if not assistant.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de IA não configurado. Configure ANTHROPIC_API_KEY no .env",
        )

    try:
        suggestion = await assistant.suggest_content(
            section_title=request.section_title,
            context=request.context,
            template_type=request.template_type,
        )
        return {"suggestion": suggestion}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar sugestão.",
        )


@router.post("/validate-norm")
async def validate_norm_compliance(
    request: ValidateNormRequest,
    _current_user: User = Depends(get_current_active_user),
    _: None = Depends(rate_limit_ai),
):
    """Valida conformidade do conteúdo com normas técnicas."""
    assistant = AIAssistant()

    if not assistant.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Serviço de IA não configurado. Configure ANTHROPIC_API_KEY no .env",
        )

    try:
        validation = await assistant.validate_norm_compliance(
            content=request.content,
            applicable_norms=request.applicable_norms,
        )
        return validation
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao validar normas.",
        )


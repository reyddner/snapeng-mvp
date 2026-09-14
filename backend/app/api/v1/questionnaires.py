"""Catalogo publico de questionarios por disciplina."""

from fastapi import APIRouter, HTTPException, status

from app.services.questionnaire_catalog import get_questionnaire, list_disciplines

router = APIRouter()


@router.get("/")
async def list_questionnaires():
    """Lista disciplinas disponiveis para iniciar um memorial."""
    return {"disciplines": list_disciplines()}


@router.get("/{discipline}")
async def get_discipline_questionnaire(discipline: str):
    """Retorna perguntas-chave para uma disciplina de engenharia."""
    questionnaire = get_questionnaire(discipline)
    if questionnaire is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disciplina nao encontrada",
        )
    return questionnaire
"""Entrada publica de documentos para extracao sem IA."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.rate_limit import rate_limit_ingestion
from app.services.document_ingestion import extract_document

router = APIRouter()


@router.post("/extract")
async def extract_uploaded_document(
    file: UploadFile = File(...),
    disciplines: Optional[str] = Form(default=None),
    _: None = Depends(rate_limit_ingestion),
):
    """Extrai texto de PDF, DOCX ou TXT e devolve dados pendentes de confirmacao.

    `disciplines` pode ser uma lista separada por virgula (ex.: eletrica,spda)
    para ativar heurísticas específicas do questionário.
    """
    try:
        content = await file.read()
        selected: List[str] = []
        if disciplines:
            selected = [item.strip() for item in disciplines.split(",") if item.strip()]
        return extract_document(file.filename or "arquivo", content, disciplines=selected)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Não foi possível ler o arquivo.",
        ) from error

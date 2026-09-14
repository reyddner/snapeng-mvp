"""
Endpoints para geração e exportação de documentos
Arquivo: backend/app/api/v1/documents.py
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.project import Project
from app.models.document import Document, DocumentFormat
from app.services.document_generator import DocumentGenerator
from app.services.template_engine import TemplateEngine
import io
import re

router = APIRouter()


def _safe_download_filename(name: str, extension: str) -> str:
    base = re.sub(r"[^\w.\-]+", "_", (name or "memorial").strip(), flags=re.UNICODE)
    base = base.strip("._") or "memorial"
    return f"{base[:80]}.{extension}"


@router.get("/project/{project_id}", response_model=List[dict])
async def list_project_documents(
    project_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Lista documentos gerados de um projeto

    Args:
        project_id: ID do projeto
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Lista de documentos
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este projeto",
        )

    documents = db.query(Document).filter(Document.project_id == project_id).all()

    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "format": doc.format.value,
            "created_at": doc.created_at.isoformat(),
            "file_size": doc.file_size,
        }
        for doc in documents
    ]


@router.post("/generate/{project_id}")
async def generate_document(
    project_id: int,
    doc_format: DocumentFormat = DocumentFormat.DOCX,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Gera documento a partir de um projeto

    Args:
        project_id: ID do projeto
        doc_format: Formato do documento (DOCX, PDF, HTML)
        current_user: Usuário autenticado
        db: Sessão do banco de dados

    Returns:
        Arquivo do documento gerado

    Raises:
        HTTPException: Se projeto não encontrado ou sem permissão
    """
    project = db.query(Project).filter(Project.id == project_id).first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projeto não encontrado",
        )

    if project.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para acessar este projeto",
        )

    # Renderizar template com dados do projeto
    template_engine = TemplateEngine()
    rendered_content = template_engine.render_template(
        project.template.structure, project.project_data
    )

    # Gerar documento
    document_generator = DocumentGenerator()
    metadata = {
        "title": f"MEMORIAL DESCRITIVO - {project.name}",
        "obra": project.name,
        "local": project.project_data.get("localizacao", "N/A"),
        "responsavel": current_user.full_name or current_user.email,
        "crea": current_user.crea or "N/A",
    }

    if doc_format == DocumentFormat.DOCX:
        file_stream = document_generator.generate_docx(rendered_content, metadata)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = _safe_download_filename(project.name, "docx")
    elif doc_format == DocumentFormat.PDF:
        file_stream = document_generator.generate_pdf(rendered_content, metadata)
        media_type = "application/pdf"
        filename = _safe_download_filename(project.name, "pdf")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato não suportado",
        )

    # Salvar referência no banco
    db_document = Document(
        filename=filename,
        format=doc_format,
        project_id=project_id,
        file_size=len(file_stream.getvalue()),
    )
    db.add(db_document)
    db.commit()

    return StreamingResponse(
        io.BytesIO(file_stream.getvalue()),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


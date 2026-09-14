"""Extracao segura de texto para analise posterior e confirmacao humana."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from docx import Document
from pypdf import PdfReader

from app.services.field_suggestions import suggest_fields_from_text

MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def extract_document(
    filename: str,
    content: bytes,
    disciplines: Optional[List[str]] = None,
) -> Dict[str, Any]:
    extension = Path(filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Formato não suportado. Use PDF, DOCX ou TXT.")
    if len(content) > MAX_FILE_SIZE:
        raise ValueError("Arquivo excede o limite de 10 MB.")
    if not content:
        raise ValueError("Arquivo vazio.")

    if extension == ".pdf":
        reader = PdfReader(BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages)
        page_count = len(pages)
    elif extension == ".docx":
        document = Document(BytesIO(content))
        paragraphs = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
        text = "\n\n".join(paragraphs)
        page_count = None
    else:
        text = content.decode("utf-8", errors="replace")
        page_count = None

    suggestions = suggest_fields_from_text(text, disciplines=disciplines)

    return {
        "filename": filename,
        "extension": extension,
        "size_bytes": len(content),
        "page_count": page_count,
        "text": text,
        "suggestions": suggestions,
        "disciplines": disciplines or [],
        "status": "pending_confirmation",
        "notice": (
            "Texto extraído para revisão. Sugestões (compartilhadas e por disciplina) "
            "são heurísticas e só entram no memorial após confirmação humana."
        ),
    }

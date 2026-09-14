"""
Model Document - SQLAlchemy
Arquivo: backend/app/models/document.py
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class DocumentFormat(str, enum.Enum):
    DOCX = "docx"
    PDF = "pdf"
    HTML = "html"


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    format = Column(Enum(DocumentFormat), nullable=False)
    file_path = Column(String(500))  # Caminho no S3 ou local
    file_size = Column(Integer)  # Tamanho em bytes

    # Conteúdo renderizado (para preview)
    rendered_content = Column(Text)

    # Relacionamento
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relacionamentos
    project = relationship("Project", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.filename} ({self.format})>"


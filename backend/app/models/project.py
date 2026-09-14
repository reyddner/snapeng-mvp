"""
Model Project - SQLAlchemy
Arquivo: backend/app/models/project.py
"""

from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Dados do projeto preenchidos pelo usuário
    project_data = Column(JSON, nullable=False)  # Variáveis preenchidas

    # Status do projeto
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT)

    # Relacionamentos
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("engineering_templates.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relacionamentos
    owner = relationship("User", back_populates="projects")
    template = relationship("EngineeringTemplate", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project {self.name} ({self.status})>"

